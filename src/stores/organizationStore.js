import { create } from 'zustand';

const useOrganizationStore = create((set, get) => ({
  // State
  selectedOrganization: null,
  organizationData: null,
  activities: [],
  lobbyists: [],
  relatedOrganizations: [],
  spendingTrends: [],
  loading: false,
  error: null,

  // Pagination state
  currentPage: 1,
  itemsPerPage: 10,
  totalActivities: 0,

  // Actions
  setSelectedOrganization: (org) => set({ selectedOrganization: org }),

  setOrganizationData: (data) => set({
    organizationData: data,
    loading: false
  }),

  setActivities: (activities) => set({
    activities,
    totalActivities: activities.length,
    loading: false
  }),

  setLobbyists: (lobbyists) => set({ lobbyists }),

  setRelatedOrganizations: (orgs) => set({ relatedOrganizations: orgs }),

  setSpendingTrends: (trends) => set({ spendingTrends: trends }),

  setLoading: (loading) => set({ loading }),

  setError: (error) => set({ error, loading: false }),

  setCurrentPage: (page) => set({ currentPage: page }),

  // Reset organization state
  clearOrganization: () => set({
    selectedOrganization: null,
    organizationData: null,
    activities: [],
    lobbyists: [],
    relatedOrganizations: [],
    spendingTrends: [],
    currentPage: 1,
    error: null
  }),

  // Computed getters
  getPaginatedActivities: () => {
    const { activities, currentPage, itemsPerPage } = get();
    const startIndex = (currentPage - 1) * itemsPerPage;
    const endIndex = startIndex + itemsPerPage;
    return activities.slice(startIndex, endIndex);
  },

  getTotalPages: () => {
    const { totalActivities, itemsPerPage } = get();
    return Math.ceil(totalActivities / itemsPerPage);
  }
}));

export default useOrganizationStore;