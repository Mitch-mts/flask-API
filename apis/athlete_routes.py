from flask import Blueprint, render_template, jsonify
from ServiceFunctions import ServiceFunctions, getData

# Create Blueprint for athlete routes
athlete_bp = Blueprint('athlete', __name__)

# Initialize service functions
functions = ServiceFunctions()

# Dataset path
athletesDataSetPath = "./data/Athletes.xlsx"

def getAthletesInfoFromTheHead(numberOfRecords):
    """Get first 10 athlete records"""
    try:
        data = functions.getHeadDataInfo(athletesDataSetPath, numberOfRecords)
        return data
    except Exception as e:
        return f"<p>Error: File not found: {athletesDataSetPath}, Reason: {e}</p>"

def getAthletesInfoFromTheTail(numberOfRecords):
    """Get last 10 athlete records"""
    try:
        data = functions.getTailDataInfo(athletesDataSetPath, numberOfRecords)
        return data
    except Exception as e:
        return f"<p>Error: File not found: {athletesDataSetPath}, Reason: {e}</p>"

def getAthletesDataFromHead(numberOfRecords):
    try:
        data = getData(athletesDataSetPath)
        print('data form service layer', data)
        print('numberOfRecords:', numberOfRecords, type(numberOfRecords))
        return data.head(numberOfRecords)
    except Exception as e:
        print(f"Error in getAthletesDataFromHead: {e}")
        return None

def getAthletesDataFromTail(numberOfRecords):
    """Get last N athlete records as raw data"""
    try:
        data = getData(athletesDataSetPath)
        return data.tail(numberOfRecords)
    except Exception as e:
        print(f"Error in getAthletesDataFromTail: {e}")
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
@athlete_bp.route('/api/athletes/head/<int:numberOfRecords>', methods=['GET'])
def athletesDataHead(numberOfRecords):
    """
    Get the first N athlete records as JSON
    ---
    tags:
      - Athletes API
    parameters:
      - name: numberOfRecords
        in: path
        type: integer
        required: true
        description: Number of athlete records to retrieve from the beginning of the dataset
        minimum: 1
        maximum: 1000
        example: 10
    responses:
      200:
        description: Successfully retrieved the first N athlete records
        schema:
          type: object
          properties:
            data:
              type: array
              description: Array of athlete records
              items:
                type: object
                description: Individual athlete record with all fields
            count:
              type: integer
              description: Number of records returned
              example: 10
            message:
              type: string
              description: Success message
              example: "Successfully retrieved first 10 athlete records"
        example:
          data: [{"ID": 1, "Name": "John Doe", "Sex": "M", "Age": 25, "Height": 180, "Weight": 75, "Team": "USA", "NOC": "USA", "Games": "2016 Summer", "Year": 2016, "Season": "Summer", "City": "Rio de Janeiro", "Sport": "Athletics", "Event": "100m", "Medal": "Gold"}]
          count: 1
          message: "Successfully retrieved first 1 athlete records"
      400:
        description: Bad request - Invalid parameter
        schema:
          type: object
          properties:
            error:
              type: string
              example: "Invalid number of records"
      404:
        description: Dataset not found
        schema:
          type: object
          properties:
            error:
              type: string
              example: "Athlete dataset not found"
      500:
        description: Internal server error
        schema:
          type: object
          properties:
            error:
              type: string
              example: "Failed to load athlete data"
    """
    try:
        data = getAthletesDataFromHead(numberOfRecords)
        if data is not None:
            # Convert DataFrame to JSON-serializable format
            records = data.to_dict('records')
            return jsonify({
                "data": records,
                "count": len(records),
                "message": "Successfully retrieved first " + str(numberOfRecords) + " athlete records"
            })
        else:
            return jsonify({"error": "Failed to load athlete data"}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@athlete_bp.route('/api/athletes/tail/<int:numberOfRecords>', methods=['GET'])
def athletesDataTail(numberOfRecords):
    """
    Get the last N athlete records as JSON
    ---
    tags:
      - Athletes API
    parameters:
      - name: numberOfRecords
        in: path
        type: integer
        required: true
        description: Number of athlete records to retrieve from the end of the dataset
        minimum: 1
        maximum: 1000
        example: 10
    responses:
      200:
        description: Successfully retrieved the last N athlete records
        schema:
          type: object
          properties:
            data:
              type: array
              description: Array of athlete records from the end of the dataset
              items:
                type: object
                description: Individual athlete record with all fields
            count:
              type: integer
              description: Number of records returned
              example: 10
            message:
              type: string
              description: Success message
              example: "Successfully retrieved last 10 athlete records"
        example:
          data: [{"ID": 271116, "Name": "Jane Smith", "Sex": "F", "Age": 23, "Height": 165, "Weight": 55, "Team": "Canada", "NOC": "CAN", "Games": "2016 Summer", "Year": 2016, "Season": "Summer", "City": "Rio de Janeiro", "Sport": "Swimming", "Event": "100m Freestyle", "Medal": "Silver"}]
          count: 1
          message: "Successfully retrieved last 1 athlete records"
      400:
        description: Bad request - Invalid parameter
        schema:
          type: object
          properties:
            error:
              type: string
              example: "Invalid number of records"
      404:
        description: Dataset not found
        schema:
          type: object
          properties:
            error:
              type: string
              example: "Athlete dataset not found"
      500:
        description: Internal server error
        schema:
          type: object
          properties:
            error:
              type: string
              example: "Failed to load athlete data"
    """
    try:
        data = getAthletesDataFromTail(numberOfRecords)
        if data is not None:
            # Convert DataFrame to JSON-serializable format
            records = data.to_dict('records')
            return jsonify({
                "data": records,
                "count": len(records),
                "message": "Successfully retrieved last  " + str(numberOfRecords) + "  athlete records"
            })
        else:
            return jsonify({"error": "Failed to load athlete data"}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@athlete_bp.route('/api/athletes/all', methods=['GET'])
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
        data = getData(athletesDataSetPath)
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
