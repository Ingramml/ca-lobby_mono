# CA Lobby Search System - Claude Code Reference

**Project:** California Lobby Search System
**Project Code:** CA_LOBBY
**Current Status:** Phase 2f.1 - Organization Profile Foundation (COMPLETED)
**Last Updated:** September 30, 2025

> **⚠️ CRITICAL REFERENCE**: Always consult [`Documentation/General/MASTER_PROJECT_PLAN.md`](Documentation/General/MASTER_PROJECT_PLAN.md) before planning or executing any new phase.
**⚠️ Fabrication Rules**
- Never Fabricate any information, steps or anything else displayed to user


## 🎯 Project Overview

### Mission Statement
Create a comprehensive, publicly accessible search system for California lobby data that enables transparency and analysis of lobbying activities, expenditures, and associations.

### Current Architecture
- **Frontend**: React app with Clerk authentication (`src/`)
- **Backend**: Flask API with BigQuery integration (`webapp/backend/`)
- **Database**: BigQuery (data processing files preserved in main branch)
- **Deployment**: Vercel with automated builds
- **Data Source**: Big Local News (BLN) API

## 📋 Current Project Status

### ✅ Completed Phases
- **Phase 1.1**: Foundation and Data Pipeline Infrastructure (COMPLETED)
- **Phase 1.2**: Enhanced Deployment Pipeline (COMPLETED)
- **Phase 1.3**: Frontend-Backend Integration (COMPLETED)
- **Phase 2a.1**: Component Structure Documentation (COMPLETED)
- **Phase 2a.2**: Enhancement Strategy Definition (COMPLETED)
- **Phase 2b**: State Management Implementation (COMPLETED - Zustand selected)
- **Phase 2f.1**: Organization Profile Foundation (COMPLETED - September 30, 2025)
  - **Report**: [`Documentation/Phase2/Reports/ORGANIZATION_PROFILE_PHASE1_COMPLETION_REPORT.md`](Documentation/Phase2/Reports/ORGANIZATION_PROFILE_PHASE1_COMPLETION_REPORT.md)

### 🎯 Current Phase: Phase 2f.2 - Organization Profile Enhanced Visualization
**Duration**: Estimated 1-2 days
**Next Milestone**: Enhanced data visualization with charts

**Objective**: Add Recharts visualizations, activity timeline, and enhanced analytics to organization profile pages.

### 📅 Upcoming Phases
- **Phase 2f.3**: Organization Profile Production Polish (Days TBD)
- **Phase 2c**: Visualization Library Decision (Days 5-6) - ✅ COMPLETED (Recharts selected)
- **Phase 2d**: Mobile-First CSS Strategy (Days 7-8)
- **Phase 2e**: API Design Specification (Days 9-10)
- **Phase 2.1**: Advanced Search and Analytics (January 2026)

## ⚡ Development Commands

### Frontend Development
```bash
# Start React development server
npm start

# Build for production
npm run build

# Run tests
npm test

# Install dependencies
npm install
```

### Backend Development
```bash
# Navigate to backend
cd webapp/backend

# Install Python dependencies
pip install -r requirements.txt

# Run Flask development server
python run.py

# Run tests
python -m pytest tests/
```

### Deployment
```bash
# Deploy to Vercel (automatic on push to main)
vercel --prod

# Local Vercel preview
vercel dev
```

## 📁 Key File Locations

