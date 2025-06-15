from datetime import datetime
from typing import List, Dict, Any, Optional

class Recipe:
    """Recipe data model for MongoDB"""
    
    def __init__(self, dish_name: str, ingredients: List[str], 
                 steps: List[Dict], recipe_type: str, 
                 cooking_time: str, difficulty: str, **kwargs):
        self.dish_name = dish_name
        self.ingredients = ingredients
        self.steps = steps
        self.recipe_type = recipe_type
        self.cooking_time = cooking_time
        self.difficulty = difficulty
        self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
        
        # Optional fields
        self.intro = kwargs.get('intro', '')
        self.fun_fact = kwargs.get('fun_fact', '')
        self.chef_tip = kwargs.get('chef_tip', '')
        self.user_rating = kwargs.get('user_rating', None)
        self.times_generated = kwargs.get('times_generated', 1)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert recipe to dictionary for MongoDB storage"""
        return {
            'dish_name': self.dish_name,
            'ingredients': self.ingredients,
            'steps': self.steps,
            'recipe_type': self.recipe_type,
            'cooking_time': self.cooking_time,
            'difficulty': self.difficulty,
            'intro': self.intro,
            'fun_fact': self.fun_fact,
            'chef_tip': self.chef_tip,
            'user_rating': self.user_rating,
            'times_generated': self.times_generated,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Recipe':
        """Create Recipe object from dictionary"""
        return cls(
            dish_name=data['dish_name'],
            ingredients=data['ingredients'],
            steps=data['steps'],
            recipe_type=data['recipe_type'],
            cooking_time=data['cooking_time'],
            difficulty=data['difficulty'],
            intro=data.get('intro', ''),
            fun_fact=data.get('fun_fact', ''),
            chef_tip=data.get('chef_tip', ''),
            user_rating=data.get('user_rating'),
            times_generated=data.get('times_generated', 1)
        )

class UserQuery:
    """User query data model for MongoDB"""
    
    def __init__(self, ingredients: List[str], preferences: List[str], 
                 user_ip: str, generated_recipe: Dict[str, Any]):
        self.ingredients = ingredients
        self.preferences = preferences
        self.user_ip = user_ip
        self.generated_recipe = generated_recipe
        self.timestamp = datetime.utcnow()
        self.response_time = None  # Will be set after AI processing
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert query to dictionary for MongoDB storage"""
        return {
            'ingredients': self.ingredients,
            'preferences': self.preferences,
            'user_ip': self.user_ip,
            'generated_recipe': self.generated_recipe,
            'timestamp': self.timestamp,
            'response_time': self.response_time
        }