from flask import Flask, jsonify
from flask_cors import CORS
from config import Config
from utils.database import db_connection
from routes.recipe_routes import recipe_bp
from routes.user_routes import user_bp
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Enable CORS for React frontend
    CORS(app, origins=["http://localhost:3000", "http://localhost:5173"])
    
    # Initialize database connection
    try:
        db_connection.connect()
        logger.info("Database connected successfully")
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
    
    # Register blueprints
    app.register_blueprint(recipe_bp, url_prefix=f'/api/{Config.API_VERSION}/recipes')
    app.register_blueprint(user_bp, url_prefix=f'/api/{Config.API_VERSION}/users')
    
    # Health check endpoint
    @app.route('/health')
    def health_check():
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.utcnow().isoformat(),
            'version': Config.API_VERSION
        })
    
    # Root endpoint
    @app.route('/')
    def root():
        return jsonify({
            'message': 'Recipe AI Backend API',
            'version': Config.API_VERSION,
            'endpoints': {
                'health': '/health',
                'recipes': f'/api/{Config.API_VERSION}/recipes',
                'users': f'/api/{Config.API_VERSION}/users'
            }
        })
    
    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'error': 'Endpoint not found'}), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        logger.error(f"Internal server error: {error}")
        return jsonify({'error': 'Internal server error'}), 500
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=Config.FLASK_ENV == 'development', host='0.0.0.0', port=5000)