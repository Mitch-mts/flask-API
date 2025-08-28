from flask import Blueprint, render_template, jsonify
from ServiceFunctions import ServiceFunctions, getExcelData

# Create Blueprint for athlete routes
athlete_bp = Blueprint('athlete', __name__)

# Initialize service functions
functions = ServiceFunctions()

# Dataset path
athletesDataSetPath = "./data/Athletes.xlsx"

def getAthletesInfoFromTheHead():
    """Get first 10 athlete records"""
    try:
        data = functions.getExcelDataSetInfoForFirstTenRecords(athletesDataSetPath)
        return data
    except Exception as e:
        return f"<p>Error: File not found: {athletesDataSetPath}, Reason: {e}</p>"

def getAthletesInfoFromTheTail():
    """Get last 10 athlete records"""
    try:
        data = functions.getExcelDataSetInfoForLastTenRecords(athletesDataSetPath)
        return data
    except Exception as e:
        return f"<p>Error: File not found: {athletesDataSetPath}, Reason: {e}</p>"

def getAthletesDataFromHead():
    """Get first 10 athlete records as raw data"""
    try:
        data = getExcelData(athletesDataSetPath)
        return data.head(10)
    except Exception as e:
        return None

def getAthletesDataFromTail():
    """Get last 10 athlete records as raw data"""
    try:
        data = getExcelData(athletesDataSetPath)
        return data.tail(10)
    except Exception as e:
        return None

@athlete_bp.route('/athletesInfoHead')
def athletesInformationHead():
    """
    Get first 10 athlete records
    ---
    tags:
      - Athletes
    responses:
      200:
        description: First 10 athlete records
        schema:
          type: string
    """
    data = getAthletesInfoFromTheHead()
    return render_template("athletesInfo.html", table_data=data)

@athlete_bp.route('/athletesInfoTail')
def athletesInformationTail():
    """
    Get last 10 athlete records
    ---
    tags:
      - Athletes
    responses:
      200:
        description: Last 10 athlete records
        schema:
          type: string
    """
    data = getAthletesInfoFromTheTail()
    return render_template("athletesInfo.html", table_data=data)

# JSON API endpoints
@athlete_bp.route('/api/athletes/head')
def athletesDataHead():
    """
    Get first 10 athlete records as JSON
    ---
    tags:
      - Athletes API
    responses:
      200:
        description: First 10 athlete records in JSON format
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
        data = getAthletesDataFromHead()
        if data is not None:
            # Convert DataFrame to JSON-serializable format
            records = data.to_dict('records')
            return jsonify({
                "data": records,
                "count": len(records),
                "message": "Successfully retrieved first 10 athlete records"
            })
        else:
            return jsonify({"error": "Failed to load athlete data"}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@athlete_bp.route('/api/athletes/tail')
def athletesDataTail():
    """
    Get last 10 athlete records as JSON
    ---
    tags:
      - Athletes API
    responses:
      200:
        description: Last 10 athlete records in JSON format
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
        data = getAthletesDataFromTail()
        if data is not None:
            # Convert DataFrame to JSON-serializable format
            records = data.to_dict('records')
            return jsonify({
                "data": records,
                "count": len(records),
                "message": "Successfully retrieved last 10 athlete records"
            })
        else:
            return jsonify({"error": "Failed to load athlete data"}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@athlete_bp.route('/api/athletes/all')
def athletesDataAll():
    """
    Get all athlete records as JSON
    ---
    tags:
      - Athletes API
    responses:
      200:
        description: All athlete records in JSON format
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
        data = getExcelData(athletesDataSetPath)
        if data is not None:
            # Convert DataFrame to JSON-serializable format
            records = data.to_dict('records')
            return jsonify({
                "data": records,
                "count": len(records),
                "message": "Successfully retrieved all athlete records"
            })
        else:
            return jsonify({"error": "Failed to load athlete data"}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500
