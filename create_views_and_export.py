"""
Create Views and Export to CSV
================================
1. Creates 11 simple views in BigQuery
2. Exports each view to CSV in alameda_data_exports/
"""

from google.cloud import bigquery
import pandas as pd
import os
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = os.getenv('CREDENTIALS_LOCATION')

PROJECT_ID = 'ca-lobby'
DATASET_ID = 'ca_lobby'
OUTPUT_DIR = Path('alameda_data_exports')
OUTPUT_DIR.mkdir(exist_ok=True)

client = bigquery.Client(project=PROJECT_ID)

print(f"{'='*80}")
print("CREATE VIEWS AND EXPORT TO CSV")
print(f"Project: {PROJECT_ID}")
print(f"Dataset: {DATASET_ID}")
print(f"Start Time: {datetime.now()}")
print(f"{'='*80}\n")

# Read the SQL file
print("Step 1: Reading view definitions from create_simple_views.sql...")
with open('create_simple_views.sql', 'r') as f:
    sql_content = f.read()

# Split into individual CREATE VIEW statements
view_statements = []
current_statement = []
for line in sql_content.split('\n'):
    if line.strip().startswith('--') and not line.strip().startswith('-- View'):
        continue
    if 'CREATE OR REPLACE VIEW' in line:
        if current_statement:
            view_statements.append('\n'.join(current_statement))
        current_statement = [line]
    elif current_statement:
        current_statement.append(line)
        if line.strip().endswith(';'):
            view_statements.append('\n'.join(current_statement))
            current_statement = []

if current_statement:
    view_statements.append('\n'.join(current_statement))

print(f"Found {len(view_statements)} view definitions\n")

# Step 2: Create each view
print(f"{'='*80}")
print("Step 2: Creating views in BigQuery...")
print(f"{'='*80}\n")

created_views = []
failed_views = []

for idx, statement in enumerate(view_statements):
    # Extract view name
    view_name = None
    for line in statement.split('\n'):
        if 'CREATE OR REPLACE VIEW' in line:
            # Extract view name from `ca-lobby.ca_lobby.view_name`
            parts = line.split('`')
            if len(parts) >= 2:
                full_name = parts[1]
                view_name = full_name.split('.')[-1]
                break

    if not view_name:
        print(f"[{idx+1}/{len(view_statements)}] ⚠ Could not extract view name, skipping...")
        continue

    print(f"[{idx+1}/{len(view_statements)}] Creating {view_name}...")

    try:
        query_job = client.query(statement)
        query_job.result()  # Wait for completion
        print(f"   ✓ SUCCESS")
        created_views.append(view_name)
    except Exception as e:
        error_msg = str(e)[:150]
        print(f"   ✗ FAILED: {error_msg}")
        failed_views.append({'view_name': view_name, 'error': error_msg})

print(f"\n{'='*80}")
print(f"View Creation Summary")
print(f"{'='*80}")
print(f"Created: {len(created_views)}")
print(f"Failed: {len(failed_views)}")

if failed_views:
    print(f"\nFailed views:")
    for fail in failed_views:
        print(f"  - {fail['view_name']}: {fail['error']}")

print(f"\n{'='*80}")
print("Step 3: Exporting views to CSV...")
print(f"{'='*80}\n")

# Step 3: Export each view to CSV
export_summary = []
total_rows_exported = 0

for idx, view_name in enumerate(created_views):
    print(f"[{idx+1}/{len(created_views)}] Exporting {view_name}...")

    try:
        # Query the view
        query = f"""
        SELECT *
        FROM `{PROJECT_ID}.{DATASET_ID}.{view_name}`
        """

        print(f"   Querying...")
        df = client.query(query).to_dataframe()
        actual_rows = len(df)

        # Save to CSV
        output_file = OUTPUT_DIR / f'{view_name}.csv'
        print(f"   Writing CSV...")
        df.to_csv(output_file, index=False)

        file_size_mb = os.path.getsize(output_file) / 1024 / 1024

        print(f"   ✓ SUCCESS - {actual_rows:,} rows → {file_size_mb:.2f} MB")

        export_summary.append({
            'view_name': view_name,
            'rows': actual_rows,
            'file_size_mb': file_size_mb,
            'status': 'SUCCESS'
        })

        total_rows_exported += actual_rows
        print()

    except Exception as e:
        error_msg = str(e)[:200]
        print(f"   ✗ FAILED: {error_msg}")
        print()

        export_summary.append({
            'view_name': view_name,
            'rows': 0,
            'file_size_mb': 0,
            'status': 'FAILED'
        })

# Step 4: Summary
print(f"\n{'='*80}")
print("EXPORT COMPLETE")
print(f"{'='*80}")

summary_df = pd.DataFrame(export_summary)
successful = len([s for s in export_summary if s['status'] == 'SUCCESS'])

print(f"\nViews Created: {len(created_views)}")
print(f"Views Exported: {successful}")
print(f"Export Failures: {len(export_summary) - successful}")
print(f"Total Rows Exported: {total_rows_exported:,}")

total_size_mb = sum([s['file_size_mb'] for s in export_summary])
print(f"Total Export Size: {total_size_mb:.2f} MB ({total_size_mb/1024:.2f} GB)")

print(f"\nOutput Directory: {OUTPUT_DIR.absolute()}")

# Save summary
summary_file = OUTPUT_DIR / '_VIEW_EXPORT_SUMMARY.csv'
summary_df.to_csv(summary_file, index=False)
print(f"Export Summary: {summary_file}")

print(f"\nEnd Time: {datetime.now()}")
print(f"{'='*80}")
