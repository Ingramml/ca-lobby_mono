// API configuration for different environments

const getApiBaseUrl = () => {
  // In production (Vercel), use relative URLs to the same domain
  if (process.env.NODE_ENV === 'production') {
    return '';
  }

  // In development, use localhost backend
  return 'http://localhost:5001';
};

export const API_BASE_URL = getApiBaseUrl();

export const API_ENDPOINTS = {
  health: `${API_BASE_URL}/health`,
  status: `${API_BASE_URL}/api/status`,
  search: `${API_BASE_URL}/api/search/`,
  cacheStats: `${API_BASE_URL}/api/cache/stats`,
  searchSuggestions: `${API_BASE_URL}/api/search/suggestions`,
  exportSearch: `${API_BASE_URL}/api/search/export`
};

// Helper function for making API calls with proper error handling
export const apiCall = async (url, options = {}) => {
  try {
    const response = await fetch(url, {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers
      },
      ...options
    });

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }

    return await response.json();
  } catch (error) {
    // Silently fail in production demo mode - don't clutter console
    // These errors are expected when backend is not available
    if (process.env.NODE_ENV === 'production' && !process.env.REACT_APP_USE_BACKEND_API) {
      // Suppress console.error for expected API failures in demo mode
      // Component fallbacks will handle this gracefully
    } else {
      console.error('API call failed:', error);
    }
    throw error;
  }
};