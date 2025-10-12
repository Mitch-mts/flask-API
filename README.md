# Flask Data Analysis API

A Flask-based REST API for analyzing student performance and athlete data with integrated Swagger UI documentation.

## Features

- **Student Performance Analysis**: CSV data processing and visualization
- **Athlete Data Analysis**: Excel data processing with head/tail operations
- **Swagger UI**: Interactive API documentation at `/apidocs/`
- **RESTful Endpoints**: JSON responses for API calls
- **Data Visualization**: HTML table rendering for web display
- **Modular Architecture**: Clean separation of concerns with blueprints
- **Dual Format Support**: Both HTML and JSON endpoints available

## Installation

1. **Clone or navigate to the project directory:**
   ```bash
   cd /path/to/flask-API
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

## Running the API

### Option 1: Direct Python execution
```bash
python app.py
```

### Option 2: Flask development server
```bash
export FLASK_APP=app.py
export FLASK_ENV=development
flask run --host=0.0.0.0 --port=5001
```

The API will be available at:
- **Main API**: http://localhost:5001
- **Swagger UI**: http://localhost:5001/apidocs/

## API Endpoints

### General Endpoints
- `GET /` - Welcome message
- `GET /api/hello` - Test endpoint
- `GET /api/health` - Health check
- `GET /api/info` - API information and endpoint list

### Student Data
- `GET /studentsInfo` - Student performance data (HTML table)
- `GET /api/students/head` - First 10 student records (JSON)
- `GET /api/students/all` - All student records (JSON)

### Athlete Data
- `GET /athletesInfoHead` - First 10 athlete records (HTML table)
- `GET /athletesInfoTail` - Last 10 athlete records (HTML table)
- `GET /api/athletes/head` - First 10 athlete records (JSON)
- `GET /api/athletes/tail` - Last 10 athlete records (JSON)
- `GET /api/athletes/all` - All athlete records (JSON)

### Dataset Information
- `GET /api/dataset/shape` - Dataset dimensions
- `GET /api/dataset/unique-values` - Unique NOC values
- `GET /api/dataset/column-counts` - NOC column value counts
- `GET /api/dataset/columns` - Column information and data types
- `GET /api/dataset/sample` - Random sample records (query param: `size`)
- `GET /api/dataset/paginated` - Paginated records (query params: `page`, `per_page`)

## JSON API Response Format

All JSON endpoints return data in a consistent format:

```json
{
  "data": [...],           // Array of records
  "count": 10,             // Number of records returned
  "message": "Success...", // Status message
  "pagination": {          // Only for paginated endpoints
    "page": 1,
    "per_page": 10,
    "total": 11085,
    "pages": 1109
  }
}
```

## Swagger UI

Access the interactive API documentation at `/apidocs/` to:
- View all available endpoints
- Test API calls directly from the browser
- See request/response schemas
- Understand API parameters and responses

## Data Files and Configuration

### Dataset Directory Configuration

The API now uses a **centralized dataset configuration system** that automatically detects the best location for your data files. The system checks for data files in the following priority order:

1. **Environment Variable**: `DATA_DIR` environment variable (highest priority)
2. **System Directories**: `/opt/app/data`, `/usr/local/share/app/data`, `/var/lib/app/data`, `/home/app/data`
3. **Local Directory**: `./data/` (fallback for development)

### Setting Custom Data Directory

#### Option 1: Environment Variable (Recommended)
```bash
export DATA_DIR=/path/to/your/data
python app.py
```

#### Option 2: System Directory
Place your data files in one of these system directories:
- `/opt/app/data/` (common for containerized apps)
- `/usr/local/share/app/data/` (system-wide data directory)
- `/var/lib/app/data/` (alternative system data directory)
- `/home/app/data/` (user-specific data directory)

### Data Files

The API expects the following data files in your configured data directory:
- `StudentPerformance.csv` - Student performance data
- `Athletes.xlsx` - Athlete competition data
- `Coaches.xlsx` - Coach information
- `EntriesGender.xlsx` - Gender-based entry data
- `Medals.xlsx` - Medal information
- `Teams.xlsx` - Team data

### Checking Configuration

You can check your current dataset configuration by calling:
```bash
curl http://localhost:5001/api/dataset/config
```

This endpoint returns:
- Current base data directory
- Paths to all dataset files
- Validation status of the data directory
- List of available and missing files

### Example Configuration Usage

```python
from configs.dataset_config import dataset_config

