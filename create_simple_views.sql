-- ============================================================================
-- SIMPLE VIEW CREATION FOR EXISTING TABLES
-- ============================================================================
-- Creates views for the 9 actual tables in ca_lobby dataset
-- ============================================================================

-- Clean up any existing views first (optional)
-- DROP VIEW IF EXISTS `ca-lobby.ca_lobby.v_filers`;
-- DROP VIEW IF EXISTS `ca-lobby.ca_lobby.v_disclosures`;
-- DROP VIEW IF EXISTS `ca-lobby.ca_lobby.v_registrations`;
-- DROP VIEW IF EXISTS `ca-lobby.ca_lobby.v_payments`;
-- DROP VIEW IF EXISTS `ca-lobby.ca_lobby.v_expenditures`;
-- DROP VIEW IF EXISTS `ca-lobby.ca_lobby.v_employers`;
-- DROP VIEW IF EXISTS `ca-lobby.ca_lobby.v_campaign_contributions`;
-- DROP VIEW IF EXISTS `ca-lobby.ca_lobby.v_other_payments`;
-- DROP VIEW IF EXISTS `ca-lobby.ca_lobby.v_attachments`;
-- DROP VIEW IF EXISTS `ca-lobby.ca_lobby.v_alameda_filers`;
-- DROP VIEW IF EXISTS `ca-lobby.ca_lobby.v_alameda_activity`;

-- ============================================================================
-- BASE VIEWS - Clean access to each table
-- ============================================================================

-- View 1: Filers (Master Registry)
CREATE OR REPLACE VIEW `ca-lobby.ca_lobby.v_filers` AS
SELECT
  FILER_ID as filer_id,
  NAML as last_name,
  NAMF as first_name,
  CONCAT(COALESCE(NAMF, ''), ' ', COALESCE(NAML, '')) as full_name,
  FILER_TYPE as filer_type,
  STATUS as status,
  EFFECT_DT as effective_date,
  XREF_FILER_ID as cross_reference_filer_id,
  -- Add location flag for Alameda
  CASE
    WHEN UPPER(NAML) LIKE '%ALAMEDA%' OR UPPER(NAMF) LIKE '%ALAMEDA%' THEN TRUE
    ELSE FALSE
  END as is_alameda
FROM `ca-lobby.ca_lobby.filername_cd`
WHERE FILER_ID IS NOT NULL;

-- View 2: Lobby Disclosures (Quarterly Filings)
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
  CASE ENTITY_CD
    WHEN 'FRM' THEN 'Lobbying Firm'
    WHEN 'LEM' THEN 'Lobbyist Employer'
    WHEN 'LCO' THEN 'Lobbying Coalition'
    WHEN 'LBY' THEN 'Individual Lobbyist'
    WHEN 'IND' THEN 'Individual Spender ($5K+)'
    ELSE ENTITY_CD
  END as entity_type,
  CASE
    WHEN ENTITY_CD IN ('LEM', 'LCO', 'IND') THEN 'PURCHASER'
    WHEN ENTITY_CD IN ('FRM', 'LBY') THEN 'PROVIDER'
    ELSE 'OTHER'
  END as organization_role,
  FORM_TYPE as form_type,
  FROM_DATE as period_start_date,
  THRU_DATE as period_end_date,
  RPT_DATE as report_date,
  EXTRACT(YEAR FROM FROM_DATE) as reporting_year,
  EXTRACT(QUARTER FROM FROM_DATE) as reporting_quarter,
  -- Alameda flag
  CASE
    WHEN UPPER(FILER_NAML) LIKE '%ALAMEDA%' OR UPPER(FIRM_NAME) LIKE '%ALAMEDA%' THEN TRUE
    ELSE FALSE
  END as is_alameda
FROM `ca-lobby.ca_lobby.cvr_lobby_disclosure_cd`
WHERE FILING_ID IS NOT NULL;

-- View 3: Registrations
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
  RPT_DATE as report_date,
  -- Alameda flag
  CASE
    WHEN UPPER(FILER_NAML) LIKE '%ALAMEDA%'
      OR UPPER(FIRM_NAME) LIKE '%ALAMEDA%'
      OR UPPER(STMT_FIRM) LIKE '%ALAMEDA%' THEN TRUE
    ELSE FALSE
  END as is_alameda
FROM `ca-lobby.ca_lobby.cvr_registration_cd`
WHERE FILING_ID IS NOT NULL;

-- View 4: Payments (KEY TABLE)
CREATE OR REPLACE VIEW `ca-lobby.ca_lobby.v_payments` AS
SELECT
  FILING_ID as filing_id,
  AMEND_ID as amendment_id,
  LINE_ITEM as line_item,
  EMPLR_NAML as employer_last_name,
  EMPLR_NAMF as employer_first_name,
  CONCAT(COALESCE(EMPLR_NAMF, ''), ' ', COALESCE(EMPLR_NAML, '')) as employer_full_name,
  FEES_AMT as fees_amount,
  REIMB_AMT as reimbursement_amount,
  ADVAN_AMT as advance_amount,
  PER_TOTAL as period_total,
  CUM_TOTAL as cumulative_total,
  FORM_TYPE as form_type,
  -- Payment tier classification
  CASE
    WHEN CAST(PER_TOTAL AS FLOAT64) >= 100000 THEN 'Very High (100K+)'
    WHEN CAST(PER_TOTAL AS FLOAT64) >= 10000 THEN 'High (10K+)'
    WHEN CAST(PER_TOTAL AS FLOAT64) >= 1000 THEN 'Medium (1K+)'
    ELSE 'Low (<1K)'
  END as payment_tier,
  -- Alameda flag
  CASE
    WHEN UPPER(EMPLR_NAML) LIKE '%ALAMEDA%' OR UPPER(EMPLR_NAMF) LIKE '%ALAMEDA%' THEN TRUE
    ELSE FALSE
  END as is_alameda
