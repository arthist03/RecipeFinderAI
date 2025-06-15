from pymongo import MongoClient, ASCENDING, DESCENDING, TEXT
from pymongo.errors import ConnectionFailure, OperationFailure
import logging
from config import Config
from services.vector_search import vector_search_service

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
        """Establish connection to MongoDB Atlas"""
        try:
            if not Config.MONGODB_URI:
                raise ValueError("MONGODB_URI not configured")
            
            self._client = MongoClient(
                Config.MONGODB_URI,
                serverSelectionTimeoutMS=5000,  # 5 second timeout
                connectTimeoutMS=10000,         # 10 second connection timeout
                maxPoolSize=50,                 # Maximum connection pool size
                retryWrites=True               # Enable retryable writes
            )
            
            self._db = self._client[Config.DATABASE_NAME]
            
            # Test connection
            self._client.admin.command('ping')
            logger.info(f"Successfully connected to MongoDB Atlas database: {Config.DATABASE_NAME}")
            
            # Initialize database structure
            self._initialize_database()
            
            # Set database connection for vector search service
            vector_search_service.set_database(self._db)
            
            return self._db
            
        except ConnectionFailure as e:
            logger.error(f"Failed to connect to MongoDB Atlas: {e}")
            raise
        except Exception as e:
            logger.error(f"Database connection error: {e}")
            raise
    
    def _initialize_database(self):
        """Initialize database collections and indexes"""
        try:
            # Create collections if they don't exist
            existing_collections = self._db.list_collection_names()
            
            collections_to_create = [
                Config.RECIPES_COLLECTION,
                Config.SEARCHES_COLLECTION,
                Config.USERS_COLLECTION,
                Config.FAVORITES_COLLECTION
            ]
            
            for collection_name in collections_to_create:
                if collection_name not in existing_collections:
                    self._db.create_collection(collection_name)
                    logger.info(f"Created collection: {collection_name}")
            
            # Create indexes
            self._create_indexes()
            
            # Initialize sample data if collections are empty
            self._initialize_sample_data()
            
        except Exception as e:
            logger.error(f"Database initialization error: {e}")
    
    def _create_indexes(self):
        """Create necessary indexes for optimal performance"""
        try:
            # Recipes collection indexes
            recipes_collection = self._db[Config.RECIPES_COLLECTION]
            
            # Text search index
            try:
                recipes_collection.create_index([
                    ("name", TEXT),
                    ("description", TEXT),
                    ("tags", TEXT)
                ], name="recipe_text_search")
                logger.info("Created text search index for recipes")
            except OperationFailure as e:
                if "already exists" not in str(e):
                    logger.warning(f"Text index creation warning: {e}")
            
            # Performance indexes
            index_specs = [
                ([("name", ASCENDING)], "recipe_name_idx"),
                ([("rating", DESCENDING)], "recipe_rating_idx"),
                ([("mood", ASCENDING)], "recipe_mood_idx"),
                ([("tags", ASCENDING)], "recipe_tags_idx"),
                ([("difficulty", ASCENDING)], "recipe_difficulty_idx"),
                ([("cookTime", ASCENDING)], "recipe_cooktime_idx")
            ]
            
            for index_spec, index_name in index_specs:
                try:
                    recipes_collection.create_index(index_spec, name=index_name)
                except OperationFailure as e:
                    if "already exists" not in str(e):
                        logger.warning(f"Index creation warning for {index_name}: {e}")
            
            # Searches collection indexes
            searches_collection = self._db[Config.SEARCHES_COLLECTION]
            search_indexes = [
                ([("timestamp", DESCENDING)], "search_timestamp_idx"),
                ([("userName", ASCENDING)], "search_user_idx"),
                ([("ingredients", ASCENDING)], "search_ingredients_idx")
            ]
            
            for index_spec, index_name in search_indexes:
                try:
                    searches_collection.create_index(index_spec, name=index_name)
                except OperationFailure as e:
                    if "already exists" not in str(e):
                        logger.warning(f"Search index creation warning for {index_name}: {e}")
            
            # Users collection indexes
            users_collection = self._db[Config.USERS_COLLECTION]
            try:
                users_collection.create_index([("name", ASCENDING)], unique=True, name="user_name_unique_idx")
                users_collection.create_index([("email", ASCENDING)], unique=True, sparse=True, name="user_email_unique_idx")
            except OperationFailure as e:
                if "already exists" not in str(e):
                    logger.warning(f"User index creation warning: {e}")
            
            # Favorites collection indexes
            favorites_collection = self._db[Config.FAVORITES_COLLECTION]
            fav_indexes = [
                ([("userName", ASCENDING)], "favorites_user_idx"),
                ([("recipeId", ASCENDING)], "favorites_recipe_idx"),
                ([("createdAt", DESCENDING)], "favorites_created_idx")
            ]
            
            for index_spec, index_name in fav_indexes:
                try:
                    favorites_collection.create_index(index_spec, name=index_name)
                except OperationFailure as e:
                    if "already exists" not in str(e):
                        logger.warning(f"Favorites index creation warning for {index_name}: {e}")
            
            logger.info("Database indexes created successfully")
            
        except Exception as e:
            logger.error(f"Error creating indexes: {e}")
    
    def _initialize_sample_data(self):
        """Initialize sample data if database is empty"""
        try:
            recipes_collection = self._db[Config.RECIPES_COLLECTION]
            
            # Check if we already have recipes
            if recipes_collection.count_documents({}) > 0:
                logger.info("Sample recipes already exist, skipping initialization")
                return
            
            # Create sample recipes with vector embeddings
            success = vector_search_service.create_sample_recipes_with_vectors()
            
            if success:
                logger.info("Sample recipes with vector embeddings created successfully")
            else:
                logger.warning("Failed to create sample recipes with vectors")
                
        except Exception as e:
            logger.error(f"Error initializing sample data: {e}")
    
    @property
    def db(self):
        """Get database instance"""
        if self._db is None:
            self.connect()
        return self._db
    
    @property
    def client(self):
        """Get MongoDB client instance"""
        if self._client is None:
            self.connect()
        return self._client
    
    def get_collection(self, collection_name: str):
        """Get a specific collection"""
        if self._db is None:
            self.connect()
        return self._db[collection_name]
    
    def close(self):
        """Close database connection"""
        if self._client:
            self._client.close()
            self._client = None
            self._db = None
            logger.info("Database connection closed")
    
    def health_check(self) -> dict:
        """Perform database health check"""
        try:
            if not self._client or not self._db:
                return {"status": "disconnected", "error": "No database connection"}
            
            # Test connection
            self._client.admin.command('ping')
            
            # Get collection stats
            collections_info = {}
            for collection_name in [Config.RECIPES_COLLECTION, Config.SEARCHES_COLLECTION, Config.USERS_COLLECTION]:
                try:
                    count = self._db[collection_name].count_documents({})
                    collections_info[collection_name] = {"count": count}
                except Exception as e:
                    collections_info[collection_name] = {"error": str(e)}
            
            return {
                "status": "healthy",
                "database": Config.DATABASE_NAME,
                "collections": collections_info
            }
            
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e)
            }

# Global database connection instance
db_connection = DatabaseConnection()