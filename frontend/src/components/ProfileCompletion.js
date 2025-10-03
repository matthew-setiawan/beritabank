import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useLanguage } from '../contexts/LanguageContext';
import { useAuth } from '../contexts/AuthContext';
import { translations } from '../translations/translations';
import EmailVerification from './EmailVerification';
import OnboardingFlow from './OnboardingFlow';

const ProfileCompletion = () => {
  const { language } = useLanguage();
  const { user, token, userStatus, statusLoading, refreshUserStatus } = useAuth();
  const navigate = useNavigate();
  const t = translations[language];
  const [isCompletingOnboarding, setIsCompletingOnboarding] = useState(false);

  useEffect(() => {
    // Only refresh user status if we don't have status data yet
    if (token && !userStatus && !statusLoading) {
      refreshUserStatus();
    }
  }, [token, userStatus, statusLoading, refreshUserStatus]);

  // Show completion loading screen
  if (isCompletingOnboarding) {
    return (
      <div className="profile-completion-container">
        <div className="profile-completion-card">
          <div className="completion-loading">
            <div className="claudia-avatar">🤖</div>
            <h2 className="completion-title">{t.settingUpProfile}</h2>
            <div className="loading-spinner"></div>
            <p className="completion-subtitle">{t.almostDone}</p>
          </div>
        </div>
      </div>
    );
  }

  // Show loading while checking status
  if (statusLoading) {
    return (
      <div className="profile-completion-container">
        <div className="profile-completion-card">
          <div className="loading-content">
            <div className="loading-spinner"></div>
            <p>{t.checkingProfile}</p>
          </div>
        </div>
      </div>
    );
  }

  // If user status is not available, redirect to login
  if (!userStatus) {
    navigate('/login');
    return null;
  }

  // If all requirements are met, redirect to home
  if (userStatus.all_requirements_met) {
    navigate('/');
    return null;
  }

  // Handle email verification requirement
  if (userStatus.missing_requirements.includes('email_verification')) {
    return (
      <EmailVerification
        email={user.email}
        token={token}
        onVerified={() => {
          refreshUserStatus();
        }}
      />
    );
  }

  // Handle user description requirement (onboarding)
  if (userStatus.missing_requirements.includes('user_description')) {
    return (
      <OnboardingFlow
        onComplete={async (description) => {
          try {
            // Show completion loading screen
            setIsCompletingOnboarding(true);
            
            // Create user description
            const { createUserDescription } = await import('../services/authService');
            await createUserDescription(description, token);
            
            // Wait a bit for better UX
            setTimeout(async () => {
              // Refresh user status
              await refreshUserStatus();
              setIsCompletingOnboarding(false);
            }, 2000);
          } catch (error) {
            console.error('Failed to create user description:', error);
            setIsCompletingOnboarding(false);
          }
        }}
      />
    );
  }

  // Fallback - redirect to home
  navigate('/');
  return null;
};

export default ProfileCompletion;
