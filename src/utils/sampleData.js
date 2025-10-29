// Sample CA Lobby Data Generator for Chart Testing
// Using real Alameda County organizations from our data set

export const generateSampleLobbyData = (count = 100) => {
  const organizations = [
    'ALAMEDA COUNTY',
    'ALAMEDA, CITY OF',
    'ALAMEDA COUNTY WASTE MANAGEMENT AUTHORITY',
    'ALAMEDA UNIFIED SCHOOL DISTRICT',
    'ALAMEDA ALLIANCE FOR HEALTH',
    'ALAMEDA CORRIDOR-EAST CONSTRUCTION AUTHORITY'
  ];

  const lobbyCategories = [
    'Healthcare',
    'Technology',
    'Energy',
    'Transportation',
    'Education',
    'Environment',
    'Labor',
    'Finance',
    'Agriculture',
    'Housing'
  ];

  const data = [];
  const startDate = new Date('2023-01-01');
  const endDate = new Date('2025-09-28');

  for (let i = 0; i < count; i++) {
    const randomDate = new Date(
      startDate.getTime() + Math.random() * (endDate.getTime() - startDate.getTime())
    );

    const organization = organizations[Math.floor(Math.random() * organizations.length)];
    const category = lobbyCategories[Math.floor(Math.random() * lobbyCategories.length)];

    // Generate realistic lobby spending amounts
    const baseAmount = Math.random() * 500000; // Up to $500K
    const amount = Math.round(baseAmount * 100) / 100; // Round to cents

    data.push({
      id: `lobby_${i + 1}`,
      date: randomDate.toISOString().split('T')[0],
      organization,
      category,
      amount,
      quarter: `Q${Math.floor(randomDate.getMonth() / 3) + 1} ${randomDate.getFullYear()}`,
      year: randomDate.getFullYear(),
      month: randomDate.toLocaleDateString('en-US', { month: 'long', year: 'numeric' })
    });
  }

  return data.sort((a, b) => new Date(a.date) - new Date(b.date));
};

// Process data for trend charts
export const processLobbyTrends = (data, groupBy = 'quarter') => {
  const grouped = data.reduce((acc, item) => {
    const key = item[groupBy];
    if (!acc[key]) {
      acc[key] = { period: key, amount: 0, count: 0 };
    }
    acc[key].amount += item.amount;
    acc[key].count += 1;
    return acc;
  }, {});

  return Object.values(grouped).sort((a, b) => {
    if (groupBy === 'quarter') {
      const [qA, yearA] = a.period.split(' ');
      const [qB, yearB] = b.period.split(' ');
      return yearA !== yearB ? yearA - yearB : qA.replace('Q', '') - qB.replace('Q', '');
    }
    return new Date(a.period) - new Date(b.period);
  });
};

// Process data for trend charts with city/county breakdown
export const processLobbyTrendsByType = (data, groupBy = 'quarter') => {
  const grouped = data.reduce((acc, item) => {
    const key = item[groupBy];
    if (!acc[key]) {
      acc[key] = {
        period: key,
        totalAmount: 0,
        cityAmount: 0,
        countyAmount: 0,
        count: 0
      };
    }

    // Categorize organization type
    const orgName = item.organization || '';
    const isCity = orgName.includes('CITY OF') || orgName.includes(', CITY OF');
    const isCounty = (orgName.includes('COUNTY') && !orgName.includes('CITY OF')) ||
                     orgName.includes('ALAMEDA COUNTY WASTE') ||
                     orgName === 'ALAMEDA COUNTY';

    acc[key].totalAmount += item.amount;
    if (isCity) {
      acc[key].cityAmount += item.amount;
    }
    if (isCounty) {
      acc[key].countyAmount += item.amount;
    }
    acc[key].count += 1;
    return acc;
  }, {});

  return Object.values(grouped).sort((a, b) => {
    if (groupBy === 'quarter') {
      const [qA, yearA] = a.period.split(' ');
      const [qB, yearB] = b.period.split(' ');
      return yearA !== yearB ? yearA - yearB : qA.replace('Q', '') - qB.replace('Q', '');
    }
    return new Date(a.period) - new Date(b.period);
  });
};

// Process data for organization comparison
export const processOrganizationData = (data, limit = 10) => {
  const grouped = data.reduce((acc, item) => {
    if (!acc[item.organization]) {
      acc[item.organization] = { name: item.organization, amount: 0, count: 0 };
    }
    acc[item.organization].amount += item.amount;
    acc[item.organization].count += 1;
    return acc;
  }, {});

  return Object.values(grouped)
    .sort((a, b) => b.amount - a.amount)
    .slice(0, limit);
};

// Process data for category breakdown
export const processCategoryData = (data) => {
  const grouped = data.reduce((acc, item) => {
    if (!acc[item.category]) {
      acc[item.category] = { name: item.category, amount: 0, count: 0 };
    }
    acc[item.category].amount += item.amount;
    acc[item.category].count += 1;
    return acc;
  }, {});

  return Object.values(grouped).sort((a, b) => b.amount - a.amount);
};

