import { apiClient } from '../services/apiClient';
import { useSearchAPI, useAnalyticsAPI } from '../hooks/useAPI';

describe('CA Lobby API Client', () => {
  beforeEach(() => {
    // Reset cache and state
    apiClient.cache.clear();
    jest.clearAllMocks();
  });

  describe('Search API', () => {
    test('should handle successful search request', async () => {
      const mockResponse = {
        data: [
          {
            id: '1',
            organization: 'Test Org',
            amount: 5000,
            date: '2025-01-01'
          }
        ],
        pagination: {
          current_page: 1,
          total_pages: 1,
          total_results: 1
        }
      };

      global.fetch = jest.fn().mockResolvedValue({
        ok: true,
        json: () => Promise.resolve(mockResponse)
      });

      const result = await apiClient.searchLobbyData({ query: 'test' });

      expect(result).toEqual(mockResponse);
      expect(fetch).toHaveBeenCalledWith(
        expect.stringContaining('/search'),
        expect.any(Object)
      );
    });

    test('should handle network errors gracefully', async () => {
      global.fetch = jest.fn().mockRejectedValue(new Error('Network error'));

      await expect(apiClient.searchLobbyData({ query: 'test' }))
        .rejects.toThrow('Network error');
    });

    test('should cache GET requests', async () => {
      const mockResponse = { data: [] };

      global.fetch = jest.fn().mockResolvedValue({
        ok: true,
        json: () => Promise.resolve(mockResponse)
      });

      // First request
      await apiClient.searchLobbyData({ query: 'test' });

      // Second request should use cache
      await apiClient.searchLobbyData({ query: 'test' });

      expect(fetch).toHaveBeenCalledTimes(1);
    });
  });

  describe('Mobile Performance', () => {
    test('should timeout requests after configured time', async () => {
      jest.useFakeTimers();

      global.fetch = jest.fn().mockImplementation(
        () => new Promise(resolve => setTimeout(resolve, 15000))
      );

      const promise = apiClient.searchLobbyData({ query: 'test' });

      jest.advanceTimersByTime(11000);

      await expect(promise).rejects.toThrow();

      jest.useRealTimers();
    });
  });
});

// Performance benchmarks
export const performanceBenchmarks = {
  searchResponse: {
    target: '< 2 seconds',
    mobile3G: '< 5 seconds',
    acceptable: '< 10 seconds'
  },
  chartData: {
    target: '< 1 second',
    mobile3G: '< 3 seconds',
    acceptable: '< 5 seconds'
  },
  export: {
    target: '< 5 seconds',
    mobile3G: '< 15 seconds',
    acceptable: '< 30 seconds'
  }
};