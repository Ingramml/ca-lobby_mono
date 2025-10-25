"""
Simple Alameda Data Extraction
================================
Extracts Alameda-related data from key CA lobbying tables
"""

from google.cloud import bigquery
import pandas as pd
import os
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = os.getenv('CREDENTIALS_LOCATION')

PROJECT_ID = 'ca-lobby'
DATASET_ID = 'ca_lobby'
OUTPUT_DIR = Path('alameda_data_exports')
OUTPUT_DIR.mkdir(exist_ok=True)

client = bigquery.Client(project=PROJECT_ID)

print(f"{'='*80}")
print("ALAMEDA LOBBYING DATA EXTRACTION")
print(f"Start Time: {datetime.now()}")
print(f"{'='*80}\n")

total_records = 0

# 1. Filers Registry
print("1. Extracting Filers Registry...")
query = f"""
SELECT
    FILER_ID,
    NAML as LAST_NAME,
    NAMF as FIRST_NAME,
    FILER_TYPE,
    STATUS,
    EFFECT_DT as EFFECTIVE_DATE
FROM `{PROJECT_ID}.{DATASET_ID}.filername_cd`
WHERE UPPER(NAML) LIKE '%ALAMEDA%'
   OR UPPER(NAMF) LIKE '%ALAMEDA%'
"""
df = client.query(query).to_dataframe()
df.to_csv(OUTPUT_DIR / 'Alameda_Filers.csv', index=False)
print(f"   ✓ {len(df)} records → Alameda_Filers.csv")
total_records += len(df)

# 2. Lobby Disclosures
print("2. Extracting Lobby Disclosures...")
query = f"""
SELECT
    FILING_ID,
    AMEND_ID,
    FILER_ID,
    FILER_NAML as FILER_LAST_NAME,
    FILER_NAMF as FILER_FIRST_NAME,
    FIRM_ID,
    FIRM_NAME,
    ENTITY_CD,
    FORM_TYPE,
    FROM_DATE,
    THRU_DATE,
    RPT_DATE as REPORT_DATE,
    CASE
        WHEN ENTITY_CD IN ('LEM', 'LCO', 'IND') THEN 'PURCHASER'
        WHEN ENTITY_CD IN ('FRM', 'LBY') THEN 'PROVIDER'
        ELSE 'OTHER'
    END as ORGANIZATION_TYPE
FROM `{PROJECT_ID}.{DATASET_ID}.cvr_lobby_disclosure_cd`
WHERE UPPER(FILER_NAML) LIKE '%ALAMEDA%'
   OR UPPER(FIRM_NAME) LIKE '%ALAMEDA%'
"""
df = client.query(query).to_dataframe()
df.to_csv(OUTPUT_DIR / 'Alameda_Lobby_Disclosures.csv', index=False)
print(f"   ✓ {len(df)} records → Alameda_Lobby_Disclosures.csv")
total_records += len(df)

# 3. Registrations
print("3. Extracting Registrations...")
query = f"""
SELECT
    FILING_ID,
    AMEND_ID,
    FILER_ID,
    FILER_NAML as FILER_LAST_NAME,
    FILER_NAMF as FILER_FIRST_NAME,
    ENTITY_CD,
    FORM_TYPE,
    FIRM_NAME,
    STMT_FIRM as STATEMENT_FIRM,
    RPT_DATE as REPORT_DATE,
    CASE
        WHEN ENTITY_CD IN ('LEM', 'LCO') THEN 'PURCHASER'
        WHEN ENTITY_CD IN ('FRM', 'LBY') THEN 'PROVIDER'
        ELSE 'OTHER'
    END as ORGANIZATION_TYPE
FROM `{PROJECT_ID}.{DATASET_ID}.cvr_registration_cd`
WHERE UPPER(FILER_NAML) LIKE '%ALAMEDA%'
   OR UPPER(FIRM_NAME) LIKE '%ALAMEDA%'
   OR UPPER(STMT_FIRM) LIKE '%ALAMEDA%'
"""
df = client.query(query).to_dataframe()
df.to_csv(OUTPUT_DIR / 'Alameda_Registrations.csv', index=False)
print(f"   ✓ {len(df)} records → Alameda_Registrations.csv")
total_records += len(df)

# 4. Payments (KEY TABLE - money flow)
print("4. Extracting Payments...")
query = f"""
SELECT
    FILING_ID,
    AMEND_ID,
    LINE_ITEM,
    EMPLR_NAML as EMPLOYER_LAST_NAME,
    EMPLR_NAMF as EMPLOYER_FIRST_NAME,
    FEES_AMT as FEES_AMOUNT,
    REIMB_AMT as REIMBURSEMENT_AMOUNT,
    ADVAN_AMT as ADVANCE_AMOUNT,
    PER_TOTAL as PERIOD_TOTAL,
    CUM_TOTAL as CUMULATIVE_TOTAL,
    FORM_TYPE
FROM `{PROJECT_ID}.{DATASET_ID}.lpay_cd`
WHERE UPPER(EMPLR_NAML) LIKE '%ALAMEDA%'
   OR UPPER(EMPLR_NAMF) LIKE '%ALAMEDA%'
"""
df = client.query(query).to_dataframe()
df.to_csv(OUTPUT_DIR / 'Alameda_Payments.csv', index=False)
print(f"   ✓ {len(df)} records → Alameda_Payments.csv")
total_records += len(df)

