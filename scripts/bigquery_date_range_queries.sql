-- ============================================================================
-- CA LOBBY - BIGQUERY SQL QUERIES FOR DATE RANGES AND SAMPLE DATA
-- ============================================================================
-- Purpose: Extract date ranges and activity data to populate dashboard
-- Target Tables: v_disclosures_alameda, v_payments_alameda, v_filers_alameda
--
-- IMPORTANT NOTE:
-- These Alameda government organizations are CLIENTS (employers) who hire
-- lobbying firms. The disclosures are filed BY THE LOBBYING FIRMS, not by
-- the organizations themselves. Therefore:
-- - Organizations appear in v_filers_alameda (they are registered)
-- - Organizations appear in v_payments_alameda (as employers)
-- - Organizations do NOT appear in v_disclosures_alameda (firms file those)
--
-- To get date ranges, we must:
-- 1. Find payments WHERE organization is the employer
-- 2. Join payments to disclosures via filing_id
-- 3. Extract period_start_date and period_end_date from those disclosures
--
-- NOTE: The v_disclosures_alameda view in the sample CSVs is filtered to
-- only show disclosures filed BY Alameda organizations. In production BigQuery,
-- you need the FULL disclosures table to join with payments.
-- ============================================================================

-- ----------------------------------------------------------------------------
-- QUERY 1: Get Date Ranges for Alameda Organizations
-- ----------------------------------------------------------------------------
-- This query finds the first and last activity dates for each organization
-- by looking at disclosure periods and payment dates

WITH alameda_orgs AS (
  -- List of our 11 Alameda government organizations
  SELECT DISTINCT
    filer_id,
    last_name as organization_name
  FROM `ca-lobby.ca_lobby.v_filers_alameda`
  WHERE
    last_name IN (
      'ALAMEDA COUNTY WATER DISTRICT',
      'ALAMEDA COUNTY WASTE MANAGEMENT AUTHORITY',
      'ALAMEDA ALLIANCE FOR HEALTH',
      'ALAMEDA COUNTY FAIR',
      'ALAMEDA CORRIDOR-EAST CONSTRUCTION AUTHORITY',
      'ALAMEDA CORRIDOR TRANSPORTATION AUTHORITY',
      'ALAMEDA, CITY OF',
      'ALAMEDA COUNTY CONGESTION MANAGEMENT AGENCY',
      'ALAMEDA COUNTY TRANSPORTATION IMPROVEMENT AUTHORITY',
      'ALAMEDA UNIFIED SCHOOL DISTRICT',
      'ALAMEDA COUNTY EMPLOYEES\' RETIREMENT ASSOCIATION'
    )
),

disclosure_dates AS (
  -- Get disclosure date ranges
  SELECT
    d.filer_id,
    MIN(d.period_start_date) as first_disclosure_date,
    MAX(d.period_end_date) as last_disclosure_date,
    COUNT(*) as disclosure_count
  FROM `ca-lobby.ca_lobby.v_disclosures_alameda` d
  INNER JOIN alameda_orgs org ON d.filer_id = org.filer_id
  WHERE d.period_start_date IS NOT NULL
  GROUP BY d.filer_id
),

payment_dates AS (
  -- Get payment date ranges (via filing joins)
  -- NOTE: We must use the FULL disclosures view (v_disclosures_all or base CVR2_LOBBY_DISCLOSURE_CD)
  -- because the payments are filed by lobbying firms, not by Alameda organizations
  -- The v_disclosures_alameda view only contains disclosures WHERE the filer is from Alameda
  SELECT
    org.filer_id,
    MIN(d.period_start_date) as first_payment_period,
    MAX(d.period_end_date) as last_payment_period,
    COUNT(DISTINCT p.filing_id) as payment_filing_count
  FROM alameda_orgs org
  INNER JOIN `ca-lobby.ca_lobby.v_payments_alameda` p
    ON UPPER(p.employer_full_name) LIKE CONCAT('%', org.organization_name, '%')
  INNER JOIN `ca-lobby.ca_lobby.CVR2_LOBBY_DISCLOSURE_CD` d
    ON p.filing_id = d.filing_id
  WHERE d.period_start_date IS NOT NULL
  GROUP BY org.filer_id
)

-- Combine and return results
SELECT
  org.filer_id,
  org.organization_name,
  COALESCE(dd.first_disclosure_date, pd.first_payment_period) as first_activity,
  COALESCE(dd.last_disclosure_date, pd.last_payment_period) as last_activity,
  DATE_DIFF(
    COALESCE(dd.last_disclosure_date, pd.last_payment_period),
    COALESCE(dd.first_disclosure_date, pd.first_payment_period),
    DAY
  ) as activity_span_days,
  COALESCE(dd.disclosure_count, 0) as disclosure_count,
  COALESCE(pd.payment_filing_count, 0) as payment_filing_count
