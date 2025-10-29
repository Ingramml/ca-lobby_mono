// Chart configuration utilities for responsive design

export const useResponsiveChart = () => {
  const isMobile = window.innerWidth <= 768;
  const isTablet = window.innerWidth <= 1024 && window.innerWidth > 768;

  return {
    isMobile,
    isTablet,
    isDesktop: !isMobile && !isTablet
  };
};

export const getMobileChartConfig = (isMobile = false) => ({
  responsive: true,
  maintainAspectRatio: false,
  margin: {
    top: isMobile ? 10 : 20,
    right: isMobile ? 15 : 30,
    left: isMobile ? 15 : 20,
    bottom: isMobile ? 40 : 20
  }
});

export const getMobileAxisConfig = (isMobile = false) => ({
  tick: {
    fontSize: isMobile ? 10 : 12,
    fill: '#6b7280'
  },
  axisLine: {
    strokeWidth: 1,
    stroke: '#e5e7eb'
  },
  tickLine: {
    strokeWidth: 1,
    stroke: '#e5e7eb'
  }
});

export const getMobileLegendConfig = (isMobile = false) => ({
  wrapperStyle: {
    fontSize: isMobile ? '10px' : '12px',
    paddingTop: '8px'
  },
  iconType: isMobile ? 'circle' : 'rect'
});

export const getMobileTooltipConfig = (theme = 'light') => {
  const colors = {
    light: {
      background: '#ffffff',
      border: '#e5e7eb',
      text: '#1f2937'
    },
    dark: {
      background: '#1f2937',
      border: '#374151',
      text: '#f9fafb'
    }
  };

  const themeColors = colors[theme] || colors.light;

  return {
    contentStyle: {
      backgroundColor: themeColors.background,
      border: `1px solid ${themeColors.border}`,
      borderRadius: '6px',
      boxShadow: '0 4px 12px rgba(0, 0, 0, 0.15)',
      fontSize: '12px',
      color: themeColors.text
    },
    labelStyle: {
      color: themeColors.text,
      fontSize: '11px',
      fontWeight: 'bold'
    }
  };
};

// Chart color schemes
export const getChartColors = (theme = 'light') => {
  const schemes = {
    light: {
      primary: '#2563eb',
      secondary: '#3b82f6',
      accent: '#60a5fa',
      success: '#10b981',
      warning: '#f59e0b',
      error: '#ef4444',
      palette: [
        '#2563eb', '#3b82f6', '#60a5fa', '#93c5fd', '#dbeafe',
        '#10b981', '#34d399', '#6ee7b7', '#a7f3d0', '#d1fae5',
        '#f59e0b', '#fbbf24', '#fcd34d', '#fde68a', '#fef3c7',
        '#ef4444', '#f87171', '#fca5a5', '#fecaca', '#fee2e2'
      ]
    },
    dark: {
      primary: '#60a5fa',
      secondary: '#93c5fd',
      accent: '#dbeafe',
      success: '#34d399',
      warning: '#fbbf24',
      error: '#f87171',
      palette: [
        '#60a5fa', '#93c5fd', '#dbeafe', '#bfdbfe', '#e0e7ff',
        '#34d399', '#6ee7b7', '#a7f3d0', '#d1fae5', '#ecfdf5',
        '#fbbf24', '#fcd34d', '#fde68a', '#fef3c7', '#fffbeb',
        '#f87171', '#fca5a5', '#fecaca', '#fee2e2', '#fef2f2'
      ]
    }
  };

  return schemes[theme] || schemes.light;
};

// Format utilities
export const formatters = {
  currency: (value, compact = false) => {
    if (compact && value >= 1000000) {
      return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD',
        notation: 'compact',
        maximumFractionDigits: 1
      }).format(value);
    }

    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0
    }).format(value);
  },

  number: (value, compact = false) => {
    if (compact && value >= 1000) {
      return new Intl.NumberFormat('en-US', {
        notation: 'compact',
        maximumFractionDigits: 1
      }).format(value);
    }

    return new Intl.NumberFormat('en-US').format(value);
  },

  percentage: (value, decimals = 1) => {
    return `${value.toFixed(decimals)}%`;
  },

  date: (dateString, format = 'short') => {
    const date = new Date(dateString);

    if (format === 'short') {
      return date.toLocaleDateString('en-US', {
        month: 'short',
        day: 'numeric'
      });
    }

    if (format === 'long') {
      return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'long',
        day: 'numeric'
      });
    }

    return date.toLocaleDateString('en-US');
  }
};

// Chart export utilities
export const exportChartConfig = {
  filename: (chartType, timestamp = new Date()) => {
    const dateStr = timestamp.toISOString().split('T')[0];
    return `ca-lobby-${chartType}-${dateStr}`;
  },

  // SVG to PNG conversion (requires html2canvas or similar library)
  toPNG: async (element, filename) => {
    // This would require html2canvas library
    // For now, return a placeholder function
    console.log(`Export to PNG: ${filename}`);
    return Promise.resolve('PNG export would be implemented here');
  },

  // SVG to PDF conversion (requires jsPDF or similar library)
  toPDF: async (element, filename) => {
    // This would require jsPDF library
    // For now, return a placeholder function
    console.log(`Export to PDF: ${filename}`);
    return Promise.resolve('PDF export would be implemented here');
  }
};