### Frontend Structure
```
src/
├── components/                # React components
│   ├── Dashboard.js          # Main dashboard
│   ├── Search.js             # Search functionality with clickable org names
│   ├── OrganizationProfile.js # Organization profile pages (Phase 2f complete)
│   ├── ActivityList.js       # Paginated activity list with export
│   ├── ActivitySummary.js    # Organization metrics display
│   ├── LobbyistNetwork.js    # Lobbyist network visualization
│   ├── RelatedOrganizations.js # Similar organizations
│   ├── Analytics.js          # Analytics views
│   ├── Reports.js            # Report generation
│   └── Settings.js           # User settings
├── stores/                    # Zustand state management
│   ├── organizationStore.js  # Organization profile state (Phase 2f)
│   ├── searchStore.js        # Search state and results
│   ├── userStore.js          # User preferences
│   └── appStore.js           # Application state
├── utils/                     # Utility functions
│   ├── sampleData.js         # Demo data generation
│   └── exportHelpers.js      # CSV/JSON export utilities (Phase 3)
├── App.js                     # Main app with lazy-loaded routes
├── App.css                    # Global styles + accessibility (Phase 3)
└── index.js                   # Entry point
```

### Backend Structure
```
webapp/backend/
├── app.py               # Flask application
├── auth.py              # Authentication logic
├── data_service.py      # Data access layer
├── database.py          # Database connections
├── middleware.py        # Request middleware
├── requirements.txt     # Python dependencies
└── run.py               # Development server
```

### Configuration Files
- `package.json` - Frontend dependencies and scripts
- `vercel.json` - Deployment configuration
- `.env` - Environment variables (not tracked)
- `.gitignore` - Git ignore patterns

## 📚 Documentation Structure

### Always Reference First
**[`Documentation/General/MASTER_PROJECT_PLAN.md`](Documentation/General/MASTER_PROJECT_PLAN.md)** - **MANDATORY reading before any phase planning or execution**

### Organized Documentation
```
Documentation/
├── General/              # Project-wide documentation
│   ├── MASTER_PROJECT_PLAN.md     # ⭐ PRIMARY REFERENCE
│   ├── COMMIT_STRATEGY.md         # Development workflow
│   └── CLAUDE_CODE_SETUP_GUIDE.md # Claude setup
├── Phase1/
│   ├── Plans/            # Phase 1 planning documents
│   └── Reports/          # Phase 1 completion reports
├── Phase2/
│   ├── Plans/            # Phase 2 planning documents
│   └── Reports/          # Phase 2 completion reports
├── Deployment/           # Infrastructure documentation
└── README.md             # Documentation navigation guide
```

## 🔄 Phase Planning & Execution Protocol

### Before Starting Any New Phase:

1. **📖 READ MASTER PLAN**: Review [`Documentation/General/MASTER_PROJECT_PLAN.md`](Documentation/General/MASTER_PROJECT_PLAN.md)
2. **📊 Check Current Status**: Verify current phase completion in master plan
3. **📋 Review Prerequisites**: Ensure all dependencies are met
4. **📝 Create Phase Plan**: Document in appropriate `Documentation/PhaseX/Plans/` directory
5. **🎯 Define Save Points**: Break down into micro save points following established patterns

### During Phase Execution:

1. **📊 Track Progress**: Update todo lists and progress indicators
2. **💾 Micro Save Points**: Commit granular changes following [`Documentation/General/COMMIT_STRATEGY.md`](Documentation/General/COMMIT_STRATEGY.md)
3. **📝 Document Issues**: Record any deviations or issues encountered
4. **🔄 Update Status**: Keep master plan status current

### After Phase Completion:

1. **📄 Create Completion Report**: **MANDATORY** - Document in `Documentation/PhaseX/Reports/`
   - **File Name Format**: `PHASE_NAME_COMPLETION_REPORT.md` (e.g., `ORGANIZATION_PROFILE_PHASE1_COMPLETION_REPORT.md`)
   - **Required Sections**:
     - Executive Summary
     - Objectives Achieved
     - Implementation Details (all tasks completed)
     - Files Modified/Created
     - Features Implemented
     - Testing Results
     - Issues Encountered and Resolved
     - Performance Metrics
     - Deviations from Plan
     - Next Steps
     - Sign-Off
   - **⚠️ CRITICAL**: This step is MANDATORY and must NEVER be skipped. The completion report is the official record of what was accomplished and serves as documentation for future phases.

