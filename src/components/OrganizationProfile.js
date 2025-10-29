import React, { useEffect, useMemo, useCallback, useRef } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useOrganizationStore, useSearchStore } from '../stores';
import {
  aggregateOrganizationMetrics,
  extractLobbyistNetwork,
  calculateSpendingTrends,
  findRelatedOrganizations
} from '../utils/sampleData';
import {
  exportToCSV,
  exportToJSON,
  generateOrganizationSummaryCSV,
  sanitizeFilename
} from '../utils/exportHelpers';
import organizationsSummary from '../data/organizations-summary.json';
import ActivitySummary from './ActivitySummary';
import SpendingTrendsChart from './charts/SpendingTrendsChart';
import ActivityList from './ActivityList';
import LobbyistNetwork from './LobbyistNetwork';
import RelatedOrganizations from './RelatedOrganizations';
import TopRecipients from './TopRecipients';

const OrganizationProfile = React.memo(() => {
  const { organizationName } = useParams();
  const navigate = useNavigate();

  const {
    selectedOrganization,
    organizationData,
    activities,
    lobbyists,
    spendingTrends,
    relatedOrganizations,
    loading: orgLoading,
    error,
    setSelectedOrganization,
    setOrganizationData,
    setLobbyists,
    setSpendingTrends,
    setRelatedOrganizations,
    setActivities,
    setLoading,
    setError,
    clearOrganization
  } = useOrganizationStore();

  const { results } = useSearchStore();

  // Ref for heading focus management
  const headingRef = useRef(null);

  // Export handlers
  const handleExportCSV = useCallback(() => {
    const summaryData = generateOrganizationSummaryCSV({
      selectedOrganization,
      organizationData,
      lobbyists
    });
    const filename = `${sanitizeFilename(selectedOrganization)}_summary.csv`;
    exportToCSV([summaryData], filename);
  }, [selectedOrganization, organizationData, lobbyists]);

  const handleExportJSON = useCallback(() => {
    const exportData = {
      organization: selectedOrganization,
      metadata: organizationData,
      activities: activities,
      lobbyists: lobbyists,
      spendingTrends: spendingTrends,
      relatedOrganizations: relatedOrganizations,
      exportDate: new Date().toISOString()
    };
    const filename = `${sanitizeFilename(selectedOrganization)}_profile.json`;
    exportToJSON(exportData, filename);
  }, [selectedOrganization, organizationData, activities, lobbyists, spendingTrends, relatedOrganizations]);

  const decodedOrgName = useMemo(() =>
    decodeURIComponent(organizationName),
    [organizationName]
  );

  // Load organization profile data (lazy loaded from JSON files)
  useEffect(() => {
    if (!decodedOrgName) {
      clearOrganization();
      return;
    }

    const loadOrganizationProfile = async () => {
      try {
        // Set loading state
        setLoading(true);
        setSelectedOrganization(decodedOrgName);

        // Sanitize organization name to match filename
        const filename = decodedOrgName
          .toLowerCase()
          .replace(/[^a-z0-9]+/g, '-')
          .replace(/^-+|-+$/g, '')
          .substring(0, 50);

        console.log(`Loading profile for: ${decodedOrgName} (${filename})`);

        // Find matching organization in summary (for metadata)
        const summaryOrg = organizationsSummary.organizations.find(
          org => org.name === decodedOrgName
        );

        if (!summaryOrg) {
          throw new Error(`Organization not found in summary: ${decodedOrgName}`);
        }

        try {
          // Try to load REAL activity data from activities directory
          const activityModule = await import(`../data/activities/${filename}-activities.json`);
          const activityData = activityModule.default || activityModule;

          console.log('Real activity data loaded:', activityData);

          // Use data from organizations-summary.json
          const transformedData = {
            totalActivities: summaryOrg.activityCount || 0,
            totalSpending: summaryOrg.totalSpending || 0,
            averageAmount: summaryOrg.averageSpending || 0,
            topCategory: summaryOrg.category || 'N/A',
            firstActivity: summaryOrg.firstActivity,
            lastActivity: summaryOrg.lastActivity
          };

          console.log('Organization data from summary:', transformedData);

          setOrganizationData(transformedData);
          setActivities(activityData.activities || []);

          // Extract lobbyists from activities (we don't have this data yet)
          const lobbyistsData = extractLobbyistNetwork(activityData.activities || []);
          setLobbyists(lobbyistsData);

          // Calculate spending trends from activities
          const trends = calculateSpendingTrends(activityData.activities || [], 'quarter');
          setSpendingTrends(trends);

          // Find related organizations from search results
          const relatedData = findRelatedOrganizations(decodedOrgName, results, 5);
          setRelatedOrganizations(relatedData);

        } catch (fileError) {
          console.warn(`Activity file not found for ${filename}, falling back to search results`, fileError);

          // Fallback: Filter activities from search results
          const orgActivities = results.filter(
            r => r.organization === decodedOrgName
          );

          if (orgActivities.length === 0) {
            throw new Error(`No data found for organization: ${decodedOrgName}`);
          }

          // Aggregate data from search results
          const metrics = aggregateOrganizationMetrics(orgActivities);
          const lobbyists = extractLobbyistNetwork(orgActivities);
          const trends = calculateSpendingTrends(orgActivities, 'quarter');
          const related = findRelatedOrganizations(decodedOrgName, results, 5);

          // Update store with fallback data
          setOrganizationData(metrics);
          setActivities(orgActivities);
          setLobbyists(lobbyists);
          setSpendingTrends(trends);
          setRelatedOrganizations(related);
        }

      } catch (error) {
        setError(error.message);
        console.error('Error loading organization data:', error);
      } finally {
        setLoading(false);
      }
    };

    loadOrganizationProfile();
  }, [decodedOrgName, results, setSelectedOrganization, setOrganizationData,
      setActivities, setLobbyists, setSpendingTrends, setRelatedOrganizations,
      setLoading, setError, clearOrganization]);

  // Keyboard navigation
  useEffect(() => {
    const handleKeyDown = (e) => {
      // Escape key to go back to search
      if (e.key === 'Escape') {
        navigate('/search');
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [navigate]);

  // Focus management - focus heading after data loads
  useEffect(() => {
    if (headingRef.current && !orgLoading && selectedOrganization) {
      headingRef.current.focus();
    }
  }, [orgLoading, selectedOrganization]);

  // Validate organization exists
  const isValidOrganization = useMemo(() => {
    // Don't validate if no search performed
    if (results.length === 0) return null;
    return activities && activities.length > 0;
  }, [activities, results.length]);

  // Handle error state
  if (error) {
    return (
      <div className="page-container">
        <div className="page-header">
          <h1>Error Loading Profile</h1>
        </div>
        <div className="page-content">
          <div className="dashboard-card">
            <h3>Something went wrong</h3>
            <p>{error}</p>
            <button onClick={() => navigate('/search')} className="btn">
              Return to Search
            </button>
          </div>
        </div>
      </div>
    );
  }

  // Early return for no data
  if (results.length === 0 && !orgLoading) {
    return (
      <div className="page-container">
        <div className="page-header">
          <button
            onClick={() => navigate('/search')}
            className="btn btn-secondary"
            style={{ marginBottom: '16px' }}
          >
            ← Back to Search
          </button>
          <h1>{decodedOrgName}</h1>
        </div>
        <div className="page-content">
          <div className="dashboard-card">
            <h3>No Data Available</h3>
            <p>
              Please perform a search first to view organization data.
            </p>
            <button
              onClick={() => navigate('/search')}
              className="btn"
              style={{ marginTop: '16px' }}
            >
              Go to Search
            </button>
          </div>
        </div>
      </div>
    );
  }

  // Handle invalid organization
  if (isValidOrganization === false) {
    return (
      <div className="page-container">
        <div className="breadcrumb">
          <span className="breadcrumb-link" onClick={() => navigate('/')}>
            Home
          </span>
          <span className="breadcrumb-separator">/</span>
          <span className="breadcrumb-link" onClick={() => navigate('/search')}>
            Search
          </span>
          <span className="breadcrumb-separator">/</span>
          <span className="breadcrumb-current">{decodedOrgName}</span>
        </div>
        <div className="page-header">
          <h1>Organization Not Found</h1>
        </div>
        <div className="page-content">
          <div className="dashboard-card">
            <h3>No Data Found</h3>
            <p>
              The organization "{decodedOrgName}" was not found in the current search results.
            </p>
            <p style={{ marginTop: '16px', color: '#666' }}>
              This could mean:
            </p>
            <ul style={{ textAlign: 'left', color: '#666' }}>
              <li>The organization name is misspelled</li>
              <li>No search has been performed yet</li>
              <li>The organization is not in the current search results</li>
            </ul>
            <button
              onClick={() => navigate('/search')}
              className="btn"
              style={{ marginTop: '16px' }}
            >
              Return to Search
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="page-container" role="main" aria-label={`Organization profile for ${decodedOrgName}`}>
      <a href="#main-content" className="skip-link">
        Skip to main content
      </a>
      <nav className="breadcrumb" aria-label="Breadcrumb navigation">
        <span
          className="breadcrumb-link"
          onClick={() => navigate('/')}
          role="link"
          tabIndex={0}
          onKeyPress={(e) => { if (e.key === 'Enter') navigate('/'); }}
          aria-label="Navigate to home page"
        >
          Home
        </span>
        <span className="breadcrumb-separator" aria-hidden="true">/</span>
        <span
          className="breadcrumb-link"
          onClick={() => navigate('/search')}
          role="link"
          tabIndex={0}
          onKeyPress={(e) => { if (e.key === 'Enter') navigate('/search'); }}
          aria-label="Navigate to search page"
        >
          Search
        </span>
        <span className="breadcrumb-separator" aria-hidden="true">/</span>
        <span className="breadcrumb-current" aria-current="page">{decodedOrgName}</span>
      </nav>

      <div className="page-header">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: '16px' }}>
          <div style={{ flex: '1', minWidth: '250px' }}>
            <button
              onClick={() => navigate('/search')}
              className="btn btn-secondary"
              style={{ marginBottom: '16px' }}
              aria-label="Back to search results (Press Escape as shortcut)"
            >
              ← Back to Search
            </button>
            <h1 ref={headingRef} tabIndex={-1} style={{ outline: 'none' }} id="org-name">{decodedOrgName}</h1>
            <p className="page-description">
              {activities?.length || 0} lobbying {activities?.length === 1 ? 'activity' : 'activities'} found
            </p>
          </div>
          <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
            <button
              onClick={handleExportCSV}
              className="btn btn-secondary"
              aria-label={`Export ${decodedOrgName} summary as CSV file`}
              title="Export summary as CSV"
            >
              📊 Export CSV
            </button>
            <button
              onClick={handleExportJSON}
              className="btn btn-secondary"
              aria-label={`Export complete ${decodedOrgName} profile as JSON file`}
              title="Export complete profile as JSON"
            >
              📁 Export JSON
            </button>
          </div>
        </div>
      </div>

      <div className="page-content" id="main-content" aria-live="polite" aria-busy={orgLoading}>
        {/* Activity Summary Metrics */}
        <ActivitySummary />

        {/* Spending Trends Chart */}
        <div className="dashboard-card">
          <SpendingTrendsChart />
        </div>

        {/* Two-column layout for lists */}
        <div className="profile-grid">
          <div className="profile-main">
            <ActivityList />
          </div>

          <div className="profile-sidebar">
            <div className="dashboard-card">
              <TopRecipients />
            </div>

            <div className="dashboard-card">
              <LobbyistNetwork />
            </div>

            <div className="dashboard-card">
              <RelatedOrganizations
                onOrganizationClick={(orgName) => {
                  navigate(`/organization/${encodeURIComponent(orgName)}`);
                  window.scrollTo({ top: 0, behavior: 'smooth' });
                }}
              />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
});

export default OrganizationProfile;