from flask import Flask
from flasgger import Swagger

# Import configurations
from configs.swagger_config import swagger_config, swagger_template

# Import routes
from apis.routes import register_blueprints

# Import utilities
from utils.startup import print_startup_info

def create_app():
    """Application factory pattern"""
    app = Flask(__name__)
    
    # Initialize Swagger
    swagger = Swagger(app, config=swagger_config, template=swagger_template)
    
    # Register all API blueprints
    register_blueprints(app)
    
    return app

# Create the Flask app
app = create_app()

if __name__ == '__main__':
    # Print startup information
    print_startup_info()
    
    # Run the app
    app.run(debug=True, host='0.0.0.0', port=5001)
