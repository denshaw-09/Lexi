import React, { createContext, useContext, useState, useEffect } from 'react';
import { authAPI } from '../api/auth';

const AuthContext = createContext();

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(false);

  const connectWallet = async () => {
    if (window.ethereum) {
      try {
        setLoading(true);
        const accounts = await window.ethereum.request({ 
          method: 'eth_requestAccounts' 
        });
        const address = accounts[0];
        
        // Get nonce from backend
        const nonceData = await authAPI.getNonce(address);
        
        // Sign message
        const signature = await window.ethereum.request({
          method: 'personal_sign',
          params: [nonceData.message, address],
        });
        
        // Verify signature with backend
        const userData = await authAPI.verifySignature(address, signature, nonceData.message);
        setUser({ address });
        
        localStorage.setItem('userAddress', address);
      } catch (error) {
        console.error('Wallet connection failed:', error);
      } finally {
        setLoading(false);
      }
    } else {
      alert('Please install MetaMask!');
    }
  };

  const disconnect = () => {
    setUser(null);
    localStorage.removeItem('userAddress');
  };

  useEffect(() => {
    const savedAddress = localStorage.getItem('userAddress');
    if (savedAddress) {
      setUser({ address: savedAddress });
    }
  }, []);

  const value = {
    user,
    loading,
    connectWallet,
    disconnect,
    isAuthenticated: !!user
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};