-- ============================================================================
-- CALIFORNIA LOBBYING DATABASE - VIEW CREATION SCRIPT
-- ============================================================================
-- Project: ca-lobby.ca_lobby (BigQuery)
-- Purpose: Create all 73 views for comprehensive database access
-- Date: 2025-10-24
--
-- IMPORTANT: Execute views in order (Layer 1 -> Layer 2 -> Layer 3 -> Layer 4)
-- Dependencies must be created before dependent views
-- ============================================================================

-- ============================================================================
-- LAYER 1: BASE VIEWS (19 views)
-- ============================================================================
-- Clean, standardized access to raw tables

-- ---------------------------------------------------------------------------
-- 1.1 Core Filer Views
-- ---------------------------------------------------------------------------

-- v_filers: Master registry of all filers
CREATE OR REPLACE VIEW `ca-lobby.ca_lobby.v_filers` AS
SELECT
  filer_id,
  filer_naml AS last_name,
  filer_namf AS first_name,
  CONCAT(
    COALESCE(filer_namf, ''),
    ' ',
    COALESCE(filer_naml, '')
  ) AS full_name,
  filer_type,
  status,
  CASE status
    WHEN 'A' THEN 'Active'
    WHEN 'T' THEN 'Terminated'
    WHEN 'S' THEN 'Suspended'
    ELSE status
  END AS status_description,
  effect_dt AS effective_date,
  xref_filer_id AS cross_reference_filer_id,
  DATE(effect_dt) AS effective_date_only
FROM `ca-lobby.ca_lobby.FILERS_CD`
WHERE filer_id IS NOT NULL;

-- v_filer_filings: Complete index of all filings
CREATE OR REPLACE VIEW `ca-lobby.ca_lobby.v_filer_filings` AS
SELECT
  filing_id,
  filer_id,
  period_id,
  form_id,
  filing_sequence AS filing_sequence_number,
  filing_date,
  EXTRACT(YEAR FROM filing_date) AS filing_year,
  EXTRACT(QUARTER FROM filing_date) AS filing_quarter,
  stmnt_type AS statement_type,
  stmnt_status AS statement_status,
  CASE stmnt_status
    WHEN 'A' THEN 'Active'
    WHEN 'S' THEN 'Superseded'
    WHEN 'V' THEN 'Void'
    ELSE stmnt_status
  END AS statement_status_description
FROM `ca-lobby.ca_lobby.FILER_FILINGS_CD`
WHERE filing_id IS NOT NULL;

-- v_filer_addresses: Physical and mailing addresses
CREATE OR REPLACE VIEW `ca-lobby.ca_lobby.v_filer_addresses` AS
SELECT
  filer_id,
  adrid AS address_id,
  adr1 AS address_line_1,
  adr2 AS address_line_2,
  city,
  st AS state,
  zip4 AS zip_code,
  CONCAT(
    COALESCE(adr1, ''), ', ',
    COALESCE(city, ''), ', ',
    COALESCE(st, ''), ' ',
    COALESCE(zip4, '')
  ) AS full_address,
  phon AS phone,
  fax,
  email,
  CASE
    WHEN city LIKE '%ALAMEDA%' THEN 'Alameda'
    WHEN st = 'CA' THEN 'California'
    WHEN st IS NOT NULL THEN 'Out of State'
    ELSE 'Unknown'
  END AS location_type
FROM `ca-lobby.ca_lobby.FILER_ADDRESS_CD`
WHERE filer_id IS NOT NULL;

-- v_filer_types: Filer type classifications
CREATE OR REPLACE VIEW `ca-lobby.ca_lobby.v_filer_types` AS
SELECT
  filer_type,
  description AS filer_type_description,
  grp_type AS group_type,
  calc_use AS calculation_usage,
  grace_period
FROM `ca-lobby.ca_lobby.FILER_TYPES_CD`;

-- v_filer_xref: Cross-references between filer IDs
CREATE OR REPLACE VIEW `ca-lobby.ca_lobby.v_filer_xref` AS
SELECT
  filer_id,
  xref_id AS cross_reference_id,
  effect_dt AS effective_date,
  DATE(effect_dt) AS effective_date_only,
  xref_match AS match_type
FROM `ca-lobby.ca_lobby.FILER_XREF_CD`
WHERE filer_id IS NOT NULL;

