// CA Lobby State Management - Zustand Stores
// Central export file for all application stores

import useSearchStore from './searchStore';
import useUserStore from './userStore';
import useAppStore from './appStore';
import useOrganizationStore from './organizationStore';

// Export individual stores
export {
  useSearchStore,
  useUserStore,
  useAppStore,
  useOrganizationStore
};

// Store utilities and helpers
export const resetAllStores = () => {
  useSearchStore.getState().resetSearch();
  useUserStore.getState().resetUser();
  // Note: App store typically doesn't need reset as it contains UI preferences
};

// Store selectors for common operations
export const searchSelectors = {
  // Search state selectors
  getSearchQuery: () => useSearchStore.getState().query,
  getFilters: () => useSearchStore.getState().filters,
  getResults: () => useSearchStore.getState().results,
  isLoading: () => useSearchStore.getState().loading,
  getError: () => useSearchStore.getState().error,

  // History selectors
  getSearchHistory: () => useSearchStore.getState().searchHistory,
  getSavedSearches: () => useSearchStore.getState().savedSearches,

  // Combined selectors
  getCurrentSearch: () => {
    const state = useSearchStore.getState();
    return {
      query: state.query,
      filters: state.filters,
      resultCount: state.results.length
    };
  }
};

export const userSelectors = {
  // Auth selectors
  isAuthenticated: () => useUserStore.getState().isAuthenticated,
  getUserProfile: () => useUserStore.getState().userProfile,

  // Preferences selectors
  getPreferences: () => useUserStore.getState().preferences,
  getTheme: () => useUserStore.getState().preferences.theme,
  getPageSize: () => useUserStore.getState().preferences.pageSize,

  // Activity selectors
  getBookmarks: () => useUserStore.getState().bookmarks,
  getRecentActivity: () => useUserStore.getState().recentActivity
};

export const appSelectors = {
  // Navigation selectors
  getCurrentPage: () => useAppStore.getState().currentPage,
  isSidebarCollapsed: () => useAppStore.getState().sidebarCollapsed,
  isMobileMenuOpen: () => useAppStore.getState().mobileMenuOpen,

  // Status selectors
  getSystemStatus: () => useAppStore.getState().systemStatus,
  getNotifications: () => useAppStore.getState().notifications,
  isGlobalLoading: () => useAppStore.getState().globalLoading
};

// Combined store state selector (useful for debugging)
export const getAllStoreState = () => ({
  search: useSearchStore.getState(),
  user: useUserStore.getState(),
  app: useAppStore.getState()
});

// Default export combines all stores for convenience
export default {
  useSearchStore,
  useUserStore,
  useAppStore,
  useOrganizationStore,
  selectors: {
    search: searchSelectors,
    user: userSelectors,
    app: appSelectors
  },
  utils: {
    resetAllStores,
    getAllStoreState
  }
};