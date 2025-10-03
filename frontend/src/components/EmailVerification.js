import React, { useState, useEffect } from 'react';
import { useLanguage } from '../contexts/LanguageContext';
import { translations } from '../translations/translations';
import { verifyEmail, regenerateVerificationCode } from '../services/authService';

const EmailVerification = ({ email, token, onVerified }) => {
  const { language } = useLanguage();
  const t = translations[language];
  
  const [verificationCode, setVerificationCode] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isResending, setIsResending] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [timeRemaining, setTimeRemaining] = useState(0);
  const [canResend, setCanResend] = useState(false);

  useEffect(() => {
    // Start countdown timer (assuming 5 minutes = 300 seconds)
    setTimeRemaining(300);
    const timer = setInterval(() => {
      setTimeRemaining(prev => {
        if (prev <= 1) {
          setCanResend(true);
          clearInterval(timer);
          return 0;
        }
        return prev - 1;
      });
    }, 1000);

    return () => clearInterval(timer);
  }, []);

  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  const handleCodeChange = (e) => {
    const value = e.target.value.replace(/\D/g, ''); // Only allow digits
    if (value.length <= 6) {
      setVerificationCode(value);
      setError('');
    }
  };

  const handleVerify = async (e) => {
    e.preventDefault();
    
    if (verificationCode.length !== 6) {
      setError(t.verificationCodeInvalid);
      return;
    }

    setIsLoading(true);
    setError('');

    try {
      const response = await verifyEmail(verificationCode, token);
      
      if (response.success) {
        setSuccess(t.emailVerifiedSuccess);
        setTimeout(() => {
          onVerified();
        }, 2000);
      }
    } catch (error) {
      console.error('Verification error:', error);
      setError(error.message || t.verificationFailed);
    } finally {
      setIsLoading(false);
    }
  };

  const handleResendCode = async () => {
    setIsResending(true);
    setError('');

    try {
      const response = await regenerateVerificationCode(token);
      
      if (response.success) {
        setSuccess(t.verificationCodeSent);
        setTimeRemaining(300);
        setCanResend(false);
        
        // Restart countdown
        const timer = setInterval(() => {
          setTimeRemaining(prev => {
            if (prev <= 1) {
              setCanResend(true);
              clearInterval(timer);
              return 0;
            }
            return prev - 1;
          });
        }, 1000);
      }
    } catch (error) {
      console.error('Resend error:', error);
      setError(error.message || t.resendFailed);
    } finally {
      setIsResending(false);
    }
  };

  return (
    <div className="email-verification-container">
      <div className="email-verification-card">
        <div className="verification-header">
          <div className="verification-icon">📧</div>
          <h2 className="verification-title">{t.verifyEmailTitle}</h2>
          <p className="verification-subtitle">
            {t.verifyEmailSubtitle.replace('{email}', email)}
          </p>
        </div>

        <form onSubmit={handleVerify} className="verification-form">
          <div className="form-group">
            <label htmlFor="verificationCode" className="form-label">
              {t.verificationCodeLabel}
            </label>
            <input
              type="text"
              id="verificationCode"
              value={verificationCode}
              onChange={handleCodeChange}
              className={`verification-input ${error ? 'error' : ''}`}
              placeholder="000000"
              maxLength="6"
              autoComplete="off"
              disabled={isLoading}
            />
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

          <div className="verification-actions">
            <button
              type="submit"
              className="btn btn-primary verification-btn"
              disabled={isLoading || verificationCode.length !== 6}
            >
              {isLoading ? t.verifying : t.verifyEmail}
            </button>
          </div>
        </form>

        <div className="resend-section">
          <p className="resend-text">
            {canResend ? t.didntReceiveCode : t.resendIn.replace('{time}', formatTime(timeRemaining))}
          </p>
          <button
            type="button"
            className="btn btn-outline resend-btn"
            onClick={handleResendCode}
            disabled={!canResend || isResending}
          >
            {isResending ? t.sending : t.resendCode}
          </button>
        </div>
      </div>
    </div>
  );
};

export default EmailVerification;
