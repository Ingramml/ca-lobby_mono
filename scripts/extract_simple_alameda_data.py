#!/usr/bin/env python3
"""
Simple Alameda County Lobbying Data Extraction
Focuses only on core government entities: County, City, School Districts, Major Agencies
"""

import pandas as pd
import json
from pathlib import Path
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# Paths
BASE_DIR = Path(__file__).parent.parent
SAMPLE_DATA_DIR = BASE_DIR / "Sample data"
OUTPUT_DIR = BASE_DIR / "src" / "data"
PROFILES_DIR = OUTPUT_DIR / "profiles"

# Create output directories
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
PROFILES_DIR.mkdir(parents=True, exist_ok=True)

# Core Alameda government entities - exact names
CORE_ORGANIZATIONS = [
    'ALAMEDA COUNTY OF',
    'ALAMEDA, CITY OF',
    'ALAMEDA COUNTY WASTE MANAGEMENT AUTHORITY',
    'ALAMEDA UNIFIED SCHOOL DISTRICT',
    'ALAMEDA ALLIANCE FOR HEALTH',
    'ALAMEDA CORRIDOR-EAST CONSTRUCTION AUTHORITY',
    'ALAMEDA COUNTY WATER DISTRICT',
    'ALAMEDA CORRIDOR TRANSPORTATION AUTHORITY',
    'ALAMEDA COUNTY TRANSPORTATION IMPROVEMENT AUTHORITY',
    'ALAMEDA COUNTY CONGESTION MANAGEMENT AGENCY',
    'ALAMEDA COUNTY FAIR',
    "ALAMEDA COUNTY EMPLOYEES' RETIREMENT ASSOCIATION"
]

print("=" * 70)
print("CA LOBBY - SIMPLE BIGQUERY VIEW DATA EXTRACTION")
print("=" * 70)
print()
print("Loading data sources...")
print("-" * 70)

# Load CSVs
filers = pd.read_csv(SAMPLE_DATA_DIR / "v_filers_alameda.csv", low_memory=False)
disclosures = pd.read_csv(SAMPLE_DATA_DIR / "v_disclosures_alameda.csv", low_memory=False)
payments = pd.read_csv(SAMPLE_DATA_DIR / "v_payments_alameda.csv", low_memory=False)

print(f"✓ Loaded filers: {len(filers)} rows")
print(f"✓ Loaded disclosures: {len(disclosures)} rows")
print(f"✓ Loaded payments: {len(payments)} rows")
print()

organizations = []

for org_name in CORE_ORGANIZATIONS:
    print(f"Processing: {org_name}")

    # Find filer(s) for this organization
    org_filers = filers[
        (filers['last_name'].fillna('').str.upper() == org_name) |
        (filers['full_name'].fillna('').str.upper() == org_name)
    ]

    if len(org_filers) == 0:
        print(f"  ⚠️  Not found in filers")
        continue

    # Get first filer_id
    filer_id = org_filers.iloc[0]['filer_id']
    print(f"  Filer ID: {filer_id}")

    # Get disclosures
    org_disclosures = disclosures[disclosures['filer_id'] == filer_id]

    # Get payments
    org_payments = payments[
        payments['employer_full_name'].fillna('').str.upper().str.contains(org_name, regex=False)
    ]

    total_activities = len(org_disclosures) + len(org_payments)
    total_spending = org_payments['period_total'].fillna(0).sum()

    # Get date range
    dates = []
    if not org_disclosures.empty:
        dates.extend(pd.to_datetime(org_disclosures['period_start_date'], errors='coerce').dropna().tolist())
        dates.extend(pd.to_datetime(org_disclosures['period_end_date'], errors='coerce').dropna().tolist())

    first_activity = min(dates).strftime('%Y-%m-%d') if dates else None
    last_activity = max(dates).strftime('%Y-%m-%d') if dates else None

    # Determine category
    if 'COUNTY OF' in org_name or (org_name.startswith('ALAMEDA COUNTY') and not any(x in org_name for x in ['WASTE', 'WATER', 'TRANSPORT', 'CORRIDOR', 'CONGEST', 'FAIR', 'EMPLOYEES'])):
        category = 'County Government'
    elif 'CITY OF' in org_name:
        category = 'City Government'
    elif 'WASTE' in org_name or 'WATER' in org_name or 'TRANSPORT' in org_name or 'CONGEST' in org_name:
        category = 'County Department'
    elif 'SCHOOL' in org_name or 'UNIFIED' in org_name:
        category = 'School District'
    elif 'HEALTH' in org_name or 'ALLIANCE' in org_name:
        category = 'Health Organization'
    elif 'CORRIDOR' in org_name or 'CONSTRUCTION' in org_name:
        category = 'Construction Authority'
    else:
        category = 'County Department'

    organizations.append({
        'id': f'org_{filer_id}',
        'filer_id': str(filer_id),
        'name': org_name,
        'category': category,
        'activityCount': total_activities,
        'totalSpending': round(float(total_spending), 2),
        'averageSpending': round(float(total_spending / total_activities) if total_activities > 0 else 0, 2),
        'firstActivity': first_activity,
        'lastActivity': last_activity
    })

    print(f"  Activities: {total_activities}")
    print(f"  Total Spending: ${total_spending:,.2f}")
    print()

# Sort by activity count
organizations = sorted(organizations, key=lambda x: x['activityCount'], reverse=True)

# Create summary
summary = {
    'metadata': {
        'totalOrganizations': len(organizations),
        'lastUpdated': datetime.now().strftime('%Y-%m-%d'),
        'dataVersion': '2.0',
        'dataSource': 'BigQuery Views'
    },
    'organizations': organizations
}

# Save summary
summary_path = OUTPUT_DIR / 'organizations-summary.json'
with open(summary_path, 'w') as f:
    json.dump(summary, f, indent=2)

print("=" * 70)
print(f"✓ Created organizations summary: {len(organizations)} organizations")
print(f"  Saved to: {summary_path}")
print("=" * 70)
print()
print("Organizations processed:")
for org in organizations:
    print(f"  - {org['name']}: {org['activityCount']} activities")
print()
print("✓ DATA EXTRACTION COMPLETE")
