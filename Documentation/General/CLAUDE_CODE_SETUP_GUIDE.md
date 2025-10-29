# Claude Code Setup Guide for CA Lobby Project

**Document Date:** September 24, 2025
**Project:** CA Lobby Search System - Phase 2 Development
**Current Status:** Phase 2a Complete, Ready for Phase 2b.1
**Target Machine:** New development environment setup

---

## 🎯 **SETUP OBJECTIVE**

This document provides complete configuration instructions for setting up Claude Code on a new machine to continue the CA Lobby project development from Phase 2b.1: State Management Requirements Analysis.

---

## 🌍 **GLOBAL CLAUDE CODE SETTINGS**

### **Claude Code Configuration File Location**
```bash
# Claude Code global settings location (create if doesn't exist)
~/.claude/config.json
```

### **Global Configuration (config.json)**
```json
{
  "version": "1.0.0",
  "defaultModel": "claude-sonnet-4-20250514",
  "systemPrompts": {
    "codeAssistant": {
      "conciseness": "high",
      "explanationLevel": "minimal",
      "codeComments": "avoid unless requested",
      "responseLength": "under 4 lines unless detailed requested"
    }
  },
  "projectDefaults": {
    "todoTracking": true,
    "savePointMethodology": true,
    "microSavePoints": true,
    "deploymentTesting": true
  },
  "behaviorSettings": {
    "proactiveAgentUsage": true,
    "batchToolCalls": true,
    "parallelDeployments": true,
    "enhancementOverCreation": true
  },
  "securitySettings": {
    "defensiveSecurityOnly": true,
    "preventMaliciousCode": true,
    "credentialProtection": true
  }
}
```

### **Global Environment Variables**
```bash
# Add to ~/.bashrc or ~/.zshrc
export CLAUDE_CODE_PROJECT_ROOT="/path/to/project/root"
export CLAUDE_CODE_DEFAULT_EDITOR="vscode"
export CLAUDE_CODE_LOG_LEVEL="info"
```

---

## 🏠 **LOCAL PROJECT SETTINGS**

### **Project Root Structure Required**
```
ca-lobby-project/
├── .claude/                           # Local Claude configuration
│   ├── project.json                   # Project-specific settings
│   ├── agents/                        # Custom agents (if any)
│   └── workflows/                     # Project workflows
├── Documents/GitHub/CA_lobby/          # Main documentation repository
└── Desktop/ca-lobby-deploy/            # Deployment directory
```

### **Local Project Configuration (.claude/project.json)**
```json
{
  "projectId": "ca-lobby-search-system",
  "projectName": "CA Lobby Search System",
  "currentPhase": "Phase 2b.1",
  "lastCompletedPhase": "Phase 2a.2",
  "

  "projectSettings": {
    "workingBranch": "working_branch",
    "mainBranch": "main",
    "deploymentBranch": "working_branch",
    "projectApproach": "proof-of-concept-ui-first"
  },

  "directoryMappings": {
    "documentation": "Documents/GitHub/CA_lobby/Documentation/",
    "deployment": "Desktop/ca-lobby-deploy/",
    "mainRepository": "Documents/GitHub/CA_lobby/",
    "scripts": "Documents/GitHub/CA_lobby/scripts/",
    "backend": "Documents/GitHub/CA_lobby/webapp/backend/"
  },

  "phaseConfiguration": {
    "currentObjective": "Phase 2b.1: State Management Requirements Analysis",
    "nextPhase": "Phase 2b.2: Technology Comparison Research",
    "savePointMethodology": "micro-save-points-4-hour-sessions",
    "commitStrategy": "feature-complete-commits",
    "deploymentTesting": "every-save-point"
  },

  "componentArchitecture": {
    "enhancementApproach": "enhance-existing-not-create-new",
    "existingComponents": [
      "App.js - application shell with Clerk auth",
      "Dashboard.js - system monitoring",
      "Search.js - advanced search interface",
      "Analytics.js - data analysis dashboard",
      "Reports.js - report generation system",
      "Settings.js - user preferences"
    ],
    "sharedServices": [
      "ExportService - unified PDF/CSV/Excel export",
      "ChartingService - unified data visualization",
      "StateManagementService - global state management",
      "AuthenticationService - enhanced Clerk integration",
      "ApiService - centralized API communication"
    ]
  },

  "deploymentConfiguration": {
    "platform": "Vercel",
    "projectName": "ca-lobby-deploy",
    "framework": "create-react-app",
    "branchConnection": "working_branch",
    "environmentVars": "set in Vercel Dashboard",
    "buildOptimization": "71.87kB target bundle size"
  },

  "authenticationSetup": {
    "provider": "Clerk",
    "integration": "existing working integration",
    "protection": "HTTP 401 expected behavior",
    "userMetadata": "Phase 2 enhancements planned"
  },

  "qualityStandards": {
    "buildTimeTarget": "15-30 seconds",
    "bundleSizeTarget": "under 75kB",
    "testCoverage": "backward compatibility required",
    "documentationLevel": "comprehensive save points",
    "deploymentValidation": "authentication and functionality checks"
  }
}
```

