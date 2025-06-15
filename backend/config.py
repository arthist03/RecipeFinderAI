import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    """Base configuration class"""
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-this')
    MONGODB_URI = os.getenv('MONGODB_URI')
    
    # AI Model settings
    MAX_INGREDIENTS = 20
    MIN_INGREDIENTS = 2
    AI_RESPONSE_TIMEOUT = 30  # seconds
    
    # Cache settings
    CACHE_RECIPES_FOR = 3600  # 1 hour in seconds

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    TESTING = False

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    TESTING = False

# Choose config based on environment
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}