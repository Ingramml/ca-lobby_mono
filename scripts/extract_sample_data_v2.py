#!/usr/bin/env python3
"""
Extract Sample Data for CA Lobby Application - Version 2
Creates trimmed dataset following SAMPLE_DATA_SIZE_STRATEGY.md

Target Organizations (from actual lobby data):
1. ALAMEDA COUNTY (government entity)
2. ALAMEDA, CITY OF (city government
3. ALAMEDA COUNTY WASTE MANAGEMENT AUTHORITY (county department)
4. ALAMEDA UNIFIED SCHOOL DISTRICT (city department/education)
5. ALAMEDA ALLIANCE FOR HEALTH (business/organization)
6. Edge case: Long or unusual name

Uses actual lobby disclosure data, not general filers.
"""

import pandas as pd
import json
import os
from pathlib import Path
import random
from datetime import datetime

# Configuration
SAMPLE_DATA_DIR = Path("Sample data")
OUTPUT_DIR = Path("src/data")
OUTPUT_DIR.mkdir(exist_ok=True)

# Load all CSV files
print("=" * 60)
print("CA LOBBY SAMPLE DATA EXTRACTION - V2")
print("=" * 60)
print()

print("Loading CSV files...")
lobby_df = pd.read_csv(SAMPLE_DATA_DIR / "Alameda_Lobby_Disclosures.csv")
payments_df = pd.read_csv(SAMPLE_DATA_DIR / "Alameda_Payments.csv")
registrations_df = pd.read_csv(SAMPLE_DATA_DIR / "Alameda_Registrations.csv")

print(f"✓ Loaded {len(lobby_df)} lobby disclosure records")
print(f"✓ Loaded {len(payments_df)} payment records")
print(f"✓ Loaded {len(registrations_df)} registration records")
print(f"✓ Found {lobby_df['FILER_LAST_NAME'].nunique()} unique organizations")
print()

# Select Target Organizations based on actual lobby data
print("Selecting target organizations from lobby data...")
print()

selected_org_names = [
    "ALAMEDA COUNTY",                              # 1. County government
    "ALAMEDA, CITY OF",                            # 2. City government
    "ALAMEDA COUNTY WASTE MANAGEMENT AUTHORITY",   # 3. County department
    "ALAMEDA UNIFIED SCHOOL DISTRICT",             # 4. City department
    "ALAMEDA ALLIANCE FOR HEALTH",                 # 5. Business/Health org
    "ALAMEDA CORRIDOR-EAST CONSTRUCTION AUTHORITY" # 6. Edge case (construction authority)
]

selected_orgs = []
for idx, org_name in enumerate(selected_org_names, 1):
    org_data = lobby_df[lobby_df['FILER_LAST_NAME'] == org_name]
    if len(org_data) > 0:
        filer_id = org_data.iloc[0]['FILER_ID']
        print(f"{idx}. {org_name}")
        print(f"   FILER_ID: {filer_id}, Activities: {len(org_data)}")

        selected_orgs.append({
            'name': org_name,
            'filer_id': filer_id,
            'type': ['County Government', 'City Government', 'County Department',
                     'City Department', 'Health Organization', 'Construction Authority'][idx-1]
        })
    else:
        print(f"{idx}. {org_name} - NOT FOUND")

print()
print(f"✓ Selected {len(selected_orgs)} organizations with lobby data")
print()

# Extract all related data
print("Extracting comprehensive data...")
selected_filer_ids = [org['filer_id'] for org in selected_orgs]

# Get all lobby activities for these organizations
all_lobby_data = lobby_df[lobby_df['FILER_ID'].isin(selected_filer_ids)]
all_filing_ids = all_lobby_data['FILING_ID'].unique()

# Get all payments for these filings
all_payments = payments_df[payments_df['FILING_ID'].isin(all_filing_ids)]

# Get all registrations
all_registrations = registrations_df[registrations_df['FILER_ID'].isin(selected_filer_ids)]

print(f"✓ Lobby activities: {len(all_lobby_data)}")
print(f"✓ Payment records: {len(all_payments)}")
print(f"✓ Registrations: {len(all_registrations)}")
print()

