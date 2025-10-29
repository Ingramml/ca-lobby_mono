import React, { useState } from 'react';
import { useOrganizationStore } from '../stores';

const LobbyistNetwork = () => {
  const { lobbyists, loading } = useOrganizationStore();
  const [expanded, setExpanded] = useState(false);

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0
    }).format(amount);
  };

  // Get initial avatar from name
  const getInitials = (name) => {
    if (!name) return '??';
    const parts = name.split(' ');
    if (parts.length >= 2) {
      return `${parts[0][0]}${parts[parts.length - 1][0]}`.toUpperCase();
    }
    return name.substring(0, 2).toUpperCase();
  };

  if (loading) {
    return (
      <div>
        <h3>Lobbyist Network</h3>
        <div className="lobbyist-skeleton">
          <div className="skeleton-item"></div>
          <div className="skeleton-item"></div>
        </div>
      </div>
    );
  }

  if (!lobbyists || lobbyists.length === 0) {
    return (
      <div>
        <h3>Lobbyist Network</h3>
        <div style={{ padding: '20px', textAlign: 'center', color: '#999' }}>
          <p>No lobbyist data available</p>
        </div>
      </div>
    );
  }

  const displayedLobbyists = expanded ? lobbyists : lobbyists.slice(0, 5);
  const hasMore = lobbyists.length > 5;

  return (
    <div>
      <h3>Lobbyist Network</h3>
      <p style={{ fontSize: '0.9rem', color: '#666', marginBottom: '16px' }}>
        {lobbyists.length} unique {lobbyists.length === 1 ? 'lobbyist' : 'lobbyists'} working with this organization
      </p>

      <div className="lobbyist-list">
        {displayedLobbyists.map((lobbyist, index) => (
          <div key={`lobbyist-${index}`} className="lobbyist-card">
            <div className="lobbyist-header">
              <div className="lobbyist-avatar">
                {getInitials(lobbyist.name)}
              </div>
              <div className="lobbyist-info">
                <h4 className="lobbyist-name">{lobbyist.name}</h4>
                <div className="lobbyist-stats">
                  <span className="lobbyist-stat">
                    {lobbyist.activityCount} {lobbyist.activityCount === 1 ? 'activity' : 'activities'}
                  </span>
                  <span className="lobbyist-stat-divider">•</span>
                  <span className="lobbyist-stat">
                    {formatCurrency(lobbyist.totalAmount)}
                  </span>
                </div>
              </div>
            </div>
            {lobbyist.categories && lobbyist.categories.length > 0 && (
              <div className="lobbyist-categories">
                <span style={{ fontSize: '0.85rem', color: '#666', marginRight: '8px' }}>
                  Focus areas:
                </span>
                {lobbyist.categories.map((cat, idx) => (
                  <span key={idx} className="lobbyist-category-tag">
                    {cat}
                  </span>
                ))}
              </div>
            )}
          </div>
        ))}
      </div>

      {hasMore && (
        <button
          className="expand-btn"
          onClick={() => setExpanded(!expanded)}
          style={{ width: '100%', marginTop: '12px' }}
        >
          {expanded ? 'Show Less' : `Show All (${lobbyists.length})`}
        </button>
      )}
    </div>
  );
};

export default LobbyistNetwork;