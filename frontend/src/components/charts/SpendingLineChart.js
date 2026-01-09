import React, { useEffect, useState } from 'react';
import { API_ENDPOINTS, apiCall } from '../../config/api';
import './charts.css';

function SpendingLineChart() {
  const [spendingData, setSpendingData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchSpending = async () => {
      try {
        setLoading(true);
        const response = await apiCall(`${API_ENDPOINTS.analytics}?type=spending`);

        if (response.success) {
          setSpendingData(response.data || []);
          setError(null);
        } else {
          throw new Error('Failed to fetch spending data');
        }
      } catch (err) {
        console.error('Spending fetch error:', err);
        setError('Unable to load data. Please refresh.');
      } finally {
        setLoading(false);
      }
    };

    fetchSpending();
  }, []);

  if (loading) {
    return (
      <div className="chart-container">
        <h3>Lobbying Spending Trends (2015-Present)</h3>
        <div className="chart-loading">Loading spending data...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="chart-container">
        <h3>Lobbying Spending Trends (2015-Present)</h3>
        <div className="chart-error">{error}</div>
      </div>
    );
  }

  if (spendingData.length === 0) {
    return (
      <div className="chart-container">
        <h3>Lobbying Spending Trends (2015-Present)</h3>
        <p style={{ textAlign: 'center', color: '#666', padding: '2rem' }}>No spending data available</p>
      </div>
    );
  }

  // Find max values for dual-axis scaling
  const maxCityCounty = Math.max(
    ...spendingData.map(d => Math.max(
      d.city_spending || 0,
      d.county_spending || 0
    ))
  );

  const maxTotal = Math.max(...spendingData.map(d => d.total_spending || 0));

  // Chart dimensions
  const chartHeight = 300;
  const chartWidth = 600;
  const padding = { top: 20, right: 40, bottom: 40, left: 80 };
  const innerWidth = chartWidth - padding.left - padding.right;
  const innerHeight = chartHeight - padding.top - padding.bottom;

  // Axis break configuration
  const breakGapHeight = 15; // Height of the break indicator
  const lowerSegmentHeight = innerHeight * 0.65; // 65% for city/county data
  const upperSegmentHeight = innerHeight * 0.25; // 25% for total spending

  // Value ranges for each segment
  const lowerMax = maxCityCounty * 1.2; // Lower segment: 0 to max city/county * 1.2
  const upperMin = maxTotal * 0.85; // Upper segment: starts at 85% of max total
  const upperMax = maxTotal * 1.05; // Upper segment: ends at 105% of max total

  // Scale functions with axis break
  const xScale = (index) => padding.left + (index / (spendingData.length - 1)) * innerWidth;

  const yScale = (value) => {
    if (value <= lowerMax) {
      // Lower segment: linear scale from 0 to lowerMax
      const ratio = value / lowerMax;
      return padding.top + lowerSegmentHeight + breakGapHeight + upperSegmentHeight - (ratio * lowerSegmentHeight);
    } else {
      // Upper segment: linear scale from upperMin to upperMax
      const ratio = (value - upperMin) / (upperMax - upperMin);
      return padding.top + upperSegmentHeight - (ratio * upperSegmentHeight);
    }
  };

  // Format currency
  const formatCurrency = (value) => {
    if (value >= 1000000) {
      return `$${(value / 1000000).toFixed(1)}M`;
    } else if (value >= 1000) {
      return `$${(value / 1000).toFixed(0)}K`;
    }
    return `$${value.toFixed(0)}`;
  };

  // Generate line paths with break handling
  const generatePath = (dataKey) => {
    let pathSegments = [];
    let currentSegment = [];

    spendingData.forEach((d, i) => {
      const value = d[dataKey] || 0;
      const x = xScale(i);
      const y = yScale(value);

      // Check if this point should start a new segment (crosses the break)
      if (i > 0) {
        const prevValue = spendingData[i - 1][dataKey] || 0;
        const crossesBreak = (prevValue <= lowerMax && value > lowerMax) ||
                            (prevValue > lowerMax && value <= lowerMax);

        if (crossesBreak) {
          // End current segment and start new one
          if (currentSegment.length > 0) {
            pathSegments.push(currentSegment.join(' '));
          }
          currentSegment = [`M ${x} ${y}`];
        } else {
          currentSegment.push(`L ${x} ${y}`);
        }
      } else {
        currentSegment.push(`M ${x} ${y}`);
      }
    });

    // Add final segment
    if (currentSegment.length > 0) {
      pathSegments.push(currentSegment.join(' '));
    }

    return pathSegments;
  };

  const totalPaths = generatePath('total_spending');
  const cityPaths = generatePath('city_spending');
  const countyPaths = generatePath('county_spending');

  return (
    <div className="chart-container">
      <h3>Lobbying Spending Trends (2015-Present)</h3>
      <div className="chart-content" style={{ padding: '1rem', overflow: 'hidden' }}>
        <svg width="100%" height={chartHeight} viewBox={`0 0 ${chartWidth} ${chartHeight}`} style={{ maxWidth: '100%' }}>
          {/* Lower segment grid lines (city/county data) */}
          {[0, 0.25, 0.5, 0.75, 1].map((factor) => {
            const value = lowerMax * factor;
            const y = yScale(value);
            return (
              <g key={`lower-${factor}`}>
                <line
                  x1={padding.left}
                  y1={y}
                  x2={chartWidth - padding.right}
                  y2={y}
                  stroke="#e5e7eb"
                  strokeWidth="1"
                />
                <text
                  x={padding.left - 10}
                  y={y + 4}
                  textAnchor="end"
                  fontSize="12"
                  fill="#6b7280"
                >
                  {formatCurrency(value)}
                </text>
              </g>
            );
          })}

          {/* Upper segment grid lines (total spending) */}
          {[0, 0.5, 1].map((factor) => {
            const value = upperMin + (upperMax - upperMin) * factor;
            const y = yScale(value);
            return (
              <g key={`upper-${factor}`}>
                <line
                  x1={padding.left}
                  y1={y}
                  x2={chartWidth - padding.right}
                  y2={y}
                  stroke="#e5e7eb"
                  strokeWidth="1"
                />
                <text
                  x={padding.left - 10}
                  y={y + 4}
                  textAnchor="end"
                  fontSize="12"
                  fill="#6b7280"
                >
                  {formatCurrency(value)}
                </text>
              </g>
            );
          })}

          {/* Axis break indicator (zigzag lines) */}
          <g>
            {/* White background for break area */}
            <rect
              x={padding.left}
              y={padding.top + upperSegmentHeight}
              width={innerWidth}
              height={breakGapHeight}
              fill="white"
            />
            {/* Zigzag break lines */}
            {Array.from({ length: Math.floor(innerWidth / 15) }).map((_, i) => {
              const x1 = padding.left + i * 15;
              const x2 = padding.left + (i + 1) * 15;
              const yTop = padding.top + upperSegmentHeight;
              const yBottom = padding.top + upperSegmentHeight + breakGapHeight;
              return (
                <path
                  key={`break-${i}`}
                  d={`M ${x1} ${yTop} L ${x1 + 7.5} ${yTop + breakGapHeight / 2} L ${x2} ${yBottom}`}
                  stroke="#9ca3af"
                  strokeWidth="1.5"
                  fill="none"
                />
              );
            })}
          </g>

          {/* X-axis labels */}
          {spendingData.map((d, i) => {
            const x = xScale(i);
            return (
              <text
                key={i}
                x={x}
                y={chartHeight - padding.bottom + 20}
                textAnchor="middle"
                fontSize="12"
                fill="#6b7280"
              >
                {d.year}
              </text>
            );
          })}

          {/* Lines */}
          {totalPaths.map((pathData, idx) => (
            <path
              key={`total-${idx}`}
              d={pathData}
              fill="none"
              stroke="#3b82f6"
              strokeWidth="3"
              strokeLinecap="round"
              strokeLinejoin="round"
            />
          ))}
          {cityPaths.map((pathData, idx) => (
            <path
              key={`city-${idx}`}
              d={pathData}
              fill="none"
              stroke="#10b981"
              strokeWidth="2.5"
              strokeLinecap="round"
              strokeLinejoin="round"
            />
          ))}
          {countyPaths.map((pathData, idx) => (
            <path
              key={`county-${idx}`}
              d={pathData}
              fill="none"
              stroke="#8b5cf6"
              strokeWidth="2.5"
              strokeLinecap="round"
              strokeLinejoin="round"
            />
          ))}

          {/* Data points */}
          {spendingData.map((d, i) => {
            const x = xScale(i);
            return (
              <g key={i}>
                <circle cx={x} cy={yScale(d.total_spending || 0)} r="4" fill="#3b82f6" />
                <circle cx={x} cy={yScale(d.city_spending || 0)} r="3.5" fill="#10b981" />
                <circle cx={x} cy={yScale(d.county_spending || 0)} r="3.5" fill="#8b5cf6" />
              </g>
            );
          })}
        </svg>

        {/* Legend */}
        <div style={{
          display: 'flex',
          justifyContent: 'center',
          gap: '24px',
          marginTop: '16px',
          flexWrap: 'wrap'
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <div style={{ width: '24px', height: '3px', backgroundColor: '#3b82f6' }}></div>
            <span style={{ fontSize: '14px', color: '#374151' }}>Total Spending</span>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <div style={{ width: '24px', height: '3px', backgroundColor: '#10b981' }}></div>
            <span style={{ fontSize: '14px', color: '#374151' }}>City Government</span>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <div style={{ width: '24px', height: '3px', backgroundColor: '#8b5cf6' }}></div>
            <span style={{ fontSize: '14px', color: '#374151' }}>County Government</span>
          </div>
        </div>
      </div>
    </div>
  );
}

export default SpendingLineChart;
