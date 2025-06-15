import pickle
import numpy as np
from sentence_transformers import SentenceTransformer
import logging
from typing import List, Dict, Any
from config import Config
import os

logger = logging.getLogger(__name__)

class AIService:
    def __init__(self):
        self.model = None
        self.embedding_model = None
        self._load_models()
    
    def _load_models(self):
        """Load AI models for recipe prediction and embeddings"""
        try:
            # Load your trained recipe prediction model
            model_path = Config.AI_MODEL_PATH
            if os.path.exists(model_path):
                with open(model_path, 'rb') as f:
                    self.model = pickle.load(f)
                logger.info("Recipe prediction model loaded successfully")
            else:
                logger.warning(f"Model file not found at {model_path}, using fallback")
            
            # Load sentence transformer for embeddings
            self.embedding_model = SentenceTransformer(Config.EMBEDDING_MODEL)
            logger.info("Embedding model loaded successfully")
            
        except Exception as e:
            logger.error(f"Failed to load AI models: {e}")
            # Continue without models - will use fallback methods
    
    def generate_ingredient_embedding(self, ingredients: List[str]) -> List[float]:
        """Generate vector embedding for ingredients list"""
        try:
            if not self.embedding_model:
                return []
            
            # Combine ingredients into searchable text
            ingredient_text = ", ".join([ing.lower().strip() for ing in ingredients])
            
            # Generate embedding
            embedding = self.embedding_model.encode(ingredient_text)
            return embedding.tolist()
            
        except Exception as e:
            logger.error(f"Error generating embedding: {e}")
            return []
    
    def predict_recipes(self, ingredients: List[str], mood: str = "comfort") -> List[Dict[str, Any]]:
        """Use AI model to predict best recipe matches"""
        try:
            # Generate embedding for input
            ingredient_embedding = self.generate_ingredient_embedding(ingredients)
            
            if self.model and ingredient_embedding:
                # Use your trained model for predictions
                predictions = self._use_trained_model(ingredient_embedding, ingredients, mood)
            else:
                # Fallback to rule-based generation
                predictions = self._generate_smart_recipes(ingredients, mood)
            
            return predictions
            
        except Exception as e:
            logger.error(f"Error in recipe prediction: {e}")
            return self._generate_fallback_recipes(ingredients, mood)
    
    def _use_trained_model(self, embedding: List[float], ingredients: List[str], mood: str) -> List[Dict[str, Any]]:
        """Use your trained model for predictions"""
        try:
            # Reshape embedding for model input
            input_data = np.array(embedding).reshape(1, -1)
            
            # Get model predictions
            predictions = self.model.predict(input_data)
            
            # Convert predictions to recipe format
            # This depends on your model's output format
            # Adjust based on your specific model
            
            return self._format_model_predictions(predictions, ingredients, mood)
            
        except Exception as e:
            logger.error(f"Error using trained model: {e}")
            return self._generate_smart_recipes(ingredients, mood)
    
    def _format_model_predictions(self, predictions, ingredients: List[str], mood: str) -> List[Dict[str, Any]]:
        """Format model predictions into recipe objects"""
        # This is a template - adjust based on your model's output
        recipes = []
        
        for i, prediction in enumerate(predictions[:3]):  # Top 3 predictions
            recipe = {
                "name": f"AI-Crafted {mood.title()} Dish #{i+1}",
                "description": f"A personalized {mood} recipe created just for you",
                "cookTime": self._estimate_cook_time(ingredients),
                "difficulty": self._estimate_difficulty(ingredients),
                "rating": round(4.5 + (prediction * 0.4), 1),  # Scale to 4.5-4.9
                "image": self._select_emoji(ingredients, mood),
                "ingredients": self._format_ingredients(ingredients),
                "instructions": self._generate_instructions(ingredients, mood),
                "tip": self._generate_tip(ingredients, mood),
                "tags": ingredients[:3] + [mood],
                "mood": mood
            }
            recipes.append(recipe)
        
        return recipes
    
    def _generate_smart_recipes(self, ingredients: List[str], mood: str) -> List[Dict[str, Any]]:
        """Generate intelligent recipe suggestions based on ingredients and mood"""
        recipes = []
        
        # Recipe templates based on mood
        mood_templates = {
            "comfort": {
                "styles": ["Hearty", "Cozy", "Warm", "Creamy"],
                "cooking_methods": ["simmered", "baked", "slow-cooked", "braised"],
                "emojis": ["🍲", "🥘", "🍝", "🧀"]
            },
            "fresh": {
                "styles": ["Light", "Crisp", "Vibrant", "Garden-Fresh"],
                "cooking_methods": ["tossed", "grilled", "steamed", "raw"],
                "emojis": ["🥗", "🌿", "🥒", "🍅"]
            },
            "indulgent": {
                "styles": ["Rich", "Decadent", "Luxurious", "Gourmet"],
                "cooking_methods": ["seared", "roasted", "caramelized", "flambéed"],
                "emojis": ["🥩", "🍫", "🧈", "✨"]
            }
        }
        
        template = mood_templates.get(mood, mood_templates["comfort"])
        
        for i in range(3):
            style = template["styles"][i % len(template["styles"])]
            method = template["cooking_methods"][i % len(template["cooking_methods"])]
            emoji = template["emojis"][i % len(template["emojis"])]
            
            recipe = {
                "name": f"{style} {self._create_dish_name(ingredients)}",
                "description": f"A {mood} dish featuring your ingredients, {method} to perfection",
                "cookTime": self._estimate_cook_time(ingredients),
                "difficulty": self._estimate_difficulty(ingredients),
                "rating": round(4.3 + (i * 0.2), 1),
                "image": emoji,
                "ingredients": self._format_ingredients(ingredients),
                "instructions": self._generate_instructions(ingredients, mood),
                "tip": self._generate_tip(ingredients, mood),
                "tags": ingredients[:3] + [mood],
                "mood": mood
            }
            recipes.append(recipe)
        
        return recipes
    
    def _create_dish_name(self, ingredients: List[str]) -> str:
        """Create appealing dish names from ingredients"""
        main_ingredient = ingredients[0].title() if ingredients else "Special"
        
        name_patterns = [
            f"{main_ingredient} Medley",
            f"Chef's {main_ingredient} Creation",
            f"{main_ingredient} Fusion Bowl",
            f"Artisan {main_ingredient} Dish",
            f"{main_ingredient} Symphony"
        ]
        
        import random
        return random.choice(name_patterns)
    
    def _format_ingredients(self, user_ingredients: List[str]) -> List[Dict[str, str]]:
        """Format ingredients with estimated amounts"""
        formatted = []
        
        for ingredient in user_ingredients[:8]:  # Limit to 8 ingredients
            formatted.append({
                "name": ingredient.title(),
                "amount": self._estimate_amount(ingredient)
            })
        
        # Add common complementary ingredients
        complementary = [
            {"name": "Salt", "amount": "to taste"},
            {"name": "Black pepper", "amount": "to taste"},
            {"name": "Olive oil", "amount": "2 tbsp"}
        ]
        
        formatted.extend(complementary)
        return formatted
    
    def _estimate_amount(self, ingredient: str) -> str:
        """Estimate ingredient amounts based on type"""
        ingredient_lower = ingredient.lower()
        
        # Proteins
        if any(protein in ingredient_lower for protein in ['chicken', 'beef', 'pork', 'fish', 'salmon', 'turkey']):
            return "300-400g"
        
        # Vegetables
        if any(veg in ingredient_lower for veg in ['tomato', 'onion', 'pepper', 'carrot', 'potato']):
            return "2-3 pieces"
        
        # Leafy greens
        if any(green in ingredient_lower for green in ['lettuce', 'spinach', 'kale', 'arugula']):
            return "2 cups"
        
        # Grains/Pasta
        if any(grain in ingredient_lower for grain in ['pasta', 'rice', 'quinoa', 'noodles']):
            return "200g"
        
        # Dairy
        if any(dairy in ingredient_lower for dairy in ['cheese', 'milk', 'cream', 'yogurt']):
            return "100ml"
        
        # Default
        return "1 cup"
    
    def _estimate_cook_time(self, ingredients: List[str]) -> str:
        """Estimate cooking time based on ingredients"""
        has_meat = any(meat in ' '.join(ingredients).lower() 
                      for meat in ['chicken', 'beef', 'pork', 'fish'])
        has_grains = any(grain in ' '.join(ingredients).lower() 
                        for grain in ['rice', 'pasta', 'quinoa'])
        
        if has_meat and has_grains:
            return "35-45 min"
        elif has_meat:
            return "25-35 min"
        elif has_grains:
            return "20-30 min"
        else:
            return "15-25 min"
    
    def _estimate_difficulty(self, ingredients: List[str]) -> str:
        """Estimate difficulty based on ingredient count and complexity"""
        ingredient_count = len(ingredients)
        
        if ingredient_count <= 3:
            return "Simple"
        elif ingredient_count <= 6:
            return "Easy"
        elif ingredient_count <= 9:
            return "Medium"
        else:
            return "Advanced"
    
    def _select_emoji(self, ingredients: List[str], mood: str) -> str:
        """Select appropriate emoji based on ingredients and mood"""
        ingredient_text = ' '.join(ingredients).lower()
        
        # Ingredient-based emojis
        if any(meat in ingredient_text for meat in ['chicken', 'beef', 'pork']):
            return "🍖"
        elif any(fish in ingredient_text for fish in ['fish', 'salmon', 'tuna']):
            return "🐟"
        elif any(pasta in ingredient_text for pasta in ['pasta', 'noodles', 'spaghetti']):
            return "🍝"
        elif any(veg in ingredient_text for veg in ['salad', 'lettuce', 'greens']):
            return "🥗"
        elif any(grain in ingredient_text for grain in ['rice', 'quinoa']):
            return "🍚"
        
        # Mood-based fallback
        mood_emojis = {
            "comfort": "🍲",
            "fresh": "🌿",
            "indulgent": "✨"
        }
        
        return mood_emojis.get(mood, "🍽️")
    
    def _generate_instructions(self, ingredients: List[str], mood: str) -> List[str]:
        """Generate cooking instructions"""
        base_instructions = [
            f"Gather and prepare your {', '.join(ingredients[:3])} and other ingredients.",
            "Heat oil in a large pan or pot over medium heat.",
            "Add your main ingredients in order of cooking time needed.",
            "Season generously with salt, pepper, and your favorite herbs.",
            "Cook until ingredients are tender and flavors have melded beautifully.",
            "Taste and adjust seasoning as needed.",
            f"Serve hot and enjoy your personalized {mood} creation!"
        ]
        
        return base_instructions
    
    def _generate_tip(self, ingredients: List[str], mood: str) -> str:
        """Generate helpful cooking tips"""
        tips = [
            "Let the ingredients rest together for a few minutes before serving to enhance flavors! ✨",
            "Don't be afraid to taste and adjust - cooking is all about personal preference! 👨‍🍳",
            "Save some fresh herbs for garnish to add a pop of color and freshness! 🌿",
            "A squeeze of lemon at the end can brighten up any dish! 🍋",
            "Trust your instincts - you know your taste better than anyone! 💚"
        ]
        
        import random
        return random.choice(tips)
    
    def _generate_fallback_recipes(self, ingredients: List[str], mood: str) -> List[Dict[str, Any]]:
        """Fallback recipes when all else fails"""
        return [{
            "name": "Simple Comfort Bowl",
            "description": "A reliable, delicious meal made with your available ingredients",
            "cookTime": "20 min",
            "difficulty": "Easy",
            "rating": 4.5,
            "image": "🍽️",
            "ingredients": [{"name": ing.title(), "amount": "as needed"} for ing in ingredients[:5]],
            "instructions": [
                "Prepare your ingredients with love.",
                "Cook them together until tender.",
                "Season to taste and enjoy!"
            ],
            "tip": "Sometimes the simplest dishes are the most satisfying! 💚",
            "tags": ingredients[:3] + [mood],
            "mood": mood
        }]

# Global AI service instance
ai_service = AIService()