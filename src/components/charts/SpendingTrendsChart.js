import React from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { useOrganizationStore } from '../../stores';

const SpendingTrendsChart = () => {
  const { spendingTrends, loading } = useOrganizationStore();

  if (loading) {
    return (
      <div style={{ padding: '20px' }}>
        <h3>Spending Trends</h3>
        <div style={{ height: '400px', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
          <div className="chart-skeleton">Loading chart...</div>
        </div>
      </div>
    );
  }

  if (!spendingTrends || spendingTrends.length === 0) {
    return (
      <div style={{ padding: '20px' }}>
        <h3>Spending Trends</h3>
        <div style={{ height: '300px', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
          <p style={{ color: '#999' }}>No spending data available</p>
        </div>
      </div>
    );
  }

  const formatCurrency = (value) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0
    }).format(value);
  };

  const CustomTooltip = ({ active, payload, label }) => {
    if (active && payload && payload.length) {
      return (
        <div style={{
          backgroundColor: 'white',
          border: '1px solid #ccc',
          padding: '10px',
          borderRadius: '4px',
          boxShadow: '0 2px 4px rgba(0,0,0,0.1)'
        }}>
          <p style={{ margin: '0 0 5px', fontWeight: 'bold' }}>{label}</p>
          <p style={{ margin: 0, color: '#1976d2' }}>
            Amount: {formatCurrency(payload[0].value)}
          </p>
          <p style={{ margin: '5px 0 0', color: '#666', fontSize: '0.85rem' }}>
            Activities: {payload[0].payload.count}
          </p>
        </div>
      );
    }
    return null;
  };

  // Determine chart height based on screen size
  const isMobile = window.innerWidth < 768;
  const chartHeight = isMobile ? 300 : 400;

  return (
    <div style={{ padding: '20px' }}>
      <h3>Spending Trends Over Time</h3>
      <ResponsiveContainer width="100%" height={chartHeight}>
        <LineChart
          data={spendingTrends}
          margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
        >
          <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
          <XAxis
            dataKey="period"
            tick={{ fontSize: 12 }}
            stroke="#666"
          />
          <YAxis
            tickFormatter={formatCurrency}
            tick={{ fontSize: 12 }}
            stroke="#666"
          />
          <Tooltip content={<CustomTooltip />} />
          <Legend
            wrapperStyle={{ paddingTop: '20px' }}
            iconType="line"
          />
          <Line
            type="monotone"
            dataKey="amount"
            stroke="#1976d2"
            strokeWidth={2}
            dot={{ fill: '#1976d2', r: 4 }}
            activeDot={{ r: 6 }}
            name="Spending Amount"
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
};

export default SpendingTrendsChart;