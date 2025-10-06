import React, { useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { useLanguage } from '../contexts/LanguageContext';
import { useAuth } from '../contexts/AuthContext';
import { translations } from '../translations/translations';
import LoginRequiredModal from './LoginRequiredModal';
import SettingsModal from './SettingsModal';
import logo from '../beritabanklogo.png';

const Navbar = () => {
  const { language, setLanguage } = useLanguage();
  const { isAuthenticated, logout } = useAuth();
  const t = translations[language];
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [isSettingsOpen, setIsSettingsOpen] = useState(false);
  const location = useLocation();

  const handleAIAssistantClick = (e) => {
    if (!isAuthenticated) {
      e.preventDefault();
      setIsModalOpen(true);
    }
  };

  const closeModal = () => {
    setIsModalOpen(false);
  };

  const openSettings = () => {
    setIsSettingsOpen(true);
  };

  const closeSettings = () => {
    setIsSettingsOpen(false);
  };

  const handleLanguageChange = (newLanguage) => {
    if (newLanguage !== language) {
      setLanguage(newLanguage);
      // If we're on the Claudia AI page, refresh to regenerate content with new language
      if (location.pathname === '/claudia') {
        window.location.reload();
      }
    }
  };

  return (
    <nav className="navbar">
      <div className="container">
        <div className="navbar-content">
          {/* Logo */}
          <Link to="/" className="navbar-brand">
            <img src={logo} alt="Berita Bank" className="navbar-logo" />
          </Link>
          
          {/* Navigation Menu */}
          <ul className="navbar-nav">
            <li>
              <Link to="/news">{t.news}</Link>
            </li>
            <li>
              <Link to="/bank-compare">{t.bankCompare}</Link>
            </li>
            <li>
              <Link to="/claudia" onClick={handleAIAssistantClick}>{t.aiAssistant}</Link>
            </li>
          </ul>
          
          {/* Login/Signup Buttons and Language Toggle */}
          <div className="navbar-actions">
            {isAuthenticated ? (
              <>
                <button className="btn btn-outline settings-btn" onClick={openSettings}>
                  ⚙️ {t.settings}
                </button>
                <button className="btn btn-outline" onClick={logout}>Logout</button>
              </>
            ) : (
              <>
                <Link to="/login" className="btn btn-outline">{t.login}</Link>
                <Link to="/register" className="btn btn-primary">{t.signUp}</Link>
              </>
            )}
            <div className="language-toggle-pill">
              <button 
                className={`language-option ${language === 'id' ? 'active' : ''}`}
                onClick={() => handleLanguageChange('id')}
              >
                ID
              </button>
              <div className="language-divider"></div>
              <button 
                className={`language-option ${language === 'en' ? 'active' : ''}`}
                onClick={() => handleLanguageChange('en')}
              >
                EN
              </button>
            </div>
          </div>
        </div>
      </div>
      
      {/* Login Required Modal */}
      <LoginRequiredModal 
        isOpen={isModalOpen} 
        onClose={closeModal} 
      />
      
      {/* Settings Modal */}
      <SettingsModal 
        isOpen={isSettingsOpen} 
        onClose={closeSettings} 
      />
    </nav>
  );
};

export default Navbar;
