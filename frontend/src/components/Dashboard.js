import React, { useEffect, useState } from 'react';
import { useUser } from '@clerk/clerk-react';
import { useUserStore } from '../stores';
import { API_ENDPOINTS, apiCall } from '../config/api';
import { TopOrganizationsChart, SpendingLineChart, CityRecipientsChart, CountyRecipientsChart } from './charts';
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
  const [showExplanation, setShowExplanation] = useState(false);

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
      <div className="page-content">
        {/* Row 1: Total Spending + County Spending (Largest) */}
        <div className="dashboard-grid" style={{ gridTemplateColumns: 'repeat(4, 1fr)', gap: '16px' }}>
          {/* Total Lobbying Expenditures */}
          <div className="dashboard-card" style={{
            borderTop: '4px solid #2563eb',
            borderLeft: '3px solid #64748b',
            position: 'relative',
            padding: '16px'
          }}>
            <span style={{
              position: 'absolute',
              top: '12px',
              right: '12px',
              padding: '3px 8px',
              borderRadius: '10px',
              fontSize: '0.65rem',
              fontWeight: '600',
              background: '#dbeafe',
              color: '#1e40af'
            }}>{currentYear}</span>
            <div className="kpi-header" style={{ paddingRight: '60px', marginBottom: '8px' }}>
              <span className="kpi-icon" style={{ fontSize: '1.25rem' }}>💰</span>
              <h3 style={{ fontSize: '0.875rem' }}>Total Spending</h3>
            </div>
            <div className="kpi-value" style={{ fontSize: '1.5rem', fontWeight: 'bold', color: '#1f2937', margin: '8px 0' }}>
              ${(kpis.totalSpending / 1000000).toLocaleString('en-US', { minimumFractionDigits: 1, maximumFractionDigits: 1 })}M
            </div>
            <p style={{ color: '#6b7280', fontSize: '0.75rem' }}>All Lobbying {currentYear}</p>
          </div>

          {/* County Other Lobbying Spending */}
          <div className="dashboard-card" style={{
            borderTop: '4px solid #8b5cf6',
            borderLeft: '3px solid #8b5cf6',
            position: 'relative',
            padding: '16px',
            background: '#faf5ff'
          }}>
            <span style={{
              position: 'absolute',
              top: '12px',
              right: '12px',
              padding: '3px 8px',
              borderRadius: '10px',
              fontSize: '0.65rem',
              fontWeight: '600',
              background: '#ede9fe',
              color: '#6b21a8'
            }}>{currentYear}</span>
            <div className="kpi-header" style={{ paddingRight: '60px', marginBottom: '8px' }}>
              <span className="kpi-icon" style={{ fontSize: '1.25rem' }}>🏢</span>
              <h3 style={{ fontSize: '0.875rem' }}>County Other Lobbying</h3>
            </div>
            <div className="kpi-value" style={{ fontSize: '1.5rem', fontWeight: 'bold', color: '#6b21a8', margin: '8px 0' }}>
              ${(kpis.countyOtherLobbying / 1000000).toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}M
            </div>
            <p style={{ color: '#7c3aed', fontSize: '0.75rem' }}>County Direct Lobbying</p>
          </div>

          {/* County Membership Spending */}
          <div className="dashboard-card" style={{
            borderTop: '4px solid #a855f7',
            borderLeft: '3px solid #8b5cf6',
            position: 'relative',
            padding: '16px',
            background: '#faf5ff'
          }}>
            <span style={{
              position: 'absolute',
              top: '12px',
              right: '12px',
              padding: '3px 8px',
              borderRadius: '10px',
              fontSize: '0.65rem',
              fontWeight: '600',
              background: '#ede9fe',
              color: '#6b21a8'
            }}>{currentYear}</span>
            <div className="kpi-header" style={{ paddingRight: '60px', marginBottom: '8px' }}>
              <span className="kpi-icon" style={{ fontSize: '1.25rem' }}>🎫</span>
              <h3 style={{ fontSize: '0.875rem' }}>County Membership</h3>
            </div>
            <div className="kpi-value" style={{ fontSize: '1.5rem', fontWeight: 'bold', color: '#6b21a8', margin: '8px 0' }}>
              ${(kpis.countyMembership / 1000000).toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}M
            </div>
            <p style={{ color: '#7c3aed', fontSize: '0.75rem' }}>County Membership Dues</p>
          </div>

          {/* County Count */}
          <div className="dashboard-card" style={{
            borderTop: '4px solid #8b5cf6',
            borderLeft: '3px solid #8b5cf6',
            position: 'relative',
            padding: '16px',
            background: '#faf5ff'
          }}>
            <span style={{
              position: 'absolute',
              top: '12px',
              right: '12px',
              padding: '3px 8px',
              borderRadius: '10px',
              fontSize: '0.65rem',
              fontWeight: '600',
              background: '#ede9fe',
              color: '#6b21a8'
            }}>{currentYear}</span>
            <div className="kpi-header" style={{ paddingRight: '60px', marginBottom: '8px' }}>
              <span className="kpi-icon" style={{ fontSize: '1.25rem' }}>🏢</span>
              <h3 style={{ fontSize: '0.875rem' }}>County Orgs/Depts</h3>
            </div>
            <div className="kpi-value" style={{ fontSize: '1.5rem', fontWeight: 'bold', color: '#6b21a8', margin: '8px 0' }}>
              {kpis.countyCount.toLocaleString()}
            </div>
            <p style={{ color: '#7c3aed', fontSize: '0.75rem' }}>County Entities</p>
          </div>
        </div>

        {/* Row 2: City Spending + Counts (Smaller/More Specific) */}
        <div className="dashboard-grid" style={{ gridTemplateColumns: 'repeat(4, 1fr)', gap: '16px', marginTop: '16px' }}>
          {/* City Other Lobbying Spending */}
          <div className="dashboard-card" style={{
            borderTop: '4px solid #10b981',
            borderLeft: '3px solid #10b981',
            position: 'relative',
            padding: '16px',
            background: '#f0fdf4'
          }}>
            <span style={{
              position: 'absolute',
              top: '12px',
              right: '12px',
              padding: '3px 8px',
              borderRadius: '10px',
              fontSize: '0.65rem',
              fontWeight: '600',
              background: '#d1fae5',
              color: '#065f46'
            }}>{currentYear}</span>
            <div className="kpi-header" style={{ paddingRight: '60px', marginBottom: '8px' }}>
              <span className="kpi-icon" style={{ fontSize: '1.25rem' }}>🏛️</span>
              <h3 style={{ fontSize: '0.875rem' }}>City Other Lobbying</h3>
            </div>
            <div className="kpi-value" style={{ fontSize: '1.5rem', fontWeight: 'bold', color: '#065f46', margin: '8px 0' }}>
              ${(kpis.cityOtherLobbying / 1000000).toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}M
            </div>
            <p style={{ color: '#059669', fontSize: '0.75rem' }}>City Direct Lobbying</p>
          </div>

          {/* City Membership Spending */}
          <div className="dashboard-card" style={{
            borderTop: '4px solid #06b6d4',
            borderLeft: '3px solid #10b981',
            position: 'relative',
            padding: '16px',
            background: '#f0fdf4'
          }}>
            <span style={{
              position: 'absolute',
              top: '12px',
              right: '12px',
              padding: '3px 8px',
              borderRadius: '10px',
              fontSize: '0.65rem',
              fontWeight: '600',
              background: '#d1fae5',
              color: '#065f46'
            }}>{currentYear}</span>
            <div className="kpi-header" style={{ paddingRight: '60px', marginBottom: '8px' }}>
              <span className="kpi-icon" style={{ fontSize: '1.25rem' }}>🎫</span>
              <h3 style={{ fontSize: '0.875rem' }}>City Membership</h3>
            </div>
            <div className="kpi-value" style={{ fontSize: '1.5rem', fontWeight: 'bold', color: '#065f46', margin: '8px 0' }}>
              ${(kpis.cityMembership / 1000000).toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}M
            </div>
            <p style={{ color: '#059669', fontSize: '0.75rem' }}>City Membership Dues</p>
          </div>

          {/* City Count */}
          <div className="dashboard-card" style={{
            borderTop: '4px solid #10b981',
            borderLeft: '3px solid #10b981',
            position: 'relative',
            padding: '16px',
            background: '#f0fdf4'
          }}>
            <span style={{
              position: 'absolute',
              top: '12px',
              right: '12px',
              padding: '3px 8px',
              borderRadius: '10px',
              fontSize: '0.65rem',
              fontWeight: '600',
              background: '#d1fae5',
              color: '#065f46'
            }}>{currentYear}</span>
            <div className="kpi-header" style={{ paddingRight: '60px', marginBottom: '8px' }}>
              <span className="kpi-icon" style={{ fontSize: '1.25rem' }}>🏛️</span>
              <h3 style={{ fontSize: '0.875rem' }}>City Orgs/Depts</h3>
            </div>
            <div className="kpi-value" style={{ fontSize: '1.5rem', fontWeight: 'bold', color: '#065f46', margin: '8px 0' }}>
              {kpis.cityCount.toLocaleString()}
            </div>
            <p style={{ color: '#059669', fontSize: '0.75rem' }}>City Entities</p>
          </div>

          {/* Spacer to maintain 4-column grid */}
          <div style={{ visibility: 'hidden' }}></div>
        </div>

        {/* KPI Explanation Table - Collapsible */}
        <div style={{
          background: 'white',
          borderRadius: '8px',
          marginTop: '32px',
          boxShadow: '0 1px 3px rgba(0,0,0,0.1)',
          border: '1px solid #e5e7eb',
          overflow: 'hidden'
        }}>
          <button
            onClick={() => setShowExplanation(!showExplanation)}
            style={{
              width: '100%',
              padding: '20px 24px',
              background: 'transparent',
              border: 'none',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              transition: 'background-color 0.2s'
            }}
            onMouseEnter={(e) => e.currentTarget.style.backgroundColor = '#f9fafb'}
            onMouseLeave={(e) => e.currentTarget.style.backgroundColor = 'transparent'}
            aria-expanded={showExplanation}
            aria-controls="metrics-explanation"
          >
            <h3 style={{ color: '#1f2937', fontSize: '1.25rem', margin: 0, fontWeight: '600' }}>
              Understanding the Dashboard Metrics
            </h3>
            <svg
              style={{
                width: '20px',
                height: '20px',
                transform: showExplanation ? 'rotate(180deg)' : 'rotate(0deg)',
                transition: 'transform 0.2s'
              }}
              fill="none"
              stroke="#6b7280"
              viewBox="0 0 24 24"
              xmlns="http://www.w3.org/2000/svg"
            >
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
            </svg>
          </button>

          {showExplanation && (
            <div
              id="metrics-explanation"
              style={{
                padding: '0 24px 24px 24px',
                animation: 'slideDown 0.3s ease-out'
              }}
            >
              <div style={{ overflowX: 'auto' }}>
                <table style={{
                  width: '100%',
                  borderCollapse: 'collapse',
                  fontSize: '0.875rem'
                }}>
                  <thead>
                    <tr style={{ borderBottom: '2px solid #e5e7eb', background: '#f9fafb' }}>
                      <th style={{ padding: '12px', textAlign: 'left', fontWeight: '600', color: '#374151' }}>KPI Name</th>
                      <th style={{ padding: '12px', textAlign: 'left', fontWeight: '600', color: '#374151' }}>What It Measures</th>
                      <th style={{ padding: '12px', textAlign: 'left', fontWeight: '600', color: '#374151' }}>Time Period</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr style={{ borderBottom: '1px solid #e5e7eb' }}>
                      <td style={{ padding: '12px', color: '#1f2937', fontWeight: '500' }}>Total Spending</td>
                      <td style={{ padding: '12px', color: '#4b5563' }}>The total amount spent on all lobbying activities across California</td>
                      <td style={{ padding: '12px', color: '#4b5563' }}>{currentYear} only</td>
                    </tr>
                    <tr style={{ borderBottom: '1px solid #e5e7eb', background: '#faf5ff' }}>
                      <td style={{ padding: '12px', color: '#6b21a8', fontWeight: '500' }}>County Other Lobbying</td>
                      <td style={{ padding: '12px', color: '#4b5563' }}>Total spent by county governments on direct lobbying activities (not membership dues)</td>
                      <td style={{ padding: '12px', color: '#4b5563' }}>{currentYear} only</td>
                    </tr>
                    <tr style={{ borderBottom: '1px solid #e5e7eb', background: '#faf5ff' }}>
                      <td style={{ padding: '12px', color: '#6b21a8', fontWeight: '500' }}>County Membership</td>
                      <td style={{ padding: '12px', color: '#4b5563' }}>Total spent by county governments on membership dues to lobbying organizations like CSAC</td>
                      <td style={{ padding: '12px', color: '#4b5563' }}>{currentYear} only</td>
                    </tr>
                    <tr style={{ borderBottom: '1px solid #e5e7eb', background: '#faf5ff' }}>
                      <td style={{ padding: '12px', color: '#6b21a8', fontWeight: '500' }}>County Organizations/Departments</td>
                      <td style={{ padding: '12px', color: '#4b5563' }}>Number of county government organizations and departments that filed lobbying reports</td>
                      <td style={{ padding: '12px', color: '#4b5563' }}>{currentYear} only</td>
                    </tr>
                    <tr style={{ borderBottom: '1px solid #e5e7eb', background: '#f0fdf4' }}>
                      <td style={{ padding: '12px', color: '#065f46', fontWeight: '500' }}>City Other Lobbying</td>
                      <td style={{ padding: '12px', color: '#4b5563' }}>Total spent by city governments on direct lobbying activities (not membership dues)</td>
                      <td style={{ padding: '12px', color: '#4b5563' }}>{currentYear} only</td>
                    </tr>
                    <tr style={{ borderBottom: '1px solid #e5e7eb', background: '#f0fdf4' }}>
                      <td style={{ padding: '12px', color: '#065f46', fontWeight: '500' }}>City Membership</td>
                      <td style={{ padding: '12px', color: '#4b5563' }}>Total spent by city governments on membership dues to lobbying organizations like League of California Cities</td>
                      <td style={{ padding: '12px', color: '#4b5563' }}>{currentYear} only</td>
                    </tr>
                    <tr style={{ background: '#f0fdf4' }}>
                      <td style={{ padding: '12px', color: '#065f46', fontWeight: '500' }}>City Organizations/Departments</td>
                      <td style={{ padding: '12px', color: '#4b5563' }}>Number of city government organizations and departments that filed lobbying reports</td>
                      <td style={{ padding: '12px', color: '#4b5563' }}>{currentYear} only</td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
          )}
        </div>

        {/* Charts Section - Live California Data */}
        <div className="dashboard-grid" style={{ marginTop: '2rem', gridTemplateColumns: 'repeat(auto-fit, minmax(500px, 1fr))' }}>
          <SpendingLineChart />
          <TopOrganizationsChart />
        </div>

        {/* Government Money Recipients - City vs County */}
        <div className="dashboard-grid" style={{ marginTop: '2rem', gridTemplateColumns: 'repeat(auto-fit, minmax(500px, 1fr))' }}>
          <CityRecipientsChart />
          <CountyRecipientsChart />
        </div>
      </div>
    </div>
  );
}

export default Dashboard;
