import React from 'react';
import { useNavigate } from 'react-router-dom';
import { useSearchStore } from '../stores';
import { API_ENDPOINTS, apiCall } from '../config/api';

// Import real Alameda County lobby data
import organizationsSummary from '../data/organizations-summary.json';

// Generate search results from real lobby data
const generateSearchResults = (query, filters) => {
  // Use real organizations data
  const organizations = organizationsSummary.organizations;

  // Transform organizations into searchable results format
  // Each organization becomes a result with its summary info
  const searchableData = organizations.map(org => ({
    organization: org.name,
    filer_id: org.filer_id,
    lobbyist: '', // Will be populated from profile data when needed
    description: `${org.category} - ${org.activityCount} activities from ${org.firstActivity} to ${org.lastActivity}`,
    amount: org.totalSpending,
    date: org.lastActivity,
    filing_date: org.lastActivity,
    category: org.category.toLowerCase().replace(/\s+/g, '-'),
    activity_description: `${org.organization_type} with ${org.registrationCount} registrations`,
    activityCount: org.activityCount,
    registrationCount: org.registrationCount,
    firstActivity: org.firstActivity,
    organization_type: org.organization_type
  }));

  // Keep old demo data as fallback for variety
  // ALL LEGACY DEMO DATA REMOVED - Only real Alameda County data now

  // Combine real data with legacy demo data for variety
  const allData = searchableData; // Only real data, no legacy demo

  // Filter data based on search query and filters
  const filtered = allData.filter(item => {
    // If no query provided, show all items (will be filtered by other criteria)
    const matchesQuery = !query || !query.trim() ||
      item.organization.toLowerCase().includes(query.toLowerCase()) ||
      (item.lobbyist && item.lobbyist.toLowerCase().includes(query.toLowerCase())) ||
      item.description.toLowerCase().includes(query.toLowerCase());

    const matchesOrganization = !filters.organization ||
      item.organization.toLowerCase().includes(filters.organization.toLowerCase());

    const matchesLobbyist = !filters.lobbyist ||
      (item.lobbyist && item.lobbyist.toLowerCase().includes(filters.lobbyist.toLowerCase()));

    const matchesCategory = !filters.category || filters.category === 'all' ||
      item.category === filters.category;

    // Date range filtering
    const matchesDateRange = !filters.dateRange || filters.dateRange === 'all' || (() => {
      const itemDate = new Date(item.date);
      const now = new Date();

      switch (filters.dateRange) {
        case 'last-month':
          const lastMonth = new Date(now.getFullYear(), now.getMonth() - 1, now.getDate());
          return itemDate >= lastMonth;
        case 'last-quarter':
          const lastQuarter = new Date(now.getFullYear(), now.getMonth() - 3, now.getDate());
          return itemDate >= lastQuarter;
        case 'last-year':
          const lastYear = new Date(now.getFullYear() - 1, now.getMonth(), now.getDate());
          return itemDate >= lastYear;
        default:
          return true;
      }
    })();

    // Amount range filtering
    const matchesAmountMin = !filters.amountMin ||
      item.amount >= parseInt(filters.amountMin);

    const matchesAmountMax = !filters.amountMax ||
      item.amount <= parseInt(filters.amountMax);

    const passes = matchesQuery && matchesOrganization && matchesLobbyist &&
           matchesCategory && matchesDateRange && matchesAmountMin && matchesAmountMax;

    // Debug first item to see why it fails
    if (item === allData[0]) {
      console.log('First item filter check:', {
        organization: item.organization,
        matchesQuery,
        matchesOrganization,
        matchesLobbyist,
        matchesCategory,
        matchesDateRange,
        matchesAmountMin,
        matchesAmountMax,
        passes
      });
    }

    return passes;
  }).slice(0, 20); // Limit to 20 results for demo

  console.log('generateSearchResults: filtered', filtered.length, 'from', allData.length, 'items');
  return filtered;
};

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

  // Memoized helper function to get organization activity count
  const getOrganizationActivityCount = React.useMemo(
    () => (orgName) => results.filter(r => r.organization === orgName).length,
    [results]
  );

  const handleSearch = async (e) => {
    e.preventDefault();
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

    // Use store methods properly
    setLoading(true);
    setError(null);

    try {
      // ALWAYS use demo data until backend integration is explicitly requested
      // Set REACT_APP_USE_BACKEND_API=true in .env to enable backend calls
      const useBackend = process.env.REACT_APP_USE_BACKEND_API === 'true';

      if (!useBackend) {
        // Use real lobby data (default behavior)
        console.log('Generating search results...');
        const searchResults = generateSearchResults(query, filters);
        console.log('Search results generated:', searchResults.length, 'results');

        // Update search store with results
        setResults(searchResults);
        console.log('Results set in store');

        // Add current search to history
        addToHistory({
          query,
          filters,
          resultCount: searchResults.length,
          timestamp: new Date().toISOString()
        });

        console.log('Search completed successfully');
      } else {
        // Backend API mode (requires REACT_APP_USE_BACKEND_API=true in .env)
        const searchParams = new URLSearchParams({
          q: query.trim(),
          client: filters.organization || '',
          lobbyist: filters.lobbyist || '',
          category: filters.category === 'all' ? '' : filters.category || '',
          date_range: filters.dateRange === 'all' ? '' : filters.dateRange || ''
        });

        const data = await apiCall(`${API_ENDPOINTS.search}?${searchParams}`);

        if (data.success) {
          setResults(data.data || []);
          addToHistory({
            query,
            filters,
            resultCount: data.data?.length || 0,
            timestamp: new Date().toISOString()
          });
          console.log('Backend search completed:', data);
        } else {
          throw new Error(data.message || 'Search failed');
        }
      }
    } catch (error) {
      console.error('Search error:', error);

      // Always fallback to real data on any error
      const fallbackResults = generateSearchResults(query, filters);
      setResults(fallbackResults);

      addToHistory({
        query,
        filters,
        resultCount: fallbackResults.length,
        timestamp: new Date().toISOString()
      });

      console.log('Fallback to real data:', fallbackResults.length, 'results');
    } finally {
      // Always stop loading regardless of success or error
      setLoading(false);
    }
  };

  return (
    <div className="page-container">
      <div className="page-header">
        <h1>Advanced Search</h1>
        <p className="page-description">
          Search through CA lobby data with powerful filtering and analysis tools
        </p>
        {process.env.NODE_ENV === 'production' && (
          <div className="demo-banner">
            <p>📝 <strong>Demo Mode:</strong> This is a demonstration of the search functionality with sample data.
            The full system connects to live California lobby data when deployed with the backend API.</p>
          </div>
        )}
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
              <button type="submit" className="search-btn" disabled={loading}>
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
                <label>Min Amount ($):</label>
                <input
                  type="number"
                  value={filters.amountMin || ''}
                  onChange={(e) => setFilters({ amountMin: e.target.value })}
                  placeholder="e.g. 50000"
                  disabled={loading}
                />
              </div>

              <div className="filter-group">
                <label>Max Amount ($):</label>
                <input
                  type="number"
                  value={filters.amountMax || ''}
                  onChange={(e) => setFilters({ amountMax: e.target.value })}
                  placeholder="e.g. 100000"
                  disabled={loading}
                />
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
              <h3>Search Results ({results.length} found)</h3>
              <div className="results-list">
                {results.slice(0, 10).map((result, index) => (
                  <div key={index} className="result-item">
                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                      <h4
                        className="organization-link"
                        style={{ margin: 0, display: 'inline' }}
                        onClick={() => {
                          console.log('Navigating to profile for:', result.organization);
                          navigate(`/organization/${encodeURIComponent(result.organization)}`);
                        }}
                      >
                        {result.organization || result.lobbyist || 'Lobby Entry'}
                      </h4>
                      {result.organization && getOrganizationActivityCount(result.organization) > 1 && (
                        <span style={{
                          backgroundColor: '#e3f2fd',
                          color: '#1565c0',
                          padding: '2px 8px',
                          borderRadius: '12px',
                          fontSize: '0.75rem',
                          fontWeight: '600'
                        }}>
                          {getOrganizationActivityCount(result.organization)} activities
                        </span>
                      )}
                    </div>
                    <p>{result.description || result.activity_description || 'No description available'}</p>
                    <span className="result-meta">
                      Amount: {result.amount ? `$${result.amount.toLocaleString()}` : 'N/A'} |
                      Date: {result.date || result.filing_date || 'N/A'}
                    </span>
                  </div>
                ))}
                {results.length > 10 && (
                  <p className="results-more">Showing first 10 of {results.length} results</p>
                )}
              </div>
            </div>
          )}

          {loading && (
            <div className="search-loading">
              <h3>Searching...</h3>
              <div className="loading-spinner"></div>
            </div>
          )}
        </div>

        <div className="dashboard-grid">
          <div className="dashboard-card">
            <h3>Search Features</h3>
            <div className="placeholder-content">
              <p>Advanced search capabilities will include:</p>
              <ul>
                <li>Full-text search across all lobby documents</li>
                <li>Boolean operators (AND, OR, NOT)</li>
                <li>Wildcard and fuzzy matching</li>
                <li>Phrase and proximity searches</li>
                <li>Auto-complete and search suggestions</li>
              </ul>
            </div>
          </div>

          <div className="dashboard-card">
            <h3>Filter Options</h3>
            <div className="placeholder-content">
              <p>Comprehensive filtering by:</p>
              <ul>
                <li>Date ranges and time periods</li>
                <li>Organization and entity types</li>
                <li>Spending amounts and thresholds</li>
                <li>Geographic regions and districts</li>
                <li>Document types and categories</li>
              </ul>
            </div>
          </div>

          <div className="dashboard-card">
            <h3>Search Results</h3>
            <div className="placeholder-content">
              <p>Results will be displayed with:</p>
              <div className="result-preview">
                <div className="result-item">
                  <h4>Sample Result 1</h4>
                  <p>Lobbyist registration for XYZ Corporation - Healthcare sector</p>
                  <span className="result-meta">Filed: Sept 15, 2024 | Amount: $50,000</span>
                </div>
                <div className="result-item">
                  <h4>Sample Result 2</h4>
                  <p>Quarterly activity report - Technology lobbying</p>
                  <span className="result-meta">Filed: Sept 10, 2024 | Amount: $25,000</span>
                </div>
              </div>
            </div>
          </div>

          <div className="dashboard-card">
            <h3>Export & Save</h3>
            <div className="placeholder-content">
              <p>Search result options:</p>
              <ul>
                <li>Export results to CSV, Excel, or PDF</li>
                <li>Save search queries for future use</li>
                <li>Set up alerts for new matching results</li>
                <li>Share search results with team members</li>
              </ul>
              <div className="button-group">
                <button className="export-btn" disabled>💾 Save Search</button>
                <button className="export-btn" disabled>📤 Export Results</button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Search;