#!/usr/bin/env python3
"""
Fix ALL 'nan' issues and create clear money flow breakdown views
"""

from google.cloud import bigquery
import os
from dotenv import load_dotenv

load_dotenv()
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = os.getenv('CREDENTIALS_LOCATION')
client = bigquery.Client(project='ca-lobby')

print("="*80)
print("STEP 1: FIX ALL 'nan' ISSUES IN VIEWS")
print("="*80)

# The issue: pandas reads NULL as 'nan' string, and our CONCAT includes it
# Solution: Filter out 'nan' strings in BigQuery views

views_to_fix = [
    ('v_payments', '''
    CREATE OR REPLACE VIEW `ca-lobby.ca_lobby.v_payments` AS
    SELECT
      FILING_ID as filing_id,
      AMEND_ID as amendment_id,
      LINE_ITEM as line_item,
      CASE WHEN EMPLR_NAML = 'nan' THEN NULL ELSE EMPLR_NAML END as employer_last_name,
      CASE WHEN EMPLR_NAMF = 'nan' THEN NULL ELSE EMPLR_NAMF END as employer_first_name,
      CASE
        WHEN EMPLR_NAMF IS NULL OR EMPLR_NAMF = 'nan' THEN COALESCE(NULLIF(EMPLR_NAML, 'nan'), '')
        WHEN EMPLR_NAML IS NULL OR EMPLR_NAML = 'nan' THEN COALESCE(NULLIF(EMPLR_NAMF, 'nan'), '')
        ELSE CONCAT(EMPLR_NAMF, ' ', EMPLR_NAML)
      END as employer_full_name,
      CAST(FEES_AMT AS FLOAT64) as fees_amount,
      CAST(REIMB_AMT AS FLOAT64) as reimbursement_amount,
      CAST(ADVAN_AMT AS FLOAT64) as advance_amount,
      CAST(PER_TOTAL AS FLOAT64) as period_total,
      CAST(CUM_TOTAL AS FLOAT64) as cumulative_total,
      FORM_TYPE as form_type,
      CASE
        WHEN CAST(PER_TOTAL AS FLOAT64) >= 100000 THEN 'Very High (100K+)'
        WHEN CAST(PER_TOTAL AS FLOAT64) >= 10000 THEN 'High (10K+)'
        WHEN CAST(PER_TOTAL AS FLOAT64) >= 1000 THEN 'Medium (1K+)'
        ELSE 'Low (<1K)'
      END as payment_tier,
      CASE
        WHEN UPPER(EMPLR_NAML) LIKE '%ALAMEDA%' OR UPPER(EMPLR_NAMF) LIKE '%ALAMEDA%' THEN TRUE
        ELSE FALSE
      END as is_alameda
    FROM `ca-lobby.ca_lobby.lpay_cd`
    WHERE FILING_ID IS NOT NULL
    '''),

    ('v_expenditures', '''
    CREATE OR REPLACE VIEW `ca-lobby.ca_lobby.v_expenditures` AS
    SELECT
      FILING_ID as filing_id,
      AMEND_ID as amendment_id,
      LINE_ITEM as line_item,
      CASE WHEN PAYEE_NAML = 'nan' THEN NULL ELSE PAYEE_NAML END as payee_last_name,
      CASE WHEN PAYEE_NAMF = 'nan' THEN NULL ELSE PAYEE_NAMF END as payee_first_name,
      CASE
        WHEN PAYEE_NAMF IS NULL OR PAYEE_NAMF = 'nan' THEN COALESCE(NULLIF(PAYEE_NAML, 'nan'), '')
        WHEN PAYEE_NAML IS NULL OR PAYEE_NAML = 'nan' THEN COALESCE(NULLIF(PAYEE_NAMF, 'nan'), '')
        ELSE CONCAT(PAYEE_NAMF, ' ', PAYEE_NAML)
      END as payee_full_name,
      CAST(AMOUNT AS FLOAT64) as amount,
      EXPN_DSCR as expense_description,
      EXPN_DATE_DATE as expense_date,
      BAKREF_TID as transaction_id,
      FORM_TYPE as form_type,
      CASE
        WHEN UPPER(PAYEE_NAML) LIKE '%ALAMEDA%'
          OR UPPER(PAYEE_NAMF) LIKE '%ALAMEDA%'
          OR UPPER(EXPN_DSCR) LIKE '%ALAMEDA%' THEN TRUE
        ELSE FALSE
      END as is_alameda
    FROM `ca-lobby.ca_lobby.lexp_cd`
    WHERE FILING_ID IS NOT NULL
    '''),

    ('v_filers', '''
    CREATE OR REPLACE VIEW `ca-lobby.ca_lobby.v_filers` AS
    SELECT
      FILER_ID as filer_id,
      CASE WHEN NAML = 'nan' THEN NULL ELSE NAML END as last_name,
      CASE WHEN NAMF = 'nan' THEN NULL ELSE NAMF END as first_name,
      CASE WHEN NAMT = 'nan' THEN NULL ELSE NAMT END as title,
      CASE WHEN NAMS = 'nan' THEN NULL ELSE NAMS END as suffix,
      CASE
        WHEN NAMF IS NULL OR NAMF = 'nan' THEN COALESCE(NULLIF(NAML, 'nan'), '')
        WHEN NAML IS NULL OR NAML = 'nan' THEN COALESCE(NULLIF(NAMF, 'nan'), '')
        ELSE CONCAT(NAMF, ' ', NAML)
      END as full_name,
      FILER_TYPE as filer_type,
      STATUS as status,
      EFFECT_DT_DATE as effective_date,
      XREF_FILER_ID as cross_reference_filer_id,
      CASE
        WHEN UPPER(NAML) LIKE '%ALAMEDA%' OR UPPER(NAMF) LIKE '%ALAMEDA%' THEN TRUE
        ELSE FALSE
      END as is_alameda
    FROM `ca-lobby.ca_lobby.filername_cd`
    WHERE FILER_ID IS NOT NULL
    ''')
]

