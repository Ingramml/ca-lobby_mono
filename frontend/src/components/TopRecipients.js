import React, { useMemo } from 'react';
import { useOrganizationStore } from '../stores';
import './TopRecipients.css';

/**
 * TopRecipients - Displays top recipients of lobbying money
 * Shows both firms (companies) and individuals (persons) who received payments
 */
const TopRecipients = () => {
  const { activities } = useOrganizationStore();

  // Process activities to find top recipients
  const recipientData = useMemo(() => {
    if (!activities || activities.length === 0) {
      return { firms: [], persons: [] };
    }

    // Aggregate spending by firm name and person
    const firmTotals = {};
    const personTotals = {};

    activities.forEach(activity => {
      const amount = activity.amount || 0;

      // Track firm recipients
      if (activity.firm_name && activity.firm_name.trim()) {
        const firmName = activity.firm_name.trim();
        if (!firmTotals[firmName]) {
          firmTotals[firmName] = {
            name: firmName,
            total: 0,
            count: 0
          };
        }
        firmTotals[firmName].total += amount;
        firmTotals[firmName].count += 1;
      }

      // Track individual recipients (if available in data)
      if (activity.lobbyist && activity.lobbyist.trim() && activity.lobbyist !== 'Unknown Lobbyist') {
        const personName = activity.lobbyist.trim();
        if (!personTotals[personName]) {
          personTotals[personName] = {
            name: personName,
            total: 0,
            count: 0
          };
        }
        personTotals[personName].total += amount;
        personTotals[personName].count += 1;
      }
    });

    // Sort and get top 5
    const topFirms = Object.values(firmTotals)
      .sort((a, b) => b.total - a.total)
      .slice(0, 5);

    const topPersons = Object.values(personTotals)
      .sort((a, b) => b.total - a.total)
      .slice(0, 5);

    return { firms: topFirms, persons: topPersons };
  }, [activities]);

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0
    }).format(amount);
  };

  const hasData = recipientData.firms.length > 0 || recipientData.persons.length > 0;

  if (!hasData) {
    return (
      <div className="top-recipients">
        <h3>Top Recipients</h3>
        <p className="no-data">No recipient data available</p>
      </div>
    );
  }

  return (
    <div className="top-recipients">
      <h3>💰 Top Recipients of Lobbying Money</h3>

      {/* Top Lobbying Firms */}
      {recipientData.firms.length > 0 && (
        <div className="recipients-section">
          <h4 className="recipients-subtitle">
            🏢 Top Lobbying Firms/Companies
          </h4>
          <div className="recipients-list">
            {recipientData.firms.map((firm, index) => (
              <div key={index} className="recipient-item">
                <div className="recipient-rank">#{index + 1}</div>
                <div className="recipient-info">
                  <div className="recipient-name">{firm.name}</div>
                  <div className="recipient-meta">
                    {firm.count} {firm.count === 1 ? 'payment' : 'payments'}
                  </div>
                </div>
                <div className="recipient-amount">
                  {formatCurrency(firm.total)}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Top Individual Lobbyists */}
      {recipientData.persons.length > 0 && (
        <div className="recipients-section">
          <h4 className="recipients-subtitle">
            👤 Top Individual Lobbyists
          </h4>
          <div className="recipients-list">
            {recipientData.persons.map((person, index) => (
              <div key={index} className="recipient-item">
                <div className="recipient-rank">#{index + 1}</div>
                <div className="recipient-info">
                  <div className="recipient-name">{person.name}</div>
                  <div className="recipient-meta">
                    {person.count} {person.count === 1 ? 'payment' : 'payments'}
                  </div>
                </div>
                <div className="recipient-amount">
                  {formatCurrency(person.total)}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default TopRecipients;
