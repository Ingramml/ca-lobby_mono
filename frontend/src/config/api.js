// API configuration for different environments

const getApiBaseUrl = () => {
  // In production (Vercel), use relative URLs to the same domain
  if (process.env.NODE_ENV === 'production') {
    return '';
  }

  // In development with Vercel dev, use relative URLs (same server)
  // Vercel dev serves both frontend and API on same port (3000)
  return '';
};

export const API_BASE_URL = getApiBaseUrl();

export const API_ENDPOINTS = {
  health: `${API_BASE_URL}/api/health`,
  analytics: `${API_BASE_URL}/api/analytics`,
  search: `${API_BASE_URL}/api/search`,
  status: `${API_BASE_URL}/api/status`,
  cacheStats: `${API_BASE_URL}/api/cache/stats`,
  searchSuggestions: `${API_BASE_URL}/api/search/suggestions`,
  exportSearch: `${API_BASE_URL}/api/search/export`,
  databaseStats: `${API_BASE_URL}/api/database_stats`
};

// Helper function for making API calls with proper error handling and timeout
export const apiCall = async (url, options = {}) => {
  const timeout = options.timeout || 30000; // Default 30s timeout

  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), timeout);

  try {
    const response = await fetch(url, {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers
      },
      signal: controller.signal,
      ...options
    });

    clearTimeout(timeoutId);

    if (!response.ok) {
      // Handle rate limiting specifically
      if (response.status === 429) {
        throw new Error('Rate limit exceeded. Please wait before making more requests.');
      }
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }

    return await response.json();
  } catch (error) {
    clearTimeout(timeoutId);

    // Handle timeout specifically
    if (error.name === 'AbortError') {
      throw new Error('Request timed out. Please try again.');
    }

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