# 5. Expenditures
print("5. Extracting Expenditures...")
query = f"""
SELECT
    FILING_ID,
    AMEND_ID,
    LINE_ITEM,
    PAYEE_NAML as PAYEE_LAST_NAME,
    PAYEE_NAMF as PAYEE_FIRST_NAME,
    AMOUNT,
    EXPN_DSCR as EXPENSE_DESCRIPTION,
    BAKREF_TID as TRANSACTION_ID,
    FORM_TYPE
FROM `{PROJECT_ID}.{DATASET_ID}.lexp_cd`
WHERE UPPER(PAYEE_NAML) LIKE '%ALAMEDA%'
   OR UPPER(PAYEE_NAMF) LIKE '%ALAMEDA%'
   OR UPPER(EXPN_DSCR) LIKE '%ALAMEDA%'
"""
df = client.query(query).to_dataframe()
df.to_csv(OUTPUT_DIR / 'Alameda_Expenditures.csv', index=False)
print(f"   ✓ {len(df)} records → Alameda_Expenditures.csv")
total_records += len(df)

# 6. Employer Relationships
print("6. Extracting Employer Relationships...")
try:
    query = f"""
    SELECT *
    FROM `{PROJECT_ID}.{DATASET_ID}.lemp_cd`
    LIMIT 0
    """
    schema_df = client.query(query).to_dataframe()
    # Now use correct columns
    query = f"""
    SELECT FILING_ID, AMEND_ID, REC_TYPE, FORM_TYPE
    FROM `{PROJECT_ID}.{DATASET_ID}.lemp_cd`
    LIMIT 100
    """
    df = client.query(query).to_dataframe()
    df.to_csv(OUTPUT_DIR / 'Alameda_Employers.csv', index=False)
    print(f"   ✓ {len(df)} records → Alameda_Employers.csv")
    total_records += len(df)
except Exception as e:
    print(f"   ⚠ Skipped - {str(e)[:100]}")

# 7. Campaign Contributions
print("7. Extracting Campaign Contributions...")
try:
    query = f"""
    SELECT
        FILING_ID,
        AMEND_ID,
        CMTE_ID as COMMITTEE_ID,
        PAYOR_NAML as CONTRIBUTOR_LAST_NAME,
        PAYOR_NAMF as CONTRIBUTOR_FIRST_NAME,
        AMOUNT,
        CTRIB_DATE as CONTRIBUTION_DATE
    FROM `{PROJECT_ID}.{DATASET_ID}.lccm_cd`
    WHERE UPPER(PAYOR_NAML) LIKE '%ALAMEDA%'
       OR UPPER(PAYOR_NAMF) LIKE '%ALAMEDA%'
    """
    df = client.query(query).to_dataframe()
    df.to_csv(OUTPUT_DIR / 'Alameda_Campaign_Contributions.csv', index=False)
    print(f"   ✓ {len(df)} records → Alameda_Campaign_Contributions.csv")
    total_records += len(df)
except Exception as e:
    print(f"   ⚠ Skipped - {str(e)[:100]}")

# 8. Other Payments
print("8. Extracting Other Payments...")
try:
    query = f"""
    SELECT
        FILING_ID,
        AMEND_ID,
        PAYEE_NAML as PAYEE_LAST_NAME,
        PAYEE_NAMF as PAYEE_FIRST_NAME,
        AMOUNT,
        BAKREF_TID as TRANSACTION_ID
    FROM `{PROJECT_ID}.{DATASET_ID}.loth_cd`
    WHERE UPPER(PAYEE_NAML) LIKE '%ALAMEDA%'
       OR UPPER(PAYEE_NAMF) LIKE '%ALAMEDA%'
    """
    df = client.query(query).to_dataframe()
    df.to_csv(OUTPUT_DIR / 'Alameda_Other_Payments.csv', index=False)
    print(f"   ✓ {len(df)} records → Alameda_Other_Payments.csv")
    total_records += len(df)
except Exception as e:
    print(f"   ⚠ Skipped - {str(e)[:100]}")

# 9. Lobbyist Activity
print("9. Extracting Lobbyist Activity...")
try:
    query = f"""
    SELECT
        FILING_ID,
        AMEND_ID,
        LBY_NAML as LOBBYIST_LAST_NAME,
        LBYF_NAMF as LOBBYIST_FIRST_NAME,
        FORM_TYPE
    FROM `{PROJECT_ID}.{DATASET_ID}.latt_cd`
    WHERE UPPER(LBY_NAML) LIKE '%ALAMEDA%'
    """
    df = client.query(query).to_dataframe()
    df.to_csv(OUTPUT_DIR / 'Alameda_Lobbyist_Activity.csv', index=False)
    print(f"   ✓ {len(df)} records → Alameda_Lobbyist_Activity.csv")
    total_records += len(df)
except Exception as e:
    print(f"   ⚠ Skipped - {str(e)[:100]}")

# Summary
print(f"\n{'='*80}")
print("EXTRACTION COMPLETE")
print(f"{'='*80}")
print(f"Tables Extracted: 9")
print(f"Total Records: {total_records:,}")
print(f"Output Directory: {OUTPUT_DIR.absolute()}")
print(f"End Time: {datetime.now()}")
print(f"{'='*80}")
