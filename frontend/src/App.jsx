import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import FeedPage from './pages/FeedPage';
import ProfilePage from './pages/ProfilePage';
import Navbar from './components/Navbar';
import './index.css';

function App() {
  return (
    <Router>
      <AuthProvider>
        <div style={{ minHeight: '100vh' }}>
          <Navbar />
          <Routes>
            <Route path="/" element={<FeedPage />} />
            <Route path="/profile" element={<ProfilePage />} />
          </Routes>
        </div>
      </AuthProvider>
    </Router>
  );
}

export default App;