import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { LanguageProvider } from './contexts/LanguageContext';
import { AuthProvider, useAuth } from './contexts/AuthContext';
import Navbar from './components/Navbar';
import Home from './pages/Home';
import News from './pages/News';
import ArticleDetail from './pages/ArticleDetail';
import BankCompare from './pages/BankCompare';
import Register from './pages/Register';
import Login from './pages/Login';
import Claudia from './pages/Claudia';
import ProfileCompletion from './components/ProfileCompletion';

const HomeOrRedirect = () => {
  const { isAuthenticated, userStatus, statusLoading } = useAuth();
  
  if (!isAuthenticated) {
    return <Home />;
  }
  
  if (statusLoading) {
    return <div className="loading-container"><div className="loading-spinner"></div><p>Loading...</p></div>;
  }
  
  if (userStatus && !userStatus.all_requirements_met) {
    return <ProfileCompletion />;
  }
  
  return <Claudia />;
};

const ProtectedClaudia = () => {
  const { isAuthenticated, userStatus, statusLoading } = useAuth();
  
  if (!isAuthenticated) {
    return <Home />;
  }
  
  if (statusLoading) {
    return <div className="loading-container"><div className="loading-spinner"></div><p>Loading...</p></div>;
  }
  
  if (userStatus && !userStatus.all_requirements_met) {
    return <ProfileCompletion />;
  }
  
  return <Claudia />;
};

function App() {
  return (
    <AuthProvider>
      <LanguageProvider>
        <Router>
          <div className="App">
            <Navbar />
            <main className="main-content">
              <Routes>
                <Route path="/" element={<HomeOrRedirect />} />
                <Route path="/news" element={<News />} />
                <Route path="/news/:id" element={<ArticleDetail />} />
                <Route path="/bank-compare" element={<BankCompare />} />
                <Route path="/register" element={<Register />} />
                <Route path="/login" element={<Login />} />
                <Route path="/claudia" element={<ProtectedClaudia />} />
              </Routes>
            </main>
          </div>
        </Router>
      </LanguageProvider>
    </AuthProvider>
  );
}

export default App;
