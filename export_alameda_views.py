"""
Export Alameda Data from Views
================================
Exports Alameda-filtered data from each view to CSV
"""

from google.cloud import bigquery
import pandas as pd
import os
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = os.getenv('CREDENTIALS_LOCATION')

PROJECT_ID = 'ca-lobby'
DATASET_ID = 'ca_lobby'
OUTPUT_DIR = Path('alameda_data_exports')
OUTPUT_DIR.mkdir(exist_ok=True)

client = bigquery.Client(project=PROJECT_ID)

print(f"{'='*80}")
print("ALAMEDA DATA EXPORT FROM VIEWS")
print(f"{'='*80}\n")

# Define views to export with Alameda filter
views_to_export = [
    {
        'view': 'v_filers',
        'filter': "WHERE is_alameda = TRUE",
        'output': 'v_alameda_filers.csv'
    },
    {
        'view': 'v_disclosures',
        'filter': "WHERE is_alameda = TRUE",
        'output': 'v_alameda_disclosures.csv'
    },
    {
        'view': 'v_registrations',
        'filter': "WHERE is_alameda = TRUE",
        'output': 'v_alameda_registrations.csv'
    },
    {
        'view': 'v_payments',
        'filter': "WHERE is_alameda = TRUE",
        'output': 'v_alameda_payments.csv'
    },
    {
        'view': 'v_expenditures',
        'filter': "WHERE is_alameda = TRUE",
        'output': 'v_alameda_expenditures.csv'
    },
    {
        'view': 'v_alameda_filers',
        'filter': "",  # Already filtered
        'output': 'v_alameda_filers_direct.csv'
    }
]

total_rows = 0
exports = []

for idx, view_info in enumerate(views_to_export):
    view_name = view_info['view']
    filter_clause = view_info['filter']
    output_name = view_info['output']

    print(f"[{idx+1}/{len(views_to_export)}] {view_name}")

    try:
        query = f"""
        SELECT *
        FROM `{PROJECT_ID}.{DATASET_ID}.{view_name}`
        {filter_clause}
        """

        print(f"   Querying...")
        df = client.query(query).to_dataframe()
        rows = len(df)

        output_file = OUTPUT_DIR / output_name
        print(f"   Writing...")
        df.to_csv(output_file, index=False)

        size_mb = os.path.getsize(output_file) / 1024 / 1024
        print(f"   ✓ {rows:,} rows → {size_mb:.2f} MB")

        total_rows += rows
        exports.append({'file': output_name, 'rows': rows, 'size_mb': size_mb})
        print()

    except Exception as e:
        print(f"   ✗ FAILED: {str(e)[:100]}")
        print()

print(f"{'='*80}")
print(f"COMPLETE - {len(exports)} files exported")
print(f"Total rows: {total_rows:,}")
print(f"Output: {OUTPUT_DIR.absolute()}")
print(f"{'='*80}\n")

print("Files created:")
for exp in exports:
    print(f"  {exp['file']} - {exp['rows']:,} rows ({exp['size_mb']:.2f} MB)")
