const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000/api/v1';

class ApiService {
  async searchRecipes(searchData) {
    try {
      const response = await fetch(`${API_BASE_URL}/recipes/search`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(searchData),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      return data;
    } catch (error) {
      console.error('API Error:', error);
      throw error;
    }
  }

  async getRecipeDetails(recipeId) {
    try {
      const response = await fetch(`${API_BASE_URL}/recipes/recipe/${recipeId}`);
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error('API Error:', error);
      throw error;
    }
  }

  async getPopularRecipes(limit = 10) {
    try {
      const response = await fetch(`${API_BASE_URL}/recipes/popular?limit=${limit}`);
      return await response.json();
    } catch (error) {
      console.error('API Error:', error);
      throw error;
    }
  }
}

export default new ApiService();