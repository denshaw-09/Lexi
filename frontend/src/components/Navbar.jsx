import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

const Navbar = () => {
  const { user, connectWallet, disconnect, isAuthenticated } = useAuth();
  const location = useLocation();

  return (
    <nav style={{
      position: 'fixed',
      top: 0,
      left: 0,
      right: 0,
      background: 'white',
      borderBottom: '1px solid #e2e8f0',
      padding: '1rem 0',
      zIndex: 1000
    }}>
      <div className="container">
        <div className="flex justify-between items-center">
          {/* Logo */}
          <Link to="/" className="flex items-center gap-3" style={{ textDecoration: 'none', color: 'inherit' }}>
            {/* <div style={{
              width: '32px',
              height: '32px',
              background: 'linear-gradient(135deg, #14b8a6, #0d9488)',
              borderRadius: '8px',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              color: 'white',
              fontWeight: '600',
              fontSize: '14px'
            }}>
              
            </div> */}
            <span style={{ fontSize: '20px', fontWeight: '700', color: '#1e293b' }}>
              Lexi
            </span>
          </Link>

          {/* Navigation Links */}
          <div style={{ display: 'flex', gap: '2rem', alignItems: 'center' }}>
            <Link 
              to="/" 
              style={{
                textDecoration: 'none',
                color: location.pathname === '/' ? '#14b8a6' : '#64748b',
                fontWeight: location.pathname === '/' ? '600' : '400',
                padding: '0.5rem 1rem',
                borderRadius: '8px',
                backgroundColor: location.pathname === '/' ? '#f0fdfa' : 'transparent'
              }}
            >
              Feed
            </Link>
            <Link 
              to="/profile" 
              style={{
                textDecoration: 'none',
                color: location.pathname === '/profile' ? '#14b8a6' : '#64748b',
                fontWeight: location.pathname === '/profile' ? '600' : '400',
                padding: '0.5rem 1rem',
                borderRadius: '8px',
                backgroundColor: location.pathname === '/profile' ? '#f0fdfa' : 'transparent'
              }}
            >
              Profile
            </Link>
          </div>

          {/* Wallet Connection */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
            {!isAuthenticated ? (
              <button
                onClick={connectWallet}
                style={{
                  background: 'linear-gradient(135deg, #14b8a6, #0d9488)',
                  color: 'white',
                  border: 'none',
                  padding: '0.5rem 1.5rem',
                  borderRadius: '8px',
                  fontWeight: '500',
                  fontSize: '14px',
                  cursor: 'pointer'
                }}
              >
                Connect Wallet
              </button>
            ) : (
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                <div style={{
                  background: '#f1f5f9',
                  color: '#475569',
                  padding: '0.25rem 0.75rem',
                  borderRadius: '20px',
                  fontSize: '14px',
                  fontFamily: 'monospace'
                }}>
                  {user?.address.slice(0, 6)}...{user?.address.slice(-4)}
                </div>
                <button
                  onClick={disconnect}
                  style={{
                    color: '#64748b',
                    background: 'none',
                    border: 'none',
                    fontSize: '14px',
                    cursor: 'pointer'
                  }}
                >
                  Disconnect
                </button>
              </div>
            )}
          </div>
        </div>
      </div>
    </nav>
  );
};

export default Navbar;