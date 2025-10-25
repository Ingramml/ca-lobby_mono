# Proposed Opening Workflow Changes

## Summary of Changes

Add a **safety check step** to the opening workflow that detects older/dormant projects and requires file structure approval before executing the full workflow.

---

## Current Workflow Flow

```
1. Pre-workflow Validation
   ↓
2. File Synchronization Phase
   ↓
3. Setup Script Execution Phase
   ↓
4. Subject Outline Generation Phase
   ↓
5. Workflow Completion
```

---

## Proposed New Workflow Flow

```
1. Project Age Detection & Analysis
   ↓
2. [IF OLDER PROJECT] Generate & Present File Structure
   ↓
3. [IF OLDER PROJECT] Wait for User Approval
   ↓
4. Pre-workflow Validation
   ↓
5. File Synchronization Phase
   ↓
6. Setup Script Execution Phase
   ↓
7. Subject Outline Generation Phase
   ↓
8. Workflow Completion
```

---

## Detailed Changes

### NEW STEP 1: Project Age Detection & Analysis

**What it does:**
- **PRIMARY CHECK**: Looks for session archives in `.claude/sessions/`
- **FALLBACK CHECK**: If no archives, checks git log for last commit date
- Analyzes project structure for signs of age/staleness
- Determines if project is "older" based on Claude Code activity or git activity

**Detection Criteria (Priority Order):**
```bash
# PRIMARY: Check for session archives (indicates Claude Code usage)
if [ -d ".claude/sessions" ]; then
    LATEST_SESSION=$(ls -t .claude/sessions/*.md 2>/dev/null | head -1)
    if [ -n "$LATEST_SESSION" ]; then
        # Session archives exist - this is an active/known project
        PROJECT_IS_OLDER=false
        echo "✅ Session archives found - project has Claude Code history"
    else
        # .claude/sessions exists but empty - treat as older
        PROJECT_IS_OLDER=true
        echo "⚠️ No session archives found - treating as older project"
    fi
else
    # No session archives directory - check git as fallback
    echo "📋 No session archives - checking git history..."
    LAST_COMMIT=$(git log -1 --format=%ct 2>/dev/null)
    CURRENT_TIME=$(date +%s)
    DAYS_SINCE_COMMIT=$(( (CURRENT_TIME - LAST_COMMIT) / 86400 ))

    if [ $DAYS_SINCE_COMMIT -gt 30 ] || [ -z "$LAST_COMMIT" ]; then
        PROJECT_IS_OLDER=true
        echo "⚠️ Last commit >30 days ago - treating as older project"
    else
        PROJECT_IS_OLDER=false
        echo "✅ Recent git activity - proceeding normally"
    fi
fi
```

**Markers of "Older Project" (Priority Order):**
1. **PRIMARY MARKER**: No session archives in `.claude/sessions/` directory
2. **SECONDARY MARKER**: Last commit >30 days ago (only checked if no session archives)
3. **ADDITIONAL INDICATORS**:
   - Empty `.claude/sessions/` directory
   - No commits in current branch for >30 days
   - Presence of legacy config files
   - No recent file modifications

**Logic Rationale:**
- **Session archives = active project**: If session archives exist, the project has been worked on with Claude Code, even if git commits are old
- **No session archives = needs review**: If no session archives, this is either:
  - A legacy project being revisited
  - A project from before session archiving was implemented
  - A project worked on without Claude Code
- **Git is fallback only**: Only check git history if session archives don't exist

---

### NEW STEP 2: File Structure Generation (Conditional)

**Triggers when:** Project detected as "older"

**What it generates:**
1. **Complete directory tree** (excluding node_modules, .git, etc.)
2. **Package.json analysis** (if exists)
3. **Technology stack detection**
4. **Git status summary**
5. **Environment files listing**
6. **Identified issues/concerns**
7. **Potential risks**

**Output file:** `PROJECT_STRUCTURE.md` (like the one I just created)

**Structure sections:**
```markdown
# [Project Name] Structure Analysis

## Project Age Analysis
- Session archives found: [YES/NO]
- Last session: [date or N/A]
- Last commit: [date]
- Days since activity: [number]
- Branch: [name]
- Status: OLDER PROJECT DETECTED
- Detection method: [Session archives / Git history]

## Overview
[Project description and type]

## Directory Structure
[Complete tree view]

## Technology Stack
[Detected technologies and versions]

## Git Status
[Current git state]

## Potential Issues
[List of concerns]

## Recommendations
[What to review before proceeding]
```

---

### NEW STEP 3: User Approval Gate (Conditional)

**Triggers when:** File structure has been generated

**What it does:**
1. Presents the `PROJECT_STRUCTURE.md` file
2. Displays summary in chat
3. **PAUSES execution**
4. Waits for explicit user approval

**User response options:**
```
Option 1: "approved" or "proceed" → Continue with workflow
Option 2: "cancel" or "stop" → Abort workflow
Option 3: "modify" or questions → Address concerns first
```

