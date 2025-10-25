#!/usr/bin/env python3
"""
Convert all STRING date columns to proper DATE type in BigQuery
"""

from google.cloud import bigquery
import os
from dotenv import load_dotenv
import pandas as pd

load_dotenv()
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = os.getenv('CREDENTIALS_LOCATION')

PROJECT_ID = 'ca-lobby'
DATASET_ID = 'ca_lobby'

client = bigquery.Client(project=PROJECT_ID)

print("="*80)
print("CONVERTING DATE COLUMNS FROM STRING TO DATE TYPE")
print("="*80)
print()

# Read the list of columns to convert
df = pd.read_csv('date_columns_to_convert.csv')

print(f"Found {len(df)} columns to convert\n")

# Group by table to process all columns in a table together
tables = df.groupby('table')

conversion_queries = []
success_count = 0
failed_count = 0

for table_name, columns in tables:
    print(f"\n{'='*80}")
    print(f"TABLE: {table_name}")
    print(f"{'='*80}")

    date_columns = columns['column'].tolist()
    print(f"Converting {len(date_columns)} columns: {', '.join(date_columns)}")

    # Build ALTER TABLE query to add new DATE columns
    for col_name in date_columns:
        new_col_name = f"{col_name}_DATE"

        print(f"\n  Processing {col_name}...")

        # Step 1: Add new DATE column
        add_column_sql = f"""
        ALTER TABLE `{PROJECT_ID}.{DATASET_ID}.{table_name}`
        ADD COLUMN IF NOT EXISTS {new_col_name} DATE
        """

        try:
            print(f"    1. Adding column {new_col_name}...")
            client.query(add_column_sql).result()
            print(f"       ✓ Column added")
        except Exception as e:
            error_msg = str(e)
            if "already exists" in error_msg.lower():
                print(f"       ✓ Column already exists")
            else:
                print(f"       ✗ Failed to add column: {str(e)[:100]}")
                failed_count += 1
                continue

        # Step 2: Update the new column with parsed dates
        # Date format is "M/D/YYYY 12:00:00 AM"
        update_sql = f"""
        UPDATE `{PROJECT_ID}.{DATASET_ID}.{table_name}`
        SET {new_col_name} = PARSE_DATE('%m/%d/%Y', REGEXP_EXTRACT({col_name}, r'^(\\d+/\\d+/\\d+)'))
        WHERE {col_name} IS NOT NULL
          AND {col_name} != 'nan'
          AND {col_name} != ''
        """

        try:
            print(f"    2. Converting dates from {col_name}...")
            job = client.query(update_sql)
            result = job.result()
            rows_updated = job.num_dml_affected_rows
            print(f"       ✓ Converted {rows_updated:,} rows")

            success_count += 1
            conversion_queries.append({
                'table': table_name,
                'old_column': col_name,
                'new_column': new_col_name,
                'rows_updated': rows_updated,
                'status': 'success'
            })

        except Exception as e:
            print(f"       ✗ Failed to convert: {str(e)[:200]}")
            failed_count += 1
            conversion_queries.append({
                'table': table_name,
                'old_column': col_name,
                'new_column': new_col_name,
                'rows_updated': 0,
                'status': 'failed',
                'error': str(e)[:200]
            })

print("\n" + "="*80)
print("CONVERSION SUMMARY")
print("="*80)

print(f"\nTotal columns processed: {len(df)}")
print(f"  ✓ Successfully converted: {success_count}")
print(f"  ✗ Failed: {failed_count}")

# Save results
results_df = pd.DataFrame(conversion_queries)
results_df.to_csv('date_conversion_results.csv', index=False)
print(f"\n✓ Saved detailed results to: date_conversion_results.csv")

if success_count > 0:
    print("\n" + "="*80)
    print("NEW DATE COLUMNS CREATED")
    print("="*80)

    successful = results_df[results_df['status'] == 'success']
    for _, row in successful.iterrows():
        print(f"\n{row['table']}:")
        print(f"  Old column: {row['old_column']} (STRING)")
        print(f"  New column: {row['new_column']} (DATE)")
        print(f"  Rows converted: {row['rows_updated']:,}")

print("\n" + "="*80)
print("NEXT STEPS")
print("="*80)
print("\n1. Review the new *_DATE columns in BigQuery")
print("2. Update your views to use the new DATE columns instead of STRING")
print("3. Optionally drop the old STRING columns if no longer needed")
print("\nExample view update:")
print("  FROM_DATE (STRING) → FROM_DATE_DATE (DATE)")
print("  RPT_DATE (STRING) → RPT_DATE_DATE (DATE)")

print("\n" + "="*80)
print("COMPLETE")
print("="*80)
