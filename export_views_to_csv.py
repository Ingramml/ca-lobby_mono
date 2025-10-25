"""
Export All Views to CSV
========================
Exports all BigQuery views to CSV files in alameda_data_exports/
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
print("EXPORTING ALL VIEWS TO CSV")
print(f"Project: {PROJECT_ID}")
print(f"Dataset: {DATASET_ID}")
print(f"Output: {OUTPUT_DIR}")
print(f"Start Time: {datetime.now()}")
print(f"{'='*80}\n")

# Step 1: Discover all views in the dataset
print("Step 1: Discovering all views...\n")

# Get all tables in the dataset
dataset_ref = client.dataset(DATASET_ID, project=PROJECT_ID)
all_objects = list(client.list_tables(dataset_ref))

# Filter to only views
views = []
for obj in all_objects:
    full_table = client.get_table(obj.reference)
    if full_table.table_type == 'VIEW' or full_table.table_type == 'MATERIALIZED_VIEW':
        views.append({
            'view_name': obj.table_id,
            'view_type': full_table.table_type,
            'num_rows': full_table.num_rows if hasattr(full_table, 'num_rows') else 'N/A'
        })

# Sort by name
views.sort(key=lambda x: x['view_name'])

print(f"Found {len(views)} views/materialized views:\n")
for v in views:
    print(f"  - {v['view_name']} ({v['view_type']})")

if len(views) == 0:
    print("\n⚠ No views found in the dataset!")
    print("Make sure you've run CREATE_ALL_VIEWS.sql first")
    print("\nTo create views:")
    print("  bq query --use_legacy_sql=false < CREATE_ALL_VIEWS.sql")
    exit(1)

print(f"\n{'='*80}\n")

# Step 2: Export each view
print("Step 2: Exporting views to CSV...\n")

export_summary = []
total_rows_exported = 0
failed_exports = []

for idx, view_info in enumerate(views):
    view_name = view_info['view_name']
    view_type = view_info['view_type']

    print(f"[{idx+1}/{len(views)}] Exporting {view_name} ({view_type})...")

    try:
        # Query the view
        query = f"""
        SELECT *
        FROM `{PROJECT_ID}.{DATASET_ID}.{view_name}`
        """

        print(f"   Querying view...")
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
            'view_type': view_type,
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

        failed_exports.append({
            'view_name': view_name,
            'error': error_msg
        })

        export_summary.append({
            'view_name': view_name,
            'view_type': view_type,
            'rows': 0,
            'file_size_mb': 0,
            'status': f'FAILED'
        })

# Step 3: Summary
print(f"\n{'='*80}")
print("EXPORT COMPLETE")
print(f"{'='*80}")

summary_df = pd.DataFrame(export_summary)
successful = len([s for s in export_summary if s['status'] == 'SUCCESS'])

print(f"\nViews Found: {len(views)}")
print(f"Successful Exports: {successful}")
print(f"Failed Exports: {len(failed_exports)}")
print(f"Total Rows Exported: {total_rows_exported:,}")

total_size_mb = sum([s['file_size_mb'] for s in export_summary])
print(f"Total Export Size: {total_size_mb:.2f} MB ({total_size_mb/1024:.2f} GB)")

print(f"\nOutput Directory: {OUTPUT_DIR.absolute()}")

# Save summary
summary_file = OUTPUT_DIR / '_VIEW_EXPORT_SUMMARY.csv'
summary_df.to_csv(summary_file, index=False)
print(f"Export Summary: {summary_file}")

# Print failures if any
if failed_exports:
    print(f"\n{'='*80}")
    print(f"FAILED EXPORTS ({len(failed_exports)} views)")
    print(f"{'='*80}")
    for fail in failed_exports:
        print(f"\nView: {fail['view_name']}")
        print(f"Error: {fail['error']}")

print(f"\nEnd Time: {datetime.now()}")
print(f"{'='*80}")
