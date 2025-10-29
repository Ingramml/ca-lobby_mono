import React, { useState } from 'react';
import { PROJECT_STATUS, getStatusIcon, getStatusColor } from '../config/projectStatus';

function PhaseStatus() {
  const [isExpanded, setIsExpanded] = useState(false);


  return (
    <div className="phase-status">
      <div
        className="phase-status-badge"
        onClick={() => setIsExpanded(!isExpanded)}
        style={{
          backgroundColor: '#f8f9fa',
          border: '1px solid #dee2e6',
          borderRadius: '8px',
          padding: '8px 12px',
          cursor: 'pointer',
          display: 'inline-flex',
          alignItems: 'center',
          gap: '8px',
          fontSize: '14px',
          fontWeight: '500',
          color: '#495057',
          userSelect: 'none',
          transition: 'all 0.2s ease'
        }}
      >
        <span>🚀</span>
        <span>{PROJECT_STATUS.currentPhase}</span>
        <span style={{
          backgroundColor: getStatusColor('completed'),
          color: 'white',
          borderRadius: '12px',
          padding: '2px 8px',
          fontSize: '12px',
          fontWeight: 'bold'
        }}>
          {PROJECT_STATUS.stats.completionPercentage}%
        </span>
        <span style={{ fontSize: '12px' }}>
          {isExpanded ? '▼' : '▶'}
        </span>
      </div>

      {isExpanded && (
        <div
          className="phase-status-details"
          style={{
            position: 'absolute',
            top: '100%',
            right: '0',
            backgroundColor: 'white',
            border: '1px solid #dee2e6',
            borderRadius: '8px',
            boxShadow: '0 4px 12px rgba(0,0,0,0.15)',
            padding: '16px',
            minWidth: '400px',
            zIndex: 1000,
            marginTop: '4px'
          }}
        >
          <div style={{ marginBottom: '16px' }}>
            <h4 style={{ margin: '0 0 8px 0', color: '#212529' }}>CA Lobby Development Status</h4>
            <p style={{ margin: '0', fontSize: '14px', color: '#6c757d' }}>
              Version {PROJECT_STATUS.version} • Updated {PROJECT_STATUS.lastUpdated}
            </p>
          </div>

          <div style={{ marginBottom: '16px' }}>
            <div style={{
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center',
              marginBottom: '8px'
            }}>
              <span style={{ fontSize: '14px', fontWeight: '600' }}>Progress</span>
              <span style={{ fontSize: '14px', color: '#6c757d' }}>
                {PROJECT_STATUS.stats.completedCount} of {PROJECT_STATUS.stats.totalPhases} phases
              </span>
            </div>
            <div style={{
              width: '100%',
              height: '8px',
              backgroundColor: '#e9ecef',
              borderRadius: '4px',
              overflow: 'hidden'
            }}>
              <div style={{
                width: `${PROJECT_STATUS.stats.completionPercentage}%`,
                height: '100%',
                backgroundColor: '#28a745',
                transition: 'width 0.3s ease'
              }} />
            </div>
          </div>

          <div style={{ marginBottom: '16px' }}>
            <h5 style={{ margin: '0 0 8px 0', fontSize: '14px', fontWeight: '600', color: '#212529' }}>
              ✅ Completed Phases
            </h5>
            <div style={{ maxHeight: '120px', overflowY: 'auto' }}>
              {PROJECT_STATUS.completedPhases.map((phase) => (
                <div key={phase.id} style={{
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center',
                  padding: '4px 0',
                  fontSize: '13px'
                }}>
                  <span>
                    <span style={{ marginRight: '6px' }}>{getStatusIcon(phase.status)}</span>
                    <strong>Phase {phase.id}:</strong> {phase.name}
                  </span>
                  <span style={{ color: '#6c757d', fontSize: '12px' }}>{phase.date}</span>
                </div>
              ))}
            </div>
          </div>

          <div>
            <h5 style={{ margin: '0 0 8px 0', fontSize: '14px', fontWeight: '600', color: '#212529' }}>
              📅 Upcoming Phases
            </h5>
            <div>
              {PROJECT_STATUS.upcomingPhases.slice(0, 3).map((phase) => (
                <div key={phase.id} style={{
                  display: 'flex',
                  alignItems: 'center',
                  padding: '4px 0',
                  fontSize: '13px',
                  color: '#6c757d'
                }}>
                  <span style={{ marginRight: '6px' }}>{getStatusIcon(phase.status)}</span>
                  <span><strong>Phase {phase.id}:</strong> {phase.name}</span>
                </div>
              ))}
            </div>
          </div>

          <div style={{
            marginTop: '12px',
            paddingTop: '12px',
            borderTop: '1px solid #e9ecef',
            fontSize: '12px',
            color: '#6c757d'
          }}>
            🔧 <strong>Current Features:</strong> Zustand State Management, Clerk Auth, 5 Components
          </div>
        </div>
      )}
    </div>
  );
}

export default PhaseStatus;