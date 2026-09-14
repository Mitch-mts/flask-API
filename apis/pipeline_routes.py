"""
Data Studio HTTP routes.

/studio and /dashboard render the UI.
/api/pipeline/* handles upload, cleaning, charts, Excel download, and
ServiceFunctions inspect calls used on the Explore panel.
"""
import os

from flask import Blueprint, current_app, jsonify, render_template, request, send_file

from configs.dataset_config import dataset_config
from utils.explore import EXPLORE_METHODS
from utils.pipeline import AVAILABLE_FEATURES, PipelineStore, build_chart

pipeline_bp = Blueprint("pipeline", __name__)

_store = None


def get_store():
    global _store
    if _store is None:
        upload_dir = current_app.config.get(
            "UPLOAD_FOLDER",
            os.path.join(os.getcwd(), "uploads"),
        )
        _store = PipelineStore(upload_dir)
    return _store


def _existing_datasets():
    names = ["athletes", "student", "coaches", "entries_gender", "medals", "teams"]
    available = []
    for name in names:
        try:
            path = dataset_config.get_dataset_path(name)
        except ValueError:
            continue
        if os.path.exists(path):
            available.append({"id": name, "label": name.replace("_", " ").title(), "path": path})
    return available


@pipeline_bp.route("/studio")
@pipeline_bp.route("/dashboard")
def data_studio():
    """
    Interactive data cleaning studio and process dashboard
    ---
    tags:
      - Data Studio
    responses:
      200:
        description: Data Studio HTML page
    """
    return render_template("data_studio.html")


@pipeline_bp.route("/api/pipeline/jobs", methods=["GET"])
def list_jobs():
    """
    List all pipeline jobs for the dashboard
    ---
    tags:
      - Data Studio
    responses:
      200:
        description: Job cards and status counts
    """
    return jsonify(get_store().list_jobs())


@pipeline_bp.route("/api/pipeline/jobs/<string:job_id>", methods=["GET"])
def get_job(job_id):
    """
    Get one pipeline job, including previews
    ---
    tags:
      - Data Studio
    parameters:
      - name: job_id
        in: path
        type: string
        required: true
    responses:
      200:
        description: Job details
      404:
        description: Job not found
    """
    try:
        return jsonify(get_store().public_job(job_id))
    except KeyError as exc:
        return jsonify({"error": str(exc)}), 404


@pipeline_bp.route("/api/pipeline/jobs/<string:job_id>", methods=["DELETE"])
def delete_job(job_id):
    """
    Remove a pipeline job from the dashboard
    ---
    tags:
      - Data Studio
    parameters:
      - name: job_id
        in: path
        type: string
        required: true
    responses:
      200:
        description: Job removed
      404:
        description: Job not found
    """
    try:
        get_store().delete(job_id)
        return jsonify({"message": "Job removed.", "job_id": job_id})
    except KeyError as exc:
        return jsonify({"error": str(exc)}), 404


@pipeline_bp.route("/api/pipeline/features", methods=["GET"])
def list_features():
    """
    List selectable cleaning and processing features
    ---
    tags:
      - Data Studio
    responses:
      200:
        description: Available processing features and built-in datasets
    """
    return jsonify({
        "features": AVAILABLE_FEATURES,
        "datasets": [{"id": item["id"], "label": item["label"]} for item in _existing_datasets()],
        "charts": [
            {"id": "bar", "label": "Bar"},
            {"id": "histogram", "label": "Histogram"},
            {"id": "pie", "label": "Pie"},
            {"id": "scatter", "label": "Scatter"},
            {"id": "box", "label": "Box"},
            {"id": "line", "label": "Line"},
        ],
        "explore_methods": EXPLORE_METHODS,
    })


@pipeline_bp.route("/api/pipeline/upload", methods=["POST"])
def upload_dataset():
    """
    Upload a CSV or Excel file to start a cleaning session
    ---
    tags:
      - Data Studio
    consumes:
      - multipart/form-data
    parameters:
      - name: file
        in: formData
        type: file
        required: false
        description: CSV or Excel file to upload
      - name: dataset
        in: formData
        type: string
        required: false
        description: Built-in dataset name if no file is uploaded
    responses:
      200:
        description: Upload accepted and preview generated
      400:
        description: Missing or invalid file
    """
    try:
        store = get_store()
        dataset_name = request.form.get("dataset") or request.args.get("dataset")
        uploaded = request.files.get("file")

        if uploaded and uploaded.filename:
            payload = store.create_from_upload(uploaded)
        elif dataset_name:
            match = next((item for item in _existing_datasets() if item["id"] == dataset_name), None)
            if match is None:
                return jsonify({"error": f"Unknown or missing dataset: {dataset_name}"}), 400
            payload = store.create_from_existing(match["id"], match["path"])
        else:
            return jsonify({"error": "Choose a file or a built-in dataset to continue."}), 400

        payload["message"] = "File ready. Select the processing features you want to apply."
        return jsonify(payload)
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400
    except Exception as exc:
        return jsonify({"error": f"Could not read the file: {exc}"}), 500


