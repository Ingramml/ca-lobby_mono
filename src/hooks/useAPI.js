import { useCallback, useEffect } from 'react';
import { apiClient } from '../services/apiClient';
import { useSearchStore } from '../stores/searchStore';
import { useUserStore } from '../stores/userStore';
import { useAppStore } from '../stores/appStore';

export const useSearchAPI = () => {
  const {
    query,
    filters,
    results,
    loading,
    setResults,
    setLoading,
    addToHistory
  } = useSearchStore();

  const search = useCallback(async (searchQuery = query, searchFilters = filters, page = 1) => {
    setLoading(true);

    try {
      const searchParams = {
        query: searchQuery,
        ...searchFilters
      };

      const response = await apiClient.searchLobbyData(searchParams, page);

      setResults(response.data);

      // Add to search history
      addToHistory({
        query: searchQuery,
        filters: searchFilters,
        timestamp: new Date(),
        resultCount: response.total_results
      });

    } catch (error) {
      console.error('Search error:', error);
      setResults([]);
    } finally {
      setLoading(false);
    }
  }, [query, filters, setResults, setLoading, addToHistory]);

  return {
    search,
    results,
    loading,
    filters,
    query
  };
};

export const useAnalyticsAPI = () => {
  const { addNotification } = useAppStore();

  const getTrends = useCallback(async (timeframe, category) => {
    try {
      return await apiClient.getAnalyticsTrends(timeframe, category);
    } catch (error) {
      addNotification({
        type: 'error',
        message: 'Failed to load trend data'
      });
      throw error;
    }
  }, [addNotification]);

  const getOrganizationData = useCallback(async (limit, timeframe) => {
    try {
      return await apiClient.getOrganizationAnalytics(limit, timeframe);
    } catch (error) {
      addNotification({
        type: 'error',
        message: 'Failed to load organization data'
      });
      throw error;
    }
  }, [addNotification]);

  return {
    getTrends,
    getOrganizationData
  };
};

export const useUserAPI = () => {
  const { userProfile, isAuthenticated } = useUserStore();
  const { addNotification } = useAppStore();

  const getSavedSearches = useCallback(async () => {
    if (!isAuthenticated) return [];

    try {
      return await apiClient.getSavedSearches();
    } catch (error) {
      addNotification({
        type: 'error',
        message: 'Failed to load saved searches'
      });
      return [];
    }
  }, [isAuthenticated, addNotification]);

  const saveSearch = useCallback(async (name, filters) => {
    if (!isAuthenticated) {
      addNotification({
        type: 'warning',
        message: 'Please sign in to save searches'
      });
      return false;
    }

    try {
      await apiClient.saveSearch(name, filters);
      addNotification({
        type: 'success',
        message: 'Search saved successfully'
      });
      return true;
    } catch (error) {
      addNotification({
        type: 'error',
        message: 'Failed to save search'
      });
      return false;
    }
  }, [isAuthenticated, addNotification]);

  return {
    getSavedSearches,
    saveSearch,
    isAuthenticated
  };
};

export const useExportAPI = () => {
  const { addNotification } = useAppStore();

  const exportData = useCallback(async (format, filters, columns = []) => {
    try {
      addNotification({
        type: 'info',
        message: `Preparing ${format.toUpperCase()} export...`
      });

      const response = await apiClient.exportData(format, filters, columns);

      addNotification({
        type: 'success',
        message: 'Export completed successfully'
      });

      return response;
    } catch (error) {
      addNotification({
        type: 'error',
        message: 'Export failed. Please try again.'
      });
      throw error;
    }
  }, [addNotification]);

  return {
    exportData
  };
};

export const useSystemAPI = () => {
  const { addNotification } = useAppStore();

  const getSystemStatus = useCallback(async () => {
    try {
      return await apiClient.getSystemStatus();
    } catch (error) {
      addNotification({
        type: 'warning',
        message: 'Unable to check system status'
      });
      return {
        status: 'unknown',
        api_version: '1.0.0'
      };
    }
  }, [addNotification]);

  return {
    getSystemStatus
  };
};