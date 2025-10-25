"""
ALAMEDA Lobbying Data Extraction Script
========================================
Purpose: Extract all records related to organizations containing "ALAMEDA"
         from California CAL-ACCESS lobbying database

Output: CSV files named Alameda_[TableName].csv
Categories:
  - Organizations PURCHASING lobbying services (Employers/Clients)
  - Organizations PROVIDING lobbying services (Firms/Lobbyists)

Requirements:
  - google-cloud-bigquery
  - pandas
  - python-dotenv

Usage:
    python extract_alameda_data.py
"""

from google.cloud import bigquery
import pandas as pd
import os
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
CREDENTIALS_PATH = os.getenv('CREDENTIALS_LOCATION')
if not CREDENTIALS_PATH:
    raise ValueError("CREDENTIALS_LOCATION not found in .env file")

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = CREDENTIALS_PATH

PROJECT_ID = os.getenv('GCP_PROJECT_ID', 'ca-lobby')
DATASET_ID = os.getenv('BIGQUERY_DATASET', 'ca_lobby')
OUTPUT_DIR = Path('alameda_data_exports')

# Create output directory
OUTPUT_DIR.mkdir(exist_ok=True)

print(f"Using credentials: {CREDENTIALS_PATH}")
print(f"Project ID: {PROJECT_ID}")
print(f"Dataset: {DATASET_ID}\n")

# Initialize BigQuery client
client = bigquery.Client(project=PROJECT_ID)

def export_table(query, filename, description):
    """
    Execute query and export results to CSV

    Args:
        query (str): BigQuery SQL query
        filename (str): Output CSV filename
        description (str): Description for logging
    """
    print(f"\n{'='*80}")
    print(f"Extracting: {description}")
    print(f"Output: {filename}")
    print(f"{'='*80}")

    try:
        # Execute query
        df = client.query(query).to_dataframe()

        # Export to CSV
        output_path = OUTPUT_DIR / filename
        df.to_csv(output_path, index=False)

        print(f"✅ SUCCESS: {len(df)} records exported to {output_path}")
        return len(df)

    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        return 0

