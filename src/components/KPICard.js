import React from 'react';
import './KPICard.css';

/**
 * KPICard - Displays a Key Performance Indicator with icon, title, value, and subtitle
 *
 * @param {string} title - Main title of the KPI (e.g., "Total Lobbying Expenditures")
 * @param {string} subtitle - Subtitle with context (e.g., "Year-to-Date 2025")
 * @param {number} value - Numeric value to display (will be formatted as currency)
 * @param {string} icon - Emoji icon to display
 * @param {string} color - Border color for the card (hex color)
 * @param {boolean} isEstimate - Whether to show "Estimated" badge
 */
const KPICard = ({ title, subtitle, value, icon, color, isEstimate = false }) => {
  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0
    }).format(amount);
  };

  return (
    <div className="kpi-card" style={{ borderTop: `4px solid ${color}` }}>
      <div className="kpi-header">
        <span className="kpi-icon" role="img" aria-label={title}>
          {icon}
        </span>
        <h3 className="kpi-title">{title}</h3>
      </div>
      <div className="kpi-value" aria-label={`Amount: ${formatCurrency(value)}`}>
        {formatCurrency(value)}
      </div>
      <div className="kpi-subtitle">
        <span>{subtitle}</span>
        {isEstimate && (
          <span className="kpi-estimate-badge" title="Based on activity counts and estimated averages">
            Estimated
          </span>
        )}
      </div>
    </div>
  );
};

export default KPICard;
