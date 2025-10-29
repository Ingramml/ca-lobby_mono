/**
 * Export Helper Functions
 * Utility functions for exporting organization profile data to CSV and JSON formats
 */

/**
 * Triggers a browser download for the given content
 * @param {string} content - The file content to download
 * @param {string} filename - The name of the file to download
 * @param {string} type - MIME type of the file
 */
const triggerDownload = (content, filename, type) => {
  const blob = new Blob([content], { type });
  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  URL.revokeObjectURL(url);
};

/**
 * Converts an array of objects to CSV format and triggers download
 * @param {Array} data - Array of objects to export
 * @param {string} filename - Name for the downloaded file
 */
export const exportToCSV = (data, filename) => {
  if (!data || data.length === 0) {
    console.warn('No data to export');
    return;
  }

  // Get headers from first object
  const headers = Object.keys(data[0]);
  const csvContent = [
    headers.join(','),
    ...data.map(row =>
      headers.map(header => {
        const value = row[header];
        // Handle values that contain commas, quotes, or newlines
        if (value === null || value === undefined) {
          return '';
        }
        const stringValue = String(value);
        if (stringValue.includes(',') || stringValue.includes('"') || stringValue.includes('\n')) {
          return `"${stringValue.replace(/"/g, '""')}"`;
        }
        return stringValue;
      }).join(',')
    )
  ].join('\n');

  triggerDownload(csvContent, filename, 'text/csv;charset=utf-8;');
};

/**
 * Converts data to JSON format and triggers download
 * @param {*} data - Data to export (any JSON-serializable data)
 * @param {string} filename - Name for the downloaded file
 */
export const exportToJSON = (data, filename) => {
  if (!data) {
    console.warn('No data to export');
    return;
  }

  const jsonContent = JSON.stringify(data, null, 2);
  triggerDownload(jsonContent, filename, 'application/json;charset=utf-8;');
};

/**
 * Formats organization profile summary data for CSV export
 * @param {Object} orgData - Organization data from organizationStore
 * @returns {Object} Formatted summary object
 */
export const generateOrganizationSummaryCSV = (orgData) => {
  return {
    Organization: orgData.selectedOrganization || 'Unknown',
    'Total Activities': orgData.organizationData?.totalActivities || 0,
    'Total Spending': `$${(orgData.organizationData?.totalSpending || 0).toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`,
    'Average Amount': `$${(orgData.organizationData?.averageAmount || 0).toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`,
    'Unique Lobbyists': orgData.lobbyists?.length || 0,
    'Unique Categories': orgData.organizationData?.uniqueCategories || 0,
    'First Activity': orgData.organizationData?.firstActivity || 'N/A',
    'Latest Activity': orgData.organizationData?.lastActivity || 'N/A',
    'Top Category': orgData.organizationData?.topCategory || 'N/A'
  };
};

/**
 * Formats activity list for CSV export
 * @param {Array} activities - Array of activity objects
 * @returns {Array} Formatted activities for CSV
 */
export const generateActivitiesCSV = (activities) => {
  if (!activities || activities.length === 0) {
    return [];
  }

  return activities.map(activity => ({
    Date: activity.date || activity.filing_date || 'N/A',
    Organization: activity.organization || 'Unknown',
    Lobbyist: activity.lobbyist || 'Unknown',
    Amount: `$${(activity.amount || 0).toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`,
    Category: activity.category || 'N/A',
    Description: (activity.description || activity.activity_description || 'No description').replace(/\n/g, ' ').trim()
  }));
};

/**
 * Formats lobbyist network for CSV export
 * @param {Array} lobbyists - Array of lobbyist objects
 * @returns {Array} Formatted lobbyists for CSV
 */
export const generateLobbyistsCSV = (lobbyists) => {
  if (!lobbyists || lobbyists.length === 0) {
    return [];
  }

  return lobbyists.map(lobbyist => ({
    Name: lobbyist.name || 'Unknown',
    'Activity Count': lobbyist.count || 0,
    'Total Amount': `$${(lobbyist.totalAmount || 0).toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`,
    'Average Amount': `$${(lobbyist.averageAmount || 0).toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`
  }));
};

/**
 * Sanitizes filename to remove invalid characters
 * @param {string} name - Original filename
 * @returns {string} Sanitized filename
 */
export const sanitizeFilename = (name) => {
  return name
    .replace(/[^a-z0-9]/gi, '_')
    .replace(/_{2,}/g, '_')
    .toLowerCase();
};

/**
 * Gets current timestamp for filename
 * @returns {string} Formatted timestamp YYYYMMDD_HHMMSS
 */
export const getTimestamp = () => {
  const now = new Date();
  return now.toISOString()
    .replace(/[-:]/g, '')
    .replace(/T/, '_')
    .substring(0, 15);
};
