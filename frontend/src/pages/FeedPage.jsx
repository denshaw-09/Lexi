import React, { useState, useEffect } from 'react';
import ArticleCard from '../components/ArticleCard';
import { feedAPI } from '../api/feed';

const FeedPage = () => {
  const [articles, setArticles] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedEcosystem, setSelectedEcosystem] = useState('');
  const [searchQuery, setSearchQuery] = useState('');

  const ecosystems = [
    { value: '', label: 'All Networks' },
    { value: 'ethereum', label: 'Ethereum' },
    { value: 'base', label: 'Base' },
    { value: 'solana', label: 'Solana' },
    { value: 'farcaster', label: 'Farcaster' },
    { value: 'web3', label: 'Web3' },
    { value: 'defi', label: 'DeFi' },
    { value: 'research', label: 'Research' }
  ];

  // Test data
  const testArticles = [
    {
      id: '1',
      title: 'Ethereum Protocol Updates and Roadmap',
      summary: 'Latest developments in Ethereum protocol including upcoming upgrades and improvements for scalability.',
      source: 'ethereum',
      ecosystem_tag: 'ethereum',
      legitimacy_score: 0.95,
      url: 'https://ethereum.org',
      created_at: new Date().toISOString()
    },
    {
      id: '2',
      title: 'Base Ecosystem Growth Analysis',
      summary: 'Comprehensive report on Base network growth, developer adoption, and ecosystem expansion.',
      source: 'base',
      ecosystem_tag: 'base',
      legitimacy_score: 0.88,
      url: 'https://base.org',
      created_at: new Date().toISOString()
    },
    {
      id: '3',
      title: 'Farcaster Social Protocol Updates',
      summary: 'Recent improvements to Farcaster protocol and new features for decentralized social networking.',
      source: 'farcaster',
      ecosystem_tag: 'farcaster',
      legitimacy_score: 0.92,
      url: 'https://farcaster.xyz',
      created_at: new Date().toISOString()
    },
    {
      id: '4',
      title: 'Web3 Development Best Practices',
      summary: 'Essential guidelines and best practices for building secure and scalable Web3 applications.',
      source: 'web3',
      ecosystem_tag: 'web3',
      legitimacy_score: 0.85,
      url: 'https://web3.dev',
      created_at: new Date().toISOString()
    }
  ];

  const loadArticles = async () => {
    setLoading(true);
    try {
      let data;
      if (searchQuery) {
        data = await feedAPI.searchArticles(searchQuery);
      } else {
        data = await feedAPI.getFeed(selectedEcosystem);
      }
      setArticles(data && data.length > 0 ? data : testArticles);
    } catch (error) {
      console.error('Error loading articles:', error);
      setArticles(testArticles);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadArticles();
  }, [selectedEcosystem]);

  const handleSearch = (e) => {
    e.preventDefault();
    loadArticles();
  };

  return (
    <div style={{ minHeight: '100vh', background: '#f8fafc', paddingTop: '80px' }}>
      <div className="container">
        {/* Header */}
        <div className="text-center" style={{ marginBottom: '3rem' }}>
          <h1 style={{ fontSize: '2.5rem', fontWeight: '700', color: '#1e293b', marginBottom: '1rem' }}>
            Web3 Intelligence <span style={{ background: 'linear-gradient(135deg, #14b8a6, #0d9488)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>Feed</span>
          </h1>
          <p style={{ fontSize: '1.125rem', color: '#64748b', maxWidth: '600px', margin: '0 auto' }}>
            Curated updates from Ethereum, Base, Farcaster, and the broader Web3 ecosystem.
          </p>
        </div>

        {/* Filters and Search */}
        <div style={{
          background: 'white',
          borderRadius: '12px',
          border: '1px solid #e2e8f0',
          padding: '1.5rem',
          marginBottom: '2rem'
        }}>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr', gap: '1.5rem' }}>
            {/* Ecosystem Filter */}
            <div>
              <label style={{ display: 'block', fontSize: '14px', fontWeight: '500', color: '#374151', marginBottom: '12px' }}>
                Filter by Network
              </label>
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
                {ecosystems.map(eco => (
                  <button
                    key={eco.value}
                    onClick={() => setSelectedEcosystem(eco.value)}
                    style={{
                      padding: '8px 16px',
                      borderRadius: '8px',
                      fontSize: '14px',
                      fontWeight: '500',
                      border: 'none',
                      cursor: 'pointer',
                      transition: 'all 0.2s ease',
                      ...(selectedEcosystem === eco.value ? {
                        background: '#f0fdfa',
                        color: '#14b8a6',
                        border: '1px solid #a7f3d0'
                      } : {
                        background: '#f8fafc',
                        color: '#64748b',
                        border: '1px solid transparent'
                      })
                    }}
                  >
                    {eco.label}
                  </button>
                ))}
              </div>
            </div>

            {/* Search */}
            <div>
              <label style={{ display: 'block', fontSize: '14px', fontWeight: '500', color: '#374151', marginBottom: '12px' }}>
                Search Articles
              </label>
              <form onSubmit={handleSearch} style={{ display: 'flex', gap: '8px' }}>
                <div style={{ position: 'relative', flex: 1 }}>
                  <input
                    type="text"
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    placeholder="Search articles..."
                    style={{
                      width: '100%',
                      padding: '8px 16px 8px 40px',
                      border: '1px solid #d1d5db',
                      borderRadius: '8px',
                      fontSize: '14px'
                    }}
                  />
                  <svg 
                    style={{
                      position: 'absolute',
                      left: '12px',
                      top: '50%',
                      transform: 'translateY(-50%)',
                      width: '16px',
                      height: '16px',
                      color: '#9ca3af'
                    }}
                    fill="none" 
                    stroke="currentColor" 
                    viewBox="0 0 24 24"
                  >
                    <path strokeWidth="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                  </svg>
                </div>
                <button
                  type="submit"
                  style={{
                    padding: '8px 20px',
                    background: '#14b8a6',
                    color: 'white',
                    border: 'none',
                    borderRadius: '8px',
                    fontSize: '14px',
                    fontWeight: '500',
                    cursor: 'pointer'
                  }}
                >
                  Search
                </button>
              </form>
            </div>
          </div>
        </div>

        {/* Articles Grid - 4 cards per row */}
        {loading ? (
          <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', padding: '3rem' }}>
            <div style={{
              width: '32px',
              height: '32px',
              border: '3px solid #f3f4f6',
              borderTop: '3px solid #14b8a6',
              borderRadius: '50%',
              animation: 'spin 1s linear infinite'
            }}></div>
          </div>
        ) : (
          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))',
            gap: '1.5rem'
          }}>
            {articles.map(article => (
              <ArticleCard key={article.id} article={article} />
            ))}
          </div>
        )}
      </div>

      <style>{`
        @keyframes spin {
          0% { transform: rotate(0deg); }
          100% { transform: rotate(360deg); }
        }
      `}</style>
    </div>
  );
};

export default FeedPage;