#!/usr/bin/env python3
"""
Query Sample Data for Website Comparison
Validates data shown on website matches the BigQuery view CSV sources
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

def print_header(title):
    """Print formatted header"""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80)

def print_subheader(title):
    """Print formatted subheader"""
    print("\n" + "-" * 80)
    print(f"  {title}")
    print("-" * 80)

def load_csv_safe(filename):
    """Load CSV with error handling"""
    filepath = SAMPLE_DATA_DIR / filename
    if not filepath.exists():
        return pd.DataFrame()
    try:
        return pd.read_csv(filepath, low_memory=False)
    except Exception as e:
        print(f"  ✗ Error loading {filename}: {e}")
        return pd.DataFrame()

print_header("CA LOBBY - SAMPLE DATA QUERY TOOL")
print("\nPurpose: Validate website data against BigQuery view CSV sources")
print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

# Load all CSV sources
print_subheader("Loading BigQuery View CSV Files")

filers = load_csv_safe("v_filers_alameda.csv")
disclosures = load_csv_safe("v_disclosures_alameda.csv")
payments = load_csv_safe("v_payments_alameda.csv")
expenditures = load_csv_safe("v_expenditures_alameda.csv")
registrations = load_csv_safe("v_registrations_alameda.csv")

print(f"✓ v_filers_alameda.csv: {len(filers):,} rows")
print(f"✓ v_disclosures_alameda.csv: {len(disclosures):,} rows")
print(f"✓ v_payments_alameda.csv: {len(payments):,} rows")
print(f"✓ v_expenditures_alameda.csv: {len(expenditures):,} rows")
print(f"✓ v_registrations_alameda.csv: {len(registrations):,} rows")

# Load organizations summary
print_subheader("Loading Website Data")

summary_path = OUTPUT_DIR / 'organizations-summary.json'
with open(summary_path, 'r') as f:
    summary = json.load(f)

print(f"✓ organizations-summary.json: {summary['metadata']['totalOrganizations']} organizations")
print(f"  Data Version: {summary['metadata']['dataVersion']}")
print(f"  Data Source: {summary['metadata']['dataSource']}")
print(f"  Last Updated: {summary['metadata']['lastUpdated']}")

# Organization comparison
print_header("ORGANIZATION DATA VALIDATION")

for org in summary['organizations']:
    print_subheader(org['name'])

    filer_id = int(org['filer_id'])

    # Get filer info
    filer = filers[filers['filer_id'] == filer_id]
    if len(filer) == 0:
        print(f"  ⚠️  WARNING: Filer ID {filer_id} not found in v_filers_alameda.csv")
        continue

    filer_info = filer.iloc[0]

    print(f"  Filer ID: {filer_id}")
    print(f"  Status: {filer_info.get('status', 'N/A')}")
    print(f"  Filer Type: {filer_info.get('filer_type', 'N/A')}")

    # Get disclosures
    org_disclosures = disclosures[disclosures['filer_id'] == filer_id]

    # Get payments (as employer)
    org_payments = payments[
        payments['employer_full_name'].fillna('').str.upper().str.contains(org['name'], regex=False)
    ]

    # Get expenditures (via filing_ids from disclosures)
    org_expenditures = pd.DataFrame()
    if not org_disclosures.empty:
        filing_ids = org_disclosures['filing_id'].unique()
        org_expenditures = expenditures[expenditures['filing_id'].isin(filing_ids)]

    # Get registrations
    org_registrations = registrations[registrations['filer_id'] == filer_id]

    # Calculate totals
    total_disclosures = len(org_disclosures)
    total_payments = len(org_payments)
    total_expenditures = len(org_expenditures)
    total_registrations = len(org_registrations)

    payment_total = org_payments['period_total'].fillna(0).sum()

    # Expenditures may have 'amount' column or be empty
    if not org_expenditures.empty and 'amount' in org_expenditures.columns:
        expenditure_total = org_expenditures['amount'].fillna(0).sum()
    else:
        expenditure_total = 0.0

    # Get date ranges
    dates = []
    if not org_disclosures.empty:
        dates.extend(pd.to_datetime(org_disclosures['period_start_date'], errors='coerce').dropna().tolist())
        dates.extend(pd.to_datetime(org_disclosures['period_end_date'], errors='coerce').dropna().tolist())

    first_activity = min(dates).strftime('%Y-%m-%d') if dates else None
    last_activity = max(dates).strftime('%Y-%m-%d') if dates else None

    # Compare with website data
    print(f"\n  ACTIVITY COUNTS:")
    print(f"    Disclosures: {total_disclosures}")
    print(f"    Payments: {total_payments}")
    print(f"    Expenditures: {total_expenditures}")
    print(f"    Registrations: {total_registrations}")
    print(f"    Total Activities: {total_disclosures + total_payments}")
    print(f"    Website Shows: {org['activityCount']}")

    # Check match
    calculated_total = total_disclosures + total_payments
    if calculated_total != org['activityCount']:
        print(f"    ⚠️  MISMATCH: Calculated={calculated_total}, Website={org['activityCount']}")
    else:
        print(f"    ✓ MATCH")

    print(f"\n  SPENDING:")
    print(f"    Payment Total: ${payment_total:,.2f}")
    print(f"    Expenditure Total: ${expenditure_total:,.2f}")
    print(f"    Combined Total: ${payment_total + expenditure_total:,.2f}")
    print(f"    Website Shows: ${org['totalSpending']:,.2f}")

    # Check match
    calculated_spending = payment_total + expenditure_total
    if abs(calculated_spending - org['totalSpending']) > 0.01:
        print(f"    ⚠️  MISMATCH: Calculated=${calculated_spending:,.2f}, Website=${org['totalSpending']:,.2f}")
    else:
        print(f"    ✓ MATCH")

    print(f"\n  DATE RANGE:")
    print(f"    First Activity: {first_activity or 'N/A'}")
    print(f"    Last Activity: {last_activity or 'N/A'}")
    print(f"    Website Shows: {org['firstActivity']} to {org['lastActivity']}")

    # Show sample payments
    if not org_payments.empty:
        print(f"\n  SAMPLE PAYMENTS (Top 5 by Amount):")
        top_payments = org_payments.nlargest(5, 'period_total')
        for idx, pay in top_payments.iterrows():
            print(f"    - Filing {pay['filing_id']}: ${pay['period_total']:,.2f} ({pay.get('form_type', 'N/A')})")

    # Show sample disclosures
    if not org_disclosures.empty:
        print(f"\n  SAMPLE DISCLOSURES (Most Recent 5):")
        recent_disc = org_disclosures.nlargest(5, 'filing_id')
        for idx, disc in recent_disc.iterrows():
            print(f"    - Filing {disc['filing_id']}: {disc.get('form_type', 'N/A')} ({disc.get('period_start_date', 'N/A')} to {disc.get('period_end_date', 'N/A')})")

# Summary statistics
print_header("SUMMARY STATISTICS")

print("\nDATA SOURCE TOTALS:")
print(f"  Total Filers: {len(filers):,}")
print(f"  Total Disclosures: {len(disclosures):,}")
print(f"  Total Payments: {len(payments):,}")
print(f"  Total Expenditures: {len(expenditures):,}")
print(f"  Total Registrations: {len(registrations):,}")

print("\nWEBSITE TOTALS:")
total_activities = sum(org['activityCount'] for org in summary['organizations'])
total_spending = sum(org['totalSpending'] for org in summary['organizations'])
print(f"  Organizations: {len(summary['organizations'])}")
print(f"  Total Activities: {total_activities:,}")
print(f"  Total Spending: ${total_spending:,.2f}")
print(f"  Average per Org: ${total_spending / len(summary['organizations']):,.2f}")

# Payment tier distribution
print("\nPAYMENT TIER DISTRIBUTION:")
if 'payment_tier' in payments.columns:
    tier_counts = payments['payment_tier'].value_counts()
    for tier, count in tier_counts.items():
        print(f"  {tier}: {count:,} payments")

# Form type distribution
print("\nFORM TYPE DISTRIBUTION (Disclosures):")
if 'form_type' in disclosures.columns:
    form_counts = disclosures['form_type'].value_counts().head(10)
    for form, count in form_counts.items():
        print(f"  {form}: {count:,} filings")

# Yearly trends
print("\nYEARLY TRENDS (from disclosure periods):")
if not disclosures.empty and 'period_start_date' in disclosures.columns:
    disclosures['year'] = pd.to_datetime(disclosures['period_start_date'], errors='coerce').dt.year
    yearly = disclosures['year'].value_counts().sort_index()
    for year, count in yearly.tail(5).items():
        print(f"  {int(year)}: {count:,} disclosures")

print("\n" + "=" * 80)
print("  QUERY COMPLETE")
print("=" * 80 + "\n")
