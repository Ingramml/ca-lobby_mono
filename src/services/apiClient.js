import { useSearchStore } from '../stores/searchStore';
import { useUserStore } from '../stores/userStore';
import { useAppStore } from '../stores/appStore';

class CALobbyAPIClient {
  constructor() {
    // Enhanced environment-aware base URL configuration
    this.baseURL = this.getApiBaseUrl();
    this.cache = new Map();
    this.requestQueue = [];
    this.isOnline = navigator.onLine;
    this.connectionType = this.getConnectionType();

    // Enhanced mobile-specific configurations
    this.mobileConfig = {
      timeout: {
        fast: 5000,      // 5s for quick operations (health, status)
        normal: 10000,   // 10s for search operations
        slow: 30000      // 30s for export operations
      },
      retryAttempts: 3,
      cacheExpiry: 5 * 60 * 1000, // 5 minutes
      batchDelay: 100, // Batch requests for mobile
      compressionThreshold: 1024 // Compress responses > 1KB
    };

    // Performance metrics tracking
    this.metrics = {
      requests: 0,
      cacheHits: 0,
      cacheMisses: 0,
      errors: 0,
      avgResponseTime: 0
    };

    this.setupNetworkListeners();
  }

  getApiBaseUrl() {
    // Enhanced environment detection
    if (process.env.NODE_ENV === 'production') {
      return '/api/v1'; // Use relative URLs in production
    }
    return process.env.REACT_APP_API_URL || 'http://localhost:5001/api/v1';
  }

  getConnectionType() {
    if (!navigator.onLine) return 'offline';

    const connection = navigator.connection || navigator.mozConnection || navigator.webkitConnection;
    if (connection) {
      return connection.effectiveType || connection.type || 'unknown';
    }
    return 'unknown';
  }

  isSlowConnection() {
    return ['slow-2g', '2g', '3g'].includes(this.connectionType);
  }

  getUserAgent() {
    return `CA-Lobby-App/1.0 (${navigator.platform}; ${this.connectionType})`;
  }

  updateResponseTimeMetrics(responseTime) {
    // Simple moving average for response time
    if (this.metrics.avgResponseTime === 0) {
      this.metrics.avgResponseTime = responseTime;
    } else {
      this.metrics.avgResponseTime = (this.metrics.avgResponseTime * 0.9) + (responseTime * 0.1);
    }
  }

  getPerformanceMetrics() {
    const cacheHitRate = this.metrics.requests > 0
      ? (this.metrics.cacheHits / this.metrics.requests * 100).toFixed(1)
      : '0.0';

    return {
      ...this.metrics,
      cacheHitRate: `${cacheHitRate}%`,
      avgResponseTime: `${this.metrics.avgResponseTime.toFixed(0)}ms`,
      connectionType: this.connectionType,
      isOnline: this.isOnline
    };
  }

  setupNetworkListeners() {
    window.addEventListener('online', () => {
      this.isOnline = true;
      this.processQueuedRequests();
    });

    window.addEventListener('offline', () => {
      this.isOnline = false;
    });
  }

  async request(endpoint, options = {}) {
    const startTime = performance.now();
    const url = `${this.baseURL}${endpoint}`;
    const cacheKey = `${endpoint}:${JSON.stringify(options)}`;

    this.metrics.requests++;

    // Check cache first (mobile optimization)
    if ((options.method === 'GET' || !options.method) && this.cache.has(cacheKey)) {
      const cached = this.cache.get(cacheKey);
      if (Date.now() - cached.timestamp < this.mobileConfig.cacheExpiry) {
        this.metrics.cacheHits++;
        return cached.data;
      }
    }

    this.metrics.cacheMisses++;

    // Queue request if offline
    if (!this.isOnline) {
      return this.queueRequest(endpoint, options);
    }

    // Determine timeout based on connection speed and endpoint type
    let timeout = this.mobileConfig.timeout.normal;
    if (endpoint.includes('/health') || endpoint.includes('/status')) {
      timeout = this.mobileConfig.timeout.fast;
    } else if (endpoint.includes('/export') || endpoint.includes('/analytics')) {
      timeout = this.mobileConfig.timeout.slow;
    }

    // Adjust timeout for slow connections
    if (this.isSlowConnection()) {
      timeout *= 2;
    }

    const config = {
      timeout,
      ...options,
      headers: {
        'Content-Type': 'application/json',
        'Accept-Encoding': 'gzip, deflate, br',
        'User-Agent': this.getUserAgent(),
        ...options.headers
      }
    };

    try {
      const response = await this.fetchWithTimeout(url, config);

      if (!response.ok) {
        const error = new Error(`API Error: ${response.status}`);
        error.status = response.status;
        throw error;
      }

      const data = await response.json();

      // Update performance metrics
      const responseTime = performance.now() - startTime;
      this.updateResponseTimeMetrics(responseTime);

      // Cache successful GET requests
      if (options.method === 'GET' || !options.method) {
        this.cache.set(cacheKey, {
          data,
          timestamp: Date.now()
        });
      }

      return data;
    } catch (error) {
      return this.handleError(error, endpoint, options);
    }
  }

