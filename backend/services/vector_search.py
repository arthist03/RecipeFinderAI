import numpy as np
from typing import List, Dict, Any, Optional
from pymongo import MongoClient
from pymongo.errors import OperationFailure
from services.ai_service import ai_service
from config import Config
import logging

logger = logging.getLogger(__name__)

class VectorSearchService:
    def __init__(self, db_connection=None):
        self.db = db_connection
        self.recipes_collection = None
        if self.db:
            self.recipes_collection = self.db[Config.RECIPES_COLLECTION]
    
    def set_database(self, db_connection):
        """Set database connection"""
        self.db = db_connection
        self.recipes_collection = self.db[Config.RECIPES_COLLECTION]
    
    def search_similar_recipes(self, ingredients: List[str], mood: Optional[str] = None, limit: int = 5) -> List[Dict[str, Any]]:
        """Search for similar recipes using MongoDB Atlas Vector Search"""
        try:
            if not self.recipes_collection:
                logger.error("Database connection not available")
                return []
            
            # Generate embedding for search query
            query_embedding = ai_service.generate_ingredient_embedding(ingredients)
            
            if not query_embedding:
                logger.warning("Could not generate embedding, falling back to text search")
                return self._fallback_text_search(ingredients, mood, limit)
            
            # Build vector search pipeline
            pipeline = self._build_vector_search_pipeline(query_embedding, mood, limit)
            
            # Execute search
            results = list(self.recipes_collection.aggregate(pipeline))
            
            # Process results
            processed_results = self._process_search_results(results)
            
            logger.info(f"Vector search found {len(processed_results)} similar recipes")
            return processed_results
            
        except Exception as e:
            logger.error(f"Vector search error: {e}")
            return self._fallback_text_search(ingredients, mood, limit)
    
    def _build_vector_search_pipeline(self, query_embedding: List[float], mood: Optional[str], limit: int) -> List[Dict]:
        """Build MongoDB aggregation pipeline for vector search"""
        pipeline = [
            {
                "$vectorSearch": {
                    "index": Config.VECTOR_INDEX_NAME,
                    "path": "ingredientVector",
                    "queryVector": query_embedding,
                    "numCandidates": min(100, limit * 10),
                    "limit": limit * 2  # Get more candidates for filtering
                }
            },
            {
                "$addFields": {
                    "searchScore": {"$meta": "vectorSearchScore"}
                }
            }
        ]
        
        # Add mood filter if specified
        if mood:
            pipeline.append({
                "$match": {
                    "$or": [
                        {"mood": mood},
                        {"tags": {"$in": [mood]}},
                        {"searchScore": {"$gte": Config.SIMILARITY_THRESHOLD}}
                    ]
                }
            })
        else:
            pipeline.append({
                "$match": {
                    "searchScore": {"$gte": Config.SIMILARITY_THRESHOLD}
                }
            })
        
        # Sort by score and limit results
        pipeline.extend([
            {"$sort": {"searchScore": -1}},
            {"$limit": limit}
        ])
        
        return pipeline
    
    def _process_search_results(self, results: List[Dict]) -> List[Dict[str, Any]]:
        """Process and format search results"""
        processed = []
        
        for result in results:
            # Convert ObjectId to string for JSON serialization
            if '_id' in result:
                result['id'] = str(result['_id'])
                del result['_id']
            
            # Remove vector data from response (too large)
            if 'ingredientVector' in result:
                del result['ingredientVector']
            
            # Ensure required fields exist
            result.setdefault('rating', 4.5)
            result.setdefault('image', '🍽️')
            result.setdefault('tip', 'Enjoy this delicious recipe!')
            
            processed.append(result)
        
        return processed
    
    def _fallback_text_search(self, ingredients: List[str], mood: Optional[str], limit: int) -> List[Dict[str, Any]]:
        """Fallback to text search when vector search fails"""
        try:
            if not self.recipes_collection:
                return []
            
            # Build text search query
            search_terms = " ".join(ingredients)
            if mood:
                search_terms += f" {mood}"
            
            # Text search with scoring
            query = {"$text": {"$search": search_terms}}
            projection = {"score": {"$meta": "textScore"}}
            
            results = list(
                self.recipes_collection
                .find(query, projection)
                .sort([("score", {"$meta": "textScore"})])
                .limit(limit)
            )
            
            return self._process_search_results(results)
            
        except Exception as e:
            logger.error(f"Fallback text search error: {e}")
            return []
    
    def index_recipe_vectors(self, recipes: List[Dict[str, Any]]) -> bool:
        """Index recipes with vector embeddings"""
        try:
            if not self.recipes_collection:
                logger.error("Database connection not available for indexing")
                return False
            
            indexed_count = 0
            
            for recipe in recipes:
                try:
                    # Extract ingredients for embedding
                    ingredients_text = self._extract_ingredients_text(recipe)
                    
                    if ingredients_text:
                        # Generate vector embedding
                        vector = ai_service.generate_ingredient_embedding(ingredients_text)
                        
                        if vector:
                            recipe['ingredientVector'] = vector
                            
                            # Update or insert recipe
                            filter_query = {"name": recipe["name"]}
                            update_doc = {"$set": recipe}
                            
                            self.recipes_collection.update_one(
                                filter_query, 
                                update_doc, 
                                upsert=True
                            )
                            indexed_count += 1
                
                except Exception as e:
                    logger.error(f"Error indexing recipe {recipe.get('name', 'unknown')}: {e}")
                    continue
            
            logger.info(f"Successfully indexed {indexed_count} recipes with vectors")
            return indexed_count > 0
            
        except Exception as e:
            logger.error(f"Vector indexing error: {e}")
            return False
    
    def _extract_ingredients_text(self, recipe: Dict[str, Any]) -> List[str]:
        """Extract ingredient names from recipe for embedding"""
        ingredients_text = []
        
        ingredients = recipe.get('ingredients', [])
        
        for ingredient in ingredients:
            if isinstance(ingredient, dict):
                name = ingredient.get('name', '')
            elif isinstance(ingredient, str):
                name = ingredient
            else:
                continue
            
            if name:
                ingredients_text.append(name.lower().strip())
        
        # Also include recipe name and tags for better matching
        if recipe.get('name'):
            ingredients_text.append(recipe['name'].lower())
        
        if recipe.get('tags'):
            ingredients_text.extend([tag.lower() for tag in recipe['tags']])
        
        return ingredients_text
    
    def create_sample_recipes_with_vectors(self) -> bool:
        """Create sample recipes with vector embeddings"""
        sample_recipes = [
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
                    "While pasta cooks, heat olive oil in a large pan over medium heat.",
                    "Add minced garlic and cook for 30 seconds until fragrant.",
                    "Add cherry tomatoes and cook until they start to burst.",
                    "Pour in cream and simmer gently to create a silky sauce.",
                    "Drain pasta, reserving pasta water.",
                    "Combine pasta with sauce, adding pasta water if needed.",
                    "Finish with fresh basil and Parmesan cheese."
                ],
                "tip": "Save pasta water before draining - it's the secret to silky sauce! ✨",
                "tags": ["pasta", "cream", "tomatoes", "comfort", "easy"]
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
                "tip": "Add avocado at the very end to keep it perfectly green! 🥑",
                "tags": ["salad", "vegetables", "fresh", "healthy", "quick"]
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
                "tip": "Don't overbake - the center should be slightly jiggly! 🍰",
                "tags": ["chocolate", "dessert", "indulgent", "rich", "special"]
            }
        ]
        
        return self.index_recipe_vectors(sample_recipes)

# Global vector search service instance
vector_search_service = VectorSearchService()