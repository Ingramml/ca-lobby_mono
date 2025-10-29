#!/usr/bin/env python3
"""
Create All Production Views in BigQuery

This script creates 5 production views with corrected date parsing.
"""

from pipeline.Bigquery_connection import bigquery_connect
import os
from dotenv import load_dotenv

def create_view(client, view_name, sql):
    """Create a single view"""
    print(f"\n🔨 Creating {view_name}...")
    try:
        result = client.query(sql).result()
        print(f"✅ SUCCESS: {view_name} created")
        return True
    except Exception as e:
        print(f"❌ FAILED: {view_name}")
        print(f"   Error: {str(e)[:300]}")
        return False

def main():
    print("=" * 80)
    print("CREATING ALL PRODUCTION VIEWS")
    print("=" * 80)

    load_dotenv()
    credentials_path = os.getenv('CREDENTIALS_LOCATION')

    if not credentials_path:
        print("❌ ERROR: CREDENTIALS_LOCATION not set")
        return

    client = bigquery_connect(credentials_path)
    if not client:
        print("❌ ERROR: Failed to connect to BigQuery")
        return

    # Define all views
    views = {}

    # VIEW 1: v_org_profiles_complete
    views['v_org_profiles_complete'] = '''
CREATE OR REPLACE VIEW `ca-lobby.ca_lobby.v_org_profiles_complete` AS
SELECT
  -- Organization identification
  CASE
    WHEN p.EMPLR_NAMF IS NULL OR p.EMPLR_NAMF = 'nan' THEN COALESCE(NULLIF(p.EMPLR_NAML, 'nan'), '')
    WHEN p.EMPLR_NAML IS NULL OR p.EMPLR_NAML = 'nan' THEN COALESCE(NULLIF(p.EMPLR_NAMF, 'nan'), '')
    ELSE CONCAT(p.EMPLR_NAMF, ' ', p.EMPLR_NAML)
  END as organization_name,
  p.EMPLR_ID as organization_filer_id,
  p.EMPLR_CITY as organization_city,
  p.EMPLR_ST as organization_state,
  p.EMPLR_ZIP4 as organization_zip,
  d.FILING_ID as filing_id,
  d.AMEND_ID as amendment_id,
  CAST(PARSE_TIMESTAMP('%m/%d/%Y %I:%M:%S %p', d.FROM_DATE) AS DATE) as period_start_date,
  CAST(PARSE_TIMESTAMP('%m/%d/%Y %I:%M:%S %p', d.THRU_DATE) AS DATE) as period_end_date,
  CAST(PARSE_TIMESTAMP('%m/%d/%Y %I:%M:%S %p', d.RPT_DATE) AS DATE) as filing_date,
  d.FIRM_NAME as lobbying_firm_name,
  d.FIRM_ID as lobbying_firm_id,
  d.FILER_NAML as firm_contact_last_name,
  d.FILER_NAMF as firm_contact_first_name,
  d.FORM_TYPE as form_type,
  d.ENTITY_CD as entity_code,
  p.LINE_ITEM as line_item,
  SAFE_CAST(p.FEES_AMT AS FLOAT64) as fees_amount,
  SAFE_CAST(p.REIMB_AMT AS FLOAT64) as reimbursement_amount,
  SAFE_CAST(p.ADVAN_AMT AS FLOAT64) as advance_amount,
  SAFE_CAST(p.PER_TOTAL AS FLOAT64) as period_total,
  SAFE_CAST(p.CUM_TOTAL AS FLOAT64) as cumulative_total,
  p.LBY_ACTVTY as lobbying_activity,
  EXTRACT(YEAR FROM CAST(PARSE_TIMESTAMP('%m/%d/%Y %I:%M:%S %p', d.FROM_DATE) AS DATE)) as reporting_year,
  EXTRACT(QUARTER FROM CAST(PARSE_TIMESTAMP('%m/%d/%Y %I:%M:%S %p', d.FROM_DATE) AS DATE)) as reporting_quarter
FROM `ca-lobby.ca_lobby.lpay_cd` p
INNER JOIN `ca-lobby.ca_lobby.cvr_lobby_disclosure_cd` d
  ON p.FILING_ID = d.FILING_ID AND p.AMEND_ID = d.AMEND_ID
WHERE p.EMPLR_NAML IS NOT NULL AND d.FROM_DATE IS NOT NULL
  AND d.FILING_ID != '0' AND p.EMPLR_NAML != 'nan'
ORDER BY CAST(PARSE_TIMESTAMP('%m/%d/%Y %I:%M:%S %p', d.FROM_DATE) AS DATE) DESC, organization_name, p.LINE_ITEM
'''

    # VIEW 2: v_lobbyist_network
    views['v_lobbyist_network'] = '''
CREATE OR REPLACE VIEW `ca-lobby.ca_lobby.v_lobbyist_network` AS
SELECT
  CASE
    WHEN p.EMPLR_NAMF IS NULL OR p.EMPLR_NAMF = 'nan' THEN COALESCE(NULLIF(p.EMPLR_NAML, 'nan'), '')
    WHEN p.EMPLR_NAML IS NULL OR p.EMPLR_NAML = 'nan' THEN COALESCE(NULLIF(p.EMPLR_NAMF, 'nan'), '')
    ELSE CONCAT(p.EMPLR_NAMF, ' ', p.EMPLR_NAML)
  END as organization_name,
  p.EMPLR_ID as organization_filer_id,
  d.FIRM_NAME as lobbying_firm,
  d.FIRM_ID as firm_filer_id,
  d.FIRM_CITY as firm_city,
  d.FIRM_ST as firm_state,
  CASE
    WHEN d.FILER_NAMF IS NULL OR d.FILER_NAMF = 'nan' THEN COALESCE(NULLIF(d.FILER_NAML, 'nan'), '')
    WHEN d.FILER_NAML IS NULL OR d.FILER_NAML = 'nan' THEN COALESCE(NULLIF(d.FILER_NAMF, 'nan'), '')
    ELSE CONCAT(d.FILER_NAMF, ' ', d.FILER_NAML)
  END as firm_contact_name,
  COUNT(DISTINCT d.FILING_ID) as filing_count,
  SUM(SAFE_CAST(p.FEES_AMT AS FLOAT64)) as total_fees_paid,
  SUM(SAFE_CAST(p.REIMB_AMT AS FLOAT64)) as total_reimbursements,
  SUM(SAFE_CAST(p.ADVAN_AMT AS FLOAT64)) as total_advances,
  SUM(SAFE_CAST(p.PER_TOTAL AS FLOAT64)) as total_payments,
  MIN(CAST(PARSE_TIMESTAMP('%m/%d/%Y %I:%M:%S %p', d.FROM_DATE) AS DATE)) as first_activity_date,
  MAX(CAST(PARSE_TIMESTAMP('%m/%d/%Y %I:%M:%S %p', d.THRU_DATE) AS DATE)) as last_activity_date
FROM `ca-lobby.ca_lobby.lpay_cd` p
INNER JOIN `ca-lobby.ca_lobby.cvr_lobby_disclosure_cd` d
  ON p.FILING_ID = d.FILING_ID AND p.AMEND_ID = d.AMEND_ID
WHERE p.EMPLR_NAML IS NOT NULL AND d.FIRM_NAME IS NOT NULL
  AND d.FILING_ID != '0' AND p.EMPLR_NAML != 'nan'
GROUP BY organization_name, p.EMPLR_ID, d.FIRM_NAME, d.FIRM_ID, d.FIRM_CITY, d.FIRM_ST, firm_contact_name
ORDER BY organization_name, total_payments DESC
'''

    # VIEW 3: v_activity_timeline
    views['v_activity_timeline'] = '''
CREATE OR REPLACE VIEW `ca-lobby.ca_lobby.v_activity_timeline` AS
WITH latest_amendments AS (
  SELECT FILING_ID, MAX(SAFE_CAST(AMEND_ID AS INT64)) as max_amend_id
  FROM `ca-lobby.ca_lobby.cvr_lobby_disclosure_cd`
  WHERE FILING_ID IS NOT NULL
  GROUP BY FILING_ID
)
SELECT
  CASE
    WHEN p.EMPLR_NAMF IS NULL OR p.EMPLR_NAMF = 'nan' THEN COALESCE(NULLIF(p.EMPLR_NAML, 'nan'), '')
    WHEN p.EMPLR_NAML IS NULL OR p.EMPLR_NAML = 'nan' THEN COALESCE(NULLIF(p.EMPLR_NAMF, 'nan'), '')
    ELSE CONCAT(p.EMPLR_NAMF, ' ', p.EMPLR_NAML)
  END as organization_name,
  p.EMPLR_ID as organization_filer_id,
  d.FILING_ID as filing_id,
  d.AMEND_ID as amendment_id,
  CAST(PARSE_TIMESTAMP('%m/%d/%Y %I:%M:%S %p', d.FROM_DATE) AS DATE) as period_start_date,
  CAST(PARSE_TIMESTAMP('%m/%d/%Y %I:%M:%S %p', d.THRU_DATE) AS DATE) as period_end_date,
  CAST(PARSE_TIMESTAMP('%m/%d/%Y %I:%M:%S %p', d.RPT_DATE) AS DATE) as report_date,
  EXTRACT(YEAR FROM CAST(PARSE_TIMESTAMP('%m/%d/%Y %I:%M:%S %p', d.FROM_DATE) AS DATE)) as reporting_year,
  EXTRACT(QUARTER FROM CAST(PARSE_TIMESTAMP('%m/%d/%Y %I:%M:%S %p', d.FROM_DATE) AS DATE)) as reporting_quarter,
  d.FIRM_NAME as lobbying_firm_name,
  d.FIRM_ID as lobbying_firm_id,
  d.FORM_TYPE as form_type,
  d.ENTITY_CD as entity_code,
  SUM(SAFE_CAST(p.FEES_AMT AS FLOAT64)) as total_fees,
  SUM(SAFE_CAST(p.REIMB_AMT AS FLOAT64)) as total_reimbursements,
  SUM(SAFE_CAST(p.ADVAN_AMT AS FLOAT64)) as total_advances,
  SUM(SAFE_CAST(p.PER_TOTAL AS FLOAT64)) as total_payments,
  COUNT(p.LINE_ITEM) as payment_line_item_count
FROM `ca-lobby.ca_lobby.lpay_cd` p
INNER JOIN `ca-lobby.ca_lobby.cvr_lobby_disclosure_cd` d
  ON p.FILING_ID = d.FILING_ID AND p.AMEND_ID = d.AMEND_ID
INNER JOIN latest_amendments la
  ON d.FILING_ID = la.FILING_ID AND SAFE_CAST(d.AMEND_ID AS INT64) = la.max_amend_id
WHERE p.EMPLR_NAML IS NOT NULL AND d.FROM_DATE IS NOT NULL
  AND d.FILING_ID != '0' AND p.EMPLR_NAML != 'nan'
GROUP BY organization_name, p.EMPLR_ID, d.FILING_ID, d.AMEND_ID, d.FROM_DATE, d.THRU_DATE, d.RPT_DATE, d.FIRM_NAME, d.FIRM_ID, d.FORM_TYPE, d.ENTITY_CD
ORDER BY period_start_date DESC, organization_name
'''

    # VIEW 4: v_expenditure_categories
    views['v_expenditure_categories'] = '''
CREATE OR REPLACE VIEW `ca-lobby.ca_lobby.v_expenditure_categories` AS
SELECT
  CASE
    WHEN p.EMPLR_NAMF IS NULL OR p.EMPLR_NAMF = 'nan' THEN COALESCE(NULLIF(p.EMPLR_NAML, 'nan'), '')
    WHEN p.EMPLR_NAML IS NULL OR p.EMPLR_NAML = 'nan' THEN COALESCE(NULLIF(p.EMPLR_NAMF, 'nan'), '')
    ELSE CONCAT(p.EMPLR_NAMF, ' ', p.EMPLR_NAML)
  END as organization_name,
  p.EMPLR_ID as organization_filer_id,
  d.FILING_ID as filing_id,
  CAST(PARSE_TIMESTAMP('%m/%d/%Y %I:%M:%S %p', d.FROM_DATE) AS DATE) as period_start_date,
  CAST(PARSE_TIMESTAMP('%m/%d/%Y %I:%M:%S %p', d.THRU_DATE) AS DATE) as period_end_date,
  EXTRACT(YEAR FROM CAST(PARSE_TIMESTAMP('%m/%d/%Y %I:%M:%S %p', d.FROM_DATE) AS DATE)) as reporting_year,
  EXTRACT(QUARTER FROM CAST(PARSE_TIMESTAMP('%m/%d/%Y %I:%M:%S %p', d.FROM_DATE) AS DATE)) as reporting_quarter,
  exp.EXPN_DSCR as expense_description,
  exp.EXPN_DATE as expense_date,
  SAFE_CAST(exp.AMOUNT AS FLOAT64) as expense_amount,
  exp.PAYEE_NAML as payee_last_name,
  exp.PAYEE_NAMF as payee_first_name,
  CASE
    WHEN exp.PAYEE_NAMF IS NULL OR exp.PAYEE_NAMF = 'nan' THEN COALESCE(NULLIF(exp.PAYEE_NAML, 'nan'), '')
    WHEN exp.PAYEE_NAML IS NULL OR exp.PAYEE_NAML = 'nan' THEN COALESCE(NULLIF(exp.PAYEE_NAMF, 'nan'), '')
    ELSE CONCAT(exp.PAYEE_NAMF, ' ', exp.PAYEE_NAML)
  END as payee_full_name,
  exp.PAYEE_CITY as payee_city,
  exp.PAYEE_ST as payee_state
FROM `ca-lobby.ca_lobby.lexp_cd` exp
INNER JOIN `ca-lobby.ca_lobby.cvr_lobby_disclosure_cd` d
  ON exp.FILING_ID = d.FILING_ID AND exp.AMEND_ID = d.AMEND_ID
LEFT JOIN `ca-lobby.ca_lobby.lpay_cd` p
  ON d.FILING_ID = p.FILING_ID AND d.AMEND_ID = p.AMEND_ID
WHERE d.FROM_DATE IS NOT NULL AND d.FILING_ID != '0'
  AND exp.AMOUNT IS NOT NULL AND p.EMPLR_NAML IS NOT NULL AND p.EMPLR_NAML != 'nan'
ORDER BY organization_name, period_start_date DESC, expense_amount DESC
'''

    # VIEW 5: v_organization_summary
    views['v_organization_summary'] = '''
CREATE OR REPLACE VIEW `ca-lobby.ca_lobby.v_organization_summary` AS
SELECT
  CASE
    WHEN p.EMPLR_NAMF IS NULL OR p.EMPLR_NAMF = 'nan' THEN COALESCE(NULLIF(p.EMPLR_NAML, 'nan'), '')
    WHEN p.EMPLR_NAML IS NULL OR p.EMPLR_NAML = 'nan' THEN COALESCE(NULLIF(p.EMPLR_NAMF, 'nan'), '')
    ELSE CONCAT(p.EMPLR_NAMF, ' ', p.EMPLR_NAML)
  END as organization_name,
  p.EMPLR_ID as organization_filer_id,
  p.EMPLR_CITY as organization_city,
  p.EMPLR_ST as organization_state,
  COUNT(DISTINCT d.FILING_ID) as total_filings,
  COUNT(DISTINCT d.FIRM_NAME) as total_lobbying_firms,
  COUNT(p.LINE_ITEM) as total_payment_line_items,
  SUM(SAFE_CAST(p.FEES_AMT AS FLOAT64)) as total_fees,
  SUM(SAFE_CAST(p.REIMB_AMT AS FLOAT64)) as total_reimbursements,
  SUM(SAFE_CAST(p.ADVAN_AMT AS FLOAT64)) as total_advances,
  SUM(SAFE_CAST(p.PER_TOTAL AS FLOAT64)) as total_spending,
  MIN(CAST(PARSE_TIMESTAMP('%m/%d/%Y %I:%M:%S %p', d.FROM_DATE) AS DATE)) as first_activity_date,
  MAX(CAST(PARSE_TIMESTAMP('%m/%d/%Y %I:%M:%S %p', d.THRU_DATE) AS DATE)) as last_activity_date,
  MAX(EXTRACT(YEAR FROM CAST(PARSE_TIMESTAMP('%m/%d/%Y %I:%M:%S %p', d.FROM_DATE) AS DATE))) as most_recent_year
FROM `ca-lobby.ca_lobby.lpay_cd` p
INNER JOIN `ca-lobby.ca_lobby.cvr_lobby_disclosure_cd` d
  ON p.FILING_ID = d.FILING_ID AND p.AMEND_ID = d.AMEND_ID
WHERE p.EMPLR_NAML IS NOT NULL AND d.FROM_DATE IS NOT NULL
  AND d.FILING_ID != '0' AND p.EMPLR_NAML != 'nan'
GROUP BY organization_name, p.EMPLR_ID, p.EMPLR_CITY, p.EMPLR_ST
ORDER BY total_spending DESC, organization_name
'''

    # Create all views
    success_count = 0
    for view_name, sql in views.items():
        if create_view(client, view_name, sql):
            success_count += 1

    # Summary
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"\n✅ Successfully created: {success_count}/{len(views)} views")

    if success_count == len(views):
        print("\n🎉 All views created successfully!")
        print("\nNext step: Run test_production_views.py to verify")
    else:
        print("\n⚠️  Some views failed. Review errors above.")

if __name__ == "__main__":
    main()
