import { API_BASE_URL } from '../config/api';

const CLAUDIA_ENDPOINTS = {
  MESSAGE: '/api/message',
  UPDATE_DESC: '/api/update_desc',
};

const getAuthHeaders = () => {
  try {
    const stored = localStorage.getItem('user');
    if (!stored) return {};
    const { token } = JSON.parse(stored);
    return token ? { Authorization: `Bearer ${token}` } : {};
  } catch {
    return {};
  }
};

export const sendMessageToClaudia = async (message = '', language = 'en') => {
  try {
    const response = await fetch(`${API_BASE_URL}${CLAUDIA_ENDPOINTS.MESSAGE}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...getAuthHeaders(),
      },
      body: JSON.stringify({ message, language }),
    });

    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.error || 'Failed to send message to Claudia');
    }

    return data;
  } catch (error) {
    console.error('Claudia AI error:', error);
    throw error;
  }
};

export const updateUserDescription = async (message) => {
  try {
    const response = await fetch(`${API_BASE_URL}${CLAUDIA_ENDPOINTS.UPDATE_DESC}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...getAuthHeaders(),
      },
      body: JSON.stringify({ message }),
    });

    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.error || 'Failed to update user description');
    }

    return data;
  } catch (error) {
    console.error('Update description error:', error);
    throw error;
  }
};

export const updateUserDescriptionWithContext = async (message, context) => {
  try {
    // Combine context and new message
    const messageWithContext = context ? `${context}\n\n${message}` : message;
    
    const response = await fetch(`${API_BASE_URL}${CLAUDIA_ENDPOINTS.UPDATE_DESC}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...getAuthHeaders(),
      },
      body: JSON.stringify({ message: messageWithContext }),
    });

    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.error || 'Failed to update user description');
    }

    return data;
  } catch (error) {
    console.error('Update description with context error:', error);
    throw error;
  }
};
