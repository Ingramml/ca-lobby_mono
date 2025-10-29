#!/usr/bin/env python3
"""
Extract Sample Data for CA Lobby Application
Creates trimmed dataset following SAMPLE_DATA_SIZE_STRATEGY.md

Target Organizations:
1. ALAMEDA COUNTY (government entity)
2. ALAMEDA City (city government)
3. One ALAMEDA COUNTY department/agency
4. One ALAMEDA City department/agency
5. One ALAMEDA business
6. One random edge case (long name)
"""

import pandas as pd
import json
import os
from pathlib import Path
import random

# Configuration
SAMPLE_DATA_DIR = Path("Sample data")
OUTPUT_DIR = Path("src/data")
OUTPUT_DIR.mkdir(exist_ok=True)

# Load all CSV files
print("=" * 60)
print("CA LOBBY SAMPLE DATA EXTRACTION")
print("=" * 60)
print()

print("Loading CSV files...")
filers_df = pd.read_csv(SAMPLE_DATA_DIR / "Alameda_Filers.csv")
employers_df = pd.read_csv(SAMPLE_DATA_DIR / "Alameda_Employers.csv")
expenditures_df = pd.read_csv(SAMPLE_DATA_DIR / "Alameda_Expenditures.csv")
lobby_df = pd.read_csv(SAMPLE_DATA_DIR / "Alameda_Lobby_Disclosures.csv")
payments_df = pd.read_csv(SAMPLE_DATA_DIR / "Alameda_Payments.csv")
registrations_df = pd.read_csv(SAMPLE_DATA_DIR / "Alameda_Registrations.csv")

print(f"✓ Loaded {len(filers_df)} filer records")
print(f"✓ Loaded {len(employers_df)} employer records")
print(f"✓ Loaded {len(expenditures_df)} expenditure records")
print(f"✓ Loaded {len(lobby_df)} lobby disclosure records")
print(f"✓ Loaded {len(payments_df)} payment records")
print(f"✓ Loaded {len(registrations_df)} registration records")
print()

# Select Target Organizations
print("Selecting target organizations...")
print()

# 1. ALAMEDA COUNTY (main government entity)
county_org = filers_df[filers_df['LAST_NAME'] == 'ALAMEDA COUNTY'].iloc[0]
print(f"1. County Government: {county_org['LAST_NAME']}")

# 2. ALAMEDA City government
city_candidates = filers_df[
    filers_df['LAST_NAME'].str.contains('ALAMEDA CITY UNIFIED SCHOOL DISTRICT', case=False, na=False)
]
if len(city_candidates) > 0:
    city_org = city_candidates.iloc[0]
    print(f"2. City Entity: {city_org['LAST_NAME']}")
else:
    city_org = None
    print("2. City Entity: Not found - will use alternative")

# 3. ALAMEDA COUNTY department/agency
county_agencies = filers_df[
    filers_df['LAST_NAME'].str.contains('ALAMEDA COUNTY', case=False, na=False) &
    (filers_df['LAST_NAME'].str.contains('AUTHORITY|AGENCY|DISTRICT|COMMISSION', case=False, na=False))
]['LAST_NAME'].unique()
county_dept = filers_df[filers_df['LAST_NAME'] == 'ALAMEDA COUNTY WASTE MANAGEMENT AUTHORITY'].iloc[0]
print(f"3. County Department: {county_dept['LAST_NAME']}")

# 4. ALAMEDA City department
city_dept_candidates = filers_df[filers_df['LAST_NAME'].str.contains('ALAMEDA HEALTH', case=False, na=False)]
if len(city_dept_candidates) > 0:
    city_dept = city_dept_candidates.iloc[0]
    print(f"4. City Department: {city_dept['LAST_NAME']}")
else:
    # Fallback to any district
    city_dept = filers_df[filers_df['LAST_NAME'] == 'ALAMEDA UNIFIED SCHOOL DISTRICT'].iloc[0]
    print(f"4. City Department: {city_dept['LAST_NAME']}")

# 5. ALAMEDA business
business = filers_df[filers_df['LAST_NAME'] == 'ALAMEDA PRODUCE MARKET, INC.'].iloc[0]
print(f"5. Business: {business['LAST_NAME']}")

# 6. Edge case - long name
edge_cases = filers_df[filers_df['LAST_NAME'].str.len() > 100]
random_edge = edge_cases.sample(1).iloc[0]
print(f"6. Edge Case: {random_edge['LAST_NAME'][:80]}...")
print()

# Collect all selected FILER_IDs
selected_filer_ids = [
    county_org['FILER_ID'],
    county_dept['FILER_ID'],
    city_dept['FILER_ID'],
    business['FILER_ID'],
    random_edge['FILER_ID']
]

