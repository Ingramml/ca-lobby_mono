import React, { useEffect, useState } from 'react';
import { API_ENDPOINTS, apiCall } from '../../config/api';
import './charts.css';

function TrendsChart() {
  const [trendsData, setTrendsData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchTrends = async () => {
      try {
        setLoading(true);
        const response = await apiCall(`${API_ENDPOINTS.analytics}?type=trends`);

        if (response.success) {
          setTrendsData(response.data || []);
          setError(null);
        } else {
          throw new Error('Failed to fetch trends');
        }
      } catch (err) {
        console.error('Trends fetch error:', err);
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    fetchTrends();
  }, []);

  if (loading) {
    return (
      <div className="chart-container">
        <h3>Filing Trends (2020-Present)</h3>
        <div className="chart-loading">Loading trends data...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="chart-container">
        <h3>Filing Trends (2020-Present)</h3>
        <div className="chart-error">Error loading trends: {error}</div>
      </div>
    );
  }

  // Find max value for scaling bars
  const maxCount = Math.max(...trendsData.map(d => d.filing_count || 0));

  return (
    <div className="chart-container">
      <h3>Filing Trends (2020-Present)</h3>
      <div className="chart-content" style={{ padding: '1rem' }}>
        {trendsData.length === 0 ? (
          <p style={{ textAlign: 'center', color: '#666' }}>No trend data available</p>
        ) : (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
            {trendsData.map((item, index) => (
              <div key={index} style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                <div style={{
                  minWidth: '120px',
                  fontSize: '0.875rem',
                  color: '#374151',
                  fontWeight: '500'
                }}>
                  {item.year} - {item.period?.substring(0, 10) || 'Unknown'}
                </div>
                <div style={{ flex: 1, height: '24px', position: 'relative' }}>
                  <div style={{
                    width: `${(item.filing_count / maxCount) * 100}%`,
                    height: '100%',
                    backgroundColor: '#3b82f6',
                    borderRadius: '4px',
                    transition: 'width 0.3s ease'
                  }} />
                </div>
                <div style={{
                  minWidth: '80px',
                  textAlign: 'right',
                  fontSize: '0.875rem',
                  color: '#6b7280',
                  fontWeight: '600'
                }}>
                  {item.filing_count?.toLocaleString() || 0}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

export default TrendsChart;
