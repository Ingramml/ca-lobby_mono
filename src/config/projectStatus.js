// CA Lobby Project Status Configuration
// Update this file when phases are completed for automatic display on website

export const PROJECT_STATUS = {
  // Current project information
  currentPhase: 'Phase 2.1 - Advanced Search & Analytics',
  version: '1.0.0',
  lastUpdated: 'September 28, 2025',

  // All completed phases - ADD NEW COMPLETIONS HERE
  completedPhases: [
    {
      id: '1.1',
      name: 'Foundation & Data Pipeline',
      status: 'completed',
      date: 'Sep 21, 2025',
      description: 'Automated BLN API data acquisition, BigQuery integration, data processing pipelines'
    },
    {
      id: '1.2',
      name: 'Enhanced Deployment Pipeline',
      status: 'completed',
      date: 'Sep 22, 2025',
      description: 'Multi-page React app, Vercel integration, deployment automation'
    },
    {
      id: '1.3',
      name: 'Frontend-Backend Integration',
      status: 'completed',
      date: 'Sep 24, 2025',
      description: 'REST API endpoints, real-time search, dashboard metrics, authentication'
    },
    {
      id: '2a.1',
      name: 'Component Structure Documentation',
      status: 'completed',
      date: 'Sep 24, 2025',
      description: 'Component analysis, enhancement strategy, architecture documentation'
    },
    {
      id: '2a.2',
      name: 'Enhancement Strategy Definition',
      status: 'completed',
      date: 'Sep 24, 2025',
      description: 'Enhancement-first approach, shared services, testing strategy'
    },
    {
      id: '2b',
      name: 'State Management Implementation',
      status: 'completed',
      date: 'Sep 28, 2025',
      description: 'Zustand stores (search, user, app), localStorage persistence, component integration'
    },
    {
      id: '2c',
      name: 'Visualization Library Implementation',
      status: 'completed',
      date: 'Sep 28, 2025',
      description: 'Recharts library selection, interactive charts (trends, organizations, categories), mobile optimization'
    },
    {
      id: '2d',
      name: 'Mobile-First CSS Strategy',
      status: 'completed',
      date: 'Sep 28, 2025',
      description: 'Responsive CSS architecture, mobile-first design system, touch optimization, government accessibility'
    },
    {
      id: '2e',
      name: 'API Design Specification',
      status: 'completed',
      date: 'Sep 28, 2025',
      description: 'OpenAPI 3.0 specification, mobile-optimized client architecture, performance monitoring, testing framework'
    }

    // 🔄 ADD NEW COMPLETED PHASES HERE:
    // {
    //   id: '2c',
    //   name: 'Visualization Library Decision',
    //   status: 'completed',
    //   date: 'UPDATE_DATE_HERE',
    //   description: 'Chart library selection, interactive visualizations, mobile optimization'
    // }
  ],

  // Upcoming phases - UPDATE WHEN PLANNING CHANGES
  upcomingPhases: [
    {
      id: '2.1',
      name: 'Advanced Search & Analytics',
      status: 'planned',
      description: 'Complex filters, trend analysis, export functionality'
    },
    {
      id: '2.2',
      name: 'Reporting & Visualization',
      status: 'planned',
      description: 'Interactive charts, custom reports, data comparison'
    },
    {
      id: '2.3',
      name: 'API & Integration',
      status: 'planned',
      description: 'Public API, webhooks, developer portal'
    }
  ],

  // Auto-calculated statistics
  get stats() {
    const totalPhases = this.completedPhases.length + this.upcomingPhases.length;
    const completedCount = this.completedPhases.length;
    const completionPercentage = Math.round((completedCount / totalPhases) * 100);

    return {
      totalPhases,
      completedCount,
      completionPercentage
    };
  },

  // Current features implemented
  currentFeatures: [
    'Zustand State Management',
    'Clerk Authentication',
    'React Router Navigation',
    '5 Core Components',
    'localStorage Persistence',
    'Mobile-First CSS Architecture',
    'Recharts Visualizations',
    'API Client with Caching',
    'Performance Monitoring',
    'Phase Status Tracking'
  ],

  // Deployment information
  deployment: {
    local: 'http://localhost:3000',
    production: 'https://ca-lobby-webapp.vercel.app',
    lastDeployment: 'Sep 28, 2025',
    status: 'Active'
  }
};

// Helper functions for status management
export const getStatusIcon = (status) => {
  switch (status) {
    case 'completed': return '✅';
    case 'current': return '🎯';
    case 'planned': return '📅';
    case 'in-progress': return '🔄';
    default: return '⏳';
  }
};

export const getStatusColor = (status) => {
  switch (status) {
    case 'completed': return '#28a745';
    case 'current': return '#007bff';
    case 'in-progress': return '#ffc107';
    case 'planned': return '#6c757d';
    default: return '#6c757d';
  }
};

// Template for adding new completed phases
export const PHASE_TEMPLATE = {
  id: 'PHASE_ID',           // e.g., '2c', '2d', '2.1'
  name: 'PHASE_NAME',       // e.g., 'Visualization Library Decision'
  status: 'completed',
  date: 'COMPLETION_DATE',  // e.g., 'Oct 5, 2025'
  description: 'DESCRIPTION' // Brief description of what was accomplished
};

// Instructions for updating:
// 1. Move phase from upcomingPhases to completedPhases
// 2. Update status to 'completed' and add completion date
// 3. Update currentPhase if this is the latest completed
// 4. Update lastUpdated date
// 5. Update currentFeatures array if new features were added