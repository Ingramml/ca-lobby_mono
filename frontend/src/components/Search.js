import React from 'react';
import { useNavigate } from 'react-router-dom';
import { useSearchStore } from '../stores';
import { API_ENDPOINTS, apiCall } from '../config/api';

// All sample data removed - application now uses live BigQuery API only
// No fallback to demo/sample data

function Search() {
  // Use Zustand store instead of local state
  const {
    query,
    filters,
    results,
    loading,
    error,
    setQuery,
    setFilters,
    setResults,
    setLoading,
    setError,
    addToHistory
  } = useSearchStore();

  const navigate = useNavigate();

  // Pagination state
  const [currentPage, setCurrentPage] = React.useState(1);
  const [totalCount, setTotalCount] = React.useState(0);
  const resultsPerPage = 10;

  // Memoized helper function to get organization activity count
  const getOrganizationActivityCount = React.useMemo(
    () => (orgName) => results.filter(r => r.organization_name === orgName).length,
    [results]
  );

  const handleSearch = async (e, page = 1) => {
    if (e) e.preventDefault();
    console.log('Search button clicked - handleSearch triggered');

    // Allow search with just filters (no query required)
    const hasFilters = filters.organization ||
                      filters.lobbyist ||
                      (filters.category && filters.category !== 'all') ||
                      (filters.dateRange && filters.dateRange !== 'all') ||
                      filters.amountMin ||
                      filters.amountMax;

    console.log('Query:', query, 'Has filters:', hasFilters);
    console.log('Filters object:', JSON.stringify(filters, null, 2));

    if (!query.trim() && !hasFilters) {
      console.log('No search query or filters provided');
      setError('Please enter a search term or select at least one filter.');
      return;
    }

    // Validate query length
    const sanitizedQuery = query.trim().slice(0, 500);
    if (sanitizedQuery.length > 0 && sanitizedQuery.length < 2) {
      setError('Search query must be at least 2 characters.');
      return;
    }

    // Use store methods properly
    setLoading(true);
    setError(null);

    try {
      // ALWAYS use backend API - no sample data fallback
      const searchParams = new URLSearchParams({
        q: sanitizedQuery,
        page: page,
        limit: resultsPerPage
      });

      console.log('Calling API:', `${API_ENDPOINTS.search}?${searchParams}`);
      const data = await apiCall(`${API_ENDPOINTS.search}?${searchParams}`);

      if (data.success) {
        console.log('API response:', data);
        setResults(data.data || []);
        setCurrentPage(page);
        setTotalCount(data.pagination?.total_count || data.data?.length || 0);
        addToHistory({
          query,
          filters,
          resultCount: data.pagination?.total_count || data.data?.length || 0,
          timestamp: new Date().toISOString()
        });
        console.log('Backend search completed:', data.data?.length, 'results');
      } else {
        throw new Error(data.error?.message || 'Search failed');
      }
    } catch (error) {
      console.error('Search error:', error);
      // User-friendly error message (don't expose internal details)
      if (error.message?.includes('Rate limit')) {
        setError('Too many requests. Please wait a moment and try again.');
      } else {
        setError('Search failed. Please try again.');
      }
      setResults([]);
    } finally {
      // Always stop loading regardless of success or error
      setLoading(false);
    }
  };

  // Handle page change
  const handlePageChange = (newPage) => {
    handleSearch(null, newPage);
  };

  return (
    <div className="page-container">
      <div className="page-header">
        <h1>Advanced Search</h1>
        <p className="page-description">
          Search through California state lobbying data with powerful filtering and analysis tools
        </p>
      </div>

      <div className="page-content">
        <div className="search-section">
          <form onSubmit={handleSearch} className="search-form">
            <div className="search-input-group">
              <input
                type="text"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder="Search for lobbyists, organizations, bills, or topics..."
                className="search-input"
              />
              <button
                type="submit"
                className="search-btn"
                disabled={loading}
                style={{
                  opacity: loading ? 0.6 : 1,
                  pointerEvents: loading ? 'none' : 'auto'
                }}
              >
                {loading ? '⏳ Searching...' : '🔍 Search'}
              </button>
            </div>
          </form>

          <div className="filters-section">
            <h3>Advanced Filters</h3>
            <div className="filters-grid">
              <div className="filter-group">
                <label>Date Range:</label>
                <select
                  value={filters.dateRange}
                  onChange={(e) => setFilters({ dateRange: e.target.value })}
                  disabled={loading}
                >
                  <option value="all">All Time</option>
                  <option value="last-month">Last Month</option>
                  <option value="last-quarter">Last Quarter</option>
                  <option value="last-year">Last Year</option>
                  <option value="custom">Custom Range</option>
                </select>
              </div>

              <div className="filter-group">
                <label>Organization:</label>
                <input
                  type="text"
                  value={filters.organization}
                  onChange={(e) => setFilters({ organization: e.target.value })}
                  placeholder="Filter by organization name"
                  disabled={loading}
                />
              </div>

              <div className="filter-group">
                <label>Lobbyist:</label>
                <input
                  type="text"
                  value={filters.lobbyist}
                  onChange={(e) => setFilters({ lobbyist: e.target.value })}
                  placeholder="Filter by lobbyist name"
                  disabled={loading}
                />
              </div>

              <div className="filter-group">
                <label>Category:</label>
                <select
                  value={filters.category}
                  onChange={(e) => setFilters({ category: e.target.value })}
                  disabled={loading}
                >
                  <option value="all">All Categories</option>
                  <option value="healthcare">Healthcare</option>
                  <option value="technology">Technology</option>
                  <option value="environment">Environment</option>
                  <option value="education">Education</option>
                  <option value="finance">Finance</option>
                </select>
              </div>

              <div className="filter-group">
                <button
                  type="button"
                  className="btn btn-secondary"
                  onClick={() => setFilters({
                    dateRange: 'all',
                    organization: '',
                    lobbyist: '',
                    category: 'all',
                    amountMin: '',
                    amountMax: ''
                  })}
                  disabled={loading}
                >
                  Clear All Filters
                </button>
              </div>
            </div>
          </div>

          {/* Search Results Section */}
          {error && (
            <div className="search-error">
              <h3>Search Error</h3>
              <p>{error}</p>
              <button onClick={() => setError(null)} className="btn btn-secondary">
                Dismiss
              </button>
            </div>
          )}

          {results && results.length > 0 && (
            <div className="search-results">
              <h3>Search Results ({totalCount > 0 ? totalCount : results.length} found)</h3>
              <div className="results-list">
                {results.map((result, index) => (
                  <div
                    key={result.filer_id || index}
                    className="result-item"
                    onClick={() => {
                      console.log('Navigating to profile for:', result.organization_name);
                      navigate(`/organization/${encodeURIComponent(result.organization_name)}`);
                    }}
                    style={{ cursor: 'pointer' }}
                  >
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start' }}>
                      <div style={{ flex: 1 }}>
                        <h4
                          className="organization-link"
                          style={{ margin: '0 0 0.5rem 0', color: '#1f2937' }}
                        >
                          {result.organization_name || 'Unknown Organization'}
                        </h4>
                        <p style={{ margin: '0.25rem 0', color: '#6b7280', fontSize: '0.875rem' }}>
                          <strong>Filer ID:</strong> {result.filer_id || 'N/A'}
                        </p>
                        <p style={{ margin: '0.25rem 0', color: '#6b7280', fontSize: '0.875rem' }}>
                          <strong>Active Period:</strong> {result.first_year} - {result.latest_year}
                        </p>
                        {result.total_spending > 0 && (
                          <p style={{
                            margin: '0.5rem 0',
                            fontSize: '1rem',
                            fontWeight: '700',
                            color: '#059669',
                            background: '#ecfdf5',
                            padding: '6px 12px',
                            borderRadius: '6px',
                            display: 'inline-block'
                          }}>
                            Total Spent: ${(result.total_spending / 1000000).toFixed(2)}M
                          </p>
                        )}
                        {result.total_lobbying_firms > 0 && (
                          <p style={{ margin: '0.25rem 0', color: '#6b7280', fontSize: '0.875rem' }}>
                            <strong>Lobbying Firms:</strong> {result.total_lobbying_firms}
                          </p>
                        )}
                      </div>
                      <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-end', gap: '0.5rem' }}>
                        <span style={{
                          backgroundColor: '#e3f2fd',
                          color: '#1565c0',
                          padding: '4px 12px',
                          borderRadius: '12px',
                          fontSize: '0.75rem',
                          fontWeight: '600'
                        }}>
                          {result.filing_count} filing{result.filing_count !== 1 ? 's' : ''}
                        </span>
                        <span style={{
                          backgroundColor: '#f3e8ff',
                          color: '#7c3aed',
                          padding: '4px 12px',
                          borderRadius: '12px',
                          fontSize: '0.75rem',
                          fontWeight: '600'
                        }}>
                          {result.latest_year}
                        </span>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
              {/* Pagination Controls */}
              {totalCount > resultsPerPage && (
                <div style={{
                  display: 'flex',
                  justifyContent: 'center',
                  alignItems: 'center',
                  gap: '1rem',
                  marginTop: '1.5rem',
                  padding: '1rem',
                  borderTop: '1px solid #e5e7eb'
                }}>
                  <button
                    onClick={() => handlePageChange(currentPage - 1)}
                    disabled={currentPage <= 1 || loading}
                    style={{
                      padding: '8px 16px',
                      borderRadius: '6px',
                      border: '1px solid #d1d5db',
                      background: currentPage <= 1 ? '#f3f4f6' : '#fff',
                      cursor: currentPage <= 1 ? 'not-allowed' : 'pointer',
                      color: currentPage <= 1 ? '#9ca3af' : '#374151'
                    }}
                  >
                    ← Previous
                  </button>
                  <span style={{ color: '#6b7280' }}>
                    Page {currentPage} of {Math.ceil(totalCount / resultsPerPage)}
                  </span>
                  <button
                    onClick={() => handlePageChange(currentPage + 1)}
                    disabled={currentPage >= Math.ceil(totalCount / resultsPerPage) || loading}
                    style={{
                      padding: '8px 16px',
                      borderRadius: '6px',
                      border: '1px solid #d1d5db',
                      background: currentPage >= Math.ceil(totalCount / resultsPerPage) ? '#f3f4f6' : '#fff',
                      cursor: currentPage >= Math.ceil(totalCount / resultsPerPage) ? 'not-allowed' : 'pointer',
                      color: currentPage >= Math.ceil(totalCount / resultsPerPage) ? '#9ca3af' : '#374151'
                    }}
                  >
                    Next →
                  </button>
                </div>
              )}
            </div>
          )}

          {loading && (
            <div className="search-loading">
              <h3>Searching California lobbying database...</h3>
              <div className="loading-spinner"></div>
            </div>
          )}

          {!loading && !error && results.length === 0 && (
            <div className="search-results">
              <p>No results yet. Try searching for "California" or any organization name.</p>
            </div>
          )}
        </div>

        <div className="dashboard-grid">
          <div className="dashboard-card">
            <h3>Search Features</h3>
            <div className="placeholder-content">
              <p>Advanced search capabilities:</p>
              <ul>
                <li>Full-text search across California lobbying records</li>
                <li>Search by organization name</li>
                <li>Filter by date and time period</li>
                <li>View detailed filing information</li>
                <li>Navigate to organization profiles</li>
              </ul>
            </div>
          </div>

          <div className="dashboard-card">
            <h3>Database Statistics</h3>
            <div className="placeholder-content">
              <p>Currently searching:</p>
              <ul>
                <li>21,588 unique organizations</li>
                <li>4.2 million lobbying filings</li>
                <li>California statewide data</li>
                <li>Historical records through 2025</li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Search;
