import React, { useMemo, useState, useEffect } from 'react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend
} from 'recharts';
import ChartWrapper from './ChartWrapper';
import { useSearchStore, useUserStore } from '../../stores';
import { generateSampleLobbyData, processLobbyTrendsByType } from '../../utils/sampleData';
import { getMobileChartConfig, getMobileAxisConfig, formatters } from '../../utils/chartConfig';

const LobbyTrendsChart = () => {
  const { results } = useSearchStore();
  const { preferences } = useUserStore();
  const [isMobile, setIsMobile] = useState(window.innerWidth <= 768);

  // Use sample data for now, will be replaced with real search results
  const sampleData = useMemo(() => generateSampleLobbyData(200), []);
  const chartData = useMemo(() => {
    const dataToProcess = results && results.length > 0 ? results : sampleData;
    return processLobbyTrendsByType(dataToProcess, 'quarter');
  }, [results, sampleData]);

  // Handle responsive behavior
  useEffect(() => {
    const handleResize = () => {
      setIsMobile(window.innerWidth <= 768);
    };

    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  const formatCurrency = (value) => {
    return formatters.currency(value, isMobile);
  };

  const handleDataClick = (data) => {
    console.log('Trend data clicked:', data);
    // Future: Filter search results by selected time period
  };

  const chartTheme = {
    light: {
      background: '#ffffff',
      text: '#333333',
      total: '#2563eb',
      city: '#10b981',
      county: '#8b5cf6',
      grid: '#e5e7eb'
    },
    dark: {
      background: '#1f2937',
      text: '#f9fafb',
      total: '#60a5fa',
      city: '#34d399',
      county: '#a78bfa',
      grid: '#374151'
    }
  };

  const theme = chartTheme[preferences.theme] || chartTheme.light;
  const mobileConfig = getMobileChartConfig(isMobile);
  const axisConfig = getMobileAxisConfig(isMobile);

  return (
    <ChartWrapper
      title="CA Lobby Expenditure Trends"
      height={isMobile ? 300 : 350}
      className="lobby-trends-chart"
    >
      <ResponsiveContainer width="100%" height="100%">
        <LineChart
          data={chartData}
          margin={mobileConfig.margin}
          onClick={handleDataClick}
        >
          <CartesianGrid strokeDasharray="3 3" stroke={theme.grid} />
          <XAxis
            dataKey="period"
            stroke={theme.text}
            tick={axisConfig.tick}
            angle={isMobile ? -45 : -30}
            textAnchor="end"
            height={isMobile ? 50 : 60}
            interval={isMobile ? 1 : 0}
          />
          <YAxis
            stroke={theme.text}
            tick={axisConfig.tick}
            tickFormatter={formatCurrency}
          />
          <Tooltip
            formatter={(value, name) => [formatCurrency(value), name]}
            labelStyle={{ color: theme.text }}
            contentStyle={{
              backgroundColor: theme.background,
              border: `1px solid ${theme.grid}`,
              borderRadius: '4px'
            }}
          />
          <Legend />
          <Line
            type="monotone"
            dataKey="totalAmount"
            stroke={theme.total}
            strokeWidth={2}
            dot={{ fill: theme.total, strokeWidth: 2, r: 4 }}
            activeDot={{ r: 6, stroke: theme.total, strokeWidth: 2 }}
            name="Total Spending"
          />
          <Line
            type="monotone"
            dataKey="cityAmount"
            stroke={theme.city}
            strokeWidth={2}
            dot={{ fill: theme.city, strokeWidth: 2, r: 4 }}
            activeDot={{ r: 6, stroke: theme.city, strokeWidth: 2 }}
            name="City Organizations"
          />
          <Line
            type="monotone"
            dataKey="countyAmount"
            stroke={theme.county}
            strokeWidth={2}
            dot={{ fill: theme.county, strokeWidth: 2, r: 4 }}
            activeDot={{ r: 6, stroke: theme.county, strokeWidth: 2 }}
            name="County Organizations"
          />
        </LineChart>
      </ResponsiveContainer>
    </ChartWrapper>
  );
};

export default LobbyTrendsChart;