# Get dataset paths
athletes_path = dataset_config.athletes_dataset_path
student_path = dataset_config.student_dataset_path

# Validate data directory
validation = dataset_config.validate_data_directory()
if validation['valid']:
    print("All data files are available!")
else:
    print(f"Missing files: {validation['missing_files']}")
```

## Project Structure

```
flask-API/
├── app.py                    # Main Flask application (clean and minimal)
├── ServiceFunctions.py       # Data processing functions
├── requirements.txt          # Python dependencies
├── README.md                # This file
├── apis/                    # API route modules
│   ├── __init__.py
│   ├── routes.py            # Blueprint registry
│   ├── general_routes.py    # General endpoints
│   ├── student_routes.py    # Student data endpoints
│   ├── athlete_routes.py    # Athlete data endpoints
│   └── dataset_routes.py    # Dataset info endpoints
├── configs/                  # Configuration files
│   ├── swagger_config.py    # Swagger UI configuration
│   └── dataset_config.py    # Dataset path configuration
├── utils/                    # Utility functions
│   ├── __init__.py
│   └── startup.py           # Startup utilities
├── data/                     # Data files directory
└── templates/                # HTML templates
```

## Architecture Benefits

- **Separation of Concerns**: Each module has a specific responsibility
- **Maintainability**: Easy to add new endpoints or modify existing ones
- **Scalability**: Blueprint-based routing for better organization
- **Configuration Management**: Centralized configuration files
- **Clean Main App**: `app.py` only handles app creation and configuration
- **Dual Format Support**: HTML for web display, JSON for API consumption

## API Usage Examples

### Get first 10 athletes as JSON
```bash
curl http://localhost:5001/api/athletes/head
```

### Get paginated dataset records
```bash
curl "http://localhost:5001/api/dataset/paginated?page=1&per_page=20"
```

### Get random sample of records
```bash
curl "http://localhost:5001/api/dataset/sample?size=5"
```

### Get API information
```bash
curl http://localhost:5001/api/info
```

## Troubleshooting

### Common Issues:

1. **Port already in use:**
   ```bash
   # Kill process using port 5001
   lsof -ti:5001 | xargs kill -9
   ```

2. **Missing dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Data file errors:**
   - Ensure all data files are in the `data/` directory
   - Check file permissions
   - Verify file formats (CSV/Excel)

### Error Handling

The API includes comprehensive error handling for:
- Missing data files
- Invalid file formats
- Data processing errors
- API endpoint errors

## Development

To add new endpoints:

1. **Create a new route file** in the `apis/` directory
2. **Define your blueprint** with the appropriate routes
3. **Add Swagger documentation** in the function docstrings
4. **Register the blueprint** in `apis/routes.py`
5. **Test with the Swagger UI**

### Example of adding a new endpoint:

```python
# apis/new_feature_routes.py
from flask import Blueprint

new_feature_bp = Blueprint('new_feature', __name__)

@new_feature_bp.route('/api/new-feature')
def new_feature():
    """
    New feature endpoint
    ---
    tags:
      - New Feature
    responses:
      200:
        description: Success
    """
    return {"message": "New feature works!"}
```

Then add it to `apis/routes.py`:
```python
from .new_feature_routes import new_feature_bp

blueprints = [
    # ... existing blueprints ...
    new_feature_bp
]
```

## License

This project is open source and available under the MIT License.