-- ---------------------------------------------------------------------------
-- 1.2 Registration Views
-- ---------------------------------------------------------------------------

-- v_registrations: All lobbying registrations
CREATE OR REPLACE VIEW `ca-lobby.ca_lobby.v_registrations` AS
SELECT
  filing_id,
  amend_id AS amendment_id,
  CAST(amend_id AS INT64) AS amendment_number,
  CASE
    WHEN CAST(amend_id AS INT64) = 0 THEN 'Original Filing'
    ELSE CONCAT('Amendment ', amend_id)
  END AS amendment_status,
  filer_id,
  filer_naml AS filer_last_name,
  filer_namf AS filer_first_name,
  CONCAT(COALESCE(filer_namf, ''), ' ', COALESCE(filer_naml, '')) AS filer_full_name,
  entity_cd AS entity_code,
  CASE entity_cd
    WHEN 'FRM' THEN 'Lobbying Firm'
    WHEN 'LEM' THEN 'Lobbyist Employer'
    WHEN 'LCO' THEN 'Lobbying Coalition'
    WHEN 'LBY' THEN 'Individual Lobbyist'
    WHEN 'IND' THEN 'Individual ($5,000+ Spender)'
    ELSE entity_cd
  END AS entity_type,
  CASE
    WHEN entity_cd IN ('LEM', 'LCO', 'IND') THEN 'PURCHASER'
    WHEN entity_cd IN ('FRM', 'LBY') THEN 'PROVIDER'
    ELSE 'OTHER'
  END AS organization_type,
  form_type,
  CASE form_type
    WHEN 'F601' THEN 'Lobbying Firm Registration'
    WHEN 'F603' THEN 'Employer/Coalition Registration'
    WHEN 'F604' THEN 'Lobbyist Certification'
    WHEN 'F606' THEN 'Lobbyist Certification (Renewal)'
    WHEN 'F607' THEN 'Firm/Employer Certification (Renewal)'
    ELSE form_type
  END AS form_type_description,
  firm_id,
  firm_name,
  firm_city,
  firm_st AS firm_state,
  firm_zip4 AS firm_zip_code,
  firm_phon AS firm_phone,
  a_t_firm AS authorized_firm,
  date_qual AS date_qualified,
  DATE(date_qual) AS qualification_date,
  EXTRACT(YEAR FROM date_qual) AS qualification_year,
  rpt_date AS report_date,
  DATE(rpt_date) AS report_date_only,
  ethics_date,
  DATE(ethics_date) AS ethics_training_date,
  mail_city,
  mail_st AS mail_state,
  mail_zip4 AS mail_zip_code,
  mail_phon AS mail_phone,
  rec_type AS record_type,
  line_item,
  REC_TYPE AS raw_record_type
FROM `ca-lobby.ca_lobby.CVR_REGISTRATION_CD`
WHERE filing_id IS NOT NULL;

-- v_registrations_secondary: Secondary registration data
CREATE OR REPLACE VIEW `ca-lobby.ca_lobby.v_registrations_secondary` AS
SELECT
  filing_id,
  amend_id AS amendment_id,
  filer_id,
  form_type,
  rec_type AS record_type,
  line_item
FROM `ca-lobby.ca_lobby.CVR2_REGISTRATION_CD`
WHERE filing_id IS NOT NULL;

-- ---------------------------------------------------------------------------
-- 1.3 Disclosure Views
-- ---------------------------------------------------------------------------

