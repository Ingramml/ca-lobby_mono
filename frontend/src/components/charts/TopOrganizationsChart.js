import React, { useEffect, useState } from 'react';
import { API_ENDPOINTS, apiCall } from '../../config/api';
import './charts.css';

function TopOrganizationsChart() {
  const [orgsData, setOrgsData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchTopOrgs = async () => {
      try {
        setLoading(true);
        const response = await apiCall(`${API_ENDPOINTS.analytics}?type=top_organizations`);

        if (response.success) {
          setOrgsData(response.data || []);
          setError(null);
        } else {
          throw new Error('Failed to fetch top organizations');
        }
      } catch (err) {
        console.error('Top organizations fetch error:', err);
        setError('Unable to load data. Please refresh.');
      } finally {
        setLoading(false);
      }
    };

    fetchTopOrgs();
  }, []);

  if (loading) {
    return (
      <div className="chart-container">
        <h3>Top 10 Organizations by Filings</h3>
        <div className="chart-loading">Loading organizations data...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="chart-container">
        <h3>Top 10 Organizations by Filings</h3>
        <div className="chart-error">{error}</div>
      </div>
    );
  }

  // Find max value for scaling bars (API returns total_spending, not filing_count)
  const maxSpending = Math.max(...orgsData.map(d => d.total_spending || 0));

  return (
    <div className="chart-container">
      <h3>Top 10 Organizations by Spending</h3>
      <p style={{ color: '#6b7280', fontSize: '0.875rem', marginTop: '8px', marginBottom: '16px' }}>
        Organizations with the highest total lobbying expenditures
      </p>
      <div className="chart-content" style={{ padding: '1rem' }}>
        {orgsData.length === 0 ? (
          <p style={{ textAlign: 'center', color: '#666' }}>No organization data available</p>
        ) : (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
            {orgsData.map((org, index) => (
              <div key={index}>
                <div style={{
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between',
                  marginBottom: '4px',
                  gap: '8px'
                }}>
                  <div style={{
                    fontSize: '0.875rem',
                    color: '#374151',
                    fontWeight: '500',
                    flex: 1
                  }}>
                    {index + 1}. {org.organization_name || 'Unknown'}
                  </div>
                  <div style={{
                    fontSize: '0.875rem',
                    color: '#2563eb',
                    fontWeight: '600'
                  }}>
                    ${(org.total_spending / 1000000).toFixed(2)}M
                  </div>
                </div>
                <div style={{ height: '8px', backgroundColor: '#e5e7eb', borderRadius: '4px', overflow: 'hidden' }}>
                  <div style={{
                    width: `${(org.total_spending / maxSpending) * 100}%`,
                    height: '100%',
                    backgroundColor: '#3b82f6',
                    transition: 'width 0.3s ease'
                  }} />
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

export default TopOrganizationsChart;
