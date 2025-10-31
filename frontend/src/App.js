import React from 'react';
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
            <h1>Welcome to TPC's CA lobby search_gitdeopoy</h1>
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
              <Route path="/organization/:organizationName" element={<OrganizationProfile />} />
            </Routes>
          </ErrorBoundary>
        </SignedIn>
      </main>
    </>
  );
}


export default App;