---

## 📚 **PROJECT CONTEXT ESSENTIALS**

### **Critical Project Understanding**
```markdown
## Project Approach
- **Proof of Concept:** UI functionality built first, data connection later
- **Enhancement Strategy:** Build upon existing components, avoid duplication
- **Save Point Methodology:** Micro save points every 4 hours with deployment testing
- **Commit Strategy:** Feature-complete commits with descriptive messages

## Phase Status
- **Phase 1.1:** ✅ COMPLETED - Data pipeline (Python scripts, BigQuery, BLN API)
- **Phase 1.2:** ✅ COMPLETED - Deployment pipeline (Vercel automation)
- **Phase 1.3:** ✅ COMPLETED - Frontend deployment (React, Clerk auth)
- **Phase 2a.1:** ✅ COMPLETED - Component structure documentation
- **Phase 2a.2:** ✅ COMPLETED - Enhancement strategy definition
- **Phase 2b.1:** 🎯 NEXT - State management requirements analysis

## Current Production Status
- **URL:** https://ca-lobby-deploy-*.vercel.app (consistent naming)
- **Authentication:** Clerk integration working (HTTP 401 protection)
- **Components:** 5 React components ready for Phase 2 enhancement
- **Documentation:** Comprehensive save point documentation available
```

### **Essential Reference Documents**
```markdown
## Must-Read Documents for Context (in order)
1. **MASTER_PROJECT_PLAN.md** - Overall project roadmap and phases
2. **PHASE_2A1_COMPONENT_STRUCTURE_DOCUMENTATION.md** - Component analysis
3. **PHASE_2A2_ENHANCEMENT_STRATEGY_DEFINITION.md** - Enhancement strategy
4. **DEPLOYMENT_REFERENCE.md** - Deployment procedures and settings
5. **DEPLOYMENT_CONFIGURATION_SUMMARY.md** - Current deployment configuration
6. **PHASE_2_PREPARATION_IMPLEMENTATION_PLAN.md** - Phase 2 implementation plan

## Key Architectural Decisions Made
- **No new major components** needed for Phase 2
- **Shared service architecture** prevents code duplication
- **Enhancement-first approach** for all Phase 2 features
- **Clerk authentication enhancement** without breaking existing functionality
- **Consistent deployment naming** with working_branch integration
```

---

## ⚙️ **DEVELOPMENT ENVIRONMENT SETUP**

### **Required Software Stack**
```bash
# Core Development Tools
- Node.js (version compatible with Create React App)
- npm (latest version recommended)
- Git (with working_branch access)
- Claude Code CLI (latest version)

# Deployment Tools
- Vercel CLI (configured with team scope)
- Access to team_agKdPbial8abFCKrGX9IJeU4 scope

# Development Environment
- VS Code or preferred editor
- Browser for testing deployments
- Terminal with bash/zsh access
```