for i, (name, sql) in enumerate(views_to_fix, 1):
    print(f"\n[{i}/3] Fixing {name}...")
    try:
        client.query(sql).result()
        print(f"    ✓ SUCCESS - 'nan' strings now filtered out")
    except Exception as e:
        print(f"    ✗ FAILED: {str(e)[:200]}")

print("\n" + "="*80)
print("STEP 2: CREATE MONEY FLOW BREAKDOWN VIEWS")
print("="*80)

money_flow_views = [
    ('v_money_flow_payments', '''
    CREATE OR REPLACE VIEW `ca-lobby.ca_lobby.v_money_flow_payments` AS
    SELECT
      p.filing_id,
      p.employer_full_name as from_entity,
      'EMPLOYER/CLIENT' as from_type,
      d.firm_name as to_entity,
      'LOBBYING FIRM' as to_type,
      p.fees_amount as amount,
      'LOBBYING FEES' as payment_type,
      d.period_start_date,
      d.period_end_date,
      d.report_date,
      p.is_alameda,
      p.payment_tier
    FROM `ca-lobby.ca_lobby.v_payments` p
    LEFT JOIN `ca-lobby.ca_lobby.v_disclosures` d ON p.filing_id = d.filing_id
    WHERE p.employer_full_name IS NOT NULL
      AND p.employer_full_name != ''
      AND p.fees_amount > 0
    '''),

    ('v_money_flow_expenditures', '''
    CREATE OR REPLACE VIEW `ca-lobby.ca_lobby.v_money_flow_expenditures` AS
    SELECT
      e.filing_id,
      d.firm_name as from_entity,
      'LOBBYING FIRM' as from_type,
      e.payee_full_name as to_entity,
      'VENDOR/SERVICE PROVIDER' as to_type,
      e.amount,
      e.expense_description as payment_type,
      e.expense_date,
      d.period_start_date,
      d.period_end_date,
      d.report_date,
      e.is_alameda
    FROM `ca-lobby.ca_lobby.v_expenditures` e
    LEFT JOIN `ca-lobby.ca_lobby.v_disclosures` d ON e.filing_id = d.filing_id
    WHERE e.payee_full_name IS NOT NULL
      AND e.payee_full_name != ''
      AND e.amount > 0
    '''),

    ('v_money_flow_alameda_summary', '''
    CREATE OR REPLACE VIEW `ca-lobby.ca_lobby.v_money_flow_alameda_summary` AS
    SELECT
      from_entity,
      to_entity,
      SUM(amount) as total_amount,
      COUNT(*) as number_of_payments,
      MIN(period_start_date) as first_payment_date,
      MAX(period_end_date) as last_payment_date,
      'PAYMENT' as flow_type
    FROM `ca-lobby.ca_lobby.v_money_flow_payments`
    WHERE is_alameda = TRUE
    GROUP BY from_entity, to_entity

    UNION ALL

    SELECT
      from_entity,
      to_entity,
      SUM(amount) as total_amount,
      COUNT(*) as number_of_payments,
      MIN(period_start_date) as first_payment_date,
      MAX(period_end_date) as last_payment_date,
      'EXPENDITURE' as flow_type
    FROM `ca-lobby.ca_lobby.v_money_flow_expenditures`
    WHERE is_alameda = TRUE
    GROUP BY from_entity, to_entity
    ORDER BY total_amount DESC
    '''),

    ('v_alameda_who_paid_who', '''
    CREATE OR REPLACE VIEW `ca-lobby.ca_lobby.v_alameda_who_paid_who` AS
    SELECT
      from_entity as payer,
      to_entity as payee,
      total_amount,
      number_of_payments,
      first_payment_date,
      last_payment_date,
      flow_type
    FROM `ca-lobby.ca_lobby.v_money_flow_alameda_summary`
    ORDER BY total_amount DESC
    ''')
]

for i, (name, sql) in enumerate(money_flow_views, 1):
    print(f"\n[{i}/4] Creating {name}...")
    try:
        client.query(sql).result()
        print(f"    ✓ SUCCESS - Money flow view created")
    except Exception as e:
        print(f"    ✗ FAILED: {str(e)[:200]}")

print("\n" + "="*80)
print("COMPLETE")
print("="*80)
print("\nAll views fixed and money flow views created!")
print("\nNew views available:")
print("  - v_money_flow_payments: Who paid lobbying firms")
print("  - v_money_flow_expenditures: Who firms paid")
print("  - v_money_flow_alameda_summary: Aggregated money flow")
print("  - v_alameda_who_paid_who: Simple who-paid-who breakdown")
