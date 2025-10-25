-- ============================================================================
-- ALAMEDA LOBBYING DATA EXTRACTION SCRIPT
-- ============================================================================
-- Purpose: Extract all records related to organizations containing "ALAMEDA"
-- Output: Each table exported to CSV named Alameda_[TableName].csv
-- Categories: Organizations purchasing lobbying services OR providing lobbying services
-- ============================================================================

-- CATEGORY 1: Organizations PURCHASING lobbying services (Employers/Clients)
-- CATEGORY 2: Organizations PROVIDING lobbying services (Firms/Lobbyists)

-- ============================================================================
-- TABLE 1: FILERS_CD - Master Registry of All Alameda Filers
-- ============================================================================
-- Both purchasers and providers are registered here

EXPORT DATA OPTIONS(
  uri='gs://your-bucket/Alameda_FILERS_CD.csv',
  format='CSV',
  overwrite=true,
  header=true
) AS
SELECT
    FILER_ID,
    FILER_NAML as LAST_NAME,
    FILER_NAMF as FIRST_NAME,
    FILER_TYPE,
    STATUS,
    EFFECT_DT as EFFECTIVE_DATE,
    XREF_FILER_ID,
    'FILERS_CD' as SOURCE_TABLE
FROM FILERS_CD
WHERE UPPER(FILER_NAML) LIKE '%ALAMEDA%'
   OR UPPER(FILER_NAMF) LIKE '%ALAMEDA%'
ORDER BY FILER_NAML, FILER_NAMF;

-- ============================================================================
-- TABLE 2: CVR_LOBBY_DISCLOSURE_CD - Disclosure Filings (Cover Pages)
-- ============================================================================
-- Shows both who filed and what firm they used

EXPORT DATA OPTIONS(
  uri='gs://your-bucket/Alameda_CVR_LOBBY_DISCLOSURE_CD.csv',
  format='CSV',
  overwrite=true,
  header=true
) AS
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
FROM CVR_LOBBY_DISCLOSURE_CD
WHERE UPPER(FILER_NAML) LIKE '%ALAMEDA%'
   OR UPPER(FIRM_NAME) LIKE '%ALAMEDA%'
ORDER BY FROM_DATE DESC, FILER_NAML;

-- ============================================================================
-- TABLE 3: CVR_REGISTRATION_CD - Registration Records
-- ============================================================================
-- Initial registration of firms, employers, and lobbyists

EXPORT DATA OPTIONS(
  uri='gs://your-bucket/Alameda_CVR_REGISTRATION_CD.csv',
  format='CSV',
  overwrite=true,
  header=true
) AS
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
FROM CVR_REGISTRATION_CD
WHERE UPPER(FILER_NAML) LIKE '%ALAMEDA%'
   OR UPPER(FIRM_NAME) LIKE '%ALAMEDA%'
   OR UPPER(A_T_FIRM) LIKE '%ALAMEDA%'
ORDER BY DATE_QUAL DESC, FILER_NAML;

-- ============================================================================
-- TABLE 4: LPAY_CD - Payments (Money flowing between organizations)
-- ============================================================================
-- Key table showing who paid whom for lobbying services

