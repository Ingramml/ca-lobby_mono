#!/usr/bin/env python3
"""
Test BigQuery date range queries locally using CSV data
This validates the SQL logic before running in BigQuery
"""

import pandas as pd
from pathlib import Path
from datetime import datetime

# Paths
BASE_DIR = Path(__file__).parent.parent
SAMPLE_DATA_DIR = BASE_DIR / "Sample data"

# Core organizations to query
CORE_ORGANIZATIONS = [
    'ALAMEDA COUNTY WATER DISTRICT',
    'ALAMEDA COUNTY WASTE MANAGEMENT AUTHORITY',
    'ALAMEDA ALLIANCE FOR HEALTH',
    'ALAMEDA COUNTY FAIR',
    'ALAMEDA CORRIDOR-EAST CONSTRUCTION AUTHORITY',
    'ALAMEDA CORRIDOR TRANSPORTATION AUTHORITY',
    'ALAMEDA, CITY OF',
    'ALAMEDA COUNTY CONGESTION MANAGEMENT AGENCY',
    'ALAMEDA COUNTY TRANSPORTATION IMPROVEMENT AUTHORITY',
    'ALAMEDA UNIFIED SCHOOL DISTRICT',
    "ALAMEDA COUNTY EMPLOYEES' RETIREMENT ASSOCIATION"
]

print("=" * 80)
print("TESTING BIGQUERY DATE RANGE QUERIES ON LOCAL CSV DATA")
print("=" * 80)
print()

# Load data
print("Loading CSV files...")
filers = pd.read_csv(SAMPLE_DATA_DIR / "v_filers_alameda.csv", low_memory=False)
disclosures = pd.read_csv(SAMPLE_DATA_DIR / "v_disclosures_alameda.csv", low_memory=False)
payments = pd.read_csv(SAMPLE_DATA_DIR / "v_payments_alameda.csv", low_memory=False)

print(f"✓ Loaded {len(filers)} filers")
print(f"✓ Loaded {len(disclosures)} disclosures")
print(f"✓ Loaded {len(payments)} payments")
print()

# QUERY 1: Date Ranges for Alameda Organizations
print("=" * 80)
print("QUERY 1: Date Ranges for Alameda Organizations")
print("=" * 80)
print()

results = []

for org_name in CORE_ORGANIZATIONS:
    # Find filer
    org_filers = filers[
        (filers['last_name'].fillna('').str.upper() == org_name)
    ]

    if len(org_filers) == 0:
        print(f"⚠️  {org_name}: NOT FOUND in filers")
        continue

    filer_id = org_filers.iloc[0]['filer_id']

    # These organizations are CLIENTS (employers), not direct filers
    # They appear in the payments table, not disclosures table
    # We need to find payments WHERE this org is the employer

    org_payments = payments[
        payments['employer_full_name'].fillna('').str.contains(org_name, case=False, regex=False)
    ]

    if len(org_payments) == 0:
        print(f"⚠️  {org_name}: NO PAYMENTS FOUND")
        continue

    # Get the filing_ids for these payments
    payment_filing_ids = org_payments['filing_id'].unique()

    # Join with disclosures to get period dates
    # The disclosures are filed BY THE LOBBYING FIRMS, not by the organization
    payment_disclosures = disclosures[disclosures['filing_id'].isin(payment_filing_ids)]

    # Extract dates from the disclosure periods
    payment_dates = pd.to_datetime(payment_disclosures['period_start_date'], errors='coerce').dropna()
    payment_end_dates = pd.to_datetime(payment_disclosures['period_end_date'], errors='coerce').dropna()

    first_activity = payment_dates.min() if len(payment_dates) > 0 else None
    last_activity = payment_end_dates.max() if len(payment_end_dates) > 0 else None

    # Calculate span
    activity_span_days = None
    if first_activity and last_activity:
        if first_activity is not pd.NaT and last_activity is not pd.NaT:
            activity_span_days = (last_activity - first_activity).days

    disclosure_count = len(payment_disclosures)
    payment_count = len(org_payments)

    result = {
        'filer_id': filer_id,
        'organization_name': org_name,
        'first_activity': first_activity.strftime('%Y-%m-%d') if first_activity is not None and first_activity is not pd.NaT else None,
        'last_activity': last_activity.strftime('%Y-%m-%d') if last_activity is not None and last_activity is not pd.NaT else None,
        'activity_span_days': activity_span_days,
        'disclosure_count': disclosure_count,
        'payment_count': payment_count
    }

    results.append(result)

    print(f"{org_name}")
    print(f"  Filer ID: {filer_id}")
    print(f"  First Activity: {result['first_activity']}")
    print(f"  Last Activity: {result['last_activity']}")
    print(f"  Span: {activity_span_days} days" if activity_span_days else "  Span: N/A")
    print(f"  Filings (via payments): {disclosure_count}")
    print(f"  Payment Line Items: {payment_count}")
    print()

# Summary
print("=" * 80)
print("SUMMARY")
print("=" * 80)
print(f"Total organizations: {len(results)}")
print(f"Organizations with date ranges: {sum(1 for r in results if r['first_activity'])}")
print(f"Organizations missing dates: {sum(1 for r in results if not r['first_activity'])}")
print()

# Show date range distribution
print("Date Range Distribution:")
for result in sorted(results, key=lambda x: x['activity_span_days'] or 0, reverse=True):
    if result['first_activity']:
        print(f"  {result['organization_name'][:40]:<40} | {result['first_activity']} to {result['last_activity']} ({result['activity_span_days']} days)")

print()
print("=" * 80)
print("NEXT STEP: Run the SQL queries in BigQuery to get production data")
print("=" * 80)
print()
print("To run in BigQuery:")
print("1. Go to https://console.cloud.google.com/bigquery")
print("2. Select project: ca-lobby")
print("3. Open scripts/bigquery_date_range_queries.sql")
print("4. Run QUERY 1 (lines 14-80)")
print("5. Export results as CSV")
print("6. Use CSV to update organizations-summary.json")
