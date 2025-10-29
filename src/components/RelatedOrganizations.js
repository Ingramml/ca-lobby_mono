import React from 'react';
import { useOrganizationStore } from '../stores';

const RelatedOrganizations = ({ onOrganizationClick }) => {
  const { relatedOrganizations, loading } = useOrganizationStore();

  const formatCurrency = (amount) => {
    // Compact currency formatting for larger amounts
    if (amount >= 1000000) {
      return `$${(amount / 1000000).toFixed(1)}M`;
    } else if (amount >= 1000) {
      return `$${(amount / 1000).toFixed(0)}K`;
    }
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0
    }).format(amount);
  };

  const getSimilarityBadge = (score) => {
    if (score >= 0.8) {
      return { label: 'Very Similar', color: '#4caf50' };
    } else if (score >= 0.6) {
      return { label: 'Similar', color: '#2196f3' };
    } else if (score >= 0.4) {
      return { label: 'Somewhat Similar', color: '#ff9800' };
    } else {
      return { label: 'Related', color: '#9e9e9e' };
    }
  };

  if (loading) {
    return (
      <div>
        <h3>Related Organizations</h3>
        <div className="related-orgs-skeleton">
          <div className="skeleton-item"></div>
          <div className="skeleton-item"></div>
        </div>
      </div>
    );
  }

  if (!relatedOrganizations || relatedOrganizations.length === 0) {
    return (
      <div>
        <h3>Related Organizations</h3>
        <div style={{ padding: '20px', textAlign: 'center', color: '#999' }}>
          <p>No related organizations found</p>
        </div>
      </div>
    );
  }

  return (
    <div>
      <h3>Related Organizations</h3>
      <p style={{ fontSize: '0.9rem', color: '#666', marginBottom: '16px' }}>
        Organizations with similar lobbying patterns
      </p>

      <div className="related-orgs-list">
        {relatedOrganizations.map((org, index) => {
          const similarityBadge = getSimilarityBadge(org.similarityScore);
          return (
            <div
              key={`related-org-${index}`}
              className="related-org-card"
              onClick={() => onOrganizationClick && onOrganizationClick(org.name)}
              style={{ cursor: onOrganizationClick ? 'pointer' : 'default' }}
            >
              <div className="related-org-header">
                <h4 className="related-org-name">{org.name}</h4>
                <span
                  className="similarity-badge"
                  style={{ backgroundColor: similarityBadge.color }}
                >
                  {similarityBadge.label}
                </span>
              </div>

              <div className="related-org-stats">
                <div className="related-org-stat">
                  <span className="stat-label">Total Spending</span>
                  <span className="stat-value">{formatCurrency(org.totalSpending)}</span>
                </div>
                <div className="related-org-stat">
                  <span className="stat-label">Activities</span>
                  <span className="stat-value">{org.activityCount}</span>
                </div>
              </div>

              {org.categories && org.categories.length > 0 && (
                <div className="related-org-categories">
                  {org.categories.slice(0, 3).map((cat, idx) => (
                    <span key={idx} className="related-org-category-tag">
                      {cat}
                    </span>
                  ))}
                  {org.categories.length > 3 && (
                    <span className="related-org-category-tag" style={{ backgroundColor: '#f5f5f5', color: '#666' }}>
                      +{org.categories.length - 3} more
                    </span>
                  )}
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
};

export default RelatedOrganizations;