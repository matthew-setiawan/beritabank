import { API_BASE_URL } from '../config/api';

const AUTH_ENDPOINTS = {
  REGISTER: '/api/auth/register',
  LOGIN: '/api/auth/login',
  CREATE_DESC: '/api/auth/create_desc',
  REGENERATE_VERIFICATION: '/api/auth/regenerate_verification_code',
  VERIFY_EMAIL: '/api/auth/verify_email',
  CHECK_STATUS: '/api/auth/check_status',
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

export const createUserDescription = async (description, token) => {
  try {
    const response = await fetch(`${API_BASE_URL}${AUTH_ENDPOINTS.CREATE_DESC}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify({
        desc: description
      }),
    });

    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.error || 'Failed to create user description');
    }

    return data;
  } catch (error) {
    console.error('Create description error:', error);
    throw error;
  }
};

export const regenerateVerificationCode = async (token) => {
  try {
    const response = await fetch(`${API_BASE_URL}${AUTH_ENDPOINTS.REGENERATE_VERIFICATION}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
    });

    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.error || 'Failed to regenerate verification code');
    }

    return data;
  } catch (error) {
    console.error('Regenerate verification error:', error);
    throw error;
  }
};

export const verifyEmail = async (code, token) => {
  try {
    const response = await fetch(`${API_BASE_URL}${AUTH_ENDPOINTS.VERIFY_EMAIL}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify({
        code: code
      }),
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

export const checkUserStatus = async (token) => {
  try {
    const response = await fetch(`${API_BASE_URL}${AUTH_ENDPOINTS.CHECK_STATUS}`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
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
