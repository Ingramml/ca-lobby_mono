#!/usr/bin/env python3
"""
Add human-readable details to transactions:
- Who received the payment (lobbying firm name)
- When the payment was made (period dates)
- What it was for (description)

Joins payment data with disclosure data to get complete information
"""

import pandas as pd
import json
from pathlib import Path
from datetime import datetime

# Paths
BASE_DIR = Path(__file__).parent.parent
SAMPLE_DATA_DIR = BASE_DIR / "Sample data"
OUTPUT_DIR = BASE_DIR / "src" / "data"

print("=" * 80)
print("ADDING HUMAN-READABLE DETAILS TO TRANSACTIONS")
print("=" * 80)
print()

# Load CSV files
print("Loading data files...")
payments = pd.read_csv(SAMPLE_DATA_DIR / "v_payments_alameda.csv", low_memory=False)
disclosures = pd.read_csv(SAMPLE_DATA_DIR / "v_disclosures_alameda.csv", low_memory=False)
filers = pd.read_csv(SAMPLE_DATA_DIR / "v_filers_alameda.csv", low_memory=False)

print(f"✓ Loaded {len(payments):,} payment records")
print(f"✓ Loaded {len(disclosures):,} disclosure filings")
print(f"✓ Loaded {len(filers):,} filer records")
print()

# Create a lookup for disclosure information by filing_id
# Keep only the latest amendment for each filing_id
disclosures_latest = disclosures.sort_values('amendment_id', ascending=False).drop_duplicates('filing_id', keep='first')
disclosure_lookup = disclosures_latest.set_index('filing_id').to_dict('index')

# Create a lookup for filer names
filer_lookup = filers.set_index('filer_id')['last_name'].to_dict()

print("Processing Alameda County Water District transactions...")
print()

# Get Water District payments
water_district_payments = payments[
    payments['employer_full_name'].fillna('').str.upper().str.contains('ALAMEDA COUNTY WATER DISTRICT', regex=False)
].copy()

print(f"Found {len(water_district_payments)} payment line items")
print()

# Enhance each payment with disclosure information
enhanced_transactions = []

for idx, payment in water_district_payments.iterrows():
    filing_id = payment['filing_id']

    # Get disclosure information for this filing
    disclosure = disclosure_lookup.get(filing_id, {})

    # Extract human-readable information
    firm_name = disclosure.get('firm_name', 'Unknown Lobbying Firm')
    if pd.isna(firm_name) or firm_name == 'nan':
        # Try to get from filer_id
        filer_id = disclosure.get('filer_id')
        if filer_id and filer_id in filer_lookup:
            firm_name = filer_lookup[filer_id]
        else:
            firm_name = 'Unknown Firm'

    period_start = disclosure.get('period_start_date', None)
    period_end = disclosure.get('period_end_date', None)
    report_date = disclosure.get('report_date', None)
    form_type = disclosure.get('form_type', payment['form_type'])

    # Format dates
    if period_start and not pd.isna(period_start):
        try:
            period_start_formatted = pd.to_datetime(period_start).strftime('%Y-%m-%d')
        except:
            period_start_formatted = str(period_start)
    else:
        period_start_formatted = None

    if period_end and not pd.isna(period_end):
        try:
            period_end_formatted = pd.to_datetime(period_end).strftime('%Y-%m-%d')
        except:
            period_end_formatted = str(period_end)
    else:
        period_end_formatted = None

    if report_date and not pd.isna(report_date):
        try:
            report_date_formatted = pd.to_datetime(report_date).strftime('%Y-%m-%d')
        except:
            report_date_formatted = str(report_date)
    else:
        report_date_formatted = None

    # Create human-readable description
    description_parts = []

    if firm_name and firm_name != 'Unknown Firm':
        description_parts.append(f"Payment to {firm_name}")

    if period_start_formatted and period_end_formatted:
        description_parts.append(f"for services from {period_start_formatted} to {period_end_formatted}")

    # Form type explanation
    form_descriptions = {
        'F625': 'Quarterly Lobbying Report',
        'F625P2': 'Quarterly Payment Schedule',
        'F635': 'Periodic Report',
        'F645': 'Termination Report',
        'F615': 'Registration Form'
    }

    if form_type in form_descriptions:
        description_parts.append(f"({form_descriptions[form_type]})")

    human_description = ' '.join(description_parts) if description_parts else f"Payment line item #{payment['line_item']}"

    # Build enhanced transaction
    transaction = {
        'id': f"payment_{payment['filing_id']}_{payment['line_item']}",
        'filing_id': int(payment['filing_id']),
        'line_item': int(payment['line_item']) if pd.notna(payment['line_item']) else 0,
        'organization': 'ALAMEDA COUNTY WATER DISTRICT',
        'category': 'County Department',

        # Human-readable information
        'firm_name': firm_name,
        'lobbyist': firm_name,  # Using firm name as lobbyist for now
        'description': human_description,

        # Dates
        'date': period_end_formatted,  # Use period end as transaction date
        'from_date': period_start_formatted,
        'thru_date': period_end_formatted,
        'filing_date': report_date_formatted,

        # Payment amounts
        'fees_amount': round(float(payment['fees_amount']), 2) if pd.notna(payment['fees_amount']) else 0.0,
        'reimbursement_amount': round(float(payment['reimbursement_amount']), 2) if pd.notna(payment['reimbursement_amount']) else 0.0,
        'advance_amount': round(float(payment['advance_amount']), 2) if pd.notna(payment['advance_amount']) else 0.0,
        'amount': round(float(payment['period_total']), 2) if pd.notna(payment['period_total']) else 0.0,
        'cumulative_total': round(float(payment['cumulative_total']), 2) if pd.notna(payment['cumulative_total']) else 0.0,

        # Form metadata
        'form_type': str(form_type) if pd.notna(form_type) else 'Unknown',
        'payment_tier': str(payment['payment_tier']) if pd.notna(payment['payment_tier']) else 'Unknown',

        # Employer info
        'employer_last_name': str(payment['employer_last_name']) if pd.notna(payment['employer_last_name']) else None,
        'employer_first_name': str(payment['employer_first_name']) if pd.notna(payment['employer_first_name']) else None
    }

    enhanced_transactions.append(transaction)