2. **✅ Update Master Plan**: **MANDATORY** - Update [`Documentation/General/MASTER_PROJECT_PLAN.md`](Documentation/General/MASTER_PROJECT_PLAN.md) with:
   - Mark phase as ✅ COMPLETED with completion date
   - Add reference to the phase completion report
   - Update current status to next phase
   - Document key achievements and metrics

3. **🔗 Cross-Reference**: Link completion report in master plan documentation index

4. **🔄 Prepare Next Phase**: Reference updated master plan for next phase requirements

5. **🚀 Deploy/Test**: Ensure phase deliverables are fully deployed and tested

## 📄 Completion Report Requirements

### ⚠️ MANDATORY REQUIREMENT
**A completion report MUST be created after EVERY phase execution** - this is NOT optional!

### When to Create a Completion Report
- ✅ After completing ANY implementation plan
- ✅ After executing multiple related tasks as a phase
- ✅ After any significant feature development
- ✅ When closing out a numbered phase (Phase 1.1, Phase 2b, etc.)
- ✅ Before requesting to move to a new phase

### Report Location
- **Path**: `Documentation/PhaseX/Reports/`
- **File Name**: `PHASE_NAME_COMPLETION_REPORT.md`
- **Example**: `Documentation/Phase2/Reports/ORGANIZATION_PROFILE_PHASE1_COMPLETION_REPORT.md`

### Required Report Contents
1. **Executive Summary** - High-level overview of what was accomplished
2. **Objectives Achieved** - List of primary goals and success criteria met
3. **Implementation Details** - Complete list of all tasks completed
4. **Files Modified/Created** - Every file touched with descriptions of changes
5. **Features Implemented** - User-facing features added
6. **Testing Results** - Compilation, functional, and performance testing outcomes
7. **Issues Encountered and Resolved** - Any problems found and how they were fixed
8. **Performance Metrics** - Code size, build time, bundle impact
9. **Deviations from Plan** - Any changes from original plan with justification
10. **Integration Points** - How new code integrates with existing systems
11. **Next Steps** - Immediate actions and phase progression
12. **Sign-Off** - Status declaration and readiness assessment

### Report Template
See completed example at: [`Documentation/Phase2/Reports/ORGANIZATION_PROFILE_PHASE1_COMPLETION_REPORT.md`](Documentation/Phase2/Reports/ORGANIZATION_PROFILE_PHASE1_COMPLETION_REPORT.md)

---

## 📊 Master Plan Maintenance Protocol

### Critical Requirement
**The master plan MUST be updated after every phase completion AND completion report creation** - this is not optional!

### Master Plan Update Checklist
When completing any phase:

1. **✅ Status Update**: Change phase status from "🎯 NEXT" or "🔄 IN PROGRESS" to "✅ COMPLETED"
2. **📅 Date Recording**: Add actual completion date
3. **📄 Report Reference**: Add link to completion report in documentation index
4. **📈 Metrics Update**: Record actual vs. planned metrics and achievements
5. **🔄 Next Phase**: Update "Current Phase" section to reflect next phase
6. **⚠️ Issues**: Document any deviations from plan or lessons learned

### Example Master Plan Update
```markdown
#### Phase 2b: State Management Implementation ✅ COMPLETED
**Duration:** September 28-29, 2025 (2 days)
**Status:** ✅ COMPLETED

**Deliverables Achieved:**
- ✅ State management decision (Zustand selected)
- ✅ Implementation completed
- ✅ Integration with existing components

**Reference Documents:**
- **Completion Report**: [`Documentation/Phase2/Reports/PHASE_2B_COMPLETION_REPORT.md`](Documentation/Phase2/Reports/PHASE_2B_COMPLETION_REPORT.md)
```

## 🚨 Critical Reminders

