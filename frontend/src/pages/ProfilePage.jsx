import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { feedAPI } from '../api/feed';
import ArticleCard from '../components/ArticleCard';

const ProfilePage = () => {
  const { user, login } = useAuth();
  const [bookmarks, setBookmarks] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (user) {
      loadBookmarks();
    } else {
      setLoading(false);
    }
  }, [user]);

  const loadBookmarks = async () => {
    setLoading(true);
    try {
      const data = await feedAPI.getBookmarks(user.address);

      // check: ensure data is an arr b4 mapping
      const safeData = Array.isArray(data) ? data : [];

      // handle supabase join structure (if article is nested) or flat structure
      const processedBookmarks = safeData.map(item => item.articles ? item.articles : item);

      setBookmarks(data.map(item => item.articles || item));
    } catch (error) {
      console.error('Error loading bookmarks:', error);
      setBookmarks([]);
    } finally {
      setLoading(false);
    }
  };

  if (!user) {
    return (
      <div className="min-h-screen flex items-center justify-center py-8">
        <div className="max-w-md w-full bg-white rounded-2xl shadow-sm border border-slate-200 p-8 text-center">
          <div className="w-16 h-16 mx-auto mb-4 bg-slate-100 rounded-full flex items-center justify-center">
            <svg className="w-8 h-8 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
            </svg>
          </div>
          <h2 className="text-xl font-semibold text-slate-900 mb-2">Authentication Required</h2>
          <p className="text-slate-600 mb-6">Please connect your wallet to access your profile</p>
          <button onClick={login} className="w-full py-2 px-4 bg-teal-600 hover:bg-teal-700 text-white rounded-lg font-medium transition-colors" >
            Connect Wallet
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Profile Header */}
        <div className="bg-white rounded-2xl shadow-sm border border-slate-200 p-8 mb-8">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-slate-900 mb-2">Your Profile</h1>
              <p className="text-slate-600">Manage your saved articles and preferences</p>
            </div>
            <div className="text-right">
              <div className="text-sm text-slate-500 mb-1">Wallet Address</div>
              <div className="font-mono text-slate-900 bg-slate-100 px-3 py-2 rounded-lg">
                {user.address}
              </div>
            </div>
          </div>

          {/* Stats */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mt-8">
            <div className="bg-mint-50 rounded-xl p-6 border border-mint-200">
              <div className="text-2xl font-bold text-mint-600 mb-1">{bookmarks.length}</div>
              <div className="text-sm text-mint-700">Saved Articles</div>
            </div>
            <div className="bg-slate-50 rounded-xl p-6 border border-slate-200">
              <div className="text-2xl font-bold text-slate-600 mb-1">
                {new Set(bookmarks.map(b => b.ecosystem_tag)).size}
              </div>
              <div className="text-sm text-slate-700">Networks Followed</div>
            </div>
            <div className="bg-slate-50 rounded-xl p-6 border border-slate-200">
              <div className="text-2xl font-bold text-slate-600 mb-1">
                {bookmarks.filter(b => b.legitimacy_score >= 0.8).length}
              </div>
              <div className="text-sm text-slate-700">High Trust Articles</div>
            </div>
          </div>
        </div>

        {/* Saved Articles */}
        <div className="bg-white rounded-2xl shadow-sm border border-slate-200 p-8">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-2xl font-bold text-slate-900">Saved Articles</h2>
            <span className="bg-mint-100 text-mint-700 px-3 py-1 rounded-full text-sm font-medium">
              {bookmarks.length} items
            </span>
          </div>

          {loading ? (
            <div className="flex justify-center items-center py-12">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-mint-500"></div>
            </div>
          ) : bookmarks.length === 0 ? (
            <div className="text-center py-12">
              <div className="w-24 h-24 mx-auto mb-4 bg-slate-100 rounded-full flex items-center justify-center">
                <svg className="w-10 h-10 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 5a2 2 0 012-2h10a2 2 0 012 2v16l-7-3.5L5 21V5z" />
                </svg>
              </div>
              <h3 className="text-lg font-medium text-slate-900 mb-2">No saved articles yet</h3>
              <p className="text-slate-600 mb-6">Start saving articles from the feed to build your knowledge base</p>
              <a 
                href="/" 
                className="inline-flex items-center px-4 py-2 bg-mint-500 text-white rounded-lg hover:bg-mint-600 transition-colors font-medium"
              >
                Browse Articles
              </a>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {bookmarks.map(article => (
                <ArticleCard key={article.id} article={article} />
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default ProfilePage;