# Generate Tier 1: Summary Data (organizations-summary.json)
print("Generating Tier 1: organizations-summary.json...")
organizations_summary = []

for org in selected_orgs:
    filer_id = org['filer_id']
    org_name = org['name']

    # Get all activities for this org
    org_lobby = all_lobby_data[all_lobby_data['FILER_ID'] == filer_id]
    org_filing_ids = org_lobby['FILING_ID'].unique()
    org_payments = all_payments[all_payments['FILING_ID'].isin(org_filing_ids)]
    org_registrations = all_registrations[all_registrations['FILER_ID'] == filer_id]

    # Calculate total spending
    total_fees = org_payments['FEES_AMOUNT'].sum() if 'FEES_AMOUNT' in org_payments.columns else 0
    total_reimbursement = org_payments['REIMBURSEMENT_AMOUNT'].sum() if 'REIMBURSEMENT_AMOUNT' in org_payments.columns else 0
    total_advance = org_payments['ADVANCE_AMOUNT'].sum() if 'ADVANCE_AMOUNT' in org_payments.columns else 0
    total_spending = total_fees + total_reimbursement + total_advance

    # Get date range
    if len(org_lobby) > 0 and 'FROM_DATE' in org_lobby.columns:
        from_dates = pd.to_datetime(org_lobby['FROM_DATE'], errors='coerce')
        thru_dates = pd.to_datetime(org_lobby['THRU_DATE'], errors='coerce')
        first_activity = from_dates.min()
        last_activity = thru_dates.max()
        first_activity_str = first_activity.strftime('%Y-%m-%d') if pd.notna(first_activity) else None
        last_activity_str = last_activity.strftime('%Y-%m-%d') if pd.notna(last_activity) else None
    else:
        first_activity_str = None
        last_activity_str = None

    # Get lobbyist count
    lobbyist_count = org_payments['EMPLOYER_LAST_NAME'].nunique() if 'EMPLOYER_LAST_NAME' in org_payments.columns else 0

    # Get organization type
    org_type = org_lobby['ORGANIZATION_TYPE'].mode()[0] if len(org_lobby) > 0 and 'ORGANIZATION_TYPE' in org_lobby.columns else 'UNKNOWN'

    summary = {
        'id': f"org_{filer_id}",
        'filer_id': str(filer_id),  # Keep as string - can be alphanumeric
        'name': org_name,
        'organization_type': org_type,
        'category': org['type'],
        'totalSpending': float(total_spending) if pd.notna(total_spending) else 0.0,
        'activityCount': int(len(org_lobby)),
        'registrationCount': int(len(org_registrations)),
        'firstActivity': first_activity_str,
        'lastActivity': last_activity_str,
        'lobbyistCount': int(lobbyist_count)
    }

    organizations_summary.append(summary)
    print(f"  ✓ {org_name[:50]}: ${total_spending:,.0f}, {len(org_lobby)} activities")

summary_output = {
    'metadata': {
        'totalOrganizations': len(organizations_summary),
        'lastUpdated': datetime.now().strftime('%Y-%m-%d'),
        'dataVersion': '1.0',
        'dataSource': 'Alameda County Lobby Data Sample',
        'description': 'Sample dataset for CA Lobby application testing - 6 representative organizations'
    },
    'organizations': organizations_summary
}

# Save Tier 1
tier1_file = OUTPUT_DIR / 'organizations-summary.json'
with open(tier1_file, 'w') as f:
    json.dump(summary_output, f, indent=2)

file_size_kb = tier1_file.stat().st_size / 1024
print()
print(f"✓ Created {tier1_file} ({file_size_kb:.1f} KB)")
print()

# Generate Tier 2: Individual Profile JSONs
print("Generating Tier 2: Individual profile JSONs...")
profiles_dir = OUTPUT_DIR / 'profiles'
profiles_dir.mkdir(exist_ok=True)