### Demo Data Configuration ⚠️ IMPORTANT
- **Current Mode**: ALL deployments use demo/fake data by default
- **Backend API**: Not required for local development
- **Documentation**: See [`Documentation/General/DEMO_DATA_CONFIGURATION.md`](Documentation/General/DEMO_DATA_CONFIGURATION.md)
- **To Enable Backend**: Set `REACT_APP_USE_BACKEND_API=true` in `.env` file (not configured by default)
- **⚠️ CRITICAL**: Do NOT attempt backend integration until explicitly requested

### Data Processing Files
- **Location**: Data processing files are preserved in the `main` branch
- **Current Branch**: `working_branch` is focused on web application only
- **Access**: Switch to `main` branch to access BigQuery integration scripts

### Branch Management
- **Main Branch**: Contains full project including data processing
- **Working Branch**: Web application focus (current)
- **Deployment**: Automated via Vercel on branch pushes

### Authentication
- **System**: Clerk authentication integrated
- **Configuration**: Managed through Clerk dashboard
- **Implementation**: See `src/` components and `webapp/backend/auth.py`

## 🔧 Common Tasks

### Organization Profile Feature
Navigate to organization profiles by clicking organization names in search results.

**URL Pattern**: `/organization/:organizationName`

**Features**:
- Comprehensive statistics and metrics (6 metric cards)
- Spending trends visualization (Recharts line chart)
- Paginated activity list (10 items per page)
- Lobbyist network display with expand/collapse
- Related organizations with similarity scoring
- **Export to CSV/JSON** (Phase 3)
- **Keyboard navigation** (Escape to return, Enter on breadcrumbs)
- **WCAG 2.1 AA accessibility compliant**

**Export Functionality**:
- 📊 Export CSV: Organization summary with key metrics
- 📁 Export JSON: Complete profile data (all sections)
- 📥 Export Activities: All activities as CSV

**Testing**:
```bash
# Run development server
npm start

# Navigate to search, click organization name
# Or access directly:
# http://localhost:3000/organization/California%20Medical%20Association

# Test exports - files download to ~/Downloads/
# Test keyboard: Press Escape on profile to return to search
```

### Adding New Features
1. Reference master plan for feature alignment
2. Follow Phase 2 enhancement strategy (see `Documentation/Phase2/Plans/`)
3. Enhance existing components rather than creating new ones
4. Update state management as needed (Phase 2b focus)

### Debugging
- **Frontend**: Browser dev tools + React Dev Tools
- **Backend**: Flask debug mode + logs in `webapp/backend/logs/`
- **Deployment**: Vercel dashboard for build/runtime logs

### Testing
- **Frontend**: `npm test` (Jest + React Testing Library)
- **Backend**: `python -m pytest tests/`
- **Integration**: Manual testing + deployment validation

## 📞 Quick References

### Key URLs
- **Production**: https://ca-lobby-webapp.vercel.app (check latest deployment)
- **Vercel Dashboard**: Project deployments and logs
- **Clerk Dashboard**: Authentication management

### Important Files to Reference
- [`Documentation/General/MASTER_PROJECT_PLAN.md`](Documentation/General/MASTER_PROJECT_PLAN.md) - **Primary planning document**
- [`Documentation/General/COMMIT_STRATEGY.md`](Documentation/General/COMMIT_STRATEGY.md) - Development workflow
- [`Documentation/Phase2/Plans/PHASE_2_PREPARATION_IMPLEMENTATION_PLAN.md`](Documentation/Phase2/Plans/PHASE_2_PREPARATION_IMPLEMENTATION_PLAN.md) - Current phase planning

---

## 🎯 Next Immediate Action

**Phase 2b.1: State Management Decision**
- Choose between Redux and Zustand
- Document decision rationale
- Reference: Phase 2 preparation plan for detailed requirements

**Remember**: Always consult the master plan before proceeding with any phase planning or execution!

---

**Last Updated**: September 28, 2025
**Next Review**: Phase 2b completion
**Maintained By**: CA Lobby Project Team