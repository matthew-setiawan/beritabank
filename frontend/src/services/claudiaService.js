import { API_BASE_URL } from '../config/api';

const CLAUDIA_ENDPOINTS = {
  MESSAGE: '/api/message',
  UPDATE_DESC: '/api/update_desc',
  PREFERENCE_TAGS: '/api/auth/preference_tags',
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
      body: JSON.stringify({ 
        message
      }),
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

export const getPreferenceTags = async () => {
  try {
    const response = await fetch(`${API_BASE_URL}${CLAUDIA_ENDPOINTS.PREFERENCE_TAGS}`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
        ...getAuthHeaders(),
      },
    });

    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.error || 'Failed to get preference tags');
    }

    return data;
  } catch (error) {
    console.error('Get preference tags error:', error);
    throw error;
  }
};