@pipeline_bp.route("/api/pipeline/process", methods=["POST"])
def process_dataset():
    """
    Apply selected processing features to an uploaded dataset
    ---
    tags:
      - Data Studio
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            job_id:
              type: string
            operations:
              type: array
              items:
                type: object
    responses:
      200:
        description: Cleaned dataset preview
      400:
        description: Invalid job or operations
    """
    try:
        body = request.get_json(silent=True) or {}
        job_id = body.get("job_id")
        operations = body.get("operations") or []
        if not job_id:
            return jsonify({"error": "job_id is required."}), 400
        payload = get_store().process(job_id, operations)
        payload["message"] = "Processing started. Watch this job on the dashboard."
        return jsonify(payload)
    except KeyError as exc:
        return jsonify({"error": str(exc)}), 404
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400
    except Exception as exc:
        return jsonify({"error": str(exc)}), 500


@pipeline_bp.route("/api/pipeline/chart", methods=["POST"])
def chart_dataset():
    """
    Build a Plotly chart from the cleaned dataset
    ---
    tags:
      - Data Studio
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            job_id:
              type: string
            chart_type:
              type: string
            x:
              type: string
            y:
              type: string
    responses:
      200:
        description: Plotly figure JSON
    """
    try:
        body = request.get_json(silent=True) or {}
        job_id = body.get("job_id")
        if not job_id:
            return jsonify({"error": "job_id is required."}), 400
        job = get_store().get(job_id)
        figure = build_chart(
            job["cleaned"],
            body.get("chart_type"),
            x=body.get("x"),
            y=body.get("y"),
        )
        return jsonify({"figure": figure, "message": "Chart generated."})
    except KeyError as exc:
        return jsonify({"error": str(exc)}), 404
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400
    except Exception as exc:
        return jsonify({"error": str(exc)}), 500


@pipeline_bp.route("/api/pipeline/export/<string:job_id>", methods=["GET"])
def export_dataset(job_id):
    """
    Download the cleaned dataset as CSV or Excel
    ---
    tags:
      - Data Studio
    parameters:
      - name: job_id
        in: path
        type: string
        required: true
      - name: format
        in: query
        type: string
        enum: [csv, xlsx]
        default: csv
    responses:
      200:
        description: Cleaned file download
      404:
        description: Job not found
    """
    try:
        export_format = request.args.get("format", "csv")
        buffer, filename, mime = get_store().export_bytes(job_id, export_format)
        return send_file(buffer, as_attachment=True, download_name=filename, mimetype=mime)
    except KeyError as exc:
        return jsonify({"error": str(exc)}), 404
    except Exception as exc:
        return jsonify({"error": str(exc)}), 500


@pipeline_bp.route("/api/pipeline/jobs/<string:job_id>/record", methods=["GET"])
def get_job_record(job_id):
    """
    Return a single row so the dashboard can step through the sheet one record at a time
    ---
    tags:
      - Data Studio
    parameters:
      - name: job_id
        in: path
        type: string
        required: true
      - name: source
        in: query
        type: string
        enum: [original, cleaned]
        default: cleaned
      - name: index
        in: query
        type: integer
        default: 0
    responses:
      200:
        description: One record and pager metadata
    """
    try:
        source = request.args.get("source", "cleaned")
        index = request.args.get("index", 0, type=int)
        return jsonify(get_store().get_record(job_id, source, index))
    except KeyError as exc:
        return jsonify({"error": str(exc)}), 404
    except Exception as exc:
        return jsonify({"error": str(exc)}), 500


@pipeline_bp.route("/api/pipeline/jobs/<string:job_id>/workbook", methods=["GET"])
def download_workbook(job_id):
    """
    Download the job as an Excel workbook so it can be opened in Excel
    ---
    tags:
      - Data Studio
    parameters:
      - name: job_id
        in: path
        type: string
        required: true
      - name: source
        in: query
        type: string
        enum: [original, cleaned]
        default: cleaned
    responses:
      200:
        description: Excel file
    """
    try:
        source = request.args.get("source", "cleaned")
        buffer, filename, mime = get_store().workbook_bytes(job_id, source)
        return send_file(buffer, as_attachment=True, download_name=filename, mimetype=mime)
    except KeyError as exc:
        return jsonify({"error": str(exc)}), 404
    except Exception as exc:
        return jsonify({"error": str(exc)}), 500


@pipeline_bp.route("/api/pipeline/explore", methods=["POST"])
def explore_dataset():
    """
    Run one ServiceFunctions inspect method on the uploaded or cleaned sheet
    ---
    tags:
      - Data Studio
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            job_id:
              type: string
            source:
              type: string
            method:
              type: string
            n:
              type: integer
            column:
              type: string
            column2:
              type: string
            ascending:
              type: boolean
    responses:
      200:
        description: Inspect result
    """
    try:
        body = request.get_json(silent=True) or {}
        job_id = body.get("job_id")
        if not job_id:
            return jsonify({"error": "job_id is required."}), 400
        payload = get_store().run_explore(
            job_id,
            body.get("source", "cleaned"),
            body.get("method"),
            {
                "n": body.get("n", 10),
                "column": body.get("column"),
                "column2": body.get("column2"),
                "ascending": body.get("ascending", True),
            },
        )
        payload["message"] = f"Ran ServiceFunctions.{payload['service_method']}"
        return jsonify(payload)
    except KeyError as exc:
        return jsonify({"error": str(exc)}), 404
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400
    except Exception as exc:
        return jsonify({"error": str(exc)}), 500
