import axios from 'axios';

const API_BASE = 'http://localhost:8000/api/v1';

// Create axios instance with better error handling
const api = axios.create({
  baseURL: API_BASE,
  timeout: 10000,
});

// Add response interceptor for better error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('API Error:', error.response?.data || error.message);
    return Promise.reject(error);
  }
);

export const feedAPI = {
  getFeed: async (ecosystem = null, limit = 20) => {
    try {
      const params = { limit };
      if (ecosystem) params.ecosystem = ecosystem;
      
      const response = await api.get('/feed/', { params });
      return response.data;
    } catch (error) {
      console.error('Error fetching feed:', error);
      throw error;
    }
  },

  searchArticles: async (query) => {
    try {
      const response = await api.get('/feed/search', {
        params: { q: query }
      });
      return response.data;
    } catch (error) {
      console.error('Error searching articles:', error);
      throw error;
    }
  },

  saveBookmark: async (userAddress, articleId) => {
    try {
      const response = await api.post('/user/bookmarks', {
        user_address: userAddress,
        article_id: articleId
      });
      return response.data;
    } catch (error) {
      console.error('Error saving bookmark:', error);
      throw error;
    }
  },

  getBookmarks: async (userAddress) => {
    try {
      const response = await api.get(`/user/${userAddress}/bookmarks`);
      return response.data;
    } catch (error) {
      console.error('Error fetching bookmarks:', error);
      throw error;
    }
  },

  deleteBookmark: async (bookmarkId, userAddress) => {
    try {
      await api.delete(`/user/bookmarks/${bookmarkId}`, {
        params: { wallet_address: userAddress }
      });
    } catch (error) {
      console.error('Error deleting bookmark:', error);
      throw error;
    }
  }
};