import React, { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { feedAPI } from '../api/feed';

const ArticleCard = ({ article }) => {
  const { user, isAuthenticated } = useAuth();
  const [isSaved, setIsSaved] = useState(false);

  const handleSave = async () => {
    if (!isAuthenticated) return;
    try {
      if (!isSaved) {
        await feedAPI.saveBookmark(user.address, article.id);
      }
      setIsSaved(!isSaved);
    } catch (error) {
      console.error('Error saving bookmark:', error);
    }
  };

  const getEcosystemColor = (ecosystem) => {
    const colors = {
      ethereum: { bg: '#ede9fe', text: '#7c3aed' },
      base: { bg: '#dbeafe', text: '#1d4ed8' },
      solana: { bg: '#dcfce7', text: '#16a34a' },
      farcaster: { bg: '#e0e7ff', text: '#4f46e5' },
      web3: { bg: '#ccfbf1', text: '#0d9488' },
      defi: { bg: '#fef3c7', text: '#d97706' },
      research: { bg: '#cffafe', text: '#0891b2' }
    };
    return colors[ecosystem] || { bg: '#f1f5f9', text: '#475569' };
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    });
  };

  const ecosystemColor = getEcosystemColor(article.ecosystem_tag);

  return (
    <div style={{
      background: 'white',
      borderRadius: '12px',
      border: '1px solid #e2e8f0',
      overflow: 'hidden',
      transition: 'all 0.2s ease'
    }}>
      {/* Article Image */}
      <div style={{
        height: '160px',
        background: `linear-gradient(135deg, ${ecosystemColor.bg}, ${ecosystemColor.bg}00)`,
        position: 'relative',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center'
      }}>
        <div style={{
          position: 'absolute',
          top: '12px',
          left: '12px',
          background: ecosystemColor.bg,
          color: ecosystemColor.text,
          padding: '4px 12px',
          borderRadius: '20px',
          fontSize: '12px',
          fontWeight: '600'
        }}>
          {article.ecosystem_tag?.toUpperCase() || 'WEB3'}
        </div>
        <div style={{
          position: 'absolute',
          top: '12px',
          right: '12px',
          background: 'rgba(255, 255, 255, 0.9)',
          color: article.legitimacy_score >= 0.8 ? '#16a34a' : article.legitimacy_score >= 0.6 ? '#d97706' : '#dc2626',
          padding: '4px 8px',
          borderRadius: '6px',
          fontSize: '12px',
          fontWeight: '600'
        }}>
          {Math.round(article.legitimacy_score * 100)}% Trust
        </div>
        <div style={{
          fontSize: '32px',
          color: ecosystemColor.text,
          opacity: 0.3
        }}>
          {article.source?.charAt(0).toUpperCase()}
        </div>
      </div>
      
      {/* Article Content */}
      <div style={{ padding: '1.5rem' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '12px' }}>
          <div style={{ flex: 1, paddingRight: '12px' }}>
            <h3 style={{
              fontSize: '18px',
              fontWeight: '600',
              color: '#1e293b',
              marginBottom: '8px',
              lineHeight: '1.4',
              display: '-webkit-box',
              WebkitLineClamp: 2,
              WebkitBoxOrient: 'vertical',
              overflow: 'hidden'
            }}>
              <a 
                href={article.url} 
                target="_blank" 
                rel="noopener noreferrer"
                style={{ color: 'inherit', textDecoration: 'none' }}
              >
                {article.title}
              </a>
            </h3>
            
            {article.summary && (
              <p style={{
                color: '#64748b',
                fontSize: '14px',
                lineHeight: '1.5',
                marginBottom: '12px',
                display: '-webkit-box',
                WebkitLineClamp: 3,
                WebkitBoxOrient: 'vertical',
                overflow: 'hidden'
              }}>
                {article.summary}
              </p>
            )}
          </div>
          
          {isAuthenticated && (
            <button
              onClick={handleSave}
              style={{
                background: 'none',
                border: 'none',
                color: isSaved ? '#14b8a6' : '#94a3b8',
                cursor: 'pointer',
                padding: '4px'
              }}
              title={isSaved ? 'Saved' : 'Save article'}
            >
              <svg width="20" height="20" viewBox="0 0 24 24" fill={isSaved ? "currentColor" : "none"} stroke="currentColor">
                <path strokeWidth="2" d="M5 5a2 2 0 012-2h10a2 2 0 012 2v16l-7-3.5L5 21V5z" />
              </svg>
            </button>
          )}
        </div>

        {/* Article Meta */}
        <div style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          fontSize: '14px',
          color: '#64748b'
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
            <span style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                <path strokeWidth="2" d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1" />
              </svg>
              <span style={{ textTransform: 'capitalize' }}>{article.source}</span>
            </span>
            <span style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                <path strokeWidth="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
              </svg>
              <span>{formatDate(article.created_at)}</span>
            </span>
          </div>
          
          <a 
            href={article.url} 
            target="_blank" 
            rel="noopener noreferrer"
            style={{
              color: '#14b8a6',
              fontWeight: '500',
              textDecoration: 'none',
              display: 'flex',
              alignItems: 'center',
              gap: '4px'
            }}
          >
            <span>Read</span>
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <path strokeWidth="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
            </svg>
          </a>
        </div>

        {!isAuthenticated && (
          <div style={{
            marginTop: '12px',
            padding: '8px 12px',
            background: '#f0fdfa',
            border: '1px solid #a7f3d0',
            borderRadius: '6px',
            textAlign: 'center'
          }}>
            <p style={{ color: '#0d9488', fontSize: '12px', margin: 0 }}>
              Connect wallet to save articles
            </p>
          </div>
        )}
      </div>
    </div>
  );
};

export default ArticleCard;