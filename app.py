import os

from flask import Flask
from flasgger import Swagger

# Import configurations
from configs.swagger_config import swagger_config, swagger_template

# Import routes
from apis.routes import register_blueprints

def create_app():
    """Application factory pattern"""
    app = Flask(__name__)
    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-data-studio-key")
    app.config["UPLOAD_FOLDER"] = os.path.join(os.getcwd(), "uploads")
    app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
    
    # Initialize Swagger
    swagger = Swagger(app, config=swagger_config, template=swagger_template)
    
    # Register all API blueprints
    register_blueprints(app)
    
    return app

# Create the Flask app
app = create_app()

if __name__ == '__main__':
   
    # Run the app
    app.run(debug=True, host='0.0.0.0', port=5003)
