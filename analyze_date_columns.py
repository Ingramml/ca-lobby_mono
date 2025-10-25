#!/usr/bin/env python3
"""
Analyze all BigQuery tables to find DATE/DTE columns that need type conversion
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
print("ANALYZING DATE COLUMNS IN ALL TABLES")
print("="*80)
print()

# Get all tables in the dataset
query = f"""
SELECT table_name
FROM `{PROJECT_ID}.{DATASET_ID}.INFORMATION_SCHEMA.TABLES`
WHERE table_type = 'BASE TABLE'
ORDER BY table_name
"""

tables = [row.table_name for row in client.query(query).result()]
print(f"Found {len(tables)} tables to analyze\n")

all_date_columns = []

for table_name in tables:
    print(f"\n{'='*80}")
    print(f"TABLE: {table_name}")
    print(f"{'='*80}")

    # Get all columns with their data types
    schema_query = f"""
    SELECT
        column_name,
        data_type,
        is_nullable
    FROM `{PROJECT_ID}.{DATASET_ID}.INFORMATION_SCHEMA.COLUMNS`
    WHERE table_name = '{table_name}'
    ORDER BY ordinal_position
    """

    columns = client.query(schema_query).result()

    # Find columns that look like dates
    date_related_columns = []
    for col in columns:
        col_name = col.column_name
        col_type = col.data_type

        # Check if column name contains DATE or DT or ends with _DT or _DATE
        is_date_name = (
            'DATE' in col_name.upper() or
            col_name.upper().endswith('_DT') or
            col_name.upper().endswith('_DTE') or
            col_name.upper().startswith('DT_')
        )

        if is_date_name:
            date_related_columns.append({
                'table': table_name,
                'column': col_name,
                'current_type': col_type,
                'nullable': col.is_nullable,
                'needs_conversion': col_type not in ['DATE', 'DATETIME', 'TIMESTAMP']
            })

            status = "✗ NEEDS CONVERSION" if col_type not in ['DATE', 'DATETIME', 'TIMESTAMP'] else "✓ Already correct"
            print(f"  {col_name:<30} {col_type:<15} {status}")

    if not date_related_columns:
        print("  (No date-related columns found)")

    all_date_columns.extend(date_related_columns)

# Summary
print("\n" + "="*80)
print("SUMMARY")
print("="*80)

df = pd.DataFrame(all_date_columns)

if len(df) > 0:
    needs_conversion = df[df['needs_conversion'] == True]
    already_correct = df[df['needs_conversion'] == False]

    print(f"\nTotal date-related columns found: {len(df)}")
    print(f"  ✓ Already correct type: {len(already_correct)}")
    print(f"  ✗ Need conversion: {len(needs_conversion)}")

    if len(needs_conversion) > 0:
        print("\n" + "="*80)
        print("COLUMNS THAT NEED CONVERSION")
        print("="*80)

        # Group by table
        for table_name in needs_conversion['table'].unique():
            table_cols = needs_conversion[needs_conversion['table'] == table_name]
            print(f"\n{table_name}:")
            for _, row in table_cols.iterrows():
                print(f"  - {row['column']:<30} ({row['current_type']})")

        # Save to CSV for further analysis
        needs_conversion.to_csv('date_columns_to_convert.csv', index=False)
        print(f"\n✓ Saved detailed list to: date_columns_to_convert.csv")

        # Check sample data to determine if dates are in valid format
        print("\n" + "="*80)
        print("SAMPLE DATA ANALYSIS")
        print("="*80)

        for _, row in needs_conversion.head(10).iterrows():
            print(f"\n{row['table']}.{row['column']} (current type: {row['current_type']})")

            sample_query = f"""
            SELECT {row['column']}, COUNT(*) as count
            FROM `{PROJECT_ID}.{DATASET_ID}.{row['table']}`
            WHERE {row['column']} IS NOT NULL
            GROUP BY {row['column']}
            ORDER BY count DESC
            LIMIT 5
            """

            try:
                samples = client.query(sample_query).result()
                print("  Sample values:")
                for sample in samples:
                    value = sample[row['column']]
                    count = sample['count']
                    print(f"    {value} (appears {count:,} times)")
            except Exception as e:
                print(f"    Error getting samples: {str(e)[:100]}")

else:
    print("\nNo date-related columns found in any table")

print("\n" + "="*80)
print("ANALYSIS COMPLETE")
print("="*80)
