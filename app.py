import os

from flask import Flask, jsonify
from flasgger import Swagger
from werkzeug.exceptions import RequestEntityTooLarge

# Import configurations
from configs.swagger_config import swagger_config, swagger_template

# Import routes
from apis.routes import register_blueprints

def create_app():
    """Application factory pattern"""
    app = Flask(__name__)
    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-data-studio-key")
    app.config["UPLOAD_FOLDER"] = os.path.join(os.getcwd(), "uploads")
    # Allow large CSV/Excel uploads. Werkzeug 3 also caps in-memory form fields
    # at 500 KB by default, which raises 413 "data value transmitted exceeds
    # the capacity limit" even when MAX_CONTENT_LENGTH is higher.
    max_upload_bytes = int(os.environ.get("MAX_UPLOAD_BYTES", 64 * 1024 * 1024))
    app.config["MAX_CONTENT_LENGTH"] = max_upload_bytes
    app.config["MAX_FORM_MEMORY_SIZE"] = max_upload_bytes
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

    @app.errorhandler(RequestEntityTooLarge)
    def file_too_large(_error):
        limit_mb = max_upload_bytes // (1024 * 1024)
        return jsonify({
            "error": f"File is too large. Maximum upload size is {limit_mb} MB."
        }), 413
    
    # Initialize Swagger
    swagger = Swagger(app, config=swagger_config, template=swagger_template)
    
    # Register all API blueprints
    register_blueprints(app)
    
    return app

# Create the Flask app
app = create_app()

if __name__ == '__main__':
   
    # Run the app
    app.run(debug=True, host='0.0.0.0', port=5001)
