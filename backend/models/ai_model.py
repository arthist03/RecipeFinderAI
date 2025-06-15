import json
import random
from typing import List, Dict, Any
import numpy as np

class RecipeAIModel:
    """
    Your custom AI model for generating funny, creative recipes
    """
    
    def __init__(self):
        self.humor_templates = [
            "Time to channel your inner Gordon Ramsay (but nicer)!",
            "Let's cook something that won't require a fire extinguisher!",
            "Warning: This recipe may cause uncontrollable happiness!",
            "Prepare to amaze yourself (and possibly your neighbors)!",
            "Get ready to create some culinary magic ✨"
        ]
        
        self.cooking_verbs = [
            "lovingly dice", "enthusiastically chop", "gently massage",
            "carefully pamper", "boldly attack", "gracefully dance with"
        ]
        
        # Load your trained model here
        # self.model = torch.load('your_model.pth')
        # For now, we'll use rule-based generation
    
    def generate_recipe(self, ingredients: List[str], preferences: List[str] = None) -> Dict[str, Any]:
        """
        Generate a funny, creative recipe based on ingredients
        
        Args:
            ingredients: List of available ingredients
            preferences: List of preferences like 'baked', 'high protein', etc.
            
        Returns:
            Dictionary containing recipe data
        """
        if not ingredients:
            return self._generate_error_response("No ingredients provided!")
        
        # Your AI logic goes here
        # For demonstration, I'll show a rule-based approach
        recipe_data = self._create_recipe_from_ingredients(ingredients, preferences)
        
        return recipe_data
    
    def _create_recipe_from_ingredients(self, ingredients: List[str], preferences: List[str]) -> Dict[str, Any]:
        """Create a recipe using rule-based AI logic"""
        
        # Determine recipe type based on ingredients
        recipe_type = self._determine_recipe_type(ingredients, preferences)
        dish_name = self._generate_dish_name(ingredients, recipe_type)
        
        # Generate cooking steps with humor
        steps = self._generate_cooking_steps(ingredients, recipe_type)
        
        # Add humor and personality
        intro = random.choice(self.humor_templates)
        
        return {
            'dish_name': dish_name,
            'intro': intro,
            'ingredients_used': ingredients,
            'recipe_type': recipe_type,
            'cooking_time': self._estimate_cooking_time(recipe_type),
            'difficulty': self._rate_difficulty(ingredients, recipe_type),
            'steps': steps,
            'fun_fact': self._generate_fun_fact(dish_name),
            'chef_tip': self._generate_chef_tip()
        }
    
    def _determine_recipe_type(self, ingredients: List[str], preferences: List[str]) -> str:
        """Determine what type of dish to make"""
        # Simple logic - you can make this more sophisticated
        if any(pref in ['baked', 'oven'] for pref in (preferences or [])):
            return 'baked'
        elif any(ing in ['pasta', 'noodles', 'spaghetti'] for ing in ingredients):
            return 'pasta'
        elif any(ing in ['chicken', 'beef', 'pork'] for ing in ingredients):
            return 'main_course'
        elif any(ing in ['flour', 'sugar', 'eggs'] for ing in ingredients):
            return 'dessert'
        else:
            return 'creative_mix'
    
    def _generate_dish_name(self, ingredients: List[str], recipe_type: str) -> str:
        """Generate a creative dish name"""
        main_ingredient = ingredients[0] if ingredients else "Mystery"
        
        creative_adjectives = [
            "Spectacular", "Mind-Blowing", "Heavenly", "Epic", 
            "Legendary", "Magical", "Incredible", "Supreme"
        ]
        
        adjective = random.choice(creative_adjectives)
        
        if recipe_type == 'pasta':
            return f"{adjective} {main_ingredient.title()} Pasta Extravaganza"
        elif recipe_type == 'baked':
            return f"{adjective} Baked {main_ingredient.title()} Delight"
        else:
            return f"{adjective} {main_ingredient.title()} Surprise"
    
    def _generate_cooking_steps(self, ingredients: List[str], recipe_type: str) -> List[Dict]:
        """Generate cooking steps with humor"""
        steps = []
        
        # Prep step
        verb = random.choice(self.cooking_verbs)
        steps.append({
            'step_number': 1,
            'instruction': f"First, {verb} your {ingredients[0]} like it owes you money (but in a loving way). This is where the magic begins!",
            'time_estimate': '5-10 minutes',
            'humor_level': 'high'
        })
        
        # Cooking steps based on type
        if recipe_type == 'baked':
            steps.append({
                'step_number': 2,
                'instruction': f"Preheat your oven to 375°F (or whatever temperature makes your oven happy). Mix your ingredients like you're conducting a delicious orchestra! 🎵",
                'time_estimate': '15 minutes',
                'humor_level': 'medium'
            })
            
            steps.append({
                'step_number': 3,
                'instruction': "Pop it in the oven and resist the urge to open the door every 2 minutes. Trust the process, young grasshopper!",
                'time_estimate': '25-30 minutes',
                'humor_level': 'high'
            })
        
        elif recipe_type == 'pasta':
            steps.append({
                'step_number': 2,
                'instruction': "Boil water like you're summoning a pasta spirit. Add salt generously - your pasta should taste like the sea (but in a good way)!",
                'time_estimate': '10 minutes',
                'humor_level': 'medium'
            })
        
        # Always add a finishing step
        steps.append({
            'step_number': len(steps) + 1,
            'instruction': "Plate your masterpiece with the confidence of a Michelin star chef. Take a photo for Instagram, then devour immediately!",
            'time_estimate': '2 minutes',
            'humor_level': 'high'
        })
        
        return steps
    
    def _estimate_cooking_time(self, recipe_type: str) -> str:
        """Estimate total cooking time"""
        time_map = {
            'baked': '45-60 minutes',
            'pasta': '20-30 minutes',
            'main_course': '30-45 minutes',
            'dessert': '60-90 minutes',
            'creative_mix': '25-40 minutes'
        }
        return time_map.get(recipe_type, '30-45 minutes')
    
    def _rate_difficulty(self, ingredients: List[str], recipe_type: str) -> str:
        """Rate recipe difficulty"""
        if len(ingredients) <= 3:
            return "Beginner (You got this!)"
        elif len(ingredients) <= 6:
            return "Intermediate (Flex those chef muscles!)"
        else:
            return "Advanced (Time to show off!)"
    
    def _generate_fun_fact(self, dish_name: str) -> str:
        """Generate a fun fact about the dish"""
        facts = [
            f"Fun fact: {dish_name} was probably invented by someone who was really, really hungry!",
            f"Did you know? {dish_name} tastes 47% better when you cook it with love and good music!",
            f"Chef's secret: {dish_name} is scientifically proven to make you happier (results may vary)!",
            f"Legend says {dish_name} brings good luck to anyone brave enough to make it!"
        ]
        return random.choice(facts)
    
    def _generate_chef_tip(self) -> str:
        """Generate a helpful chef tip"""
        tips = [
            "Pro tip: Taste as you go - cooking is like a conversation with your taste buds!",
            "Remember: Confidence is the secret ingredient that makes everything taste better!",
            "Chef wisdom: If you drop something, it's just gravity seasoning. Keep going!",
            "Golden rule: Cook with music on - your food will absorb the good vibes!"
        ]
        return random.choice(tips)
    
    def _generate_error_response(self, error_message: str) -> Dict[str, Any]:
        """Generate a humorous error response"""
        return {
            'error': True,
            'message': error_message,
            'suggestion': "How about we start with some ingredients? Even I can't make magic out of thin air! 🎩✨",
            'humor': "Don't worry, even Gordon Ramsay started somewhere (probably with more ingredients though)!"
        }