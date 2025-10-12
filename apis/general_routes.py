from flask import Blueprint, jsonify
from ServiceFunctions import ServiceFunctions

# Create Blueprint for general routes
general_bp = Blueprint('general', __name__)

# Initialize service functions
functions = ServiceFunctions()

@general_bp.route('/')
def helloWorld():
    """
    Root endpoint
    ---
    tags:
      - General
    responses:
      200:
        description: Welcome message
        schema:
          type: string
    """
    return "Hello, from your Flask Data Analysis API!"

@general_bp.route('/api/hello')
def hello():
    """
    Test endpoint
    ---
    tags:
      - General
    responses:
      200:
        description: Success message
        schema:
          type: object
          properties:
            message:
              type: string
    """
    response = functions.hello_world()
    return jsonify({"message": response})

    """
    API information endpoint
    ---
    tags:
      - General
    responses:
      200:
        description: API information and available endpoints
        schema:
          type: object
          properties:
            name:
              type: string
            description:
              type: string
            version:
              type: string
            endpoints:
              type: object
    """
    return jsonify({
        "name": "Flask Data Analysis API",
        "description": "A Flask API for analyzing student performance and athlete data",
        "version": "1.0.0",
        "endpoints": {
            "general": [
                "GET / - Welcome message",
                "GET /api/hello - Test endpoint",
                "GET /api/health - Health check",
                "GET /api/info - API information"
            ],
            "students": [
                "GET /studentsInfo - Student data (HTML)",
                "GET /api/students/head - First 10 students (JSON)",
                "GET /api/students/all - All students (JSON)"
            ],
            "athletes": [
                "GET /athletesInfoHead - First 10 athletes (HTML)",
                "GET /athletesInfoTail - Last 10 athletes (HTML)",
                "GET /api/athletes/head - First 10 athletes (JSON)",
                "GET /api/athletes/tail - Last 10 athletes (JSON)",
                "GET /api/athletes/all - All athletes (JSON)"
            ],
            "dataset": [
                "GET /api/dataset/shape - Dataset dimensions",
                "GET /api/dataset/unique-values - Unique NOC values",
                "GET /api/dataset/column-counts - Column value counts",
                "GET /api/dataset/columns - Column information",
                "GET /api/dataset/sample - Random sample records",
                "GET /api/dataset/paginated - Paginated records"
            ]
        },
        "documentation": "/apidocs/"
    })
