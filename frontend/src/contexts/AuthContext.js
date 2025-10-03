import React, { createContext, useContext, useEffect, useMemo, useState } from 'react';
import { checkUserStatus } from '../services/authService';

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(null);
  const [loading, setLoading] = useState(true);
  const [userStatus, setUserStatus] = useState(null);
  const [statusLoading, setStatusLoading] = useState(false);
  const [lastStatusCheck, setLastStatusCheck] = useState(0);

  useEffect(() => {
    try {
      const stored = localStorage.getItem('user');
      if (stored) {
        const parsed = JSON.parse(stored);
        setUser({
          userId: parsed.user_id,
          username: parsed.username,
          email: parsed.email,
        });
        setToken(parsed.token);
      }
    } catch (e) {
      console.error('Failed to parse stored user', e);
    } finally {
      setLoading(false);
    }
  }, []);

  // Check user status when token is available (only once per session)
  useEffect(() => {
    const checkStatus = async () => {
      const now = Date.now();
      // Only check if we haven't checked in the last 5 seconds
      if (token && user && !userStatus && (now - lastStatusCheck) > 5000) {
        setStatusLoading(true);
        setLastStatusCheck(now);
        try {
          const status = await checkUserStatus(token);
          setUserStatus(status.data);
        } catch (error) {
          console.error('Failed to check user status:', error);
          // If status check fails, assume user needs to complete profile
          setUserStatus({
            is_verified: false,
            has_description: false,
            all_requirements_met: false,
            missing_requirements: ['email_verification', 'user_description']
          });
        } finally {
          setStatusLoading(false);
        }
      }
    };

    checkStatus();
  }, [token, user, userStatus, lastStatusCheck]);

  const login = (authData) => {
    setUser({
      userId: authData.user_id,
      username: authData.username,
      email: authData.email,
    });
    setToken(authData.token);
    localStorage.setItem('user', JSON.stringify(authData));
  };

  const logout = () => {
    setUser(null);
    setToken(null);
    setUserStatus(null);
    localStorage.removeItem('user');
  };

  const refreshUserStatus = async () => {
    const now = Date.now();
    // Only refresh if we haven't checked in the last 2 seconds
    if (token && (now - lastStatusCheck) > 2000) {
      setStatusLoading(true);
      setLastStatusCheck(now);
      try {
        const status = await checkUserStatus(token);
        setUserStatus(status.data);
      } catch (error) {
        console.error('Failed to refresh user status:', error);
      } finally {
        setStatusLoading(false);
      }
    }
  };

  const value = useMemo(() => ({
    user,
    token,
    loading,
    isAuthenticated: Boolean(token),
    userStatus,
    statusLoading,
    refreshUserStatus,
    login,
    logout,
  }), [user, token, loading, userStatus, statusLoading]);

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuth must be used within AuthProvider');
  return ctx;
};