// Aggregate organization summary metrics
export const aggregateOrganizationMetrics = (activities) => {
  if (!activities || activities.length === 0) {
    return {
      totalSpending: 0,
      totalActivities: 0,
      averageAmount: 0,
      firstActivity: null,
      lastActivity: null,
      topCategory: 'N/A'
    };
  }

  const totalSpending = activities.reduce((sum, a) => sum + (a.amount || 0), 0);
  const totalActivities = activities.length;
  const averageAmount = totalSpending / totalActivities;

  const sortedByDate = [...activities].sort((a, b) =>
    new Date(a.date || a.filing_date) - new Date(b.date || b.filing_date)
  );

  const firstActivity = sortedByDate[0]?.date || sortedByDate[0]?.filing_date;
  const lastActivity = sortedByDate[sortedByDate.length - 1]?.date ||
                       sortedByDate[sortedByDate.length - 1]?.filing_date;

  // Find top category
  const categoryCount = activities.reduce((acc, a) => {
    const cat = a.category || 'Unknown';
    acc[cat] = (acc[cat] || 0) + 1;
    return acc;
  }, {});

  const topCategory = Object.entries(categoryCount)
    .sort((a, b) => b[1] - a[1])[0]?.[0] || 'N/A';

  return {
    totalSpending,
    totalActivities,
    averageAmount,
    firstActivity,
    lastActivity,
    topCategory
  };
};

// Extract unique lobbyists from organization activities
export const extractLobbyistNetwork = (activities) => {
  const lobbyistMap = activities.reduce((acc, activity) => {
    const name = activity.lobbyist;
    if (!name) return acc;

    if (!acc[name]) {
      acc[name] = {
        name,
        activityCount: 0,
        totalAmount: 0,
        categories: new Set()
      };
    }

    acc[name].activityCount += 1;
    acc[name].totalAmount += activity.amount || 0;
    if (activity.category) {
      acc[name].categories.add(activity.category);
    }

    return acc;
  }, {});

  return Object.values(lobbyistMap)
    .map(l => ({
      ...l,
      categories: Array.from(l.categories)
    }))
    .sort((a, b) => b.totalAmount - a.totalAmount);
};

// Calculate spending trends by time period
// CRITICAL BUG FIX APPLIED: Fixed sorting logic for quarters
export const calculateSpendingTrends = (activities, periodType = 'quarter') => {
  const trendMap = activities.reduce((acc, activity) => {
    const date = new Date(activity.date || activity.filing_date);
    let period;

    if (periodType === 'quarter') {
      const q = Math.floor(date.getMonth() / 3) + 1;
      period = `Q${q} ${date.getFullYear()}`;
    } else if (periodType === 'month') {
      period = date.toLocaleDateString('en-US', { month: 'short', year: 'numeric' });
    } else {
      period = date.getFullYear().toString();
    }

    if (!acc[period]) {
      acc[period] = { period, amount: 0, count: 0 };
    }

    acc[period].amount += activity.amount || 0;
    acc[period].count += 1;

    return acc;
  }, {});

  // FIXED VERSION: Proper chronological sorting for quarters
  return Object.values(trendMap).sort((a, b) => {
    if (periodType === 'quarter') {
      const [qA, yearA] = a.period.split(' ');
      const [qB, yearB] = b.period.split(' ');
      const yearComp = parseInt(yearA) - parseInt(yearB);
      return yearComp !== 0 ? yearComp : parseInt(qA.replace('Q', '')) - parseInt(qB.replace('Q', ''));
    }
    return new Date(a.period) - new Date(b.period);
  });
};

// Find related organizations (same category or similar spending patterns)
// CRITICAL BUG FIX APPLIED: Fixed NaN issue in categorySimilarity calculation
export const findRelatedOrganizations = (organizationName, allActivities, limit = 5) => {
  // Get current org activities
  const orgActivities = allActivities.filter(a => a.organization === organizationName);
  const orgCategories = [...new Set(orgActivities.map(a => a.category))];
  const orgTotalSpending = orgActivities.reduce((sum, a) => sum + (a.amount || 0), 0);

  // Group all other organizations
  const otherOrgs = allActivities
    .filter(a => a.organization !== organizationName)
    .reduce((acc, activity) => {
      const org = activity.organization;
      if (!acc[org]) {
        acc[org] = {
          name: org,
          totalSpending: 0,
          activityCount: 0,
          categories: new Set(),
          sharedCategories: 0
        };
      }

      acc[org].totalSpending += activity.amount || 0;
      acc[org].activityCount += 1;
      if (activity.category) {
        acc[org].categories.add(activity.category);
        if (orgCategories.includes(activity.category)) {
          acc[org].sharedCategories += 1;
        }
      }

      return acc;
    }, {});

  // Calculate similarity scores
  return Object.values(otherOrgs)
    .map(org => {
      const spendingDiff = Math.abs(org.totalSpending - orgTotalSpending);
      const spendingSimilarity = 1 / (1 + spendingDiff / 1000000); // Normalize
      // FIXED VERSION: Handle division by zero when orgCategories is empty
      const categorySimilarity = orgCategories.length > 0
        ? org.sharedCategories / orgCategories.length
        : 0;

      return {
        ...org,
        categories: Array.from(org.categories),
        similarityScore: (spendingSimilarity * 0.4) + (categorySimilarity * 0.6)
      };
    })
    .sort((a, b) => b.similarityScore - a.similarityScore)
    .slice(0, limit);
};