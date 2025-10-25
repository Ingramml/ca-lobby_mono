#!/usr/bin/env python3
"""
Extract complete transaction details from BigQuery
Joins v_payments_alameda to FULL CVR2_LOBBY_DISCLOSURE_CD table
to get missing firm names and dates
"""

from google.cloud import bigquery
import pandas as pd
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = os.getenv('CREDENTIALS_LOCATION')

# Initialize BigQuery client
client = bigquery.Client(project='ca-lobby')

# Output directory
OUTPUT_DIR = Path('alameda_data_exports')
OUTPUT_DIR.mkdir(exist_ok=True)

print("=" * 80)
print("EXTRACTING COMPLETE TRANSACTION DETAILS FROM BIGQUERY")
print("=" * 80)
print()
print("Purpose: Get missing firm names and dates for frontend activity JSON files")
print("Method: Join v_payments_alameda to FULL CVR2_LOBBY_DISCLOSURE_CD table")
print()

# The SQL query to get complete transaction details
# Joins payments to FULL v_disclosures view (not the filtered v_disclosures_alameda)
query = """
-- Extract complete payment transaction details
-- Joins v_payments_alameda to FULL v_disclosures view to get firm names and dates

SELECT
  p.filing_id,
  p.amendment_id,
  p.line_item,
  p.employer_full_name as organization,
  p.period_total as amount,
  p.fees_amount,
  p.reimbursement_amount,
  p.advance_amount,
  p.cumulative_total,
  p.form_type as payment_form_type,
  p.payment_tier,

  -- MISSING DATA FROM FULL DISCLOSURE VIEW:
  d.firm_name,              -- WHO WAS PAID (lobbying firm)
  d.period_start_date,      -- QUARTER START (clean DATE column)
  d.period_end_date,        -- QUARTER END (clean DATE column)
  d.report_date,            -- FILING DATE (clean DATE column)
  d.filer_id,
  d.entity_code,
  d.form_type as disclosure_form_type

FROM `ca-lobby.ca_lobby.v_payments` p
INNER JOIN `ca-lobby.ca_lobby.v_disclosures` d
  ON p.filing_id = d.filing_id
  AND p.amendment_id = d.amendment_id

WHERE p.is_alameda = TRUE
  AND UPPER(p.employer_full_name) IN (
  'ALAMEDA COUNTY WATER DISTRICT',
  'ALAMEDA COUNTY WASTE MANAGEMENT AUTHORITY',
  'ALAMEDA ALLIANCE FOR HEALTH',
  'ALAMEDA COUNTY FAIR',
  'ALAMEDA CORRIDOR-EAST CONSTRUCTION AUTHORITY',
  'ALAMEDA CORRIDOR TRANSPORTATION AUTHORITY',
  'ALAMEDA, CITY OF',
  'ALAMEDA COUNTY CONGESTION MANAGEMENT AGENCY',
  'ALAMEDA COUNTY TRANSPORTATION IMPROVEMENT AUTHORITY',
  'ALAMEDA UNIFIED SCHOOL DISTRICT',
  'ALAMEDA COUNTY EMPLOYEES\\' RETIREMENT ASSOCIATION'
)

ORDER BY p.employer_full_name, d.period_start_date DESC, p.line_item
"""

print("Running BigQuery query...")
print("Query: Join v_payments_alameda to v_disclosures (FULL, not filtered)")
print()

# Run the query
try:
    df = client.query(query).to_dataframe()

    print(f"✓ Query successful!")
    print(f"  Rows returned: {len(df):,}")
    print()

    # Show column summary
    print("Columns in result:")
    for col in df.columns:
        non_null = df[col].notna().sum()
        null_count = df[col].isna().sum()
        print(f"  - {col:30s} ({non_null:,} non-null, {null_count:,} null)")
    print()

    # Show organization breakdown
    print("Transaction breakdown by organization:")
    org_summary = df.groupby('organization').agg({
        'filing_id': 'count',
        'amount': 'sum'
    }).sort_values('amount', ascending=False)

    for org, row in org_summary.iterrows():
        print(f"  {org:60s} {row['filing_id']:4,} transactions  ${row['amount']:,.2f}")

    print()
    print(f"TOTAL: {len(df):,} transactions, ${df['amount'].sum():,.2f}")
    print()

    # Export to CSV
    output_file = OUTPUT_DIR / 'transaction_details_complete.csv'
    df.to_csv(output_file, index=False)

    size_mb = os.path.getsize(output_file) / 1024 / 1024
    print(f"✓ Exported to: {output_file}")
    print(f"  File size: {size_mb:.2f} MB")
    print()

    # Show sample data
    print("Sample data (first 3 rows):")
    print("-" * 80)
    sample = df.head(3)
    for idx, row in sample.iterrows():
        print(f"\nTransaction #{idx + 1}:")
        print(f"  Organization: {row['organization']}")
        print(f"  Firm: {row['firm_name']}")
        print(f"  Amount: ${row['amount']:,.2f}")
        print(f"  Period: {row['period_start_date']} to {row['period_end_date']}")
        print(f"  Filed: {row['report_date']}")

    print()
    print("=" * 80)
    print("✅ EXTRACTION COMPLETE!")
    print("=" * 80)
    print()
    print("Next step: Run update_activity_json_with_firm_data.py")
    print("This will update all activity JSON files with firm names and dates")
    print()

except Exception as e:
    print(f"❌ ERROR: {e}")
    print()
    print("Troubleshooting:")
    print("1. Check table name: CVR2_LOBBY_DISCLOSURE_CD vs CVR_LOBBY_DISCLOSURE_CD")
    print("2. Verify BigQuery credentials are loaded")
    print("3. Check that v_payments_alameda view exists")
    print()
    raise
