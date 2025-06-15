from pymongo import MongoClient, ASCENDING, DESCENDING
from pymongo.errors import OperationFailure
import logging
from config import Config

logger = logging.getLogger(__name__)

class DatabaseManager:
    def __init__(self, uri=None, database_name=None):
        self.uri = uri or Config.MONGODB_URI
        self.database_name = database_name or Config.DATABASE_NAME
        self.client = None
        self.db = None
        
    def connect(self):
        """Establish connection to MongoDB Atlas"""
        try:
            self.client = MongoClient(self.uri)
            self.db = self.client[self.database_name]
            
            # Test connection
            self.client.admin.command('ping')
            logger.info(f"Connected to MongoDB Atlas database: {self.database_name}")
            
            # Initialize collections and indexes
            self.setup_collections()
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            return False
    
    def setup_collections(self):
        """Create collections and indexes"""
        try:
            # Create collections if they don't exist
            collections = [
                Config.RECIPES_COLLECTION,
                Config.SEARCHES_COLLECTION,
                Config.USERS_COLLECTION,
                Config.FAVORITES_COLLECTION
            ]
            
            existing_collections = self.db.list_collection_names()
            
            for collection_name in collections:
                if collection_name not in existing_collections:
                    self.db.create_collection(collection_name)
                    logger.info(f"Created collection: {collection_name}")
            
            # Setup indexes
            self.setup_indexes()
            
            # Setup vector search index
            self.setup_vector_search()
            
        except Exception as e:
            logger.error(f"Error setting up collections: {e}")
    
    def setup_indexes(self):
        """Create necessary indexes for efficient queries"""
        try:
            # Recipes collection indexes
            recipes_collection = self.db[Config.RECIPES_COLLECTION]
            recipes_collection.create_index([("name", ASCENDING)])
            recipes_collection.create_index([("ingredients.name", ASCENDING)])
            recipes_collection.create_index([("difficulty", ASCENDING)])
            recipes_collection.create_index([("cookTime", ASCENDING)])
            recipes_collection.create_index([("rating", DESCENDING)])
            recipes_collection.create_index([("mood", ASCENDING)])
            
            # Searches collection indexes
            searches_collection = self.db[Config.SEARCHES_COLLECTION]
            searches_collection.create_index([("timestamp", DESCENDING)])
            searches_collection.create_index([("user_name", ASCENDING)])
            searches_collection.create_index([("ingredients", ASCENDING)])
            searches_collection.create_index([("mood", ASCENDING)])
            
            # Users collection indexes
            users_collection = self.db[Config.USERS_COLLECTION]
            users_collection.create_index([("name", ASCENDING)], unique=True)
            users_collection.create_index([("created_at", DESCENDING)])
            
            # Favorites collection indexes
            favorites_collection = self.db[Config.FAVORITES_COLLECTION]
            favorites_collection.create_index([("user_name", ASCENDING)])
            favorites_collection.create_index([("recipe_id", ASCENDING)])
            favorites_collection.create_index([("created_at", DESCENDING)])
            
            logger.info("Database indexes created successfully")
            
        except Exception as e:
            logger.error(f"Error creating indexes: {e}")
    
    def setup_vector_search(self):
        """Setup vector search index for Atlas Vector Search"""
        try:
            recipes_collection = self.db[Config.RECIPES_COLLECTION]
            
            # Vector search index definition
            vector_index = {
                "name": Config.VECTOR_INDEX_NAME,
                "type": "vectorSearch",
                "definition": {
                    "fields": [
                        {
                            "type": "vector",
                            "path": "embedding",
                            "numDimensions": Config.VECTOR_DIMENSION,
                            "similarity": "cosine"
                        },
                        {
                            "type": "filter",
                            "path": "mood"
                        },
                        {
                            "type": "filter",
                            "path": "difficulty"
                        }
                    ]
                }
            }
            
            # Note: Vector search indexes are created through Atlas UI or Atlas CLI
            # This is a placeholder for the index structure
            logger.info("Vector search index definition prepared")
            
        except Exception as e:
            logger.error(f"Error setting up vector search: {e}")
    
    def get_collection(self, collection_name):
        """Get a specific collection"""
        if not self.db:
            raise Exception("Database not connected")
        return self.db[collection_name]
    
    def close_connection(self):
        """Close database connection"""
        if self.client:
            self.client.close()
            logger.info("Database connection closed")

