from flask_pymongo import PyMongo
from pymongo.errors import PyMongoError
from datetime import datetime
from typing import List, Dict, Any, Optional
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DatabaseManager:
    """Handle all database operations"""
    
    def __init__(self, mongo: PyMongo):
        self.mongo = mongo
        self.db = mongo.db
    
    def save_recipe(self, recipe_data: Dict[str, Any]) -> Optional[str]:
        """
        Save a generated recipe to the database
        
        Args:
            recipe_data: Recipe data dictionary
            
        Returns:
            Recipe ID if successful, None if failed
        """
        try:
            # Add timestamp
            recipe_data['created_at'] = datetime.utcnow()
            
            # Insert into recipes collection
            result = self.db.recipes.insert_one(recipe_data)
            logger.info(f"Recipe saved with ID: {result.inserted_id}")
            return str(result.inserted_id)
            
        except PyMongoError as e:
            logger.error(f"Error saving recipe: {str(e)}")
            return None
    
    def save_user_query(self, query_data: Dict[str, Any]) -> Optional[str]:
        """
        Save user query and response for analytics
        
        Args:
            query_data: User query data
            
        Returns:
            Query ID if successful, None if failed
        """
        try:
            query_data['timestamp'] = datetime.utcnow()
            result = self.db.user_queries.insert_one(query_data)
            logger.info(f"User query saved with ID: {result.inserted_id}")
            return str(result.inserted_id)
            
        except PyMongoError as e:
            logger.error(f"Error saving user query: {str(e)}")
            return None
    
    def get_popular_ingredients(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get most popular ingredients based on user queries
        
        Args:
            limit: Number of ingredients to return
            
        Returns:
            List of popular ingredients with counts
        """
        try:
            pipeline = [
                {"$unwind": "$ingredients"},
                {"$group": {
                    "_id": "$ingredients",
                    "count": {"$sum": 1}
                }},
                {"$sort": {"count": -1}},
                {"$limit": limit}
            ]
            
            result = list(self.db.user_queries.aggregate(pipeline))
            return result
            
        except PyMongoError as e:
            logger.error(f"Error getting popular ingredients: {str(e)}")
            return []
    
    def get_recipe_by_ingredients(self, ingredients: List[str]) -> Optional[Dict[str, Any]]:
        """
        Check if we have a similar recipe already generated
        
        Args:
            ingredients: List of ingredients to search for
            
        Returns:
            Existing recipe if found, None otherwise
        """
        try:
            # Look for recipes with similar ingredients
            query = {
                "ingredients": {"$in": ingredients}
            }
            
            recipe = self.db.recipes.find_one(query, sort=[("created_at", -1)])
            
            if recipe:
                # Update the times_generated counter
                self.db.recipes.update_one(
                    {"_id": recipe["_id"]},
                    {"$inc": {"times_generated": 1}}
                )
            
            return recipe
            
        except PyMongoError as e:
            logger.error(f"Error searching recipes: {str(e)}")
            return None
    
    def get_database_stats(self) -> Dict[str, Any]:
        """Get database statistics for monitoring"""
        try:
            stats = {
                'total_recipes': self.db.recipes.count_documents({}),
                'total_queries': self.db.user_queries.count_documents({}),
                'database_status': 'healthy'
            }
            return stats
            
        except PyMongoError as e:
            logger.error(f"Error getting database stats: {str(e)}")
            return {'database_status': 'error', 'error': str(e)}