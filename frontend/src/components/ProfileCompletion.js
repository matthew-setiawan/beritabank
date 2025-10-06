import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useLanguage } from '../contexts/LanguageContext';
import { useAuth } from '../contexts/AuthContext';
import { translations } from '../translations/translations';
import { createUserDescription } from '../services/authService';
import EmailVerification from './EmailVerification';
import OnboardingFlow from './OnboardingFlow';

const ProfileCompletion = ({ onComplete, description }) => {
  const { language } = useLanguage();
  const { user, token, userStatus, statusLoading, refreshUserStatus } = useAuth();
  const t = translations[language];
  const navigate = useNavigate();
  
  const [currentStep, setCurrentStep] = useState('checking');
  const [isSaving, setIsSaving] = useState(false);

  useEffect(() => {
    // If we have a description from Register component, go directly to saving
    if (description) {
      setCurrentStep('saving');
      handleOnboardingComplete(description);
      return;
    }

    if (userStatus && !statusLoading) {
      if (!userStatus.is_verified && !userStatus.has_description) {
        setCurrentStep('email-verification');
      } else if (!userStatus.is_verified) {
        setCurrentStep('email-verification');
      } else if (!userStatus.has_description) {
        setCurrentStep('onboarding');
      } else {
        // All requirements met, redirect to Claudia
        navigate('/claudia');
      }
    }
  }, [userStatus, statusLoading, navigate, description]);

  const handleEmailVerified = () => {
    // Refresh user status after email verification
    refreshUserStatus().then(() => {
      // The useEffect will handle the next step
    });
  };

  const handleOnboardingComplete = async (description) => {
    setIsSaving(true);
    try {
      if (onComplete) {
        // Use the custom completion handler from Register component
        await onComplete(description);
      } else {
        // Save the description to the backend
        await createUserDescription(description, token);
        
        // Refresh user status after successful save
        await refreshUserStatus();
      }
    } catch (error) {
      console.error('Failed to save user description:', error);
      setIsSaving(false);
      // You might want to show an error message to the user here
    }
  };

  if (statusLoading || currentStep === 'checking') {
    return (
      <div className="profile-completion-container">
        <div className="loading-container">
          <div className="loading-spinner"></div>
          <p>{t.checkingProfileStatus}</p>
        </div>
      </div>
    );
  }

  if (isSaving || currentStep === 'saving') {
    return (
      <div className="profile-completion-container">
        <div className="saving-container">
          <div className="claudia-avatar">🤖</div>
          <h2 className="saving-title">{t.settingUpProfile}</h2>
          <div className="loading-spinner"></div>
          <p className="saving-subtitle">{t.creatingPersonalizedExperience}</p>
          <div className="progress-steps">
            <div className="step completed">
              <span className="step-icon">✅</span>
              <span className="step-text">{t.onboardingCompleted}</span>
            </div>
            <div className="step active">
              <span className="step-icon">⏳</span>
              <span className="step-text">{t.savingPreferences}</span>
            </div>
            <div className="step pending">
              <span className="step-icon">⏸️</span>
              <span className="step-text">{t.generatingSummary}</span>
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (currentStep === 'email-verification') {
    return (
      <EmailVerification
        email={user?.email}
        token={token}
        onVerified={handleEmailVerified}
      />
    );
  }

  if (currentStep === 'onboarding') {
    return (
      <OnboardingFlow
        onComplete={handleOnboardingComplete}
      />
    );
  }

  // Fallback - should not reach here
  return (
    <div className="profile-completion-container">
      <div className="error-container">
        <h2>{t.somethingWentWrong}</h2>
        <p>{t.pleaseRefreshPage}</p>
        <button onClick={() => window.location.reload()}>
          {t.refreshPage}
        </button>
      </div>
    </div>
  );
};

export default ProfileCompletion;
