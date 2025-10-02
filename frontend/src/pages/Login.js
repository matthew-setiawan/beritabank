import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useLanguage } from '../contexts/LanguageContext';
import { translations } from '../translations/translations';
import { loginUser } from '../services/authService';
import { useAuth } from '../contexts/AuthContext';

const Login = () => {
  const { language } = useLanguage();
  const t = translations[language];
  const navigate = useNavigate();
  const { login } = useAuth();

  const [formData, setFormData] = useState({
    username: '',
    password: ''
  });
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
    setError('');
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!formData.username || !formData.password) {
      setError(t.registrationError);
      return;
    }
    setIsLoading(true);
    try {
      const res = await loginUser({ username: formData.username, password: formData.password });
      if (res.success) {
        login(res.data);
        navigate('/claudia');
      } else {
        setError(res.error || t.registrationError);
      }
    } catch (err) {
      setError(err.message || t.registrationError);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="registration-container">
      <div className="registration-card">
        <div className="registration-header">
          <h1 className="registration-title">{t.login}</h1>
          <p className="registration-subtitle">Claudia AI access requires login</p>
        </div>

        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label htmlFor="username" className="form-label">Username / Email</label>
            <input
              id="username"
              name="username"
              type="text"
              className="form-input"
              value={formData.username}
              onChange={handleChange}
              placeholder="yourname or you@example.com"
              disabled={isLoading}
            />
          </div>

          <div className="form-group">
            <label htmlFor="password" className="form-label">{t.password}</label>
            <input
              id="password"
              name="password"
              type="password"
              className="form-input"
              value={formData.password}
              onChange={handleChange}
              placeholder="••••••••"
              disabled={isLoading}
            />
          </div>

          {error && (
            <div className="error-message">
              <span>⚠️</span>
              {error}
            </div>
          )}

          <div className="registration-actions">
            <button type="submit" className="btn btn-primary registration-btn" disabled={isLoading}>
              {isLoading ? 'Signing in...' : t.login}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default Login;