FROM `ca-lobby.ca_lobby.lpay_cd`
WHERE FILING_ID IS NOT NULL;

-- View 5: Expenditures
CREATE OR REPLACE VIEW `ca-lobby.ca_lobby.v_expenditures` AS
SELECT
  FILING_ID as filing_id,
  AMEND_ID as amendment_id,
  LINE_ITEM as line_item,
  PAYEE_NAML as payee_last_name,
  PAYEE_NAMF as payee_first_name,
  CONCAT(COALESCE(PAYEE_NAMF, ''), ' ', COALESCE(PAYEE_NAML, '')) as payee_full_name,
  AMOUNT as amount,
  EXPN_DSCR as expense_description,
  BAKREF_TID as transaction_id,
  FORM_TYPE as form_type,
  -- Alameda flag
  CASE
    WHEN UPPER(PAYEE_NAML) LIKE '%ALAMEDA%'
      OR UPPER(PAYEE_NAMF) LIKE '%ALAMEDA%'
      OR UPPER(EXPN_DSCR) LIKE '%ALAMEDA%' THEN TRUE
    ELSE FALSE
  END as is_alameda
FROM `ca-lobby.ca_lobby.lexp_cd`
WHERE FILING_ID IS NOT NULL;

-- View 6: Employer Relationships
CREATE OR REPLACE VIEW `ca-lobby.ca_lobby.v_employers` AS
SELECT
  FILING_ID as filing_id,
  AMEND_ID as amendment_id,
  REC_TYPE as record_type,
  FORM_TYPE as form_type
FROM `ca-lobby.ca_lobby.lemp_cd`
WHERE FILING_ID IS NOT NULL;

-- View 7: Campaign Contributions
CREATE OR REPLACE VIEW `ca-lobby.ca_lobby.v_campaign_contributions` AS
SELECT
  FILING_ID as filing_id,
  AMEND_ID as amendment_id,
  CMTE_ID as committee_id,
  AMOUNT as amount,
  CTRIB_DATE as contribution_date,
  EXTRACT(YEAR FROM CTRIB_DATE) as contribution_year
FROM `ca-lobby.ca_lobby.lccm_cd`
WHERE FILING_ID IS NOT NULL;

-- View 8: Other Payments
CREATE OR REPLACE VIEW `ca-lobby.ca_lobby.v_other_payments` AS
SELECT
  FILING_ID as filing_id,
  AMEND_ID as amendment_id,
  AMOUNT as amount,
  BAKREF_TID as transaction_id
FROM `ca-lobby.ca_lobby.loth_cd`
WHERE FILING_ID IS NOT NULL;

-- View 9: Attachments
CREATE OR REPLACE VIEW `ca-lobby.ca_lobby.v_attachments` AS
SELECT
  FILING_ID as filing_id,
  AMEND_ID as amendment_id,
  FORM_TYPE as form_type
FROM `ca-lobby.ca_lobby.latt_cd`
WHERE FILING_ID IS NOT NULL;

-- ============================================================================
-- FILTERED VIEWS - Common filters pre-applied
-- ============================================================================

-- View 10: Alameda Filers Only
CREATE OR REPLACE VIEW `ca-lobby.ca_lobby.v_alameda_filers` AS
SELECT *
FROM `ca-lobby.ca_lobby.v_filers`
WHERE is_alameda = TRUE;

-- View 11: Alameda Activity (All disclosures, payments, expenditures)
CREATE OR REPLACE VIEW `ca-lobby.ca_lobby.v_alameda_activity` AS
SELECT
  f.filer_id,
  f.full_name as organization_name,
  d.filing_id,
  d.period_start_date,
  d.period_end_date,
  d.reporting_year,
  d.reporting_quarter,
  d.entity_type,
  d.organization_role,
  'DISCLOSURE' as activity_type
FROM `ca-lobby.ca_lobby.v_filers` f
INNER JOIN `ca-lobby.ca_lobby.v_disclosures` d
  ON f.filer_id = d.filer_id
WHERE f.is_alameda = TRUE

UNION ALL

SELECT
  NULL as filer_id,
  p.employer_full_name as organization_name,
  p.filing_id,
  NULL as period_start_date,
  NULL as period_end_date,
  NULL as reporting_year,
  NULL as reporting_quarter,
  'Payment' as entity_type,
  'PURCHASER' as organization_role,
  'PAYMENT' as activity_type
FROM `ca-lobby.ca_lobby.v_payments` p
WHERE p.is_alameda = TRUE;

-- ============================================================================
-- Summary
-- ============================================================================
-- Views created: 11
-- - 9 base views (one per table)
-- - 2 filtered views (Alameda-specific)
-- ============================================================================