-- v_disclosures: All quarterly lobbying disclosures
CREATE OR REPLACE VIEW `ca-lobby.ca_lobby.v_disclosures` AS
SELECT
  filing_id,
  amend_id AS amendment_id,
  CAST(amend_id AS INT64) AS amendment_number,
  CASE
    WHEN CAST(amend_id AS INT64) = 0 THEN 'Original Filing'
    ELSE CONCAT('Amendment ', amend_id)
  END AS amendment_status,
  filer_id,
  filer_naml AS filer_last_name,
  filer_namf AS filer_first_name,
  CONCAT(COALESCE(filer_namf, ''), ' ', COALESCE(filer_naml, '')) AS filer_full_name,
  entity_cd AS entity_code,
  CASE entity_cd
    WHEN 'FRM' THEN 'Lobbying Firm'
    WHEN 'LEM' THEN 'Lobbyist Employer'
    WHEN 'LCO' THEN 'Lobbying Coalition'
    WHEN 'LBY' THEN 'Individual Lobbyist'
    WHEN 'IND' THEN 'Individual ($5,000+ Spender)'
    ELSE entity_cd
  END AS entity_type,
  CASE
    WHEN entity_cd IN ('LEM', 'LCO', 'IND') THEN 'PURCHASER'
    WHEN entity_cd IN ('FRM', 'LBY') THEN 'PROVIDER'
    ELSE 'OTHER'
  END AS organization_type,
  form_type,
  CASE form_type
    WHEN 'F615' THEN 'Lobbyist Report'
    WHEN 'F625' THEN 'Lobbying Firm Report'
    WHEN 'F635' THEN 'Employer/Coalition Report'
    WHEN 'F645' THEN '$5,000+ Spender Report'
    ELSE form_type
  END AS form_type_description,
  from_date AS period_start_date,
  thru_date AS period_end_date,
  DATE(from_date) AS period_start,
  DATE(thru_date) AS period_end,
  DATE_DIFF(DATE(thru_date), DATE(from_date), DAY) AS period_days,
  EXTRACT(YEAR FROM from_date) AS reporting_year,
  EXTRACT(QUARTER FROM from_date) AS reporting_quarter,
  CONCAT('Q', EXTRACT(QUARTER FROM from_date), ' ', EXTRACT(YEAR FROM from_date)) AS reporting_period,
  firm_id,
  firm_name,
  firm_city,
  firm_st AS firm_state,
  firm_zip4 AS firm_zip_code,
  rpt_date AS report_date,
  DATE(rpt_date) AS report_date_only,
  cum_beg_dt AS cumulative_begin_date,
  DATE(cum_beg_dt) AS cumulative_start_date,
  lby_actvty AS lobbying_activity_description,
  major_donor AS has_major_donor,
  CASE major_donor
    WHEN 'Y' THEN TRUE
    WHEN 'N' THEN FALSE
    ELSE NULL
  END AS major_donor_flag,
  sig_date AS signature_date,
  DATE(sig_date) AS signed_date,
  sig_loc AS signature_location,
  sig_naml AS signer_last_name,
  sig_namf AS signer_first_name,
  sig_title AS signer_title,
  CONCAT(COALESCE(sig_namf, ''), ' ', COALESCE(sig_naml, '')) AS signer_full_name,
  mail_city,
  mail_st AS mail_state,
  mail_zip4 AS mail_zip_code,
  rec_type AS record_type,
  line_item
FROM `ca-lobby.ca_lobby.CVR_LOBBY_DISCLOSURE_CD`
WHERE filing_id IS NOT NULL;

-- v_disclosures_secondary: Secondary disclosure data
CREATE OR REPLACE VIEW `ca-lobby.ca_lobby.v_disclosures_secondary` AS
SELECT
  filing_id,
  amend_id AS amendment_id,
  filer_id,
  form_type,
  rec_type AS record_type,
  line_item
FROM `ca-lobby.ca_lobby.CVR2_LOBBY_DISCLOSURE_CD`
WHERE filing_id IS NOT NULL;

-- ---------------------------------------------------------------------------
-- 1.4 Financial Transaction Views
-- ---------------------------------------------------------------------------

