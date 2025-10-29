#!/usr/bin/env python3
"""
Generate real activity data from payment transactions
Processes v_payments_alameda.csv and v_disclosures_alameda.csv
to create complete activity records for organization profiles
"""

import pandas as pd
import json
from pathlib import Path
from datetime import datetime

# Paths
BASE_DIR = Path(__file__).parent.parent
SAMPLE_DATA_DIR = BASE_DIR / "Sample data"
OUTPUT_DIR = BASE_DIR / "src" / "data"

# Core organizations
CORE_ORGANIZATIONS = {
    'ALAMEDA COUNTY WATER DISTRICT': {
        'category': 'County Department',
        'filer_id': 1144594
    },
    'ALAMEDA COUNTY WASTE MANAGEMENT AUTHORITY': {
        'category': 'County Department',
        'filer_id': 1250137
    },
    'ALAMEDA ALLIANCE FOR HEALTH': {
        'category': 'Health Organization',
        'filer_id': 1276637
    },
    'ALAMEDA COUNTY FAIR': {
        'category': 'County Department',
        'filer_id': 1145110
    },
    'ALAMEDA CORRIDOR-EAST CONSTRUCTION AUTHORITY': {
        'category': 'Construction Authority',
        'filer_id': 1146730
    },
    'ALAMEDA CORRIDOR TRANSPORTATION AUTHORITY': {
        'category': 'Construction Authority',
        'filer_id': 1146119
    },
    'ALAMEDA, CITY OF': {
        'category': 'City Government',
        'filer_id': 1145570
    },
    'ALAMEDA COUNTY CONGESTION MANAGEMENT AGENCY': {
        'category': 'County Department',
        'filer_id': 1144020
    },
    'ALAMEDA COUNTY TRANSPORTATION IMPROVEMENT AUTHORITY': {
        'category': 'County Department',
        'filer_id': 1143409
    },
    'ALAMEDA UNIFIED SCHOOL DISTRICT': {
        'category': 'School District',
        'filer_id': 1356003
    },
    "ALAMEDA COUNTY EMPLOYEES' RETIREMENT ASSOCIATION": {
        'category': 'County Department',
        'filer_id': 1324131
    }
}

print("=" * 80)
print("GENERATING REAL ACTIVITY DATA FROM PAYMENT TRANSACTIONS")
print("=" * 80)
print()

# Load CSV files
print("Loading CSV files...")
payments = pd.read_csv(SAMPLE_DATA_DIR / "v_payments_alameda.csv", low_memory=False)
disclosures = pd.read_csv(SAMPLE_DATA_DIR / "v_disclosures_alameda.csv", low_memory=False)

print(f"✓ Loaded {len(payments):,} payment transactions")
print(f"✓ Loaded {len(disclosures):,} disclosure filings")
print()

# Since disclosures are empty for these orgs (filed by lobbying firms),
# we'll create activity records directly from payments with estimated dates
print("Processing activities for each organization...")
print()

all_activities = {}

for org_name, org_info in CORE_ORGANIZATIONS.items():
    print(f"Processing: {org_name}")

    # Find all payments for this organization
    org_payments = payments[
        payments['employer_full_name'].fillna('').str.upper().str.contains(org_name, regex=False)
    ].copy()

    if len(org_payments) == 0:
        print(f"  ⚠️  No payments found")
        all_activities[org_name] = []
        continue

    print(f"  Found {len(org_payments):,} payment line items")

    # Group by filing_id to create activities (one activity = one quarterly filing)
    activities = []

    for filing_id, filing_group in org_payments.groupby('filing_id'):
        # Get the first record for filing metadata
        first_payment = filing_group.iloc[0]

        # Sum all payments in this filing
        total_amount = filing_group['period_total'].sum()
        payment_count = len(filing_group)

        # Extract firm name from the first payment if available
        # Note: We don't have the disclosure record, so we'll estimate dates
        # based on form type and create synthetic quarterly dates

        activity = {
            'id': f'activity_{filing_id}',
            'filing_id': int(filing_id),
            'organization': org_name,
            'category': org_info['category'],
            'amount': round(float(total_amount), 2),
            'payment_count': int(payment_count),
            'form_type': first_payment.get('form_type', 'F625'),
            'payment_tier': first_payment.get('payment_tier', 'Unknown'),
            # We don't have actual dates from disclosures, so we'll mark as null
            # and handle this in the UI
            'date': None,
            'from_date': None,
            'thru_date': None,
            'filing_date': None,
            # Estimate description
            'description': f"{payment_count} payment{'s' if payment_count > 1 else ''} totaling ${total_amount:,.2f}",
            'lobbyist': None,  # Not available without disclosure
            'firm_name': None  # Not available without disclosure
        }

        activities.append(activity)

    # Sort by filing_id descending (most recent first, approximately)
    activities.sort(key=lambda x: x['filing_id'], reverse=True)

    all_activities[org_name] = activities

    print(f"  Created {len(activities)} activities (grouped by filing)")
    print(f"  Total spending: ${sum(a['amount'] for a in activities):,.2f}")
    print()

# Save activities for each organization
print("=" * 80)
print("SAVING ACTIVITY FILES")
print("=" * 80)
print()

(OUTPUT_DIR / "activities").mkdir(exist_ok=True)

for org_name, activities in all_activities.items():
    # Sanitize filename
    filename = org_name.lower().replace(' ', '-').replace(',', '').replace("'", '')
    filepath = OUTPUT_DIR / "activities" / f"{filename}-activities.json"

    activity_data = {
        'organization': org_name,
        'generated_date': datetime.now().strftime('%Y-%m-%d'),
        'data_source': 'v_payments_alameda.csv',
        'total_activities': len(activities),
        'total_spending': sum(a['amount'] for a in activities),
        'note': 'Activities grouped by filing_id. Dates are NOT available because disclosures are filed by lobbying firms, not by this organization.',
        'activities': activities
    }

    with open(filepath, 'w') as f:
        json.dump(activity_data, f, indent=2)

    print(f"✓ Saved {len(activities)} activities → {filepath.name}")

print()
print("=" * 80)
print("SUMMARY")
print("=" * 80)
print(f"Total organizations processed: {len(all_activities)}")
print(f"Total activities created: {sum(len(acts) for acts in all_activities.values())}")
print(f"Total spending tracked: ${sum(sum(a['amount'] for a in acts) for acts in all_activities.values()):,.2f}")
print()
print("⚠️  IMPORTANT:")
print("These activities DO NOT have dates because the disclosure records are")
print("filed by lobbying firms (not by these organizations) and are not included")
print("in the v_disclosures_alameda.csv filtered view.")
print()
print("To get dates, you must:")
print("1. Run the BigQuery SQL queries in scripts/bigquery_date_range_queries.sql")
print("2. Join payments to the FULL CVR2_LOBBY_DISCLOSURE_CD table")
print("3. Extract period_start_date and period_end_date for each filing_id")
print()
print("For now, the UI will display activities without dates.")
