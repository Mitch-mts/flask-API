# Routes registry - imports and registers all API blueprints

from .general_routes import general_bp
from .student_routes import student_bp
from .athlete_routes import athlete_bp
from .dataset_routes import dataset_bp

# List of all blueprints to register
blueprints = [
    general_bp,
    student_bp,
    athlete_bp,
    dataset_bp
]

def register_blueprints(app):
    """Register all blueprints with the Flask app"""
    for blueprint in blueprints:
        app.register_blueprint(blueprint)
