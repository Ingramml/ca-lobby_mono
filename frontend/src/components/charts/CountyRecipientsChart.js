import React, { useEffect, useState } from 'react';
import { API_ENDPOINTS, apiCall } from '../../config/api';
import './charts.css';

function CountyRecipientsChart() {
  const [recipientsData, setRecipientsData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchCountyRecipients = async () => {
      try {
        setLoading(true);
        const response = await apiCall(`${API_ENDPOINTS.analytics}?type=top_county_recipients`);

        if (response.success) {
          setRecipientsData(response.data || []);
          setError(null);
        } else {
          throw new Error('Failed to fetch county recipients data');
        }
      } catch (err) {
        console.error('County recipients fetch error:', err);
        setError('Unable to load data. Please refresh.');
      } finally {
        setLoading(false);
      }
    };

    fetchCountyRecipients();
  }, []);

  if (loading) {
    return (
      <div className="chart-container">
        <h3>Top 10 Counties by Lobbying Spending</h3>
        <div className="chart-loading">Loading county spending data...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="chart-container">
        <h3>Top 10 Counties by Lobbying Spending</h3>
        <div className="chart-error">{error}</div>
      </div>
    );
  }

  // Find max value for scaling bars
  const maxAmount = Math.max(...recipientsData.map(d => d.total_amount || 0));

  return (
    <div className="chart-container">
      <h3>Top 10 Counties by Lobbying Spending</h3>
      <p style={{ color: '#6b7280', fontSize: '0.875rem', marginTop: '8px', marginBottom: '16px' }}>
        County governments with the highest lobbying expenditures
      </p>
      <div className="chart-content" style={{ padding: '1rem' }}>
        {recipientsData.length === 0 ? (
          <p style={{ textAlign: 'center', color: '#666' }}>No county recipients data available</p>
        ) : (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
            {recipientsData.map((recipient, index) => (
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
                    {index + 1}. {recipient.recipient_name || 'Unknown'}
                  </div>
                  <div style={{
                    fontSize: '0.875rem',
                    color: '#6b21a8',
                    fontWeight: '600'
                  }}>
                    ${(recipient.total_amount / 1000000).toFixed(2)}M
                  </div>
                </div>
                <div style={{ height: '8px', backgroundColor: '#e5e7eb', borderRadius: '4px', overflow: 'hidden' }}>
                  <div style={{
                    width: `${(recipient.total_amount / maxAmount) * 100}%`,
                    height: '100%',
                    backgroundColor: '#8b5cf6',
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

export default CountyRecipientsChart;