**Approval message:**
```
🔍 OLDER PROJECT DETECTED

I've generated a file structure analysis in PROJECT_STRUCTURE.md

⚠️ This project appears to be older/dormant. Review the structure before proceeding.

Key concerns identified:
- [Issue 1]
- [Issue 2]
- [Issue 3]

Please review PROJECT_STRUCTURE.md and respond with:
- "approved" to proceed with opening workflow
- "cancel" to abort
- Ask questions if you need clarification

The workflow will NOT proceed until you approve.
```

---

### MODIFIED STEP 4: Pre-workflow Validation

**New additions:**
- Check if approval received (for older projects)
- Verify PROJECT_STRUCTURE.md was reviewed
- Log approval timestamp
- Proceed only with explicit confirmation

---

## Files to Modify

### 1. `master-files/workflows/opening-workflow-guide.md`

**Section to add** (after "## Workflow Components"):

```markdown
## Project Age Detection (Safety Feature)

### Purpose
Protect older/dormant projects from unexpected changes by requiring file structure review and approval before workflow execution.

### Detection Process
The workflow automatically detects older projects using a priority-based approach:

**PRIMARY Detection** (Most Reliable):
1. Check for `.claude/sessions/` directory
2. If session archives exist → Project has Claude Code history → Skip safety check
3. If no session archives → Trigger safety check (needs review)

**FALLBACK Detection** (When no session archives):
1. Check last git commit date (>30 days = older)
2. Check file modification timestamps
3. Analyze git activity patterns
4. Check for stale configurations

**Why Session Archives First?**
- Session archives are the most reliable indicator of Claude Code usage
- A project with session archives has been properly set up and worked on
- Git commits can be old even on actively maintained projects
- Session archives are created by the closing workflow, indicating proper project management

### Safety Workflow
When an older project is detected:

1. **Automatic Structure Generation**
   - Creates PROJECT_STRUCTURE.md with complete analysis
   - Includes directory tree, technologies, git status
   - Identifies potential issues and risks

2. **User Review & Approval Required**
   - Workflow pauses for user review
   - User must explicitly approve to proceed
   - Options: approve, cancel, or ask questions

3. **Workflow Continues on Approval**
   - Only proceeds after explicit "approved" response
   - Logs approval for audit trail
   - Executes standard workflow steps

### Bypassing Safety Check
To skip safety check (not recommended):
```
"Run opening workflow --skip-safety-check"
```

### Manual Structure Generation
To generate structure without running workflow:
```
"Generate project structure analysis"
```
```

---

### 2. `master-files/agents/workflow-management/opening-workflow-manager.md`

**Section to add** (after "## Core Responsibilities"):

```markdown
### 0. **Project Age Detection & Safety Gate** (Pre-workflow)

**Purpose**: Prevent unexpected changes to older/dormant projects by requiring review and approval.

**Detection Criteria (Priority Order)**:
1. **PRIMARY**: No session archives in `.claude/sessions/` directory
2. **FALLBACK**: Last git commit >30 days ago (only if no session archives)
3. **ADDITIONAL**: No recent file modifications
4. **ADDITIONAL**: Stale configuration markers
5. **ADDITIONAL**: Dormant repository indicators

**Safety Workflow**:
1. Detect project age automatically
2. If older project detected:
   - Generate comprehensive PROJECT_STRUCTURE.md
   - Present file structure to user
   - List potential issues and concerns
   - **PAUSE and wait for explicit approval**
3. Only proceed when user responds with "approved"
4. Log approval and continue with standard workflow

**Structure Generation Requirements**:
- Complete directory tree (exclude node_modules, .git, etc.)
- Technology stack analysis
- Git status and history
- Environment files inventory
- Identified risks and concerns
- Recommendations for review

**Approval Gate**:
- MUST wait for explicit user confirmation
- Accepted responses: "approved", "proceed", "yes, continue"
- Cancel responses: "cancel", "stop", "abort"
- Questions allowed before approval
- No timeout - wait indefinitely for user

**Bypassing** (use with caution):
- User can include `--skip-safety-check` flag
- Log bypass for audit trail
- Warn user of risks
```

---

### 3. `master-files/agents/workflow-management/opening-workflow-manager.md`

**Modify "Workflow Execution Pattern" section:**

```markdown
## Workflow Execution Pattern

### Standard Opening Workflow Sequence:

0. **[NEW] Project Age Detection & Safety Gate**
   - **PRIMARY CHECK**: Look for session archives in `.claude/sessions/`
   - **FALLBACK CHECK**: If no archives, analyze git history and file timestamps
   - Determine if project needs safety review:
     * Session archives exist → Skip safety check (known project)
     * No session archives → Trigger safety check
     * (Fallback) Last commit >30 days → Trigger safety check
   - IF SAFETY CHECK TRIGGERED:
     a. Generate PROJECT_STRUCTURE.md with complete analysis
     b. Present structure to user with identified concerns
     c. **PAUSE execution and wait for approval**
     d. Only proceed when user explicitly approves
   - IF ACTIVE PROJECT WITH ARCHIVES: Skip to step 1

1. **Pre-workflow Validation**
   - Verify ~/Github/Claude_files directory exists and is accessible
   - Check current project directory permissions
   - Confirm workspace readiness for initialization
   - [NEW] Verify approval received (if older project)

[Rest of workflow continues as before...]
```

