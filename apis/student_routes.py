from flask import Blueprint, render_template, jsonify
from ServiceFunctions import ServiceFunctions, getCSVData
from configs.dataset_config import dataset_config

# Create Blueprint for student routes
student_bp = Blueprint('student', __name__)

# Initialize service functions
functions = ServiceFunctions()

# Dataset path - now using centralized configuration
studentDataSetPath = dataset_config.student_dataset_path

def getStudentDataSet():
    """Extract dataset values and return first ten records"""
    try:
        data = functions.getCsvDataSetInfoForFirstTenRecords(studentDataSetPath)
        return data
    except Exception as e:
        return f"<p>Error: File not found: {studentDataSetPath}, Reason: {e}</p>"

def getStudentDataRaw():
    """Get first 10 student records as raw data"""
    try:
        data = getCSVData(studentDataSetPath)
        return data.head(10)
    except Exception as e:
        return None

@student_bp.route('/studentsInfo')
def studentInformation():
    """
    Get student performance data
    ---
    tags:
      - Students
    responses:
      200:
        description: Student performance data table
        schema:
          type: string
    """
    data = getStudentDataSet()
    return render_template("studentInfo.html", table_data=data)

# JSON API endpoints
@student_bp.route('/api/students/head')
def studentsDataHead():
    """
    Get first 10 student records as JSON
    ---
    tags:
      - Students API
    responses:
      200:
        description: First 10 student records in JSON format
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
        data = getStudentDataRaw()
        if data is not None:
            # Convert DataFrame to JSON-serializable format
            records = data.to_dict('records')
            return jsonify({
                "data": records,
                "count": len(records),
                "message": "Successfully retrieved first 10 student records"
            })
        else:
            return jsonify({"error": "Failed to load student data"}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@student_bp.route('/api/students/all')
def studentsDataAll():
    """
    Get all student records as JSON
    ---
    tags:
      - Students API
    responses:
      200:
        description: All student records in JSON format
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
        data = getCSVData(studentDataSetPath)
        if data is not None:
            # Convert DataFrame to JSON-serializable format
            records = data.to_dict('records')
            return jsonify({
                "data": records,
                "count": len(records),
                "message": "Successfully retrieved all student records"
            })
        else:
            return jsonify({"error": "Failed to load student data"}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500
