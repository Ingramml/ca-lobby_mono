#!/usr/bin/env python3
"""
Review all workflow files for ambiguous language that Claude Code might misunderstand
"""

import re
from pathlib import Path

# Workflow files to review
WORKFLOW_DIR = Path.home() / "Documents/GitHub/master-files-toolkit/workflows"

# Ambiguous patterns to look for
AMBIGUOUS_PATTERNS = [
    # Pattern 1: "from X to Y" - can be misread as copy operation
    (r'from\s+[`"]?([^`"\s]+)[`"]?\s+to\s+[`"]?([^`"\s]+)[`"]?',
     "FROM-TO pattern (ambiguous direction)",
     "Consider: 'Create X pointing to Y' or 'Link X → Y'"),

    # Pattern 2: "create" without specifying symlink vs directory
    (r'create\s+(?!symlink)(\w+[-/]\w+)',
     "CREATE without specifying symlink",
     "Clarify: 'create symlink' or 'create directory'"),

    # Pattern 3: "copy" near master-files (red flag!)
    (r'copy.*master[-_]files|master[-_]files.*copy',
     "COPY mentioned with master-files",
     "Should NEVER copy master-files, only symlink"),

    # Pattern 4: Ambiguous "link" (could mean URL or symlink)
    (r'\blink\s+(?!to|from)(\w+)',
     "LINK without clear direction",
     "Clarify: 'create symlink' or use ln -s command"),

    # Pattern 5: "setup" without specific steps
    (r'setup\s+master[-_]files(?!\s+by)',
     "SETUP without clear steps",
     "Specify exact commands: mkdir, ln -s, verify"),

    # Pattern 6: "configure" vs "create" ambiguity
    (r'configure\s+(\w+)\s+(?:directory|folder)',
     "CONFIGURE directory (ambiguous)",
     "Use 'create directory' or 'create symlink'"),

    # Pattern 7: Path without specifying if symlink or real
    (r'\.claude/master[-_]files(?!\s+→|\s+-|symlink)',
     ".claude/master-files without symlink indicator",
     "Add '(symlink)' or show with '→' arrow"),
]

def review_file(filepath):
    """Review a single file for ambiguous language"""
    issues = []

    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
        lines = content.split('\n')

    for line_num, line in enumerate(lines, 1):
        for pattern, issue_type, suggestion in AMBIGUOUS_PATTERNS:
            matches = re.finditer(pattern, line, re.IGNORECASE)
            for match in matches:
                issues.append({
                    'line': line_num,
                    'text': line.strip(),
                    'match': match.group(0),
                    'issue_type': issue_type,
                    'suggestion': suggestion
                })

    return issues

def main():
    print("=" * 80)
    print("WORKFLOW AMBIGUOUS LANGUAGE REVIEW")
    print("=" * 80)
    print()
    print("Searching for language patterns that Claude Code might misunderstand...")
    print()

    workflow_files = sorted(WORKFLOW_DIR.glob("*.md"))

    total_issues = 0
    files_with_issues = 0

    for filepath in workflow_files:
        issues = review_file(filepath)

        if issues:
            files_with_issues += 1
            total_issues += len(issues)

            print(f"\n{'='*80}")
            print(f"FILE: {filepath.name}")
            print(f"{'='*80}")

            for issue in issues:
                print(f"\n  Line {issue['line']}: {issue['issue_type']}")
                print(f"  Text: {issue['text'][:100]}...")
                print(f"  Match: '{issue['match']}'")
                print(f"  💡 {issue['suggestion']}")

    print(f"\n{'='*80}")
    print("SUMMARY")
    print(f"{'='*80}")
    print(f"Files reviewed: {len(workflow_files)}")
    print(f"Files with issues: {files_with_issues}")
    print(f"Total issues found: {total_issues}")
    print()

    if total_issues == 0:
        print("✅ No ambiguous language patterns found!")
    else:
        print("⚠️  Review issues above and update workflows for clarity")
        print()
        print("Priority patterns to fix:")
        print("  1. 'from X to Y' → 'Create X pointing to Y'")
        print("  2. 'create X' → 'create symlink X' or 'create directory X'")
        print("  3. '.claude/master-files' → '.claude/master-files (symlink)'")
        print("  4. Add '→' arrows in examples to show direction")
    print()

if __name__ == "__main__":
    main()
