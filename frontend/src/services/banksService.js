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

export const fetchBanks = async () => {
  try {
    const response = await fetch(`${API_BASE_URL}/api/banks`, {
      headers: {
        ...getAuthHeaders(),
      },
    });
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Error fetching banks:', error);
    throw error;
  }
};
