from flask import Blueprint, request, jsonify
from utils.database import db_connection
from utils.validators import sanitize_input
from config import Config
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

user_bp = Blueprint('users', __name__)

@user_bp.route('/profile', methods=['POST'])
def create_or_update_profile():
    """Create or update user profile"""
    try:
        data = request.get_json()
        
        if not data or 'name' not in data:
            return jsonify({
                'error': 'User name is required',
                'code': 'MISSING_NAME'
            }), 400
        
        name = sanitize_input(data['name']).strip()
        if not name:
            return jsonify({
                'error': 'Valid user name is required',
                'code': 'INVALID_NAME'
            }), 400
        
        # Get users collection
        users_collection = db_connection.get_collection(Config.USERS_COLLECTION)
        
        # Prepare user data
        user_data = {
            'name': name,
            'email': sanitize_input(data.get('email', '')),
            'preferences': {
                'favoriteIngredients': data.get('favoriteIngredients', []),
                'dietaryRestrictions': data.get('dietaryRestrictions', []),
                'preferredMoods': data.get('preferredMoods', ['comfort'])
            },
            'updatedAt': datetime.utcnow()
        }
        
        # Update or create user
        result = users_collection.update_one(
            {'name': name},
            {
                '$set': user_data,
                '$setOnInsert': {'createdAt': datetime.utcnow()}
            },
            upsert=True
        )
        
        return jsonify({
            'success': True,
            'message': 'Profile updated successfully',
            'userId': str(result.upserted_id) if result.upserted_id else None
        })
        
    except Exception as e:
        logger.error(f"Profile update error: {e}")
        return jsonify({
            'error': 'Failed to update profile',
            'code': 'PROFILE_ERROR'
        }), 500

@user_bp.route('/profile/<username>', methods=['GET'])
def get_profile(username):
    """Get user profile"""
    try:
        username = sanitize_input(username).strip()
        if not username:
            return jsonify({
                'error': 'Valid username is required',
                'code': 'INVALID_USERNAME'
            }), 400
        
        users_collection = db_connection.get_collection(Config.USERS_COLLECTION)
        user = users_collection.find_one({'name': username})
        
        if not user:
            return jsonify({
                'error': 'User not found',
                'code': 'USER_NOT_FOUND'
            }), 404
        
        # Remove sensitive data and convert ObjectId
        user['_id'] = str(user['_id'])
        
        return jsonify({
            'success': True,
            'user': user
        })
        
    except Exception as e:
        logger.error(f"Get profile error: {e}")
        return jsonify({
            'error': 'Failed to get profile',
            'code': 'PROFILE_ERROR'
        }), 500

@user_bp.route('/search-history/<username>', methods=['GET'])
def get_search_history(username):
    """Get user's search history"""
    try:
        username = sanitize_input(username).strip()
        if not username:
            return jsonify({
                'error': 'Valid username is required',
                'code': 'INVALID_USERNAME'
            }), 400
        
        # Get pagination parameters
        page = request.args.get('page', 1, type=int)
        limit = min(request.args.get('limit', 20, type=int), 100)
        skip = (page - 1) * limit
        
        searches_collection = db_connection.get_collection(Config.SEARCHES_COLLECTION)
        
        # Get search history
        searches = list(
            searches_collection
            .find({'userName': username})
            .sort('timestamp', -1)
            .skip(skip)
            .limit(limit)
        )
        
        # Convert ObjectIds to strings
        for search in searches:
            search['_id'] = str(search['_id'])
        
        # Get total count
        total_count = searches_collection.count_documents({'userName': username})
        
        return jsonify({
            'success': True,
            'searches': searches,
            'pagination': {
                'page': page,
                'limit': limit,
                'total': total_count,
                'pages': (total_count + limit - 1) // limit
            }
        })
        
    except Exception as e:
        logger.error(f"Search history error: {e}")
        return jsonify({
            'error': 'Failed to get search history',
            'code': 'HISTORY_ERROR'
        }), 500

@user_bp.route('/favorites/<username>', methods=['GET'])
def get_favorites(username):
    """Get user's favorite recipes"""
    try:
        username = sanitize_input(username).strip()
        if not username:
            return jsonify({
                'error': 'Valid username is required',
                'code': 'INVALID_USERNAME'
            }), 400
        
        favorites_collection = db_connection.get_collection(Config.FAVORITES_COLLECTION)
        
        favorites = list(
            favorites_collection
            .find({'userName': username})
            .sort('createdAt', -1)
        )
        
        # Convert ObjectIds to strings
        for favorite in favorites:
            favorite['_id'] = str(favorite['_id'])
        
        return jsonify({
            'success': True,
            'favorites': favorites
        })
        
    except Exception as e:
        logger.error(f"Get favorites error: {e}")
        return jsonify({
            'error': 'Failed to get favorites',
            'code': 'FAVORITES_ERROR'
        }), 500

@user_bp.route('/favorites', methods=['POST'])
def add_favorite():
    """Add recipe to favorites"""
    try:
        data = request.get_json()
        
        required_fields = ['userName', 'recipeId', 'recipeName']
        for field in required_fields:
            if not data.get(field):
                return jsonify({
                    'error': f'{field} is required',
                    'code': 'MISSING_FIELD'
                }), 400
        
        favorites_collection = db_connection.get_collection(Config.FAVORITES_COLLECTION)
        
        favorite_data = {
            'userName': sanitize_input(data['userName']),
            'recipeId': sanitize_input(data['recipeId']),
            'recipeName': sanitize_input(data['recipeName']),
            'recipeData': data.get('recipeData', {}),
            'createdAt': datetime.utcnow()
        }
        
        # Check if already favorited
        existing = favorites_collection.find_one({
            'userName': favorite_data['userName'],
            'recipeId': favorite_data['recipeId']
        })
        
        if existing:
            return jsonify({
                'success': True,
                'message': 'Recipe already in favorites'
            })
        
        # Add to favorites
        result = favorites_collection.insert_one(favorite_data)
        
        return jsonify({
            'success': True,
            'message': 'Recipe added to favorites',
            'favoriteId': str(result.inserted_id)
        })
        
    except Exception as e:
        logger.error(f"Add favorite error: {e}")
        return jsonify({
            'error': 'Failed to add favorite',
            'code': 'FAVORITE_ERROR'
        }), 500

@user_bp.route('/favorites/<username>/<recipe_id>', methods=['DELETE'])
def remove_favorite(username, recipe_id):
    """Remove recipe from favorites"""
    try:
        username = sanitize_input(username).strip()
        recipe_id = sanitize_input(recipe_id).strip()
        
        if not username or not recipe_id:
            return jsonify({
                'error': 'Username and recipe ID are required',
                'code': 'MISSING_PARAMETERS'
            }), 400
        
        favorites_collection = db_connection.get_collection(Config.FAVORITES_COLLECTION)
        
        result = favorites_collection.delete_one({
            'userName': username,
            'recipeId': recipe_id
        })
        
        if result.deleted_count == 0:
            return jsonify({
                'error': 'Favorite not found',
                'code': 'FAVORITE_NOT_FOUND'
            }), 404
        
        return jsonify({
            'success': True,
            'message': 'Recipe removed from favorites'
        })
        
    except Exception as e:
        logger.error(f"Remove favorite error: {e}")
        return jsonify({
            'error': 'Failed to remove favorite',
            'code': 'FAVORITE_ERROR'
        }), 500