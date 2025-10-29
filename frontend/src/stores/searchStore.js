import { create } from 'zustand';
import { persist } from 'zustand/middleware';

// Search Store - Core functionality for lobby data search
const useSearchStore = create(
  persist(
    (set, get) => ({
      // Search state
      query: '',
      filters: {
        dateRange: 'all',
        organization: '',
        lobbyist: '',
        category: 'all',
        amountRange: { min: 0, max: 1000000 }
      },
      results: [],
      loading: false,
      error: null,

      // Search history and persistence
      searchHistory: [],
      savedSearches: [],
      lastSearchTime: null,

      // Actions
      setQuery: (query) => set({ query }),

      setFilters: (newFilters) => set((state) => ({
        filters: { ...state.filters, ...newFilters }
      })),

      setResults: (results) => set({
        results,
        loading: false,
        lastSearchTime: new Date().toISOString()
      }),

      setLoading: (loading) => set({ loading }),

      setError: (error) => set({ error, loading: false }),

      addToHistory: (search) => set((state) => ({
        searchHistory: [
          {
            query: search.query,
            filters: search.filters,
            timestamp: new Date().toISOString(),
            resultCount: search.resultCount || 0
          },
          ...state.searchHistory.slice(0, 9) // Keep last 10 searches
        ]
      })),

      saveSearch: (name, search) => set((state) => ({
        savedSearches: [
          ...state.savedSearches,
          {
            id: Date.now(),
            name,
            query: search.query,
            filters: search.filters,
            dateCreated: new Date().toISOString()
          }
        ]
      })),

      removeSavedSearch: (id) => set((state) => ({
        savedSearches: state.savedSearches.filter(search => search.id !== id)
      })),

      clearResults: () => set({
        results: [],
        error: null,
        lastSearchTime: null
      }),

      clearHistory: () => set({
        searchHistory: []
      }),

      // Reset search state
      resetSearch: () => set({
        query: '',
        filters: {
          dateRange: 'all',
          organization: '',
          lobbyist: '',
          category: 'all',
          amountRange: { min: 0, max: 1000000 }
        },
        results: [],
        loading: false,
        error: null
      })
    }),
    {
      name: 'ca-lobby-search-storage',
      // Only persist certain fields
      partialize: (state) => ({
        savedSearches: state.savedSearches,
        searchHistory: state.searchHistory,
        filters: state.filters // Persist last used filters
      })
    }
  )
);

export default useSearchStore;