import React, { useEffect, useState } from 'react';
import { API_ENDPOINTS, apiCall } from '../../config/api';
import './charts.css';

function OrgSpendingByGovtChart() {
  const [orgsData, setOrgsData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchOrgSpending = async () => {
      try {
        setLoading(true);
        const response = await apiCall(`${API_ENDPOINTS.analytics}?type=org_spending_by_govt`);

        if (response.success) {
          setOrgsData(response.data || []);
          setError(null);
        } else {
          throw new Error('Failed to fetch organization spending data');
        }
      } catch (err) {
        console.error('Organization spending fetch error:', err);
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    fetchOrgSpending();
  }, []);

  if (loading) {
    return (
      <div className="chart-container">
        <h3>Top 10 Organizations - City vs County Spending</h3>
        <div className="chart-loading">Loading organization spending data...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="chart-container">
        <h3>Top 10 Organizations - City vs County Spending</h3>
        <div className="chart-error">Error loading organization spending: {error}</div>
      </div>
    );
  }

  // Find max value for scaling bars
  const maxSpending = Math.max(...orgsData.map(d => d.total_spending || 0));

  return (
    <div className="chart-container">
      <h3>Top 10 Organizations - City vs County Spending</h3>
      <div className="chart-content" style={{ padding: '1rem' }}>
        {orgsData.length === 0 ? (
          <p style={{ textAlign: 'center', color: '#666' }}>No organization spending data available</p>
        ) : (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
            {orgsData.map((org, index) => {
              const cityPercent = (org.city_spending / org.total_spending) * 100;
              const countyPercent = (org.county_spending / org.total_spending) * 100;

              return (
                <div key={index}>
                  <div style={{
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'space-between',
                    marginBottom: '6px',
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
                      color: '#6b7280',
                      fontWeight: '600'
                    }}>
                      ${(org.total_spending / 1000000).toFixed(2)}M
                    </div>
                  </div>

                  {/* Stacked Bar */}
                  <div style={{
                    height: '24px',
                    backgroundColor: '#e5e7eb',
                    borderRadius: '4px',
                    overflow: 'hidden',
                    display: 'flex',
                    width: `${(org.total_spending / maxSpending) * 100}%`,
                    minWidth: '50px'
                  }}>
                    {/* City portion (green) */}
                    {org.city_spending > 0 && (
                      <div
                        style={{
                          width: `${cityPercent}%`,
                          height: '100%',
                          backgroundColor: '#10b981',
                          transition: 'width 0.3s ease',
                          display: 'flex',
                          alignItems: 'center',
                          justifyContent: 'center'
                        }}
                        title={`City: $${(org.city_spending / 1000000).toFixed(2)}M`}
                      >
                        {cityPercent > 15 && (
                          <span style={{
                            fontSize: '0.7rem',
                            color: 'white',
                            fontWeight: '600'
                          }}>
                            City
                          </span>
                        )}
                      </div>
                    )}

                    {/* County portion (purple) */}
                    {org.county_spending > 0 && (
                      <div
                        style={{
                          width: `${countyPercent}%`,
                          height: '100%',
                          backgroundColor: '#8b5cf6',
                          transition: 'width 0.3s ease',
                          display: 'flex',
                          alignItems: 'center',
                          justifyContent: 'center'
                        }}
                        title={`County: $${(org.county_spending / 1000000).toFixed(2)}M`}
                      >
                        {countyPercent > 15 && (
                          <span style={{
                            fontSize: '0.7rem',
                            color: 'white',
                            fontWeight: '600'
                          }}>
                            County
                          </span>
                        )}
                      </div>
                    )}
                  </div>

                  {/* Breakdown details */}
                  <div style={{
                    display: 'flex',
                    gap: '12px',
                    marginTop: '4px',
                    fontSize: '0.75rem'
                  }}>
                    {org.city_spending > 0 && (
                      <div style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
                        <div style={{
                          width: '12px',
                          height: '12px',
                          backgroundColor: '#10b981',
                          borderRadius: '2px'
                        }} />
                        <span style={{ color: '#065f46' }}>
                          City: ${(org.city_spending / 1000000).toFixed(2)}M
                        </span>
                      </div>
                    )}
                    {org.county_spending > 0 && (
                      <div style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
                        <div style={{
                          width: '12px',
                          height: '12px',
                          backgroundColor: '#8b5cf6',
                          borderRadius: '2px'
                        }} />
                        <span style={{ color: '#6b21a8' }}>
                          County: ${(org.county_spending / 1000000).toFixed(2)}M
                        </span>
                      </div>
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
}

export default OrgSpendingByGovtChart;
