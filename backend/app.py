from flask import Flask, jsonify, request
from flask_cors import CORS
from config import Config
from utils.database import db_connection
from routes.recipe_routes import recipe_bp
from routes.user_routes import user_bp
import logging
from datetime import datetime
import os

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('app.log') if os.path.exists('.') else logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def create_app():
    """Create and configure Flask application"""
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Enable CORS for React frontend
    CORS(app, 
         origins=Config.CORS_ORIGINS,
         methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
         allow_headers=['Content-Type', 'Authorization'],
         supports_credentials=True)
    
    # Initialize database connection
    try:
        db_connection.connect()
        logger.info("Database connected successfully")
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        # Continue without database - some features will be limited
    
    # Register blueprints
    app.register_blueprint(recipe_bp, url_prefix=f'/api/{Config.API_VERSION}/recipes')
    app.register_blueprint(user_bp, url_prefix=f'/api/{Config.API_VERSION}/users')
    
    # Root endpoint
    @app.route('/')
    def root():
        """API root endpoint with information"""
        return jsonify({
            'message': 'Recipe AI Backend API',
            'version': Config.API_VERSION,
            'status': 'running',
            'endpoints': {
                'health': '/health',
                'recipes': f'/api/{Config.API_VERSION}/recipes',
                'users': f'/api/{Config.API_VERSION}/users'
            },
            'documentation': {
                'search_recipes': f'/api/{Config.API_VERSION}/recipes/search',
                'popular_recipes': f'/api/{Config.API_VERSION}/recipes/popular',
                'random_recipe': f'/api/{Config.API_VERSION}/recipes/random'
            }
        })
    
    # Health check endpoint
    @app.route('/health')
    def health_check():
        """Comprehensive health check"""
        try:
            # Check database health
            db_health = db_connection.health_check()
            
            # Check AI service health
            from services.ai_service import ai_service
            ai_health = {
                "status": "healthy" if ai_service.embedding_model else "degraded",
                "embedding_model": "loaded" if ai_service.embedding_model else "not_loaded",
                "prediction_model": "loaded" if ai_service.model else "not_loaded"
            }
            
            # Overall health status
            overall_status = "healthy"
            if db_health.get("status") != "healthy":
                overall_status = "degraded"
            if ai_health.get("status") != "healthy":
                overall_status = "degraded" if overall_status == "healthy" else "unhealthy"
            
            return jsonify({
                'status': overall_status,
                'timestamp': datetime.utcnow().isoformat(),
                'version': Config.API_VERSION,
                'services': {
                    'database': db_health,
                    'ai_service': ai_health
                },
                'environment': Config.FLASK_ENV
            })
            
        except Exception as e:
            logger.error(f"Health check error: {e}")
            return jsonify({
                'status': 'unhealthy',
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }), 500
    
    # Global error handlers
    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            'error': 'Bad request',
            'message': 'The request could not be understood by the server',
            'code': 'BAD_REQUEST'
        }), 400
    
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            'error': 'Endpoint not found',
            'message': 'The requested resource could not be found',
            'code': 'NOT_FOUND'
        }), 404
    
    @app.errorhandler(405)
    def method_not_allowed(error):
        return jsonify({
            'error': 'Method not allowed',
            'message': 'The method is not allowed for the requested URL',
            'code': 'METHOD_NOT_ALLOWED'
        }), 405
    
    @app.errorhandler(500)
    def internal_error(error):
        logger.error(f"Internal server error: {error}")
        return jsonify({
            'error': 'Internal server error',
            'message': 'An unexpected error occurred',
            'code': 'INTERNAL_ERROR'
        }), 500
    
    # Request logging middleware
    @app.before_request
    def log_request_info():
        if request.endpoint != 'health_check':  # Don't log health checks
            logger.info(f"Request: {request.method} {request.url} from {request.remote_addr}")
    
    @app.after_request
    def log_response_info(response):
        if request.endpoint != 'health_check':  # Don't log health check responses
            logger.info(f"Response: {response.status_code} for {request.method} {request.url}")
        return response
    
    # CORS preflight handler
    @app.before_request
    def handle_preflight():
        if request.method == "OPTIONS":
            response = jsonify({'status': 'ok'})
            response.headers.add("Access-Control-Allow-Origin", "*")
            response.headers.add('Access-Control-Allow-Headers', "Content-Type,Authorization")
            response.headers.add('Access-Control-Allow-Methods', "GET,PUT,POST,DELETE,OPTIONS")
            return response
    
    return app

def main():
    """Main application entry point"""
    try:
        # Create Flask app
        app = create_app()
        
        # Get configuration
        host = os.getenv('FLASK_HOST', '0.0.0.0')
        port = int(os.getenv('FLASK_PORT', 5000))
        debug = Config.FLASK_ENV == 'development'
        
        logger.info(f"Starting Recipe AI Backend on {host}:{port}")
        logger.info(f"Environment: {Config.FLASK_ENV}")
        logger.info(f"Debug mode: {debug}")
        
        # Run the application
        app.run(
            host=host,
            port=port,
            debug=debug,
            threaded=True
        )
        
    except Exception as e:
        logger.error(f"Failed to start application: {e}")
        raise

if __name__ == '__main__':
    main()