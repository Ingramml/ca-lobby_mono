#!/usr/bin/env python3
"""
Create the 4 missing views with correct schemas
"""

from google.cloud import bigquery
import os
from dotenv import load_dotenv

load_dotenv()
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = os.getenv('CREDENTIALS_LOCATION')

client = bigquery.Client(project='ca-lobby')

print("="*80)
print("CREATING 4 MISSING VIEWS")
print("="*80)

views = [
    ('v_disclosures', """
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
      FROM_DATE as period_start_date,
      THRU_DATE as period_end_date,
      RPT_DATE as report_date,
      CASE
        WHEN UPPER(FILER_NAML) LIKE '%ALAMEDA%'
          OR UPPER(FIRM_NAME) LIKE '%ALAMEDA%' THEN TRUE
        ELSE FALSE
      END as is_alameda
    FROM `ca-lobby.ca_lobby.cvr_lobby_disclosure_cd`
    WHERE FILING_ID IS NOT NULL
    """),
    
    ('v_campaign_contributions', """
    CREATE OR REPLACE VIEW `ca-lobby.ca_lobby.v_campaign_contributions` AS
    SELECT
      FILING_ID as filing_id,
      AMEND_ID as amendment_id,
      LINE_ITEM as line_item,
      AMOUNT as amount,
      CTRIB_DATE as contribution_date
    FROM `ca-lobby.ca_lobby.lccm_cd`
    WHERE FILING_ID IS NOT NULL
    """),
    
    ('v_other_payments', """
    CREATE OR REPLACE VIEW `ca-lobby.ca_lobby.v_other_payments` AS
    SELECT
      FILING_ID as filing_id,
      AMEND_ID as amendment_id,
      LINE_ITEM as line_item,
      AMOUNT as amount,
      PMT_DATE as payment_date,
      PAYEE_NAML as payee_last_name,
      PAYEE_NAMF as payee_first_name,
      CASE
        WHEN UPPER(PAYEE_NAML) LIKE '%ALAMEDA%' THEN TRUE
        ELSE FALSE
      END as is_alameda
    FROM `ca-lobby.ca_lobby.loth_cd`
    WHERE FILING_ID IS NOT NULL
    """),
    
    ('v_alameda_activity', """
    CREATE OR REPLACE VIEW `ca-lobby.ca_lobby.v_alameda_activity` AS
    SELECT
      f.filer_id,
      f.full_name as organization_name,
      d.filing_id,
      'DISCLOSURE' as activity_type
    FROM `ca-lobby.ca_lobby.v_filers` f
    INNER JOIN `ca-lobby.ca_lobby.v_disclosures` d ON f.filer_id = d.filer_id
    WHERE f.is_alameda = TRUE
    UNION ALL
    SELECT
      CAST(NULL AS STRING) as filer_id,
      p.employer_full_name as organization_name,
      p.filing_id,
      'PAYMENT' as activity_type
    FROM `ca-lobby.ca_lobby.v_payments` p
    WHERE p.is_alameda = TRUE
    """)
]

for i, (name, sql) in enumerate(views, 1):
    print(f"\n[{i}/4] Creating {name}...")
    try:
        client.query(sql).result()
        print(f"    ✓ SUCCESS")
    except Exception as e:
        print(f"    ✗ FAILED: {str(e)[:200]}")

print("\n" + "="*80)
print("COMPLETE")
print("="*80)
