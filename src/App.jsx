import React, { useState } from 'react';
import './App.css';

function App() {
  const [userName, setUserName] = useState('');
  const [ingredients, setIngredients] = useState('');
  const [mood, setMood] = useState('comfort');
  const [currentView, setCurrentView] = useState('welcome'); // Always starts with welcome
  const [isLoading, setIsLoading] = useState(false);
  const [recipes, setRecipes] = useState([]);
  const [selectedRecipe, setSelectedRecipe] = useState(null);

  const getTimeBasedGreeting = () => {
    const hour = new Date().getHours();
    if (hour >= 5 && hour < 12) return 'Good morning';
    if (hour >= 12 && hour < 17) return 'Good afternoon';
    if (hour >= 17 && hour < 22) return 'Good evening';
    return 'Good night';
  };

  const handleNameSubmit = (e) => {
    e.preventDefault();
    if (userName.trim()) {
      setCurrentView('search');
    }
  };

  // Enhanced search function with better error handling
  const handleSearch = async (e) => {
    e.preventDefault();
    if (!ingredients.trim()) return;
    
    setIsLoading(true);
    
    try {
      const searchData = {
        ingredients: ingredients,
        mood: mood,
        userName: userName
      };
      
      const response = await fetch('http://localhost:5000/api/v1/recipes/search', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(searchData)
      });
      
      if (!response.ok) {
        throw new Error(`Search failed: ${response.status}`);
      }
      
      const data = await response.json();
      
      if (data.success && data.recipes) {
        setRecipes(data.recipes);
        setCurrentView('results');
      } else {
        throw new Error('Invalid response format');
      }
      
    } catch (error) {
      console.error('Search error:', error);
      // Enhanced fallback with more variety
      setRecipes(generateFallbackRecipes(ingredients, mood));
      setCurrentView('results');
    } finally {
      setIsLoading(false);
    }
  };

  const generateFallbackRecipes = (ingredients, mood) => {
    const ingredientList = ingredients.split(',').map(ing => ing.trim());
    
    return [
      {
        id: 'fallback-1',
        name: `${mood.charAt(0).toUpperCase() + mood.slice(1)} ${ingredientList[0]?.charAt(0).toUpperCase() + ingredientList[0]?.slice(1)} Bowl`,
        description: `A delightful ${mood} dish featuring your favorite ingredients`,
        cookTime: '25 min',
        difficulty: 'Easy',
        rating: 4.6,
        image: mood === 'comfort' ? '🍲' : mood === 'fresh' ? '🥗' : '✨',
        ingredients: ingredientList.slice(0, 5).map(ing => ({
          name: ing.charAt(0).toUpperCase() + ing.slice(1),
          amount: 'as needed'
        })),
        instructions: [
          'Prepare your ingredients with care and attention.',
          'Cook them together until perfectly tender.',
          'Season to taste and serve with love.',
          'Enjoy your personalized creation!'
        ],
        tip: 'Trust your instincts - you know your taste best! 👨‍🍳'
      },
      {
        id: 'fallback-2',
        name: `Chef's Special ${ingredientList[1]?.charAt(0).toUpperCase() + ingredientList[1]?.slice(1) || 'Surprise'}`,
        description: `A creative fusion of your ingredients in perfect harmony`,
        cookTime: '30 min',
        difficulty: 'Medium',
        rating: 4.7,
        image: '🍽️',
        ingredients: ingredientList.slice(0, 6).map(ing => ({
          name: ing.charAt(0).toUpperCase() + ing.slice(1),
          amount: 'to taste'
        })),
        instructions: [
          'Start by preparing your main ingredients.',
          'Combine them using your preferred cooking method.',
          'Add seasonings and let flavors develop.',
          'Plate beautifully and enjoy!'
        ],
        tip: 'Cooking is an art - let your creativity shine! ✨'
      },
      {
        id: 'fallback-3',
        name: `Simple ${mood.charAt(0).toUpperCase() + mood.slice(1)} Delight`,
        description: `Sometimes the simplest dishes are the most satisfying`,
        cookTime: '20 min',
        difficulty: 'Simple',
        rating: 4.8,
        image: '💚',
        ingredients: ingredientList.slice(0, 4).map(ing => ({
          name: ing.charAt(0).toUpperCase() + ing.slice(1),
          amount: '1 portion'
        })),
        instructions: [
          'Keep it simple and focus on quality.',
          'Let each ingredient shine.',
          'Cook with patience and love.',
          'Savor every bite!'
        ],
        tip: 'The best meals come from the heart! 💚'
      }
    ];
  };

  const selectRecipe = (recipe) => {
    setSelectedRecipe(recipe);
    setCurrentView('recipe');
  };

  const goBack = () => {
    if (currentView === 'recipe') {
      setCurrentView('results');
    } else if (currentView === 'results') {
      setCurrentView('search');
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-amber-50 to-orange-50 font-sans text-gray-800 leading-relaxed">
      {/* Welcome View */}
      {currentView === 'welcome' && (
        <div className="min-h-screen flex items-center justify-center p-8">
          <div className="text-center bg-white p-12 rounded-3xl shadow-2xl max-w-lg w-full">
            <div className="text-6xl mb-6 animate-bounce">👋</div>
            <h1 className="text-3xl font-semibold text-gray-900 mb-4">Welcome to your kitchen companion!</h1>
            <p className="text-lg text-gray-600 mb-8 leading-relaxed">I'm here to help you create something delicious. What should I call you?</p>
            
            <div className="flex flex-col gap-6">
              <input
                type="text"
                value={userName}
                onChange={(e) => setUserName(e.target.value)}
                placeholder="Enter your name..."
                className="w-full p-4 text-lg border-2 border-gray-200 rounded-2xl outline-none transition-all duration-300 bg-gray-50 text-center focus:border-indigo-500 focus:bg-white focus:shadow-lg focus:shadow-indigo-500/20"
                autoFocus
                onKeyPress={(e) => e.key === 'Enter' && handleNameSubmit(e)}
              />
              <button 
                onClick={handleNameSubmit}
                className="p-4 text-lg font-semibold bg-gradient-to-r from-indigo-500 to-purple-600 text-white border-none rounded-2xl cursor-pointer transition-all duration-300 hover:transform hover:-translate-y-1 hover:shadow-xl hover:shadow-indigo-500/40 disabled:opacity-60 disabled:cursor-not-allowed disabled:transform-none"
                disabled={!userName.trim()}
              >
                Let's cook together! 🍳
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Search View */}
      {currentView === 'search' && (
        <div className="min-h-screen flex flex-col justify-center items-center p-8 text-center">
          <div className="mb-12">
            <h1 className="text-4xl font-semibold text-gray-900 mb-4">{getTimeBasedGreeting()}, {userName}! ✨</h1>
            <p className="text-xl text-gray-600">What shall we create together today?</p>
          </div>
          
          <div className="bg-white p-10 rounded-2xl shadow-xl w-full max-w-md">
            <div>
              <div className="mb-8">
                <label className="block text-base font-medium text-gray-700 mb-2">What's in your kitchen?</label>
                <input
                  type="text"
                  value={ingredients}
                  onChange={(e) => setIngredients(e.target.value)}
                  placeholder="chicken, pasta, tomatoes..."
                  className="w-full p-4 text-base border-2 border-gray-200 rounded-xl outline-none transition-all duration-300 bg-gray-50 focus:border-indigo-500 focus:bg-white focus:shadow-lg focus:shadow-indigo-500/20"
                  onKeyPress={(e) => e.key === 'Enter' && handleSearch(e)}
                />
              </div>
              
              <div className="mb-8">
                <label className="block text-base font-medium text-gray-700 mb-4">What's your mood?</label>
                <div className="flex gap-4 justify-center mb-8">
                  {[
                    { value: 'comfort', emoji: '🏠', label: 'Comfort' },
                    { value: 'fresh', emoji: '🌿', label: 'Fresh' },
                    { value: 'indulgent', emoji: '✨', label: 'Indulgent' }
                  ].map(option => (
                    <button
                      key={option.value}
                      type="button"
                      className={`flex flex-col items-center gap-2 p-4 border-2 rounded-xl bg-white cursor-pointer transition-all duration-300 flex-1 hover:border-gray-300 hover:transform hover:-translate-y-1 ${
                        mood === option.value 
                          ? 'border-indigo-500 bg-blue-50 transform -translate-y-1' 
                          : 'border-gray-200'
                      }`}
                      onClick={() => setMood(option.value)}
                    >
                      <span className="text-2xl">{option.emoji}</span>
                      <span className="text-sm font-medium">{option.label}</span>
                    </button>
                  ))}
                </div>
              </div>
              
              <button 
                onClick={handleSearch}
                className="w-full p-4 text-lg font-semibold bg-gradient-to-r from-indigo-500 to-purple-600 text-white border-none rounded-xl cursor-pointer transition-all duration-300 hover:transform hover:-translate-y-1 hover:shadow-xl hover:shadow-indigo-500/40 disabled:opacity-60 disabled:cursor-not-allowed disabled:transform-none"
                disabled={!ingredients.trim()}
              >
                Find My Perfect Recipe
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Enhanced Loading View with Cooking Animations */}
      {isLoading && (
        <div className="min-h-screen flex items-center justify-center text-center">
          <div className="bg-white p-12 rounded-2xl shadow-xl max-w-md">
            <div className="text-6xl mb-4 animate-bounce">👨‍🍳</div>
            <h2 className="text-2xl text-gray-700 mb-2">Cooking up something special...</h2>
            <p className="text-gray-600 mb-8">Our AI chef is crafting your perfect recipes</p>
            
            {/* Enhanced animated cooking emojis */}
            <div className="flex justify-center gap-3 mb-6 flex-wrap">
              {['🍕', '🥕', '🥣', '🍳', '🧄', '🌶️', '🥘', '🍅', '🧅'].map((emoji, index) => (
                <div
                  key={index}
                  className="text-2xl animate-bounce"
                  style={{ 
                    animationDelay: `${index * 0.15}s`,
                    animationDuration: '1.2s'
                  }}
                >
                  {emoji}
                </div>
              ))}
            </div>
            
            {/* Enhanced progress indicator */}
            <div className="flex justify-center gap-2 mb-4">
              {[0, 1, 2, 3, 4].map(i => (
                <div
                  key={i}
                  className="w-2 h-2 bg-indigo-500 rounded-full animate-pulse"
                  style={{ 
                    animationDelay: `${i * 0.2}s`,
                    animationDuration: '1s'
                  }}
                />
              ))}
            </div>
            
            {/* Rotating cooking tips */}
            <div className="text-sm text-gray-500 italic">
              {[
                "Analyzing your ingredients...",
                "Finding flavor combinations...",
                "Crafting personalized recipes...",
                "Adding the perfect finishing touches..."
              ][Math.floor(Date.now() / 1000) % 4]}
            </div>
          </div>
        </div>
      )}

      {/* Results View */}
      {currentView === 'results' && (
        <div className="min-h-screen p-8">
          <div className="text-center mb-12">
            <button className="bg-none border-none text-indigo-500 text-base cursor-pointer mb-8 p-2 rounded-lg transition-all duration-300 hover:bg-blue-50 hover:text-indigo-600" onClick={goBack}>
              ← Back to search
            </button>
            <h2 className="text-3xl text-gray-900 mb-2">Perfect matches for you</h2>
            <p className="text-gray-600 text-lg">Choose the one that speaks to your heart</p>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8 max-w-6xl mx-auto">
            {recipes.map((recipe, index) => (
              <div 
                key={recipe.id} 
                className="bg-white rounded-2xl overflow-hidden shadow-lg cursor-pointer transition-all duration-300 opacity-0 transform translate-y-8 animate-[slideUp_0.6s_ease_forwards] hover:transform hover:-translate-y-3 hover:shadow-2xl"
                style={{ animationDelay: `${index * 0.2}s` }}
                onClick={() => selectRecipe(recipe)}
              >
                <div className="h-32 flex items-center justify-center text-6xl bg-gradient-to-br from-yellow-200 to-orange-300">
                  {recipe.image}
                </div>
                <div className="p-6">
                  <h3 className="text-xl text-gray-900 mb-2 font-semibold">{recipe.name}</h3>
                  <p className="text-gray-600 mb-4 text-sm leading-relaxed">{recipe.description}</p>
                  <div className="flex gap-4 text-xs text-gray-500">
                    <span>{recipe.cookTime}</span>
                    <span>{recipe.difficulty}</span>
                    <span>⭐ {recipe.rating}</span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Recipe Detail View */}
      {currentView === 'recipe' && selectedRecipe && (
        <div className="min-h-screen p-8 max-w-4xl mx-auto">
          <div className="mb-12">
            <button className="bg-none border-none text-indigo-500 text-base cursor-pointer mb-8 p-2 rounded-lg transition-all duration-300 hover:bg-blue-50 hover:text-indigo-600" onClick={goBack}>
              ← All recipes
            </button>
            <div className="flex items-center gap-8 bg-white p-8 rounded-2xl shadow-lg">
              <div className="text-6xl flex-shrink-0">{selectedRecipe.image}</div>
              <div>
                <h1 className="text-3xl text-gray-900 mb-2">{selectedRecipe.name}</h1>
                <p className="text-gray-600 mb-4">{selectedRecipe.description}</p>
                <div className="flex gap-2 flex-wrap">
                  <span className="bg-gray-100 text-gray-700 px-3 py-1 rounded-full text-sm font-medium">{selectedRecipe.cookTime}</span>
                  <span className="bg-gray-100 text-gray-700 px-3 py-1 rounded-full text-sm font-medium">{selectedRecipe.difficulty}</span>
                  <span className="bg-gray-100 text-gray-700 px-3 py-1 rounded-full text-sm font-medium">⭐ {selectedRecipe.rating}</span>
                </div>
              </div>
            </div>
          </div>

          <div className="flex flex-col gap-8">
            <div className="bg-white p-8 rounded-2xl shadow-md">
              <h3 className="text-xl text-gray-800 mb-6 font-semibold">🛒 What you'll need</h3>
              <div className="grid gap-3">
                {selectedRecipe.ingredients.map((ingredient, index) => (
                  <div key={index} className="flex justify-between items-center p-4 bg-blue-50 rounded-xl border-l-4 border-indigo-500">
                    <span className="font-medium text-gray-700">{ingredient.name}</span>
                    <span className="text-indigo-600 font-semibold">{ingredient.amount}</span>
                  </div>
                ))}
              </div>
            </div>

            <div className="bg-white p-8 rounded-2xl shadow-md">
              <h3 className="text-xl text-gray-800 mb-6 font-semibold">👨‍🍳 Let's cook together</h3>
              <div className="flex flex-col gap-6">
                {selectedRecipe.instructions.map((step, index) => (
                  <div key={index} className="flex gap-4 items-start">
                    <div className="bg-gradient-to-r from-indigo-500 to-purple-600 text-white w-8 h-8 rounded-full flex items-center justify-center text-sm font-semibold flex-shrink-0">
                      {index + 1}
                    </div>
                    <p className="text-gray-700 leading-relaxed">{step}</p>
                  </div>
                ))}
              </div>
            </div>

            <div className="bg-gradient-to-r from-yellow-50 to-orange-50 p-6 rounded-2xl border-l-4 border-orange-400">
              <h4 className="text-orange-700 mb-2 text-lg font-medium">💡 Chef's secret</h4>
              <p className="text-orange-800 italic">{selectedRecipe.tip}</p>
            </div>
          </div>
        </div>
      )}

      <style>
        {`
          @keyframes slideUp {
            to {
              opacity: 1;
              transform: translateY(0);
            }
          }
        `}
      </style>
    </div>
  );
}

export default App;