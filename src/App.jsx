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

  const handleSearch = async (e) => {
    e.preventDefault();
    if (!ingredients.trim()) return;
    
    setIsLoading(true);
    
    // Simulate API call
    setTimeout(() => {
      const mockRecipes = [
        {
          id: 1,
          name: "Golden Sunset Pasta",
          description: "A warm embrace in a bowl with creamy sauce and tender vegetables",
          cookTime: "25 min",
          difficulty: "Easy",
          rating: 4.8,
          image: "🍝",
          ingredients: [
            { name: "Pasta", amount: "200g" },
            { name: "Heavy cream", amount: "150ml" },
            { name: "Cherry tomatoes", amount: "150g" },
            { name: "Fresh basil", amount: "10 leaves" },
            { name: "Garlic", amount: "2 cloves" },
            { name: "Parmesan cheese", amount: "50g" }
          ],
          instructions: [
            "Bring a large pot of salted water to a gentle boil. Add pasta and cook until al dente.",
            "While pasta dances in the water, heat olive oil in a large pan over medium heat.",
            "Add minced garlic and let it release its wonderful aroma for about 30 seconds.",
            "Toss in halved cherry tomatoes and cook until they start to burst with flavor.",
            "Pour in the cream and let it simmer gently, creating a silky sauce.",
            "Drain pasta, reserving a cup of that precious pasta water.",
            "Combine pasta with the creamy sauce, adding pasta water if needed for perfect consistency.",
            "Finish with fresh basil leaves and a generous sprinkle of Parmesan."
          ],
          tip: "Save some pasta water before draining - it's the secret to a silky smooth sauce that hugs every strand! ✨"
        },
        {
          id: 2,
          name: "Cozy Chicken Comfort Bowl",
          description: "Tender chicken with fluffy rice and a sprinkle of love",
          cookTime: "30 min",
          difficulty: "Simple",
          rating: 4.9,
          image: "🍗",
          ingredients: [
            { name: "Chicken breast", amount: "300g" },
            { name: "Jasmine rice", amount: "150g" },
            { name: "Mixed vegetables", amount: "200g" },
            { name: "Soy sauce", amount: "3 tbsp" },
            { name: "Sesame oil", amount: "1 tbsp" },
            { name: "Fresh ginger", amount: "1 inch" }
          ],
          instructions: [
            "Start by giving your rice a gentle rinse until the water runs clear.",
            "Cook rice with love - 1 cup rice to 1.5 cups water, bring to a boil then simmer for 15 minutes.",
            "Season chicken with salt and pepper, then cook in a hot pan for 6-7 minutes each side.",
            "Let the chicken rest for 5 minutes (patience makes it juicier!), then slice.",
            "In the same pan, stir-fry your vegetables until they're tender-crisp.",
            "Drizzle with soy sauce and sesame oil, toss everything together.",
            "Serve over fluffy rice and enjoy this bowl of comfort."
          ],
          tip: "Let your chicken rest after cooking - this simple step keeps all those delicious juices locked in! 🥢"
        },
        {
          id: 3,
          name: "Garden Fresh Veggie Delight",
          description: "A colorful celebration of fresh vegetables in perfect harmony",
          cookTime: "20 min",
          difficulty: "Effortless",
          rating: 4.7,
          image: "🥗",
          ingredients: [
            { name: "Mixed greens", amount: "200g" },
            { name: "Bell peppers", amount: "2 pieces" },
            { name: "Cucumber", amount: "1 large" },
            { name: "Cherry tomatoes", amount: "150g" },
            { name: "Avocado", amount: "1 ripe" },
            { name: "Olive oil", amount: "3 tbsp" },
            { name: "Lemon juice", amount: "2 tbsp" }
          ],
          instructions: [
            "Wash all your beautiful vegetables with care - they're the stars of this dish.",
            "Slice the bell peppers into colorful strips that catch the light.",
            "Dice the cucumber into perfect little cubes, keeping some skin for texture.",
            "Halve the cherry tomatoes to release their sweet juices.",
            "Gently slice the avocado just before serving to keep it bright and fresh.",
            "Whisk together olive oil and lemon juice with a pinch of salt.",
            "Toss everything together and serve immediately while the colors are vibrant."
          ],
          tip: "Add the avocado at the very end to keep it perfectly green and creamy! 🥑"
        }
      ];
      
      setRecipes(mockRecipes);
      setIsLoading(false);
      setCurrentView('results');
    }, 1500);
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

      {/* Loading View */}
      {isLoading && (
        <div className="min-h-screen flex items-center justify-center text-center">
          <div className="bg-white p-12 rounded-2xl shadow-xl">
            <div className="text-6xl mb-4 animate-bounce">👨‍🍳</div>
            <h2 className="text-2xl text-gray-700 mb-2">Searching for your perfect match...</h2>
            <p className="text-gray-600 mb-8">Looking through thousands of delicious possibilities</p>
            <div className="flex justify-center gap-2">
              {[0, 1, 2].map(i => (
                <div
                  key={i}
                  className="w-3 h-3 bg-indigo-500 rounded-full animate-pulse"
                  style={{ animationDelay: `${i * 0.2}s` }}
                />
              ))}
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

      <style jsx>{`
        @keyframes slideUp {
          to {
            opacity: 1;
            transform: translateY(0);
          }
        }
      `}</style>
    </div>
  );
}

export default App;