if city_org is not None:
    selected_filer_ids.append(city_org['FILER_ID'])

selected_orgs = [
    {
        'id': county_org['FILER_ID'],
        'name': county_org['LAST_NAME'],
        'type': 'County Government'
    },
    {
        'id': county_dept['FILER_ID'],
        'name': county_dept['LAST_NAME'],
        'type': 'County Department'
    },
    {
        'id': city_dept['FILER_ID'],
        'name': city_dept['LAST_NAME'],
        'type': 'City Department'
    },
    {
        'id': business['FILER_ID'],
        'name': business['LAST_NAME'],
        'type': 'Business'
    },
    {
        'id': random_edge['FILER_ID'],
        'name': random_edge['LAST_NAME'],
        'type': 'Edge Case (Long Name)'
    }
]

if city_org is not None:
    selected_orgs.insert(1, {
        'id': city_org['FILER_ID'],
        'name': city_org['LAST_NAME'],
        'type': 'City Government'
    })

print(f"Selected {len(selected_orgs)} organizations")
print()

# Extract related data for selected organizations
print("Extracting related data...")
print()

# Get all activities for these organizations
lobby_activities = lobby_df[lobby_df['FILER_ID'].isin(selected_filer_ids)]
print(f"✓ Found {len(lobby_activities)} lobby disclosure records")

payments_activities = payments_df[payments_df['FILING_ID'].isin(lobby_activities['FILING_ID'])]
print(f"✓ Found {len(payments_activities)} payment records")

registrations_activities = registrations_df[registrations_df['FILER_ID'].isin(selected_filer_ids)]
print(f"✓ Found {len(registrations_activities)} registration records")

expenditures_activities = expenditures_df[expenditures_df['FILING_ID'].isin(lobby_activities['FILING_ID'])]
print(f"✓ Found {len(expenditures_activities)} expenditure records")
print()

# Generate Tier 1: Summary Data (organizations-summary.json)
print("Generating Tier 1: organizations-summary.json...")
organizations_summary = []

for org in selected_orgs:
    org_id = org['id']
    org_name = org['name']

    # Get activities for this org
    org_lobby = lobby_activities[lobby_activities['FILER_ID'] == org_id]
    org_payments = payments_activities[payments_activities['FILING_ID'].isin(org_lobby['FILING_ID'])]

    # Calculate metrics
    total_spending = org_payments['FEES_AMOUNT'].sum() if len(org_payments) > 0 else 0
    activity_count = len(org_lobby)

    # Get date range
    if len(org_lobby) > 0 and 'FROM_DATE' in org_lobby.columns:
        first_activity = pd.to_datetime(org_lobby['FROM_DATE'], errors='coerce').min()
        last_activity = pd.to_datetime(org_lobby['THRU_DATE'], errors='coerce').max()
        first_activity_str = first_activity.strftime('%Y-%m-%d') if pd.notna(first_activity) else None
        last_activity_str = last_activity.strftime('%Y-%m-%d') if pd.notna(last_activity) else None
    else:
        first_activity_str = None
        last_activity_str = None

    # Get organization type
    org_type = org_lobby['ORGANIZATION_TYPE'].mode()[0] if len(org_lobby) > 0 and 'ORGANIZATION_TYPE' in org_lobby.columns else 'UNKNOWN'

    organizations_summary.append({
        'id': f"org_{org_id}",
        'filer_id': int(org_id),
        'name': org_name,
        'organization_type': org_type,
        'category': org['type'],
        'totalSpending': float(total_spending) if pd.notna(total_spending) else 0.0,
        'activityCount': int(activity_count),
        'firstActivity': first_activity_str,
        'lastActivity': last_activity_str,
        'lobbyistCount': len(org_payments['EMPLOYER_LAST_NAME'].unique()) if len(org_payments) > 0 else 0
    })

summary_output = {
    'metadata': {
        'totalOrganizations': len(organizations_summary),
        'lastUpdated': pd.Timestamp.now().strftime('%Y-%m-%d'),
        'dataVersion': '1.0',
        'dataSource': 'Alameda County Sample Data',
        'description': 'Sample dataset for CA Lobby application testing'
    },
    'organizations': organizations_summary
}

# Save Tier 1
tier1_file = OUTPUT_DIR / 'organizations-summary.json'
with open(tier1_file, 'w') as f:
    json.dump(summary_output, f, indent=2)

file_size_kb = tier1_file.stat().st_size / 1024
print(f"✓ Created {tier1_file} ({file_size_kb:.1f} KB)")
print()