for org in selected_orgs:
    filer_id = org['filer_id']
    org_name = org['name']

    # Sanitize filename
    filename = org_name.lower().replace(' ', '-').replace(',', '').replace('.', '')
    filename = ''.join(c for c in filename if c.isalnum() or c == '-')[:50]

    # Get all data for this org
    org_lobby = all_lobby_data[all_lobby_data['FILER_ID'] == filer_id]
    org_filing_ids = org_lobby['FILING_ID'].unique()
    org_payments = all_payments[all_payments['FILING_ID'].isin(org_filing_ids)]
    org_registrations = all_registrations[all_registrations['FILER_ID'] == filer_id]

    # Build activities list (limit to first 100)
    activities = []
    for idx, row in org_lobby.head(100).iterrows():
        filing_id = row['FILING_ID']
        filing_payments = org_payments[org_payments['FILING_ID'] == filing_id]

        # Calculate total for this activity
        total_amount = 0
        if len(filing_payments) > 0:
            total_amount = (
                filing_payments['FEES_AMOUNT'].sum() +
                filing_payments['REIMBURSEMENT_AMOUNT'].sum() +
                filing_payments['ADVANCE_AMOUNT'].sum()
            )

        activity = {
            'id': f"act_{filing_id}",
            'filing_id': int(filing_id),
            'amend_id': int(row.get('AMEND_ID', 0)),
            'from_date': pd.to_datetime(row.get('FROM_DATE'), errors='coerce').strftime('%Y-%m-%d') if pd.notna(row.get('FROM_DATE')) else None,
            'thru_date': pd.to_datetime(row.get('THRU_DATE'), errors='coerce').strftime('%Y-%m-%d') if pd.notna(row.get('THRU_DATE')) else None,
            'report_date': pd.to_datetime(row.get('REPORT_DATE'), errors='coerce').strftime('%Y-%m-%d') if pd.notna(row.get('REPORT_DATE')) else None,
            'amount': float(total_amount) if pd.notna(total_amount) else 0.0,
            'organization_type': str(row.get('ORGANIZATION_TYPE', 'UNKNOWN')),
            'form_type': str(row.get('FORM_TYPE', 'UNKNOWN')),
            'firm_name': str(row.get('FIRM_NAME', '')) if pd.notna(row.get('FIRM_NAME')) else None
        }
        activities.append(activity)

    # Build lobbyist network
    lobbyists = []
    if 'EMPLOYER_LAST_NAME' in org_payments.columns and len(org_payments) > 0:
        lobbyist_groups = org_payments.groupby('EMPLOYER_LAST_NAME').agg({
            'FEES_AMOUNT': 'sum',
            'REIMBURSEMENT_AMOUNT': 'sum',
            'ADVANCE_AMOUNT': 'sum',
            'FILING_ID': 'count'
        }).reset_index()

        lobbyist_groups['total_amount'] = (
            lobbyist_groups['FEES_AMOUNT'] +
            lobbyist_groups['REIMBURSEMENT_AMOUNT'] +
            lobbyist_groups['ADVANCE_AMOUNT']
        )

        lobbyist_groups = lobbyist_groups.sort_values('total_amount', ascending=False)

        for idx, row in lobbyist_groups.head(30).iterrows():
            if pd.notna(row['EMPLOYER_LAST_NAME']) and row['EMPLOYER_LAST_NAME'] != '':
                lobbyists.append({
                    'name': str(row['EMPLOYER_LAST_NAME']),
                    'activityCount': int(row['FILING_ID']),
                    'totalAmount': float(row['total_amount']),
                    'fees': float(row['FEES_AMOUNT']),
                    'reimbursements': float(row['REIMBURSEMENT_AMOUNT']),
                    'advances': float(row['ADVANCE_AMOUNT'])
                })

    # Calculate spending trends by quarter
    spending_trends = []
    if len(org_lobby) > 0:
        for idx, row in org_lobby.iterrows():
            from_date = pd.to_datetime(row.get('FROM_DATE'), errors='coerce')
            if pd.notna(from_date):
                quarter = f"Q{(from_date.month-1)//3 + 1} {from_date.year}"
                filing_id = row['FILING_ID']
                filing_payments = org_payments[org_payments['FILING_ID'] == filing_id]
                amount = (filing_payments['FEES_AMOUNT'].sum() +
                         filing_payments['REIMBURSEMENT_AMOUNT'].sum() +
                         filing_payments['ADVANCE_AMOUNT'].sum())

                spending_trends.append({'period': quarter, 'amount': amount})

        # Aggregate by quarter
        if spending_trends:
            trends_df = pd.DataFrame(spending_trends)
            trends_df = trends_df.groupby('period')['amount'].sum().reset_index()
            spending_trends = trends_df.to_dict('records')

    # Calculate summary metrics
    total_fees = org_payments['FEES_AMOUNT'].sum() if 'FEES_AMOUNT' in org_payments.columns else 0
    total_reimbursement = org_payments['REIMBURSEMENT_AMOUNT'].sum() if 'REIMBURSEMENT_AMOUNT' in org_payments.columns else 0
    total_advance = org_payments['ADVANCE_AMOUNT'].sum() if 'ADVANCE_AMOUNT' in org_payments.columns else 0
    total_spending = total_fees + total_reimbursement + total_advance

    profile_data = {
        'id': f"org_{filer_id}",
        'filer_id': str(filer_id),  # Keep as string - can be alphanumeric
        'name': org_name,
        'category': org['type'],
        'summary': {
            'totalSpending': float(total_spending) if pd.notna(total_spending) else 0.0,
            'totalFees': float(total_fees) if pd.notna(total_fees) else 0.0,
            'totalReimbursements': float(total_reimbursement) if pd.notna(total_reimbursement) else 0.0,
            'totalAdvances': float(total_advance) if pd.notna(total_advance) else 0.0,
            'activityCount': len(org_lobby),
            'averageSpending': float(total_spending / len(org_lobby)) if len(org_lobby) > 0 else 0.0,
            'firstActivity': activities[0]['from_date'] if len(activities) > 0 and activities[0]['from_date'] else None,
            'lastActivity': activities[-1]['thru_date'] if len(activities) > 0 and activities[-1]['thru_date'] else None,
            'registrationCount': len(org_registrations),
            'lobbyistCount': len(lobbyists)
        },
        'activities': activities,
        'lobbyists': lobbyists,
        'spendingTrends': spending_trends,
        'relatedOrganizations': []  # Can be populated later
    }

    # Save profile
    profile_file = profiles_dir / f"{filename}.json"
    with open(profile_file, 'w') as f:
        json.dump(profile_data, f, indent=2)

    profile_size_kb = profile_file.stat().st_size / 1024
    print(f"  ✓ {filename}.json ({profile_size_kb:.1f} KB)")
    print(f"     {len(activities)} activities, {len(lobbyists)} lobbyists, {len(spending_trends)} quarters")

