export class DataOptimizer {
  constructor() {
    this.debounceTimers = new Map();
    this.intersectionObserver = null;
    this.setupIntersectionObserver();
  }

  // Debounce search requests for mobile typing
  debounceSearch(searchFn, delay = 300) {
    return (...args) => {
      const key = 'search';

      if (this.debounceTimers.has(key)) {
        clearTimeout(this.debounceTimers.get(key));
      }

      const timer = setTimeout(() => {
        searchFn(...args);
        this.debounceTimers.delete(key);
      }, delay);

      this.debounceTimers.set(key, timer);
    };
  }

  // Lazy loading for charts and heavy components
  setupIntersectionObserver() {
    if ('IntersectionObserver' in window) {
      this.intersectionObserver = new IntersectionObserver(
        (entries) => {
          entries.forEach(entry => {
            if (entry.isIntersecting) {
              entry.target.dispatchEvent(new CustomEvent('lazyLoad'));
              this.intersectionObserver.unobserve(entry.target);
            }
          });
        },
        { threshold: 0.1 }
      );
    }
  }

  observeElement(element) {
    if (this.intersectionObserver && element) {
      this.intersectionObserver.observe(element);
    }
  }

  // Batch API requests for efficiency
  createBatchProcessor(processFn, batchSize = 5, delay = 100) {
    let batch = [];
    let timer = null;

    return (item) => {
      batch.push(item);

      if (batch.length >= batchSize) {
        processFn([...batch]);
        batch = [];
        if (timer) {
          clearTimeout(timer);
          timer = null;
        }
      } else if (!timer) {
        timer = setTimeout(() => {
          if (batch.length > 0) {
            processFn([...batch]);
            batch = [];
          }
          timer = null;
        }, delay);
      }
    };
  }

  // Progressive data loading for large datasets
  async loadDataProgressively(loadFn, totalItems, batchSize = 25) {
    const results = [];
    let loaded = 0;

    while (loaded < totalItems) {
      const batch = await loadFn(loaded, batchSize);
      results.push(...batch);
      loaded += batch.length;

      // Allow UI to update between batches
      await new Promise(resolve => setTimeout(resolve, 10));
    }

    return results;
  }
}

// Performance monitoring
export class APIPerformanceMonitor {
  constructor() {
    this.metrics = new Map();
    this.performanceEntries = [];
  }

  startTiming(key) {
    this.metrics.set(key, {
      start: performance.now(),
      key
    });
  }

  endTiming(key) {
    const metric = this.metrics.get(key);
    if (metric) {
      const duration = performance.now() - metric.start;

      this.performanceEntries.push({
        key,
        duration,
        timestamp: new Date()
      });

      // Log slow requests (>2 seconds)
      if (duration > 2000) {
        console.warn(`Slow API request: ${key} took ${duration.toFixed(2)}ms`);
      }

      this.metrics.delete(key);
      return duration;
    }
  }

  getAverageTime(key) {
    const entries = this.performanceEntries.filter(entry => entry.key === key);
    if (entries.length === 0) return 0;

    const total = entries.reduce((sum, entry) => sum + entry.duration, 0);
    return total / entries.length;
  }

  getPerformanceReport() {
    const report = {};
    const uniqueKeys = [...new Set(this.performanceEntries.map(entry => entry.key))];

    uniqueKeys.forEach(key => {
      const entries = this.performanceEntries.filter(entry => entry.key === key);
      report[key] = {
        count: entries.length,
        average: this.getAverageTime(key),
        min: Math.min(...entries.map(e => e.duration)),
        max: Math.max(...entries.map(e => e.duration))
      };
    });

    return report;
  }
}

export const dataOptimizer = new DataOptimizer();
export const performanceMonitor = new APIPerformanceMonitor();