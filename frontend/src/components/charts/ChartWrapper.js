import React, { useState, useRef, useEffect } from 'react';
import { useUserStore, useAppStore } from '../../stores';

const ChartWrapper = ({
  children,
  title,
  height = 400,
  loading = false,
  error = null,
  className = '',
  onError
}) => {
  const { preferences } = useUserStore();
  const { addNotification } = useAppStore();
  const [isVisible, setIsVisible] = useState(true);
  const containerRef = useRef(null);

  const handleError = (errorMessage) => {
    addNotification({
      type: 'error',
      message: `Chart Error: ${errorMessage}`,
      duration: 5000
    });
    if (onError) {
      onError(errorMessage);
    }
  };

  // Intersection Observer to handle visibility
  useEffect(() => {
    const observer = new IntersectionObserver(
      ([entry]) => {
        setIsVisible(entry.isIntersecting);
      },
      { threshold: 0.1, rootMargin: '50px' }
    );

    if (containerRef.current) {
      observer.observe(containerRef.current);
    }

    return () => {
      if (containerRef.current) {
        observer.unobserve(containerRef.current);
      }
    };
  }, []);

  // Handle chart recovery
  const handleChartRecovery = () => {
    setIsVisible(false);
    setTimeout(() => setIsVisible(true), 100);
  };

  if (error) {
    return (
      <div className={`chart-container error ${className}`} ref={containerRef}>
        <h3>{title}</h3>
        <div className="chart-error">
          <p>Unable to load chart: {error}</p>
          <button onClick={handleChartRecovery}>
            Retry
          </button>
        </div>
      </div>
    );
  }

  if (loading) {
    return (
      <div className={`chart-container loading ${className}`}>
        <h3>{title}</h3>
        <div className="chart-skeleton" style={{ height }}>
          <div className="skeleton-content">
            <div className="skeleton-bar"></div>
            <div className="skeleton-bar"></div>
            <div className="skeleton-bar"></div>
            <div className="skeleton-bar"></div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div
      ref={containerRef}
      className={`chart-container ${preferences.theme} ${className}`}
      style={{ height: height + 40 }} // Add space for title
    >
      <div className="chart-header">
        <h3>{title}</h3>
        <button
          onClick={handleChartRecovery}
          className="chart-refresh-btn"
          title="Refresh chart"
          style={{
            background: 'none',
            border: 'none',
            cursor: 'pointer',
            fontSize: '14px',
            opacity: 0.7,
            marginLeft: 'auto'
          }}
        >
          🔄
        </button>
      </div>
      <div className="chart-content" style={{ height }}>
        {isVisible ? children : <div>Chart hidden during scroll</div>}
      </div>
    </div>
  );
};

export default ChartWrapper;