EXPORT DATA OPTIONS(
  uri='gs://your-bucket/Alameda_LPAY_CD.csv',
  format='CSV',
  overwrite=true,
  header=true
) AS
WITH alameda_filers AS (
    SELECT DISTINCT FILER_ID
    FROM FILERS_CD
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
FROM LPAY_CD lp
LEFT JOIN FILERS_CD f ON lp.FILER_ID = f.FILER_ID
WHERE lp.FILER_ID IN (SELECT FILER_ID FROM alameda_filers)
   OR UPPER(lp.EMPLR_NAML) LIKE '%ALAMEDA%'
   OR UPPER(lp.PAYEE_NAML) LIKE '%ALAMEDA%'
ORDER BY lp.FILING_ID, lp.LINE_ITEM;

-- ============================================================================
-- TABLE 5: LEXP_CD - Lobbying Expenditures
-- ============================================================================
-- Money spent on lobbying activities

EXPORT DATA OPTIONS(
  uri='gs://your-bucket/Alameda_LEXP_CD.csv',
  format='CSV',
  overwrite=true,
  header=true
) AS
WITH alameda_filers AS (
    SELECT DISTINCT FILER_ID
    FROM FILERS_CD
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
FROM LEXP_CD le
LEFT JOIN FILERS_CD f ON le.FILER_ID = f.FILER_ID
WHERE le.FILER_ID IN (SELECT FILER_ID FROM alameda_filers)
   OR UPPER(le.PAYEE_NAML) LIKE '%ALAMEDA%'
   OR UPPER(le.EXPN_DSCR) LIKE '%ALAMEDA%'
ORDER BY le.FILING_ID, le.LINE_ITEM;

-- ============================================================================
-- TABLE 6: LEMP_CD - Employer Relationships
-- ============================================================================
-- Shows which employers hired which lobbyists/firms

EXPORT DATA OPTIONS(
  uri='gs://your-bucket/Alameda_LEMP_CD.csv',
  format='CSV',
  overwrite=true,
  header=true
) AS
WITH alameda_filers AS (
    SELECT DISTINCT FILER_ID
    FROM FILERS_CD
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
FROM LEMP_CD le
LEFT JOIN FILERS_CD f ON le.FILER_ID = f.FILER_ID
WHERE le.FILER_ID IN (SELECT FILER_ID FROM alameda_filers)
   OR UPPER(le.AGCY_NAML) LIKE '%ALAMEDA%'
ORDER BY le.FILING_ID;

-- ============================================================================
-- TABLE 7: LCCM_CD - Campaign Contributions by Lobbying Entities
-- ============================================================================
-- Political contributions made by lobbyists/firms

EXPORT DATA OPTIONS(
  uri='gs://your-bucket/Alameda_LCCM_CD.csv',
  format='CSV',
  overwrite=true,
  header=true
) AS
WITH alameda_filers AS (
    SELECT DISTINCT FILER_ID
    FROM FILERS_CD
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
FROM LCCM_CD lc
LEFT JOIN FILERS_CD f ON lc.FILER_ID = f.FILER_ID
WHERE lc.FILER_ID IN (SELECT FILER_ID FROM alameda_filers)
   OR UPPER(lc.PAYOR_NAML) LIKE '%ALAMEDA%'
ORDER BY lc.CTRIB_DATE DESC, lc.FILING_ID;

-- ============================================================================
-- TABLE 8: LOTH_CD - Other Lobbying Payments
-- ============================================================================
-- Miscellaneous payments not in other categories

EXPORT DATA OPTIONS(
  uri='gs://your-bucket/Alameda_LOTH_CD.csv',
  format='CSV',
  overwrite=true,
  header=true
) AS
WITH alameda_filers AS (
    SELECT DISTINCT FILER_ID
    FROM FILERS_CD
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
FROM LOTH_CD lo
LEFT JOIN FILERS_CD f ON lo.FILER_ID = f.FILER_ID
WHERE lo.FILER_ID IN (SELECT FILER_ID FROM alameda_filers)
   OR UPPER(lo.PAYEE_NAML) LIKE '%ALAMEDA%'
ORDER BY lo.FILING_ID;

-- ============================================================================
-- TABLE 9: LATT_CD - Attachments and Supporting Documents
-- ============================================================================
-- Additional payment/activity documentation

EXPORT DATA OPTIONS(
  uri='gs://your-bucket/Alameda_LATT_CD.csv',
  format='CSV',
  overwrite=true,
  header=true
) AS
WITH alameda_filings AS (
    SELECT DISTINCT FILING_ID
    FROM CVR_LOBBY_DISCLOSURE_CD
    WHERE UPPER(FILER_NAML) LIKE '%ALAMEDA%'
       OR UPPER(FIRM_NAME) LIKE '%ALAMEDA%'
)
SELECT
    la.FILING_ID,
    la.AMEND_ID,
    la.LINE_ITEM,
    la.FILER_ID,
    la.REC_TYPE,
    la.FORM_TYPE,
    'LATT_CD' as SOURCE_TABLE
FROM LATT_CD la
WHERE la.FILING_ID IN (SELECT FILING_ID FROM alameda_filings)
ORDER BY la.FILING_ID, la.LINE_ITEM;

-- ============================================================================
-- TABLE 10: FILER_FILINGS_CD - Index of All Filings
-- ============================================================================
-- Links filers to their filing history

EXPORT DATA OPTIONS(
  uri='gs://your-bucket/Alameda_FILER_FILINGS_CD.csv',
  format='CSV',
  overwrite=true,
  header=true
) AS
WITH alameda_filers AS (
    SELECT DISTINCT FILER_ID, FILER_NAML
    FROM FILERS_CD
    WHERE UPPER(FILER_NAML) LIKE '%ALAMEDA%'
)
SELECT
    ff.FILING_ID,
    ff.FILER_ID,
    af.FILER_NAML as FILER_NAME,
    ff.PERIOD_ID,
    ff.FORM_ID,
    'FILER_FILINGS_CD' as SOURCE_TABLE
FROM FILER_FILINGS_CD ff
JOIN alameda_filers af ON ff.FILER_ID = af.FILER_ID
ORDER BY ff.FILING_ID DESC;

-- ============================================================================
-- TABLE 11: FILER_ADDRESS_CD - Address Information
-- ============================================================================
-- Physical addresses for Alameda organizations

EXPORT DATA OPTIONS(
  uri='gs://your-bucket/Alameda_FILER_ADDRESS_CD.csv',
  format='CSV',
  overwrite=true,
  header=true
) AS
WITH alameda_filers AS (
    SELECT DISTINCT FILER_ID, FILER_NAML
    FROM FILERS_CD
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
FROM FILER_ADDRESS_CD fa
JOIN alameda_filers af ON fa.FILER_ID = af.FILER_ID
WHERE fa.FILER_ID IN (SELECT FILER_ID FROM alameda_filers)
   OR UPPER(fa.CITY) LIKE '%ALAMEDA%'
ORDER BY af.FILER_NAML;

-- ============================================================================
-- TABLE 12: NAMES_CD - Name Variations and Aliases
-- ============================================================================
-- Different name formats for Alameda entities

EXPORT DATA OPTIONS(
  uri='gs://your-bucket/Alameda_NAMES_CD.csv',
  format='CSV',
  overwrite=true,
  header=true
) AS
SELECT
    NAMID as NAME_ID,
    NAML as LAST_NAME,
    NAMF as FIRST_NAME,
    NAMT as TITLE,
    NAMS as SUFFIX,
    'NAMES_CD' as SOURCE_TABLE
FROM NAMES_CD
WHERE UPPER(NAML) LIKE '%ALAMEDA%'
   OR UPPER(NAMF) LIKE '%ALAMEDA%'
ORDER BY NAML, NAMF;

-- ============================================================================
-- TABLE 13: LOBBY_AMENDMENTS_CD - Amendment History
-- ============================================================================
-- Tracks changes to filings over time

EXPORT DATA OPTIONS(
  uri='gs://your-bucket/Alameda_LOBBY_AMENDMENTS_CD.csv',
  format='CSV',
  overwrite=true,
  header=true
) AS
WITH alameda_filings AS (
    SELECT DISTINCT FILING_ID
    FROM CVR_REGISTRATION_CD
    WHERE UPPER(FILER_NAML) LIKE '%ALAMEDA%'
       OR UPPER(FIRM_NAME) LIKE '%ALAMEDA%'
)
SELECT
    la.FILING_ID,
    la.AMEND_ID,
    la.FILER_ID,
    la.REC_TYPE,
    la.FORM_TYPE,
    la.EXEC_DATE as EXECUTION_DATE,
    'LOBBY_AMENDMENTS_CD' as SOURCE_TABLE
FROM LOBBY_AMENDMENTS_CD la
WHERE la.FILING_ID IN (SELECT FILING_ID FROM alameda_filings)
ORDER BY la.FILING_ID, la.AMEND_ID;

-- ============================================================================
-- SUMMARY TABLE: Combined View of All Alameda Activities
-- ============================================================================
-- Comprehensive view showing both purchasers and providers

EXPORT DATA OPTIONS(
  uri='gs://your-bucket/Alameda_SUMMARY.csv',
  format='CSV',
  overwrite=true,
  header=true
) AS
WITH alameda_filers AS (
    SELECT DISTINCT
        FILER_ID,
        FILER_NAML as ORGANIZATION_NAME
    FROM FILERS_CD
    WHERE UPPER(FILER_NAML) LIKE '%ALAMEDA%'
),
disclosure_summary AS (
    SELECT
        cvr.FILER_ID,
        cvr.ENTITY_CD,
        COUNT(DISTINCT cvr.FILING_ID) as FILING_COUNT,
        MIN(cvr.FROM_DATE) as FIRST_ACTIVITY_DATE,
        MAX(cvr.THRU_DATE) as LAST_ACTIVITY_DATE
    FROM CVR_LOBBY_DISCLOSURE_CD cvr
    WHERE cvr.FILER_ID IN (SELECT FILER_ID FROM alameda_filers)
    GROUP BY cvr.FILER_ID, cvr.ENTITY_CD
),
payment_summary AS (
    SELECT
        lp.FILER_ID,
        COUNT(*) as PAYMENT_COUNT,
        SUM(COALESCE(lp.FEES_AMT, 0)) as TOTAL_FEES,
        SUM(COALESCE(lp.REIMB_AMT, 0)) as TOTAL_REIMBURSEMENTS
    FROM LPAY_CD lp
    WHERE lp.FILER_ID IN (SELECT FILER_ID FROM alameda_filers)
    GROUP BY lp.FILER_ID
),
expenditure_summary AS (
    SELECT
        le.FILER_ID,
        COUNT(*) as EXPENDITURE_COUNT,
        SUM(COALESCE(le.AMOUNT, 0)) as TOTAL_EXPENDITURES
    FROM LEXP_CD le
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
ORDER BY af.ORGANIZATION_NAME;

-- ============================================================================
-- END OF EXTRACTION SCRIPT
-- ============================================================================
-- Total Tables Extracted: 14 (13 detail tables + 1 summary)
-- Naming Convention: Alameda_[TableName].csv
-- All exports include SOURCE_TABLE column for traceability
-- ============================================================================
