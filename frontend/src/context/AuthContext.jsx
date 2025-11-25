import React, { createContext, useContext, useState, useEffect } from 'react';
import { ethers } from 'ethers';

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
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  // 1. Check connection on load
  useEffect(() => {
    const savedAddress = localStorage.getItem('userAddress');
    if (savedAddress) {
      setUser({ address: savedAddress });
      setIsAuthenticated(true);
    }
  }, []);

  // 2. Login Function
  const login = async () => {
    if (!window.ethereum) {
      alert("Please install MetaMask!");
      return;
    }

    setLoading(true);
    try {
      const provider = new ethers.BrowserProvider(window.ethereum);
      const signer = await provider.getSigner();
      const address = await signer.getAddress();

      // Get Nonce
      const nonceRes = await fetch('http://127.0.0.1:8000/api/v1/user/auth/nonce', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ wallet_address: address })
      });
      const { nonce } = await nonceRes.json();

      // Sign Message
      const message = `Login to Lexi. Nonce: ${nonce}`;
      const signature = await signer.signMessage(message);

      // Verify
      const verifyRes = await fetch('http://127.0.0.1:8000/api/v1/user/auth/verify', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          wallet_address: address,
          signature: signature 
        })
      });

      if (!verifyRes.ok) throw new Error('Verification failed');

      const data = await verifyRes.json();
      
      if (data.authenticated) {
        setUser({ address: address });
        setIsAuthenticated(true);
        localStorage.setItem('userAddress', address);
      }
    } catch (error) {
      console.error("Login failed:", error);
      alert("Login failed. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  // 3. Logout Function
  const logout = () => {
    setUser(null);
    setIsAuthenticated(false);
    localStorage.removeItem('userAddress');
    // Optional: Reload page to clear any other state
    window.location.reload();
  };

  // 4. Expose functions consistently
  const value = {
    user,
    loading,
    isAuthenticated,
    login,   // Use this to connect
    logout   // Use this to disconnect
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};