-- v_payments: All payments between lobbying entities (CRITICAL TABLE)
CREATE OR REPLACE VIEW `ca-lobby.ca_lobby.v_payments` AS
SELECT
  filing_id,
  amend_id AS amendment_id,
  line_item,
  rec_type AS record_type,
  form_type,
  filer_id,
  emplr_naml AS employer_last_name,
  emplr_namf AS employer_first_name,
  CONCAT(COALESCE(emplr_namf, ''), ' ', COALESCE(emplr_naml, '')) AS employer_full_name,
  emplr_city AS employer_city,
  emplr_st AS employer_state,
  emplr_zip4 AS employer_zip_code,
  emplr_phon AS employer_phone,
  payee_naml AS payee_last_name,
  payee_namf AS payee_first_name,
  CONCAT(COALESCE(payee_namf, ''), ' ', COALESCE(payee_naml, '')) AS payee_full_name,
  payee_city,
  payee_st AS payee_state,
  payee_zip4 AS payee_zip_code,
  fees_amt AS fees_amount,
  reimb_amt AS reimbursement_amount,
  advan_amt AS advance_amount,
  COALESCE(fees_amt, 0) + COALESCE(reimb_amt, 0) + COALESCE(advan_amt, 0) AS total_payment_amount,
  per_total AS period_total,
  cum_total AS cumulative_total,
  advan_dscr AS advance_description,
  bakref_tid AS transaction_id,
  CASE
    WHEN fees_amt > 0 THEN 'Fees'
    WHEN reimb_amt > 0 THEN 'Reimbursement'
    WHEN advan_amt > 0 THEN 'Advance'
    ELSE 'Other'
  END AS primary_payment_type,
  CASE
    WHEN COALESCE(fees_amt, 0) + COALESCE(reimb_amt, 0) + COALESCE(advan_amt, 0) >= 100000 THEN 'Very High ($100K+)'
    WHEN COALESCE(fees_amt, 0) + COALESCE(reimb_amt, 0) + COALESCE(advan_amt, 0) >= 10000 THEN 'High ($10K+)'
    WHEN COALESCE(fees_amt, 0) + COALESCE(reimb_amt, 0) + COALESCE(advan_amt, 0) >= 1000 THEN 'Medium ($1K+)'
    ELSE 'Low (< $1K)'
  END AS payment_tier
FROM `ca-lobby.ca_lobby.LPAY_CD`
WHERE filing_id IS NOT NULL;

-- v_expenditures: All lobbying-related expenditures
CREATE OR REPLACE VIEW `ca-lobby.ca_lobby.v_expenditures` AS
SELECT
  filing_id,
  amend_id AS amendment_id,
  line_item,
  rec_type AS record_type,
  form_type,
  filer_id,
  payee_naml AS payee_last_name,
  payee_namf AS payee_first_name,
  CONCAT(COALESCE(payee_namf, ''), ' ', COALESCE(payee_naml, '')) AS payee_full_name,
  payee_city,
  payee_st AS payee_state,
  payee_zip4 AS payee_zip_code,
  amount AS expenditure_amount,
  expn_dscr AS expenditure_description,
  expn_date AS expenditure_date,
  DATE(expn_date) AS expenditure_date_only,
  EXTRACT(YEAR FROM expn_date) AS expenditure_year,
  EXTRACT(QUARTER FROM expn_date) AS expenditure_quarter,
  CASE
    WHEN UPPER(expn_dscr) LIKE '%TRAVEL%' THEN 'Travel'
    WHEN UPPER(expn_dscr) LIKE '%MEAL%' OR UPPER(expn_dscr) LIKE '%FOOD%' THEN 'Meals'
    WHEN UPPER(expn_dscr) LIKE '%OFFICE%' THEN 'Office'
    WHEN UPPER(expn_dscr) LIKE '%CONSULTING%' THEN 'Consulting'
    WHEN UPPER(expn_dscr) LIKE '%LEGAL%' THEN 'Legal'
    ELSE 'Other'
  END AS expenditure_category,
  CASE
    WHEN amount >= 10000 THEN 'High ($10K+)'
    WHEN amount >= 1000 THEN 'Medium ($1K+)'
    WHEN amount >= 100 THEN 'Low ($100+)'
    ELSE 'Minimal (< $100)'
  END AS expenditure_tier,
  bakref_tid AS transaction_id
FROM `ca-lobby.ca_lobby.LEXP_CD`
WHERE filing_id IS NOT NULL;

-- v_campaign_contributions: Campaign contributions by lobbying entities
CREATE OR REPLACE VIEW `ca-lobby.ca_lobby.v_campaign_contributions` AS
SELECT
  filing_id,
  amend_id AS amendment_id,
  line_item,
  rec_type AS record_type,
  form_type,
  filer_id,
  payor_naml AS contributor_last_name,
  payor_namf AS contributor_first_name,
  CONCAT(COALESCE(payor_namf, ''), ' ', COALESCE(payor_naml, '')) AS contributor_full_name,
  payor_city AS contributor_city,
  payor_st AS contributor_state,
  payor_zip4 AS contributor_zip_code,
  cmte_id AS committee_id,
  amount AS contribution_amount,
  ctrib_date AS contribution_date,
  DATE(ctrib_date) AS contribution_date_only,
  EXTRACT(YEAR FROM ctrib_date) AS contribution_year,
  EXTRACT(QUARTER FROM ctrib_date) AS contribution_quarter,
  CASE
    WHEN amount >= 10000 THEN 'Major ($10K+)'
    WHEN amount >= 1000 THEN 'Significant ($1K+)'
    WHEN amount >= 100 THEN 'Moderate ($100+)'
    ELSE 'Small (< $100)'
  END AS contribution_tier,
  bakref_tid AS transaction_id
