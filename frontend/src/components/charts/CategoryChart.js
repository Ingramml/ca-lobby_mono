import React, { useMemo } from 'react';
import {
  PieChart,
  Pie,
  Cell,
  ResponsiveContainer,
  Tooltip,
  Legend
} from 'recharts';
import ChartWrapper from './ChartWrapper';
import { useSearchStore, useUserStore } from '../../stores';
import organizationsSummary from '../../data/organizations-summary.json';

const CategoryChart = () => {
  const { results } = useSearchStore();
  const { preferences } = useUserStore();

  // Use real organization type data from BigQuery views
  const chartData = useMemo(() => {
    // Group organizations by category and sum spending
    const categoryMap = {};

    organizationsSummary.organizations.forEach(org => {
      const category = org.category || 'Other';
      if (!categoryMap[category]) {
        categoryMap[category] = {
          name: category,
          amount: 0,
          count: 0
        };
      }
      categoryMap[category].amount += org.totalSpending || 0;
      categoryMap[category].count += 1;
    });

    // Convert to array and sort by amount
    return Object.values(categoryMap).sort((a, b) => b.amount - a.amount);
  }, []);

  const formatCurrency = (value) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0
    }).format(value);
  };

  const handleSliceClick = (data) => {
    console.log('Category clicked:', data);
    // Future: Filter search results by selected category
  };

  const chartTheme = {
    light: {
      colors: ['#2563eb', '#3b82f6', '#60a5fa', '#93c5fd', '#dbeafe', '#bfdbfe', '#e0e7ff', '#c7d2fe', '#a5b4fc', '#818cf8'],
      background: '#ffffff',
      text: '#333333'
    },
    dark: {
      colors: ['#60a5fa', '#93c5fd', '#dbeafe', '#bfdbfe', '#e0e7ff', '#c7d2fe', '#a5b4fc', '#818cf8', '#6366f1', '#4f46e5'],
      background: '#1f2937',
      text: '#f9fafb'
    }
  };

  const theme = chartTheme[preferences.theme] || chartTheme.light;

  const CustomTooltip = ({ active, payload }) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload;
      return (
        <div
          style={{
            backgroundColor: theme.background,
            border: '1px solid #e5e7eb',
            borderRadius: '4px',
            padding: '8px 12px',
            boxShadow: '0 4px 12px rgba(0, 0, 0, 0.15)'
          }}
        >
          <p style={{ margin: 0, fontWeight: 'bold', color: theme.text }}>
            {data.name}
          </p>
          <p style={{ margin: '4px 0 0 0', color: theme.text }}>
            {formatCurrency(data.amount)} ({((data.amount / chartData.reduce((sum, item) => sum + item.amount, 0)) * 100).toFixed(1)}%)
          </p>
          <p style={{ margin: '2px 0 0 0', fontSize: '12px', color: '#6b7280' }}>
            {data.count} {data.count === 1 ? 'entry' : 'entries'}
          </p>
        </div>
      );
    }
    return null;
  };

  const CustomLabel = ({ cx, cy, midAngle, innerRadius, outerRadius, percent }) => {
    if (percent < 0.05) return null; // Don't show labels for slices smaller than 5%

    const RADIAN = Math.PI / 180;
    const radius = innerRadius + (outerRadius - innerRadius) * 0.5;
    const x = cx + radius * Math.cos(-midAngle * RADIAN);
    const y = cy + radius * Math.sin(-midAngle * RADIAN);

    return (
      <text
        x={x}
        y={y}
        fill={theme.background}
        textAnchor={x > cx ? 'start' : 'end'}
        dominantBaseline="central"
        fontSize={12}
        fontWeight="bold"
      >
        {`${(percent * 100).toFixed(0)}%`}
      </text>
    );
  };

  return (
    <ChartWrapper
      title="Lobby Spending by Category"
      height={400}
      className="category-chart"
    >
      <ResponsiveContainer width="100%" height="100%">
        <PieChart>
          <Pie
            data={chartData}
            cx="50%"
            cy="50%"
            labelLine={false}
            label={CustomLabel}
            outerRadius={120}
            fill="#8884d8"
            dataKey="amount"
            onClick={handleSliceClick}
            style={{ cursor: 'pointer' }}
          >
            {chartData.map((entry, index) => (
              <Cell
                key={`cell-${index}`}
                fill={theme.colors[index % theme.colors.length]}
              />
            ))}
          </Pie>
          <Tooltip content={<CustomTooltip />} />
          <Legend
            verticalAlign="bottom"
            height={36}
            wrapperStyle={{
              fontSize: '12px',
              color: theme.text
            }}
          />
        </PieChart>
      </ResponsiveContainer>
    </ChartWrapper>
  );
};

export default CategoryChart;