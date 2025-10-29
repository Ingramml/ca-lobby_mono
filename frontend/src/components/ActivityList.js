import React from 'react';
import { useOrganizationStore } from '../stores';
import { exportToCSV, generateActivitiesCSV, sanitizeFilename } from '../utils/exportHelpers';

const ActivityList = () => {
  const {
    activities,
    selectedOrganization,
    currentPage,
    totalActivities,
    loading,
    getPaginatedActivities,
    getTotalPages,
    setCurrentPage
  } = useOrganizationStore();

  const [expandedActivity, setExpandedActivity] = React.useState(null);

  const paginatedActivities = getPaginatedActivities();
  const totalPages = getTotalPages();

  const toggleActivityDetails = (activityId) => {
    setExpandedActivity(expandedActivity === activityId ? null : activityId);
  };

  const handlePageChange = (newPage) => {
    setCurrentPage(newPage);
    // Scroll to top of activity list
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  const handleExportActivities = () => {
    const csvData = generateActivitiesCSV(activities);
    const filename = `${sanitizeFilename(selectedOrganization)}_activities.csv`;
    exportToCSV(csvData, filename);
  };

  const getCategoryClass = (category) => {
    const normalizedCategory = category?.toLowerCase() || 'default';
    return `category-badge ${normalizedCategory}`;
  };

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 2,
      maximumFractionDigits: 2
    }).format(amount);
  };

  const formatDate = (dateString) => {
    if (!dateString) return 'N/A';
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    });
  };

  const getExpenseDescription = (activity) => {
    const parts = [];

    // Form type explanation
    if (activity.form_type) {
      const formDescriptions = {
        'F625': 'Quarterly Report',
        'F635': 'Periodic Report',
        'F645': 'Termination Report',
        'F615': 'Registration Form',
        'F640': 'Amendment'
      };
      parts.push(formDescriptions[activity.form_type] || activity.form_type);
    }

    // Organization type
    if (activity.organization_type) {
      const orgTypes = {
        'PURCHASER': 'Lobbying Services Purchased',
        'EMPLOYER': 'In-House Lobbying',
        'FIRM': 'Lobbying Firm Services',
        'CONTRACTOR': 'Contract Lobbying'
      };
      parts.push(orgTypes[activity.organization_type] || activity.organization_type);
    }

    // Reporting period
    if (activity.from_date && activity.thru_date) {
      const fromDate = formatDate(activity.from_date);
      const thruDate = formatDate(activity.thru_date);
      parts.push(`Period: ${fromDate} - ${thruDate}`);
    }

    return parts.length > 0 ? parts.join(' • ') : activity.description || activity.activity_description || 'Lobby Activity';
  };

  if (loading) {
    return (
      <div className="dashboard-card">
        <h3>Recent Activities</h3>
        <div className="activity-list-skeleton">
          <div className="skeleton-item"></div>
          <div className="skeleton-item"></div>
          <div className="skeleton-item"></div>
        </div>
      </div>
    );
  }

  if (!activities || activities.length === 0) {
    return (
      <div className="dashboard-card">
        <h3>Recent Activities</h3>
        <div style={{ padding: '20px', textAlign: 'center', color: '#999' }}>
          <p>No activities found for this organization.</p>
        </div>
      </div>
    );
  }

  const startIndex = (currentPage - 1) * 10 + 1;
  const endIndex = Math.min(currentPage * 10, totalActivities);

  return (
    <div className="dashboard-card">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px', flexWrap: 'wrap', gap: '12px' }}>
        <h3 style={{ margin: 0 }}>Recent Activities</h3>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <span style={{ fontSize: '0.9rem', color: '#666' }}>
            Showing {startIndex}-{endIndex} of {totalActivities}
          </span>
          <button
            onClick={handleExportActivities}
            className="btn btn-sm"
            aria-label="Export all activities as CSV"
            title="Export all activities to CSV"
          >
            📥 Export
          </button>
        </div>
      </div>

      <div className="activity-list">
        {paginatedActivities.map((activity, index) => {
          const isExpanded = expandedActivity === activity.id;
          return (
            <div key={`activity-${currentPage}-${index}`} className="activity-item">
              <div className="activity-header">
                <span className={getCategoryClass(activity.category)}>
                  {activity.category || 'Other'}
                </span>
                <span className="activity-date">{formatDate(activity.date || activity.filing_date)}</span>
              </div>
              <div className="activity-body">
                <h4 className="activity-lobbyist">
                  {activity.lobbyist || activity.firm_name || activity.organization || 'Unknown Lobbyist'}
                </h4>
                <p className="activity-description">
                  {getExpenseDescription(activity)}
                </p>

                {/* Payment breakdown */}
                {(activity.fees_amount > 0 || activity.reimbursement_amount > 0 || activity.advance_amount > 0) && (
                  <div style={{ marginTop: '8px', fontSize: '0.85rem', color: '#666' }}>
                    {activity.fees_amount > 0 && <span>Fees: {formatCurrency(activity.fees_amount)} </span>}
                    {activity.reimbursement_amount > 0 && <span>• Reimbursement: {formatCurrency(activity.reimbursement_amount)} </span>}
                    {activity.advance_amount > 0 && <span>• Advance: {formatCurrency(activity.advance_amount)}</span>}
                  </div>
                )}
              </div>
              <div className="activity-footer">
                <span className="activity-amount">{formatCurrency(activity.amount || 0)}</span>
                <button
                  onClick={() => toggleActivityDetails(activity.id)}
                  className="btn btn-sm"
                  style={{ marginLeft: '12px', padding: '4px 8px', fontSize: '0.8rem' }}
                  aria-label={isExpanded ? "Hide details" : "Show details"}
                >
                  {isExpanded ? '▲ Hide' : '▼ Details'}
                </button>
              </div>

              {/* Expanded details section */}
              {isExpanded && (
                <div style={{
                  marginTop: '12px',
                  padding: '12px',
                  backgroundColor: '#f9fafb',
                  borderRadius: '4px',
                  borderTop: '1px solid #e5e7eb'
                }}>
                  <h5 style={{ margin: '0 0 8px 0', fontSize: '0.9rem', fontWeight: '600' }}>Transaction Details</h5>
                  <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '8px', fontSize: '0.85rem' }}>
                    <div>
                      <strong>Filing ID:</strong> {activity.filing_id || 'N/A'}
                    </div>
                    <div>
                      <strong>Line Item:</strong> {activity.line_item || 'N/A'}
                    </div>
                    <div>
                      <strong>Form Type:</strong> {activity.form_type || 'N/A'}
                    </div>
                    <div>
                      <strong>Payment Tier:</strong> {activity.payment_tier || 'N/A'}
                    </div>
                    {activity.cumulative_total > 0 && (
                      <div>
                        <strong>Cumulative Total:</strong> {formatCurrency(activity.cumulative_total)}
                      </div>
                    )}
                    {activity.entity_code && (
                      <div>
                        <strong>Entity Code:</strong> {activity.entity_code}
                      </div>
                    )}
                  </div>

                  {/* Payment breakdown detail */}
                  {(activity.fees_amount > 0 || activity.reimbursement_amount > 0 || activity.advance_amount > 0) && (
                    <div style={{ marginTop: '12px' }}>
                      <strong style={{ fontSize: '0.9rem' }}>Payment Breakdown:</strong>
                      <div style={{ marginTop: '4px', display: 'flex', flexDirection: 'column', gap: '4px' }}>
                        {activity.fees_amount > 0 && (
                          <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                            <span>Lobbying Fees:</span>
                            <span>{formatCurrency(activity.fees_amount)}</span>
                          </div>
                        )}
                        {activity.reimbursement_amount > 0 && (
                          <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                            <span>Reimbursements:</span>
                            <span>{formatCurrency(activity.reimbursement_amount)}</span>
                          </div>
                        )}
                        {activity.advance_amount > 0 && (
                          <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                            <span>Advances:</span>
                            <span>{formatCurrency(activity.advance_amount)}</span>
                          </div>
                        )}
                        <div style={{ display: 'flex', justifyContent: 'space-between', borderTop: '1px solid #ddd', paddingTop: '4px', fontWeight: '600' }}>
                          <span>Total:</span>
                          <span>{formatCurrency(activity.amount || 0)}</span>
                        </div>
                      </div>
                    </div>
                  )}

                  {/* Date information */}
                  {(activity.from_date || activity.thru_date || activity.filing_date) && (
                    <div style={{ marginTop: '12px' }}>
                      <strong style={{ fontSize: '0.9rem' }}>Period Information:</strong>
                      <div style={{ marginTop: '4px', fontSize: '0.85rem' }}>
                        {activity.from_date && <div>From: {formatDate(activity.from_date)}</div>}
                        {activity.thru_date && <div>Through: {formatDate(activity.thru_date)}</div>}
                        {activity.filing_date && <div>Filed: {formatDate(activity.filing_date)}</div>}
                      </div>
                    </div>
                  )}
                </div>
              )}
            </div>
          );
        })}
      </div>

      {totalPages > 1 && (
        <div className="pagination-controls">
          <button
            className="pagination-btn"
            onClick={() => handlePageChange(1)}
            disabled={currentPage === 1}
          >
            First
          </button>
          <button
            className="pagination-btn"
            onClick={() => handlePageChange(currentPage - 1)}
            disabled={currentPage === 1}
          >
            Previous
          </button>
          <span className="pagination-info">
            Page {currentPage} of {totalPages}
          </span>
          <button
            className="pagination-btn"
            onClick={() => handlePageChange(currentPage + 1)}
            disabled={currentPage === totalPages}
          >
            Next
          </button>
          <button
            className="pagination-btn"
            onClick={() => handlePageChange(totalPages)}
            disabled={currentPage === totalPages}
          >
            Last
          </button>
        </div>
      )}
    </div>
  );
};

export default ActivityList;