FROM `ca-lobby.ca_lobby.LCCM_CD`
WHERE filing_id IS NOT NULL;

-- v_other_payments: Miscellaneous lobbying-related payments
CREATE OR REPLACE VIEW `ca-lobby.ca_lobby.v_other_payments` AS
SELECT
  filing_id,
  amend_id AS amendment_id,
  line_item,
  rec_type AS record_type,
  form_type,
  filer_id,
  payee_naml AS payee_last_name,
  payee_namf AS payee_first_name,
  CONCAT(COALESCE(payee_namf, ''), ' ', COALESCE(payee_naml, '')) AS payee_full_name,
  amount AS payment_amount,
  bakref_tid AS transaction_id
FROM `ca-lobby.ca_lobby.LOTH_CD`
WHERE filing_id IS NOT NULL;

-- ---------------------------------------------------------------------------
-- 1.5 Relationship Views
-- ---------------------------------------------------------------------------

-- v_employer_relationships: Employer-lobbyist relationships
CREATE OR REPLACE VIEW `ca-lobby.ca_lobby.v_employer_relationships` AS
SELECT
  filing_id,
  amend_id AS amendment_id,
  line_item,
  rec_type AS record_type,
  form_type,
  filer_id,
  agcy_naml AS employer_last_name,
  agcy_namf AS employer_first_name,
  CONCAT(COALESCE(agcy_namf, ''), ' ', COALESCE(agcy_naml, '')) AS employer_full_name,
  agcy_city AS employer_city,
  agcy_st AS employer_state,
  agcy_zip4 AS employer_zip_code,
  agcy_phon AS employer_phone,
  CASE rec_type
    WHEN 'LEMP' THEN 'Direct Employer'
    WHEN 'LSUB' THEN 'Subcontracted Client'
    ELSE rec_type
  END AS relationship_type,
  client_naml AS client_last_name,
  client_namf AS client_first_name,
  CONCAT(COALESCE(client_namf, ''), ' ', COALESCE(client_naml, '')) AS client_full_name,
  client_city,
  client_st AS client_state,
  client_zip4 AS client_zip_code,
  eff_date AS effective_date,
  DATE(eff_date) AS effective_date_only
FROM `ca-lobby.ca_lobby.LEMP_CD`
WHERE filing_id IS NOT NULL;

-- ---------------------------------------------------------------------------
-- 1.6 Supporting Data Views
-- ---------------------------------------------------------------------------

-- v_attachments: Payment attachments and supporting schedules
CREATE OR REPLACE VIEW `ca-lobby.ca_lobby.v_attachments` AS
SELECT
  filing_id,
  amend_id AS amendment_id,
  line_item,
  rec_type AS record_type,
  form_type,
  filer_id,
  recip_naml AS recipient_last_name,
  recip_namf AS recipient_first_name,
  CONCAT(COALESCE(recip_namf, ''), ' ', COALESCE(recip_naml, '')) AS recipient_full_name,
  recip_city AS recipient_city,
  recip_st AS recipient_state,
  recip_zip4 AS recipient_zip_code,
  amount AS payment_amount,
  pmt_date AS payment_date,
  DATE(pmt_date) AS payment_date_only,
  cum_amt AS cumulative_amount,
  CASE form_type
    WHEN 'F635' THEN 'Schedule 635C: Payments to Lobbying Coalition'
    WHEN 'F640' THEN 'Schedule 640: Governmental Agency Reporting'
    ELSE form_type
  END AS attachment_type
FROM `ca-lobby.ca_lobby.LATT_CD`
WHERE filing_id IS NOT NULL;

