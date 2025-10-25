"""
Complete Database Export Script V2
===================================
Exports ALL tables from the ca_lobby dataset to CSV files
NO FILTERING - Complete table exports
Using API list_tables() instead of metadata queries
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
OUTPUT_DIR = Path('full_database_export')
OUTPUT_DIR.mkdir(exist_ok=True)

client = bigquery.Client(project=PROJECT_ID)

print(f"{'='*80}")
print("COMPLETE DATABASE EXPORT - ALL TABLES (V2)")
print(f"Project: {PROJECT_ID}")
print(f"Dataset: {DATASET_ID}")
print(f"Output: {OUTPUT_DIR}")
print(f"Start Time: {datetime.now()}")
print(f"{'='*80}\n")

# Step 1: Get list of all tables using API (faster than metadata query)
print("Step 1: Discovering all tables in dataset...")
dataset_ref = client.dataset(DATASET_ID, project=PROJECT_ID)
tables = list(client.list_tables(dataset_ref))

print(f"Found {len(tables)} tables\n")

# Get table info
table_list = []
for table in tables:
    table_ref = client.get_table(table.reference)
    table_list.append({
        'table_name': table.table_id,
        'row_count': table_ref.num_rows,
        'size_gb': round(table_ref.num_bytes / 1024 / 1024 / 1024, 3)
    })

# Sort and display
table_list.sort(key=lambda x: x['table_name'])
df_tables = pd.DataFrame(table_list)
print(df_tables.to_string(index=False))
print(f"\n{'='*80}\n")

# Step 2: Export each table
print("Step 2: Exporting all tables...\n")

export_summary = []
total_rows_exported = 0
failed_exports = []
total_tables = len(table_list)

for idx, table_info in enumerate(table_list):
    table_name = table_info['table_name']
    expected_rows = table_info['row_count']
    size_gb = table_info['size_gb']

    print(f"[{idx+1}/{total_tables}] {table_name}")
    print(f"   Rows: {expected_rows:,} | Size: {size_gb:.3f} GB")

    # Skip if too large (>2GB = potential memory issues)
    if size_gb > 2:
        print(f"   ⚠ SKIPPED - Table too large ({size_gb:.3f} GB)")
        print(f"   Use BigQuery export to GCS instead for large tables")
        export_summary.append({
            'table_name': table_name,
            'expected_rows': expected_rows,
            'actual_rows': 0,
            'file_size_mb': 0,
            'status': f'SKIPPED - TOO LARGE ({size_gb:.3f} GB)'
        })
        print()
        continue

    try:
        # Export entire table - NO FILTERING
        query = f"""
        SELECT *
        FROM `{PROJECT_ID}.{DATASET_ID}.{table_name}`
        """

        # Execute query with progress indicator
        print(f"   Querying...")
        query_job = client.query(query)
        df = query_job.to_dataframe()
        actual_rows = len(df)

        # Save to CSV
        print(f"   Writing CSV...")
        output_file = OUTPUT_DIR / f'{table_name}.csv'
        df.to_csv(output_file, index=False)

        # Verify
        file_size_mb = os.path.getsize(output_file) / 1024 / 1024

        print(f"   ✓ SUCCESS - {actual_rows:,} rows → {file_size_mb:.2f} MB")

        # Check if row counts match
        if actual_rows != expected_rows:
            print(f"   ⚠ Row mismatch! Expected {expected_rows:,}, got {actual_rows:,}")

        export_summary.append({
            'table_name': table_name,
            'expected_rows': expected_rows,
            'actual_rows': actual_rows,
            'file_size_mb': file_size_mb,
            'status': 'SUCCESS'
        })

        total_rows_exported += actual_rows
        print()

    except Exception as e:
        error_msg = str(e)[:150]
        print(f"   ✗ FAILED: {error_msg}")
        print()

        failed_exports.append({
            'table_name': table_name,
            'error': error_msg
        })

        export_summary.append({
            'table_name': table_name,
            'expected_rows': expected_rows,
            'actual_rows': 0,
            'file_size_mb': 0,
            'status': f'FAILED: {error_msg[:50]}'
        })

# Step 3: Summary
print(f"\n{'='*80}")
print("EXPORT COMPLETE")
print(f"{'='*80}")

summary_df = pd.DataFrame(export_summary)
successful = len([s for s in export_summary if s['status'] == 'SUCCESS'])
skipped = len([s for s in export_summary if 'SKIPPED' in s['status']])

print(f"\nTables Found: {total_tables}")
print(f"Successful Exports: {successful}")
print(f"Skipped (Too Large): {skipped}")
print(f"Failed Exports: {len(failed_exports)}")
print(f"Total Rows Exported: {total_rows_exported:,}")

# Calculate total export size
total_size_mb = sum([s['file_size_mb'] for s in export_summary])
print(f"Total Export Size: {total_size_mb:.2f} MB ({total_size_mb/1024:.2f} GB)")

print(f"\nOutput Directory: {OUTPUT_DIR.absolute()}")

# Save summary to CSV
summary_file = OUTPUT_DIR / '_EXPORT_SUMMARY.csv'
summary_df.to_csv(summary_file, index=False)
print(f"Export Summary: {summary_file}")

# Print skipped tables
if skipped > 0:
    print(f"\n{'='*80}")
    print(f"SKIPPED TABLES ({skipped} tables)")
    print(f"{'='*80}")
    for s in export_summary:
        if 'SKIPPED' in s['status']:
            print(f"{s['table_name']}: {s['status']}")

# Print failed exports
if failed_exports:
    print(f"\n{'='*80}")
    print(f"FAILED EXPORTS ({len(failed_exports)} tables)")
    print(f"{'='*80}")
    for fail in failed_exports:
        print(f"\nTable: {fail['table_name']}")
        print(f"Error: {fail['error']}")

print(f"\nEnd Time: {datetime.now()}")
print(f"{'='*80}")
