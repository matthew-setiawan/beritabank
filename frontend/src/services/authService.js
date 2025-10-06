import { API_BASE_URL } from '../config/api';

const AUTH_ENDPOINTS = {
  REGISTER: '/api/auth/register',
  LOGIN: '/api/auth/login',
  VERIFY_EMAIL: '/api/auth/verify_email',
  REGENERATE_CODE: '/api/auth/regenerate_verification_code',
  USER_STATUS: '/api/auth/check_status',
  CREATE_DESCRIPTION: '/api/auth/create_desc',
  CHANGE_PASSWORD: '/api/auth/change_password',
  DELETE_ACCOUNT: '/api/auth/delete_account',
};

export const registerUser = async (userData) => {
  try {
    const response = await fetch(`${API_BASE_URL}${AUTH_ENDPOINTS.REGISTER}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(userData),
    });

    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.error || 'Registration failed');
    }

    return data;
  } catch (error) {
    console.error('Registration error:', error);
    throw error;
  }
};

export const loginUser = async (credentials) => {
  try {
    const response = await fetch(`${API_BASE_URL}${AUTH_ENDPOINTS.LOGIN}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(credentials),
    });

    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.error || 'Login failed');
    }

    return data;
  } catch (error) {
    console.error('Login error:', error);
    throw error;
  }
};

export const verifyEmail = async (verificationCode, token) => {
  try {
    const response = await fetch(`${API_BASE_URL}${AUTH_ENDPOINTS.VERIFY_EMAIL}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`,
      },
      body: JSON.stringify({ code: verificationCode }),
    });

    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.error || 'Email verification failed');
    }

    return data;
  } catch (error) {
    console.error('Email verification error:', error);
    throw error;
  }
};

export const regenerateVerificationCode = async (token) => {
  try {
    const response = await fetch(`${API_BASE_URL}${AUTH_ENDPOINTS.REGENERATE_CODE}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`,
      },
    });

    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.error || 'Failed to regenerate verification code');
    }

    return data;
  } catch (error) {
    console.error('Regenerate verification code error:', error);
    throw error;
  }
};

export const checkUserStatus = async (token) => {
  try {
    const response = await fetch(`${API_BASE_URL}${AUTH_ENDPOINTS.USER_STATUS}`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`,
      },
    });

    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.error || 'Failed to check user status');
    }

    return data;
  } catch (error) {
    console.error('Check user status error:', error);
    throw error;
  }
};

export const createUserDescription = async (description, token) => {
  try {
    const response = await fetch(`${API_BASE_URL}${AUTH_ENDPOINTS.CREATE_DESCRIPTION}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`,
      },
      body: JSON.stringify({ desc: description }),
    });

    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.error || 'Failed to create user description');
    }

    return data;
  } catch (error) {
    console.error('Create user description error:', error);
    throw error;
  }
};

export const changePassword = async (passwordData, token) => {
  try {
    const response = await fetch(`${API_BASE_URL}${AUTH_ENDPOINTS.CHANGE_PASSWORD}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`,
      },
      body: JSON.stringify(passwordData),
    });

    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.error || 'Failed to change password');
    }

    return data;
  } catch (error) {
    console.error('Change password error:', error);
    throw error;
  }
};

export const deleteAccount = async (accountData, token) => {
  try {
    const response = await fetch(`${API_BASE_URL}${AUTH_ENDPOINTS.DELETE_ACCOUNT}`, {
      method: 'DELETE',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`,
      },
      body: JSON.stringify(accountData),
    });

    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.error || 'Failed to delete account');
    }

    return data;
  } catch (error) {
    console.error('Delete account error:', error);
    throw error;
  }
};
