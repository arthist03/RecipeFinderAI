from typing import Dict, Any, List
import re

def validate_search_request(data: Dict[str, Any]) -> Dict[str, Any]:
    """Validate recipe search request data"""
    
    if not data:
        return {
            'valid': False,
            'message': 'Request body is required'
        }
    
    # Validate ingredients
    ingredients = data.get('ingredients', '').strip()
    if not ingredients:
        return {
            'valid': False,
            'message': 'Ingredients are required'
        }
    
    # Check ingredients format and length
    ingredient_list = [ing.strip() for ing in ingredients.split(',') if ing.strip()]
    
    if len(ingredient_list) == 0:
        return {
            'valid': False,
            'message': 'At least one ingredient is required'
        }
    
    if len(ingredient_list) > 15:
        return {
            'valid': False,
            'message': 'Maximum 15 ingredients allowed'
        }
    
    # Validate individual ingredients
    for ingredient in ingredient_list:
        if len(ingredient) < 2:
            return {
                'valid': False,
                'message': f'Ingredient "{ingredient}" is too short (minimum 2 characters)'
            }
        
        if len(ingredient) > 50:
            return {
                'valid': False,
                'message': f'Ingredient "{ingredient}" is too long (maximum 50 characters)'
            }
        
        # Check for valid characters (letters, numbers, spaces, hyphens)
        if not re.match(r'^[a-zA-Z0-9\s\-\']+$', ingredient):
            return {
                'valid': False,
                'message': f'Ingredient "{ingredient}" contains invalid characters'
            }
    
    # Validate mood
    mood = data.get('mood', 'comfort').lower().strip()
    valid_moods = ['comfort', 'fresh', 'indulgent', 'spicy', 'sweet', 'savory']
    
    if mood not in valid_moods:
        return {
            'valid': False,
            'message': f'Invalid mood. Must be one of: {", ".join(valid_moods)}'
        }
    
    # Validate userName (optional)
    user_name = data.get('userName', '').strip()
    if user_name:
        if len(user_name) > 50:
            return {
                'valid': False,
                'message': 'User name is too long (maximum 50 characters)'
            }
        
        if not re.match(r'^[a-zA-Z0-9\s\-\']+$', user_name):
            return {
                'valid': False,
                'message': 'User name contains invalid characters'
            }
    
    return {
        'valid': True,
        'message': 'Valid request'
    }

def validate_recipe_data(recipe: Dict[str, Any]) -> Dict[str, Any]:
    """Validate recipe data structure"""
    
    required_fields = ['name', 'description', 'ingredients', 'instructions']
    
    for field in required_fields:
        if field not in recipe:
            return {
                'valid': False,
                'message': f'Required field "{field}" is missing'
            }
    
    # Validate name
    if not isinstance(recipe['name'], str) or len(recipe['name'].strip()) < 3:
        return {
            'valid': False,
            'message': 'Recipe name must be at least 3 characters long'
        }
    
    # Validate description
    if not isinstance(recipe['description'], str) or len(recipe['description'].strip()) < 10:
        return {
            'valid': False,
            'message': 'Recipe description must be at least 10 characters long'
        }
    
    # Validate ingredients
    if not isinstance(recipe['ingredients'], list) or len(recipe['ingredients']) == 0:
        return {
            'valid': False,
            'message': 'Recipe must have at least one ingredient'
        }
    
    # Validate instructions
    if not isinstance(recipe['instructions'], list) or len(recipe['instructions']) == 0:
        return {
            'valid': False,
            'message': 'Recipe must have at least one instruction'
        }
    
    # Validate optional numeric fields
    numeric_fields = ['rating', 'cookTime']
    for field in numeric_fields:
        if field in recipe:
            if field == 'rating':
                if not isinstance(recipe[field], (int, float)) or not (0 <= recipe[field] <= 5):
                    return {
                        'valid': False,
                        'message': 'Rating must be a number between 0 and 5'
                    }
    
    return {
        'valid': True,
        'message': 'Valid recipe data'
    }

def sanitize_input(text: str) -> str:
    """Sanitize user input text"""
    if not isinstance(text, str):
        return ""
    
    # Remove excessive whitespace
    text = re.sub(r'\s+', ' ', text.strip())
    
    # Remove potentially harmful characters
    text = re.sub(r'[<>"\']', '', text)
    
    return text

def validate_pagination_params(page: int, limit: int) -> Dict[str, Any]:
    """Validate pagination parameters"""
    
    if not isinstance(page, int) or page < 1:
        return {
            'valid': False,
            'message': 'Page must be a positive integer'
        }
    
    if not isinstance(limit, int) or limit < 1 or limit > 100:
        return {
            'valid': False,
            'message': 'Limit must be between 1 and 100'
        }
    
    return {
        'valid': True,
        'message': 'Valid pagination parameters'
    }