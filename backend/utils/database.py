from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
import logging
from config import Config

logger = logging.getLogger(__name__)

class DatabaseConnection:
    _instance = None
    _client = None
    _db = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def connect(self):
        try:
            self._client = MongoClient(Config.MONGODB_URI)
            self._db = self._client[Config.DATABASE_NAME]
            
            # Test connection
            self._client.admin.command('ping')
            logger.info("Successfully connected to MongoDB Atlas")
            
            # Create indexes
            self._create_indexes()
            
            return self._db
        except ConnectionFailure as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            raise
    
    def _create_indexes(self):
        """Create necessary indexes for optimal performance"""
        try:
            # Text index for recipe search
            self._db.recipes.create_index([
                ("name", "text"),
                ("description", "text"),
                ("ingredients", "text"),
                ("tags", "text")
            ])
            
            # Vector search index (Atlas Search)
            # This needs to be created in MongoDB Atlas UI
            # Index name: "vector_search"
            # Field mappings: ingredientVector (knnVector, dimensions: 384)
            
            # Regular indexes
            self._db.recipes.create_index("rating")
            self._db.recipes.create_index("cookTime")
            self._db.recipes.create_index("difficulty")
            self._db.users.create_index("email", unique=True)
            
            logger.info("Database indexes created successfully")
        except Exception as e:
            logger.warning(f"Index creation warning: {e}")
    
    @property
    def db(self):
        if self._db is None:
            self.connect()
        return self._db
    
    def close(self):
        if self._client:
            self._client.close()

# Global database instance
db_connection = DatabaseConnection()