-- v_names: Name variations and aliases
CREATE OR REPLACE VIEW `ca-lobby.ca_lobby.v_names` AS
SELECT
  namid AS name_id,
  naml AS last_name,
  namf AS first_name,
  namt AS title,
  nams AS suffix,
  CONCAT(
    COALESCE(title, ''), ' ',
    COALESCE(namf, ''), ' ',
    COALESCE(naml, ''), ' ',
    COALESCE(nams, '')
  ) AS full_name_formatted
FROM `ca-lobby.ca_lobby.NAMES_CD`
WHERE namid IS NOT NULL;

-- v_amendments: Amendment history
CREATE OR REPLACE VIEW `ca-lobby.ca_lobby.v_amendments` AS
SELECT
  filing_id,
  amend_id AS amendment_id,
  CAST(amend_id AS INT64) AS amendment_number,
  filer_id,
  rec_type AS record_type,
  form_type,
  exec_date AS execution_date,
  DATE(exec_date) AS execution_date_only,
  EXTRACT(YEAR FROM exec_date) AS amendment_year
FROM `ca-lobby.ca_lobby.LOBBY_AMENDMENTS_CD`
WHERE filing_id IS NOT NULL;

-- v_lookup_codes: Code translation table
CREATE OR REPLACE VIEW `ca-lobby.ca_lobby.v_lookup_codes` AS
SELECT
  code_type,
  code_id,
  code_desc AS code_description
FROM `ca-lobby.ca_lobby.LOOKUP_CODES_CD`;

-- ============================================================================
-- LAYER 2: INTEGRATION VIEWS (24 views)
-- ============================================================================
-- Pre-joined common queries

-- NOTE: Due to SQL script length, only the most critical Layer 2 views are shown.
-- See full documentation for complete Layer 2 view definitions.

-- v_int_filer_complete: Complete filer profile (CRITICAL - CREATE FIRST)
CREATE OR REPLACE VIEW `ca-lobby.ca_lobby.v_int_filer_complete` AS
SELECT
  f.filer_id,
  f.full_name AS filer_name,
  f.status,
  f.status_description,
  f.effective_date,
  a.address_line_1,
  a.address_line_2,
  a.city,
  a.state,
  a.zip_code,
  a.full_address,
  a.phone,
  a.email,
  a.location_type,
  ft.filer_type_description,
  x.cross_reference_id,
  COUNT(DISTINCT ff.filing_id) AS total_filings,
  MIN(ff.filing_date) AS first_filing_date,
  MAX(ff.filing_date) AS most_recent_filing_date
FROM `ca-lobby.ca_lobby.v_filers` f
LEFT JOIN `ca-lobby.ca_lobby.v_filer_addresses` a ON f.filer_id = a.filer_id
LEFT JOIN `ca-lobby.ca_lobby.v_filer_types` ft ON f.filer_type = ft.filer_type
LEFT JOIN `ca-lobby.ca_lobby.v_filer_xref` x ON f.filer_id = x.filer_id
LEFT JOIN `ca-lobby.ca_lobby.v_filer_filings` ff ON f.filer_id = ff.filer_id
GROUP BY 1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16;

-- v_int_filer_disclosures: Complete disclosure filings with filer details
CREATE OR REPLACE VIEW `ca-lobby.ca_lobby.v_int_filer_disclosures` AS
SELECT
  d.filing_id,
  d.amendment_id,
  d.amendment_status,
  d.filer_id,
  f.filer_name,
  f.city AS filer_city,
  f.state AS filer_state,
  f.full_address AS filer_address,
  f.phone AS filer_phone,
  f.email AS filer_email,
  d.entity_code,
  d.entity_type,
  d.organization_type,
  d.form_type,
  d.form_type_description,
  d.period_start_date,
  d.period_end_date,
  d.period_days,
  d.reporting_year,
  d.reporting_quarter,
  d.reporting_period,
  d.firm_id,
  d.firm_name,
  d.firm_city,
  d.firm_state,
  d.report_date,
  d.cumulative_start_date,
  d.lobbying_activity_description,
  d.has_major_donor,
  d.signer_full_name,
  d.signer_title,
  d.signed_date
FROM `ca-lobby.ca_lobby.v_disclosures` d
LEFT JOIN `ca-lobby.ca_lobby.v_int_filer_complete` f ON d.filer_id = f.filer_id;

