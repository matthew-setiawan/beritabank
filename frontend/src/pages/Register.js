import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useLanguage } from '../contexts/LanguageContext';
import { translations } from '../translations/translations';
import { registerUser } from '../services/authService';
import OnboardingFlow from '../components/OnboardingFlow';

const Register = () => {
  const { language } = useLanguage();
  const t = translations[language];
  const navigate = useNavigate();

  const [formData, setFormData] = useState({
    username: '',
    email: '',
    password: '',
    confirmPassword: ''
  });

  const [errors, setErrors] = useState({});
  const [isLoading, setIsLoading] = useState(false);
  const [successMessage, setSuccessMessage] = useState('');
  const [showOnboarding, setShowOnboarding] = useState(false);
  const [userDescription, setUserDescription] = useState('');

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
    
    // Clear error when user starts typing
    if (errors[name]) {
      setErrors(prev => ({
        ...prev,
        [name]: ''
      }));
    }
  };

  const validateForm = () => {
    const newErrors = {};

    // Username validation
    if (!formData.username.trim()) {
      newErrors.username = t.usernameRequired;
    }

    // Email validation
    if (!formData.email.trim()) {
      newErrors.email = t.emailRequired;
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email)) {
      newErrors.email = t.invalidEmail;
    }

    // Password validation
    if (!formData.password) {
      newErrors.password = t.passwordRequired;
    } else if (formData.password.length < 6) {
      newErrors.password = t.passwordTooShort;
    }

    // Confirm password validation
    if (!formData.confirmPassword) {
      newErrors.confirmPassword = t.confirmPasswordRequired;
    } else if (formData.password !== formData.confirmPassword) {
      newErrors.confirmPassword = t.passwordMismatch;
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!validateForm()) {
      return;
    }

    // Show onboarding flow after form validation
    setShowOnboarding(true);
  };

  const handleOnboardingComplete = (description) => {
    setUserDescription(description); // keep for persistence/UX
    setShowOnboarding(false);
    handleRegistration(description); // pass directly
  };

  const handleRegistration = async (descParam) => {
    setIsLoading(true);
    setSuccessMessage('');

    try {
      
      const response = await registerUser({
        username: formData.username.trim(),
        email: formData.email.trim(),
        password: formData.password,
        desc: descParam || userDescription // fallback to state if provided
      });

      if (response.success) {
        setSuccessMessage(t.registrationSuccess);
        
        // Store user data in localStorage (you might want to use a more secure method)
        localStorage.setItem('user', JSON.stringify({
          user_id: response.data.user_id,
          username: response.data.username,
          email: response.data.email,
          token: response.data.token
        }));

        // Redirect to home page after successful registration
        setTimeout(() => {
          navigate('/');
        }, 2000);
      }
    } catch (error) {
      console.error('Registration error:', error);
      
      // Handle specific error messages
      if (error.message.includes('Username or email already exists')) {
        if (error.message.includes('username')) {
          setErrors({ username: t.usernameExists });
        } else {
          setErrors({ email: t.emailExists });
        }
      } else {
        setErrors({ general: error.message || t.registrationError });
      }
    } finally {
      setIsLoading(false);
    }
  };

  // Show onboarding flow if triggered
  if (showOnboarding) {
    return <OnboardingFlow onComplete={handleOnboardingComplete} />;
  }

  return (
    <div className="registration-container">
      <div className="registration-card">
        <div className="registration-header">
          <h1 className="registration-title">{t.joinBeritaBank}</h1>
          <p className="registration-subtitle">{t.createAccountDesc}</p>
        </div>

        <form onSubmit={handleSubmit}>
          {/* Username Field */}
          <div className="form-group">
            <label htmlFor="username" className="form-label">
              {t.username}
            </label>
            <input
              type="text"
              id="username"
              name="username"
              value={formData.username}
              onChange={handleInputChange}
              className={`form-input ${errors.username ? 'error' : ''}`}
              placeholder="Enter your username"
              disabled={isLoading}
            />
            {errors.username && (
              <div className="error-message">
                <span>⚠️</span>
                {errors.username}
              </div>
            )}
          </div>

          {/* Email Field */}
          <div className="form-group">
            <label htmlFor="email" className="form-label">
              {t.email}
            </label>
            <input
              type="email"
              id="email"
              name="email"
              value={formData.email}
              onChange={handleInputChange}
              className={`form-input ${errors.email ? 'error' : ''}`}
              placeholder="Enter your email"
              disabled={isLoading}
            />
            {errors.email && (
              <div className="error-message">
                <span>⚠️</span>
                {errors.email}
              </div>
            )}
          </div>

          {/* Password Field */}
          <div className="form-group">
            <label htmlFor="password" className="form-label">
              {t.password}
            </label>
            <input
              type="password"
              id="password"
              name="password"
              value={formData.password}
              onChange={handleInputChange}
              className={`form-input ${errors.password ? 'error' : ''}`}
              placeholder="Enter your password"
              disabled={isLoading}
            />
            {errors.password && (
              <div className="error-message">
                <span>⚠️</span>
                {errors.password}
              </div>
            )}
          </div>

          {/* Confirm Password Field */}
          <div className="form-group">
            <label htmlFor="confirmPassword" className="form-label">
              {t.confirmPassword}
            </label>
            <input
              type="password"
              id="confirmPassword"
              name="confirmPassword"
              value={formData.confirmPassword}
              onChange={handleInputChange}
              className={`form-input ${errors.confirmPassword ? 'error' : ''}`}
              placeholder="Confirm your password"
              disabled={isLoading}
            />
            {errors.confirmPassword && (
              <div className="error-message">
                <span>⚠️</span>
                {errors.confirmPassword}
              </div>
            )}
          </div>

          {/* General Error Message */}
          {errors.general && (
            <div className="error-message">
              <span>⚠️</span>
              {errors.general}
            </div>
          )}

          {/* Success Message */}
          {successMessage && (
            <div className="success-message">
              <span>✅</span>
              {successMessage}
            </div>
          )}

          {/* Submit Button */}
          <div className="registration-actions">
            <button
              type="submit"
              className="btn btn-primary registration-btn"
              disabled={isLoading}
            >
              {isLoading ? (
                <>
                  <span className="loading-spinner"></span>
                  Creating Account...
                </>
              ) : (
                t.createAccountBtn
              )}
            </button>
          </div>
        </form>

        {/* Footer */}
        <div className="registration-footer">
          <p>
            {t.alreadyHaveAccount}{' '}
            <a href="#" onClick={(e) => {
              e.preventDefault();
              // Navigate to login page when implemented
              console.log('Navigate to login page');
            }}>
              {t.signInHere}
            </a>
          </p>
        </div>
      </div>
    </div>
  );
};

export default Register;
