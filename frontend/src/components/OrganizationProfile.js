import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { API_ENDPOINTS, apiCall } from '../config/api';

function OrganizationProfile() {
  const { organizationName } = useParams();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [filings, setFilings] = useState([]);
  const [bills, setBills] = useState([]);
  const [spendingData, setSpendingData] = useState([]);
  const [organizationSummary, setOrganizationSummary] = useState(null);
  const [yearlySpending, setYearlySpending] = useState([]);

  // Determine if organization is city or county related
  const isCityOrg = organizationName?.toUpperCase().includes('CITY OF') ||
                    organizationName?.toUpperCase().includes('LEAGUE') && organizationName?.toUpperCase().includes('CITIES');
  const isCountyOrg = organizationName?.toUpperCase().includes('COUNTY') ||
                      organizationName?.toUpperCase().includes('CSAC') ||
                      organizationName?.toUpperCase().includes('ASSOCIATION OF COUNTIES');
  const isGovtOrg = isCityOrg || isCountyOrg;

  useEffect(() => {
    const fetchOrganizationData = async () => {
      try {
        setLoading(true);
        setError(null);

        // Fetch filings AND search data in parallel
        const filingsParams = new URLSearchParams({
          organization: organizationName
        });
        const searchParams = new URLSearchParams({
          q: organizationName,
          limit: 10
        });

        const filingsUrl = `${API_ENDPOINTS.search}?${filingsParams}`;
        const searchUrl = `${API_ENDPOINTS.search}?${searchParams}`;

        console.log('DEBUG: Fetching organization filings from URL:', filingsUrl);
        console.log('DEBUG: Fetching organization summary from URL:', searchUrl);

        const [filingsData, searchData] = await Promise.all([
          apiCall(filingsUrl),
          apiCall(searchUrl)
        ]);

        console.log('Organization profile filings response:', filingsData);
        console.log('Organization profile search response:', searchData);

        if (filingsData.success) {
          // Use all results - API returns all filings for this organization
          const allResults = filingsData.data || [];
          console.log('Total filings:', allResults.length);
          console.log('DEBUG: First filing:', allResults[0]);
          setFilings(allResults);

          // Get summary data from search results (has total_spending)
          let summaryData = null;
          if (searchData.success && searchData.data?.length > 0) {
            // Find exact match for organization name
            summaryData = searchData.data.find(
              r => r.organization_name?.toUpperCase() === organizationName?.toUpperCase()
            ) || searchData.data[0];
            console.log('DEBUG: Found summary data:', summaryData);
          }

          // Calculate organization summary - prefer search data for spending
          if (allResults.length > 0 || summaryData) {
            const firstFiling = allResults[0] || {};
            setOrganizationSummary({
              total_spending: summaryData?.total_spending || 0,
              filing_count: summaryData?.filing_count || allResults.length,
              first_year: summaryData?.first_year || firstFiling.year,
              latest_year: summaryData?.latest_year || firstFiling.year,
              total_lobbying_firms: summaryData?.total_lobbying_firms || 0
            });

            // Calculate yearly spending from filings if available
            const yearMap = {};
            allResults.forEach(filing => {
              if (filing.year && filing.amount) {
                yearMap[filing.year] = (yearMap[filing.year] || 0) + filing.amount;
              }
            });
            const yearlyData = Object.entries(yearMap)
              .map(([year, amount]) => ({ year: parseInt(year), amount }))
              .sort((a, b) => a.year - b.year);
            setYearlySpending(yearlyData);
          }
        } else {
          throw new Error(filingsData.error?.message || 'Failed to load organization data');
        }
      } catch (err) {
        console.error('Organization fetch error:', err);
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    if (organizationName) {
      fetchOrganizationData();
    }
  }, [organizationName]);

  // Pie chart component
  const PieChart = ({ data, dataKey, title }) => {
    const total = data.reduce((sum, item) => sum + item.amount, 0);
    let currentAngle = 0;
    const colors = ['#3b82f6', '#10b981', '#f59e0b', '#8b5cf6', '#ef4444'];

    return (
      <div className="chart-container">
        <h3>{title}</h3>
        <div style={{ display: 'flex', alignItems: 'center', gap: '2rem', padding: '1rem' }}>
          <svg width="200" height="200" viewBox="0 0 200 200">
            {data.map((item, index) => {
              const percentage = (item.amount / total) * 100;
              const angle = (percentage / 100) * 360;
              const startAngle = currentAngle;
              const endAngle = currentAngle + angle;

              // Calculate path
              const x1 = 100 + 80 * Math.cos((Math.PI * startAngle) / 180);
              const y1 = 100 + 80 * Math.sin((Math.PI * startAngle) / 180);
              const x2 = 100 + 80 * Math.cos((Math.PI * endAngle) / 180);
              const y2 = 100 + 80 * Math.sin((Math.PI * endAngle) / 180);
              const largeArc = angle > 180 ? 1 : 0;

              currentAngle += angle;

              return (
                <path
                  key={index}
                  d={`M 100 100 L ${x1} ${y1} A 80 80 0 ${largeArc} 1 ${x2} ${y2} Z`}
                  fill={colors[index % colors.length]}
                  stroke="white"
                  strokeWidth="2"
                />
              );
            })}
          </svg>
          <div style={{ flex: 1 }}>
            {data.map((item, index) => (
              <div key={index} style={{ display: 'flex', alignItems: 'center', marginBottom: '8px' }}>
                <div style={{
                  width: '16px',
                  height: '16px',
                  backgroundColor: colors[index % colors.length],
                  marginRight: '8px',
                  borderRadius: '2px'
                }}></div>
                <div style={{ flex: 1 }}>
                  <div style={{ fontSize: '0.875rem', fontWeight: '500', color: '#374151' }}>
                    {item[dataKey]}
                  </div>
                  <div style={{ fontSize: '0.75rem', color: '#6b7280' }}>
                    ${item.amount.toLocaleString()} ({((item.amount / total) * 100).toFixed(1)}%)
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    );
  };

  if (loading) {
    return (
      <div className="page-container">
        <div className="loading-container">
          <div className="loading-spinner"></div>
          <p>Loading organization profile...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="page-container">
        <div className="page-header">
          <h1>Error</h1>
        </div>
        <div className="error-container">
          <h3>Failed to Load Organization</h3>
          <p>{error}</p>
          <button onClick={() => navigate('/search')} className="btn btn-primary">
            Back to Search
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="page-container">
      <div className="page-header">
        <button
          onClick={() => navigate('/search')}
          className="btn btn-secondary"
          style={{ marginBottom: '1rem' }}
        >
          ← Back to Search
        </button>
        <h1>{organizationName}</h1>
        <p className="page-description">
          Organization profile with {filings.length} filing{filings.length !== 1 ? 's' : ''} found
        </p>
      </div>

      <div className="page-content">
        {/* Organization Type Badge */}
        {isGovtOrg && (
          <div style={{ marginBottom: '1rem' }}>
            <span style={{
              backgroundColor: isCityOrg ? '#d1fae5' : '#ede9fe',
              color: isCityOrg ? '#065f46' : '#6b21a8',
              padding: '6px 16px',
              borderRadius: '20px',
              fontSize: '0.875rem',
              fontWeight: '600'
            }}>
              {isCityOrg ? '🏛️ City Government' : '🏢 County Government'}
            </span>
          </div>
        )}

        {/* Summary Cards */}
        <div className="dashboard-grid" style={{ gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))' }}>
          {/* Total Spent - Prominent KPI for all orgs */}
          <div className="dashboard-card" style={{
            borderTop: '4px solid #059669',
            background: '#ecfdf5'
          }}>
            <h3 style={{ color: '#065f46' }}>💰 Total Spent</h3>
            <div className="kpi-value" style={{ fontSize: '2rem', fontWeight: 'bold', color: '#059669' }}>
              ${organizationSummary?.total_spending
                ? (organizationSummary.total_spending / 1000000).toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 }) + 'M'
                : '0'}
            </div>
            <p style={{ color: '#065f46', fontSize: '0.875rem' }}>Total lobbying expenditures</p>
          </div>

          <div className="dashboard-card">
            <h3>Total Filings</h3>
            <div className="kpi-value" style={{ fontSize: '2rem', fontWeight: 'bold', color: '#1f2937' }}>
              {organizationSummary?.filing_count || filings.length}
            </div>
            <p style={{ color: '#6b7280', fontSize: '0.875rem' }}>Lobbying disclosure filings</p>
          </div>

          <div className="dashboard-card">
            <h3>Active Period</h3>
            <div className="kpi-value" style={{ fontSize: '1.5rem', fontWeight: 'bold', color: '#1f2937' }}>
              {organizationSummary?.first_year || 'N/A'} - {organizationSummary?.latest_year || 'N/A'}
            </div>
            <p style={{ color: '#6b7280', fontSize: '0.875rem' }}>Years with filings</p>
          </div>

          <div className="dashboard-card">
            <h3>Lobbying Firms</h3>
            <div className="kpi-value" style={{ fontSize: '2rem', fontWeight: 'bold', color: '#1f2937' }}>
              {organizationSummary?.total_lobbying_firms || 0}
            </div>
            <p style={{ color: '#6b7280', fontSize: '0.875rem' }}>Firms hired for lobbying</p>
          </div>
        </div>

        {/* Lobbying Efforts - Bill Tracking */}
        <div className="search-results" style={{ marginTop: '2rem' }}>
          <h3>Lobbying Efforts - Bill Tracking</h3>
          <div className="results-list">
            {bills.length === 0 ? (
              <p style={{ textAlign: 'center', color: '#666', padding: '2rem' }}>
                No bill tracking data available for this organization.
              </p>
            ) : (
              bills.map((bill, index) => (
                <div key={index} className="result-item">
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start' }}>
                    <div style={{ flex: 1 }}>
                      <h4 style={{ margin: '0 0 0.5rem 0' }}>
                        {bill.bill_id}: {bill.description}
                      </h4>
                      <p style={{ margin: '0.25rem 0', color: '#6b7280' }}>
                        <strong>Transaction Date:</strong> {bill.date}
                      </p>
                    </div>
                    <span style={{
                      backgroundColor: bill.position === 'Support' ? '#dcfce7' :
                                     bill.position === 'Oppose' ? '#fee2e2' : '#e0e7ff',
                      color: bill.position === 'Support' ? '#166534' :
                             bill.position === 'Oppose' ? '#991b1b' : '#3730a3',
                      padding: '4px 12px',
                      borderRadius: '12px',
                      fontSize: '0.75rem',
                      fontWeight: '600',
                      whiteSpace: 'nowrap'
                    }}>
                      {bill.position}
                    </span>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>

        {/* Spending Analysis - Pie Charts */}
        {spendingData.length > 0 && (
          <div style={{ marginTop: '2rem' }}>
            <h3 style={{ marginBottom: '1rem' }}>Spending Analysis</h3>
            <div className="dashboard-grid" style={{ gridTemplateColumns: 'repeat(auto-fit, minmax(400px, 1fr))' }}>
              <PieChart
                data={spendingData}
                dataKey="category"
                title="Spending by Category"
              />
              <PieChart
                data={spendingData}
                dataKey="recipient"
                title="Spending by Recipient"
              />
            </div>
          </div>
        )}

        {/* Filings List */}
        <div className="search-results" style={{ marginTop: '2rem' }}>
          <h3>All Filings</h3>
          <div className="results-list">
            {filings.length === 0 ? (
              <p style={{ textAlign: 'center', color: '#666', padding: '2rem' }}>
                No filings found for this organization.
              </p>
            ) : (
              filings.map((filing, index) => (
                <div key={filing.filing_id || index} className="result-item">
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start' }}>
                    <div>
                      <h4 style={{ margin: '0 0 0.5rem 0' }}>
                        Filing ID: {filing.filing_id}
                      </h4>
                      <p style={{ margin: '0.25rem 0' }}>
                        <strong>Filer ID:</strong> {filing.filer_id}
                      </p>
                      <p style={{ margin: '0.25rem 0' }}>
                        <strong>Year:</strong> {filing.year || 'N/A'} |{' '}
                        <strong>Period:</strong> {filing.period || 'N/A'}
                      </p>
                      {filing.filing_date && (
                        <p style={{ margin: '0.25rem 0' }}>
                          <strong>Date:</strong> {filing.filing_date}
                        </p>
                      )}
                      {filing.amount && (
                        <p style={{ margin: '0.25rem 0' }}>
                          <strong>Amount:</strong> ${filing.amount.toLocaleString()}
                        </p>
                      )}
                    </div>
                    <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-end', gap: '4px' }}>
                      <span style={{
                        backgroundColor: '#e3f2fd',
                        color: '#1565c0',
                        padding: '4px 12px',
                        borderRadius: '12px',
                        fontSize: '0.75rem',
                        fontWeight: '600'
                      }}>
                        {filing.year || 'N/A'}
                      </span>
                      {filing.amount && (
                        <span style={{
                          backgroundColor: '#ecfdf5',
                          color: '#059669',
                          padding: '4px 12px',
                          borderRadius: '12px',
                          fontSize: '0.875rem',
                          fontWeight: '600'
                        }}>
                          ${(filing.amount / 1000).toFixed(1)}K
                        </span>
                      )}
                    </div>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

export default OrganizationProfile;
