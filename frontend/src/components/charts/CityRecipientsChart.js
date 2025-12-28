import React, { useEffect, useState } from 'react';
import { API_ENDPOINTS, apiCall } from '../../config/api';
import './charts.css';

function CityRecipientsChart() {
  const [recipientsData, setRecipientsData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchCityRecipients = async () => {
      try {
        setLoading(true);
        const response = await apiCall(`${API_ENDPOINTS.analytics}?type=top_city_recipients`);

        if (response.success) {
          setRecipientsData(response.data || []);
          setError(null);
        } else {
          throw new Error('Failed to fetch city recipients data');
        }
      } catch (err) {
        console.error('City recipients fetch error:', err);
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    fetchCityRecipients();
  }, []);

  if (loading) {
    return (
      <div className="chart-container">
        <h3>Top 10 Recipients of City Lobbying Money</h3>
        <div className="chart-loading">Loading recipient data...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="chart-container">
        <h3>Top 10 Recipients of City Lobbying Money</h3>
        <div className="chart-error">Error loading recipient data: {error}</div>
      </div>
    );
  }

  // Find max value for scaling bars
  const maxAmount = Math.max(...recipientsData.map(d => d.total_amount || 0));

  return (
    <div className="chart-container">
      <h3>Top 10 Recipients of City Lobbying Money</h3>
      <p style={{ color: '#6b7280', fontSize: '0.875rem', marginTop: '8px', marginBottom: '16px' }}>
        Lobbying firms and consultants that received the most money from city governments (last 3 years)
      </p>
      <div className="chart-content" style={{ padding: '1rem' }}>
        {recipientsData.length === 0 ? (
          <p style={{ textAlign: 'center', color: '#666' }}>No city recipients data available</p>
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
                    color: '#065f46',
                    fontWeight: '600'
                  }}>
                    ${(recipient.total_amount / 1000000).toFixed(2)}M
                  </div>
                </div>
                <div style={{ height: '8px', backgroundColor: '#e5e7eb', borderRadius: '4px', overflow: 'hidden' }}>
                  <div style={{
                    width: `${(recipient.total_amount / maxAmount) * 100}%`,
                    height: '100%',
                    backgroundColor: '#10b981',
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

export default CityRecipientsChart;
