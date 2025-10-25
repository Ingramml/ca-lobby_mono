#!/usr/bin/env python3
"""
Create all 11 views and export them to CSV for local deployment
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
OUTPUT_DIR = Path('view_exports')
OUTPUT_DIR.mkdir(exist_ok=True)

client = bigquery.Client(project=PROJECT_ID)

print("="*80)
print("STEP 1: CREATE ALL 11 VIEWS")
print("="*80)

# Read the SQL file and execute it
with open('create_simple_views.sql', 'r') as f:
    sql_content = f.read()

# Split by CREATE statements
view_statements = []
current_statement = []
for line in sql_content.split('\n'):
    if line.strip().startswith('CREATE OR REPLACE VIEW'):
        if current_statement:
            view_statements.append('\n'.join(current_statement))
        current_statement = [line]
    elif current_statement:
        current_statement.append(line)
        # Check if this completes a statement (ends with semicolon)
        if line.strip().endswith(';'):
            view_statements.append('\n'.join(current_statement))
            current_statement = []

view_names = [
    'v_filers',
    'v_disclosures',
    'v_registrations',
    'v_payments',
    'v_expenditures',
    'v_employers',
    'v_campaign_contributions',
    'v_other_payments',
    'v_attachments',
    'v_alameda_filers',
    'v_alameda_activity'
]

created_views = []
for i, (view_name, sql) in enumerate(zip(view_names, view_statements), 1):
    print(f"\n[{i}/11] Creating {view_name}...")
    try:
        client.query(sql).result()
        print(f"   ✓ SUCCESS")
        created_views.append(view_name)
    except Exception as e:
        print(f"   ✗ FAILED: {str(e)[:150]}")

print(f"\n✓ Created {len(created_views)}/{len(view_names)} views")

print("\n" + "="*80)
print("STEP 2: EXPORT ALL VIEWS TO CSV")
print("="*80)

total_rows = 0
exports = []

for i, view_name in enumerate(created_views, 1):
    print(f"\n[{i}/{len(created_views)}] {view_name}")

    try:
        # Query the entire view
        query = f"SELECT * FROM `{PROJECT_ID}.{DATASET_ID}.{view_name}`"

        print(f"   Querying...")
        df = client.query(query).to_dataframe()
        rows = len(df)

        # Save to CSV
        output_file = OUTPUT_DIR / f"{view_name}.csv"
        print(f"   Writing to CSV...")
        df.to_csv(output_file, index=False)

        size_mb = os.path.getsize(output_file) / 1024 / 1024
        print(f"   ✓ {rows:,} rows → {size_mb:.2f} MB")

        total_rows += rows
        exports.append({
            'view': view_name,
            'file': f"{view_name}.csv",
            'rows': rows,
            'size_mb': size_mb
        })

    except Exception as e:
        print(f"   ✗ FAILED: {str(e)[:150]}")

print("\n" + "="*80)
print("EXPORT COMPLETE")
print("="*80)
print(f"\nTotal files: {len(exports)}")
print(f"Total rows: {total_rows:,}")
print(f"Output directory: {OUTPUT_DIR.absolute()}\n")

print("Files created:")
for exp in exports:
    print(f"  {exp['file']:<30} {exp['rows']:>8,} rows  ({exp['size_mb']:>8.2f} MB)")

print("\n" + "="*80)
print("VIEWS READY FOR LOCAL DEPLOYMENT")
print("="*80)
print("\nThese CSV files contain the complete view data structure")
print("that will be used to build the website.")
