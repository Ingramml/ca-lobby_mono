# Workflow Language Audit Results

**Date:** October 25, 2025
**Purpose:** Identify ambiguous language in workflows that Claude Code might misunderstand
**Tool Used:** review_workflows_ambiguous_language.py

---

## Executive Summary

**FILES REVIEWED:** 9 workflow files in master-files-toolkit
**ISSUES FOUND:** 158 instances of potentially ambiguous language
**MOST CRITICAL:** "from X to Y" pattern (caused the master-files misunderstanding)

---

## Critical Findings

### Issue 1: "from X to Y" Pattern (Highest Priority)
**Pattern:** "Creates symlink from `~/.claude/master-files/` to `.claude/master-files/`"

**Why Ambiguous:**
- "FROM→TO" commonly means "copy FROM source TO destination"
- Claude Code interpreted as copy operation
- Led to creating `./master-files/` directory instead of `.claude/master-files` symlink

**Examples Found:**
- opening-workflow-guide.md: Line 13
- Multiple workflow files

**Fix:**
```
❌ BAD:  "Creates symlink from ~/.claude/master-files/ to .claude/master-files/"
✅ GOOD: "Creates symlink .claude/master-files pointing to ~/.claude/master-files/"
✅ GOOD: "Create .claude/master-files → ~/.claude/master-files (symlink)"
```

### Issue 2: Missing Symlink Indicators (147 instances)
**Pattern:** `.claude/master-files` without clarifying it's a symlink

**Why Ambiguous:**
- Could be interpreted as a real directory
- No visual indication it should be a symbolic link
- Can cause confusion about whether to create directory or symlink

**Examples:**
- "ln -s ~/.claude/master-files .claude/master-files"  ← Which is the symlink?
- "cd ~/.claude/master-files" ← Real directory or symlink?

**Fix:**
```
❌ BAD:  .claude/master-files
✅ GOOD: .claude/master-files (symlink)
✅ GOOD: .claude/master-files →  ~/.claude/master-files
✅ GOOD: .claude/master-files (link)
```

### Issue 3: "Copy" Near master-files
**Pattern:** Any mention of "copy" with "master-files"

**Why Critical:**
- master-files should NEVER be copied
- Only symlinked
- "copy" creates confusion about the architecture

**Fix:**
```
❌ BAD:  "Global master copy"
✅ GOOD: "Global master source"
✅ GOOD: "Centralized master-files (symlink target)"
```

### Issue 4: Ambiguous "create" Commands
**Pattern:** "create master-files" without specifying directory vs symlink

**Why Ambiguous:**
- "create" could mean mkdir (directory) or ln -s (symlink)
- Claude Code defaults to mkdir
- Must explicitly say "create symlink"

**Fix:**
```
❌ BAD:  "create master-files"
✅ GOOD: "create symlink to master-files"
✅ GOOD: "use ln -s to link master-files"
```

---

## Files Affected (All 9 Workflows)

1. **MASTER_FILES_SYNC_GUIDE.md** - 35 issues
2. **centralization-plan.md** - Multiple issues
3. **closing-workflow-guide.md** - Multiple issues
4. **context-management-workflow.md** - Multiple issues
5. **git-submodule-implementation.md** - Multiple issues
6. **global-close-command-plan.md** - Multiple issues
7. **opening-workflow-guide.md** - Multiple issues ⚠️ CRITICAL
8. **sync-workflows.md** - Multiple issues
9. **OPENING_WORKFLOW_CRITICAL_WARNING.md** - 0 issues ✅ (just created with clear language)

---

## Priority Fixes

### Immediate (High Priority)

#### 1. opening-workflow-guide.md - Line 13
**Current:** "Creates symlink from `~/.claude/master-files/` to `.claude/master-files/` in current project"

**Fix to:**
```markdown
Creates symlink .claude/master-files pointing to ~/.claude/master-files/

Architecture:
~/.claude/master-files/  ← Centralized source
         ↑
         │ (symlink)
         │
.claude/master-files  ← Project symlink (NOT a copy!)
```

#### 2. Add Warning Banner to All Workflow Files
Insert at top of each workflow:
```markdown
⚠️ **For Claude Code:** Read [OPENING_WORKFLOW_CRITICAL_WARNING.md](OPENING_WORKFLOW_CRITICAL_WARNING.md) before executing any setup commands involving master-files.

**Key rule:** NEVER copy master-files, always create symlinks using `ln -s`
```

#### 3. Replace All "from X to Y" with Clear Direction
Search and replace across all workflows:
- "from X to Y" → "X pointing to Y"
- "symlink from X to Y" → "create symlink Y → X"

### Medium Priority

#### 4. Add Symlink Indicators
Update all references to `.claude/master-files`:
- Add "(symlink)" after first mention
- Use "→" arrows in examples
- Show with `ls -la` output examples

#### 5. Add Verification Steps
After every `ln -s` command, add:
```bash
# Verify symlink created (must show → arrow)
ls -la .claude/master-files
```

#### 6. Add Visual Diagrams
Include architecture diagrams showing:
- ✅ Correct: Symlink arrows
- ❌ Wrong: Real directories