FROM alameda_orgs org
LEFT JOIN disclosure_dates dd ON org.filer_id = dd.filer_id
LEFT JOIN payment_dates pd ON org.filer_id = pd.filer_id
ORDER BY org.organization_name;


-- ----------------------------------------------------------------------------
-- QUERY 2: Get Activity Timeline Data for Dashboard Charts
-- ----------------------------------------------------------------------------
-- This creates a timeline of quarterly activities with spending amounts
-- Start from payments (where org is employer) and join to disclosures for dates

WITH alameda_payments AS (
  SELECT
    p.*,
    d.period_start_date,
    d.period_end_date,
    d.form_type
  FROM `ca-lobby.ca_lobby.v_payments_alameda` p
  INNER JOIN `ca-lobby.ca_lobby.CVR2_LOBBY_DISCLOSURE_CD` d
    ON p.filing_id = d.filing_id
  WHERE
    UPPER(p.employer_full_name) IN (
      'ALAMEDA COUNTY WATER DISTRICT',
      'ALAMEDA COUNTY WASTE MANAGEMENT AUTHORITY',
      'ALAMEDA ALLIANCE FOR HEALTH',
      'ALAMEDA COUNTY FAIR',
      'ALAMEDA CORRIDOR-EAST CONSTRUCTION AUTHORITY',
      'ALAMEDA CORRIDOR TRANSPORTATION AUTHORITY',
      'ALAMEDA, CITY OF',
      'ALAMEDA COUNTY CONGESTION MANAGEMENT AGENCY',
      'ALAMEDA COUNTY TRANSPORTATION IMPROVEMENT AUTHORITY',
      'ALAMEDA UNIFIED SCHOOL DISTRICT',
      'ALAMEDA COUNTY EMPLOYEES\' RETIREMENT ASSOCIATION'
    )
    AND d.period_start_date IS NOT NULL
)

SELECT
  employer_full_name as organization_name,
  period_start_date,
  period_end_date,
  form_type,
  COUNT(DISTINCT filing_id) as payment_filing_count,
  COUNT(*) as payment_line_items,
  SUM(period_total) as total_spending,
  EXTRACT(YEAR FROM period_start_date) as activity_year,
  CONCAT('Q', CAST(EXTRACT(QUARTER FROM period_start_date) AS STRING), ' ', CAST(EXTRACT(YEAR FROM period_start_date) AS STRING)) as quarter
FROM alameda_payments
GROUP BY
  employer_full_name,
  period_start_date,
  period_end_date,
  form_type,
  activity_year,
  quarter
ORDER BY
  employer_full_name,
  period_start_date;


-- ----------------------------------------------------------------------------
-- QUERY 3: Get Filing Details with Payment Information
-- ----------------------------------------------------------------------------
-- This provides complete filing information for the activities list
-- Start from payments and join to full disclosures

SELECT
  d.filing_id,
  d.amendment_id,
  d.filer_id,
  p.employer_full_name as organization_name,
  d.period_start_date,
  d.period_end_date,
  d.report_date,
  d.form_type,
  d.entity_code,
  d.firm_name,
  COUNT(p.line_item) as payment_line_items,
  SUM(p.fees_amount) as total_fees,
  SUM(p.reimbursement_amount) as total_reimbursements,
  SUM(p.period_total) as total_payments
FROM `ca-lobby.ca_lobby.v_payments_alameda` p
INNER JOIN `ca-lobby.ca_lobby.CVR2_LOBBY_DISCLOSURE_CD` d
  ON p.filing_id = d.filing_id
WHERE
  UPPER(p.employer_full_name) IN (
    'ALAMEDA COUNTY WATER DISTRICT',
    'ALAMEDA COUNTY WASTE MANAGEMENT AUTHORITY',
    'ALAMEDA ALLIANCE FOR HEALTH',
    'ALAMEDA COUNTY FAIR',
    'ALAMEDA CORRIDOR-EAST CONSTRUCTION AUTHORITY',
    'ALAMEDA CORRIDOR TRANSPORTATION AUTHORITY',
    'ALAMEDA, CITY OF',
    'ALAMEDA COUNTY CONGESTION MANAGEMENT AGENCY',
    'ALAMEDA COUNTY TRANSPORTATION IMPROVEMENT AUTHORITY',
    'ALAMEDA UNIFIED SCHOOL DISTRICT',
    'ALAMEDA COUNTY EMPLOYEES\' RETIREMENT ASSOCIATION'
  )
  AND d.period_start_date >= '2020-01-01'  -- Last 5 years