# Sample data for initial setup
SAMPLE_RECIPES = [
    {
        "name": "Golden Sunset Pasta",
        "description": "A warm embrace in a bowl with creamy sauce and tender vegetables",
        "cookTime": "25 min",
        "difficulty": "Easy",
        "rating": 4.8,
        "image": "🍝",
        "mood": "comfort",
        "ingredients": [
            {"name": "Pasta", "amount": "200g"},
            {"name": "Heavy cream", "amount": "150ml"},
            {"name": "Cherry tomatoes", "amount": "150g"},
            {"name": "Fresh basil", "amount": "10 leaves"},
            {"name": "Garlic", "amount": "2 cloves"},
            {"name": "Parmesan cheese", "amount": "50g"}
        ],
        "instructions": [
            "Bring a large pot of salted water to a gentle boil. Add pasta and cook until al dente.",
            "While pasta dances in the water, heat olive oil in a large pan over medium heat.",
            "Add minced garlic and let it release its wonderful aroma for about 30 seconds.",
            "Toss in halved cherry tomatoes and cook until they start to burst with flavor.",
            "Pour in the cream and let it simmer gently, creating a silky sauce.",
            "Drain pasta, reserving a cup of that precious pasta water.",
            "Combine pasta with the creamy sauce, adding pasta water if needed for perfect consistency.",
            "Finish with fresh basil leaves and a generous sprinkle of Parmesan."
        ],
        "tip": "Save some pasta water before draining - it's the secret to a silky smooth sauce that hugs every strand! ✨",
        "tags": ["pasta", "cream", "tomatoes", "comfort", "easy"],
        "embedding": None  # Will be populated with vector embeddings
    },
    {
        "name": "Garden Fresh Salad Bowl",
        "description": "A vibrant celebration of fresh vegetables in perfect harmony",
        "cookTime": "15 min",
        "difficulty": "Effortless",
        "rating": 4.6,
        "image": "🥗",
        "mood": "fresh",
        "ingredients": [
            {"name": "Mixed greens", "amount": "200g"},
            {"name": "Cherry tomatoes", "amount": "150g"},
            {"name": "Cucumber", "amount": "1 large"},
            {"name": "Bell peppers", "amount": "2 pieces"},
            {"name": "Avocado", "amount": "1 ripe"},
            {"name": "Olive oil", "amount": "3 tbsp"},
            {"name": "Lemon juice", "amount": "2 tbsp"}
        ],
        "instructions": [
            "Wash all vegetables thoroughly and pat dry.",
            "Chop vegetables into bite-sized pieces.",
            "Mix olive oil and lemon juice for dressing.",
            "Toss salad with dressing just before serving.",
            "Add avocado last to prevent browning."
        ],
        "tip": "Add the avocado at the very end to keep it perfectly green and creamy! 🥑",
        "tags": ["salad", "vegetables", "fresh", "healthy", "quick"],
        "embedding": None
    },
    {
        "name": "Decadent Chocolate Delight",
        "description": "Rich, luxurious dessert that melts in your mouth",
        "cookTime": "45 min",
        "difficulty": "Medium",
        "rating": 4.9,
        "image": "🍫",
        "mood": "indulgent",
        "ingredients": [
            {"name": "Dark chocolate", "amount": "200g"},
            {"name": "Butter", "amount": "100g"},
            {"name": "Eggs", "amount": "3 large"},
            {"name": "Sugar", "amount": "100g"},
            {"name": "Flour", "amount": "50g"},
            {"name": "Vanilla extract", "amount": "1 tsp"}
        ],
        "instructions": [
            "Preheat oven to 180°C (350°F).",
            "Melt chocolate and butter together gently.",
            "Whisk eggs and sugar until light and fluffy.",
            "Fold in melted chocolate mixture.",
            "Add flour and vanilla, mix until just combined.",
            "Bake for 25-30 minutes until set but still soft."
        ],
        "tip": "Don't overbake - the center should still be slightly jiggly for the perfect texture! 🍰",
        "tags": ["chocolate", "dessert", "indulgent", "rich", "special"],
        "embedding": None
    }
]

def populate_sample_data(db_manager):
    """Populate database with sample recipes"""
    try:
        recipes_collection = db_manager.get_collection(Config.RECIPES_COLLECTION)
        
        # Check if data already exists
        if recipes_collection.count_documents({}) > 0:
            logger.info("Sample data already exists, skipping population")
            return
        
        # Insert sample recipes
        result = recipes_collection.insert_many(SAMPLE_RECIPES)
        logger.info(f"Inserted {len(result.inserted_ids)} sample recipes")
        
    except Exception as e:
        logger.error(f"Error populating sample data: {e}")

# Initialize database manager
db_manager = DatabaseManager()

if __name__ == "__main__":
    # Test database connection and setup
    if db_manager.connect():
        populate_sample_data(db_manager)
        print("Database setup completed successfully!")
    else:
        print("Failed to setup database")