# Sort by filing_id descending (most recent first)
enhanced_transactions.sort(key=lambda x: (-x['filing_id'], x['line_item']))

print(f"✓ Enhanced {len(enhanced_transactions)} transactions with human-readable details")
print()

# Calculate statistics
transactions_with_dates = sum(1 for t in enhanced_transactions if t['date'] is not None)
transactions_with_firms = sum(1 for t in enhanced_transactions if t['firm_name'] != 'Unknown Firm')

print("Enhancement Statistics:")
print(f"  Transactions with dates: {transactions_with_dates} ({transactions_with_dates/len(enhanced_transactions)*100:.1f}%)")
print(f"  Transactions with firm names: {transactions_with_firms} ({transactions_with_firms/len(enhanced_transactions)*100:.1f}%)")
print()

# Save enhanced data
output_file = OUTPUT_DIR / "activities" / "alameda-county-water-district-activities.json"

activity_data = {
    'organization': 'ALAMEDA COUNTY WATER DISTRICT',
    'generated_date': datetime.now().strftime('%Y-%m-%d'),
    'data_source': 'v_payments_alameda.csv + v_disclosures_alameda.csv',
    'data_type': 'individual_transactions_enhanced',
    'total_activities': len(enhanced_transactions),
    'total_spending': round(sum(t['amount'] for t in enhanced_transactions), 2),
    'note': 'Enhanced with firm names and dates from disclosure records. Each activity is one payment line item.',
    'activities': enhanced_transactions
}

with open(output_file, 'w') as f:
    json.dump(activity_data, f, indent=2)

print(f"✓ Saved enhanced transactions to: {output_file}")
print()

# Show sample transactions
print("=" * 80)
print("SAMPLE ENHANCED TRANSACTIONS (First 10)")
print("=" * 80)
print()

for i, trans in enumerate(enhanced_transactions[:10], 1):
    print(f"{i}. Filing #{trans['filing_id']}, Line {trans['line_item']}")
    print(f"   Amount: ${trans['amount']:,.2f}")
    print(f"   Paid to: {trans['firm_name']}")
    if trans['from_date'] and trans['thru_date']:
        print(f"   Period: {trans['from_date']} to {trans['thru_date']}")
    if trans['filing_date']:
        print(f"   Filed: {trans['filing_date']}")
    print(f"   Description: {trans['description']}")
    print()

print("=" * 80)
print("COMPLETE! Transactions are now human-readable.")
print("=" * 80)
