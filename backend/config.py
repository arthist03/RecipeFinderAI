import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    MONGODB_URI = os.getenv('MONGODB_URI')
    DATABASE_NAME = os.getenv('DATABASE_NAME', 'recipe_app')
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key')
    FLASK_ENV = os.getenv('FLASK_ENV', 'development')
    API_VERSION = os.getenv('API_VERSION', 'v1')
    
    # Vector search configuration
    VECTOR_DIMENSION = 384  # Sentence transformer default
    SIMILARITY_THRESHOLD = 0.7
    MAX_RESULTS = 10