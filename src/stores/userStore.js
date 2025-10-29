import { create } from 'zustand';
import { persist } from 'zustand/middleware';

// User Store - Authentication and preferences
const useUserStore = create(
  persist(
    (set, get) => ({
      // User authentication (synced with Clerk)
      isAuthenticated: false,
      userProfile: null,

      // User preferences
      preferences: {
        theme: 'light',
        pageSize: 25,
        defaultView: 'list',
        notifications: true,
        autoSave: true,
        language: 'en'
      },

      // User activity
      recentActivity: [],
      bookmarks: [],
      lastVisit: null,

      // Actions
      setAuthenticated: (isAuthenticated) => set({ isAuthenticated }),

      setUserProfile: (userProfile) => set({
        userProfile,
        lastVisit: new Date().toISOString()
      }),

      updatePreferences: (newPrefs) => set((state) => ({
        preferences: { ...state.preferences, ...newPrefs }
      })),

      addBookmark: (item) => set((state) => {
        // Check if bookmark already exists
        const exists = state.bookmarks.some(bookmark => bookmark.id === item.id);
        if (exists) return state;

        return {
          bookmarks: [
            ...state.bookmarks,
            {
              ...item,
              dateBookmarked: new Date().toISOString()
            }
          ]
        };
      }),

      removeBookmark: (itemId) => set((state) => ({
        bookmarks: state.bookmarks.filter(bookmark => bookmark.id !== itemId)
      })),

      addActivity: (activity) => set((state) => ({
        recentActivity: [
          {
            ...activity,
            timestamp: new Date().toISOString(),
            id: Date.now()
          },
          ...state.recentActivity.slice(0, 19) // Keep last 20 activities
        ]
      })),

      clearActivity: () => set({
        recentActivity: []
      }),

      // Sync with Clerk authentication (with validation)
      syncWithClerk: (clerkUser) => set((state) => {
        try {
          // Prevent unnecessary updates if user hasn't changed
          const currentUserId = state.userProfile?.id;
          const newUserId = clerkUser?.id;

          if (currentUserId === newUserId && !!clerkUser === state.isAuthenticated) {
            return state; // No change needed
          }

          const newState = {
            ...state,
            isAuthenticated: !!clerkUser,
            userProfile: clerkUser ? {
              id: clerkUser.id,
              email: clerkUser.primaryEmailAddress?.emailAddress || '',
              name: clerkUser.fullName || `${clerkUser.firstName || ''} ${clerkUser.lastName || ''}`.trim() || 'User',
              firstName: clerkUser.firstName || '',
              lastName: clerkUser.lastName || '',
              imageUrl: clerkUser.imageUrl || ''
            } : null,
            lastVisit: new Date().toISOString()
          };

          return newState;
        } catch (error) {
          console.error('Error syncing with Clerk:', error);
          return state; // Return unchanged state on error
        }
      }),

      // Reset user state (logout)
      resetUser: () => set({
        isAuthenticated: false,
        userProfile: null,
        recentActivity: [],
        bookmarks: []
        // Keep preferences even after logout
      })
    }),
    {
      name: 'ca-lobby-user-storage',
      // Persist user preferences and bookmarks, but not session data
      partialize: (state) => ({
        preferences: state.preferences,
        bookmarks: state.bookmarks,
        recentActivity: state.recentActivity
      })
    }
  )
);

export default useUserStore;