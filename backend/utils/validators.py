from typing import List, Dict, Any, Tuple
import re

class InputValidator:
    """Validate user inputs before processing"""
    
    @staticmethod
    def validate_ingredients(ingredients: List[str]) -> Tuple[bool, str]:
        """
        Validate ingredients list
        
        Args:
            ingredients: List of ingredient strings
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not ingredients:
            return False, "Please provide at least one ingredient!"
        
        if len(ingredients) > 20:
            return False, "Whoa there! Maximum 20 ingredients please. We're making food, not a chemistry experiment!"
        
        # Check each ingredient
        for ingredient in ingredients:
            if not ingredient or not ingredient.strip():
                return False, "Empty ingredients aren't very tasty! Please provide valid ingredient names."
            
            if len(ingredient.strip()) > 50:
                return False, f"Ingredient name too long: '{ingredient[:20]}...'. Keep it simple!"
            
            # Check for suspicious characters (basic sanitization)
            if re.search(r'[<>\"\'&]', ingredient):
                return False, "Invalid characters in ingredient names. Keep it clean!"
        
        return True, "Ingredients look delicious!"
    
    @staticmethod
    def validate_preferences(preferences: List[str]) -> Tuple[bool, str]:
        """
        Validate cooking preferences
        
        Args:
            preferences: List of preference strings
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not preferences:
            return True, "No preferences - we'll surprise you!"
        
        if len(preferences) > 10:
            return False, "Too many preferences! Pick your top 10 favorites."
        
        valid_preferences = [
            'baked', 'fried', 'grilled', 'boiled', 'steamed',
            'high protein', 'low carb', 'vegetarian', 'vegan',
            'spicy', 'mild', 'sweet', 'savory', 'quick', 'healthy'
        ]
        
        for pref in preferences:
            if pref.lower() not in valid_preferences:
                return False, f"Unknown preference: '{pref}'. Try something like 'baked', 'spicy', or 'healthy'!"
        
        return True, "Preferences noted, chef!"
    
    @staticmethod
    def sanitize_input(text: str) -> str:
        """
        Clean and sanitize text input
        
        Args:
            text: Raw text input
            
        Returns:
            Cleaned text
        """
        if not text:
            return ""
        
        # Remove extra whitespace
        text = text.strip()
        
        # Remove potentially dangerous characters
        text = re.sub(r'[<>\"\'&]', '', text)
        
        # Limit length
        if len(text) > 100:
            text = text[:100]
        
        return text