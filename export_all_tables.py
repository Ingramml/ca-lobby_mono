"""
Complete Database Export Script
=================================
Exports ALL tables from the ca_lobby dataset to CSV files
NO FILTERING - Complete table exports
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
print("COMPLETE DATABASE EXPORT - ALL TABLES")
print(f"Project: {PROJECT_ID}")
print(f"Dataset: {DATASET_ID}")
print(f"Output: {OUTPUT_DIR}")
print(f"Start Time: {datetime.now()}")
print(f"{'='*80}\n")

# Step 1: Get list of all tables in the dataset
print("Step 1: Discovering all tables in dataset...")
query = f"""
SELECT
    table_id as table_name,
    row_count,
    ROUND(size_bytes / 1024 / 1024, 2) as size_mb
FROM `{PROJECT_ID}.{DATASET_ID}.__TABLES__`
WHERE type = 1
ORDER BY table_id
"""

tables_info = client.query(query).to_dataframe()
total_tables = len(tables_info)
print(f"Found {total_tables} tables\n")
print(tables_info.to_string(index=False))
print(f"\n{'='*80}\n")

# Step 2: Export each table
print("Step 2: Exporting all tables...\n")

export_summary = []
total_rows_exported = 0
failed_exports = []

for idx, row in tables_info.iterrows():
    table_name = row['table_name']
    expected_rows = row['row_count']
    size_mb = row['size_mb']

    print(f"[{idx+1}/{total_tables}] Exporting {table_name}...")
    print(f"   Expected rows: {expected_rows:,}")
    print(f"   Size: {size_mb:.2f} MB")

    try:
        # Export entire table - NO FILTERING
        query = f"""
        SELECT *
        FROM `{PROJECT_ID}.{DATASET_ID}.{table_name}`
        """

        # Execute query
        df = client.query(query).to_dataframe()
        actual_rows = len(df)

        # Save to CSV
        output_file = OUTPUT_DIR / f'{table_name}.csv'
        df.to_csv(output_file, index=False)

        # Verify
        file_size_mb = os.path.getsize(output_file) / 1024 / 1024

        print(f"   ✓ Exported {actual_rows:,} rows → {output_file.name}")
        print(f"   ✓ File size: {file_size_mb:.2f} MB")

        # Check if row counts match
        if actual_rows != expected_rows:
            print(f"   ⚠ Row count mismatch! Expected {expected_rows:,}, got {actual_rows:,}")

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
        print(f"   ✗ FAILED: {str(e)[:100]}")
        print()

        failed_exports.append({
            'table_name': table_name,
            'error': str(e)
        })

        export_summary.append({
            'table_name': table_name,
            'expected_rows': expected_rows,
            'actual_rows': 0,
            'file_size_mb': 0,
            'status': f'FAILED: {str(e)[:50]}'
        })

# Step 3: Summary
print(f"\n{'='*80}")
print("EXPORT COMPLETE")
print(f"{'='*80}")

summary_df = pd.DataFrame(export_summary)
print(f"\nTables Processed: {total_tables}")
print(f"Successful Exports: {len([s for s in export_summary if s['status'] == 'SUCCESS'])}")
print(f"Failed Exports: {len(failed_exports)}")
print(f"Total Rows Exported: {total_rows_exported:,}")
print(f"\nOutput Directory: {OUTPUT_DIR.absolute()}")

# Save summary to CSV
summary_file = OUTPUT_DIR / '_EXPORT_SUMMARY.csv'
summary_df.to_csv(summary_file, index=False)
print(f"\nExport Summary: {summary_file}")

# Print failed exports
if failed_exports:
    print(f"\n{'='*80}")
    print("FAILED EXPORTS")
    print(f"{'='*80}")
    for fail in failed_exports:
        print(f"Table: {fail['table_name']}")
        print(f"Error: {fail['error']}")
        print()

print(f"\nEnd Time: {datetime.now()}")
print(f"{'='*80}")
