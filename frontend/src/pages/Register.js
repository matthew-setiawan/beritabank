import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useLanguage } from '../contexts/LanguageContext';
import { useAuth } from '../contexts/AuthContext';
import { translations } from '../translations/translations';
import { registerUser, loginUser, createUserDescription } from '../services/authService';
import { API_BASE_URL } from '../config/api';
import OnboardingFlow from '../components/OnboardingFlow';
import EmailVerification from '../components/EmailVerification';

const Register = () => {
  const { language } = useLanguage();
  const { login } = useAuth();
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
  const [showEmailVerification, setShowEmailVerification] = useState(false);
  const [userDescription, setUserDescription] = useState('');
  const [isTransitioning, setIsTransitioning] = useState(false);

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

    // Register user first
    await handleRegistration();
  };

  const handleOnboardingComplete = async (description) => {
    setUserDescription(description);
    setShowOnboarding(false);
    
    // Use the new create_desc endpoint and then login
    await handleCreateDescriptionAndLogin(description);
  };

  const handleCreateDescriptionAndLogin = async (description) => {
    setIsLoading(true);
    setSuccessMessage('');

    try {
      // Get the token from registration response
      const registrationToken = localStorage.getItem('registration_token');
      
      if (!registrationToken) {
        throw new Error('No registration token found');
      }

      // Create the description using the registration token
      await createUserDescription(description, registrationToken);

      // Use AuthContext login function to properly update authentication state
      login({
        user_id: localStorage.getItem('user_id'),
        username: formData.username,
        email: formData.email,
        token: registrationToken
      });

      // Clean up the temporary data
      localStorage.removeItem('registration_token');
      localStorage.removeItem('user_id');

      setSuccessMessage(t.onboardingCompleteSuccess);
      
      // Redirect to Claudia page after successful onboarding
      setTimeout(() => {
        navigate('/claudia');
      }, 2000);
    } catch (error) {
      console.error('Onboarding completion error:', error);
      setErrors({ general: error.message || t.onboardingError });
    } finally {
      setIsLoading(false);
    }
  };

  const handleRegistration = async (descParam) => {
    setIsLoading(true);
    setSuccessMessage('');

    try {
      // Register user without description
      const response = await registerUser({
        username: formData.username.trim(),
        email: formData.email.trim(),
        password: formData.password
      });

      if (response.success) {
        // Store the token and user data from registration response
        localStorage.setItem('registration_token', response.data.token);
        localStorage.setItem('user_id', response.data.user_id);
        
        setSuccessMessage(t.registrationSuccess);
        
        // Show email verification after successful registration
        setTimeout(() => {
          setShowEmailVerification(true);
        }, 1500);
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

  // Show email verification if triggered
  if (showEmailVerification) {
    return (
      <EmailVerification
        email={formData.email}
        token={localStorage.getItem('registration_token')}
        onVerified={() => {
          setShowEmailVerification(false);
          // Show transition animation before onboarding
          setTimeout(() => {
            setIsTransitioning(true);
          }, 500);
          
          // Show onboarding flow after transition animation
          setTimeout(() => {
            setShowOnboarding(true);
          }, 2500);
        }}
      />
    );
  }

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

          {/* Transition Animation */}
          {isTransitioning && !showOnboarding && (
            <div className="transition-animation">
              <div className="claudia-avatar">🤖</div>
              <h3 className="transition-title">Setting up your personalized experience...</h3>
              <div className="loading-spinner"></div>
              <p className="transition-subtitle">This will only take a moment</p>
            </div>
          )}

          {/* Submit Button */}
          <div className="registration-actions">
            <button
              type="submit"
              className={`btn registration-btn ${isLoading || successMessage ? 'btn-disabled' : 'btn-primary'}`}
              disabled={isLoading || successMessage}
            >
              {isLoading ? (
                'Creating Account...'
              ) : successMessage ? (
                'Account Created!'
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
