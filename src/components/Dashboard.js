import React, { Suspense, useMemo } from 'react';
import { useUser } from '@clerk/clerk-react';
import { useUserStore } from '../stores';
import { LobbyTrendsChart, OrganizationChart, CategoryChart } from './charts';
import KPICard from './KPICard';
import {
  getTotalYearSpending,
  getCityGovernmentSpending,
  getCountyGovernmentSpending,
  getOrganizationCounts
} from '../utils/kpiCalculations';
import './charts/charts.css';

// Error Boundary component for chart protection
class ChartErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }

  componentDidCatch(error, errorInfo) {
    console.error('Chart error caught by boundary:', error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="chart-container error">
          <h3>Chart Error</h3>
          <div className="chart-error">
            <p>Chart temporarily unavailable</p>
            <button onClick={() => this.setState({ hasError: false, error: null })}>
              Retry
            </button>
          </div>
        </div>
      );
    }
    return this.props.children;
  }
}

function Dashboard() {
  const { user, isLoaded: userLoaded } = useUser();
  const [dashboardLoading, setDashboardLoading] = React.useState(true);
  const [dashboardError, setDashboardError] = React.useState(null);
  const [chartsEnabled, setChartsEnabled] = React.useState(true);

  // Connect to Zustand stores
  const { syncWithClerk } = useUserStore();

  // Calculate KPI values (memoized for performance)
  const currentYear = new Date().getFullYear();
  const kpiData = useMemo(() => ({
    totalYearSpending: getTotalYearSpending(),
    citySpending: getCityGovernmentSpending(),
    countySpending: getCountyGovernmentSpending(),
    counts: getOrganizationCounts()
  }), []);

  // Sync user data with Clerk when user changes
  React.useEffect(() => {
    if (userLoaded) {
      try {
        syncWithClerk(user);
        setDashboardLoading(false);
        setDashboardError(null);
      } catch (error) {
        console.error('Dashboard sync error:', error);
        setDashboardError('Failed to sync user data');
        setDashboardLoading(false);
      }
    }
  }, [user, userLoaded, syncWithClerk]);

  // Handle chart stability
  const handleChartError = React.useCallback((error) => {
    console.error('Chart rendering error:', error);
    setChartsEnabled(false);
    setTimeout(() => setChartsEnabled(true), 2000); // Re-enable after 2 seconds
  }, []);

  // Show loading state while Clerk is loading
  if (!userLoaded || dashboardLoading) {
    return (
      <div className="page-container">
        <div className="loading-container">
          <div className="loading-spinner"></div>
          <p>Loading dashboard...</p>
        </div>
      </div>
    );
  }

  // Show error state if something went wrong
  if (dashboardError) {
    return (
      <div className="page-container">
        <div className="error-container">
          <h2>Dashboard Error</h2>
          <p>{dashboardError}</p>
          <button onClick={() => window.location.reload()} className="btn btn-primary">
            Retry
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="page-container">
      <div className="page-header">
        <h1>California Lobbying Dashboard</h1>
        <p className="page-description">
          Welcome back, {user?.firstName || 'User'}! Year-to-date lobbying expenditure analysis for {currentYear}
        </p>
      </div>

      <div className="page-content">
        {/* KPI Section */}
        <div className="kpi-section">
          <div className="kpi-grid">
            <KPICard
              title="Total Lobbying Expenditures"
              subtitle={`Year-to-Date ${currentYear}`}
              value={kpiData.totalYearSpending}
              icon="💰"
              color="#2563eb"
              isEstimate={true}
            />
            <KPICard
              title="City Government Lobbying"
              subtitle={`${kpiData.counts.cityOrganizations} California ${kpiData.counts.cityOrganizations === 1 ? 'City' : 'Cities'}`}
              value={kpiData.citySpending}
              icon="🏛️"
              color="#10b981"
              isEstimate={true}
            />
            <KPICard
              title="County Government Lobbying"
              subtitle={`${kpiData.counts.countyOrganizations} California ${kpiData.counts.countyOrganizations === 1 ? 'County' : 'Counties'}`}
              value={kpiData.countySpending}
              icon="🏢"
              color="#8b5cf6"
              isEstimate={true}
            />
          </div>
        </div>

        {/* Visualization Section */}
        <div className="dashboard-section">
          <h2>CA Lobby Data Insights</h2>
          {chartsEnabled ? (
            <Suspense fallback={<div className="charts-loading">Loading charts...</div>}>
              {/* Full-width Lobby Trends Chart */}
              <div className="chart-full-width">
                <ChartErrorBoundary>
                  <LobbyTrendsChart onError={handleChartError} />
                </ChartErrorBoundary>
              </div>

              {/* Two-column grid for other charts */}
              <div className="charts-grid">
                <ChartErrorBoundary>
                  <OrganizationChart onError={handleChartError} />
                </ChartErrorBoundary>
                <ChartErrorBoundary>
                  <CategoryChart onError={handleChartError} />
                </ChartErrorBoundary>
              </div>
            </Suspense>
          ) : (
            <div className="charts-disabled">
              <div className="chart-container">
                <h3>Charts Temporarily Disabled</h3>
                <p>Charts are being reloaded due to a display issue.</p>
                <button
                  onClick={() => setChartsEnabled(true)}
                  className="btn btn-primary"
                >
                  Enable Charts
                </button>
              </div>
            </div>
          )}
        </div>

      </div>
    </div>
  );
}

export default Dashboard;