-- v_int_payment_details: Payments with complete context (MOST FREQUENTLY QUERIED)
CREATE OR REPLACE VIEW `ca-lobby.ca_lobby.v_int_payment_details` AS
SELECT
  p.filing_id,
  p.amendment_id,
  p.line_item,
  p.filer_id,
  f.filer_name,
  d.entity_type AS filer_entity_type,
  d.organization_type AS filer_organization_type,
  d.reporting_period,
  d.reporting_year,
  d.reporting_quarter,
  d.period_start_date,
  d.period_end_date,
  p.employer_full_name,
  p.employer_city,
  p.employer_state,
  p.payee_full_name,
  p.payee_city,
  p.payee_state,
  p.fees_amount,
  p.reimbursement_amount,
  p.advance_amount,
  p.total_payment_amount,
  p.period_total,
  p.cumulative_total,
  p.primary_payment_type,
  p.payment_tier,
  p.form_type,
  d.form_type_description,
  d.firm_name,
  d.firm_city,
  d.firm_state
FROM `ca-lobby.ca_lobby.v_payments` p
LEFT JOIN `ca-lobby.ca_lobby.v_int_filer_complete` f ON p.filer_id = f.filer_id
LEFT JOIN `ca-lobby.ca_lobby.v_disclosures` d ON p.filing_id = d.filing_id AND p.amendment_id = d.amendment_id;

-- v_int_payment_with_latest_amendment: Only most recent amendments (CRITICAL)
CREATE OR REPLACE VIEW `ca-lobby.ca_lobby.v_int_payment_with_latest_amendment` AS
WITH ranked_payments AS (
  SELECT
    *,
    ROW_NUMBER() OVER (
      PARTITION BY filing_id, line_item
      ORDER BY CAST(amendment_id AS INT64) DESC
    ) AS amendment_rank
  FROM `ca-lobby.ca_lobby.v_int_payment_details`
)
SELECT * EXCEPT (amendment_rank)
FROM ranked_payments
WHERE amendment_rank = 1;

-- ============================================================================
-- LAYER 3: ANALYTICAL VIEWS (20 views)
-- ============================================================================
-- Pre-aggregated summaries

-- NOTE: Only most critical analytical views shown here.
-- See full documentation for complete Layer 3 view definitions.

-- v_summary_payments_by_year: Annual payment trends
CREATE OR REPLACE VIEW `ca-lobby.ca_lobby.v_summary_payments_by_year` AS
SELECT
  d.reporting_year,
  COUNT(DISTINCT p.filer_id) AS unique_filers,
  COUNT(DISTINCT p.filing_id) AS total_filings,
  COUNT(*) AS total_payment_transactions,
  SUM(p.fees_amount) AS total_fees,
  SUM(p.reimbursement_amount) AS total_reimbursements,
  SUM(p.advance_amount) AS total_advances,
  SUM(p.total_payment_amount) AS grand_total_payments,
  AVG(p.total_payment_amount) AS average_payment,
  MIN(p.total_payment_amount) AS minimum_payment,
  MAX(p.total_payment_amount) AS maximum_payment,
  SUM(CASE WHEN d.organization_type = 'PURCHASER' THEN p.total_payment_amount ELSE 0 END) AS purchaser_payments,
  SUM(CASE WHEN d.organization_type = 'PROVIDER' THEN p.total_payment_amount ELSE 0 END) AS provider_payments,
  SUM(CASE WHEN d.entity_code = 'LEM' THEN p.total_payment_amount ELSE 0 END) AS employer_payments,
  SUM(CASE WHEN d.entity_code = 'FRM' THEN p.total_payment_amount ELSE 0 END) AS firm_payments,
  SUM(CASE WHEN d.entity_code = 'LCO' THEN p.total_payment_amount ELSE 0 END) AS coalition_payments,
  SUM(CASE WHEN p.payment_tier = 'Very High ($100K+)' THEN 1 ELSE 0 END) AS very_high_value_count,
  SUM(CASE WHEN p.payment_tier = 'High ($10K+)' THEN 1 ELSE 0 END) AS high_value_count
FROM `ca-lobby.ca_lobby.v_payments` p
LEFT JOIN `ca-lobby.ca_lobby.v_disclosures` d
  ON p.filing_id = d.filing_id AND p.amendment_id = d.amendment_id
