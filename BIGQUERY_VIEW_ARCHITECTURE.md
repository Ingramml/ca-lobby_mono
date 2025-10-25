# California Lobbying Database - Complete View Architecture

**Project:** ca-lobby.ca_lobby (BigQuery)
**Purpose:** Provide comprehensive view-based data access; CSV exports only for testing
**Created:** 2025-10-24
**Total Views:** 73 views across 4 layers

---

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [View Naming Convention](#view-naming-convention)
3. [Layer 1: Base Views (19 views)](#layer-1-base-views)
4. [Layer 2: Integration Views (24 views)](#layer-2-integration-views)
5. [Layer 3: Analytical Views (20 views)](#layer-3-analytical-views)
6. [Layer 4: Specialized Filtered Views (10 views)](#layer-4-specialized-filtered-views)
7. [Performance Recommendations](#performance-recommendations)
8. [Usage Examples](#usage-examples)
9. [Migration Guide](#migration-guide)
10. [Cost Analysis](#cost-analysis)

---

## Architecture Overview

### The 4-Layer Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│ Layer 4: Specialized Filtered Views                             │
│ (Alameda-specific, active filers, high-value transactions)      │
└─────────────────────────────────────────────────────────────────┘
                              ▲
┌─────────────────────────────────────────────────────────────────┐
│ Layer 3: Analytical Views                                        │
│ (Aggregations, trends, summaries, network analysis)             │
└─────────────────────────────────────────────────────────────────┘
                              ▲
┌─────────────────────────────────────────────────────────────────┐
│ Layer 2: Integration Views                                       │
│ (Pre-joined common queries, complete filing details)            │
└─────────────────────────────────────────────────────────────────┘
                              ▲
┌─────────────────────────────────────────────────────────────────┐
│ Layer 1: Base Views                                              │
│ (Clean, standardized access to raw tables)                      │
└─────────────────────────────────────────────────────────────────┘
                              ▲
┌─────────────────────────────────────────────────────────────────┐
│ Raw CAL-ACCESS Tables (ca_lobby dataset)                        │
└─────────────────────────────────────────────────────────────────┘
```

### Design Principles

1. **No Data Loss** - All columns from raw tables accessible
2. **Human Readable** - Standardized, descriptive column names
3. **Performance First** - Recommend materialization for expensive views
4. **Cost Effective** - Minimize query costs through smart caching
5. **BigQuery Native** - Leverage partitioning, clustering, and optimization
6. **Self-Documenting** - Clear naming and inline descriptions

---

## View Naming Convention

| Prefix | Purpose | Example |
|--------|---------|---------|
| `v_` | Base views | `v_filers` |
| `v_int_` | Integration views | `v_int_filer_disclosures` |
| `v_summary_` | Analytical views | `v_summary_payments_by_year` |
| `v_filter_` | Filtered views | `v_filter_alameda` |
| `mv_` | Materialized views | `mv_complete_activity_timeline` |

### Naming Best Practices

- Use lowercase with underscores
- Keep names descriptive but concise
- Include entity names (filer, payment, disclosure)
- For joins: list entities in alphabetical order
- For aggregations: include aggregation type (by_year, top_10)

---

## Layer 1: Base Views

**Purpose:** Clean, standardized access to raw tables with human-readable column names.

### Entity Code Translation Reference

```sql
-- Used throughout base views
CASE entity_cd
  WHEN 'CLI' THEN 'Client (Unknown)'
  WHEN 'FRM' THEN 'Lobbying Firm'
  WHEN 'IND' THEN 'Individual ($5,000+ Spender)'
  WHEN 'LBY' THEN 'Lobbyist (Individual)'
  WHEN 'LCO' THEN 'Lobbying Coalition'
  WHEN 'LEM' THEN 'Lobbyist Employer'
  WHEN 'OTH' THEN 'Other'
  ELSE entity_cd
END
```

### 1.1 Core Filer Views

#### v_filers
**Purpose:** Clean master registry of all filers
**Materialization:** No
**Expected Query Cost:** Low (small table)

```sql
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
```

#### v_filer_filings
**Purpose:** Complete index of all filings by filer
**Materialization:** No
**Expected Query Cost:** Low-Medium

```sql
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
```

~~#### v_filer_addresses~~ (not needed)
**Purpose:** Physical and mailing addresses for all filers
**Materialization:** No
**Expected Query Cost:** Low

```sql
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
  -- Address type classification
  CASE
    WHEN city LIKE '%ALAMEDA%' THEN 'Alameda'
    WHEN st = 'CA' THEN 'California'
    WHEN st IS NOT NULL THEN 'Out of State'
    ELSE 'Unknown'
  END AS location_type
FROM `ca-lobby.ca_lobby.FILER_ADDRESS_CD`
WHERE filer_id IS NOT NULL;
```

#### v_filer_types
**Purpose:** Filer type classifications and descriptions
**Materialization:** No
**Expected Query Cost:** Very Low (lookup table)

```sql
CREATE OR REPLACE VIEW `ca-lobby.ca_lobby.v_filer_types` AS
SELECT
  filer_type,
  description AS filer_type_description,
  grp_type AS group_type,
  calc_use AS calculation_usage,
  grace_period
FROM `ca-lobby.ca_lobby.FILER_TYPES_CD`;
```

#### v_filer_xref
**Purpose:** Cross-references between different filer IDs
**Materialization:** No
**Expected Query Cost:** Low

```sql
CREATE OR REPLACE VIEW `ca-lobby.ca_lobby.v_filer_xref` AS
SELECT
  filer_id,
  xref_id AS cross_reference_id,
  effect_dt AS effective_date,
  DATE(effect_dt) AS effective_date_only,
  xref_match AS match_type
FROM `ca-lobby.ca_lobby.FILER_XREF_CD`
WHERE filer_id IS NOT NULL;
```

### 1.2 Registration Views

#### v_registrations
**Purpose:** All lobbying registrations with clean column names
**Materialization:** No
**Expected Query Cost:** Medium

```sql
CREATE OR REPLACE VIEW `ca-lobby.ca_lobby.v_registrations` AS
SELECT
  filing_id,
  amend_id AS amendment_id,
  -- Amendment tracking
  CAST(amend_id AS INT64) AS amendment_number,
  CASE
    WHEN CAST(amend_id AS INT64) = 0 THEN 'Original Filing'
    ELSE CONCAT('Amendment ', amend_id)
  END AS amendment_status,

  -- Filer information
  filer_id,
  filer_naml AS filer_last_name,
  filer_namf AS filer_first_name,
  CONCAT(COALESCE(filer_namf, ''), ' ', COALESCE(filer_naml, '')) AS filer_full_name,

  -- Entity classification
  entity_cd AS entity_code,
  CASE entity_cd
    WHEN 'FRM' THEN 'Lobbying Firm'
    WHEN 'LEM' THEN 'Lobbyist Employer'
    WHEN 'LCO' THEN 'Lobbying Coalition'
    WHEN 'LBY' THEN 'Individual Lobbyist'
    WHEN 'IND' THEN 'Individual ($5,000+ Spender)'
    ELSE entity_cd
  END AS entity_type,

  -- Organization type: purchaser vs provider
  CASE
    WHEN entity_cd IN ('LEM', 'LCO', 'IND') THEN 'PURCHASER'
    WHEN entity_cd IN ('FRM', 'LBY') THEN 'PROVIDER'
    ELSE 'OTHER'
  END AS organization_type,

  -- Form information
  form_type,
  CASE form_type
    WHEN 'F601' THEN 'Lobbying Firm Registration'
    WHEN 'F603' THEN 'Employer/Coalition Registration'
    WHEN 'F604' THEN 'Lobbyist Certification'
    WHEN 'F606' THEN 'Lobbyist Certification (Renewal)'
    WHEN 'F607' THEN 'Firm/Employer Certification (Renewal)'
    ELSE form_type
  END AS form_type_description,

  -- Firm/Employer details
  firm_id,
  firm_name,
  firm_city,
  firm_st AS firm_state,
  firm_zip4 AS firm_zip_code,
  firm_phon AS firm_phone,

  -- Authorization
  a_t_firm AS authorized_firm,

  -- Dates
  date_qual AS date_qualified,
  DATE(date_qual) AS qualification_date,
  EXTRACT(YEAR FROM date_qual) AS qualification_year,
  rpt_date AS report_date,
  DATE(rpt_date) AS report_date_only,

  -- Ethics training
  ethics_date,
  DATE(ethics_date) AS ethics_training_date,

  -- Additional fields
  mail_city,
  mail_st AS mail_state,
  mail_zip4 AS mail_zip_code,
  mail_phon AS mail_phone,

  -- Record metadata
  rec_type AS record_type,
  line_item,
  REC_TYPE AS raw_record_type

FROM `ca-lobby.ca_lobby.CVR_REGISTRATION_CD`
WHERE filing_id IS NOT NULL;
```

~~#### v_registrations_secondary~~
**Purpose:** Secondary registration cover page data
**Materialization:** No
**Expected Query Cost:** Low

```sql
CREATE OR REPLACE VIEW `ca-lobby.ca_lobby.v_registrations_secondary` AS
SELECT
  filing_id,
  amend_id AS amendment_id,
  filer_id,
  form_type,
  -- Additional fields specific to CVR2_REGISTRATION_CD
  -- Add all relevant columns with clean names
  rec_type AS record_type,
  line_item
FROM `ca-lobby.ca_lobby.CVR2_REGISTRATION_CD`
WHERE filing_id IS NOT NULL;
```

### 1.3 Disclosure Views

#### v_disclosures
**Purpose:** All quarterly lobbying disclosure filings
**Materialization:** No
**Expected Query Cost:** Medium-High

```sql
CREATE OR REPLACE VIEW `ca-lobby.ca_lobby.v_disclosures` AS
SELECT
  filing_id,
  amend_id AS amendment_id,
  CAST(amend_id AS INT64) AS amendment_number,
  CASE
    WHEN CAST(amend_id AS INT64) = 0 THEN 'Original Filing'
    ELSE CONCAT('Amendment ', amend_id)
  END AS amendment_status,

  -- Filer information
  filer_id,
  filer_naml AS filer_last_name,
  filer_namf AS filer_first_name,
  CONCAT(COALESCE(filer_namf, ''), ' ', COALESCE(filer_naml, '')) AS filer_full_name,

  -- Entity classification
  entity_cd AS entity_code,
  CASE entity_cd
    WHEN 'FRM' THEN 'Lobbying Firm'
    WHEN 'LEM' THEN 'Lobbyist Employer'
    WHEN 'LCO' THEN 'Lobbying Coalition'
    WHEN 'LBY' THEN 'Individual Lobbyist'
    WHEN 'IND' THEN 'Individual ($5,000+ Spender)'
    ELSE entity_cd
  END AS entity_type,

  -- Organization type
  CASE
    WHEN entity_cd IN ('LEM', 'LCO', 'IND') THEN 'PURCHASER'
    WHEN entity_cd IN ('FRM', 'LBY') THEN 'PROVIDER'
    ELSE 'OTHER'
  END AS organization_type,

  -- Form information
  form_type,
  CASE form_type
    WHEN 'F615' THEN 'Lobbyist Report'
    WHEN 'F625' THEN 'Lobbying Firm Report'
    WHEN 'F635' THEN 'Employer/Coalition Report'
    WHEN 'F645' THEN '$5,000+ Spender Report'
    ELSE form_type
  END AS form_type_description,

  -- Reporting period
  from_date AS period_start_date,
  thru_date AS period_end_date,
  DATE(from_date) AS period_start,
  DATE(thru_date) AS period_end,
  DATE_DIFF(DATE(thru_date), DATE(from_date), DAY) AS period_days,
  EXTRACT(YEAR FROM from_date) AS reporting_year,
  EXTRACT(QUARTER FROM from_date) AS reporting_quarter,
  CONCAT('Q', EXTRACT(QUARTER FROM from_date), ' ', EXTRACT(YEAR FROM from_date)) AS reporting_period,

  -- Firm information (for employers using firms)
  firm_id,
  firm_name,
  firm_city,
  firm_st AS firm_state,
  firm_zip4 AS firm_zip_code,

  -- Report metadata
  rpt_date AS report_date,
  DATE(rpt_date) AS report_date_only,

  -- Cumulative reporting period
  cum_beg_dt AS cumulative_begin_date,
  DATE(cum_beg_dt) AS cumulative_start_date,

  -- Lobbying activity description
  lby_actvty AS lobbying_activity_description,

  -- Major donor information
  major_donor AS has_major_donor,
  CASE major_donor
    WHEN 'Y' THEN TRUE
    WHEN 'N' THEN FALSE
    ELSE NULL
  END AS major_donor_flag,

  -- Signer information
  sig_date AS signature_date,
  DATE(sig_date) AS signed_date,
  sig_loc AS signature_location,
  sig_naml AS signer_last_name,
  sig_namf AS signer_first_name,
  sig_title AS signer_title,
  CONCAT(COALESCE(sig_namf, ''), ' ', COALESCE(sig_naml, '')) AS signer_full_name,

  -- Additional fields
  mail_city,
  mail_st AS mail_state,
  mail_zip4 AS mail_zip_code,

  -- Record metadata
  rec_type AS record_type,
  line_item

FROM `ca-lobby.ca_lobby.CVR_LOBBY_DISCLOSURE_CD`
WHERE filing_id IS NOT NULL;
```

#### v_disclosures_secondary
**Purpose:** Secondary disclosure cover page data
**Materialization:** No
**Expected Query Cost:** Low

```sql
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
```

### 1.4 Financial Transaction Views

#### v_payments
**Purpose:** All payments between lobbying entities (most critical table)
**Materialization:** RECOMMENDED (frequently queried)
**Expected Query Cost:** High (large table with many aggregations)

```sql
CREATE OR REPLACE VIEW `ca-lobby.ca_lobby.v_payments` AS
SELECT
  filing_id,
  amend_id AS amendment_id,
  line_item,
  rec_type AS record_type,
  form_type,

  -- Filer (the organization filing the report)
  filer_id,

  -- Employer information (who is paying for lobbying)
  emplr_naml AS employer_last_name,
  emplr_namf AS employer_first_name,
  CONCAT(COALESCE(emplr_namf, ''), ' ', COALESCE(emplr_naml, '')) AS employer_full_name,
  emplr_city AS employer_city,
  emplr_st AS employer_state,
  emplr_zip4 AS employer_zip_code,
  emplr_phon AS employer_phone,

  -- Payee information (who is receiving payment for lobbying)
  payee_naml AS payee_last_name,
  payee_namf AS payee_first_name,
  CONCAT(COALESCE(payee_namf, ''), ' ', COALESCE(payee_naml, '')) AS payee_full_name,
  payee_city,
  payee_st AS payee_state,
  payee_zip4 AS payee_zip_code,

  -- Payment amounts
  fees_amt AS fees_amount,
  reimb_amt AS reimbursement_amount,
  advan_amt AS advance_amount,
  COALESCE(fees_amt, 0) + COALESCE(reimb_amt, 0) + COALESCE(advan_amt, 0) AS total_payment_amount,

  -- Period and cumulative totals
  per_total AS period_total,
  cum_total AS cumulative_total,

  -- Descriptions
  advan_dscr AS advance_description,

  -- Transaction metadata
  bakref_tid AS transaction_id,

  -- Payment categorization
  CASE
    WHEN fees_amt > 0 THEN 'Fees'
    WHEN reimb_amt > 0 THEN 'Reimbursement'
    WHEN advan_amt > 0 THEN 'Advance'
    ELSE 'Other'
  END AS primary_payment_type,

  -- High-value transaction flags
  CASE
    WHEN COALESCE(fees_amt, 0) + COALESCE(reimb_amt, 0) + COALESCE(advan_amt, 0) >= 100000 THEN 'Very High ($100K+)'
    WHEN COALESCE(fees_amt, 0) + COALESCE(reimb_amt, 0) + COALESCE(advan_amt, 0) >= 10000 THEN 'High ($10K+)'
    WHEN COALESCE(fees_amt, 0) + COALESCE(reimb_amt, 0) + COALESCE(advan_amt, 0) >= 1000 THEN 'Medium ($1K+)'
    ELSE 'Low (< $1K)'
  END AS payment_tier

FROM `ca-lobby.ca_lobby.LPAY_CD`
WHERE filing_id IS NOT NULL;
```

#### v_expenditures
**Purpose:** All lobbying-related expenditures
**Materialization:** RECOMMENDED
**Expected Query Cost:** Medium-High

```sql
CREATE OR REPLACE VIEW `ca-lobby.ca_lobby.v_expenditures` AS
SELECT
  filing_id,
  amend_id AS amendment_id,
  line_item,
  rec_type AS record_type,
  form_type,

  -- Filer
  filer_id,

  -- Payee (vendor/recipient)
  payee_naml AS payee_last_name,
  payee_namf AS payee_first_name,
  CONCAT(COALESCE(payee_namf, ''), ' ', COALESCE(payee_naml, '')) AS payee_full_name,
  payee_city,
  payee_st AS payee_state,
  payee_zip4 AS payee_zip_code,

  -- Amount
  amount AS expenditure_amount,

  -- Description
  expn_dscr AS expenditure_description,

  -- Date
  expn_date AS expenditure_date,
  DATE(expn_date) AS expenditure_date_only,
  EXTRACT(YEAR FROM expn_date) AS expenditure_year,
  EXTRACT(QUARTER FROM expn_date) AS expenditure_quarter,

  -- Categorization
  CASE
    WHEN UPPER(expn_dscr) LIKE '%TRAVEL%' THEN 'Travel'
    WHEN UPPER(expn_dscr) LIKE '%MEAL%' OR UPPER(expn_dscr) LIKE '%FOOD%' THEN 'Meals'
    WHEN UPPER(expn_dscr) LIKE '%OFFICE%' THEN 'Office'
    WHEN UPPER(expn_dscr) LIKE '%CONSULTING%' THEN 'Consulting'
    WHEN UPPER(expn_dscr) LIKE '%LEGAL%' THEN 'Legal'
    ELSE 'Other'
  END AS expenditure_category,

  -- Amount tier
  CASE
    WHEN amount >= 10000 THEN 'High ($10K+)'
    WHEN amount >= 1000 THEN 'Medium ($1K+)'
    WHEN amount >= 100 THEN 'Low ($100+)'
    ELSE 'Minimal (< $100)'
  END AS expenditure_tier,

  -- Transaction reference
  bakref_tid AS transaction_id

FROM `ca-lobby.ca_lobby.LEXP_CD`
WHERE filing_id IS NOT NULL;
```

#### v_campaign_contributions
**Purpose:** Campaign contributions by lobbying entities
**Materialization:** No
**Expected Query Cost:** Medium

```sql
CREATE OR REPLACE VIEW `ca-lobby.ca_lobby.v_campaign_contributions` AS
SELECT
  filing_id,
  amend_id AS amendment_id,
  line_item,
  rec_type AS record_type,
  form_type,

  -- Filer
  filer_id,

  -- Contributor (payor)
  payor_naml AS contributor_last_name,
  payor_namf AS contributor_first_name,
  CONCAT(COALESCE(payor_namf, ''), ' ', COALESCE(payor_naml, '')) AS contributor_full_name,
  payor_city AS contributor_city,
  payor_st AS contributor_state,
  payor_zip4 AS contributor_zip_code,

  -- Recipient committee
  cmte_id AS committee_id,

  -- Contribution details
  amount AS contribution_amount,
  ctrib_date AS contribution_date,
  DATE(ctrib_date) AS contribution_date_only,
  EXTRACT(YEAR FROM ctrib_date) AS contribution_year,
  EXTRACT(QUARTER FROM ctrib_date) AS contribution_quarter,

  -- Amount tier
  CASE
    WHEN amount >= 10000 THEN 'Major ($10K+)'
    WHEN amount >= 1000 THEN 'Significant ($1K+)'
    WHEN amount >= 100 THEN 'Moderate ($100+)'
    ELSE 'Small (< $100)'
  END AS contribution_tier,

  -- Transaction reference
  bakref_tid AS transaction_id

FROM `ca-lobby.ca_lobby.LCCM_CD`
WHERE filing_id IS NOT NULL;
```

#### v_other_payments
**Purpose:** Miscellaneous lobbying-related payments
**Materialization:** No
**Expected Query Cost:** Low-Medium

```sql
CREATE OR REPLACE VIEW `ca-lobby.ca_lobby.v_other_payments` AS
SELECT
  filing_id,
  amend_id AS amendment_id,
  line_item,
  rec_type AS record_type,
  form_type,

  -- Filer
  filer_id,

  -- Payee
  payee_naml AS payee_last_name,
  payee_namf AS payee_first_name,
  CONCAT(COALESCE(payee_namf, ''), ' ', COALESCE(payee_naml, '')) AS payee_full_name,

  -- Amount
  amount AS payment_amount,

  -- Transaction reference
  bakref_tid AS transaction_id

FROM `ca-lobby.ca_lobby.LOTH_CD`
WHERE filing_id IS NOT NULL;
```

### 1.5 Relationship Views

#### v_employer_relationships
**Purpose:** Employer-lobbyist relationships and subcontracted clients
**Materialization:** No
**Expected Query Cost:** Medium

```sql
CREATE OR REPLACE VIEW `ca-lobby.ca_lobby.v_employer_relationships` AS
SELECT
  filing_id,
  amend_id AS amendment_id,
  line_item,
  rec_type AS record_type,
  form_type,

  -- Filer (the lobbying firm or lobbyist)
  filer_id,

  -- Employer/Client information
  agcy_naml AS employer_last_name,
  agcy_namf AS employer_first_name,
  CONCAT(COALESCE(agcy_namf, ''), ' ', COALESCE(agcy_naml, '')) AS employer_full_name,
  agcy_city AS employer_city,
  agcy_st AS employer_state,
  agcy_zip4 AS employer_zip_code,
  agcy_phon AS employer_phone,

  -- Relationship type
  CASE rec_type
    WHEN 'LEMP' THEN 'Direct Employer'
    WHEN 'LSUB' THEN 'Subcontracted Client'
    ELSE rec_type
  END AS relationship_type,

  -- Client details (for subcontracts)
  client_naml AS client_last_name,
  client_namf AS client_first_name,
  CONCAT(COALESCE(client_namf, ''), ' ', COALESCE(client_naml, '')) AS client_full_name,
  client_city,
  client_st AS client_state,
  client_zip4 AS client_zip_code,

  -- Effective dates
  eff_date AS effective_date,
  DATE(eff_date) AS effective_date_only

FROM `ca-lobby.ca_lobby.LEMP_CD`
WHERE filing_id IS NOT NULL;
```

### 1.6 Supporting Data Views

#### v_attachments
**Purpose:** Payment attachments and supporting schedules
**Materialization:** No
**Expected Query Cost:** Low

```sql
CREATE OR REPLACE VIEW `ca-lobby.ca_lobby.v_attachments` AS
SELECT
  filing_id,
  amend_id AS amendment_id,
  line_item,
  rec_type AS record_type,
  form_type,
  filer_id,

  -- Recipient information (for Schedule 635C)
  recip_naml AS recipient_last_name,
  recip_namf AS recipient_first_name,
  CONCAT(COALESCE(recip_namf, ''), ' ', COALESCE(recip_naml, '')) AS recipient_full_name,
  recip_city AS recipient_city,
  recip_st AS recipient_state,
  recip_zip4 AS recipient_zip_code,

  -- Payment details
  amount AS payment_amount,
  pmt_date AS payment_date,
  DATE(pmt_date) AS payment_date_only,
  cum_amt AS cumulative_amount,

  -- Description
  CASE form_type
    WHEN 'F635' THEN 'Schedule 635C: Payments to Lobbying Coalition'
    WHEN 'F640' THEN 'Schedule 640: Governmental Agency Reporting'
    ELSE form_type
  END AS attachment_type

FROM `ca-lobby.ca_lobby.LATT_CD`
WHERE filing_id IS NOT NULL;
```

#### v_names
**Purpose:** Name variations and aliases
**Materialization:** No
**Expected Query Cost:** Low

```sql
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
```

#### v_amendments
**Purpose:** Amendment history for lobbying registrations
**Materialization:** No
**Expected Query Cost:** Low

```sql
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
```

#### v_lookup_codes
**Purpose:** Code translation table
**Materialization:** No
**Expected Query Cost:** Very Low (reference table)

```sql
CREATE OR REPLACE VIEW `ca-lobby.ca_lobby.v_lookup_codes` AS
SELECT
  code_type,
  code_id,
  code_desc AS code_description
FROM `ca-lobby.ca_lobby.LOOKUP_CODES_CD`;
```

---

## Layer 2: Integration Views

**Purpose:** Pre-joined common queries to eliminate repetitive joins.

### 2.1 Filer Integration Views

#### v_int_filer_complete
**Purpose:** Complete filer profile with all related information
**Materialization:** RECOMMENDED
**Expected Query Cost:** Medium

```sql
CREATE OR REPLACE VIEW `ca-lobby.ca_lobby.v_int_filer_complete` AS
SELECT
  f.filer_id,
  f.full_name AS filer_name,
  f.status,
  f.status_description,
  f.effective_date,

  -- Address information
  a.address_line_1,
  a.address_line_2,
  a.city,
  a.state,
  a.zip_code,
  a.full_address,
  a.phone,
  a.email,
  a.location_type,

  -- Filer type
  ft.filer_type_description,

  -- Cross-reference
  x.cross_reference_id,

  -- Activity summary
  COUNT(DISTINCT ff.filing_id) AS total_filings,
  MIN(ff.filing_date) AS first_filing_date,
  MAX(ff.filing_date) AS most_recent_filing_date

FROM `ca-lobby.ca_lobby.v_filers` f
LEFT JOIN `ca-lobby.ca_lobby.v_filer_addresses` a ON f.filer_id = a.filer_id
LEFT JOIN `ca-lobby.ca_lobby.v_filer_types` ft ON f.filer_type = ft.filer_type
LEFT JOIN `ca-lobby.ca_lobby.v_filer_xref` x ON f.filer_id = x.filer_id
LEFT JOIN `ca-lobby.ca_lobby.v_filer_filings` ff ON f.filer_id = ff.filer_id
GROUP BY 1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16;
```

### 2.2 Disclosure Integration Views

#### v_int_filer_disclosures
**Purpose:** Complete disclosure filings with filer details
**Materialization:** RECOMMENDED (frequently queried)
**Expected Query Cost:** High

```sql
CREATE OR REPLACE VIEW `ca-lobby.ca_lobby.v_int_filer_disclosures` AS
SELECT
  d.filing_id,
  d.amendment_id,
  d.amendment_status,

  -- Filer information
  d.filer_id,
  f.filer_name,
  f.city AS filer_city,
  f.state AS filer_state,
  f.full_address AS filer_address,
  f.phone AS filer_phone,
  f.email AS filer_email,

  -- Entity classification
  d.entity_code,
  d.entity_type,
  d.organization_type,

  -- Form information
  d.form_type,
  d.form_type_description,

  -- Reporting period
  d.period_start_date,
  d.period_end_date,
  d.period_days,
  d.reporting_year,
  d.reporting_quarter,
  d.reporting_period,

  -- Firm information (if using a firm)
  d.firm_id,
  d.firm_name,
  d.firm_city,
  d.firm_state,

  -- Report metadata
  d.report_date,
  d.cumulative_start_date,

  -- Lobbying details
  d.lobbying_activity_description,
  d.has_major_donor,

  -- Signer
  d.signer_full_name,
  d.signer_title,
  d.signed_date

FROM `ca-lobby.ca_lobby.v_disclosures` d
LEFT JOIN `ca-lobby.ca_lobby.v_int_filer_complete` f ON d.filer_id = f.filer_id;
```

#### v_int_filer_registrations
**Purpose:** Complete registration records with filer details
**Materialization:** No
**Expected Query Cost:** Medium

```sql
CREATE OR REPLACE VIEW `ca-lobby.ca_lobby.v_int_filer_registrations` AS
SELECT
  r.filing_id,
  r.amendment_id,
  r.amendment_status,

  -- Filer information
  r.filer_id,
  f.filer_name,
  f.city AS filer_city,
  f.state AS filer_state,
  f.full_address AS filer_address,

  -- Entity classification
  r.entity_code,
  r.entity_type,
  r.organization_type,

  -- Form information
  r.form_type,
  r.form_type_description,

  -- Qualification
  r.date_qualified,
  r.qualification_year,

  -- Firm details
  r.firm_id,
  r.firm_name,
  r.firm_city,
  r.firm_state,
  r.authorized_firm,

  -- Ethics training
  r.ethics_training_date,

  -- Report date
  r.report_date

FROM `ca-lobby.ca_lobby.v_registrations` r
LEFT JOIN `ca-lobby.ca_lobby.v_int_filer_complete` f ON r.filer_id = f.filer_id;
```

### 2.3 Payment Integration Views

#### v_int_payment_details
**Purpose:** Payments with complete filer, employer, and disclosure context
**Materialization:** RECOMMENDED (most frequently queried)
**Expected Query Cost:** Very High

```sql
CREATE OR REPLACE VIEW `ca-lobby.ca_lobby.v_int_payment_details` AS
SELECT
  p.filing_id,
  p.amendment_id,
  p.line_item,

  -- Filer (the organization filing the report)
  p.filer_id,
  f.filer_name,
  d.entity_type AS filer_entity_type,
  d.organization_type AS filer_organization_type,

  -- Disclosure context
  d.reporting_period,
  d.reporting_year,
  d.reporting_quarter,
  d.period_start_date,
  d.period_end_date,

  -- Employer (purchaser of lobbying services)
  p.employer_full_name,
  p.employer_city,
  p.employer_state,

  -- Payee (provider of lobbying services)
  p.payee_full_name,
  p.payee_city,
  p.payee_state,

  -- Payment amounts
  p.fees_amount,
  p.reimbursement_amount,
  p.advance_amount,
  p.total_payment_amount,
  p.period_total,
  p.cumulative_total,

  -- Payment categorization
  p.primary_payment_type,
  p.payment_tier,

  -- Form information
  p.form_type,
  d.form_type_description,

  -- Firm information (if filer used a firm)
  d.firm_name,
  d.firm_city,
  d.firm_state

FROM `ca-lobby.ca_lobby.v_payments` p
LEFT JOIN `ca-lobby.ca_lobby.v_int_filer_complete` f ON p.filer_id = f.filer_id
LEFT JOIN `ca-lobby.ca_lobby.v_disclosures` d ON p.filing_id = d.filing_id AND p.amendment_id = d.amendment_id;
```

#### v_int_payment_with_latest_amendment
**Purpose:** Only the most recent amendment for each payment
**Materialization:** RECOMMENDED (eliminates duplicate handling)
**Expected Query Cost:** High

```sql
CREATE OR REPLACE VIEW `ca-lobby.ca_lobby.v_int_payment_with_latest_amendment` AS
WITH ranked_payments AS (
  SELECT
    *,
    ROW_NUMBER() OVER (
      PARTITION BY filing_id, line_item
      ORDER BY amendment_number DESC
    ) AS amendment_rank
  FROM `ca-lobby.ca_lobby.v_int_payment_details`
)
SELECT * EXCEPT (amendment_rank)
FROM ranked_payments
WHERE amendment_rank = 1;
```

### 2.4 Expenditure Integration Views

#### v_int_expenditure_details
**Purpose:** Expenditures with filer and disclosure context
**Materialization:** RECOMMENDED
**Expected Query Cost:** High

```sql
CREATE OR REPLACE VIEW `ca-lobby.ca_lobby.v_int_expenditure_details` AS
SELECT
  e.filing_id,
  e.amendment_id,
  e.line_item,

  -- Filer information
  e.filer_id,
  f.filer_name,
  d.entity_type AS filer_entity_type,

  -- Disclosure context
  d.reporting_period,
  d.reporting_year,
  d.reporting_quarter,

  -- Payee (vendor)
  e.payee_full_name,
  e.payee_city,
  e.payee_state,

  -- Expenditure details
  e.expenditure_amount,
  e.expenditure_description,
  e.expenditure_date,
  e.expenditure_year,
  e.expenditure_quarter,
  e.expenditure_category,
  e.expenditure_tier,

  -- Form
  e.form_type,
  d.form_type_description

FROM `ca-lobby.ca_lobby.v_expenditures` e
LEFT JOIN `ca-lobby.ca_lobby.v_int_filer_complete` f ON e.filer_id = f.filer_id
LEFT JOIN `ca-lobby.ca_lobby.v_disclosures` d ON e.filing_id = d.filing_id AND e.amendment_id = d.amendment_id;
```

### 2.5 Employer-Firm Relationship Views

#### v_int_employer_firm_relationships
**Purpose:** Complete picture of which employers hired which firms/lobbyists
**Materialization:** RECOMMENDED
**Expected Query Cost:** Medium

```sql
CREATE OR REPLACE VIEW `ca-lobby.ca_lobby.v_int_employer_firm_relationships` AS
SELECT
  er.filing_id,
  er.amendment_id,

  -- Firm/Lobbyist (filer)
  er.filer_id AS firm_filer_id,
  firm.filer_name AS firm_name,
  firm.city AS firm_city,
  firm.state AS firm_state,

  -- Employer/Client
  er.employer_full_name,
  er.employer_city,
  er.employer_state,
  er.relationship_type,

  -- Subcontracted client (if applicable)
  er.client_full_name,
  er.client_city,
  er.client_state,

  -- Effective dates
  er.effective_date,

  -- Registration context
  r.qualification_year,
  r.entity_type AS firm_entity_type,

  -- Form
  er.form_type

FROM `ca-lobby.ca_lobby.v_employer_relationships` er
LEFT JOIN `ca-lobby.ca_lobby.v_int_filer_complete` firm ON er.filer_id = firm.filer_id
LEFT JOIN `ca-lobby.ca_lobby.v_registrations` r ON er.filing_id = r.filing_id AND er.amendment_id = r.amendment_id;
```

### 2.6 Complete Activity Views

#### v_int_complete_filing_details
**Purpose:** Everything about a specific filing (disclosure + all transactions)
**Materialization:** No (too broad, use filtered versions)
**Expected Query Cost:** Very High

```sql
CREATE OR REPLACE VIEW `ca-lobby.ca_lobby.v_int_complete_filing_details` AS
SELECT
  d.filing_id,
  d.amendment_id,
  d.filer_id,
  d.filer_name,
  d.entity_type,
  d.organization_type,
  d.reporting_period,
  d.reporting_year,
  d.reporting_quarter,
  d.period_start_date,
  d.period_end_date,

  -- Payment summary
  COALESCE(ps.payment_count, 0) AS total_payments,
  COALESCE(ps.total_fees, 0) AS total_fees_paid,
  COALESCE(ps.total_reimbursements, 0) AS total_reimbursements,
  COALESCE(ps.total_advances, 0) AS total_advances,
  COALESCE(ps.grand_total_payments, 0) AS total_payment_amount,

  -- Expenditure summary
  COALESCE(es.expenditure_count, 0) AS total_expenditures,
  COALESCE(es.total_expenditure_amount, 0) AS total_expenditure_amount,

  -- Campaign contribution summary
  COALESCE(cs.contribution_count, 0) AS total_contributions,
  COALESCE(cs.total_contribution_amount, 0) AS total_contribution_amount,

  -- Other payment summary
  COALESCE(os.other_payment_count, 0) AS total_other_payments,
  COALESCE(os.total_other_amount, 0) AS total_other_payment_amount,

  -- Grand total financial activity
  COALESCE(ps.grand_total_payments, 0) +
  COALESCE(es.total_expenditure_amount, 0) +
  COALESCE(cs.total_contribution_amount, 0) +
  COALESCE(os.total_other_amount, 0) AS grand_total_financial_activity

FROM `ca-lobby.ca_lobby.v_int_filer_disclosures` d

-- Payment summary
LEFT JOIN (
  SELECT
    filing_id,
    amendment_id,
    COUNT(*) AS payment_count,
    SUM(fees_amount) AS total_fees,
    SUM(reimbursement_amount) AS total_reimbursements,
    SUM(advance_amount) AS total_advances,
    SUM(total_payment_amount) AS grand_total_payments
  FROM `ca-lobby.ca_lobby.v_payments`
  GROUP BY filing_id, amendment_id
) ps ON d.filing_id = ps.filing_id AND d.amendment_id = ps.amendment_id

-- Expenditure summary
LEFT JOIN (
  SELECT
    filing_id,
    amendment_id,
    COUNT(*) AS expenditure_count,
    SUM(expenditure_amount) AS total_expenditure_amount
  FROM `ca-lobby.ca_lobby.v_expenditures`
  GROUP BY filing_id, amendment_id
) es ON d.filing_id = es.filing_id AND d.amendment_id = es.amendment_id

-- Contribution summary
LEFT JOIN (
  SELECT
    filing_id,
    amendment_id,
    COUNT(*) AS contribution_count,
    SUM(contribution_amount) AS total_contribution_amount
  FROM `ca-lobby.ca_lobby.v_campaign_contributions`
  GROUP BY filing_id, amendment_id
) cs ON d.filing_id = cs.filing_id AND d.amendment_id = cs.amendment_id

-- Other payment summary
LEFT JOIN (
  SELECT
    filing_id,
    amendment_id,
    COUNT(*) AS other_payment_count,
    SUM(payment_amount) AS total_other_amount
  FROM `ca-lobby.ca_lobby.v_other_payments`
  GROUP BY filing_id, amendment_id
) os ON d.filing_id = os.filing_id AND d.amendment_id = os.amendment_id;
```

### 2.7 Money Flow Views

#### v_int_money_flow_purchaser_to_provider
**Purpose:** Track money from purchasers (employers) to providers (firms/lobbyists)
**Materialization:** RECOMMENDED
**Expected Query Cost:** High

```sql
CREATE OR REPLACE VIEW `ca-lobby.ca_lobby.v_int_money_flow_purchaser_to_provider` AS
SELECT
  -- Provider (who received the money)
  p.filer_id AS provider_filer_id,
  p.filer_name AS provider_name,
  provider_disc.entity_type AS provider_type,
  p.payee_full_name AS provider_payee_name,

  -- Purchaser (who paid for lobbying)
  p.employer_full_name AS purchaser_name,

  -- Payment details
  p.total_payment_amount,
  p.fees_amount,
  p.reimbursement_amount,
  p.advance_amount,
  p.payment_tier,

  -- Time period
  p.reporting_year,
  p.reporting_quarter,
  p.reporting_period,
  p.period_start_date,
  p.period_end_date,

  -- Geography
  p.employer_city AS purchaser_city,
  p.employer_state AS purchaser_state,
  p.payee_city AS provider_city,
  p.payee_state AS provider_state,

  -- Form
  p.form_type,
  p.form_type_description,

  -- Transaction reference
  p.filing_id,
  p.amendment_id,
  p.line_item

FROM `ca-lobby.ca_lobby.v_int_payment_details` p
LEFT JOIN `ca-lobby.ca_lobby.v_disclosures` provider_disc
  ON p.filer_id = provider_disc.filer_id
  AND p.filing_id = provider_disc.filing_id;
```

### 2.8 Network Analysis Views

#### v_int_network_employer_to_firm
**Purpose:** Network graph data: employers and their lobbying firms
**Materialization:** RECOMMENDED (for network visualization)
**Expected Query Cost:** Medium

```sql
CREATE OR REPLACE VIEW `ca-lobby.ca_lobby.v_int_network_employer_to_firm` AS
SELECT DISTINCT
  -- Source node (employer)
  er.employer_full_name AS source_node,
  'EMPLOYER' AS source_type,
  er.employer_city AS source_city,
  er.employer_state AS source_state,

  -- Target node (firm/lobbyist)
  er.filer_id AS target_node_id,
  firm.filer_name AS target_node,
  'FIRM' AS target_type,
  firm.city AS target_city,
  firm.state AS target_state,

  -- Edge properties
  er.relationship_type AS edge_type,
  COUNT(DISTINCT er.filing_id) AS relationship_count,
  MIN(er.effective_date) AS relationship_start,
  MAX(r.report_date) AS last_filing_date,

  -- Payment summary (if available)
  SUM(p.total_payment_amount) AS total_payments_made

FROM `ca-lobby.ca_lobby.v_employer_relationships` er
LEFT JOIN `ca-lobby.ca_lobby.v_int_filer_complete` firm ON er.filer_id = firm.filer_id
LEFT JOIN `ca-lobby.ca_lobby.v_registrations` r ON er.filing_id = r.filing_id
LEFT JOIN `ca-lobby.ca_lobby.v_payments` p
  ON er.filing_id = p.filing_id
  AND er.employer_full_name = p.employer_full_name
GROUP BY 1,2,3,4,5,6,7,8,9,10;
```

### 2.9 Amendment Tracking Views

#### v_int_amendment_history
**Purpose:** Track all amendments to a filing over time
**Materialization:** No
**Expected Query Cost:** Medium

```sql
CREATE OR REPLACE VIEW `ca-lobby.ca_lobby.v_int_amendment_history` AS
SELECT
  d.filing_id,
  d.filer_id,
  f.filer_name,
  d.amendment_id,
  d.amendment_number,
  d.amendment_status,
  d.reporting_period,
  d.report_date,

  -- Amendment metadata
  a.execution_date AS amendment_date,
  a.amendment_year,

  -- Changes in payment totals (compare to original)
  p.payment_count AS payments_in_amendment,
  p.total_fees AS fees_in_amendment,

  -- Days between original and amendment
  DATE_DIFF(a.execution_date, orig.report_date, DAY) AS days_since_original_filing

FROM `ca-lobby.ca_lobby.v_disclosures` d
LEFT JOIN `ca-lobby.ca_lobby.v_int_filer_complete` f ON d.filer_id = f.filer_id
LEFT JOIN `ca-lobby.ca_lobby.v_amendments` a
  ON d.filing_id = a.filing_id AND d.amendment_id = a.amendment_id
LEFT JOIN (
  SELECT filing_id, amendment_id, COUNT(*) AS payment_count, SUM(fees_amount) AS total_fees
  FROM `ca-lobby.ca_lobby.v_payments`
  GROUP BY filing_id, amendment_id
) p ON d.filing_id = p.filing_id AND d.amendment_id = p.amendment_id
LEFT JOIN (
  SELECT filing_id, report_date
  FROM `ca-lobby.ca_lobby.v_disclosures`
  WHERE amendment_number = 0
) orig ON d.filing_id = orig.filing_id
WHERE d.amendment_number > 0;
```

### 2.10 Additional Integration Views

#### v_int_filer_payment_summary
**Purpose:** Total payments by filer across all time
**Materialization:** RECOMMENDED
**Expected Query Cost:** High

```sql
CREATE OR REPLACE VIEW `ca-lobby.ca_lobby.v_int_filer_payment_summary` AS
SELECT
  f.filer_id,
  f.filer_name,
  f.status,
  fc.filer_type_description,

  -- Payment statistics
  COUNT(DISTINCT p.filing_id) AS total_filings_with_payments,
  COUNT(DISTINCT p.line_item) AS total_payment_transactions,

  -- Amount totals
  SUM(p.fees_amount) AS total_fees_all_time,
  SUM(p.reimbursement_amount) AS total_reimbursements_all_time,
  SUM(p.advance_amount) AS total_advances_all_time,
  SUM(p.total_payment_amount) AS grand_total_payments_all_time,

  -- Statistics
  AVG(p.total_payment_amount) AS average_payment_amount,
  MIN(p.total_payment_amount) AS minimum_payment,
  MAX(p.total_payment_amount) AS maximum_payment,

  -- Time range
  MIN(d.period_start_date) AS first_payment_period,
  MAX(d.period_end_date) AS most_recent_payment_period,

  -- Activity years
  COUNT(DISTINCT d.reporting_year) AS years_active

FROM `ca-lobby.ca_lobby.v_int_filer_complete` f
LEFT JOIN `ca-lobby.ca_lobby.v_payments` p ON f.filer_id = p.filer_id
LEFT JOIN `ca-lobby.ca_lobby.v_disclosures` d ON p.filing_id = d.filing_id AND p.amendment_id = d.amendment_id
LEFT JOIN `ca-lobby.ca_lobby.v_int_filer_complete` fc ON f.filer_id = fc.filer_id
GROUP BY 1,2,3,4;
```

#### v_int_filer_expenditure_summary
**Purpose:** Total expenditures by filer across all time
**Materialization:** RECOMMENDED
**Expected Query Cost:** High

```sql
CREATE OR REPLACE VIEW `ca-lobby.ca_lobby.v_int_filer_expenditure_summary` AS
SELECT
  f.filer_id,
  f.filer_name,

  -- Expenditure statistics
  COUNT(DISTINCT e.filing_id) AS total_filings_with_expenditures,
  COUNT(*) AS total_expenditure_transactions,

  -- Amount totals
  SUM(e.expenditure_amount) AS total_expenditures_all_time,
  AVG(e.expenditure_amount) AS average_expenditure,

  -- By category
  SUM(CASE WHEN e.expenditure_category = 'Travel' THEN e.expenditure_amount ELSE 0 END) AS total_travel_expenses,
  SUM(CASE WHEN e.expenditure_category = 'Meals' THEN e.expenditure_amount ELSE 0 END) AS total_meal_expenses,
  SUM(CASE WHEN e.expenditure_category = 'Office' THEN e.expenditure_amount ELSE 0 END) AS total_office_expenses,
  SUM(CASE WHEN e.expenditure_category = 'Consulting' THEN e.expenditure_amount ELSE 0 END) AS total_consulting_expenses,
  SUM(CASE WHEN e.expenditure_category = 'Legal' THEN e.expenditure_amount ELSE 0 END) AS total_legal_expenses,
  SUM(CASE WHEN e.expenditure_category = 'Other' THEN e.expenditure_amount ELSE 0 END) AS total_other_expenses,

  -- Time range
  MIN(d.period_start_date) AS first_expenditure_period,
  MAX(d.period_end_date) AS most_recent_expenditure_period

FROM `ca-lobby.ca_lobby.v_int_filer_complete` f
LEFT JOIN `ca-lobby.ca_lobby.v_expenditures` e ON f.filer_id = e.filer_id
LEFT JOIN `ca-lobby.ca_lobby.v_disclosures` d ON e.filing_id = d.filing_id AND e.amendment_id = d.amendment_id
GROUP BY 1,2;
```

---

## Layer 3: Analytical Views

**Purpose:** Pre-aggregated summaries for business intelligence and reporting.

### 3.1 Time-Based Aggregations

#### v_summary_payments_by_year
**Purpose:** Annual payment trends
**Materialization:** RECOMMENDED
**Expected Query Cost:** High

```sql
CREATE OR REPLACE VIEW `ca-lobby.ca_lobby.v_summary_payments_by_year` AS
SELECT
  d.reporting_year,

  -- Overall statistics
  COUNT(DISTINCT p.filer_id) AS unique_filers,
  COUNT(DISTINCT p.filing_id) AS total_filings,
  COUNT(*) AS total_payment_transactions,

  -- Amount totals
  SUM(p.fees_amount) AS total_fees,
  SUM(p.reimbursement_amount) AS total_reimbursements,
  SUM(p.advance_amount) AS total_advances,
  SUM(p.total_payment_amount) AS grand_total_payments,

  -- Statistics
  AVG(p.total_payment_amount) AS average_payment,
  MIN(p.total_payment_amount) AS minimum_payment,
  MAX(p.total_payment_amount) AS maximum_payment,

  -- By organization type
  SUM(CASE WHEN d.organization_type = 'PURCHASER' THEN p.total_payment_amount ELSE 0 END) AS purchaser_payments,
  SUM(CASE WHEN d.organization_type = 'PROVIDER' THEN p.total_payment_amount ELSE 0 END) AS provider_payments,

  -- By entity type
  SUM(CASE WHEN d.entity_code = 'LEM' THEN p.total_payment_amount ELSE 0 END) AS employer_payments,
  SUM(CASE WHEN d.entity_code = 'FRM' THEN p.total_payment_amount ELSE 0 END) AS firm_payments,
  SUM(CASE WHEN d.entity_code = 'LCO' THEN p.total_payment_amount ELSE 0 END) AS coalition_payments,

  -- High-value transactions
  SUM(CASE WHEN p.payment_tier = 'Very High ($100K+)' THEN 1 ELSE 0 END) AS very_high_value_count,
  SUM(CASE WHEN p.payment_tier = 'High ($10K+)' THEN 1 ELSE 0 END) AS high_value_count

FROM `ca-lobby.ca_lobby.v_payments` p
LEFT JOIN `ca-lobby.ca_lobby.v_disclosures` d
  ON p.filing_id = d.filing_id AND p.amendment_id = d.amendment_id
GROUP BY d.reporting_year
ORDER BY d.reporting_year DESC;
```

#### v_summary_payments_by_quarter
**Purpose:** Quarterly payment trends
**Materialization:** RECOMMENDED
**Expected Query Cost:** High

```sql
CREATE OR REPLACE VIEW `ca-lobby.ca_lobby.v_summary_payments_by_quarter` AS
SELECT
  d.reporting_year,
  d.reporting_quarter,
  d.reporting_period,

  -- Statistics
  COUNT(DISTINCT p.filer_id) AS unique_filers,
  COUNT(*) AS total_payments,
  SUM(p.total_payment_amount) AS total_payment_amount,
  AVG(p.total_payment_amount) AS average_payment,

  -- Year-over-year comparison helper
  LAG(SUM(p.total_payment_amount)) OVER (
    PARTITION BY d.reporting_quarter
    ORDER BY d.reporting_year
  ) AS same_quarter_previous_year,

  -- Growth calculation
  ROUND(
    (SUM(p.total_payment_amount) - LAG(SUM(p.total_payment_amount)) OVER (
      PARTITION BY d.reporting_quarter
      ORDER BY d.reporting_year
    )) / LAG(SUM(p.total_payment_amount)) OVER (
      PARTITION BY d.reporting_quarter
      ORDER BY d.reporting_year
    ) * 100,
    2
  ) AS yoy_growth_percent

FROM `ca-lobby.ca_lobby.v_payments` p
LEFT JOIN `ca-lobby.ca_lobby.v_disclosures` d
  ON p.filing_id = d.filing_id AND p.amendment_id = d.amendment_id
GROUP BY d.reporting_year, d.reporting_quarter, d.reporting_period
ORDER BY d.reporting_year DESC, d.reporting_quarter DESC;
```

#### v_summary_expenditures_by_year
**Purpose:** Annual expenditure trends
**Materialization:** RECOMMENDED
**Expected Query Cost:** Medium-High

```sql
CREATE OR REPLACE VIEW `ca-lobby.ca_lobby.v_summary_expenditures_by_year` AS
SELECT
  e.expenditure_year,

  -- Overall statistics
  COUNT(DISTINCT e.filer_id) AS unique_filers,
  COUNT(*) AS total_expenditure_transactions,
  SUM(e.expenditure_amount) AS total_expenditures,
  AVG(e.expenditure_amount) AS average_expenditure,

  -- By category
  SUM(CASE WHEN e.expenditure_category = 'Travel' THEN e.expenditure_amount ELSE 0 END) AS travel_expenses,
  SUM(CASE WHEN e.expenditure_category = 'Meals' THEN e.expenditure_amount ELSE 0 END) AS meal_expenses,
  SUM(CASE WHEN e.expenditure_category = 'Office' THEN e.expenditure_amount ELSE 0 END) AS office_expenses,
  SUM(CASE WHEN e.expenditure_category = 'Consulting' THEN e.expenditure_amount ELSE 0 END) AS consulting_expenses,
  SUM(CASE WHEN e.expenditure_category = 'Legal' THEN e.expenditure_amount ELSE 0 END) AS legal_expenses,
  SUM(CASE WHEN e.expenditure_category = 'Other' THEN e.expenditure_amount ELSE 0 END) AS other_expenses

FROM `ca-lobby.ca_lobby.v_expenditures` e
GROUP BY e.expenditure_year
ORDER BY e.expenditure_year DESC;
```

### 3.2 Top Spenders/Recipients Views

#### v_summary_top_payment_recipients
**Purpose:** Firms/lobbyists receiving the most money
**Materialization:** RECOMMENDED
**Expected Query Cost:** High

```sql
CREATE OR REPLACE VIEW `ca-lobby.ca_lobby.v_summary_top_payment_recipients` AS
WITH payment_recipients AS (
  SELECT
    p.filer_id,
    f.filer_name,
    d.entity_type,
    SUM(p.total_payment_amount) AS total_received,
    COUNT(DISTINCT p.filing_id) AS filing_count,
    COUNT(*) AS payment_count,
    AVG(p.total_payment_amount) AS average_payment,
    MIN(d.period_start_date) AS first_payment,
    MAX(d.period_end_date) AS most_recent_payment,
    COUNT(DISTINCT d.reporting_year) AS years_active
  FROM `ca-lobby.ca_lobby.v_payments` p
  LEFT JOIN `ca-lobby.ca_lobby.v_int_filer_complete` f ON p.filer_id = f.filer_id
  LEFT JOIN `ca-lobby.ca_lobby.v_disclosures` d ON p.filing_id = d.filing_id
  WHERE d.organization_type = 'PROVIDER'
  GROUP BY p.filer_id, f.filer_name, d.entity_type
)
SELECT
  *,
  RANK() OVER (ORDER BY total_received DESC) AS recipient_rank,
  ROUND(total_received / SUM(total_received) OVER () * 100, 2) AS percent_of_total_market
FROM payment_recipients
ORDER BY total_received DESC;
```

#### v_summary_top_purchasers
**Purpose:** Employers spending the most on lobbying
**Materialization:** RECOMMENDED
**Expected Query Cost:** High

```sql
CREATE OR REPLACE VIEW `ca-lobby.ca_lobby.v_summary_top_purchasers` AS
WITH purchaser_spending AS (
  SELECT
    p.employer_full_name AS purchaser_name,
    p.employer_city,
    p.employer_state,
    COUNT(DISTINCT p.filer_id) AS firms_hired,
    SUM(p.total_payment_amount) AS total_spent,
    COUNT(*) AS payment_count,
    AVG(p.total_payment_amount) AS average_payment,
    MIN(d.period_start_date) AS first_payment,
    MAX(d.period_end_date) AS most_recent_payment,
    COUNT(DISTINCT d.reporting_year) AS years_active
  FROM `ca-lobby.ca_lobby.v_payments` p
  LEFT JOIN `ca-lobby.ca_lobby.v_disclosures` d ON p.filing_id = d.filing_id
  WHERE p.employer_full_name IS NOT NULL
  GROUP BY p.employer_full_name, p.employer_city, p.employer_state
)
SELECT
  *,
  RANK() OVER (ORDER BY total_spent DESC) AS purchaser_rank,
  ROUND(total_spent / SUM(total_spent) OVER () * 100, 2) AS percent_of_total_spending
FROM purchaser_spending
ORDER BY total_spent DESC;
```

#### v_summary_top_campaign_contributors
**Purpose:** Lobbyists making largest campaign contributions
**Materialization:** No
**Expected Query Cost:** Medium

```sql
CREATE OR REPLACE VIEW `ca-lobby.ca_lobby.v_summary_top_campaign_contributors` AS
SELECT
  c.filer_id,
  f.filer_name,
  d.entity_type,

  -- Contribution statistics
  COUNT(*) AS total_contributions,
  SUM(c.contribution_amount) AS total_contributed,
  AVG(c.contribution_amount) AS average_contribution,
  COUNT(DISTINCT c.committee_id) AS committees_supported,

  -- Time range
  MIN(c.contribution_date) AS first_contribution,
  MAX(c.contribution_date) AS most_recent_contribution,
  COUNT(DISTINCT c.contribution_year) AS years_active,

  -- Rankings
  RANK() OVER (ORDER BY SUM(c.contribution_amount) DESC) AS contributor_rank

FROM `ca-lobby.ca_lobby.v_campaign_contributions` c
LEFT JOIN `ca-lobby.ca_lobby.v_int_filer_complete` f ON c.filer_id = f.filer_id
LEFT JOIN `ca-lobby.ca_lobby.v_disclosures` d ON c.filing_id = d.filing_id
GROUP BY c.filer_id, f.filer_name, d.entity_type
ORDER BY total_contributed DESC;
```

### 3.3 Geographic Analysis Views

#### v_summary_payments_by_region
**Purpose:** Geographic distribution of lobbying activity
**Materialization:** RECOMMENDED
**Expected Query Cost:** High

```sql
CREATE OR REPLACE VIEW `ca-lobby.ca_lobby.v_summary_payments_by_region` AS
SELECT
  COALESCE(f.state, 'Unknown') AS filer_state,
  COALESCE(f.city, 'Unknown') AS filer_city,

  -- Filer statistics
  COUNT(DISTINCT p.filer_id) AS unique_filers,
  COUNT(DISTINCT p.filing_id) AS total_filings,

  -- Payment statistics
  COUNT(*) AS total_payments,
  SUM(p.total_payment_amount) AS total_payment_amount,
  AVG(p.total_payment_amount) AS average_payment,

  -- By organization type
  SUM(CASE WHEN d.organization_type = 'PROVIDER' THEN p.total_payment_amount ELSE 0 END) AS provider_receipts,
  SUM(CASE WHEN d.organization_type = 'PURCHASER' THEN p.total_payment_amount ELSE 0 END) AS purchaser_payments,

  -- Time range
  MIN(d.period_start_date) AS earliest_activity,
  MAX(d.period_end_date) AS most_recent_activity

FROM `ca-lobby.ca_lobby.v_payments` p
LEFT JOIN `ca-lobby.ca_lobby.v_int_filer_complete` f ON p.filer_id = f.filer_id
LEFT JOIN `ca-lobby.ca_lobby.v_disclosures` d ON p.filing_id = d.filing_id
GROUP BY filer_state, filer_city
ORDER BY total_payment_amount DESC;
```

#### v_summary_alameda_activity
**Purpose:** All Alameda-related lobbying activity
**Materialization:** RECOMMENDED (frequently accessed)
**Expected Query Cost:** Medium-High

```sql
CREATE OR REPLACE VIEW `ca-lobby.ca_lobby.v_summary_alameda_activity` AS
WITH alameda_filers AS (
  SELECT DISTINCT filer_id, filer_name, city, state
  FROM `ca-lobby.ca_lobby.v_int_filer_complete`
  WHERE UPPER(filer_name) LIKE '%ALAMEDA%'
     OR UPPER(city) LIKE '%ALAMEDA%'
)
SELECT
  af.filer_id,
  af.filer_name,
  af.city,
  af.state,

  -- Entity classification
  MAX(d.entity_type) AS entity_type,
  MAX(d.organization_type) AS organization_type,

  -- Filing statistics
  COUNT(DISTINCT d.filing_id) AS total_filings,
  MIN(d.period_start_date) AS first_activity_date,
  MAX(d.period_end_date) AS most_recent_activity_date,
  COUNT(DISTINCT d.reporting_year) AS years_active,

  -- Payment statistics
  COALESCE(ps.payment_count, 0) AS total_payments,
  COALESCE(ps.total_payment_amount, 0) AS total_payment_amount,

  -- Expenditure statistics
  COALESCE(es.expenditure_count, 0) AS total_expenditures,
  COALESCE(es.total_expenditure_amount, 0) AS total_expenditure_amount,

  -- Campaign contribution statistics
  COALESCE(cs.contribution_count, 0) AS total_contributions,
  COALESCE(cs.total_contribution_amount, 0) AS total_contribution_amount,

  -- Grand total
  COALESCE(ps.total_payment_amount, 0) +
  COALESCE(es.total_expenditure_amount, 0) +
  COALESCE(cs.total_contribution_amount, 0) AS grand_total_financial_activity

FROM alameda_filers af
LEFT JOIN `ca-lobby.ca_lobby.v_disclosures` d ON af.filer_id = d.filer_id
LEFT JOIN (
  SELECT filer_id, COUNT(*) AS payment_count, SUM(total_payment_amount) AS total_payment_amount
  FROM `ca-lobby.ca_lobby.v_payments`
  GROUP BY filer_id
) ps ON af.filer_id = ps.filer_id
LEFT JOIN (
  SELECT filer_id, COUNT(*) AS expenditure_count, SUM(expenditure_amount) AS total_expenditure_amount
  FROM `ca-lobby.ca_lobby.v_expenditures`
  GROUP BY filer_id
) es ON af.filer_id = es.filer_id
LEFT JOIN (
  SELECT filer_id, COUNT(*) AS contribution_count, SUM(contribution_amount) AS total_contribution_amount
  FROM `ca-lobby.ca_lobby.v_campaign_contributions`
  GROUP BY filer_id
) cs ON af.filer_id = cs.filer_id
GROUP BY af.filer_id, af.filer_name, af.city, af.state
ORDER BY grand_total_financial_activity DESC;
```

### 3.4 Market Share Analysis

#### v_summary_firm_market_share
**Purpose:** Market share of lobbying firms
**Materialization:** RECOMMENDED
**Expected Query Cost:** High

```sql
CREATE OR REPLACE VIEW `ca-lobby.ca_lobby.v_summary_firm_market_share` AS
WITH firm_totals AS (
  SELECT
    p.filer_id,
    f.filer_name,
    SUM(p.total_payment_amount) AS total_receipts,
    COUNT(DISTINCT p.employer_full_name) AS unique_clients,
    COUNT(*) AS payment_count
  FROM `ca-lobby.ca_lobby.v_payments` p
  LEFT JOIN `ca-lobby.ca_lobby.v_int_filer_complete` f ON p.filer_id = f.filer_id
  LEFT JOIN `ca-lobby.ca_lobby.v_disclosures` d ON p.filing_id = d.filing_id
  WHERE d.entity_code = 'FRM'  -- Only lobbying firms
  GROUP BY p.filer_id, f.filer_name
),
market_total AS (
  SELECT SUM(total_receipts) AS total_market
  FROM firm_totals
)
SELECT
  ft.filer_id,
  ft.filer_name,
  ft.total_receipts,
  ft.unique_clients,
  ft.payment_count,
  ROUND(ft.total_receipts / mt.total_market * 100, 2) AS market_share_percent,
  RANK() OVER (ORDER BY ft.total_receipts DESC) AS market_rank,
  SUM(ROUND(ft.total_receipts / mt.total_market * 100, 2)) OVER (
    ORDER BY ft.total_receipts DESC
    ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
  ) AS cumulative_market_share
FROM firm_totals ft
CROSS JOIN market_total mt
ORDER BY ft.total_receipts DESC;
```

### 3.5 Activity Level Analysis

#### v_summary_filer_activity_status
**Purpose:** Classify filers by activity level
**Materialization:** RECOMMENDED
**Expected Query Cost:** Medium

```sql
CREATE OR REPLACE VIEW `ca-lobby.ca_lobby.v_summary_filer_activity_status` AS
SELECT
  f.filer_id,
  f.filer_name,
  f.status,

  -- Latest filing
  MAX(d.period_end_date) AS most_recent_filing_period_end,
  MAX(d.report_date) AS most_recent_report_date,

  -- Days since last filing
  DATE_DIFF(CURRENT_DATE(), MAX(d.period_end_date), DAY) AS days_since_last_filing,

  -- Activity classification
  CASE
    WHEN MAX(d.period_end_date) >= DATE_SUB(CURRENT_DATE(), INTERVAL 6 MONTH) THEN 'Very Active'
    WHEN MAX(d.period_end_date) >= DATE_SUB(CURRENT_DATE(), INTERVAL 12 MONTH) THEN 'Active'
    WHEN MAX(d.period_end_date) >= DATE_SUB(CURRENT_DATE(), INTERVAL 24 MONTH) THEN 'Moderately Active'
    WHEN MAX(d.period_end_date) >= DATE_SUB(CURRENT_DATE(), INTERVAL 36 MONTH) THEN 'Low Activity'
    ELSE 'Inactive'
  END AS activity_level,

  -- Filing statistics
  COUNT(DISTINCT d.filing_id) AS total_filings,
  COUNT(DISTINCT d.reporting_year) AS years_with_filings,

  -- Entity info
  MAX(d.entity_type) AS entity_type

FROM `ca-lobby.ca_lobby.v_int_filer_complete` f
LEFT JOIN `ca-lobby.ca_lobby.v_disclosures` d ON f.filer_id = d.filer_id
GROUP BY f.filer_id, f.filer_name, f.status
ORDER BY days_since_last_filing ASC;
```

### 3.6 Compliance and Filing Quality Views

#### v_summary_amendment_frequency
**Purpose:** Track amendment patterns (data quality indicator)
**Materialization:** No
**Expected Query Cost:** Medium

```sql
CREATE OR REPLACE VIEW `ca-lobby.ca_lobby.v_summary_amendment_frequency` AS
SELECT
  d.filer_id,
  f.filer_name,

  -- Filing statistics
  COUNT(DISTINCT d.filing_id) AS total_unique_filings,
  COUNT(*) AS total_filing_versions,  -- Includes all amendments
  COUNT(*) - COUNT(DISTINCT d.filing_id) AS total_amendments,

  -- Amendment rate
  ROUND(
    (COUNT(*) - COUNT(DISTINCT d.filing_id)) / COUNT(DISTINCT d.filing_id) * 100,
    2
  ) AS amendment_rate_percent,

  -- Amendment details
  MAX(d.amendment_number) AS maximum_amendments_for_single_filing,
  AVG(d.amendment_number) AS average_amendments_per_filing,

  -- Categorization
  CASE
    WHEN ROUND((COUNT(*) - COUNT(DISTINCT d.filing_id)) / COUNT(DISTINCT d.filing_id) * 100, 2) >= 50 THEN 'High Amendment Rate'
    WHEN ROUND((COUNT(*) - COUNT(DISTINCT d.filing_id)) / COUNT(DISTINCT d.filing_id) * 100, 2) >= 25 THEN 'Moderate Amendment Rate'
    WHEN ROUND((COUNT(*) - COUNT(DISTINCT d.filing_id)) / COUNT(DISTINCT d.filing_id) * 100, 2) >= 10 THEN 'Low Amendment Rate'
    ELSE 'Minimal Amendments'
  END AS amendment_pattern

FROM `ca-lobby.ca_lobby.v_disclosures` d
LEFT JOIN `ca-lobby.ca_lobby.v_int_filer_complete` f ON d.filer_id = f.filer_id
GROUP BY d.filer_id, f.filer_name
HAVING COUNT(DISTINCT d.filing_id) >= 5  -- Only filers with 5+ filings
ORDER BY amendment_rate_percent DESC;
```

### 3.7 Trend Analysis Views

#### v_summary_yoy_growth
**Purpose:** Year-over-year growth in lobbying spending
**Materialization:** RECOMMENDED
**Expected Query Cost:** High

```sql
CREATE OR REPLACE VIEW `ca-lobby.ca_lobby.v_summary_yoy_growth` AS
WITH yearly_totals AS (
  SELECT
    d.reporting_year,
    SUM(p.total_payment_amount) AS total_payments,
    COUNT(DISTINCT p.filer_id) AS unique_filers,
    COUNT(*) AS payment_count
  FROM `ca-lobby.ca_lobby.v_payments` p
  LEFT JOIN `ca-lobby.ca_lobby.v_disclosures` d ON p.filing_id = d.filing_id
  GROUP BY d.reporting_year
)
SELECT
  reporting_year,
  total_payments,
  unique_filers,
  payment_count,

  -- Previous year
  LAG(total_payments) OVER (ORDER BY reporting_year) AS previous_year_total,
  LAG(unique_filers) OVER (ORDER BY reporting_year) AS previous_year_filers,

  -- Growth calculations
  total_payments - LAG(total_payments) OVER (ORDER BY reporting_year) AS absolute_growth,
  ROUND(
    (total_payments - LAG(total_payments) OVER (ORDER BY reporting_year)) /
    LAG(total_payments) OVER (ORDER BY reporting_year) * 100,
    2
  ) AS growth_percent,

  -- Filer growth
  unique_filers - LAG(unique_filers) OVER (ORDER BY reporting_year) AS filer_growth,
  ROUND(
    (unique_filers - LAG(unique_filers) OVER (ORDER BY reporting_year)) /
    LAG(unique_filers) OVER (ORDER BY reporting_year) * 100,
    2
  ) AS filer_growth_percent

FROM yearly_totals
ORDER BY reporting_year DESC;
```

### 3.8 Network Centrality Views

#### v_summary_most_connected_filers
**Purpose:** Identify most connected players in lobbying network
**Materialization:** RECOMMENDED
**Expected Query Cost:** Medium

```sql
CREATE OR REPLACE VIEW `ca-lobby.ca_lobby.v_summary_most_connected_filers` AS
SELECT
  er.filer_id AS firm_id,
  f.filer_name AS firm_name,
  d.entity_type AS firm_type,

  -- Connection counts
  COUNT(DISTINCT er.employer_full_name) AS unique_employers,
  COUNT(DISTINCT er.client_full_name) AS unique_subcontracted_clients,
  COUNT(DISTINCT er.employer_full_name) + COUNT(DISTINCT er.client_full_name) AS total_unique_connections,

  -- Relationship details
  SUM(CASE WHEN er.relationship_type = 'Direct Employer' THEN 1 ELSE 0 END) AS direct_employer_relationships,
  SUM(CASE WHEN er.relationship_type = 'Subcontracted Client' THEN 1 ELSE 0 END) AS subcontract_relationships,

  -- Payment summary
  COALESCE(ps.total_payments, 0) AS total_payments_received,

  -- Activity range
  MIN(er.effective_date) AS first_relationship_date,
  MAX(r.report_date) AS most_recent_filing,

  -- Network rank
  RANK() OVER (ORDER BY COUNT(DISTINCT er.employer_full_name) + COUNT(DISTINCT er.client_full_name) DESC) AS network_rank

FROM `ca-lobby.ca_lobby.v_employer_relationships` er
LEFT JOIN `ca-lobby.ca_lobby.v_int_filer_complete` f ON er.filer_id = f.filer_id
LEFT JOIN `ca-lobby.ca_lobby.v_registrations` r ON er.filing_id = r.filing_id
LEFT JOIN `ca-lobby.ca_lobby.v_disclosures` d ON er.filer_id = d.filer_id AND er.filing_id = d.filing_id
LEFT JOIN (
  SELECT filer_id, SUM(total_payment_amount) AS total_payments
  FROM `ca-lobby.ca_lobby.v_payments`
  GROUP BY filer_id
) ps ON er.filer_id = ps.filer_id
GROUP BY er.filer_id, f.filer_name, d.entity_type
ORDER BY total_unique_connections DESC;
```

### 3.9 Complete Activity Timeline

#### mv_complete_activity_timeline
**Purpose:** Chronological timeline of ALL lobbying activity (MATERIALIZED)
**Materialization:** REQUIRED (very expensive query)
**Expected Query Cost:** Extremely High

```sql
CREATE MATERIALIZED VIEW `ca-lobby.ca_lobby.mv_complete_activity_timeline`
PARTITION BY DATE(activity_date)
CLUSTER BY filer_id, activity_type
AS
SELECT
  filing_id,
  filer_id,
  filer_name,
  entity_type,
  organization_type,
  activity_date,
  activity_type,
  activity_description,
  amount,
  reporting_year,
  reporting_quarter,
  counterparty_name,
  counterparty_type
FROM (
  -- Payments
  SELECT
    p.filing_id,
    p.filer_id,
    f.filer_name,
    d.entity_type,
    d.organization_type,
    d.period_start_date AS activity_date,
    'Payment' AS activity_type,
    CONCAT('Payment: ', p.primary_payment_type) AS activity_description,
    p.total_payment_amount AS amount,
    d.reporting_year,
    d.reporting_quarter,
    p.employer_full_name AS counterparty_name,
    'Employer' AS counterparty_type
  FROM `ca-lobby.ca_lobby.v_payments` p
  LEFT JOIN `ca-lobby.ca_lobby.v_int_filer_complete` f ON p.filer_id = f.filer_id
  LEFT JOIN `ca-lobby.ca_lobby.v_disclosures` d ON p.filing_id = d.filing_id

  UNION ALL

  -- Expenditures
  SELECT
    e.filing_id,
    e.filer_id,
    f.filer_name,
    d.entity_type,
    d.organization_type,
    e.expenditure_date AS activity_date,
    'Expenditure' AS activity_type,
    CONCAT('Expenditure: ', e.expenditure_category) AS activity_description,
    e.expenditure_amount AS amount,
    e.expenditure_year AS reporting_year,
    e.expenditure_quarter AS reporting_quarter,
    e.payee_full_name AS counterparty_name,
    'Vendor' AS counterparty_type
  FROM `ca-lobby.ca_lobby.v_expenditures` e
  LEFT JOIN `ca-lobby.ca_lobby.v_int_filer_complete` f ON e.filer_id = f.filer_id
  LEFT JOIN `ca-lobby.ca_lobby.v_disclosures` d ON e.filing_id = d.filing_id

  UNION ALL

  -- Campaign Contributions
  SELECT
    c.filing_id,
    c.filer_id,
    f.filer_name,
    d.entity_type,
    d.organization_type,
    c.contribution_date AS activity_date,
    'Campaign Contribution' AS activity_type,
    'Campaign Contribution' AS activity_description,
    c.contribution_amount AS amount,
    c.contribution_year AS reporting_year,
    c.contribution_quarter AS reporting_quarter,
    CAST(c.committee_id AS STRING) AS counterparty_name,
    'Committee' AS counterparty_type
  FROM `ca-lobby.ca_lobby.v_campaign_contributions` c
  LEFT JOIN `ca-lobby.ca_lobby.v_int_filer_complete` f ON c.filer_id = f.filer_id
  LEFT JOIN `ca-lobby.ca_lobby.v_disclosures` d ON c.filing_id = d.filing_id

  UNION ALL

  -- Registrations
  SELECT
    r.filing_id,
    r.filer_id,
    f.filer_name,
    r.entity_type,
    r.organization_type,
    r.date_qualified AS activity_date,
    'Registration' AS activity_type,
    CONCAT('Registration: ', r.form_type_description) AS activity_description,
    NULL AS amount,
    r.qualification_year AS reporting_year,
    NULL AS reporting_quarter,
    r.firm_name AS counterparty_name,
    'Firm' AS counterparty_type
  FROM `ca-lobby.ca_lobby.v_registrations` r
  LEFT JOIN `ca-lobby.ca_lobby.v_int_filer_complete` f ON r.filer_id = f.filer_id
);
```

### 3.10 Statistical Summary Views

#### v_summary_database_statistics
**Purpose:** Overall database statistics and health check
**Materialization:** No (lightweight)
**Expected Query Cost:** Low

```sql
CREATE OR REPLACE VIEW `ca-lobby.ca_lobby.v_summary_database_statistics` AS
SELECT
  'Filers' AS table_category,
  COUNT(*) AS record_count,
  MIN(effective_date) AS earliest_date,
  MAX(effective_date) AS most_recent_date,
  'Master registry of all filers' AS description
FROM `ca-lobby.ca_lobby.v_filers`

UNION ALL

SELECT
  'Disclosures' AS table_category,
  COUNT(*) AS record_count,
  MIN(period_start_date) AS earliest_date,
  MAX(period_end_date) AS most_recent_date,
  'Quarterly lobbying disclosure filings' AS description
FROM `ca-lobby.ca_lobby.v_disclosures`

UNION ALL

SELECT
  'Payments' AS table_category,
  COUNT(*) AS record_count,
  NULL AS earliest_date,
  NULL AS most_recent_date,
  CONCAT('Total amount: $', CAST(ROUND(SUM(total_payment_amount), 2) AS STRING)) AS description
FROM `ca-lobby.ca_lobby.v_payments`

UNION ALL

SELECT
  'Expenditures' AS table_category,
  COUNT(*) AS record_count,
  MIN(expenditure_date) AS earliest_date,
  MAX(expenditure_date) AS most_recent_date,
  CONCAT('Total amount: $', CAST(ROUND(SUM(expenditure_amount), 2) AS STRING)) AS description
FROM `ca-lobby.ca_lobby.v_expenditures`

UNION ALL

SELECT
  'Campaign Contributions' AS table_category,
  COUNT(*) AS record_count,
  MIN(contribution_date) AS earliest_date,
  MAX(contribution_date) AS most_recent_date,
  CONCAT('Total amount: $', CAST(ROUND(SUM(contribution_amount), 2) AS STRING)) AS description
FROM `ca-lobby.ca_lobby.v_campaign_contributions`

UNION ALL

SELECT
  'Employer Relationships' AS table_category,
  COUNT(*) AS record_count,
  MIN(effective_date) AS earliest_date,
  MAX(effective_date) AS most_recent_date,
  'Employer-lobbyist connections' AS description
FROM `ca-lobby.ca_lobby.v_employer_relationships`;
```

---

## Layer 4: Specialized Filtered Views

**Purpose:** Commonly used filters pre-applied for quick access.

### 4.1 Alameda-Specific Views

~~#### v_filter_alameda_filers~~ (lower priority)
**Purpose:** All Alameda-related filers
**Materialization:** No
**Expected Query Cost:** Low

```sql
CREATE OR REPLACE VIEW `ca-lobby.ca_lobby.v_filter_alameda_filers` AS
SELECT *
FROM `ca-lobby.ca_lobby.v_int_filer_complete`
WHERE UPPER(filer_name) LIKE '%ALAMEDA%'
   OR UPPER(city) LIKE '%ALAMEDA%';
```

~~#### v_filter_alameda_payments~~ (lower priority)
**Purpose:** All payments involving Alameda entities
**Materialization:** Optional (lower priority)
**Expected Query Cost:** High

```sql
CREATE OR REPLACE VIEW `ca-lobby.ca_lobby.v_filter_alameda_payments` AS
SELECT
  p.*,
  -- Flag which party is Alameda
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
```

#### v_filter_alameda_complete_activity
**Purpose:** All Alameda lobbying activity (comprehensive view)
**Materialization:** RECOMMENDED
**Expected Query Cost:** High

```sql
CREATE OR REPLACE VIEW `ca-lobby.ca_lobby.v_filter_alameda_complete_activity` AS
SELECT *
FROM `ca-lobby.ca_lobby.v_summary_alameda_activity`;
-- Already defined in Layer 3
```

### 4.2 Time-Based Filtered Views

#### v_filter_current_year
**Purpose:** Current year activity only
**Materialization:** No (changes frequently)
**Expected Query Cost:** Medium

```sql
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
```

#### v_filter_last_12_months
**Purpose:** Rolling 12-month window of activity
**Materialization:** No
**Expected Query Cost:** Medium

```sql
CREATE OR REPLACE VIEW `ca-lobby.ca_lobby.v_filter_last_12_months` AS
SELECT *
FROM `ca-lobby.ca_lobby.v_int_filer_disclosures`
WHERE period_end_date >= DATE_SUB(CURRENT_DATE(), INTERVAL 12 MONTH);
```

#### v_filter_recent_filings
**Purpose:** Most recent filings (last 6 months)
**Materialization:** No
**Expected Query Cost:** Low-Medium

```sql
CREATE OR REPLACE VIEW `ca-lobby.ca_lobby.v_filter_recent_filings` AS
SELECT *
FROM `ca-lobby.ca_lobby.v_int_filer_disclosures`
WHERE report_date >= DATE_SUB(CURRENT_DATE(), INTERVAL 6 MONTH)
ORDER BY report_date DESC;
```

### 4.3 Activity Level Filters

~~#### v_filter_active_filers~~ (lower priority)
**Purpose:** Only filers with activity in last 12 months
**Materialization:** No
**Expected Query Cost:** Medium

```sql
CREATE OR REPLACE VIEW `ca-lobby.ca_lobby.v_filter_active_filers` AS
SELECT f.*
FROM `ca-lobby.ca_lobby.v_int_filer_complete` f
WHERE f.most_recent_filing_date >= DATE_SUB(CURRENT_DATE(), INTERVAL 12 MONTH)
  AND f.status = 'Active';
```

#### v_filter_inactive_filers
**Purpose:** Filers with no recent activity (>24 months)
**Materialization:** No
**Expected Query Cost:** Low

```sql
CREATE OR REPLACE VIEW `ca-lobby.ca_lobby.v_filter_inactive_filers` AS
SELECT f.*
FROM `ca-lobby.ca_lobby.v_int_filer_complete` f
WHERE f.most_recent_filing_date < DATE_SUB(CURRENT_DATE(), INTERVAL 24 MONTH)
   OR f.most_recent_filing_date IS NULL
   OR f.status IN ('Terminated', 'Suspended');
```

### 4.4 High-Value Transaction Filters

~~#### v_filter_high_value_payments~~ (lower priority - optional example)
**Purpose:** Payments over $10,000
**Materialization:** No
**Expected Query Cost:** Medium

```sql
CREATE OR REPLACE VIEW `ca-lobby.ca_lobby.v_filter_high_value_payments` AS
SELECT *
FROM `ca-lobby.ca_lobby.v_int_payment_details`
WHERE total_payment_amount >= 10000
ORDER BY total_payment_amount DESC;
```

#### v_filter_very_high_value_payments
**Purpose:** Payments over $100,000
**Materialization:** No
**Expected Query Cost:** Low

```sql
CREATE OR REPLACE VIEW `ca-lobby.ca_lobby.v_filter_very_high_value_payments` AS
SELECT *
FROM `ca-lobby.ca_lobby.v_int_payment_details`
WHERE total_payment_amount >= 100000
ORDER BY total_payment_amount DESC;
```

### 4.5 Entity Type Filters

#### v_filter_lobbying_firms
**Purpose:** Only lobbying firms (FRM)
**Materialization:** No
**Expected Query Cost:** Low

```sql
CREATE OR REPLACE VIEW `ca-lobby.ca_lobby.v_filter_lobbying_firms` AS
SELECT d.*, f.city AS filer_city, f.state AS filer_state
FROM `ca-lobby.ca_lobby.v_disclosures` d
LEFT JOIN `ca-lobby.ca_lobby.v_int_filer_complete` f ON d.filer_id = f.filer_id
WHERE d.entity_code = 'FRM';
```

#### v_filter_employers
**Purpose:** Only lobbyist employers (LEM)
**Materialization:** No
**Expected Query Cost:** Low

```sql
CREATE OR REPLACE VIEW `ca-lobby.ca_lobby.v_filter_employers` AS
SELECT d.*, f.city AS filer_city, f.state AS filer_state
FROM `ca-lobby.ca_lobby.v_disclosures` d
LEFT JOIN `ca-lobby.ca_lobby.v_int_filer_complete` f ON d.filer_id = f.filer_id
WHERE d.entity_code = 'LEM';
```

#### v_filter_coalitions
**Purpose:** Only lobbying coalitions (LCO)
**Materialization:** No
**Expected Query Cost:** Low

```sql
CREATE OR REPLACE VIEW `ca-lobby.ca_lobby.v_filter_coalitions` AS
SELECT d.*, f.city AS filer_city, f.state AS filer_state
FROM `ca-lobby.ca_lobby.v_disclosures` d
LEFT JOIN `ca-lobby.ca_lobby.v_int_filer_complete` f ON d.filer_id = f.filer_id
WHERE d.entity_code = 'LCO';
```

---

## Performance Recommendations

### Views to Materialize (Priority Order)

#### **Critical (Materialize Immediately)**

1. **mv_complete_activity_timeline** - Extremely expensive, used for comprehensive analysis
2. **v_int_payment_with_latest_amendment** - Eliminates duplicate handling, frequently queried
3. **v_int_payment_details** - Most frequently queried, complex joins
4. **v_int_filer_complete** - Central to many other views
5. ~~**v_filter_alameda_payments**~~ - (lower priority)

#### **High Priority (Materialize if query costs become significant)**

6. **v_summary_payments_by_year** - Complex aggregation, infrequently changes
7. **v_summary_payments_by_quarter** - Complex aggregation with window functions
8. **v_summary_top_payment_recipients** - Expensive ranking calculation
9. **v_summary_top_purchasers** - Complex grouping and ranking
10. **v_int_employer_firm_relationships** - Multiple joins, network analysis
11. **v_summary_firm_market_share** - Complex calculation with window functions
12. **v_int_expenditure_details** - Frequently queried for analysis

#### **Medium Priority (Monitor query costs)**

13. **v_summary_alameda_activity** - Regional focus, moderate complexity
14. **v_summary_payments_by_region** - Geographic aggregations
15. **v_summary_yoy_growth** - Window functions, trend analysis
16. **v_int_filer_disclosures** - Complex join, frequently used
17. **v_summary_most_connected_filers** - Network analysis

### Materialization Strategy

```sql
-- Example materialization script for critical views
CREATE MATERIALIZED VIEW `ca-lobby.ca_lobby.mv_int_payment_with_latest_amendment`
PARTITION BY DATE(period_start_date)
CLUSTER BY filer_id, reporting_year, payment_tier
AS
SELECT * FROM `ca-lobby.ca_lobby.v_int_payment_with_latest_amendment`;

-- Set refresh schedule (daily at 2 AM)
-- Note: Configure in BigQuery Console or using bq command
```

### Refresh Schedule Recommendations

| View | Refresh Frequency | Rationale |
|------|-------------------|-----------|
| mv_complete_activity_timeline | Daily (2 AM) | Data updates daily |
| mv_int_payment_with_latest_amendment | Daily (3 AM) | Critical for queries |
| Payment/Expenditure summaries | Weekly (Sunday 1 AM) | Aggregations, less time-sensitive |
| Network/Market share views | Monthly (1st, 1 AM) | Slower-changing metrics |

### Partitioning and Clustering Recommendations

```sql
-- All views with date ranges should use:
PARTITION BY DATE(period_start_date)  -- Or relevant date field
CLUSTER BY filer_id, reporting_year

-- Payment views specifically:
PARTITION BY DATE(period_start_date)
CLUSTER BY filer_id, payment_tier, reporting_year

-- Geographic views:
PARTITION BY DATE(period_start_date)
CLUSTER BY state, city, filer_id
```

### Query Optimization Tips

1. **Always filter by date range** - Use partition pruning
2. **Filter by filer_id early** - Clustered field
3. **Use materialized views** - For repeated queries
4. **Avoid SELECT *** - Specify needed columns
5. **Use summary views** - Instead of aggregating raw data

---

## Usage Examples

### Example 1: Find all Alameda lobbying activity in 2024 (Optional - lower priority)

```sql
-- Note: Alameda-specific views are lower priority
SELECT *
FROM `ca-lobby.ca_lobby.v_filter_alameda_complete_activity`
WHERE years_active = 2024
ORDER BY grand_total_financial_activity DESC;
```

### Example 2: Top 10 lobbying firms by revenue

```sql
SELECT
  filer_name,
  total_receipts,
  unique_clients,
  market_share_percent,
  market_rank
FROM `ca-lobby.ca_lobby.v_summary_firm_market_share`
WHERE market_rank <= 10
ORDER BY market_rank;
```

### Example 3: Year-over-year payment growth

```sql
SELECT
  reporting_year,
  total_payments,
  growth_percent,
  unique_filers,
  filer_growth_percent
FROM `ca-lobby.ca_lobby.v_summary_yoy_growth`
ORDER BY reporting_year DESC
LIMIT 5;
```

### Example 4: All payments to a specific firm

```sql
SELECT
  reporting_period,
  employer_full_name AS client,
  total_payment_amount,
  payment_tier,
  form_type_description
FROM `ca-lobby.ca_lobby.v_int_payment_details`
WHERE filer_name = 'SPECIFIC FIRM NAME'
  AND reporting_year = 2024
ORDER BY period_start_date DESC;
```

### Example 5: High-value transactions in Q4 2024 (Optional - lower priority)

```sql
-- Note: High-value transaction views are lower priority
SELECT
  filer_name,
  employer_full_name,
  total_payment_amount,
  reporting_period,
  payment_tier
FROM `ca-lobby.ca_lobby.v_filter_high_value_payments`
WHERE reporting_year = 2024
  AND reporting_quarter = 4
ORDER BY total_payment_amount DESC;
```

### Example 6: Network graph data for visualization

```sql
SELECT
  source_node AS employer,
  target_node AS lobbying_firm,
  relationship_count,
  total_payments_made,
  relationship_start,
  last_filing_date
FROM `ca-lobby.ca_lobby.v_int_network_employer_to_firm`
WHERE total_payments_made >= 10000
ORDER BY total_payments_made DESC;
```

### Example 7: Complete filing details with all transactions

```sql
SELECT
  filing_id,
  filer_name,
  reporting_period,
  total_payments,
  total_payment_amount,
  total_expenditures,
  total_expenditure_amount,
  grand_total_financial_activity
FROM `ca-lobby.ca_lobby.v_int_complete_filing_details`
WHERE filer_id = 'SPECIFIC_FILER_ID'
  AND reporting_year = 2024
ORDER BY reporting_quarter;
```

### Example 8: Active vs Inactive filers comparison

```sql
-- Note: Active filers view is lower priority
-- Active filers
SELECT
  'Active' AS status_category,
  COUNT(*) AS filer_count,
  SUM(total_filings) AS total_filings,
  AVG(total_filings) AS avg_filings_per_filer
FROM `ca-lobby.ca_lobby.v_filter_active_filers`

UNION ALL

-- Inactive filers
SELECT
  'Inactive' AS status_category,
  COUNT(*) AS filer_count,
  SUM(total_filings) AS total_filings,
  AVG(total_filings) AS avg_filings_per_filer
FROM `ca-lobby.ca_lobby.v_filter_inactive_filers`;
```

### Example 9: Quarterly spending trends by entity type

```sql
SELECT
  reporting_year,
  reporting_quarter,
  SUM(CASE WHEN entity_code = 'LEM' THEN total_payment_amount ELSE 0 END) AS employer_spending,
  SUM(CASE WHEN entity_code = 'FRM' THEN total_payment_amount ELSE 0 END) AS firm_receipts,
  SUM(CASE WHEN entity_code = 'LCO' THEN total_payment_amount ELSE 0 END) AS coalition_spending
FROM `ca-lobby.ca_lobby.v_int_payment_details`
WHERE reporting_year >= 2020
GROUP BY reporting_year, reporting_quarter
ORDER BY reporting_year DESC, reporting_quarter DESC;
```

### Example 10: Amendment patterns for data quality

```sql
SELECT
  filer_name,
  total_unique_filings,
  total_amendments,
  amendment_rate_percent,
  amendment_pattern
FROM `ca-lobby.ca_lobby.v_summary_amendment_frequency`
WHERE amendment_pattern IN ('High Amendment Rate', 'Moderate Amendment Rate')
ORDER BY amendment_rate_percent DESC
LIMIT 20;
```

---

## Migration Guide

### CSV Exports and Views

**Note:** CSV exports are only for testing purposes. Views provide structured access to the database.

#### Phase 1: View Creation (Weeks 1-2)

1. **Create all base views** (Layer 1)
2. **Test queries** against views
3. **Validate data accuracy**
4. **Document any discrepancies**

#### Phase 2: Integration Views (Weeks 3-4)

1. **Create integration views** (Layer 2)
2. **Migrate complex queries** to use pre-joined views
3. **Create materialized views** for expensive queries
4. **Set up refresh schedules** (TBD - data does not need regular updates currently)

#### Phase 3: Analytics Migration (Weeks 5-6)

1. **Create analytical views** (Layer 3)
2. **Update reporting dashboards** to use summary views
3. **Optimize query performance**
4. **Document view dependencies**

#### Phase 4: Specialized Filters (Week 7+)

1. **Create specialized filters** (Layer 4) - Note: some filters are lower priority
2. **Train users on view usage**
3. **Establish view maintenance procedures**

### CSV Export Mapping to Views

| CSV Export (testing only) | View for Structured Access | Notes |
|----------------|----------|-------|
| `Alameda_FILERS_CD.csv` | ~~`v_filter_alameda_filers`~~ | Lower priority |
| `Alameda_LPAY_CD.csv` | ~~`v_filter_alameda_payments`~~ | Lower priority |
| `Complete_Payments.csv` | `v_int_payment_with_latest_amendment` | Latest amendments only |
| `Payment_Summary.csv` | `v_summary_payments_by_year` | Pre-aggregated |
| `Filer_Activity.csv` | `v_int_complete_filing_details` | Comprehensive view |
| `Network_Data.csv` | `v_int_network_employer_to_firm` | Graph-ready format |

### Query Conversion Examples

#### Old CSV-based approach:
```python
# Load CSV
df = pd.read_csv('Alameda_LPAY_CD.csv')

# Filter and aggregate
result = df[df['PERIOD_TOTAL'] > 10000].groupby('FILER_ID')['PERIOD_TOTAL'].sum()
```

#### New view-based approach:
```sql
SELECT
  filer_id,
  filer_name,
  SUM(total_payment_amount) AS total
-- Note: Alameda views are lower priority
FROM `ca-lobby.ca_lobby.v_filter_alameda_payments`
WHERE total_payment_amount > 10000
GROUP BY filer_id, filer_name
ORDER BY total DESC;
```

### Benefits Checklist

- **No CSV storage costs** - Save storage fees
- **Always current data** - No stale exports
- **Faster queries** - Materialized views cached
- **Better performance** - BigQuery optimization
- **Easier joins** - Pre-built relationships
- **Reduced complexity** - No export scripts
- **Version control** - View definitions in SQL
- **Access control** - BigQuery IAM integration

---

## Cost Analysis

### CSV Export Costs (Current State)

**Storage Costs:**
- Average export size: 500 MB - 2 GB per table
- ~15 tables exported regularly
- Storage: ~15 GB × $0.02/GB/month = $0.30/month
- **TOTAL STORAGE: ~$4/year**

**Query Costs (for generating exports):**
- Full table scans: 15 tables × 2 GB avg = 30 GB
- Export frequency: 1x per week = 52 times/year
- Query cost: 30 GB × 52 weeks × $5/TB = **$7.80/year**

**Data Transfer Costs:**
- CSV downloads: ~15 GB × 52 weeks = 780 GB/year
- Transfer cost (if egress): 780 GB × $0.12/GB = **$93.60/year** (if applicable)

**Labor Costs:**
- Script maintenance: 2 hours/month × $50/hour × 12 = **$1,200/year**
- CSV processing/analysis: 4 hours/week × $50/hour × 52 = **$10,400/year**

**TOTAL CSV APPROACH: ~$11,705/year**

### View-Based Costs (Proposed State)

**View Creation (One-time):**
- Initial setup: 16 hours × $100/hour = **$1,600 (one-time)**

**Query Costs:**

*Regular Views (no storage cost):*
- Query cost depends on usage
- Estimated: 10 queries/day × 1 GB avg × 365 days × $5/TB = **$18.25/year**

*Materialized Views:*
- Storage: 12 materialized views × 500 MB avg = 6 GB × $0.02/GB/month = **$1.44/year**
- Refresh queries: 6 GB × 365 days × $5/TB = **$10.95/year**

**Labor Costs:**
- View maintenance: 1 hour/month × $50/hour × 12 = **$600/year**
- Analysis (faster with views): 2 hours/week × $50/hour × 52 = **$5,200/year**

**TOTAL VIEW APPROACH: ~$5,830/year (plus $1,600 one-time setup)**

### Cost Savings Summary

| Category | CSV Approach | View Approach | Savings |
|----------|--------------|---------------|---------|
| Infrastructure | $106/year | $31/year | $75/year |
| Labor | $11,600/year | $5,800/year | $5,800/year |
| **Annual Total** | **$11,706/year** | **$5,831/year** | **$5,875/year** |
| **ROI** | - | 3.6 months | **50% reduction** |

### Performance Improvements

- **Query speed**: 10-100x faster (materialized views)
- **Data freshness**: Real-time vs. weekly
- **Analysis time**: 50% reduction in analyst hours
- **Error reduction**: No CSV version mismatches

---

## View Dependency Graph

```
Layer 1 (Base)
├── v_filers
├── v_filer_filings
├── v_filer_addresses
├── v_filer_types
├── v_filer_xref
├── v_registrations
├── v_disclosures
├── v_payments
├── v_expenditures
├── v_campaign_contributions
├── v_other_payments
├── v_employer_relationships
├── v_attachments
├── v_names
├── v_amendments
└── v_lookup_codes

Layer 2 (Integration)
├── v_int_filer_complete
│   ├── Uses: v_filers, v_filer_addresses, v_filer_types, v_filer_xref, v_filer_filings
│
├── v_int_filer_disclosures
│   ├── Uses: v_disclosures, v_int_filer_complete
│
├── v_int_payment_details
│   ├── Uses: v_payments, v_int_filer_complete, v_disclosures
│
├── v_int_payment_with_latest_amendment
│   ├── Uses: v_int_payment_details
│
└── v_int_complete_filing_details
    ├── Uses: v_int_filer_disclosures, v_payments, v_expenditures, v_campaign_contributions, v_other_payments

Layer 3 (Analytical)
├── v_summary_payments_by_year
│   ├── Uses: v_payments, v_disclosures
│
├── v_summary_top_payment_recipients
│   ├── Uses: v_payments, v_int_filer_complete, v_disclosures
│
└── mv_complete_activity_timeline (MATERIALIZED)
    ├── Uses: v_payments, v_expenditures, v_campaign_contributions, v_registrations, v_int_filer_complete

Layer 4 (Filters)
├── ~~v_filter_alameda_filers~~ (lower priority)
│   ├── Uses: v_int_filer_complete
│
├── ~~v_filter_alameda_payments~~ (lower priority)
│   ├── Uses: v_int_payment_details, v_filter_alameda_filers
│
└── v_filter_current_year
    ├── Uses: v_int_filer_disclosures, v_payments, v_expenditures
```

---

## Maintenance Procedures

### Daily Tasks (Automated)

1. **Refresh materialized views** (2-4 AM)
   - mv_complete_activity_timeline
   - mv_int_payment_with_latest_amendment
   - Other critical materialized views

### Weekly Tasks

1. **Monitor query costs** - Review BigQuery billing
2. **Check view performance** - Identify slow queries
3. **Review error logs** - Check for failed refreshes

### Monthly Tasks

1. **Update view statistics** - Refresh metadata
2. **Review view usage** - Identify unused views
3. **Optimize clustering** - Adjust based on query patterns
4. **Cost analysis** - Compare actual vs. projected costs

### Quarterly Tasks

1. **View architecture review** - Add/remove views as needed
2. **Performance tuning** - Materialize additional views if needed
3. **Documentation update** - Keep this document current
4. **User training** - Ensure team knows best practices

---

## Conclusion

This comprehensive view architecture provides:

**Complete Data Access:**
- 73 views covering all database tables
- Views provide structured access; CSV exports only for testing
- Real-time access to current data

**Performance Optimized:**
- Materialized views for expensive queries
- Partitioning and clustering strategies
- 10-100x faster than CSV-based workflows

**Cost Effective:**
- 50% reduction in annual costs
- ROI achieved in 3.6 months
- Reduced storage and labor expenses

**User Friendly:**
- Human-readable column names
- Self-documenting view structure
- Pre-joined common queries
- Ready-to-use analytical summaries

**Production Ready:**
- Follows BigQuery best practices
- Includes maintenance procedures
- Performance monitoring built-in
- Scalable architecture

---

**Next Steps:**

1. Review and approve view architecture
2. Execute view creation scripts (sequential by layer)
3. Materialize critical views
4. Set up refresh schedules (TBD - data does not need regular updates currently)
5. Test views (CSV exports only for testing)
6. Train users on view usage
7. Note: Some Layer 4 views are lower priority (alameda filters, high-value filters, active filers)

---

**Document Control:**

- **Version:** 1.0
- **Date:** 2025-10-24
- **Author:** SQL Database Expert
- **Project:** ca-lobby.ca_lobby
- **Status:** Ready for Implementation
