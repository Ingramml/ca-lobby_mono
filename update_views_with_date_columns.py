#!/usr/bin/env python3
"""
Update all views to use the clean DATE columns (*_DATE_DATE) instead of STRING columns
"""

from google.cloud import bigquery
import os
from dotenv import load_dotenv

load_dotenv()
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = os.getenv('CREDENTIALS_LOCATION')
client = bigquery.Client(project='ca-lobby')

print("="*80)
print("UPDATING VIEWS TO USE CLEAN DATE COLUMNS")
print("="*80)

views_to_update = [
    ('v_disclosures', '''
    CREATE OR REPLACE VIEW `ca-lobby.ca_lobby.v_disclosures` AS
    SELECT
      FILING_ID as filing_id,
      AMEND_ID as amendment_id,
      FILER_ID as filer_id,
      FILER_NAML as filer_last_name,
      FILER_NAMF as filer_first_name,
      FIRM_ID as firm_id,
      FIRM_NAME as firm_name,
      ENTITY_CD as entity_code,
      FORM_TYPE as form_type,
      FROM_DATE_DATE as period_start_date,
      THRU_DATE_DATE as period_end_date,
      RPT_DATE_DATE as report_date,
      CASE
        WHEN UPPER(FILER_NAML) LIKE "%ALAMEDA%"
          OR UPPER(FIRM_NAME) LIKE "%ALAMEDA%" THEN TRUE
        ELSE FALSE
      END as is_alameda
    FROM `ca-lobby.ca_lobby.cvr_lobby_disclosure_cd`
    WHERE FILING_ID IS NOT NULL
    '''),
    
    ('v_registrations', '''
    CREATE OR REPLACE VIEW `ca-lobby.ca_lobby.v_registrations` AS
    SELECT
      FILING_ID as filing_id,
      AMEND_ID as amendment_id,
      FILER_ID as filer_id,
      FILER_NAML as filer_last_name,
      FILER_NAMF as filer_first_name,
      ENTITY_CD as entity_code,
      FORM_TYPE as form_type,
      FIRM_NAME as firm_name,
      STMT_FIRM as statement_firm,
      RPT_DATE_DATE as report_date,
      QUAL_DATE_DATE as qualified_date,
      EFF_DATE_DATE as effective_date,
      CASE
        WHEN UPPER(FILER_NAML) LIKE "%ALAMEDA%"
          OR UPPER(FIRM_NAME) LIKE "%ALAMEDA%"
          OR UPPER(STMT_FIRM) LIKE "%ALAMEDA%" THEN TRUE
        ELSE FALSE
      END as is_alameda
    FROM `ca-lobby.ca_lobby.cvr_registration_cd`
    WHERE FILING_ID IS NOT NULL
    '''),
    
    ('v_campaign_contributions', '''
    CREATE OR REPLACE VIEW `ca-lobby.ca_lobby.v_campaign_contributions` AS
    SELECT
      FILING_ID as filing_id,
      AMEND_ID as amendment_id,
      LINE_ITEM as line_item,
      AMOUNT as amount,
      CTRIB_DATE_DATE as contribution_date
    FROM `ca-lobby.ca_lobby.lccm_cd`
    WHERE FILING_ID IS NOT NULL
    '''),
    
    ('v_other_payments', '''
    CREATE OR REPLACE VIEW `ca-lobby.ca_lobby.v_other_payments` AS
    SELECT
      FILING_ID as filing_id,
      AMEND_ID as amendment_id,
      LINE_ITEM as line_item,
      REC_TYPE as record_type,
      FORM_TYPE as form_type,
      TRAN_ID as transaction_id,
      FIRM_NAME as firm_name,
      FIRM_CITY as firm_city,
      FIRM_ST as firm_state,
      SUBJ_NAML as subject_last_name,
      SUBJ_NAMF as subject_first_name,
      CONCAT(COALESCE(SUBJ_NAMF, ""), " ", COALESCE(SUBJ_NAML, "")) as subject_full_name,
      AMOUNT as amount,
      PMT_DATE_DATE as payment_date,
      CASE
        WHEN UPPER(SUBJ_NAML) LIKE "%ALAMEDA%"
          OR UPPER(SUBJ_NAMF) LIKE "%ALAMEDA%"
          OR UPPER(FIRM_NAME) LIKE "%ALAMEDA%"
          OR UPPER(FIRM_CITY) LIKE "%ALAMEDA%" THEN TRUE
        ELSE FALSE
      END as is_alameda
    FROM `ca-lobby.ca_lobby.loth_cd`
    WHERE FILING_ID IS NOT NULL
    '''),
    
    ('v_attachments', '''
    CREATE OR REPLACE VIEW `ca-lobby.ca_lobby.v_attachments` AS
    SELECT
      FILING_ID as filing_id,
      AMEND_ID as amendment_id,
      LINE_ITEM as line_item,
      FORM_TYPE as form_type,
      PMT_DATE_DATE as payment_date,
      CUMBEG_DT_DATE as cumulative_begin_date
    FROM `ca-lobby.ca_lobby.latt_cd`
    WHERE FILING_ID IS NOT NULL
    '''),
    
    ('v_filers', '''
    CREATE OR REPLACE VIEW `ca-lobby.ca_lobby.v_filers` AS
    SELECT
      FILER_ID as filer_id,
      NAML as last_name,
      NAMF as first_name,
      NAMT as title,
      NAMS as suffix,
      CONCAT(COALESCE(NAMF, ""), " ", COALESCE(NAML, "")) as full_name,
      FILER_TYPE as filer_type,
      STATUS as status,
      EFFECT_DT_DATE as effective_date,
      XREF_FILER_ID as cross_reference_filer_id,
      CASE
        WHEN UPPER(NAML) LIKE "%ALAMEDA%" OR UPPER(NAMF) LIKE "%ALAMEDA%" THEN TRUE
        ELSE FALSE
      END as is_alameda
    FROM `ca-lobby.ca_lobby.filername_cd`
    WHERE FILER_ID IS NOT NULL
    '''),
    
    ('v_employers', '''
    CREATE OR REPLACE VIEW `ca-lobby.ca_lobby.v_employers` AS
    SELECT
      FILING_ID as filing_id,
      AMEND_ID as amendment_id,
      LINE_ITEM as line_item,
      REC_TYPE as record_type,
      FORM_TYPE as form_type,
      EFF_DATE_DATE as effective_date
    FROM `ca-lobby.ca_lobby.lemp_cd`
    WHERE FILING_ID IS NOT NULL
    ''')
]

for i, (name, sql) in enumerate(views_to_update, 1):
    print(f"\n[{i}/{len(views_to_update)}] Updating {name}...")
    try:
        client.query(sql).result()
        print(f"    ✓ SUCCESS - Now uses clean DATE columns")
    except Exception as e:
        print(f"    ✗ FAILED: {str(e)[:200]}")

print("\n" + "="*80)
print("COMPLETE")
print("="*80)
print("\nAll views now use clean DATE columns (no time component)")
print("Re-export to get CSV files with clean dates")
