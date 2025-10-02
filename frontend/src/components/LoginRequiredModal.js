import React from 'react';
import { Link } from 'react-router-dom';
import { useLanguage } from '../contexts/LanguageContext';
import { translations } from '../translations/translations';

const LoginRequiredModal = ({ isOpen, onClose }) => {
  const { language } = useLanguage();
  const t = translations[language];

  if (!isOpen) return null;

  const handleOverlayClick = (e) => {
    if (e.target === e.currentTarget) {
      onClose();
    }
  };

  return (
    <div className="modal-overlay" onClick={handleOverlayClick}>
      <div className="modal-content">
        <div className="modal-header">
          <h2 className="modal-title">
            🤖 {t.loginRequired}
          </h2>
          <button className="modal-close" onClick={onClose}>
            ×
          </button>
        </div>
        
        <div className="modal-body">
          <p className="modal-message">
            {t.loginRequiredMessage}
          </p>
        </div>
        
        <div className="modal-actions">
          <button className="btn btn-outline" onClick={onClose}>
            {t.close}
          </button>
          <Link 
            to="/login" 
            className="btn btn-primary"
            onClick={onClose}
          >
            {t.signInToAccess}
          </Link>
        </div>
      </div>
    </div>
  );
};

export default LoginRequiredModal;
