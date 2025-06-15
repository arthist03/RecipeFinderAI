from flask import Blueprint, request, jsonify
from services.ai_service import ai_service
from services.vector_search import vector_search_service
from utils.validators import validate_search_request
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

recipe_bp = Blueprint('recipes', __name__)

@recipe_bp.route('/search', methods=['POST'])
def search_recipes():
    """Search for recipes based on ingredients and mood using AI and vector search"""
    try:
        data = request.get_json()
        
        # Validate request
        validation_result = validate_search_request(data)
        if not validation_result['valid']:
            return jsonify({
                'error': validation_result['message'],
                'code': 'VALIDATION_ERROR'
            }), 400
        
        # Extract search parameters
        ingredients_str = data.get('ingredients', '').strip()
        if not ingredients_str:
            return jsonify({
                'error': 'Please provide at least one ingredient',
                'code': 'MISSING_INGREDIENTS'
            }), 400
        
        # Parse ingredients
        ingredients = [ing.strip().lower() for ing in ingredients_str.split(',') if ing.strip()]
        mood = data.get('mood', 'comfort').lower()
        user_name = data.get('userName', 'Chef')
        
        logger.info(f"Recipe search request - User: {user_name}, Ingredients: {ingredients}, Mood: {mood}")
        
        # Use AI service to generate personalized recipes (primary results)
        ai_recipes = ai_service.predict_recipes(ingredients, mood)
        
        # Search for similar recipes in database (supplementary results)
        similar_recipes = vector_search_service.search_similar_recipes(
            ingredients, 
            mood=mood, 
            limit=2
        )
        
        # Combine results - prioritize AI-generated recipes
        all_recipes = ai_recipes[:3]  # Take top 3 AI recipes
        
        # If we have fewer than 3 AI recipes, supplement with database recipes
        if len(all_recipes) < 3 and similar_recipes:
            needed = 3 - len(all_recipes)
            all_recipes.extend(similar_recipes[:needed])
        
        # Ensure we have exactly 3 recipes (pad with fallback if needed)
        while len(all_recipes) < 3:
            fallback_recipe = {
                "name": f"Simple {mood.title()} Creation",
                "description": f"A delightful {mood} dish made with your ingredients",
                "cookTime": "20 min",
                "difficulty": "Easy",
                "rating": 4.5,
                "image": "🍽️",
                "ingredients": [{"name": ing.title(), "amount": "as needed"} for ing in ingredients[:5]],
                "instructions": [
                    "Prepare your ingredients with care.",
                    "Cook them together until perfectly done.",
                    "Season to taste and serve with love."
                ],
                "tip": "Trust your instincts - you're the chef! 👨‍🍳",
                "tags": ingredients[:3] + [mood],
                "mood": mood
            }
            all_recipes.append(fallback_recipe)
        
        # Add unique IDs and ensure consistent format
        final_recipes = []
        for i, recipe in enumerate(all_recipes[:3]):
            recipe['id'] = f"recipe_{i+1}_{datetime.now().timestamp()}"
            
            # Ensure all required fields exist
            recipe.setdefault('rating', 4.5)
            recipe.setdefault('image', '🍽️')
            recipe.setdefault('tip', 'Enjoy this delicious creation!')
            recipe.setdefault('tags', ingredients[:3] + [mood])
            recipe.setdefault('mood', mood)
            
            final_recipes.append(recipe)
        
        # Build response
        response = {
            'success': True,
            'recipes': final_recipes,
            'searchQuery': {
                'ingredients': ingredients,
                'mood': mood,
                'userName': user_name
            },
            'metadata': {
                'totalResults': len(final_recipes),
                'aiGenerated': len(ai_recipes),
                'databaseMatches': len(similar_recipes),
                'timestamp': datetime.utcnow().isoformat()
            }
        }
        
        logger.info(f"Recipe search completed - User: {user_name}, Results: {len(final_recipes)}")
        return jsonify(response)
        
    except Exception as e:
        logger.error(f"Recipe search error: {str(e)}", exc_info=True)
        return jsonify({
            'error': 'An error occurred while searching for recipes. Please try again.',
            'code': 'SEARCH_ERROR'
        }), 500

@recipe_bp.route('/recipe/<recipe_id>', methods=['GET'])
def get_recipe_details(recipe_id):
    """Get detailed recipe information by ID"""
    try:
        # For AI-generated recipes, we don't store them in DB
        # This endpoint would be used for database-stored recipes
        # You can implement database lookup here if needed
        
        return jsonify({
            'error': 'Recipe details not found',
            'code': 'RECIPE_NOT_FOUND'
        }), 404
        
    except Exception as e:
        logger.error(f"Get recipe error: {e}")
        return jsonify({
            'error': 'Unable to fetch recipe details',
            'code': 'FETCH_ERROR'
        }), 500

@recipe_bp.route('/popular', methods=['GET'])
def get_popular_recipes():
    """Get popular recipes from database"""
    try:
        limit = request.args.get('limit', 10, type=int)
        limit = min(limit, 50)  # Cap at 50 recipes
        
        # Get popular recipes from database
        # This would query your recipes collection
        # For now, return empty array since we're focusing on AI generation
        
        return jsonify({
            'success': True,
            'recipes': [],
            'message': 'Popular recipes feature coming soon!'
        })
        
    except Exception as e:
        logger.error(f"Popular recipes error: {e}")
        return jsonify({
            'error': 'Unable to fetch popular recipes',
            'code': 'FETCH_ERROR'
        }), 500

@recipe_bp.route('/random', methods=['GET'])
def get_random_recipe():
    """Get a random recipe"""
    try:
        # Generate a random recipe using AI service
        random_ingredients = ['chicken', 'vegetables', 'herbs']
        random_mood = 'comfort'
        
        recipes = ai_service.predict_recipes(random_ingredients, random_mood)
        
        if recipes:
            recipe = recipes[0]
            recipe['id'] = f"random_{datetime.now().timestamp()}"
            
            return jsonify({
                'success': True,
                'recipe': recipe
            })
        else:
            return jsonify({
                'error': 'Unable to generate random recipe',
                'code': 'GENERATION_ERROR'
            }), 500
            
    except Exception as e:
        logger.error(f"Random recipe error: {e}")
        return jsonify({
            'error': 'Unable to fetch random recipe',
            'code': 'FETCH_ERROR'
        }), 500

@recipe_bp.route('/health', methods=['GET'])
def recipe_health_check():
    """Health check for recipe service"""
    try:
        # Test AI service
        ai_status = "healthy" if ai_service.embedding_model else "degraded"
        
        # Test vector search
        vector_status = "healthy" if vector_search_service.recipes_collection else "unavailable"
        
        return jsonify({
            'status': 'healthy',
            'services': {
                'ai_service': ai_status,
                'vector_search': vector_status
            },
            'timestamp': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Recipe health check error: {e}")
        return jsonify({
            'status': 'unhealthy',
            'error': str(e)
        }), 500