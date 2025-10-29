// KPI Calculation Utilities for Dashboard
// Calculates key performance indicators for California lobbying data

import organizationsSummary from '../data/organizations-summary.json';

// Realistic average amounts per activity by organization type
// These are used for estimated spending in demo mode
const AVERAGE_AMOUNTS = {
  'County Government': 8000,
  'City Government': 6000,
  'City Department': 5000,
  'County Department': 5500,
  'Health Organization': 7000,
  'Construction Authority': 6500,
  'School District': 4500,
  'Business': 10000,
  'default': 5000
};

/**
 * Calculate estimated spending for an organization based on activity count
 * Used in demo mode when real spending data is not available
 */
export const calculateEstimatedSpending = (org) => {
  const avgAmount = AVERAGE_AMOUNTS[org.category] || AVERAGE_AMOUNTS['default'];
  return org.activityCount * avgAmount;
};

/**
 * Get total spending for current year across all organizations
 * Returns estimated amount based on activity counts in demo mode
 */
export const getTotalYearSpending = () => {
  const useEstimates = true; // Switch to false when backend API available

  if (useEstimates) {
    // Demo mode: use estimated spending based on activity counts
    return organizationsSummary.organizations.reduce((total, org) => {
      return total + calculateEstimatedSpending(org);
    }, 0);
  } else {
    // Backend mode: use real spending data from API
    return organizationsSummary.organizations.reduce((total, org) => {
      return total + (org.totalSpending || 0);
    }, 0);
  }
};

/**
 * Get total city government spending
 * Includes organizations categorized as "City Government" or with "CITY OF" in name
 */
export const getCityGovernmentSpending = () => {
  const cityOrgs = organizationsSummary.organizations.filter(org =>
    org.category === 'City Government' ||
    org.name.includes('CITY OF')
  );

  return cityOrgs.reduce((total, org) => {
    return total + calculateEstimatedSpending(org);
  }, 0);
};

/**
 * Get total county government spending
 * Includes organizations categorized as "County Government" or with "COUNTY" in name
 * Excludes city departments that contain "COUNTY" (e.g., "COUNTY WASTE MANAGEMENT")
 */
export const getCountyGovernmentSpending = () => {
  const countyOrgs = organizationsSummary.organizations.filter(org =>
    org.category === 'County Government' ||
    org.category === 'County Department' ||
    (org.name.includes('COUNTY') && !org.name.includes('CITY OF'))
  );

  return countyOrgs.reduce((total, org) => {
    return total + calculateEstimatedSpending(org);
  }, 0);
};

/**
 * Get count of organizations by category
 * Useful for displaying in KPI subtitles
 */
export const getOrganizationCounts = () => {
  const cityOrgs = organizationsSummary.organizations.filter(org =>
    org.category === 'City Government' || org.name.includes('CITY OF')
  );

  const countyOrgs = organizationsSummary.organizations.filter(org =>
    org.category === 'County Government' ||
    org.category === 'County Department' ||
    (org.name.includes('COUNTY') && !org.name.includes('CITY OF'))
  );

  return {
    totalOrganizations: organizationsSummary.organizations.length,
    cityOrganizations: cityOrgs.length,
    countyOrganizations: countyOrgs.length
  };
};

/**
 * Get detailed breakdown of spending by category
 * Useful for future drill-down features
 */
export const getSpendingByCategory = () => {
  const categoryTotals = {};

  organizationsSummary.organizations.forEach(org => {
    const category = org.category || 'Other';
    if (!categoryTotals[category]) {
      categoryTotals[category] = {
        total: 0,
        count: 0,
        organizations: []
      };
    }

    const spending = calculateEstimatedSpending(org);
    categoryTotals[category].total += spending;
    categoryTotals[category].count += 1;
    categoryTotals[category].organizations.push({
      name: org.name,
      spending,
      activityCount: org.activityCount
    });
  });

  return categoryTotals;
};
