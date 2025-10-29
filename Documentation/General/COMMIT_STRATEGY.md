# Granular Commit Strategy for CA Lobby Project

**Effective Date:** September 22, 2025
**Purpose:** Establish clear guidelines for creating focused, traceable commits during development phases

## Overview

This document establishes a granular commit strategy to replace large, monolithic commits with focused, single-purpose commits that improve:
- **Traceability** - Easy to track specific changes
- **Debugging** - Isolated changes for easier issue identification
- **Code Review** - Smaller, focused diffs for better review quality
- **Rollback Safety** - Granular rollback options for specific features

## Commit Categories and Prefixes

### Primary Categories
- **`Fix:`** - Bug fixes and error corrections
- **`Add:`** - New features or functionality
- **`Update:`** - Modifications to existing features
- **`Remove:`** - Deletion of code or features
- **`Refactor:`** - Code restructuring without functional changes
- **`Docs:`** - Documentation changes
- **`Config:`** - Configuration file changes
- **`Test:`** - Test additions or modifications
- **`Deploy:`** - Deployment-related changes

### Micro Save Point Categories
- **`MSP-[X.Y.Z]:`** - Micro save point completion (e.g., `MSP-1.2.a:`)
- **`Phase-[X.Y]:`** - Phase completion markers
- **`Milestone:`** - Major project milestones

## Commit Size Guidelines

### ✅ Good Commit Sizes (Recommended)
- **Single File Changes:** 1-50 lines modified
- **Multi-File Logical Changes:** 2-5 related files, 50-150 lines total
- **Feature Components:** Complete small feature (authentication fix, API endpoint)
- **Configuration Updates:** Single system or tool configuration

### ⚠️ Medium Commits (Use Sparingly)
- **Related Module Changes:** 5-10 files, 150-300 lines total
- **Cross-cutting Changes:** Changes that necessarily span multiple areas
- **Integration Points:** API integrations or external service connections

### ❌ Avoid Large Commits
- **Bulk Changes:** >300 lines across many files
- **Multiple Unrelated Features:** Different functionality in one commit
- **End-of-Day Dumps:** Accumulated work without logical separation

## Implementation Timeline

### During Development (Real-time)
```bash
# Every 15-30 minutes during active development
git add specific-file.js
git commit -m "Add: User authentication validation logic"

# After completing a small feature
git add auth-component.js auth-styles.css
git commit -m "Add: Login form component with validation styling"
```

### During Micro Save Points (Every 30-45 minutes)
```bash
# At the end of each micro save point
git add completed-feature-files
git commit -m "MSP-1.3.a: Complete user session management integration"
```

### During Planning Sessions
```bash
# After each planning document
git add Documentation/PHASE_1_3_PLAN.md
git commit -m "Docs: Add Phase 1.3 planning document with technical specifications"

# After each design decision
git add config/new-service.json
git commit -m "Config: Add Redis configuration for session storage"
```

## Commit Message Format

### Structure
```
[Category]: [Brief summary (50 chars max)]

[Optional detailed description]
- Bullet point details
- Specific changes made
- Context or reasoning

[Optional technical details]
Resolves: [issue/requirement description]

🤖 Generated with [Claude Code](https://claude.ai/code)

Co-Authored-By: Claude <noreply@anthropic.com>
```

### Examples of Good Commits

#### Bug Fix
```
Fix: Resolve UserContext error in React deployment

- Add ClerkProvider wrapper to index.js
- Include environment variable validation
- Add fallback UI for missing configuration

Resolves blank screen issue on production deployment.
```

#### Feature Addition
```
Add: Redis session storage integration

- Configure Redis client with connection pooling
- Implement session middleware for Express
- Add session cleanup on user logout

Enables persistent user sessions across server restarts.
```

#### Configuration Change
```
Config: Update Vercel deployment settings for testing

- Add test pipeline integration to vercel.json
- Configure build command to run tests before deployment
- Set environment-specific build targets

Prevents deployment of failing builds to production.
```

#### Documentation
```
Docs: Add API endpoint documentation for user management

- Document authentication endpoints with examples
- Include error response formats and codes
- Add rate limiting information

Provides clear API usage guidelines for frontend integration.
```

## Branching Strategy Integration

### Feature Branches
- Create focused branches for logical feature groups
- Use descriptive branch names: `feature/user-authentication`, `fix/deployment-errors`
- Commit granularly within feature branches

### Working Branch Management
```bash
# Create feature branch for specific work
git checkout -b feature/session-management

# Make granular commits during development
git commit -m "Add: Redis client configuration"
git commit -m "Add: Session middleware setup"
git commit -m "Add: Session cleanup on logout"
git commit -m "Test: Add session persistence tests"

# Merge back to working branch
git checkout working_branch
git merge feature/session-management
```

## Automated Commit Checks

### Pre-commit Validation
- **File count check:** Warn if >10 files in single commit
- **Line count check:** Warn if >300 lines changed
- **Message format:** Validate commit message format
- **Related changes:** Ensure changes are logically related

### Commit Quality Metrics
- Track average commits per feature
- Monitor commit message quality
- Measure rollback frequency (lower is better)
- Assess debugging efficiency

## Tools and Automation

### Recommended Git Aliases
```bash
# Quick staging and committing
git config alias.ac '!git add -A && git commit -m'

# Focused file commits
git config alias.cf '!f() { git add "$1" && git commit -m "$2"; }; f'

# Interactive staging for granular commits
git config alias.ip 'add -p'
```

### VS Code Integration
- Use GitLens for inline blame and history
- Configure auto-save intervals (5-10 minutes)
- Set up commit message templates

## Benefits of Granular Commits

### For Development
1. **Easier Debugging:** Isolate exactly when issues were introduced
2. **Better Code Review:** Smaller diffs are easier to review thoroughly
3. **Safer Rollbacks:** Roll back specific changes without affecting other work
4. **Clear History:** Understand project evolution through detailed commit log

### For Project Management
1. **Progress Tracking:** See exactly what was accomplished and when
2. **Time Estimation:** Better data for future planning based on commit frequency
3. **Quality Metrics:** Track defect rates per commit size
4. **Collaboration:** Team members can follow development progress in real-time

### For Deployment
1. **Incremental Releases:** Deploy smaller, safer changes
2. **Targeted Rollbacks:** Roll back specific features without full deployment rollback
3. **Feature Flags:** Enable/disable features based on specific commits
4. **Audit Trail:** Complete history of what changes went to production when

## Migration from Large Commits

### Immediate Actions
1. **Current Work:** Break remaining work into focused commits
2. **Future Features:** Plan granular commit strategy before starting
3. **Documentation:** Create commit plans for upcoming phases

### Historical Reference
- Keep large commits as milestones for major phase completions
- Add detailed commit notes explaining the transition to granular strategy
- Use git tags to mark important milestones

## Monitoring and Improvement

### Weekly Review
- Assess commit sizes and frequency
- Identify patterns in commit types
- Adjust strategy based on what works best

### Monthly Analysis
- Review rollback frequency and causes
- Analyze debugging efficiency improvements
- Gather team feedback on commit strategy effectiveness

---

**Implementation Status:** ✅ Active
**Next Review:** Weekly during development phases
**Responsible:** Development team and project management

This strategy replaces the previous approach of large, infrequent commits with focused, frequent commits that improve development velocity and code quality.