#!/usr/bin/env python3
"""
Fix incorrect year dates in markdown files
Changes 2024 dates (Sept-Dec) to 2025 since we're currently in October 2025
"""

import os
import re
from pathlib import Path
from datetime import datetime

# Current date context: October 25, 2025
CURRENT_YEAR = 2025

# Files to fix (from grep search)
files_to_check = [
    "Documents/BigQuery_Optimization_Quick_Start.md",
    "Documents/BigQuery_Optimization_Plan.md",
    "ALAMEDA_EXTRACTION_README.md",
    "Documents/Complete_Guide_to_Database_Indexing.md",
    "Documents/context.md",
    "Claude_files/templates/README.md",
    "Claude_files/scripts/PROJECT-SETUP-SCRIPT-GUIDE.md",
    "Claude_files/MULTI-MACHINE-SYNC-GUIDE.md",
    "Claude_files/QUICK-SYNC-REFERENCE.md",
    "Claude_files/agents/workflow-management/workflow-auditor.md",
    "Claude_files/agents/specialized/research-comparison-specialist.md",
    "Claude_files/agents/specialized/database-hosting-advisor.md",
    "Claude_files/agents/specialized/deployment-safe-project-planner.md",
    "Claude_files/workflows/centralization-plan.md",
    "Claude_files/workflows/context-management-workflow.md",
    "Claude_files/workflows/git-submodule-implementation.md",
    "Claude_files/workflows/sync-workflows.md",
    "Claude_files/workflows/closing-workflow-guide.md",
    "Claude_files/workflows/opening-workflow-guide.md",
    "Claude_files/GENERIC-WORKFLOW-RECOMMENDATIONS.md",
    "master-files/workflows/opening-workflow-guide.md",
    "master-files/workflows/centralization-plan.md",
    "master-files/workflows/sync-workflows.md",
    "master-files/workflows/closing-workflow-guide.md",
]

# Patterns to replace
# Looking for 2024 dates in September, October, November, December
patterns_to_fix = [
    (r'2024-09-(\d{2})', r'2025-09-\1'),  # September 2024 -> 2025
    (r'2024-10-(\d{2})', r'2025-10-\1'),  # October 2024 -> 2025
    (r'2024-11-(\d{2})', r'2025-11-\1'),  # November 2024 -> 2025
    (r'2024-12-(\d{2})', r'2025-12-\1'),  # December 2024 -> 2025
]

def fix_file_dates(file_path):
    """Fix dates in a single file"""
    if not os.path.exists(file_path):
        return None, "File not found"

    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    original_content = content
    changes_made = []

    # Apply each pattern
    for pattern, replacement in patterns_to_fix:
        matches = re.findall(pattern, content)
        if matches:
            for match in matches:
                old_date = pattern.replace(r'(\d{2})', match)
                new_date = replacement.replace(r'\1', match)
                changes_made.append(f"{old_date} -> {new_date}")

            content = re.sub(pattern, replacement, content)

    # Only write if changes were made
    if content != original_content:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return len(changes_made), changes_made

    return 0, []

# Process all files
print("=" * 80)
print("FIXING INCORRECT YEAR DATES IN MARKDOWN FILES")
print("=" * 80)
print(f"Current date context: October 25, {CURRENT_YEAR}")
print(f"Fixing: 2024 dates (Sept-Dec) -> {CURRENT_YEAR}")
print()

total_files_changed = 0
total_changes = 0

for file_path in files_to_check:
    full_path = Path(file_path)

    if not full_path.exists():
        print(f"⚠️  SKIP: {file_path} (not found)")
        continue

    num_changes, changes = fix_file_dates(full_path)

    if num_changes is None:
        print(f"⚠️  SKIP: {file_path} ({changes})")
    elif num_changes > 0:
        print(f"✓ FIXED: {file_path}")
        for change in changes:
            print(f"    {change}")
        total_files_changed += 1
        total_changes += num_changes
    else:
        print(f"  OK: {file_path} (no changes needed)")

print()
print("=" * 80)
print("SUMMARY")
print("=" * 80)
print(f"Files checked: {len(files_to_check)}")
print(f"Files changed: {total_files_changed}")
print(f"Total date corrections: {total_changes}")
print()

if total_files_changed > 0:
    print("✅ Date corrections complete!")
    print()
    print("Next steps:")
    print("1. Review changes with: git diff")
    print("2. Commit changes if satisfied")
else:
    print("ℹ️  No changes needed - all dates are correct")
