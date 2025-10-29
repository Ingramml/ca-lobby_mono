#!/usr/bin/env python3
"""
Extract Alameda County Lobbying Data from BigQuery Views
Uses the new view-based CSV exports from the BigQuery view architecture

Data Sources (Sample data folder):
- v_filers_alameda.csv: Filer registry
- v_disclosures_alameda.csv: Quarterly lobby disclosures
- v_payments_alameda.csv: Payment transactions
- v_expenditures_alameda.csv: Lobbying expenditures
- v_registrations_alameda.csv: Lobbyist registrations
- v_employers_alameda.csv: Employer relationships
- v_campaign_contributions_alameda.csv: Campaign contributions
- v_other_payments_alameda.csv: Other payments
- v_attachments_alameda.csv: Filing attachments
- v_alameda_activity.csv: Combined activity timeline
- v_alameda_filers_direct.csv: Direct Alameda filers

Output:
- src/data/organizations-summary.json: Summary of all organizations
- src/data/profiles/*.json: Individual organization profiles with full data
"""

import pandas as pd
import json
from pathlib import Path
from datetime import datetime
import numpy as np

# Paths
BASE_DIR = Path(__file__).parent.parent
SAMPLE_DATA_DIR = BASE_DIR / "Sample data"
OUTPUT_DIR = BASE_DIR / "src" / "data"
PROFILES_DIR = OUTPUT_DIR / "profiles"

# Create output directories
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
PROFILES_DIR.mkdir(parents=True, exist_ok=True)

def load_csv(filename):
    """Load CSV file with error handling"""
    filepath = SAMPLE_DATA_DIR / filename
    if not filepath.exists():
        print(f"⚠️  File not found: {filename}")
        return pd.DataFrame()

    try:
        df = pd.read_csv(filepath, low_memory=False)
        print(f"✓ Loaded {filename}: {len(df)} rows")
        return df
    except Exception as e:
        print(f"✗ Error loading {filename}: {e}")
        return pd.DataFrame()

def clean_string(value):
    """Clean string values, handling NaN and 'nan' strings"""
    if pd.isna(value) or value == 'nan' or str(value).strip() == '':
        return None
    return str(value).strip()

def safe_float(value):
    """Convert to float safely"""
    try:
        if pd.isna(value):
            return 0.0
        return float(value)
    except:
        return 0.0

def categorize_organization(filer_type, org_name):
    """Categorize organization based on filer type and name"""
    org_name_lower = (org_name or '').lower()

    # County entities
    if 'county' in org_name_lower and 'city' not in org_name_lower:
        if 'waste' in org_name_lower or 'water' in org_name_lower or 'authority' in org_name_lower:
            return 'County Department'
        return 'County Government'

    # City entities
    if ', city of' in org_name_lower or 'city of' in org_name_lower:
        return 'City Government'

    # Health organizations
    if 'health' in org_name_lower or 'medical' in org_name_lower or 'hospital' in org_name_lower:
        return 'Health Organization'

    # Construction/infrastructure
    if 'construction' in org_name_lower or 'corridor' in org_name_lower or 'transit' in org_name_lower:
        return 'Construction Authority'

    # School districts
    if 'school' in org_name_lower or 'unified' in org_name_lower or 'district' in org_name_lower:
        return 'School District'

    # Apartment/housing
    if 'apartment' in org_name_lower or 'housing' in org_name_lower:
        return 'Housing Organization'

    # Default based on filer type
    if 'LOBBYIST' in (filer_type or '').upper():
        return 'Lobbying Firm'

    return 'Other'

