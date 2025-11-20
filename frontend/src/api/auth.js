import axios from 'axios';

const API_BASE = 'http://localhost:8000/api/v1';

const api = axios.create({
  baseURL: API_BASE,
  timeout: 10000,
});

export const authAPI = {
  getNonce: async (walletAddress) => {
    try {
      const response = await api.post('/user/auth/nonce', null, {
        params: { wallet_address: walletAddress }
      });
      return response.data;
    } catch (error) {
      console.error('Error getting nonce:', error);
      throw error;
    }
  },

  verifySignature: async (walletAddress, signature, message) => {
    try {
      const response = await api.post('/user/auth/verify', null, {
        params: {
          wallet_address: walletAddress,
          signature: signature,
          message: message
        }
      });
      return response.data;
    } catch (error) {
      console.error('Error verifying signature:', error);
      throw error;
    }
  }
};