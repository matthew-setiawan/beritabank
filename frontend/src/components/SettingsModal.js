import React, { useState } from 'react';
import { useLanguage } from '../contexts/LanguageContext';
import { useAuth } from '../contexts/AuthContext';
import { translations } from '../translations/translations';
import { changePassword, deleteAccount } from '../services/authService';

const SettingsModal = ({ isOpen, onClose }) => {
  const { language } = useLanguage();
  const { user, token, logout } = useAuth();
  const t = translations[language];
  
  const [activeTab, setActiveTab] = useState('profile');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  
  // Change password form
  const [passwordForm, setPasswordForm] = useState({
    currentPassword: '',
    newPassword: '',
    confirmPassword: ''
  });
  
  // Delete account form
  const [deleteForm, setDeleteForm] = useState({
    password: '',
    confirmText: ''
  });

  // Clear all form data and messages
  const clearAllData = () => {
    setPasswordForm({
      currentPassword: '',
      newPassword: '',
      confirmPassword: ''
    });
    setDeleteForm({
      password: '',
      confirmText: ''
    });
    setError('');
    setSuccess('');
  };

  // Handle tab change
  const handleTabChange = (tab) => {
    clearAllData();
    setActiveTab(tab);
  };

  // Handle modal close
  const handleClose = () => {
    clearAllData();
    onClose();
  };

  const handlePasswordChange = (e) => {
    const { name, value } = e.target;
    setPasswordForm(prev => ({
      ...prev,
      [name]: value
    }));
    setError('');
    setSuccess('');
  };

  const handleDeleteChange = (e) => {
    const { name, value } = e.target;
    setDeleteForm(prev => ({
      ...prev,
      [name]: value
    }));
    setError('');
  };

  const handlePasswordSubmit = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    setError('');
    setSuccess('');

    try {
      if (passwordForm.newPassword !== passwordForm.confirmPassword) {
        setError(t.passwordMismatch);
        return;
      }

      await changePassword({
        current_password: passwordForm.currentPassword,
        new_password: passwordForm.newPassword
      }, token);

      setSuccess(t.passwordChangedSuccess);
      setPasswordForm({
        currentPassword: '',
        newPassword: '',
        confirmPassword: ''
      });
    } catch (error) {
      console.error('Password change error:', error);
      setError(error.message || t.passwordChangeError);
    } finally {
      setIsLoading(false);
    }
  };

  const handleDeleteSubmit = async (e) => {
    e.preventDefault();
    
    if (deleteForm.confirmText !== 'DELETE') {
      setError(t.deleteConfirmationRequired);
      return;
    }

    if (!window.confirm(t.deleteAccountConfirm)) {
      return;
    }

    setIsLoading(true);
    setError('');

    try {
      await deleteAccount({
        password: deleteForm.password
      }, token);

      // Logout and redirect after successful deletion
      logout();
      window.location.href = '/';
    } catch (error) {
      console.error('Account deletion error:', error);
      setError(error.message || t.deleteAccountError);
    } finally {
      setIsLoading(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="settings-modal-overlay" onClick={handleClose}>
      <div className="settings-modal" onClick={(e) => e.stopPropagation()}>
        <div className="settings-header">
          <h2 className="settings-title">{t.settings}</h2>
          <button className="settings-close" onClick={handleClose}>
            ✕
          </button>
        </div>

        <div className="settings-content">
          <div className="settings-sidebar">
            <button 
              className={`settings-tab ${activeTab === 'profile' ? 'active' : ''}`}
              onClick={() => handleTabChange('profile')}
            >
              {t.userDetails}
            </button>
            <button 
              className={`settings-tab ${activeTab === 'password' ? 'active' : ''}`}
              onClick={() => handleTabChange('password')}
            >
              {t.changePassword}
            </button>
            <button 
              className={`settings-tab ${activeTab === 'delete' ? 'active' : ''}`}
              onClick={() => handleTabChange('delete')}
            >
              {t.deleteAccount}
            </button>
          </div>

          <div className="settings-main">
            {activeTab === 'profile' && (
              <div className="settings-section">
                <h3 className="section-title">{t.userDetails}</h3>
                <div className="user-info">
                  <div className="info-item">
                    <label className="info-label">{t.username}</label>
                    <div className="info-value">{user?.username}</div>
                  </div>
                  <div className="info-item">
                    <label className="info-label">{t.email}</label>
                    <div className="info-value">{user?.email}</div>
                  </div>
                </div>
              </div>
            )}

            {activeTab === 'password' && (
              <div className="settings-section">
                <h3 className="section-title">{t.changePassword}</h3>
                <form onSubmit={handlePasswordSubmit}>
                  <div className="form-group">
                    <label className="form-label">{t.currentPassword}</label>
                    <input
                      type="password"
                      name="currentPassword"
                      value={passwordForm.currentPassword}
                      onChange={handlePasswordChange}
                      className="form-input"
                      required
                    />
                  </div>
                  <div className="form-group">
                    <label className="form-label">{t.newPassword}</label>
                    <input
                      type="password"
                      name="newPassword"
                      value={passwordForm.newPassword}
                      onChange={handlePasswordChange}
                      className="form-input"
                      required
                    />
                    <div className="password-requirements">
                      <p>{t.passwordRequirements}</p>
                    </div>
                  </div>
                  <div className="form-group">
                    <label className="form-label">{t.confirmNewPassword}</label>
                    <input
                      type="password"
                      name="confirmPassword"
                      value={passwordForm.confirmPassword}
                      onChange={handlePasswordChange}
                      className="form-input"
                      required
                    />
                  </div>
                  <button 
                    type="submit" 
                    className="btn btn-primary"
                    disabled={isLoading}
                  >
                    {isLoading ? t.saving : t.changePassword}
                  </button>
                </form>
              </div>
            )}

            {activeTab === 'delete' && (
              <div className="settings-section">
                <h3 className="section-title danger">{t.deleteAccount}</h3>
                <div className="danger-warning">
                  <p>{t.deleteAccountWarning}</p>
                </div>
                <form onSubmit={handleDeleteSubmit}>
                  <div className="form-group">
                    <label className="form-label">{t.currentPassword}</label>
                    <input
                      type="password"
                      name="password"
                      value={deleteForm.password}
                      onChange={handleDeleteChange}
                      className="form-input"
                      required
                    />
                  </div>
                  <div className="form-group">
                    <label className="form-label">{t.typeDeleteToConfirm}</label>
                    <input
                      type="text"
                      name="confirmText"
                      value={deleteForm.confirmText}
                      onChange={handleDeleteChange}
                      className="form-input"
                      placeholder="DELETE"
                      required
                    />
                  </div>
                  <button 
                    type="submit" 
                    className="btn btn-danger"
                    disabled={isLoading}
                  >
                    {isLoading ? t.deleting : t.deleteAccount}
                  </button>
                </form>
              </div>
            )}

            {error && (
              <div className="error-message">
                <span>⚠️</span>
                {error}
              </div>
            )}

            {success && (
              <div className="success-message">
                <span>✅</span>
                {success}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default SettingsModal;
