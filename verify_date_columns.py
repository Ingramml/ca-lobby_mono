#!/usr/bin/env python3
"""
Verify that the new DATE columns are working correctly in BigQuery
"""

from google.cloud import bigquery
import os
from dotenv import load_dotenv

load_dotenv()
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = os.getenv('CREDENTIALS_LOCATION')

PROJECT_ID = 'ca-lobby'
DATASET_ID = 'ca_lobby'

client = bigquery.Client(project=PROJECT_ID)

print("="*80)
print("VERIFYING DATE COLUMNS IN BIGQUERY")
print("="*80)
print()

# Test queries for each table with DATE columns
test_queries = [
    {
        'table': 'cvr_lobby_disclosure_cd',
        'date_column': 'FROM_DATE_DATE',
        'description': 'Lobby disclosures from 2024'
    },
    {
        'table': 'cvr_registration_cd',
        'date_column': 'RPT_DATE_DATE',
        'description': 'Registrations from 2024'
    },
    {
        'table': 'filername_cd',
        'date_column': 'EFFECT_DT_DATE',
        'description': 'Filers with effect date in 2024'
    },
    {
        'table': 'lexp_cd',
        'date_column': 'EXPN_DATE_DATE',
        'description': 'Expenditures from 2024'
    },
    {
        'table': 'lccm_cd',
        'date_column': 'CTRIB_DATE_DATE',
        'description': 'Campaign contributions from 2024'
    }
]

all_working = True

for test in test_queries:
    print(f"\nTesting {test['table']}.{test['date_column']}")
    print(f"Query: {test['description']}")

    query = f"""
    SELECT
        COUNT(*) as total_rows,
        MIN({test['date_column']}) as earliest_date,
        MAX({test['date_column']}) as latest_date,
        COUNT(DISTINCT EXTRACT(YEAR FROM {test['date_column']})) as distinct_years
    FROM `{PROJECT_ID}.{DATASET_ID}.{test['table']}`
    WHERE {test['date_column']} IS NOT NULL
    """

    try:
        result = client.query(query).result()
        row = list(result)[0]

        print(f"  ✓ SUCCESS")
        print(f"    Total rows with dates: {row['total_rows']:,}")
        print(f"    Date range: {row['earliest_date']} to {row['latest_date']}")
        print(f"    Years covered: {row['distinct_years']}")

    except Exception as e:
        print(f"  ✗ FAILED: {str(e)[:150]}")
        all_working = False

# Test date filtering (critical for website queries)
print("\n" + "="*80)
print("TESTING DATE FILTERING")
print("="*80)

filter_test = """
SELECT
    EXTRACT(YEAR FROM FROM_DATE_DATE) as year,
    EXTRACT(QUARTER FROM FROM_DATE_DATE) as quarter,
    COUNT(*) as disclosure_count,
    SUM(CASE WHEN UPPER(FILER_NAML) LIKE '%ALAMEDA%' THEN 1 ELSE 0 END) as alameda_count
FROM `ca-lobby.ca_lobby.cvr_lobby_disclosure_cd`
WHERE FROM_DATE_DATE >= '2024-01-01'
  AND FROM_DATE_DATE < '2025-01-01'
GROUP BY year, quarter
ORDER BY year, quarter
"""

print("\nQuery: Disclosures by quarter in 2024")

try:
    results = client.query(filter_test).result()
    print("  ✓ SUCCESS - Date filtering working correctly")
    print("\n  Results:")
    for row in results:
        print(f"    Q{row['quarter']} {row['year']}: {row['disclosure_count']:,} disclosures ({row['alameda_count']:,} Alameda)")

except Exception as e:
    print(f"  ✗ FAILED: {str(e)[:200]}")
    all_working = False

# Test date functions (for website analytics)
print("\n" + "="*80)
print("TESTING DATE FUNCTIONS")
print("="*80)

functions_test = """
SELECT
    DATE_DIFF(MAX(FROM_DATE_DATE), MIN(FROM_DATE_DATE), DAY) as days_span,
    DATE_DIFF(MAX(FROM_DATE_DATE), MIN(FROM_DATE_DATE), MONTH) as months_span,
    DATE_DIFF(MAX(FROM_DATE_DATE), MIN(FROM_DATE_DATE), YEAR) as years_span
FROM `ca-lobby.ca_lobby.cvr_lobby_disclosure_cd`
WHERE FROM_DATE_DATE IS NOT NULL
"""

print("\nQuery: Calculate date range span")

try:
    result = client.query(functions_test).result()
    row = list(result)[0]
    print("  ✓ SUCCESS - Date functions working")
    print(f"    Data spans {row['days_span']:,} days / {row['months_span']:,} months / {row['years_span']} years")

except Exception as e:
    print(f"  ✗ FAILED: {str(e)[:200]}")
    all_working = False

print("\n" + "="*80)
print("VERIFICATION COMPLETE")
print("="*80)

if all_working:
    print("\n✓ All DATE columns are working correctly!")
    print("\nYou can now use these columns in your website queries:")
    print("  - Filter by date ranges: WHERE FROM_DATE_DATE >= '2024-01-01'")
    print("  - Extract year/quarter: EXTRACT(YEAR FROM FROM_DATE_DATE)")
    print("  - Calculate date differences: DATE_DIFF(date1, date2, DAY)")
    print("  - Order by date: ORDER BY FROM_DATE_DATE DESC")
else:
    print("\n✗ Some tests failed - review errors above")

print("\n" + "="*80)
