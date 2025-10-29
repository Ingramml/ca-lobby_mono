import { create } from 'zustand';
import { persist } from 'zustand/middleware';

// App Store - Application state and UI
const useAppStore = create(
  persist(
    (set, get) => ({
      // Navigation and UI
      currentPage: 'dashboard',
      sidebarCollapsed: false,

      // System status
      systemStatus: 'operational',
      notifications: [],

      // Global loading states
      globalLoading: false,

      // UI state
      mobileMenuOpen: false,

      // Actions
      setCurrentPage: (page) => set({ currentPage: page }),

      toggleSidebar: () => set((state) => ({
        sidebarCollapsed: !state.sidebarCollapsed
      })),

      setSidebarCollapsed: (collapsed) => set({
        sidebarCollapsed: collapsed
      }),

      toggleMobileMenu: () => set((state) => ({
        mobileMenuOpen: !state.mobileMenuOpen
      })),

      setMobileMenuOpen: (open) => set({
        mobileMenuOpen: open
      }),

      addNotification: (notification) => set((state) => ({
        notifications: [
          ...state.notifications,
          {
            id: Date.now(),
            type: 'info',
            autoHide: true,
            duration: 5000,
            ...notification,
            timestamp: new Date().toISOString()
          }
        ]
      })),

      removeNotification: (id) => set((state) => ({
        notifications: state.notifications.filter(n => n.id !== id)
      })),

      clearAllNotifications: () => set({
        notifications: []
      }),

      setGlobalLoading: (loading) => set({ globalLoading: loading }),

      setSystemStatus: (status) => set({ systemStatus: status }),

      // Utility actions
      showSuccessMessage: (message) => {
        get().addNotification({
          type: 'success',
          message,
          autoHide: true
        });
      },

      showErrorMessage: (message) => {
        get().addNotification({
          type: 'error',
          message,
          autoHide: false // Errors should be manually dismissed
        });
      },

      showInfoMessage: (message) => {
        get().addNotification({
          type: 'info',
          message,
          autoHide: true
        });
      },

      showWarningMessage: (message) => {
        get().addNotification({
          type: 'warning',
          message,
          autoHide: true,
          duration: 7000 // Warnings stay longer
        });
      }
    }),
    {
      name: 'ca-lobby-app-storage',
      // Only persist UI preferences, not temporary state
      partialize: (state) => ({
        sidebarCollapsed: state.sidebarCollapsed,
        currentPage: state.currentPage
      })
    }
  )
);

export default useAppStore;