import React from 'react';
import { useOrganizationStore } from '../stores';

const ActivitySummary = () => {
  const { organizationData, loading } = useOrganizationStore();

  if (loading) {
    return (
      <div className="activity-summary">
        <div className="metric-card">
          <div className="metric-skeleton"></div>
        </div>
        <div className="metric-card">
          <div className="metric-skeleton"></div>
        </div>
        <div className="metric-card">
          <div className="metric-skeleton"></div>
        </div>
      </div>
    );
  }

  if (!organizationData) {
    return null;
  }

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0
    }).format(amount);
  };

  const formatDate = (dateString) => {
    if (!dateString) return 'N/A';
    // Parse date as UTC to avoid timezone issues
    // Format: "2012-01-01" should display as "Jan 1, 2012"
    const [year, month, day] = dateString.split('-').map(Number);
    const date = new Date(year, month - 1, day); // Use local date constructor
    return date.toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    });
  };

  return (
    <div className="activity-summary">
      <div className="metric-card">
        <div className="metric-icon" style={{ backgroundColor: '#e3f2fd' }}>
          <span style={{ color: '#1976d2', fontSize: '24px' }}>$</span>
        </div>
        <div className="metric-content">
          <div className="metric-label">Total Spending</div>
          <div className="metric-value">{formatCurrency(organizationData.totalSpending)}</div>
        </div>
      </div>

      <div className="metric-card">
        <div className="metric-icon" style={{ backgroundColor: '#f3e5f5' }}>
          <span style={{ color: '#7b1fa2', fontSize: '24px' }}>📊</span>
        </div>
        <div className="metric-content">
          <div className="metric-label">Total Activities</div>
          <div className="metric-value">{organizationData.totalActivities}</div>
        </div>
      </div>

      <div className="metric-card">
        <div className="metric-icon" style={{ backgroundColor: '#e8f5e9' }}>
          <span style={{ color: '#388e3c', fontSize: '24px' }}>💰</span>
        </div>
        <div className="metric-content">
          <div className="metric-label">Average Amount</div>
          <div className="metric-value">{formatCurrency(organizationData.averageAmount)}</div>
        </div>
      </div>

      <div className="metric-card">
        <div className="metric-icon" style={{ backgroundColor: '#fff3e0' }}>
          <span style={{ color: '#f57c00', fontSize: '24px' }}>🏷️</span>
        </div>
        <div className="metric-content">
          <div className="metric-label">Top Category</div>
          <div className="metric-value" style={{ fontSize: '1rem' }}>
            {organizationData.topCategory}
          </div>
        </div>
      </div>

      <div className="metric-card">
        <div className="metric-icon" style={{ backgroundColor: '#fce4ec' }}>
          <span style={{ color: '#c2185b', fontSize: '24px' }}>📅</span>
        </div>
        <div className="metric-content">
          <div className="metric-label">First Activity</div>
          <div className="metric-value" style={{ fontSize: '0.95rem' }}>
            {formatDate(organizationData.firstActivity)}
          </div>
        </div>
      </div>

      <div className="metric-card">
        <div className="metric-icon" style={{ backgroundColor: '#e0f2f1' }}>
          <span style={{ color: '#00796b', fontSize: '24px' }}>🕒</span>
        </div>
        <div className="metric-content">
          <div className="metric-label">Latest Activity</div>
          <div className="metric-value" style={{ fontSize: '0.95rem' }}>
            {formatDate(organizationData.lastActivity)}
          </div>
        </div>
      </div>
    </div>
  );
};

export default ActivitySummary;