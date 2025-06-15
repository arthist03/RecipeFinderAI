from flask import Blueprint, request, jsonify
from services.recipe_service import recipe_service
from services.ai_service import ai_service
from services.vector_search import vector_search_service
from utils.validators import validate_search_request
import logging

logger = logging.getLogger(__name__)

recipe_bp = Blueprint('recipes', __name__)

@recipe_bp.route('/search', methods=['POST'])
def search_recipes():
    """Search for recipes based on ingredients and mood"""
    try:
        data = request.get_json()
        
        # Validate request
        validation_result = validate_search_request(data)
        if not validation_result['valid']:
            return jsonify({
                'error': validation_result['message']
            }), 400
        
        ingredients = data.get('ingredients', '').split(',')
        ingredients = [ing.strip().lower() for ing in ingredients if ing.strip()]
        mood = data.get('mood', 'comfort')
        user_name = data.get('userName', 'Chef')
        
        if not ingredients:
            return jsonify({
                'error': 'Please provide at least one ingredient'
            }), 400
        
        # Use AI service to generate personalized recipes
        ai_recipes = ai_service.predict_recipes(ingredients, mood)
        
        # Also search for similar recipes in database
        similar_recipes = vector_search_service.search_similar_recipes(ingredients, limit=5)
        
        # Combine and format results
        all_recipes = ai_recipes + similar_recipes[:2]  # AI recipes + top 2 similar
        
        # Ensure we have exactly 3 recipes
        final_recipes = all_recipes[:3]
        
        # Add unique IDs
        for i, recipe in enumerate(final_recipes):
            recipe['id'] = i + 1
        
        response = {
            'recipes': final_recipes,
            'searchQuery': {
                'ingredients': ingredients,
                'mood': mood,
                'userName': user_name
            },
            'timestamp': str(datetime.utcnow())
        }
        
        logger.info(f"Recipe search completed for {user_name}: {len(final_recipes)} recipes")
        return jsonify(response)
        
    except Exception as e:
        logger.error(f"Recipe search error: {e}")
        return jsonify({
            'error': 'An error occurred while searching for recipes'
        }), 500

@recipe_bp.route('/recipe/<int:recipe_id>', methods=['GET'])
def get_recipe_details(recipe_id):
    """Get detailed recipe information"""
    try:
        recipe = recipe_service.get_recipe_by_id(recipe_id)
        if not recipe:
            return jsonify({'error': 'Recipe not found'}), 404
        
        return jsonify(recipe)
    except Exception as e:
        logger.error(f"Get recipe error: {e}")
        return jsonify({'error': 'Recipe not found'}), 404

@recipe_bp.route('/popular', methods=['GET'])
def get_popular_recipes():
    """Get popular recipes"""
    try:
        limit = request.args.get('limit', 10, type=int)
        recipes = recipe_service.get_popular_recipes(limit)
        return jsonify({'recipes': recipes})
    except Exception as e:
        logger.error(f"Popular recipes error: {e}")
        return jsonify({'error': 'Unable to fetch popular recipes'}), 500

@recipe_bp.route('/random', methods=['GET'])
def get_random_recipe():
    """Get a random recipe"""
    try:
        recipe = recipe_service.get_random_recipe()
        return jsonify(recipe)
    except Exception as e:
        logger.error(f"Random recipe error: {e}")
        return jsonify({'error': 'Unable to fetch random recipe'}), 500