GROUP BY
  d.filing_id,
  d.amendment_id,
  d.filer_id,
  p.employer_full_name,
  d.period_start_date,
  d.period_end_date,
  d.report_date,
  d.form_type,
  d.entity_code,
  d.firm_name
ORDER BY
  p.employer_full_name,
  d.period_start_date DESC;


-- ----------------------------------------------------------------------------
-- QUERY 4: Get Top Lobbying Firms (Recipients) by Organization
-- ----------------------------------------------------------------------------
-- This provides data for the Top Recipients component
-- Start from payments and join to full disclosures for firm info and dates

WITH payment_details AS (
  SELECT
    p.employer_full_name as organization_name,
    d.firm_name as lobbying_firm,
    SUM(p.period_total) as total_paid,
    COUNT(DISTINCT p.filing_id) as payment_count,
    MIN(d.period_start_date) as first_payment_date,
    MAX(d.period_end_date) as last_payment_date
  FROM `ca-lobby.ca_lobby.v_payments_alameda` p
  INNER JOIN `ca-lobby.ca_lobby.CVR2_LOBBY_DISCLOSURE_CD` d
    ON p.filing_id = d.filing_id
  WHERE
    UPPER(p.employer_full_name) IN (
      'ALAMEDA COUNTY WATER DISTRICT',
      'ALAMEDA COUNTY WASTE MANAGEMENT AUTHORITY',
      'ALAMEDA ALLIANCE FOR HEALTH',
      'ALAMEDA COUNTY FAIR',
      'ALAMEDA CORRIDOR-EAST CONSTRUCTION AUTHORITY',
      'ALAMEDA CORRIDOR TRANSPORTATION AUTHORITY',
      'ALAMEDA, CITY OF',
      'ALAMEDA COUNTY CONGESTION MANAGEMENT AGENCY',
      'ALAMEDA COUNTY TRANSPORTATION IMPROVEMENT AUTHORITY',
      'ALAMEDA UNIFIED SCHOOL DISTRICT',
      'ALAMEDA COUNTY EMPLOYEES\' RETIREMENT ASSOCIATION'
    )
    AND d.firm_name IS NOT NULL
  GROUP BY
    p.employer_full_name,
    d.firm_name
)

SELECT
  organization_name,
  lobbying_firm,
  total_paid,
  payment_count,
  first_payment_date,
  last_payment_date,
  ROW_NUMBER() OVER (PARTITION BY organization_name ORDER BY total_paid DESC) as firm_rank
FROM payment_details
WHERE total_paid > 0
ORDER BY
  organization_name,
  total_paid DESC;


-- ----------------------------------------------------------------------------
-- QUERY 5: Export Sample Data for Dashboard Testing
-- ----------------------------------------------------------------------------
-- This creates a smaller sample dataset for local testing
-- Start from payments and join to full disclosures

SELECT
  'SAMPLE_DATA_EXPORT' as export_type,
  p.employer_full_name as organization_name,
  d.filing_id,
  d.period_start_date as from_date,
  d.period_end_date as thru_date,
  d.report_date,
  d.form_type,
  d.firm_name,
  p.period_total as amount,
  p.payment_tier,
  CONCAT('Q', CAST(EXTRACT(QUARTER FROM d.period_start_date) AS STRING), ' ', CAST(EXTRACT(YEAR FROM d.period_start_date) AS STRING)) as quarter,
  EXTRACT(YEAR FROM d.period_start_date) as year
FROM `ca-lobby.ca_lobby.v_payments_alameda` p
INNER JOIN `ca-lobby.ca_lobby.CVR2_LOBBY_DISCLOSURE_CD` d
  ON p.filing_id = d.filing_id
WHERE
  UPPER(p.employer_full_name) IN (
    'ALAMEDA COUNTY WATER DISTRICT',
    'ALAMEDA, CITY OF',
    'ALAMEDA ALLIANCE FOR HEALTH'
  )
  AND d.period_start_date >= '2023-01-01'  -- Recent data only
  AND d.period_start_date IS NOT NULL
ORDER BY
  p.employer_full_name,
  d.period_start_date DESC
LIMIT 500;

-- ============================================================================
-- USAGE INSTRUCTIONS
-- ============================================================================
/*
1. Run these queries in BigQuery console or API
2. Export results as CSV
3. Use the CSVs to populate:
   - organizations-summary.json (firstActivity, lastActivity fields)
   - Organization profile JSON files (activities array with date ranges)
   - Dashboard charts (timeline data)

4. To run in BigQuery:
   - Go to https://console.cloud.google.com/bigquery
   - Select project: ca-lobby
   - Paste query and click "Run"
   - Click "Save Results" > "CSV (local file)"

5. Alternative: Use bq command line tool:
   bq query --format=csv --use_legacy_sql=false < query.sql > output.csv
*/
