import { API_BASE_URL, API_ENDPOINTS } from '../config/api';
import { useAuth } from '../contexts/AuthContext';

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

export const fetchArticles = async () => {
  try {
    const response = await fetch(`${API_BASE_URL}${API_ENDPOINTS.ARTICLES}`, {
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
    console.error('Error fetching articles:', error);
    throw error;
  }
};

export const fetchArticleById = async (articleId) => {
  try {
    const response = await fetch(`${API_BASE_URL}${API_ENDPOINTS.ARTICLE_BY_ID}/${articleId}`, {
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
    console.error('Error fetching article by ID:', error);
    throw error;
  }
};
