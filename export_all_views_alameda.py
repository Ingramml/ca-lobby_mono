#!/usr/bin/env python3
"""
Export ALL 11 views filtered to Alameda records only
For local deployment and website development
"""

from google.cloud import bigquery
import pandas as pd
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = os.getenv('CREDENTIALS_LOCATION')

PROJECT_ID = 'ca-lobby'
DATASET_ID = 'ca_lobby'
OUTPUT_DIR = Path('alameda_data_exports')
OUTPUT_DIR.mkdir(exist_ok=True)

client = bigquery.Client(project=PROJECT_ID)

print("="*80)
print("EXPORT ALL 11 VIEWS - ALAMEDA FILTERED")
print("="*80)
print("Exporting complete view data filtered to Alameda for local deployment\n")

# Define all 11 views with their Alameda filter conditions
views_to_export = [
    {
        'view': 'v_filers',
        'filter': 'WHERE is_alameda = TRUE',
        'output': 'v_filers_alameda.csv',
        'description': 'All filers with Alameda connections'
    },
    {
        'view': 'v_disclosures',
        'filter': 'WHERE is_alameda = TRUE',
        'output': 'v_disclosures_alameda.csv',
        'description': 'Lobby disclosure filings from Alameda entities'
    },
    {
        'view': 'v_registrations',
        'filter': 'WHERE is_alameda = TRUE',
        'output': 'v_registrations_alameda.csv',
        'description': 'Lobbyist registrations for Alameda entities'
    },
    {
        'view': 'v_payments',
        'filter': 'WHERE is_alameda = TRUE',
        'output': 'v_payments_alameda.csv',
        'description': 'Lobbying payments involving Alameda'
    },
    {
        'view': 'v_expenditures',
        'filter': 'WHERE is_alameda = TRUE',
        'output': 'v_expenditures_alameda.csv',
        'description': 'Lobbying expenditures involving Alameda'
    },
    {
        'view': 'v_employers',
        'filter': '',  # No is_alameda flag in this view
        'output': 'v_employers_alameda.csv',
        'description': 'All employer relationships (no Alameda filter available)'
    },
    {
        'view': 'v_campaign_contributions',
        'filter': '',  # No is_alameda flag in this view
        'output': 'v_campaign_contributions_alameda.csv',
        'description': 'Campaign contributions (filter via JOIN with other tables)'
    },
    {
        'view': 'v_other_payments',
        'filter': '',  # No is_alameda flag in this view
        'output': 'v_other_payments_alameda.csv',
        'description': 'Other payments (filter via JOIN with other tables)'
    },
    {
        'view': 'v_attachments',
        'filter': '',  # No is_alameda flag in this view
        'output': 'v_attachments_alameda.csv',
        'description': 'Filing attachments (filter via JOIN with other tables)'
    },
    {
        'view': 'v_alameda_filers',
        'filter': '',  # Already filtered
        'output': 'v_alameda_filers_direct.csv',
        'description': 'Pre-filtered Alameda filers view'
    },
    {
        'view': 'v_alameda_activity',
        'filter': '',  # Already filtered
        'output': 'v_alameda_activity.csv',
        'description': 'Combined Alameda activity from all sources'
    }
]

total_rows = 0
exports = []
failed = []

for i, view_info in enumerate(views_to_export, 1):
    view_name = view_info['view']
    filter_clause = view_info['filter']
    output_name = view_info['output']
    description = view_info['description']

    print(f"[{i}/11] {view_name}")
    print(f"    {description}")

    try:
        # Build query
        query = f"""
        SELECT *
        FROM `{PROJECT_ID}.{DATASET_ID}.{view_name}`
        {filter_clause}
        """

        print(f"    Querying...")
        df = client.query(query).to_dataframe()
        rows = len(df)

        # Save to CSV
        output_file = OUTPUT_DIR / output_name
        print(f"    Writing...")
        df.to_csv(output_file, index=False)

        size_mb = os.path.getsize(output_file) / 1024 / 1024
        print(f"    ✓ {rows:,} rows → {size_mb:.2f} MB")

        total_rows += rows
        exports.append({
            'view': view_name,
            'file': output_name,
            'rows': rows,
            'size_mb': size_mb
        })
        print()

    except Exception as e:
        error_msg = str(e)[:200]
        print(f"    ✗ FAILED: {error_msg}")
        failed.append({'view': view_name, 'error': error_msg})
        print()

print("="*80)
print("EXPORT COMPLETE")
print("="*80)
print(f"\n✓ Successfully exported: {len(exports)}/11 views")
print(f"✗ Failed: {len(failed)}/11 views")
print(f"\nTotal rows exported: {total_rows:,}")
print(f"Output directory: {OUTPUT_DIR.absolute()}\n")

if exports:
    print("Files created:")
    for exp in exports:
        print(f"  {exp['file']:<35} {exp['rows']:>8,} rows  ({exp['size_mb']:>8.2f} MB)")

if failed:
    print("\nFailed exports:")
    for fail in failed:
        print(f"  {fail['view']}: {fail['error'][:100]}")

print("\n" + "="*80)
print("READY FOR LOCAL DEPLOYMENT")
print("="*80)
print("\nThese CSV files contain all Alameda-filtered data from the 11 views")
print("Use these to populate your local database for website development")
