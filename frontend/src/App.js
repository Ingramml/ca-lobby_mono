import React, { lazy, Suspense } from 'react';
import './App.css';
import { BrowserRouter as Router, Routes, Route, Link, useLocation } from 'react-router-dom';
import {
  SignedIn,
  SignedOut,
  SignInButton,
  UserButton
} from '@clerk/clerk-react';

// Import core page components
import Dashboard from './components/Dashboard';
import Search from './components/Search';
import Settings from './components/Settings';
import PhaseStatus from './components/PhaseStatus';
import ErrorBoundary from './components/ErrorBoundary';

// Lazy load OrganizationProfile for code splitting
const OrganizationProfile = lazy(() => import('./components/OrganizationProfile'));

function App() {
  return (
    <Router>
      <div className="App">
        <AppContent />
      </div>
    </Router>
  );
}

function AppContent() {
  const location = useLocation();

  return (
    <>
      <header className="App-header">
        <div className="header-content">
          <h1>Welcome to TPC's CA lobby search_gitdeopoy</h1>
          <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
            <div style={{ position: 'relative' }}>
              <PhaseStatus />
            </div>
            <SignedOut>
              <SignInButton mode="modal">
                <button className="sign-in-btn">Sign In</button>
              </SignInButton>
            </SignedOut>
            <SignedIn>
              <UserButton />
            </SignedIn>
          </div>
        </div>
      </header>

      <SignedIn>
        <nav className="main-nav">
          <div className="nav-content">
            <div className="nav-links">
              <Link
                to="/"
                className={`nav-link ${location.pathname === '/' ? 'active' : ''}`}
              >
                📊 Dashboard
              </Link>
              <Link
                to="/search"
                className={`nav-link ${location.pathname === '/search' ? 'active' : ''}`}
              >
                🔍 Search
              </Link>
              <Link
                to="/settings"
                className={`nav-link ${location.pathname === '/settings' ? 'active' : ''}`}
              >
                ⚙️ Admin
              </Link>
            </div>
          </div>
        </nav>
      </SignedIn>

      <main className="App-main">
        <SignedOut>
          <div className="welcome-section">
            <h2>Welcome to TPC's CA lobby search_gitdeopoy</h2>
            <p>Please sign in to access the search dashboard.</p>
          </div>
        </SignedOut>

        <SignedIn>
          <ErrorBoundary>
            <Routes>
              <Route path="/" element={<Dashboard />} />
              <Route path="/search" element={<Search />} />
              <Route path="/settings" element={<Settings />} />
              <Route
                path="/organization/:organizationName"
                element={
                  <Suspense fallback={
                    <div className="loading-container" style={{ padding: '40px', textAlign: 'center' }}>
                      <div className="loading-spinner"></div>
                      <p>Loading organization profile...</p>
                    </div>
                  }>
                    <OrganizationProfile />
                  </Suspense>
                }
              />
            </Routes>
          </ErrorBoundary>
        </SignedIn>
      </main>
    </>
  );
}


export default App;