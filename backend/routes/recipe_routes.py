from flask import Blueprint, request, jsonify, current_app
from flask_pymongo import PyMongo
from models.ai_model import RecipeAIModel
from models.recipe_model import Recipe, UserQuery
from utils.db_utils import DatabaseManager
from utils.validators import InputValidator
import time
import logging

# Create blueprint
recipe_bp = Blueprint('recipes', __name__)

# Initialize AI model (you might want to do this once at app startup)
ai_model = RecipeAIModel()

# Set up logging
logger = logging.getLogger(__name__)

@recipe_bp.route('/generate-recipe', methods=['POST'])
def generate_recipe():
    """
    Main endpoint to generate recipes based on ingredients
    
    Expected JSON format:
    {
        "ingredients": ["chicken", "rice", "tomatoes"],
        "preferences": ["baked", "high protein"]
    }
    """
    start_time = time.time()
    
    try:
        # Get data from request
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'No data provided! Send me some ingredients to work with!',
                'humor': 'I may be an AI, but I still need ingredients to make magic happen! 🎩'
            }), 400
        
        # Extract ingredients and preferences
        ingredients = data.get('ingredients', [])
        preferences = data.get('preferences', [])
        
        # Validate inputs
        is_valid, message = InputValidator.validate_ingredients(ingredients)
        if not is_valid:
            return jsonify({
                'success': False,
                'error': message,
                'humor': 'Even Gordon Ramsay needs proper ingredients! 👨‍🍳'
            }), 400
        
        is_valid, message = InputValidator.validate_preferences(preferences)
        if not is_valid:
            return jsonify({
                'success': False,
                'error': message,
                'humor': 'Let\'s keep those preferences realistic, shall we? 😄'
            }), 400
        
        # Clean inputs
        ingredients = [InputValidator.sanitize_input(ing) for ing in ingredients]
        preferences = [InputValidator.sanitize_input(pref) for pref in preferences]
        
        # Check database for existing similar recipe (optional optimization)
        db_manager = DatabaseManager(current_app.extensions['pymongo'])
        existing_recipe = db_manager.get_recipe_by_ingredients(ingredients)
        
        if existing_recipe and current_app.config.get('USE_CACHE', True):
            logger.info("Returning cached recipe")
            # Return existing recipe with updated timestamp
            recipe_data = existing_recipe
            recipe_data['cached'] = True
        else:
            # Generate new recipe using AI model
            logger.info(f"Generating new recipe for ingredients: {ingredients}")
            recipe_data = ai_model.generate_recipe(ingredients, preferences)
            
            # Save to database
            if not recipe_data.get('error'):
                recipe_obj = Recipe(
                    dish_name=recipe_data['dish_name'],
                    ingredients=recipe_data['ingredients_used'],
                    steps=recipe_data['steps'],
                    recipe_type=recipe_data['recipe_type'],
                    cooking_time=recipe_data['cooking_time'],
                    difficulty=recipe_data['difficulty'],
                    intro=recipe_data.get('intro', ''),
                    fun_fact=recipe_data.get('fun_fact', ''),
                    chef_tip=recipe_data.get('chef_tip', '')
                )
                
                db_manager.save_recipe(recipe_obj.to_dict())
        
        # Log user query for analytics
        query_obj = UserQuery(
            ingredients=ingredients,
            preferences=preferences,
            user_ip=request.remote_addr,
            generated_recipe=recipe_data
        )
        query_obj.response_time = time.time() - start_time
        db_manager.save_user_query(query_obj.to_dict())
        
        # Add performance info
        recipe_data['response_time'] = f"{time.time() - start_time:.2f} seconds"
        recipe_data['success'] = True
        
        return jsonify(recipe_data), 200
        
    except Exception as e:
        logger.error(f"Error generating recipe: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Oops! Something went wrong in the kitchen!',
            'humor': 'Even the best chefs burn toast sometimes. Let\'s try again! 🍞',
            'details': str(e) if current_app.debug else 'Internal server error'
        }), 500

@recipe_bp.route('/popular-ingredients', methods=['GET'])
def get_popular_ingredients():
    """Get most popular ingredients from user queries"""
    try:
        db_manager = DatabaseManager(current_app.extensions['pymongo'])
        popular = db_manager.get_popular_ingredients(limit=15)
        
        return jsonify({
            'success': True,
            'popular_ingredients': popular,
            'message': 'Here are the ingredients everyone loves!'
        }), 200
    except Exception as e:
        logger.error(f"Error retrieving popular ingredients: {e}")
    return jsonify({
        'success': False,
        'message': 'Failed to retrieve popular ingredients.'
    }), 500 