from flask import Flask
from flask_cors import CORS
from flask_pymongo import PyMongo
from config import config
import os
import logging

# Initialize extensions
mongo = PyMongo()

def create_app(config_name=None):
    """Application factory pattern"""
    if config_name is None:
        config_name = os.getenv('FLASK_ENV', 'development')
    
    app = Flask(__name__)
    
    # Load configuration
    app.config.from_object(config[config_name])
    
    # Initialize extensions
    mongo.init_app(app)
    
    # Configure CORS for your React frontend
    CORS(app, origins=[
        'http://localhost:5173',  # Vite default port
        'http://localhost:3000',  # React default port
        'http://127.0.0.1:5173',
        'http://127.0.0.1:3000'
    ])
    
    # Set up logging
    if not app.debug:
        logging.basicConfig(level=logging.INFO)
    
    # Register blueprints
    from routes.recipe_routes import recipe_bp
    from routes import health_bp
    
    app.register_blueprint(health_bp, url_prefix='/api')
    app.register_blueprint(recipe_bp, url_prefix='/api/recipes')
    
    # Root endpoint
    @app.route('/')
    def index():
        return {
            'message': 'Welcome to RecipeFinder Backend! 🍳',
            'status': 'running',
            'version': '1.0.0'
        }
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)