import numpy as np
from typing import List, Dict, Any
from utils.database import db_connection
from services.ai_service import ai_service
import logging

logger = logging.getLogger(__name__)

class VectorSearchService:
    def __init__(self):
        self.db = db_connection.db
        self.collection = self.db.recipes
    
    def search_similar_recipes(self, ingredients: List[str], limit: int = 10) -> List[Dict[str, Any]]:
        """Search for similar recipes using vector similarity"""
        try:
            # Generate embedding for search query
            query_embedding = ai_service.generate_ingredient_embedding(ingredients)
            
            if not query_embedding:
                return []
            
            # MongoDB Atlas Vector Search query
            pipeline = [
                {
                    "$vectorSearch": {
                        "index": "vector_search",  # Atlas Search index name
                        "path": "ingredientVector",
                        "queryVector": query_embedding,
                        "numCandidates": 100,
                        "limit": limit
                    }
                },
                {
                    "$addFields": {
                        "score": {"$meta": "vectorSearchScore"}
                    }
                },
                {
                    "$match": {
                        "score": {"$gte": 0.7}  # Minimum similarity threshold
                    }
                }
            ]
            
            results = list(self.collection.aggregate(pipeline))
            
            # Convert ObjectId to string for JSON serialization
            for result in results:
                result['_id'] = str(result['_id'])
            
            logger.info(f"Found {len(results)} similar recipes")
            return results
            
        except Exception as e:
            logger.error(f"Vector search error: {e}")
            # Fallback to text search
            return self._fallback_text_search(ingredients, limit)
    
    def _fallback_text_search(self, ingredients: List[str], limit: int) -> List[Dict[str, Any]]:
        """Fallback text search when vector search fails"""
        try:
            search_terms = " ".join(ingredients)
            
            results = list(self.collection.find(
                {"$text": {"$search": search_terms}},
                {"score": {"$meta": "textScore"}}
            ).sort([("score", {"$meta": "textScore"})]).limit(limit))
            
            # Convert ObjectId to string
            for result in results:
                result['_id'] = str(result['_id'])
            
            return results
        except Exception as e:
            logger.error(f"Fallback search error: {e}")
            return []
    
    def index_recipe_vectors(self, recipes: List[Dict[str, Any]]) -> bool:
        """Index recipes with vector embeddings"""
        try:
            for recipe in recipes:
                if 'ingredients' in recipe:
                    # Generate vector embedding
                    ingredients_text = recipe['ingredients']
                    if isinstance(ingredients_text, list):
                        ingredients_text = [ing.get('name', ing) if isinstance(ing, dict) else ing for ing in ingredients_text]
                    
                    vector = ai_service.generate_ingredient_embedding(ingredients_text)
                    recipe['ingredientVector'] = vector
            
            # Bulk insert/update
            operations = []
            for recipe in recipes:
                operations.append({
                    "updateOne": {
                        "filter": {"name": recipe["name"]},
                        "update": {"$set": recipe},
                        "upsert": True
                    }
                })
            
            if operations:
                self.collection.bulk_write(operations)
                logger.info(f"Indexed {len(recipes)} recipes with vectors")
                return True
            
        except Exception as e:
            logger.error(f"Vector indexing error: {e}")
            return False

# Global vector search service
vector_search_service = VectorSearchService()