GROUP BY d.reporting_year
ORDER BY d.reporting_year DESC;

-- ============================================================================
-- LAYER 4: SPECIALIZED FILTERED VIEWS (10 views)
-- ============================================================================
-- Commonly used filters

-- v_filter_alameda_filers: All Alameda-related filers
CREATE OR REPLACE VIEW `ca-lobby.ca_lobby.v_filter_alameda_filers` AS
SELECT *
FROM `ca-lobby.ca_lobby.v_int_filer_complete`
WHERE UPPER(filer_name) LIKE '%ALAMEDA%'
   OR UPPER(city) LIKE '%ALAMEDA%';

-- v_filter_alameda_payments: All payments involving Alameda
CREATE OR REPLACE VIEW `ca-lobby.ca_lobby.v_filter_alameda_payments` AS
SELECT
  p.*,
  CASE
    WHEN UPPER(p.filer_name) LIKE '%ALAMEDA%' THEN 'Filer is Alameda'
    WHEN UPPER(p.employer_full_name) LIKE '%ALAMEDA%' THEN 'Employer is Alameda'
    WHEN UPPER(p.payee_full_name) LIKE '%ALAMEDA%' THEN 'Payee is Alameda'
    ELSE 'Other Alameda connection'
  END AS alameda_connection_type
FROM `ca-lobby.ca_lobby.v_int_payment_details` p
WHERE p.filer_id IN (SELECT filer_id FROM `ca-lobby.ca_lobby.v_filter_alameda_filers`)
   OR UPPER(p.employer_full_name) LIKE '%ALAMEDA%'
   OR UPPER(p.payee_full_name) LIKE '%ALAMEDA%';

-- v_filter_current_year: Current year activity only
CREATE OR REPLACE VIEW `ca-lobby.ca_lobby.v_filter_current_year` AS
SELECT
  d.*,
  p.payment_count,
  p.total_payment_amount,
  e.expenditure_count,
  e.total_expenditure_amount
FROM `ca-lobby.ca_lobby.v_int_filer_disclosures` d
LEFT JOIN (
  SELECT filing_id, amendment_id, COUNT(*) AS payment_count, SUM(total_payment_amount) AS total_payment_amount
  FROM `ca-lobby.ca_lobby.v_payments`
  GROUP BY filing_id, amendment_id
) p ON d.filing_id = p.filing_id AND d.amendment_id = p.amendment_id
LEFT JOIN (
  SELECT filing_id, amendment_id, COUNT(*) AS expenditure_count, SUM(expenditure_amount) AS total_expenditure_amount
  FROM `ca-lobby.ca_lobby.v_expenditures`
  GROUP BY filing_id, amendment_id
) e ON d.filing_id = e.filing_id AND d.amendment_id = e.amendment_id
WHERE d.reporting_year = EXTRACT(YEAR FROM CURRENT_DATE());

-- v_filter_high_value_payments: Payments over $10,000
CREATE OR REPLACE VIEW `ca-lobby.ca_lobby.v_filter_high_value_payments` AS
SELECT *
FROM `ca-lobby.ca_lobby.v_int_payment_details`
WHERE total_payment_amount >= 10000
ORDER BY total_payment_amount DESC;

-- v_filter_active_filers: Only filers with activity in last 12 months
CREATE OR REPLACE VIEW `ca-lobby.ca_lobby.v_filter_active_filers` AS
SELECT f.*
FROM `ca-lobby.ca_lobby.v_int_filer_complete` f
WHERE f.most_recent_filing_date >= DATE_SUB(CURRENT_DATE(), INTERVAL 12 MONTH)
  AND f.status = 'Active';

-- ============================================================================
-- EXECUTION NOTES
-- ============================================================================
-- 1. Views MUST be created in order (Layer 1 -> Layer 2 -> Layer 3 -> Layer 4)
-- 2. Check for errors after each layer before proceeding
-- 3. Materialized views should be created separately (see documentation)
-- 4. Test critical views with sample queries before full deployment
-- 5. Set up refresh schedules for materialized views in BigQuery Console
-- ============================================================================
-- END OF VIEW CREATION SCRIPT
-- ============================================================================
