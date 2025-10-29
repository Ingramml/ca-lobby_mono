# Setup Master-Files-Toolkit in New Project

**Purpose:** Instructions for Claude Code to set up master-files-toolkit in any new project
**Location:** Add to global master-files so available everywhere
**Last Updated:** October 3, 2025

---

## 🎯 What This Does

This guide tells Claude Code how to set up the master-files-toolkit symlink structure in any new project, providing instant access to all agents, workflows, and guides.

---

## 📋 Instructions for Claude

When a user asks to "set up master-files in this project" or "add master-files-toolkit", follow these steps:

### Step 1: Check Current Project Structure

```bash
# Check if .claude directory exists
ls -la .claude/

# Check if master-files already linked
ls -la .claude/master-files
```

**Expected outcomes:**
- If `.claude/` doesn't exist: Create it (Step 2)
- If `master-files` symlink exists: Already set up, inform user
- If `master-files` directory exists (not symlink): Warn user about conflict

### Step 2: Create .claude Directory (if needed)

```bash
mkdir -p .claude
```

### Step 3: Create Symlink to Global Master-Files

```bash
ln -s ~/.claude/master-files .claude/master-files
```

**Important:** Always use the `~/.claude/master-files` path for consistency.

### Step 4: Verify Symlink

```bash
# Check symlink was created
ls -la .claude/master-files

# Verify it resolves correctly
readlink .claude/master-files

# Test access to contents
ls .claude/master-files/agents/
ls .claude/master-files/workflows/
```

**Expected output:**
```
lrwxr-xr-x  1 user  staff  41 Oct  3 09:05 .claude/master-files -> /Users/user/.claude/master-files
```

### Step 5: (Optional) Copy Reference Guide Locally

```bash
cp ~/.claude/master-files/MASTER_FILES_TOOLKIT_GUIDE.md .claude/
```

This provides a local reference, but it's also available via the symlink.

### Step 6: Verify Access

```bash
# Test reading a file through symlink
cat .claude/master-files/README.md

# List available agents
ls .claude/master-files/agents/*/
```

### Step 7: Update Project Documentation

If the project has a `CLAUDE.md` or `README.md`, inform the user you can add a section documenting that master-files is available:

```markdown
## Available Resources

This project has access to master-files-toolkit via `.claude/master-files/`:

**Agents:** `.claude/master-files/agents/`
- 35+ specialized agents for various tasks
- See: `.claude/master-files/agents/sub-agents-guide.md`

**Workflows:** `.claude/master-files/workflows/`
- Opening/closing workflows
- Context management
- Synchronization guides

**Guides:** `.claude/master-files/guides/`
- Claude Code learning resources
- Best practices
- Lessons learned

**Reference:** `.claude/master-files/MASTER_FILES_TOOLKIT_GUIDE.md`
```

---

## 🚨 Troubleshooting

### Issue: ~/.claude/master-files doesn't exist

**Solution:** The global master-files hasn't been cloned yet. Run:

```bash
cd ~/.claude
git clone https://github.com/Ingramml/master-files-toolkit.git master-files
```

Then retry the symlink creation.

### Issue: Symlink already exists

**Check if it's working:**
```bash
ls -la .claude/master-files/
```

If files appear, it's working correctly. Inform user: "master-files-toolkit is already set up in this project."

### Issue: .claude/master-files is a directory (not symlink)

**Solution:** Ask user if it's safe to replace:

```bash
# Backup existing if needed
mv .claude/master-files .claude/master-files-backup

# Create symlink
ln -s ~/.claude/master-files .claude/master-files
```

### Issue: Permission denied

**Solution:** Check file permissions:

```bash
# Check .claude directory permissions
ls -la .claude/

# Fix if needed
chmod 755 .claude/
```

---

## ✅ Success Indicators

After setup, these should all work:

```bash
# 1. Symlink exists
ls -la .claude/master-files

# 2. Points to correct location
readlink .claude/master-files
# Output: /Users/[username]/.claude/master-files

# 3. Can access agents
ls .claude/master-files/agents/

# 4. Can read files
cat .claude/master-files/README.md
```

---

## 📝 What to Tell the User

After successful setup, inform the user:

