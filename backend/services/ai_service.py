import pickle
import numpy as np
from sentence_transformers import SentenceTransformer
import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

class AIService:
    def __init__(self):
        self.model = None
        self.embedding_model = None
        self._load_models()
    
    def _load_models(self):
        """Load AI models"""
        try:
            # Load your trained model
            with open('ai_models/recipe_model.pkl', 'rb') as f:
                self.model = pickle.load(f)
            
            # Load sentence transformer for embeddings
            self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
            logger.info("AI models loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load AI models: {e}")
            raise
    
    def generate_ingredient_embedding(self, ingredients: List[str]) -> np.ndarray:
        """Generate vector embedding for ingredients"""
        try:
            # Combine ingredients into a single text
            ingredient_text = ", ".join(ingredients)
            embedding = self.embedding_model.encode(ingredient_text)
            return embedding.tolist()
        except Exception as e:
            logger.error(f"Error generating embedding: {e}")
            return []
    
    def predict_recipes(self, ingredients: List[str], mood: str = "comfort") -> List[Dict[str, Any]]:
        """Use AI model to predict best recipes"""
        try:
            # Generate embedding for input ingredients
            ingredient_embedding = self.generate_ingredient_embedding(ingredients)
            
            # Use your trained model to predict
            # This is a placeholder - adapt based on your actual model
            predictions = self.model.predict([ingredient_embedding])
            
            # Mock response based on mood and ingredients
            # Replace this with actual model predictions
            return self._generate_mock_predictions(ingredients, mood)
        except Exception as e:
            logger.error(f"Error in recipe prediction: {e}")
            return self._generate_fallback_recipes()
    
    def _generate_mock_predictions(self, ingredients: List[str], mood: str) -> List[Dict[str, Any]]:
        """Generate mock predictions (replace with actual model logic)"""
        base_recipes = [
            {
                "name": "AI-Suggested Comfort Bowl",
                "description": "A personalized comfort dish crafted just for you",
                "cookTime": "25 min",
                "difficulty": "Easy",
                "rating": 4.8,
                "image": "🍲",
                "ingredients": self._generate_ingredients(ingredients),
                "instructions": self._generate_instructions(ingredients),
                "tip": "This recipe was specially crafted by AI based on your ingredients! ✨"
            },
            {
                "name": "Smart Fusion Delight",
                "description": "An intelligent blend of your available ingredients",
                "cookTime": "30 min",
                "difficulty": "Medium",
                "rating": 4.7,
                "image": "🍽️",
                "ingredients": self._generate_ingredients(ingredients),
                "instructions": self._generate_instructions(ingredients),
                "tip": "The AI discovered this unique combination just for you! 🤖"
            },
            {
                "name": "Personalized Chef's Special",
                "description": "A custom creation based on your taste preferences",
                "cookTime": "20 min",
                "difficulty": "Simple",
                "rating": 4.9,
                "image": "⭐",
                "ingredients": self._generate_ingredients(ingredients),
                "instructions": self._generate_instructions(ingredients),
                "tip": "This recipe adapts to your mood and ingredients perfectly! 🎯"
            }
        ]
        
        return base_recipes
    
    def _generate_ingredients(self, user_ingredients: List[str]) -> List[Dict[str, str]]:
        """Generate ingredient list based on user input"""
        formatted_ingredients = []
        for ingredient in user_ingredients[:6]:  # Limit to 6 ingredients
            formatted_ingredients.append({
                "name": ingredient.title(),
                "amount": self._estimate_amount(ingredient)
            })
        return formatted_ingredients
    
    def _estimate_amount(self, ingredient: str) -> str:
        """Estimate ingredient amounts"""
        # Simple logic - enhance based on your needs
        if any(meat in ingredient.lower() for meat in ['chicken', 'beef', 'pork', 'fish']):
            return "300g"
        elif any(veg in ingredient.lower() for veg in ['tomato', 'onion', 'pepper']):
            return "2 pieces"
        elif 'pasta' in ingredient.lower():
            return "200g"
        elif 'rice' in ingredient.lower():
            return "150g"
        else:
            return "1 cup"
    
    def _generate_instructions(self, ingredients: List[str]) -> List[str]:
        """Generate cooking instructions"""
        return [
            f"Prepare your {', '.join(ingredients[:3])} by washing and chopping as needed.",
            "Heat oil in a large pan over medium heat.",
            "Add your main ingredients and cook according to their requirements.",
            "Season with salt, pepper, and your favorite herbs.",
            "Combine all ingredients and let them meld together beautifully.",
            "Taste and adjust seasoning as needed.",
            "Serve hot and enjoy your AI-crafted creation!"
        ]
    
    def _generate_fallback_recipes(self) -> List[Dict[str, Any]]:
        """Fallback recipes when AI fails"""
        return [
            {
                "name": "Simple Comfort Dish",
                "description": "A reliable, delicious meal when you need it most",
                "cookTime": "20 min",
                "difficulty": "Easy",
                "rating": 4.5,
                "image": "🍽️",
                "ingredients": [{"name": "Available ingredients", "amount": "As needed"}],
                "instructions": ["Cook with love and enjoy!"],
                "tip": "Sometimes the simplest dishes are the most satisfying! 💚"
            }
        ]

# Global AI service instance
ai_service = AIService()