print()
print("=" * 60)
print("EXTRACTION COMPLETE ✅")
print("=" * 60)
print()
print(f"📁 Tier 1 (Summary): {tier1_file}")
print(f"📁 Tier 2 (Profiles): {profiles_dir}/ ({len(selected_orgs)} files)")
print()
print("📊 Dataset Statistics:")
for org in selected_orgs:
    filer_id = org['filer_id']
    org_lobby = all_lobby_data[all_lobby_data['FILER_ID'] == filer_id]
    org_filing_ids = org_lobby['FILING_ID'].unique()
    org_payments = all_payments[all_payments['FILING_ID'].isin(org_filing_ids)]
    total_spending = org_payments['FEES_AMOUNT'].sum() + org_payments['REIMBURSEMENT_AMOUNT'].sum() + org_payments['ADVANCE_AMOUNT'].sum()
    print(f"  {org['name'][:40]:40} ${total_spending:>12,.0f}  {len(org_lobby):>4} activities")

print()
total_size = sum((profiles_dir / f).stat().st_size for f in os.listdir(profiles_dir) if f.endswith('.json'))
total_size += tier1_file.stat().st_size
print(f"📦 Total Data Size: {total_size/1024:.1f} KB")
print(f"📦 Tier 1 Size: {tier1_file.stat().st_size/1024:.1f} KB")
print(f"📦 Tier 2 Total: {(total_size - tier1_file.stat().st_size)/1024:.1f} KB")
print()
print("✅ Ready to use in React application!")
print()
print("Next steps:")
print("  1. Review generated JSON files in src/data/")
print("  2. Update Search component to use organizations-summary.json")
print("  3. Update OrganizationProfile to lazy-load from profiles/")
print("  4. Test performance with real data")
print("  5. Compare with SAMPLE_DATA_SIZE_STRATEGY.md targets")