# Generate Tier 2: Individual Profile JSONs
print("Generating Tier 2: Individual profile JSONs...")
profiles_dir = OUTPUT_DIR / 'profiles'
profiles_dir.mkdir(exist_ok=True)

for org in selected_orgs:
    org_id = org['id']
    org_name = org['name']

    # Sanitize filename
    filename = org_name.lower().replace(' ', '-').replace(',', '').replace('.', '')
    filename = ''.join(c for c in filename if c.isalnum() or c == '-')[:50]  # Limit length

    # Get all data for this org
    org_lobby = lobby_activities[lobby_activities['FILER_ID'] == org_id]
    org_payments = payments_activities[payments_activities['FILING_ID'].isin(org_lobby['FILING_ID'])]
    org_registrations = registrations_activities[registrations_activities['FILER_ID'] == org_id]

    # Build activities list
    activities = []
    for idx, row in org_lobby.head(50).iterrows():  # Limit to first 50 activities
        filing_id = row['FILING_ID']
        filing_payments = org_payments[org_payments['FILING_ID'] == filing_id]

        total_amount = filing_payments['FEES_AMOUNT'].sum() if len(filing_payments) > 0 else 0

        activity = {
            'id': f"act_{filing_id}",
            'filing_id': int(filing_id),
            'date': pd.to_datetime(row.get('FROM_DATE'), errors='coerce').strftime('%Y-%m-%d') if pd.notna(row.get('FROM_DATE')) else None,
            'thru_date': pd.to_datetime(row.get('THRU_DATE'), errors='coerce').strftime('%Y-%m-%d') if pd.notna(row.get('THRU_DATE')) else None,
            'amount': float(total_amount) if pd.notna(total_amount) else 0.0,
            'organization_type': str(row.get('ORGANIZATION_TYPE', 'UNKNOWN')),
            'form_type': str(row.get('FORM_TYPE', 'UNKNOWN'))
        }
        activities.append(activity)

    # Build lobbyist network
    lobbyists = []
    if len(org_payments) > 0:
        lobbyist_groups = org_payments.groupby('EMPLOYER_LAST_NAME').agg({
            'FEES_AMOUNT': 'sum',
            'FILING_ID': 'count'
        }).reset_index()

        for idx, row in lobbyist_groups.head(20).iterrows():
            lobbyists.append({
                'name': str(row['EMPLOYER_LAST_NAME']),
                'activityCount': int(row['FILING_ID']),
                'totalAmount': float(row['FEES_AMOUNT']) if pd.notna(row['FEES_AMOUNT']) else 0.0
            })

    # Calculate summary metrics
    total_spending = org_payments['FEES_AMOUNT'].sum() if len(org_payments) > 0 else 0

    profile_data = {
        'id': f"org_{org_id}",
        'filer_id': int(org_id),
        'name': org_name,
        'category': org['type'],
        'summary': {
            'totalSpending': float(total_spending) if pd.notna(total_spending) else 0.0,
            'activityCount': len(org_lobby),
            'averageSpending': float(total_spending / len(org_lobby)) if len(org_lobby) > 0 else 0.0,
            'firstActivity': activities[0]['date'] if len(activities) > 0 and activities[0]['date'] else None,
            'lastActivity': activities[-1]['date'] if len(activities) > 0 and activities[-1]['date'] else None,
            'registrationCount': len(org_registrations)
        },
        'activities': activities,
        'lobbyists': lobbyists,
        'relatedOrganizations': []  # Could be populated by similarity algorithm
    }

    # Save profile
    profile_file = profiles_dir / f"{filename}.json"
    with open(profile_file, 'w') as f:
        json.dump(profile_data, f, indent=2)

    profile_size_kb = profile_file.stat().st_size / 1024
    print(f"  ✓ {filename}.json ({profile_size_kb:.1f} KB) - {len(activities)} activities, {len(lobbyists)} lobbyists")

print()
print("=" * 60)
print("EXTRACTION COMPLETE")
print("=" * 60)
print()
print(f"Tier 1 (Summary): {tier1_file}")
print(f"Tier 2 (Profiles): {profiles_dir}/ ({len(selected_orgs)} files)")
print()
print("📊 Dataset Statistics:")
print(f"  Total Organizations: {len(selected_orgs)}")
print(f"  Total Activities: {len(lobby_activities)}")
print(f"  Total Payments: {len(payments_activities)}")
print(f"  Total Registrations: {len(registrations_activities)}")
print()
print("✅ Ready to use in React application!")
print()
print("Next steps:")
print("  1. Review generated JSON files in src/data/")
print("  2. Update Search component to use organizations-summary.json")
print("  3. Update OrganizationProfile to lazy-load from profiles/")
print("  4. Test performance with real data")
