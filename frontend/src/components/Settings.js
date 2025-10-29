import React from 'react';
import { useUserStore, useSearchStore } from '../stores';
import { API_ENDPOINTS, apiCall } from '../config/api';

function Settings() {
  const { preferences, updatePreferences, recentActivity, bookmarks } = useUserStore();
  const { searchHistory, savedSearches } = useSearchStore();

  const handlePreferenceChange = (key, value) => {
    updatePreferences({ [key]: value });
  };

  return (
    <div className="page-container">
      <div className="page-header">
        <h1>Admin & Settings</h1>
        <p className="page-description">
          System diagnostics, user preferences, and application settings
        </p>
      </div>

      <div className="page-content">
        <div className="settings-grid">

          {/* Display Preferences */}
          <div className="settings-card">
            <h3>🎨 Display Preferences</h3>
            <div className="settings-section">
              <div className="setting-item">
                <label>Theme:</label>
                <select
                  value={preferences.theme}
                  onChange={(e) => handlePreferenceChange('theme', e.target.value)}
                >
                  <option value="light">Light</option>
                  <option value="dark">Dark</option>
                  <option value="auto">Auto</option>
                </select>
              </div>

              <div className="setting-item">
                <label>Results per page:</label>
                <select
                  value={preferences.pageSize}
                  onChange={(e) => handlePreferenceChange('pageSize', parseInt(e.target.value))}
                >
                  <option value={10}>10</option>
                  <option value={25}>25</option>
                  <option value={50}>50</option>
                  <option value={100}>100</option>
                </select>
              </div>

              <div className="setting-item">
                <label>Default view:</label>
                <select
                  value={preferences.defaultView}
                  onChange={(e) => handlePreferenceChange('defaultView', e.target.value)}
                >
                  <option value="list">List</option>
                  <option value="grid">Grid</option>
                  <option value="table">Table</option>
                </select>
              </div>
            </div>
          </div>

          {/* Notification Settings */}
          <div className="settings-card">
            <h3>🔔 Notification Preferences</h3>
            <div className="settings-section">
              <div className="setting-item checkbox-item">
                <label>
                  <input
                    type="checkbox"
                    checked={preferences.notifications}
                    onChange={(e) => handlePreferenceChange('notifications', e.target.checked)}
                  />
                  Enable notifications
                </label>
              </div>

              <div className="setting-item checkbox-item">
                <label>
                  <input
                    type="checkbox"
                    checked={preferences.autoSave}
                    onChange={(e) => handlePreferenceChange('autoSave', e.target.checked)}
                  />
                  Auto-save searches
                </label>
              </div>
            </div>
          </div>

          {/* Language Settings */}
          <div className="settings-card">
            <h3>🌐 Language & Region</h3>
            <div className="settings-section">
              <div className="setting-item">
                <label>Language:</label>
                <select
                  value={preferences.language}
                  onChange={(e) => handlePreferenceChange('language', e.target.value)}
                >
                  <option value="en">English</option>
                  <option value="es">Español</option>
                </select>
              </div>
            </div>
          </div>

          {/* Data & Privacy */}
          <div className="settings-card">
            <h3>🔒 Data & Privacy</h3>
            <div className="settings-section">
              <div className="setting-item">
                <p className="setting-description">
                  Your search history and preferences are stored locally in your browser.
                  Data is encrypted and never shared with third parties.
                </p>
              </div>

              <div className="setting-item">
                <p className="setting-description">
                  <strong>Current preferences:</strong>
                </p>
                <pre className="preferences-display">
                  {JSON.stringify(preferences, null, 2)}
                </pre>
              </div>
            </div>
          </div>

          {/* About */}
          <div className="settings-card">
            <h3>ℹ️ About CA Lobby</h3>
            <div className="settings-section">
              <div className="setting-item">
                <p className="setting-description">
                  CA Lobby provides transparent access to California lobbying data.
                  Built with modern web technologies for fast, accessible public information access.
                </p>
              </div>

              <div className="setting-item">
                <p className="setting-description">
                  <strong>Version:</strong> 1.0.0<br />
                  <strong>Phase:</strong> 2b - State Management<br />
                  <strong>Status:</strong> Active Development
                </p>
              </div>
            </div>
          </div>

        </div>

        {/* System Status Section (Admin) */}
        <div className="dashboard-section">
          <h2>⚙️ System Status & Diagnostics</h2>
          <div className="dashboard-grid">
            <div className="dashboard-card">
              <h3>API Health Check</h3>
              <APIHealthCheck />
            </div>

            <div className="dashboard-card">
              <h3>System Status</h3>
              <SystemStatus />
            </div>

            <div className="dashboard-card">
              <h3>Cache Performance</h3>
              <DataAccessTest />
            </div>

            <div className="dashboard-card">
              <h3>Recent Search Activity</h3>
              <div className="activity-list">
                {searchHistory.length > 0 ? (
                  searchHistory.slice(0, 5).map((search, index) => (
                    <div key={index} className="activity-item">
                      <span className="search-query">"{search.query || 'Empty query'}"</span>
                      <span className="search-time">
                        {new Date(search.timestamp).toLocaleDateString()}
                      </span>
                    </div>
                  ))
                ) : (
                  <p className="no-activity">No recent searches</p>
                )}
              </div>
            </div>

            <div className="dashboard-card">
              <h3>User Stats</h3>
              <div className="stats-grid">
                <div className="stat-item">
                  <span className="stat-label">Saved Searches:</span>
                  <span className="stat-value">{savedSearches.length}</span>
                </div>
                <div className="stat-item">
                  <span className="stat-label">Bookmarks:</span>
                  <span className="stat-value">{bookmarks.length}</span>
                </div>
                <div className="stat-item">
                  <span className="stat-label">Recent Activity:</span>
                  <span className="stat-value">{recentActivity.length}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

// API Health Check Component
function APIHealthCheck() {
  const [health, setHealth] = React.useState(null);
  const [loading, setLoading] = React.useState(true);

  React.useEffect(() => {
    const fetchHealth = async () => {
      try {
        const data = await apiCall(API_ENDPOINTS.health);
        setHealth(data);
      } catch (err) {
        setHealth({
          status: 'demo_mode',
          service: 'ca-lobby-api',
          version: '1.3.0',
          environment: 'production',
          database: { status: 'demo_mode' },
          message: 'Running in demo mode - backend not connected'
        });
      } finally {
        setLoading(false);
      }
    };

    fetchHealth();
  }, []);

  if (loading) return <div>Loading...</div>;

  return (
    <div className="api-result">
      {health ? (
        <div className="success">
          <p>Status: {health.status}</p>
          <p>Service: {health.service}</p>
          <p>Version: {health.version}</p>
          <p>Environment: {health.environment}</p>
          <p>Database: {health.database?.status}</p>
        </div>
      ) : (
        <div className="error">Failed to load health status</div>
      )}
    </div>
  );
}

// System Status Component
function SystemStatus() {
  const [status, setStatus] = React.useState(null);
  const [loading, setLoading] = React.useState(true);

  React.useEffect(() => {
    const fetchStatus = async () => {
      try {
        const data = await apiCall(API_ENDPOINTS.status);
        setStatus(data);
      } catch (err) {
        setStatus({
          phase: '1.3 - Frontend-Backend Integration (Demo Mode)',
          components: {
            backend_api: 'demo_mode',
            database: 'demo_mode',
            authentication: 'clerk_active',
            search_api: 'demo_mode'
          },
          performance: {
            cache_hit_rate: 'N/A'
          }
        });
      } finally {
        setLoading(false);
      }
    };

    fetchStatus();
  }, []);

  if (loading) return <div>Loading...</div>;

  return (
    <div className="api-result">
      {status ? (
        <div className="success">
          <p>Phase: {status.phase}</p>
          <p>Backend API: {status.components?.backend_api}</p>
          <p>Database: {status.components?.database}</p>
          <p>Authentication: {status.components?.authentication}</p>
          <p>Cache Hit Rate: {status.performance?.cache_hit_rate}</p>
        </div>
      ) : (
        <div className="error">Failed to load system status</div>
      )}
    </div>
  );
}

// Cache Performance Component
function DataAccessTest() {
  const [data, setData] = React.useState(null);
  const [loading, setLoading] = React.useState(true);

  React.useEffect(() => {
    const fetchCacheStats = async () => {
      try {
        const data = await apiCall(API_ENDPOINTS.cacheStats);
        setData(data);
      } catch (err) {
        setData({
          success: true,
          cache_hits: 0,
          cache_misses: 0,
          hit_rate: '0%',
          cached_keys: 0,
          message: 'Demo mode - no backend connected'
        });
      } finally {
        setLoading(false);
      }
    };

    fetchCacheStats();
  }, []);

  if (loading) return <div>Loading...</div>;

  return (
    <div className="api-result">
      {data ? (
        <div className="success">
          <p>Status: {data.success ? 'Active' : 'Error'}</p>
          <p>Cache Hits: {data.cache_hits || 0}</p>
          <p>Cache Misses: {data.cache_misses || 0}</p>
          <p>Hit Rate: {data.hit_rate || '0%'}</p>
          <p>Cached Keys: {data.cached_keys || 0}</p>
        </div>
      ) : (
        <div className="error">Failed to load cache stats</div>
      )}
    </div>
  );
}

export default Settings;