### **Repository Setup Commands**
```bash
# 1. Clone main documentation repository
git clone [CA_lobby_repository_url] ~/Documents/GitHub/CA_lobby
cd ~/Documents/GitHub/CA_lobby
git checkout working_branch

# 2. Set up deployment directory
mkdir -p ~/Desktop/ca-lobby-deploy
cd ~/Desktop/ca-lobby-deploy

# 3. Initialize deployment repository
git init
git remote add origin ~/Documents/GitHub/CA_lobby
git branch -m working_branch

# 4. Copy deployment files (get from existing deployment)
# Copy: src/, public/, package.json, vercel.json, .env
# Install dependencies: npm install

# 5. Verify Vercel connection
vercel --scope team_agKdPbial8abFCKrGX9IJeU4
# Should connect to existing ca-lobby-deploy project
```

### **Environment Variables Setup**
```bash
# Create .env in deployment directory
REACT_APP_CLERK_PUBLISHABLE_KEY=pk_test_c3RyaWtpbmctaWd1YW5hLTgxLmNsZXJrLmFjY291bnRzLmRldiQ

# Vercel Dashboard Environment Variables (set in Vercel UI)
REACT_APP_CLERK_PUBLISHABLE_KEY=pk_test_c3RyaWtpbmctaWd1YW5hLTgxLmNsZXJrLmFjY291bnRzLmRldiQ
CLERK_SECRET_KEY=sk_test_X3r9ydct9z3cCMj1ozWzCtXvHeOYI4HmWuojIQyTaC
```

---

## 🔧 **CLAUDE CODE WORKFLOW PATTERNS**

### **Standard Session Workflow**
```markdown
## 1. Session Initialization
- Read current phase documentation
- Review previous save point status
- Check deployment status
- Set up todo tracking for current objectives

## 2. Development Workflow
- Use TodoWrite tool for task tracking
- Implement micro save points (4-hour sessions)
- Batch tool calls for performance
- Deploy and test after each save point
- Create comprehensive documentation

## 3. Session Conclusion
- Complete all todos in current save point
- Deploy to Vercel with testing validation
- Create completion report
- Run closing workflow
- Update project status for next session

## 4. Quality Standards
- Maintain backward compatibility
- Preserve existing functionality
- Test authentication protection (HTTP 401 expected)
- Maintain bundle size optimization (~72KB target)
- Ensure build times under 30 seconds
```

### **Agent Usage Patterns**
```markdown
## Proactive Agent Usage
- Use opening-workflow-manager for session setup
- Use general-purpose agent for complex searches
- Use specialized agents for specific tasks
- Batch multiple agent calls when possible

## Tool Usage Guidelines
- Read files before editing
- Use MultiEdit for multiple changes
- Batch bash commands with single calls
- Use Grep instead of bash grep/find
- Prefer TodoWrite for complex task tracking
```

---

## 📋 **VERIFICATION CHECKLIST**

### **Setup Verification Steps**
```bash
# 1. Verify Claude Code Configuration
claude --version
claude config list

# 2. Verify Repository Access
cd ~/Documents/GitHub/CA_lobby
git status  # Should show working_branch
git log --oneline -5  # Should show recent Phase 2a commits

# 3. Verify Deployment Environment
cd ~/Desktop/ca-lobby-deploy
npm --version
vercel --version
vercel projects list --scope team_agKdPbial8abFCKrGX9IJeU4
# Should show ca-lobby-deploy project

# 4. Test Build Process
npm install
npm run build
# Should complete in under 30 seconds with ~72KB bundle

# 5. Test Deployment
vercel --prod --scope team_agKdPbial8abFCKrGX9IJeU4
# Should deploy to ca-lobby-deploy-*.vercel.app
# Test URL should return HTTP 401 (authentication protection working)
```

### **Context Verification Commands**
```bash
# Verify Phase Status
cat ~/Documents/GitHub/CA_lobby/Documentation/MASTER_PROJECT_PLAN.md | grep "Phase 2"

# Check Latest Completion
ls ~/Documents/GitHub/CA_lobby/Documentation/PHASE_2A*

# Verify Deployment Configuration
cat ~/Desktop/ca-lobby-deploy/vercel.json
cat ~/Desktop/ca-lobby-deploy/package.json | grep -A5 repository
```

