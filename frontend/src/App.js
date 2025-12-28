import React, { useState } from 'react';
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
import OrganizationProfile from './components/OrganizationProfile';
import ErrorBoundary from './components/ErrorBoundary';

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
  const [navCollapsed, setNavCollapsed] = useState(false);

  return (
    <>
      <header className="App-header">
        <div className="header-content">
          <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
            <Link
              to="/"
              style={{
                fontSize: '2rem',
                textDecoration: 'none',
                cursor: 'pointer',
                display: 'flex',
                alignItems: 'center'
              }}
              title="Go to Dashboard"
            >
              🏛️
            </Link>
            <h1>California Lobbying Dashboard</h1>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
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
            <button
              onClick={() => setNavCollapsed(!navCollapsed)}
              style={{
                background: 'transparent',
                border: 'none',
                cursor: 'pointer',
                padding: '8px 12px',
                display: 'flex',
                alignItems: 'center',
                gap: '8px',
                color: '#ffffff',
                fontSize: '0.875rem',
                fontWeight: '500',
                transition: 'opacity 0.2s'
              }}
              onMouseEnter={(e) => e.currentTarget.style.opacity = '0.8'}
              onMouseLeave={(e) => e.currentTarget.style.opacity = '1'}
              aria-expanded={!navCollapsed}
              aria-controls="main-navigation"
            >
              <svg
                style={{
                  width: '16px',
                  height: '16px',
                  transform: navCollapsed ? 'rotate(-90deg)' : 'rotate(0deg)',
                  transition: 'transform 0.2s'
                }}
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
                xmlns="http://www.w3.org/2000/svg"
              >
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
              </svg>
              {navCollapsed ? 'Show Navigation' : 'Hide Navigation'}
            </button>

            {!navCollapsed && (
              <div id="main-navigation" className="nav-links">
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
            )}
          </div>
        </nav>
      </SignedIn>

      <main className="App-main">
        <SignedOut>
          <div className="welcome-section">
            <h2>California Lobbying Dashboard</h2>
            <p>Please sign in to access the search dashboard.</p>
          </div>
        </SignedOut>

        <SignedIn>
          <ErrorBoundary>
            <Routes>
              <Route path="/" element={<Dashboard />} />
              <Route path="/search" element={<Search />} />
              <Route path="/settings" element={<Settings />} />
              <Route path="/organization/:organizationName" element={<OrganizationProfile />} />
            </Routes>
          </ErrorBoundary>
        </SignedIn>
      </main>
    </>
  );
}


export default App;