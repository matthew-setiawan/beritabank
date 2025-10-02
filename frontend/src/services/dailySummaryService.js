import { API_BASE_URL } from '../config/api';

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

export const getDailySummary = async () => {
  try {
    const response = await fetch(`${API_BASE_URL}/api/daily-summary`, {
      method: 'GET',
      headers: getAuthHeaders()
    });

    const data = await response.json();
    
    if (!response.ok) {
      throw new Error(data.error || 'Failed to fetch daily summary');
    }

    return data;
  } catch (error) {
    console.error('Error fetching daily summary:', error);
    throw error;
  }
};