def extract_organization_profiles():
    """Extract organization profiles from BigQuery view CSV files"""

    print("=" * 60)
    print("CA LOBBY - BIGQUERY VIEW DATA EXTRACTION")
    print("=" * 60)
    print()

    # Load all data sources
    print("Loading data sources...")
    print("-" * 60)

    filers = load_csv("v_filers_alameda.csv")
    disclosures = load_csv("v_disclosures_alameda.csv")
    payments = load_csv("v_payments_alameda.csv")
    expenditures = load_csv("v_expenditures_alameda.csv")
    registrations = load_csv("v_registrations_alameda.csv")
    employers = load_csv("v_employers_alameda.csv")
    campaign_contributions = load_csv("v_campaign_contributions_alameda.csv")
    other_payments = load_csv("v_other_payments_alameda.csv")
    attachments = load_csv("v_attachments_alameda.csv")
    activity = load_csv("v_alameda_activity.csv")
    filers_direct = load_csv("v_alameda_filers_direct.csv")

    print()
    print("=" * 60)
    print("Processing organization data...")
    print("-" * 60)

    # Filter for Alameda government entities only
    # Focus on: County, City, School Districts, and major government agencies
    government_keywords = [
        'ALAMEDA COUNTY',
        'ALAMEDA, CITY OF',
        'CITY OF ALAMEDA',
        'ALAMEDA UNIFIED',
        'ALAMEDA ALLIANCE',
        'ALAMEDA CORRIDOR',
        'ALAMEDA WASTE',
        'ALAMEDA WATER',
        'ALAMEDA HEALTH'
    ]

    def is_government_entity(name):
        """Check if name matches government entity patterns"""
        if pd.isna(name) or name == 'nan':
            return False
        name_lower = str(name).lower()
        return any(keyword.lower() in name_lower for keyword in government_keywords)

    if not filers_direct.empty:
        alameda_orgs = filers_direct[
            filers_direct['last_name'].apply(is_government_entity) |
            filers_direct['full_name'].apply(is_government_entity)
        ]
    else:
        alameda_orgs = filers[
            filers['last_name'].apply(is_government_entity) |
            filers['full_name'].apply(is_government_entity)
        ]

    print(f"Found {len(alameda_orgs)} Alameda government organizations")

    organizations = []

    for idx, org in alameda_orgs.iterrows():
        filer_id = str(org['filer_id'])

        # Get organization name - handle 'nan' strings
        org_name = clean_string(org.get('full_name')) or clean_string(org.get('last_name'))
        if not org_name:
            continue

        # Skip if name contains 'nan' or is invalid
        if 'nan' in org_name.lower() and len(org_name) < 20:
            continue

        print(f"\nProcessing: {org_name}")

        # Get disclosures for this org
        org_disclosures = disclosures[disclosures['filer_id'] == int(filer_id)]

        # Get payments (as employer) - escape regex special characters
        org_payments = payments[
            payments['employer_full_name'].str.contains(org_name, case=False, na=False, regex=False)
        ] if not payments.empty and 'employer_full_name' in payments.columns else pd.DataFrame()

        # Get expenditures - expenditures CSV doesn't have filer_id, need to join with disclosures
        org_expenditures = pd.DataFrame()
        if not expenditures.empty and not org_disclosures.empty:
            # Get filing_ids from disclosures
            filing_ids = org_disclosures['filing_id'].unique()
            org_expenditures = expenditures[expenditures['filing_id'].isin(filing_ids)]

        # Calculate metrics
        total_disclosures = len(org_disclosures)
        total_payments = len(org_payments)
        total_expenditures = len(org_expenditures)

        # Calculate spending
        payment_total = org_payments['period_total'].sum() if not org_payments.empty else 0
        expenditure_total = org_expenditures['amount'].sum() if not org_expenditures.empty else 0
        total_spending = safe_float(payment_total) + safe_float(expenditure_total)

        # Get date range
        dates = []
        if not org_disclosures.empty:
            dates.extend(pd.to_datetime(org_disclosures['period_start_date'], errors='coerce').dropna().tolist())
            dates.extend(pd.to_datetime(org_disclosures['period_end_date'], errors='coerce').dropna().tolist())

        first_activity = min(dates).strftime('%Y-%m-%d') if dates else None
        last_activity = max(dates).strftime('%Y-%m-%d') if dates else None

        # Categorize organization
        category = categorize_organization(org.get('filer_type'), org_name)

        # Calculate average spending
        activity_count = total_disclosures + total_payments + total_expenditures
        avg_spending = total_spending / activity_count if activity_count > 0 else 0

        # Add to organizations list
        organizations.append({
            'id': f'org_{filer_id}',
            'filer_id': filer_id,
            'name': org_name,
            'category': category,
            'activityCount': activity_count,
            'totalSpending': round(total_spending, 2),
            'averageSpending': round(avg_spending, 2),
            'firstActivity': first_activity,
            'lastActivity': last_activity,
            'disclosureCount': total_disclosures,
            'paymentCount': total_payments,
            'expenditureCount': total_expenditures
        })

        print(f"  - Activities: {activity_count}")
        print(f"  - Total Spending: ${total_spending:,.2f}")
        print(f"  - Category: {category}")

    # Sort by activity count
    organizations = sorted(organizations, key=lambda x: x['activityCount'], reverse=True)

    # Create organizations summary
    summary = {
        'metadata': {
            'totalOrganizations': len(organizations),
            'lastUpdated': datetime.now().strftime('%Y-%m-%d'),
            'dataVersion': '2.0',
            'dataSource': 'BigQuery Views',
            'viewArchitecture': 'Layer 1-4 Views'
        },
        'organizations': organizations
    }

    # Save summary
    summary_path = OUTPUT_DIR / 'organizations-summary.json'
    with open(summary_path, 'w') as f:
        json.dump(summary, f, indent=2)

    print()
    print("=" * 60)
    print(f"✓ Created organizations summary: {len(organizations)} organizations")
    print(f"  Saved to: {summary_path}")
    print("=" * 60)

    return organizations, {
        'filers': filers,
        'disclosures': disclosures,
        'payments': payments,
        'expenditures': expenditures,
        'registrations': registrations,
        'employers': employers,
        'campaign_contributions': campaign_contributions,
        'other_payments': other_payments,
        'attachments': attachments
    }