---

## Usage Examples

### Example 1: Project with Session Archives (No Safety Check)
```
User: "Run opening workflow"

Claude:
🔄 Checking project status...
✅ Session archives found in .claude/sessions/
✅ Active Claude Code project detected - proceeding with standard workflow

1. ✅ Copied ~/.claude/master-files to ./Claude_files (15 files)
2. ✅ Executed project-setup-script.sh successfully
3. ✅ Generated all subject outlines
4. 🎉 Opening workflow complete
```

---

### Example 2: Project Without Session Archives (Safety Check Triggered)
```
User: "Run opening workflow"

Claude:
🔄 Checking project status...
📋 No session archives found in .claude/sessions/
⚠️ OLDER/UNKNOWN PROJECT DETECTED - Safety check triggered

Detection details:
- Session archives: NOT FOUND
- This indicates either:
  • Legacy project from before archiving
  • Project not previously worked on with Claude Code
  • Project needs initial review

📋 Generating PROJECT_STRUCTURE.md for your review...

Analysis Summary:
- Project: CA_lobby-2
- Session archives: None found
- Last commit: 78 days ago (Sep 21, 2024)
- Type: Hybrid Python/Next.js
- Branch: retest_js
- Detection method: No session archives (primary marker)
- Issues found: 3
  • Nested directory structure (ca-lobby-dashboard/ca-lobby-dashboard/)
  • Uncommitted changes present
  • Deleted file not committed (vercel.json)

⚠️ WORKFLOW PAUSED FOR APPROVAL

Please review PROJECT_STRUCTURE.md and respond with:
- "approved" to proceed with opening workflow
- "cancel" to abort
- Ask questions if you need clarification

---

User: "approved"

Claude:
✅ Approval received - proceeding with opening workflow

1. ✅ Copied ~/.claude/master-files to ./Claude_files (15 files)
2. ✅ Executed project-setup-script.sh successfully
3. ✅ Generated all subject outlines
4. 🎉 Opening workflow complete

Note: Future runs will skip safety check once session archives are created.
```

---

### Example 3: User Has Questions
```
User: "Run opening workflow"

Claude:
[Generates structure and pauses]

User: "What's the nested directory issue?"

Claude:
The nested directory issue is that you have:
ca-lobby-dashboard/ca-lobby-dashboard/

This is unusual - typically you'd have:
ca-lobby-dashboard/

The extra nesting can cause confusion with paths and may indicate
the project was restructured at some point. This should be reviewed
before running the workflow which might affect this structure.

Would you like to:
1. Fix this before running workflow
2. Proceed with workflow anyway
3. Cancel and address manually

User: "Proceed anyway"

Claude:
✅ Approval received - proceeding with opening workflow
[Continues with workflow...]
```

---

## Implementation Checklist

- [ ] Update `opening-workflow-guide.md` with new safety section
- [ ] Update `opening-workflow-manager.md` with detection logic
- [ ] Add PROJECT_STRUCTURE.md generation template
- [ ] Implement age detection logic
- [ ] Implement approval gate mechanism
- [ ] Add bypass flag handling
- [ ] Update usage examples in documentation
- [ ] Test with older project (this one!)
- [ ] Test with new project (should skip safety)
- [ ] Document in sub-agents-guide.md

---

## Benefits of This Change

✅ **Safety**: Prevents unexpected changes to older/unknown projects
✅ **Awareness**: Forces user to review project state first
✅ **Documentation**: Creates useful PROJECT_STRUCTURE.md
✅ **Flexibility**: Can be bypassed if needed
✅ **Smart**: Uses session archives as primary indicator (most reliable)
✅ **No impact**: Doesn't slow down work on projects with session archives
✅ **One-time**: Once session archives exist, safety check never triggers again
✅ **Intelligent**: Prioritizes Claude Code activity over git activity

---

## Risks & Considerations

⚠️ **False Positives**: Might trigger on intentionally dormant projects
⚠️ **User Friction**: Adds extra step for older projects
⚠️ **Threshold Tuning**: 30-day threshold may need adjustment
⚠️ **Bypass Temptation**: Users might always bypass

---

## Questions for Review

1. **Is session archives as primary marker** the right approach? ✅ APPROVED
2. **Is 30 days the right threshold** for git fallback check?
3. **Should there be different levels** (warning vs. hard stop)?
4. **What should bypass behavior be** - warn or silent?
5. **Should structure generation be automatic** or optional?
6. **Should we check archive timestamps** or just presence?

---

## Next Steps

Once you approve this plan:

1. I'll modify the two key files:
   - `opening-workflow-guide.md`
   - `opening-workflow-manager.md`

2. I'll update any related documentation

3. We can test it by running the workflow on THIS project (it should trigger the safety check)

---

**Ready to implement?** Respond with:
- "approved" → I'll make the changes
- Questions → I'll clarify
- "modify" → Tell me what to change
