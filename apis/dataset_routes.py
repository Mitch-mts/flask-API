from flask import Blueprint, jsonify, request
from ServiceFunctions import ServiceFunctions, getExcelData

# Create Blueprint for dataset routes
dataset_bp = Blueprint('dataset', __name__)

# Initialize service functions
functions = ServiceFunctions()

# Dataset path
athletesDataSetPath = "./data/Athletes.xlsx"

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

@dataset_bp.route('/api/dataset/unique-values')
def getUniqueValues():
    """
    Get unique values from NOC column
    ---
    tags:
      - Dataset Info
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
        unique_values = functions.getUniqueColumnValues(athletesDataSetPath)
        return jsonify({"unique_values": unique_values.tolist()})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@dataset_bp.route('/api/dataset/column-counts')
def getColumnCounts():
    """
    Get value counts for NOC column
    ---
    tags:
      - Dataset Info
    responses:
      200:
        description: NOC column value counts
        schema:
          type: object
          properties:
            value_counts:
              type: object
    """
    try:
        counts = functions.getColumnValueCount(athletesDataSetPath)
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
        data = getExcelData(athletesDataSetPath)
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
        data = getExcelData(athletesDataSetPath)
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
        
        data = getExcelData(athletesDataSetPath)
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