def create_individual_profiles(organizations, data_sources):
    """Create individual JSON profiles for each organization"""

    print()
    print("=" * 60)
    print("Creating individual organization profiles...")
    print("-" * 60)

    for org in organizations[:10]:  # Top 10 organizations by activity
        filer_id = org['filer_id']
        org_name = org['name']

        print(f"\nCreating profile: {org_name}")

        # Get all data for this organization
        org_disclosures = data_sources['disclosures'][
            data_sources['disclosures']['filer_id'] == int(filer_id)
        ]

        org_payments = data_sources['payments'][
            data_sources['payments']['employer_full_name'].str.contains(org_name, case=False, na=False)
        ] if not data_sources['payments'].empty else pd.DataFrame()

        # Build activities list
        activities = []

        # Add disclosure activities
        for _, disc in org_disclosures.iterrows():
            activities.append({
                'id': f'disc_{disc["filing_id"]}',
                'filing_id': int(disc['filing_id']),
                'amend_id': int(disc.get('amendment_id', 0)),
                'from_date': clean_string(disc.get('period_start_date')),
                'thru_date': clean_string(disc.get('period_end_date')),
                'report_date': clean_string(disc.get('report_date')),
                'amount': 0.0,
                'organization_type': clean_string(disc.get('entity_code')),
                'form_type': clean_string(disc.get('form_type')),
                'firm_name': org_name
            })

        # Add payment activities
        for _, pay in org_payments.iterrows():
            activities.append({
                'id': f'pay_{pay["filing_id"]}_{pay.get("line_item", 0)}',
                'filing_id': int(pay['filing_id']),
                'amend_id': int(pay.get('amendment_id', 0)),
                'amount': safe_float(pay.get('period_total', 0)),
                'fees_amount': safe_float(pay.get('fees_amount', 0)),
                'reimbursement_amount': safe_float(pay.get('reimbursement_amount', 0)),
                'form_type': clean_string(pay.get('form_type')),
                'payment_tier': clean_string(pay.get('payment_tier')),
                'firm_name': org_name
            })

        # Create profile
        profile = {
            'id': org['id'],
            'filer_id': filer_id,
            'name': org_name,
            'category': org['category'],
            'summary': {
                'activityCount': len(activities),
                'totalSpending': org['totalSpending'],
                'averageSpending': org['averageSpending'],
                'firstActivity': org['firstActivity'],
                'lastActivity': org['lastActivity']
            },
            'activities': activities[:100],  # Limit to 100 most recent
            'lobbyists': [],  # Will be populated from other data
            'spendingTrends': [],  # Will be calculated
            'relatedOrganizations': []
        }

        # Save profile
        filename = org_name.lower().replace(' ', '-').replace(',', '').replace('.', '')[:50] + '.json'
        profile_path = PROFILES_DIR / filename

        with open(profile_path, 'w') as f:
            json.dump(profile, f, indent=2)

        print(f"  ✓ Saved profile: {filename} ({len(activities)} activities)")

    print()
    print("=" * 60)
    print(f"✓ Created {min(10, len(organizations))} organization profiles")
    print("=" * 60)

if __name__ == '__main__':
    try:
        organizations, data_sources = extract_organization_profiles()
        create_individual_profiles(organizations, data_sources)

        print()
        print("=" * 60)
        print("✓ DATA EXTRACTION COMPLETE")
        print("=" * 60)
        print()
        print("Next steps:")
        print("1. Review src/data/organizations-summary.json")
        print("2. Check src/data/profiles/ for individual organization JSONs")
        print("3. Test the frontend with new data")
        print()

    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        import traceback
        traceback.print_exc()
