import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # MongoDB Configuration
    MONGODB_URI = os.getenv('MONGODB_URI')
    DATABASE_NAME = os.getenv('DATABASE_NAME', 'recipe_app')
    
    # Collections
    RECIPES_COLLECTION = 'recipes'
    SEARCHES_COLLECTION = 'searches'
    USERS_COLLECTION = 'users'
    FAVORITES_COLLECTION = 'favorites'
    
    # Flask Configuration
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    FLASK_ENV = os.getenv('FLASK_ENV', 'development')
    API_VERSION = os.getenv('API_VERSION', 'v1')
    
    # Vector Search Configuration
    VECTOR_INDEX_NAME = 'recipe_vector_search'
    VECTOR_DIMENSION = 384  # sentence-transformers/all-MiniLM-L6-v2
    SIMILARITY_THRESHOLD = 0.7
    MAX_RESULTS = 10
    
    # AI Model Configuration
    AI_MODEL_PATH = 'ai_models/recipe_model.pkl'
    EMBEDDING_MODEL = 'sentence-transformers/all-MiniLM-L6-v2'
    
    # CORS Configuration
    CORS_ORIGINS = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173"
    ]