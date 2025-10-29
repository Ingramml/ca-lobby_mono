#!/usr/bin/env python3
"""
Generate individual transaction records from payment line items
Each payment line item becomes one activity record (10 per page display)
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
print("GENERATING INDIVIDUAL TRANSACTION RECORDS FROM PAYMENT LINE ITEMS")
print("=" * 80)
print()

# Load CSV files
print("Loading CSV files...")
payments = pd.read_csv(SAMPLE_DATA_DIR / "v_payments_alameda.csv", low_memory=False)
print(f"✓ Loaded {len(payments):,} payment line items")
print()

# Process each organization
print("Processing individual transactions for each organization...")
print()

all_activities = {}

for org_name, org_info in CORE_ORGANIZATIONS.items():
    print(f"Processing: {org_name}")

    # Find all payment line items for this organization
    org_payments = payments[
        payments['employer_full_name'].fillna('').str.upper().str.contains(org_name, regex=False)
    ].copy()

    if len(org_payments) == 0:
        print(f"  ⚠️  No payment line items found")
        all_activities[org_name] = []
        continue

    print(f"  Found {len(org_payments):,} individual payment line items")

    # Create one activity record per payment line item
    activities = []

    for idx, payment in org_payments.iterrows():
        activity = {
            'id': f'payment_{payment["filing_id"]}_{payment["line_item"]}',
            'filing_id': int(payment['filing_id']),
            'line_item': int(payment['line_item']) if pd.notna(payment['line_item']) else 0,
            'organization': org_name,
            'category': org_info['category'],

            # Payment amounts
            'fees_amount': round(float(payment['fees_amount']), 2) if pd.notna(payment['fees_amount']) else 0.0,
            'reimbursement_amount': round(float(payment['reimbursement_amount']), 2) if pd.notna(payment['reimbursement_amount']) else 0.0,
            'advance_amount': round(float(payment['advance_amount']), 2) if pd.notna(payment['advance_amount']) else 0.0,
            'amount': round(float(payment['period_total']), 2) if pd.notna(payment['period_total']) else 0.0,
            'cumulative_total': round(float(payment['cumulative_total']), 2) if pd.notna(payment['cumulative_total']) else 0.0,

            # Form metadata
            'form_type': str(payment['form_type']) if pd.notna(payment['form_type']) else 'Unknown',
            'payment_tier': str(payment['payment_tier']) if pd.notna(payment['payment_tier']) else 'Unknown',

            # Employer info (from payment record)
            'employer_last_name': str(payment['employer_last_name']) if pd.notna(payment['employer_last_name']) else None,
            'employer_first_name': str(payment['employer_first_name']) if pd.notna(payment['employer_first_name']) else None,

            # Dates - will be NULL until we get disclosure data from BigQuery
            'date': None,
            'from_date': None,
            'thru_date': None,
            'filing_date': None,

            # Description
            'description': f"Payment line item #{payment['line_item']} - {payment['form_type']}",

            # Lobbyist/firm - not available in payments table
            'lobbyist': None,
            'firm_name': None
        }

        activities.append(activity)

    # Sort by filing_id descending (most recent filings first, approximately)
    # Then by line_item ascending within each filing
    activities.sort(key=lambda x: (-x['filing_id'], x['line_item']))

    all_activities[org_name] = activities

    print(f"  Created {len(activities)} individual transaction records")
    print(f"  Total spending: ${sum(a['amount'] for a in activities):,.2f}")
    print()

# Save activities for each organization
print("=" * 80)
print("SAVING TRANSACTION FILES")
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
        'data_type': 'individual_transactions',
        'total_activities': len(activities),
        'total_spending': round(sum(a['amount'] for a in activities), 2),
        'note': 'Each activity is one payment line item (individual transaction). Dates will be populated from BigQuery disclosure records.',
        'activities': activities
    }

    with open(filepath, 'w') as f:
        json.dump(activity_data, f, indent=2)

    print(f"✓ Saved {len(activities)} transactions → {filepath.name}")

print()
print("=" * 80)
print("SUMMARY")
print("=" * 80)
print(f"Total organizations processed: {len(all_activities)}")
print(f"Total transactions created: {sum(len(acts) for acts in all_activities.values()):,}")
print(f"Total spending tracked: ${sum(sum(a['amount'] for a in acts) for acts in all_activities.values()):,.2f}")
print()
print("Transaction Details:")
print("- Each activity = 1 payment line item (individual transaction)")
print("- Display: 10 transactions per page in Recent Activities")
print("- Sorting: Most recent filings first (by filing_id)")
print()
print("⚠️  Date fields are NULL - will be populated from BigQuery")
print("⚠️  Firm names are NULL - will be populated from BigQuery")
