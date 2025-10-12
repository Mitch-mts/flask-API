from flask import Blueprint, jsonify, request
from ServiceFunctions import ServiceFunctions, getData, getExcelData
from configs.dataset_config import dataset_config

# Create Blueprint for dataset routes
dataset_bp = Blueprint('dataset', __name__)

# Initialize service functions
functions = ServiceFunctions()

# Dataset path - now using centralized configuration
athletesDataSetPath = dataset_config.athletes_dataset_path

@dataset_bp.route('/api/dataset/shape')
def getDatasetShape():
    """
    Get dataset shape information
    ---
    tags:
      - Dataset Info
    responses:
      200:
        description: Dataset shape
        schema:
          type: object
          properties:
            shape:
              type: array
              items:
                type: integer
    """
    try:
        shape = functions.getDataSetShape(athletesDataSetPath)
        return jsonify({"shape": shape})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@dataset_bp.route('/api/dataset/unique-values/<string:columnName>', methods=['GET'])
def getUniqueValues(columnName):
    """
    Get unique values from NOC column
    ---
    tags:
      - Dataset Info
    parameters:
      - name: columnName
        in: path
        type: string
        required: true
        description: Name of the column to get value counts for
        example: "NOC"
    responses:
      200:
        description: Unique NOC values
        schema:
          type: object
          properties:
            unique_values:
              type: array
              items:
                type: string
    """
    try:
        unique_values = functions.getUniqueColumnValues(athletesDataSetPath, columnName)
        return jsonify({"unique_values": unique_values.tolist()})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@dataset_bp.route('/api/dataset/column-counts/<string:columnName>', methods=['GET'])
def getColumnCounts(columnName):
    """
    Get value counts for any column
    ---
    tags:
      - Dataset Info
    parameters:
      - name: columnName
        in: path
        type: string
        required: true
        description: Name of the column to get value counts for
        example: "NOC"
    responses:
      200:
        description: Column value counts
        schema:
          type: object
          properties:
            value_counts:
              type: object
              description: Dictionary with column values as keys and their counts as values
              example: {"USA": 2052, "China": 1656, "Russia": 1327}
      400:
        description: Bad request - Invalid column name
        schema:
          type: object
          properties:
            error:
              type: string
              example: "Column 'InvalidColumn' not found in dataset"
      500:
        description: Internal server error
        schema:
          type: object
          properties:
            error:
              type: string
              example: "Failed to process request"
    """
    try:
        counts = functions.getColumnValueCount(athletesDataSetPath, columnName)
        return jsonify({"value_counts": counts.to_dict()})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Additional JSON endpoints for dataset exploration
@dataset_bp.route('/api/dataset/columns')
def getDatasetColumns():
    """
    Get dataset column information
    ---
    tags:
      - Dataset Info
    responses:
      200:
        description: Dataset column information
        schema:
          type: object
          properties:
            columns:
              type: array
              items:
                type: string
            dtypes:
              type: object
    """
    try:
        data = getData(athletesDataSetPath)
        if data is not None:
            return jsonify({
                "columns": data.columns.tolist(),
                "dtypes": data.dtypes.astype(str).to_dict(),
                "message": "Successfully retrieved column information"
            })
        else:
            return jsonify({"error": "Failed to load dataset"}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@dataset_bp.route('/api/dataset/sample')
def getDatasetSample():
    """
    Get a sample of dataset records
    ---
    tags:
      - Dataset Info
    parameters:
      - name: size
        in: query
        type: integer
        default: 5
        description: Number of records to return
    responses:
      200:
        description: Sample dataset records
        schema:
          type: object
          properties:
            data:
              type: array
              items:
                type: object
            count:
              type: integer
            message:
              type: string
    """
    try:
        size = request.args.get('size', 5, type=int)
        data = getData(athletesDataSetPath)
        if data is not None:
            sample_data = data.sample(n=min(size, len(data)))
            records = sample_data.to_dict('records')
            return jsonify({
                "data": records,
                "count": len(records),
                "message": f"Successfully retrieved {len(records)} sample records"
            })
        else:
            return jsonify({"error": "Failed to load dataset"}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@dataset_bp.route('/api/dataset/paginated')
def getDatasetPaginated():
    """
    Get paginated dataset records
    ---
    tags:
      - Dataset Info
    parameters:
      - name: page
        in: query
        type: integer
        default: 1
        description: Page number (1-based)
      - name: per_page
        in: query
        type: integer
        default: 10
        description: Records per page
    responses:
      200:
        description: Paginated dataset records
        schema:
          type: object
          properties:
            data:
              type: array
              items:
                type: object
            pagination:
              type: object
              properties:
                page:
                  type: integer
                per_page:
                  type: integer
                total:
                  type: integer
                pages:
                  type: integer
            message:
              type: string
    """
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        
        data = getData(athletesDataSetPath)
        if data is not None:
            total_records = len(data)
            total_pages = (total_records + per_page - 1) // per_page
            
            # Ensure page is within valid range
            page = max(1, min(page, total_pages))
            
            start_idx = (page - 1) * per_page
            end_idx = start_idx + per_page
            
            page_data = data.iloc[start_idx:end_idx]
            records = page_data.to_dict('records')
            
            return jsonify({
                "data": records,
                "count": len(records),
                "pagination": {
                    "page": page,
                    "per_page": per_page,
                    "total": total_records,
                    "pages": total_pages
                },
                "message": f"Successfully retrieved page {page} of {total_pages}"
            })
        else:
            return jsonify({"error": "Failed to load dataset"}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@dataset_bp.route('/api/dataset/config')
def getDatasetConfig():
    """
    Get dataset configuration information
    ---
    tags:
      - Dataset Info
    responses:
      200:
        description: Dataset configuration information
        schema:
          type: object
          properties:
            base_directory:
              type: string
            athletes_path:
              type: string
            validation:
              type: object
            message:
              type: string
    """
    try:
        validation_result = dataset_config.validate_data_directory()
        return jsonify({
            "base_directory": dataset_config.base_data_dir,
            "athletes_path": dataset_config.athletes_dataset_path,
            "validation": validation_result,
            "message": "Dataset configuration retrieved successfully"
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500
