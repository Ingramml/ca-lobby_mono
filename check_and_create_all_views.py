#!/usr/bin/env python3
"""
Check existing views and create all 11 views needed for website development
"""

from google.cloud import bigquery
import sys
import os
from dotenv import load_dotenv

load_dotenv()
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = os.getenv('CREDENTIALS_LOCATION')

PROJECT_ID = 'ca-lobby'
DATASET_ID = 'ca_lobby'

client = bigquery.Client(project=PROJECT_ID)

print("="*80)
print("CHECKING EXISTING VIEWS")
print("="*80)

# List all views
query = f"""
SELECT table_name, table_type
FROM `{PROJECT_ID}.{DATASET_ID}.INFORMATION_SCHEMA.TABLES`
WHERE table_type = 'VIEW'
ORDER BY table_name
"""

existing_views = set()
for row in client.query(query).result():
    existing_views.add(row.table_name)
    print(f"  ✓ {row.table_name}")

print(f"\nFound {len(existing_views)} existing views\n")

print("="*80)
print("CREATING ALL 11 VIEWS")
print("="*80)

views_sql = [
    # 1. v_filers - All filers with Alameda flag
    """
    CREATE OR REPLACE VIEW `ca-lobby.ca_lobby.v_filers` AS
    SELECT
      FILER_ID as filer_id,
      NAML as last_name,
      NAMF as first_name,
      NAMT as title,
      NAMS as suffix,
      CONCAT(COALESCE(NAMF, ''), ' ', COALESCE(NAML, '')) as full_name,
      CASE
        WHEN UPPER(NAML) LIKE '%ALAMEDA%' OR UPPER(NAMF) LIKE '%ALAMEDA%' THEN TRUE
        ELSE FALSE
      END as is_alameda
    FROM `ca-lobby.ca_lobby.filername_cd`
    """,

    # 2. v_disclosures - Lobby disclosure filings
    """
    CREATE OR REPLACE VIEW `ca-lobby.ca_lobby.v_disclosures` AS
    SELECT
      FILING_ID as filing_id,
      AMEND_ID as amendment_id,
      REC_TYPE as record_type,
      FORM_TYPE as form_type,
      SENDER_ID as sender_id,
      FILER_ID as filer_id,
      ENTITY_CD as entity_code,
      FRM_NAML as firm_last_name,
      FRM_NAMF as firm_first_name,
      CONCAT(COALESCE(FRM_NAMF, ''), ' ', COALESCE(FRM_NAML, '')) as firm_full_name,
      CASE
        WHEN UPPER(FRM_NAML) LIKE '%ALAMEDA%' OR UPPER(FRM_NAMF) LIKE '%ALAMEDA%' THEN TRUE
        ELSE FALSE
      END as is_alameda
    FROM `ca-lobby.ca_lobby.cvr_lobby_disclosure_cd`
    """,

    # 3. v_registrations - Lobbyist registrations
    """
    CREATE OR REPLACE VIEW `ca-lobby.ca_lobby.v_registrations` AS
    SELECT
      FILING_ID as filing_id,
      AMEND_ID as amendment_id,
      REC_TYPE as record_type,
      FORM_TYPE as form_type,
      SENDER_ID as sender_id,
      FILER_ID as filer_id,
      ENTITY_CD as entity_code,
      FIRM_NAME as firm_name,
      FIRM_CITY as firm_city,
      FIRM_ST as firm_state,
      FIRM_ZIP4 as firm_zip,
      FIRM_PHON as firm_phone,
      MAIL_CITY as mail_city,
      MAIL_ST as mail_state,
      MAIL_ZIP4 as mail_zip,
      RPT_DATE as report_date,
      STMT_FIRM as statement_firm,
      CASE
        WHEN UPPER(FIRM_NAME) LIKE '%ALAMEDA%' OR UPPER(FIRM_CITY) LIKE '%ALAMEDA%' THEN TRUE
        ELSE FALSE
      END as is_alameda
    FROM `ca-lobby.ca_lobby.cvr_registration_cd`
    """,

    # 4. v_payments - Lobbying payments
    """
    CREATE OR REPLACE VIEW `ca-lobby.ca_lobby.v_payments` AS
    SELECT
      FILING_ID as filing_id,
      AMEND_ID as amendment_id,
      LINE_ITEM as line_item,
      EMPLR_NAML as employer_last_name,
      FEES_AMT as fees_amount,
      PER_TOTAL as period_total,
      CUM_TOTAL as cumulative_total,
      CASE
        WHEN FEES_AMT >= 10000 THEN 'High'
        WHEN FEES_AMT >= 5000 THEN 'Medium'
        ELSE 'Low'
      END as payment_tier,
      CASE
        WHEN UPPER(EMPLR_NAML) LIKE '%ALAMEDA%' THEN TRUE
        ELSE FALSE
      END as is_alameda
    FROM `ca-lobby.ca_lobby.lpay_cd`
    """,

    # 5. v_expenditures - Lobbying expenditures
    """
    CREATE OR REPLACE VIEW `ca-lobby.ca_lobby.v_expenditures` AS
    SELECT
      FILING_ID as filing_id,
      AMEND_ID as amendment_id,
      LINE_ITEM as line_item,
      EXPN_DSCR as expenditure_description,
      EXPN_DATE as expenditure_date,
      AMOUNT as amount,
      RECIP_NAML as recipient_last_name,
      RECIP_NAMF as recipient_first_name,
      CASE
        WHEN UPPER(RECIP_NAML) LIKE '%ALAMEDA%' OR UPPER(RECIP_NAMF) LIKE '%ALAMEDA%' OR UPPER(EXPN_DSCR) LIKE '%ALAMEDA%' THEN TRUE
        ELSE FALSE
      END as is_alameda
    FROM `ca-lobby.ca_lobby.lexp_cd`
    """,

    # 6. v_employers - Lobbyist employers
    """
    CREATE OR REPLACE VIEW `ca-lobby.ca_lobby.v_employers` AS
    SELECT
      FILING_ID as filing_id,
      AMEND_ID as amendment_id,
      LINE_ITEM as line_item,
      EMPLR_ID as employer_id,
      EMPLR_NAML as employer_last_name,
      EMPLR_NAMF as employer_first_name,
      EMPLR_CITY as employer_city,
      EMPLR_ST as employer_state,
      EMPLR_PHON as employer_phone,
      CASE
        WHEN UPPER(EMPLR_NAML) LIKE '%ALAMEDA%' OR UPPER(EMPLR_NAMF) LIKE '%ALAMEDA%' OR UPPER(EMPLR_CITY) LIKE '%ALAMEDA%' THEN TRUE
        ELSE FALSE
      END as is_alameda
    FROM `ca-lobby.ca_lobby.lemp_cd`
    """,

    # 7. v_coalitions - Lobbying coalitions
    """
    CREATE OR REPLACE VIEW `ca-lobby.ca_lobby.v_coalitions` AS
    SELECT
      FILING_ID as filing_id,
      AMEND_ID as amendment_id,
      LINE_ITEM as line_item,
      COALITION_ID as coalition_id,
      REC_TYPE as record_type,
      FORM_TYPE as form_type,
      ENTITY_CD as entity_code
    FROM `ca-lobby.ca_lobby.lccm_cd`
    """,

    # 8. v_other_payments - Other lobbying payments
    """
    CREATE OR REPLACE VIEW `ca-lobby.ca_lobby.v_other_payments` AS
    SELECT
      FILING_ID as filing_id,
      AMEND_ID as amendment_id,
      LINE_ITEM as line_item,
      EXPN_DATE as expenditure_date,
      AMOUNT as amount,
      PAYEE_NAML as payee_last_name,
      PAYEE_NAMF as payee_first_name,
      CASE
        WHEN UPPER(PAYEE_NAML) LIKE '%ALAMEDA%' OR UPPER(PAYEE_NAMF) LIKE '%ALAMEDA%' THEN TRUE
        ELSE FALSE
      END as is_alameda
    FROM `ca-lobby.ca_lobby.loth_cd`
    """,

    # 9. v_attachments - Filing attachments
    """
    CREATE OR REPLACE VIEW `ca-lobby.ca_lobby.v_attachments` AS
    SELECT
      FILING_ID as filing_id,
      AMEND_ID as amendment_id,
      LINE_ITEM as line_item,
      REC_TYPE as record_type,
      FORM_TYPE as form_type,
      ENTITY_CD as entity_code
    FROM `ca-lobby.ca_lobby.latt_cd`
    """,

    # 10. v_alameda_filers - Filtered Alameda filers only
    """
    CREATE OR REPLACE VIEW `ca-lobby.ca_lobby.v_alameda_filers` AS
    SELECT *
    FROM `ca-lobby.ca_lobby.v_filers`
    WHERE is_alameda = TRUE
    """,

    # 11. v_filer_summary - Summary of filer activity
    """
    CREATE OR REPLACE VIEW `ca-lobby.ca_lobby.v_filer_summary` AS
    SELECT
      f.filer_id,
      f.full_name,
      f.is_alameda,
      COUNT(DISTINCT p.filing_id) as total_payment_filings,
      COALESCE(SUM(p.fees_amount), 0) as total_fees,
      COALESCE(SUM(p.period_total), 0) as total_period_amount,
      COUNT(DISTINCT e.filing_id) as total_expenditure_filings,
      COALESCE(SUM(e.amount), 0) as total_expenditures
    FROM `ca-lobby.ca_lobby.v_filers` f
    LEFT JOIN `ca-lobby.ca_lobby.lpay_cd` p ON f.filer_id = p.FILING_ID
    LEFT JOIN `ca-lobby.ca_lobby.lexp_cd` e ON f.filer_id = e.FILING_ID
    GROUP BY f.filer_id, f.full_name, f.is_alameda
    """
]

view_names = [
    'v_filers',
    'v_disclosures',
    'v_registrations',
    'v_payments',
    'v_expenditures',
    'v_employers',
    'v_coalitions',
    'v_other_payments',
    'v_attachments',
    'v_alameda_filers',
    'v_filer_summary'
]

for i, (view_name, sql) in enumerate(zip(view_names, views_sql), 1):
    print(f"\n[{i}/11] {view_name}")
    try:
        client.query(sql).result()
        status = "✓ CREATED" if view_name not in existing_views else "✓ UPDATED"
        print(f"   {status}")
    except Exception as e:
        print(f"   ✗ FAILED: {e}")

print("\n" + "="*80)
print("VIEW CREATION COMPLETE")
print("="*80)