### Long Term

#### 7. Create Automated Checker
Script that validates project setup:
```bash
# check-master-files-setup.sh
if [ -d ./master-files ] && [ ! -L ./master-files ]; then
    echo "❌ ERROR: master-files/ should not exist in project root!"
    exit 1
fi

if [ ! -L .claude/master-files ]; then
    echo "❌ ERROR: .claude/master-files must be a symlink!"
    exit 1
fi

echo "✅ master-files setup correct"
```

#### 8. Update Template Variables
Use consistent terminology:
- "SOURCE" for `~/.claude/master-files/`
- "LINK" for `.claude/master-files`
- Never use "copy" or "destination"

---

## Language Rules for Future Workflows

### DO Use:
- ✅ "create symlink X pointing to Y"
- ✅ "X → Y (symlink)"
- ✅ "link X to Y using ln -s"
- ✅ ".claude/master-files (symlink)"
- ✅ Visual arrows (→) in diagrams
- ✅ Explicit "symlink" or "link" in commands
- ✅ Verification steps after each command

### DON'T Use:
- ❌ "from X to Y" (ambiguous direction)
- ❌ "copy master-files" (NEVER copy!)
- ❌ "create master-files" (without specifying symlink)
- ❌ ".claude/master-files" (without indicating symlink)
- ❌ "configure" (ambiguous action)
- ❌ "setup" (without specific commands)

---

## Example Before/After

### BEFORE (Ambiguous):
```markdown
## Setup

1. Create .claude directory
2. Create symlink from ~/.claude/master-files to .claude/master-files
3. Verify setup

This creates master-files in your project.
```

### AFTER (Clear):
```markdown
## Setup

1. Create .claude directory:
   ```bash
   mkdir -p .claude
   ```

2. Create symlink .claude/master-files pointing to ~/.claude/master-files:
   ```bash
   ln -s ~/.claude/master-files .claude/master-files
   ```

3. Verify symlink created (must show → arrow):
   ```bash
   ls -la .claude/master-files
   # Expected output:
   # lrwxr-xr-x ... .claude/master-files → /Users/you/.claude/master-files
   ```

**Architecture:**
```
~/.claude/master-files/  ← Centralized source (real directory)
         ↑
         │ (symlink - use ln -s)
         │
.claude/master-files  ← Project access point (NOT a real directory!)
```

**⚠️ NEVER do this:**
- ❌ `mkdir master-files` (creates real directory)
- ❌ `cp -r ~/.claude/master-files ./master-files` (copies files)
- ❌ Any command that creates `./master-files/` in project root
```

---

## Action Plan

### This Session (Immediate):
1. ✅ Created OPENING_WORKFLOW_CRITICAL_WARNING.md with clear language
2. ✅ Created review script (review_workflows_ambiguous_language.py)
3. ✅ Ran audit and found 158 issues
4. ✅ Created this summary document

### Next Session (High Priority):
1. Update opening-workflow-guide.md Line 13 (critical ambiguity)
2. Add warning banner to top of all workflow files
3. Replace all "from X to Y" patterns
4. Add symlink indicators to common paths

### Future Sessions (Medium/Long Term):
1. Update all 147 instances of missing symlink indicators
2. Add verification steps after all setup commands
3. Create automated setup validator script
4. Add visual diagrams to all workflows
5. Create workflow writing guidelines document

---

## Testing Strategy

### Before Deploying Updates:
1. Have Claude Code read updated workflow
2. Ask: "What command would you run to set up master-files?"
3. Verify response is: `ln -s ~/.claude/master-files .claude/master-files`
4. NOT: `mkdir master-files` or `cp -r ...`

### Acceptance Criteria:
- ✅ Claude Code always uses `ln -s`
- ✅ Claude Code never creates `./master-files/` directory
- ✅ Claude Code always verifies with `ls -la`
- ✅ Claude Code checks for `→` arrow in output

---

## Statistics

- **Total workflows audited:** 9
- **Files with issues:** 9 (100%)
- **Total issues:** 158
- **High priority:** 15 (FROM-TO patterns, critical ambiguities)
- **Medium priority:** 147 (missing symlink indicators)
- **Estimated fix time:** 2-3 hours for high priority, 4-6 hours for all

---

## Lessons Learned

### For Workflow Documentation:
1. **Be explicit:** Never assume Claude Code understands context
2. **Use visual indicators:** Arrows (→) and labels (symlink)
3. **Show expected output:** Include `ls -la` examples
4. **Add verification:** Every command needs a verification step
5. **Avoid prepositions:** "from X to Y" is ambiguous, use "X → Y"

### For Claude Code:
1. **Always verify:** Run `ls -la` after `ln -s` commands
2. **Check for arrows:** Symlinks must show `→` in ls output
3. **Never assume:** If unclear, ask before creating directories
4. **Read warnings first:** Check for CRITICAL_WARNING documents

---

**Created:** October 25, 2025
**Tool:** review_workflows_ambiguous_language.py
**Status:** Audit complete, fixes pending
**Priority:** HIGH - Affects all projects using master-files-toolkit