---

## 🚀 **FIRST SESSION COMMANDS**

### **Recommended First Claude Code Session**
```markdown
"Continue CA Lobby project Phase 2b.1: State Management Requirements Analysis.

Context: Phase 2a complete (component analysis and enhancement strategy defined).
Ready to begin state management technology selection.

Please review Phase 2a.2 completion status and begin Phase 2b.1 deliverables:
1. Document Phase 2 state management requirements
2. List features needing global state
3. Define complexity requirements and performance needs
4. Create evaluation criteria matrix

Use micro save point methodology with TodoWrite tracking and Vercel deployment testing."
```

### **Context Validation Commands**
```markdown
# First, have Claude Code run these to understand current state:
1. Read MASTER_PROJECT_PLAN.md to understand project phases
2. Read PHASE_2A2_ENHANCEMENT_STRATEGY_DEFINITION.md for latest status
3. Read DEPLOYMENT_REFERENCE.md for deployment procedures
4. Check current Vercel deployment status
5. Verify git repository status on working_branch
```

---

## ⚠️ **IMPORTANT NOTES**

### **Critical Project Principles**
```markdown
## Must Remember
1. **Enhancement Over Creation:** Always enhance existing components, never create new ones for existing functionality
2. **Backward Compatibility:** All changes must preserve existing functionality
3. **Shared Services:** Use shared service architecture to prevent duplication
4. **Deployment Testing:** Every save point must include Vercel deployment and testing
5. **Authentication Expectation:** HTTP 401 responses are correct (Clerk protection working)

## Technology Stack Decisions
- **Frontend:** Create React App (established, do not change)
- **Authentication:** Clerk (working, enhance don't replace)
- **Deployment:** Vercel with ca-lobby-deploy project name
- **Version Control:** working_branch for all development
- **State Management:** TO BE SELECTED in Phase 2b (Redux Toolkit vs Zustand vs Context API)

## Documentation Standards
- Micro save points every 4 hours
- Comprehensive documentation for each phase
- TodoWrite tracking for all multi-step tasks
- Deployment reports with testing validation
- Commit messages with clear phase indicators
```

---

## 📊 **PROJECT METRICS TO MAINTAIN**

### **Quality Standards**
```markdown
## Build Performance
- Build time: 15-30 seconds (current: ~17 seconds)
- Bundle size: Under 75KB (current: 71.87KB main.js + 1.66KB CSS)
- Dependencies install: Under 5 seconds
- Cache utilization: Should restore from previous builds

## Deployment Standards
- Status: ● Ready (not ● Error)
- Authentication: HTTP 401 protection active
- URL pattern: ca-lobby-deploy-*.vercel.app
- Project consistency: Always use ca-lobby-deploy project

## Development Standards
- Zero build errors or warnings
- Backward compatibility maintained
- Existing functionality preserved
- Documentation comprehensive and current
```

---

## 🎯 **SUCCESS CRITERIA FOR NEXT SESSION**

### **Phase 2b.1 Objectives**
```markdown
## Deliverables (4 hours)
1. **State Management Requirements Analysis** - Document all Phase 2 features needing global state
2. **Complexity Assessment** - Define performance needs and technical requirements
3. **Evaluation Criteria Matrix** - Framework for comparing Redux Toolkit vs Zustand vs Context API
4. **Integration Planning** - How state management will integrate with existing Clerk authentication

## Success Indicators
- All requirements documented with component mapping
- Technology comparison criteria established
- Ready for Phase 2b.2: Technology Comparison Research
- Deployment tested and operational
- Documentation comprehensive and current
```

---

**Setup Guide Status:** ✅ COMPLETE
**Project Transition:** ✅ READY
**Next Phase:** Phase 2b.1 - State Management Requirements Analysis
**Estimated Setup Time:** 30-45 minutes
**Development Continuity:** Seamless with this configuration

---

**Document Generated:** September 24, 2025
**For Continuation On:** New development machine
**Project Status:** Phase 2a Complete, Phase 2b.1 Ready
**Total Project Progress:** 5/6 preparation phases complete