  async fetchWithTimeout(url, config) {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), config.timeout);

    try {
      const response = await fetch(url, {
        ...config,
        signal: controller.signal
      });
      clearTimeout(timeoutId);
      return response;
    } catch (error) {
      clearTimeout(timeoutId);
      throw error;
    }
  }

  async handleError(error, endpoint, options, attempt = 1) {
    const { addNotification } = useAppStore.getState();
    this.metrics.errors++;

    // Enhanced retry logic for mobile networks
    const shouldRetry = attempt < this.mobileConfig.retryAttempts && (
      error.name === 'AbortError' ||
      error.message.includes('network') ||
      error.message.includes('timeout') ||
      (error.status >= 500 && error.status < 600)
    );

    if (shouldRetry) {
      // Exponential backoff with jitter for mobile networks
      const backoffTime = Math.min(1000 * Math.pow(2, attempt - 1) + Math.random() * 1000, 10000);

      addNotification({
        type: 'warning',
        message: `Connection issue detected. Retrying... (${attempt}/${this.mobileConfig.retryAttempts})`
      });

      await new Promise(resolve => setTimeout(resolve, backoffTime));
      return this.request(endpoint, options);
    }

    // Enhanced error messaging based on error type
    let errorMessage = 'Network error. Please check your connection and try again.';

    if (error.name === 'AbortError') {
      errorMessage = 'Request timed out. Please try again.';
    } else if (error.status === 401) {
      errorMessage = 'Authentication required. Please sign in again.';
    } else if (error.status === 429) {
      errorMessage = 'Too many requests. Please wait a moment and try again.';
    } else if (error.status >= 500) {
      errorMessage = 'Server error. Please try again in a few moments.';
    } else if (!navigator.onLine) {
      errorMessage = 'You appear to be offline. Please check your connection.';
    }

    addNotification({
      type: 'error',
      message: errorMessage
    });

    throw error;
  }

  async queueRequest(endpoint, options) {
    return new Promise((resolve, reject) => {
      this.requestQueue.push({
        endpoint,
        options,
        resolve,
        reject
      });
    });
  }

  async processQueuedRequests() {
    const queue = [...this.requestQueue];
    this.requestQueue = [];

    for (const request of queue) {
      try {
        const result = await this.request(request.endpoint, request.options);
        request.resolve(result);
      } catch (error) {
        request.reject(error);
      }
    }
  }

  // Search API methods with mobile optimization
  async searchLobbyData(filters, page = 1) {
    const params = new URLSearchParams({
      page: page.toString(),
      limit: this.isSlowConnection() ? '10' : '25', // Reduce payload on slow connections
      ...filters
    });

    // Add compression hint for large result sets
    const headers = {};
    if (filters.query && filters.query.length < 3) {
      headers['Prefer'] = 'minimal-response';
    }

    return this.request(`/search?${params}`, { headers });
  }

  async getAnalyticsTrends(timeframe = 'month', category = null) {
    const params = new URLSearchParams({ timeframe });
    if (category) params.append('category', category);

    return this.request(`/analytics/trends?${params}`);
  }

  async getOrganizationAnalytics(limit = 10, timeframe = 'year') {
    const params = new URLSearchParams({
      limit: limit.toString(),
      timeframe
    });

    return this.request(`/analytics/organizations?${params}`);
  }

  // User API methods (with authentication)
  async getSavedSearches() {
    const { userProfile } = useUserStore.getState();
    if (!userProfile) throw new Error('Authentication required');

    return this.request('/user/searches', {
      headers: {
        'Authorization': `Bearer ${userProfile.token}`
      }
    });
  }

  async saveSearch(name, filters) {
    const { userProfile } = useUserStore.getState();
    if (!userProfile) throw new Error('Authentication required');

    return this.request('/user/searches', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${userProfile.token}`
      },
      body: JSON.stringify({ name, filters })
    });
  }

  // Export functionality
  async exportData(format, filters, columns = []) {
    return this.request('/export', {
      method: 'POST',
      body: JSON.stringify({
        format,
        filters,
        columns
      })
    });
  }

  // System status with mobile optimization
  async getSystemStatus() {
    return this.request('/system/status');
  }

  // Mobile-specific methods
  async prefetchCommonData() {
    if (this.isSlowConnection()) return; // Skip on slow connections

    try {
      // Prefetch frequently accessed data
      const promises = [
        this.getAnalyticsTrends('month'),
        this.getOrganizationAnalytics(5),
        this.request('/health')
      ];

      await Promise.allSettled(promises);
    } catch (error) {
      // Silent fail for prefetch operations
      console.debug('Prefetch failed:', error);
    }
  }

  async clearCache() {
    this.cache.clear();
    return { success: true, message: 'Cache cleared successfully' };
  }

  async syncOfflineData() {
    if (!this.isOnline || this.requestQueue.length === 0) {
      return { synced: 0, failed: 0 };
    }

    return this.processQueuedRequests();
  }

  // Connection monitoring
  startConnectionMonitoring() {
    if (this.connectionMonitor) return;

    this.connectionMonitor = setInterval(() => {
      this.connectionType = this.getConnectionType();

      // Update configuration based on connection
      if (this.isSlowConnection()) {
        this.mobileConfig.batchDelay = 500;
        this.mobileConfig.retryAttempts = 2;
      } else {
        this.mobileConfig.batchDelay = 100;
        this.mobileConfig.retryAttempts = 3;
      }
    }, 30000); // Check every 30 seconds
  }

  stopConnectionMonitoring() {
    if (this.connectionMonitor) {
      clearInterval(this.connectionMonitor);
      this.connectionMonitor = null;
    }
  }
}

export const apiClient = new CALobbyAPIClient();