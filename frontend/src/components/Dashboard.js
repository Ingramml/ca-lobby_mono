import React, { useEffect, useState } from 'react';
import { useUser } from '@clerk/clerk-react';
import { useUserStore } from '../stores';
import { API_ENDPOINTS, apiCall } from '../config/api';
import { TopOrganizationsChart, SpendingLineChart } from './charts';
import './charts/charts.css';

function Dashboard() {
  const { user, isLoaded: userLoaded } = useUser();
  const [dashboardLoading, setDashboardLoading] = useState(true);
  const [dashboardError, setDashboardError] = useState(null);
  const [analyticsData, setAnalyticsData] = useState(null);

  // Connect to Zustand stores
  const { syncWithClerk } = useUserStore();

  // Sync user data with Clerk when user changes
  useEffect(() => {
    if (userLoaded) {
      try {
        syncWithClerk(user);
        setDashboardError(null);
      } catch (error) {
        console.error('Dashboard sync error:', error);
        setDashboardError('Failed to sync user data');
      }
    }
  }, [user, userLoaded, syncWithClerk]);

  // State for spending data
  const [spendingData, setSpendingData] = useState(null);
  const [spendingBreakdown, setSpendingBreakdown] = useState(null);

  // Fetch analytics data from API
  useEffect(() => {
    const fetchAnalytics = async () => {
      try {
        setDashboardLoading(true);

        // Fetch summary analytics, spending data, and spending breakdown
        const [summaryData, spendingResponse, breakdownResponse] = await Promise.all([
          apiCall(`${API_ENDPOINTS.analytics}?type=summary`),
          apiCall(`${API_ENDPOINTS.analytics}?type=spending`),
          apiCall(`${API_ENDPOINTS.analytics}?type=spending_breakdown`)
        ]);

        if (summaryData.success) {
          setAnalyticsData(summaryData.data);
          setDashboardError(null);
        } else {
          throw new Error('Failed to fetch analytics');
        }

        if (spendingResponse.success) {
          setSpendingData(spendingResponse.data);
        }

        if (breakdownResponse.success) {
          setSpendingBreakdown(breakdownResponse.data);
        }
      } catch (error) {
        console.error('Analytics fetch error:', error);
        setDashboardError(`Failed to load dashboard data: ${error.message}`);
      } finally {
        setDashboardLoading(false);
      }
    };

    if (userLoaded) {
      fetchAnalytics();
    }
  }, [userLoaded]);

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
        <div className="page-header">
          <h1>Dashboard</h1>
        </div>
        <div className="error-container">
          <h3>Error Loading Dashboard</h3>
          <p>{dashboardError}</p>
          <button
            onClick={() => window.location.reload()}
            className="btn btn-primary"
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  const currentYear = new Date().getFullYear();

  // Calculate KPI metrics from spending data
  const calculateKPIs = () => {
    const baseKpis = {
      totalSpending: 0,
      cityCount: 0,
      countyCount: 0,
      cityMembership: 0,
      cityOtherLobbying: 0,
      countyMembership: 0,
      countyOtherLobbying: 0
    };

    if (spendingData && spendingData.length > 0) {
      // Get latest year's data
      const latestYear = spendingData[spendingData.length - 1];
      baseKpis.totalSpending = latestYear?.total_spending || 0;
      baseKpis.cityCount = latestYear?.city_count || 0;
      baseKpis.countyCount = latestYear?.county_count || 0;
    }

    // Add breakdown data
    if (spendingBreakdown && spendingBreakdown.length > 0) {
      spendingBreakdown.forEach(item => {
        if (item.govt_type === 'city' && item.spending_category === 'membership') {
          baseKpis.cityMembership = item.total_amount || 0;
        } else if (item.govt_type === 'city' && item.spending_category === 'other_lobbying') {
          baseKpis.cityOtherLobbying = item.total_amount || 0;
        } else if (item.govt_type === 'county' && item.spending_category === 'membership') {
          baseKpis.countyMembership = item.total_amount || 0;
        } else if (item.govt_type === 'county' && item.spending_category === 'other_lobbying') {
          baseKpis.countyOtherLobbying = item.total_amount || 0;
        }
      });
    }

    return baseKpis;
  };

  const kpis = calculateKPIs();

  return (
    <div className="page-container">
      <div className="page-header">
        <h1>California Lobbying Dashboard</h1>
        <p className="page-description">
          Overview of California state lobbying activity and key metrics
        </p>
      </div>

      <div className="page-content">
        {/* KPI Cards - Updated to match specification */}
        <div className="dashboard-grid" style={{ gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))' }}>
          {/* Total Lobbying Expenditures */}
          <div className="dashboard-card" style={{ borderTop: '4px solid #2563eb' }}>
            <div className="kpi-header">
              <span className="kpi-icon">💰</span>
              <h3>Total Lobbying Expenditures</h3>
            </div>
            <div className="kpi-value" style={{ fontSize: '2rem', fontWeight: 'bold', color: '#1f2937', margin: '1rem 0' }}>
              ${(kpis.totalSpending / 1000000).toFixed(1)}M
            </div>
            <p style={{ color: '#6b7280', fontSize: '0.875rem' }}>Actual {currentYear} Spending</p>
          </div>

          {/* City Government Lobbying */}
          <div className="dashboard-card" style={{ borderTop: '4px solid #10b981' }}>
            <div className="kpi-header">
              <span className="kpi-icon">🏛️</span>
              <h3>City Government Lobbying</h3>
            </div>
            <div className="kpi-value" style={{ fontSize: '2rem', fontWeight: 'bold', color: '#1f2937', margin: '1rem 0' }}>
              {kpis.cityCount.toLocaleString()}
            </div>
            <p style={{ color: '#6b7280', fontSize: '0.875rem' }}>{kpis.cityCount} California Cities</p>
          </div>

          {/* County Government Lobbying */}
          <div className="dashboard-card" style={{ borderTop: '4px solid #8b5cf6' }}>
            <div className="kpi-header">
              <span className="kpi-icon">🏢</span>
              <h3>County Government Lobbying</h3>
            </div>
            <div className="kpi-value" style={{ fontSize: '2rem', fontWeight: 'bold', color: '#1f2937', margin: '1rem 0' }}>
              {kpis.countyCount.toLocaleString()}
            </div>
            <p style={{ color: '#6b7280', fontSize: '0.875rem' }}>{kpis.countyCount} California Counties</p>
          </div>
        </div>

        {/* Spending Breakdown KPI Cards - New Row */}
        <div className="dashboard-grid" style={{ gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', marginTop: '1.5rem' }}>
          {/* City Membership Spending */}
          <div className="dashboard-card" style={{ borderTop: '4px solid #06b6d4' }}>
            <div className="kpi-header">
              <span className="kpi-icon">🏛️</span>
              <h3>City Membership</h3>
            </div>
            <div className="kpi-value" style={{ fontSize: '1.5rem', fontWeight: 'bold', color: '#1f2937', margin: '1rem 0' }}>
              ${(kpis.cityMembership / 1000000).toFixed(2)}M
            </div>
            <p style={{ color: '#6b7280', fontSize: '0.875rem' }}>City Membership Dues {currentYear}</p>
          </div>

          {/* City Other Lobbying Spending */}
          <div className="dashboard-card" style={{ borderTop: '4px solid #10b981' }}>
            <div className="kpi-header">
              <span className="kpi-icon">💼</span>
              <h3>City Other Lobbying</h3>
            </div>
            <div className="kpi-value" style={{ fontSize: '1.5rem', fontWeight: 'bold', color: '#1f2937', margin: '1rem 0' }}>
              ${(kpis.cityOtherLobbying / 1000000).toFixed(2)}M
            </div>
            <p style={{ color: '#6b7280', fontSize: '0.875rem' }}>City Other Lobbying {currentYear}</p>
          </div>

          {/* County Membership Spending */}
          <div className="dashboard-card" style={{ borderTop: '4px solid #a855f7' }}>
            <div className="kpi-header">
              <span className="kpi-icon">🏢</span>
              <h3>County Membership</h3>
            </div>
            <div className="kpi-value" style={{ fontSize: '1.5rem', fontWeight: 'bold', color: '#1f2937', margin: '1rem 0' }}>
              ${(kpis.countyMembership / 1000000).toFixed(2)}M
            </div>
            <p style={{ color: '#6b7280', fontSize: '0.875rem' }}>County Membership Dues {currentYear}</p>
          </div>

          {/* County Other Lobbying Spending */}
          <div className="dashboard-card" style={{ borderTop: '4px solid #8b5cf6' }}>
            <div className="kpi-header">
              <span className="kpi-icon">📋</span>
              <h3>County Other Lobbying</h3>
            </div>
            <div className="kpi-value" style={{ fontSize: '1.5rem', fontWeight: 'bold', color: '#1f2937', margin: '1rem 0' }}>
              ${(kpis.countyOtherLobbying / 1000000).toFixed(2)}M
            </div>
            <p style={{ color: '#6b7280', fontSize: '0.875rem' }}>County Other Lobbying {currentYear}</p>
          </div>
        </div>

        {/* Charts Section - Live California Data */}
        <div className="dashboard-grid" style={{ marginTop: '2rem', gridTemplateColumns: 'repeat(auto-fit, minmax(500px, 1fr))' }}>
          <SpendingLineChart />
          <TopOrganizationsChart />
        </div>
      </div>
    </div>
  );
}

export default Dashboard;