```
✅ Master-files-toolkit successfully set up!

**Available at:** .claude/master-files/

**What's included:**
- 35+ specialized agents (.claude/master-files/agents/)
- 8+ workflow guides (.claude/master-files/workflows/)
- Reference documentation (.claude/master-files/guides/)
- Automation scripts (.claude/master-files/scripts/)

**Key files:**
- Agent catalog: .claude/master-files/agents/sub-agents-guide.md
- Setup guide: .claude/master-files/MASTER_FILES_TOOLKIT_GUIDE.md
- Opening workflow: .claude/master-files/workflows/opening-workflow-guide.md
- Closing workflow: .claude/master-files/workflows/closing-workflow-guide.md

**Usage:**
Reference agents and workflows naturally in conversation:
"Claude, act as the React Specialist from master-files"
"Follow the opening workflow from master-files"

**Sync:**
To get latest updates: cd ~/.claude/master-files && git pull
```

---

## 🔄 Alternative: Git Submodule Approach

If the user prefers git submodule instead of symlink, use this approach:

```bash
# Add as submodule
git submodule add https://github.com/Ingramml/master-files-toolkit.git .claude/master-files

# Initialize and update
git submodule init
git submodule update

# Track submodule in git
git add .gitmodules .claude/master-files
git commit -m "Add master-files-toolkit as submodule"
```

**Note:** Submodules require more git knowledge. Only use if user specifically requests it.

---

## 📦 Quick Command Summary

**For Claude to execute:**

```bash
# Complete setup in 3 commands
mkdir -p .claude
ln -s ~/.claude/master-files .claude/master-files
ls -la .claude/master-files
```

**Verification:**
```bash
# Should show symlink
ls -la .claude/master-files

# Should show agents, workflows, guides, scripts
ls .claude/master-files/
```

---

## 🎯 When to Use This

Use this setup when:
- User starts a new project
- User asks to "add master-files"
- User wants access to agents/workflows
- User mentions "set up Claude Code workspace"
- User references "opening workflow" or "closing workflow"

**Proactive suggestion:**
If a user starts a new project and doesn't have `.claude/master-files/`, proactively ask:
"Would you like me to set up master-files-toolkit in this project? It provides access to 35+ specialized agents and workflow guides."

---

## 📚 Related Documentation

- **Complete Guide:** `.claude/master-files/MASTER_FILES_TOOLKIT_GUIDE.md`
- **Sync Guide:** `.claude/master-files/workflows/MASTER_FILES_SYNC_GUIDE.md`
- **Opening Workflow:** `.claude/master-files/workflows/opening-workflow-guide.md`
- **Closing Workflow:** `.claude/master-files/workflows/closing-workflow-guide.md`
- **Agent Catalog:** `.claude/master-files/agents/sub-agents-guide.md`

---

## 🔐 Security Notes

**DO:**
- ✅ Create symlinks to `~/.claude/master-files`
- ✅ Read files from master-files
- ✅ Follow workflows and use agents

**DON'T:**
- ❌ Modify files in master-files without user permission
- ❌ Add project-specific content to master-files
- ❌ Commit master-files symlink if user doesn't want it tracked
- ❌ Replace existing .claude/master-files directory without asking

---

## 📋 Checklist for Claude

When setting up master-files-toolkit:

- [ ] Check if `.claude/` directory exists
- [ ] Check if `master-files` already linked
- [ ] Create `.claude/` directory if needed
- [ ] Create symlink to `~/.claude/master-files`
- [ ] Verify symlink works (ls command)
- [ ] Test reading a file through symlink
- [ ] Inform user of success with file locations
- [ ] Offer to update project documentation
- [ ] Provide usage examples

---

## 💡 Example Usage for Claude

**User says:** "Set up master-files in this project"

**Claude responds:**

1. Runs checks:
```bash
ls -la .claude/master-files 2>/dev/null || echo "Not set up yet"
```

2. Creates setup:
```bash
mkdir -p .claude
ln -s ~/.claude/master-files .claude/master-files
```

3. Verifies:
```bash
ls -la .claude/master-files
ls .claude/master-files/agents/
```

4. Reports to user:
"✅ Master-files-toolkit successfully set up! You now have access to 35+ agents, 8+ workflows, and extensive documentation at `.claude/master-files/`"

---

**Instructions Version:** 1.0
**Last Updated:** October 3, 2025
**Maintained By:** Master-Files-Toolkit Repository

---

## Tags

#setup #master-files #new-project #symlink #workspace #initialization