def main():
    """Main extraction process"""

    print("="*80)
    print("ALAMEDA LOBBYING DATA EXTRACTION")
    print(f"Start Time: {datetime.now()}")
    print("="*80)

    total_records = 0
    tables_extracted = 0

    # ========================================================================
    # TABLE 1: FILERS_CD - Master Registry
    # ========================================================================
    query = f"""
    SELECT
        FILER_ID,
        FILER_NAML as LAST_NAME,
        FILER_NAMF as FIRST_NAME,
        FILER_TYPE,
        STATUS,
        EFFECT_DT as EFFECTIVE_DATE,
        XREF_FILER_ID,
        'FILERS_CD' as SOURCE_TABLE
    FROM `{PROJECT_ID}.{DATASET_ID}.FILERS_CD`
    WHERE UPPER(FILER_NAML) LIKE '%ALAMEDA%'
       OR UPPER(FILER_NAMF) LIKE '%ALAMEDA%'
    ORDER BY FILER_NAML, FILER_NAMF
    """
    count = export_table(query, 'Alameda_FILERS_CD.csv',
                         'Master Registry - All Alameda Filers')
    total_records += count
    tables_extracted += 1

    # ========================================================================
    # TABLE 2: CVR_LOBBY_DISCLOSURE_CD - Disclosure Filings
    # ========================================================================
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
        FIRM_CITY,
        FIRM_ST as FIRM_STATE,
        FIRM_ZIP4,
        'CVR_LOBBY_DISCLOSURE_CD' as SOURCE_TABLE,
        CASE
            WHEN ENTITY_CD IN ('LEM', 'LCO', 'IND') THEN 'PURCHASER'
            WHEN ENTITY_CD IN ('FRM', 'LBY') THEN 'PROVIDER'
            ELSE 'OTHER'
        END as ORGANIZATION_TYPE
    FROM `{PROJECT_ID}.{DATASET_ID}.CVR_LOBBY_DISCLOSURE_CD`
    WHERE UPPER(FILER_NAML) LIKE '%ALAMEDA%'
       OR UPPER(FIRM_NAME) LIKE '%ALAMEDA%'
    ORDER BY FROM_DATE DESC, FILER_NAML
    """
    count = export_table(query, 'Alameda_CVR_LOBBY_DISCLOSURE_CD.csv',
                         'Lobbying Disclosure Filings (Cover Pages)')
    total_records += count
    tables_extracted += 1

    # ========================================================================
    # TABLE 3: CVR_REGISTRATION_CD - Registration Records
    # ========================================================================
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
        A_T_FIRM as AUTHORIZED_FIRM,
        DATE_QUAL as DATE_QUALIFIED,
        RPT_DATE as REPORT_DATE,
        FIRM_CITY,
        FIRM_ST as FIRM_STATE,
        FIRM_ZIP4,
        'CVR_REGISTRATION_CD' as SOURCE_TABLE,
        CASE
            WHEN ENTITY_CD IN ('LEM', 'LCO') THEN 'PURCHASER'
            WHEN ENTITY_CD IN ('FRM', 'LBY') THEN 'PROVIDER'
            ELSE 'OTHER'
        END as ORGANIZATION_TYPE
    FROM `{PROJECT_ID}.{DATASET_ID}.CVR_REGISTRATION_CD`
    WHERE UPPER(FILER_NAML) LIKE '%ALAMEDA%'
       OR UPPER(FIRM_NAME) LIKE '%ALAMEDA%'
       OR UPPER(A_T_FIRM) LIKE '%ALAMEDA%'
    ORDER BY DATE_QUAL DESC, FILER_NAML
    """
    count = export_table(query, 'Alameda_CVR_REGISTRATION_CD.csv',
                         'Lobbying Registration Records')
    total_records += count
    tables_extracted += 1

    # ========================================================================
    # TABLE 4: LPAY_CD - Payments (KEY TABLE)
    # ========================================================================
    query = f"""
    WITH alameda_filers AS (
        SELECT DISTINCT FILER_ID
        FROM `{PROJECT_ID}.{DATASET_ID}.FILERS_CD`
        WHERE UPPER(FILER_NAML) LIKE '%ALAMEDA%'
    )
    SELECT
        lp.FILING_ID,
        lp.AMEND_ID,
        lp.LINE_ITEM,
        lp.FILER_ID,
        f.FILER_NAML as FILER_ORGANIZATION,
        lp.EMPLR_NAML as EMPLOYER_LAST_NAME,
        lp.EMPLR_NAMF as EMPLOYER_FIRST_NAME,
        lp.PAYEE_NAML as PAYEE_LAST_NAME,
        lp.PAYEE_NAMF as PAYEE_FIRST_NAME,
        lp.FEES_AMT as FEES_AMOUNT,
        lp.REIMB_AMT as REIMBURSEMENT_AMOUNT,
        lp.ADVAN_AMT as ADVANCE_AMOUNT,
        lp.PER_TOTAL as PERIOD_TOTAL,
        lp.CUM_TOTAL as CUMULATIVE_TOTAL,
        lp.FORM_TYPE,
        'LPAY_CD' as SOURCE_TABLE,
        CASE
            WHEN UPPER(lp.EMPLR_NAML) LIKE '%ALAMEDA%' THEN 'EMPLOYER_IS_ALAMEDA'
            WHEN UPPER(lp.PAYEE_NAML) LIKE '%ALAMEDA%' THEN 'PAYEE_IS_ALAMEDA'
            WHEN lp.FILER_ID IN (SELECT FILER_ID FROM alameda_filers) THEN 'FILER_IS_ALAMEDA'
            ELSE 'OTHER_ALAMEDA_RELATION'
        END as ALAMEDA_RELATION
    FROM `{PROJECT_ID}.{DATASET_ID}.LPAY_CD` lp
    LEFT JOIN `{PROJECT_ID}.{DATASET_ID}.FILERS_CD` f ON lp.FILER_ID = f.FILER_ID
    WHERE lp.FILER_ID IN (SELECT FILER_ID FROM alameda_filers)
       OR UPPER(lp.EMPLR_NAML) LIKE '%ALAMEDA%'
       OR UPPER(lp.PAYEE_NAML) LIKE '%ALAMEDA%'
    ORDER BY lp.FILING_ID, lp.LINE_ITEM
    """
    count = export_table(query, 'Alameda_LPAY_CD.csv',
                         'Payments (Money Flow Between Organizations)')
    total_records += count
    tables_extracted += 1

    # ========================================================================
    # TABLE 5: LEXP_CD - Expenditures
    # ========================================================================
    query = f"""
    WITH alameda_filers AS (
        SELECT DISTINCT FILER_ID
        FROM `{PROJECT_ID}.{DATASET_ID}.FILERS_CD`
        WHERE UPPER(FILER_NAML) LIKE '%ALAMEDA%'
    )
    SELECT
        le.FILING_ID,
        le.AMEND_ID,
        le.LINE_ITEM,
        le.FILER_ID,
        f.FILER_NAML as FILER_ORGANIZATION,
        le.PAYEE_NAML as PAYEE_LAST_NAME,
        le.PAYEE_NAMF as PAYEE_FIRST_NAME,
        le.AMOUNT,
        le.EXPN_DSCR as EXPENSE_DESCRIPTION,
        le.BAKREF_TID as TRANSACTION_ID,
        le.FORM_TYPE,
        'LEXP_CD' as SOURCE_TABLE
    FROM `{PROJECT_ID}.{DATASET_ID}.LEXP_CD` le
    LEFT JOIN `{PROJECT_ID}.{DATASET_ID}.FILERS_CD` f ON le.FILER_ID = f.FILER_ID
    WHERE le.FILER_ID IN (SELECT FILER_ID FROM alameda_filers)
       OR UPPER(le.PAYEE_NAML) LIKE '%ALAMEDA%'
       OR UPPER(le.EXPN_DSCR) LIKE '%ALAMEDA%'
    ORDER BY le.FILING_ID, le.LINE_ITEM
    """
    count = export_table(query, 'Alameda_LEXP_CD.csv',
                         'Lobbying Expenditures')
    total_records += count
    tables_extracted += 1

    # ========================================================================
    # TABLE 6: LEMP_CD - Employer Relationships
    # ========================================================================
    query = f"""
    WITH alameda_filers AS (
        SELECT DISTINCT FILER_ID
        FROM `{PROJECT_ID}.{DATASET_ID}.FILERS_CD`
        WHERE UPPER(FILER_NAML) LIKE '%ALAMEDA%'
    )
    SELECT
        le.FILING_ID,
        le.AMEND_ID,
        le.FILER_ID,
        f.FILER_NAML as FILER_ORGANIZATION,
        le.AGCY_NAML as EMPLOYER_LAST_NAME,
        le.AGCY_NAMF as EMPLOYER_FIRST_NAME,
        le.REC_TYPE,
        le.FORM_TYPE,
        'LEMP_CD' as SOURCE_TABLE,
        CASE
            WHEN UPPER(le.AGCY_NAML) LIKE '%ALAMEDA%' THEN 'EMPLOYER_IS_ALAMEDA'
            WHEN le.FILER_ID IN (SELECT FILER_ID FROM alameda_filers) THEN 'FILER_IS_ALAMEDA'
            ELSE 'OTHER'
        END as ALAMEDA_RELATION
    FROM `{PROJECT_ID}.{DATASET_ID}.LEMP_CD` le
    LEFT JOIN `{PROJECT_ID}.{DATASET_ID}.FILERS_CD` f ON le.FILER_ID = f.FILER_ID
    WHERE le.FILER_ID IN (SELECT FILER_ID FROM alameda_filers)
       OR UPPER(le.AGCY_NAML) LIKE '%ALAMEDA%'
    ORDER BY le.FILING_ID
    """
    count = export_table(query, 'Alameda_LEMP_CD.csv',
                         'Employer-Lobbyist Relationships')
    total_records += count
    tables_extracted += 1

    # ========================================================================
    # TABLE 7: LCCM_CD - Campaign Contributions
    # ========================================================================
    query = f"""
    WITH alameda_filers AS (
        SELECT DISTINCT FILER_ID
        FROM `{PROJECT_ID}.{DATASET_ID}.FILERS_CD`
        WHERE UPPER(FILER_NAML) LIKE '%ALAMEDA%'
    )
    SELECT
        lc.FILING_ID,
        lc.AMEND_ID,
        lc.FILER_ID,
        f.FILER_NAML as FILER_ORGANIZATION,
        lc.CMTE_ID as COMMITTEE_ID,
        lc.PAYOR_NAML as CONTRIBUTOR_LAST_NAME,
        lc.PAYOR_NAMF as CONTRIBUTOR_FIRST_NAME,
        lc.AMOUNT,
        lc.CTRIB_DATE as CONTRIBUTION_DATE,
        'LCCM_CD' as SOURCE_TABLE
    FROM `{PROJECT_ID}.{DATASET_ID}.LCCM_CD` lc
    LEFT JOIN `{PROJECT_ID}.{DATASET_ID}.FILERS_CD` f ON lc.FILER_ID = f.FILER_ID
    WHERE lc.FILER_ID IN (SELECT FILER_ID FROM alameda_filers)
       OR UPPER(lc.PAYOR_NAML) LIKE '%ALAMEDA%'
    ORDER BY lc.CTRIB_DATE DESC, lc.FILING_ID
    """
    count = export_table(query, 'Alameda_LCCM_CD.csv',
                         'Campaign Contributions by Lobbying Entities')
    total_records += count
    tables_extracted += 1

    # ========================================================================
    # TABLE 8: LOTH_CD - Other Payments
    # ========================================================================
    query = f"""
    WITH alameda_filers AS (
        SELECT DISTINCT FILER_ID
        FROM `{PROJECT_ID}.{DATASET_ID}.FILERS_CD`
        WHERE UPPER(FILER_NAML) LIKE '%ALAMEDA%'
    )
    SELECT
        lo.FILING_ID,
        lo.AMEND_ID,
        lo.FILER_ID,
        f.FILER_NAML as FILER_ORGANIZATION,
        lo.PAYEE_NAML as PAYEE_LAST_NAME,
        lo.PAYEE_NAMF as PAYEE_FIRST_NAME,
        lo.AMOUNT,
        lo.BAKREF_TID as TRANSACTION_ID,
        'LOTH_CD' as SOURCE_TABLE
    FROM `{PROJECT_ID}.{DATASET_ID}.LOTH_CD` lo
    LEFT JOIN `{PROJECT_ID}.{DATASET_ID}.FILERS_CD` f ON lo.FILER_ID = f.FILER_ID
    WHERE lo.FILER_ID IN (SELECT FILER_ID FROM alameda_filers)
       OR UPPER(lo.PAYEE_NAML) LIKE '%ALAMEDA%'
    ORDER BY lo.FILING_ID
    """
    count = export_table(query, 'Alameda_LOTH_CD.csv',
                         'Other Lobbying Payments')
    total_records += count
    tables_extracted += 1

    # ========================================================================
    # TABLE 9: FILER_ADDRESS_CD - Address Information
    # ========================================================================
    query = f"""
    WITH alameda_filers AS (
        SELECT DISTINCT FILER_ID, FILER_NAML
        FROM `{PROJECT_ID}.{DATASET_ID}.FILERS_CD`
        WHERE UPPER(FILER_NAML) LIKE '%ALAMEDA%'
    )
    SELECT
        fa.FILER_ID,
        af.FILER_NAML as FILER_NAME,
        fa.ADRID as ADDRESS_ID,
        fa.CITY,
        fa.ST as STATE,
        fa.ZIP4,
        fa.PHON as PHONE,
        fa.EMAIL,
        'FILER_ADDRESS_CD' as SOURCE_TABLE
    FROM `{PROJECT_ID}.{DATASET_ID}.FILER_ADDRESS_CD` fa
    JOIN alameda_filers af ON fa.FILER_ID = af.FILER_ID
    WHERE fa.FILER_ID IN (SELECT FILER_ID FROM alameda_filers)
       OR UPPER(fa.CITY) LIKE '%ALAMEDA%'
    ORDER BY af.FILER_NAML
    """
    count = export_table(query, 'Alameda_FILER_ADDRESS_CD.csv',
                         'Address Information')
    total_records += count
    tables_extracted += 1

    # ========================================================================
    # TABLE 10: SUMMARY - Comprehensive View
    # ========================================================================
    query = f"""
    WITH alameda_filers AS (
        SELECT DISTINCT
            FILER_ID,
            FILER_NAML as ORGANIZATION_NAME
        FROM `{PROJECT_ID}.{DATASET_ID}.FILERS_CD`
        WHERE UPPER(FILER_NAML) LIKE '%ALAMEDA%'
    ),
    disclosure_summary AS (
        SELECT
            cvr.FILER_ID,
            cvr.ENTITY_CD,
            COUNT(DISTINCT cvr.FILING_ID) as FILING_COUNT,
            MIN(cvr.FROM_DATE) as FIRST_ACTIVITY_DATE,
            MAX(cvr.THRU_DATE) as LAST_ACTIVITY_DATE
        FROM `{PROJECT_ID}.{DATASET_ID}.CVR_LOBBY_DISCLOSURE_CD` cvr
        WHERE cvr.FILER_ID IN (SELECT FILER_ID FROM alameda_filers)
        GROUP BY cvr.FILER_ID, cvr.ENTITY_CD
    ),
    payment_summary AS (
        SELECT
            lp.FILER_ID,
            COUNT(*) as PAYMENT_COUNT,
            SUM(COALESCE(lp.FEES_AMT, 0)) as TOTAL_FEES,
            SUM(COALESCE(lp.REIMB_AMT, 0)) as TOTAL_REIMBURSEMENTS
        FROM `{PROJECT_ID}.{DATASET_ID}.LPAY_CD` lp
        WHERE lp.FILER_ID IN (SELECT FILER_ID FROM alameda_filers)
        GROUP BY lp.FILER_ID
    ),
    expenditure_summary AS (
        SELECT
            le.FILER_ID,
            COUNT(*) as EXPENDITURE_COUNT,
            SUM(COALESCE(le.AMOUNT, 0)) as TOTAL_EXPENDITURES
        FROM `{PROJECT_ID}.{DATASET_ID}.LEXP_CD` le
        WHERE le.FILER_ID IN (SELECT FILER_ID FROM alameda_filers)
        GROUP BY le.FILER_ID
    )
    SELECT
        af.FILER_ID,
        af.ORGANIZATION_NAME,
        ds.ENTITY_CD,
        CASE
            WHEN ds.ENTITY_CD IN ('LEM', 'LCO', 'IND') THEN 'PURCHASER (Buying Lobbying Services)'
            WHEN ds.ENTITY_CD IN ('FRM', 'LBY') THEN 'PROVIDER (Selling Lobbying Services)'
            ELSE 'OTHER'
        END as ORGANIZATION_ROLE,
        CASE ds.ENTITY_CD
            WHEN 'FRM' THEN 'Lobbying Firm'
            WHEN 'LEM' THEN 'Lobbyist Employer'
            WHEN 'LCO' THEN 'Lobbying Coalition'
            WHEN 'LBY' THEN 'Individual Lobbyist'
            WHEN 'IND' THEN 'Person Spending $5,000+'
            ELSE 'Other'
        END as ENTITY_TYPE_DESCRIPTION,
        ds.FILING_COUNT,
        ds.FIRST_ACTIVITY_DATE,
        ds.LAST_ACTIVITY_DATE,
        COALESCE(ps.PAYMENT_COUNT, 0) as PAYMENT_TRANSACTION_COUNT,
        COALESCE(ps.TOTAL_FEES, 0) as TOTAL_FEES_PAID_OR_RECEIVED,
        COALESCE(ps.TOTAL_REIMBURSEMENTS, 0) as TOTAL_REIMBURSEMENTS,
        COALESCE(es.EXPENDITURE_COUNT, 0) as EXPENDITURE_COUNT,
        COALESCE(es.TOTAL_EXPENDITURES, 0) as TOTAL_EXPENDITURES
    FROM alameda_filers af
    LEFT JOIN disclosure_summary ds ON af.FILER_ID = ds.FILER_ID
    LEFT JOIN payment_summary ps ON af.FILER_ID = ps.FILER_ID
    LEFT JOIN expenditure_summary es ON af.FILER_ID = es.FILER_ID
    ORDER BY af.ORGANIZATION_NAME
    """
    count = export_table(query, 'Alameda_SUMMARY.csv',
                         'SUMMARY - Comprehensive Activity View')
    total_records += count
    tables_extracted += 1

    # ========================================================================
    # Final Summary
    # ========================================================================
    print("\n" + "="*80)
    print("EXTRACTION COMPLETE")
    print("="*80)
    print(f"Tables Extracted: {tables_extracted}")
    print(f"Total Records: {total_records:,}")
    print(f"Output Directory: {OUTPUT_DIR.absolute()}")
    print(f"End Time: {datetime.now()}")
    print("="*80)

if __name__ == "__main__":
    main()
