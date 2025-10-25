# BigQuery Optimization Plan for California Lobbying Database

**Generated**: October 24, 2025
**Platform**: Google BigQuery
**Project**: ca-lobby
**Dataset**: ca_lobby
**Author**: SQL Database Expert

---

## Executive Summary

This comprehensive optimization plan transforms traditional SQL Server indexing strategies into BigQuery-native performance optimizations. By leveraging BigQuery's columnar architecture, partitioning, clustering, and materialized views, we can achieve:

### Expected Performance Improvements

| Metric | Before Optimization | After Optimization | Improvement |
|--------|-------------------|-------------------|-------------|
| Full table scans (text search) | 30-120 seconds | 2-5 seconds | 90-95% faster |
| Complex joins (3+ tables) | 60-180 seconds | 5-15 seconds | 85-92% faster |
| Date range queries | 45-90 seconds | 1-3 seconds | 95-98% faster |
| Aggregate queries | 30-60 seconds | 2-8 seconds | 85-90% faster |
| **Query costs** | **High slot usage** | **60-80% reduction** | **Major savings** |

### Key Benefits

1. **No Downtime Required**: All optimizations are non-destructive
2. **Cost Reduction**: 60-80% reduction in query processing costs
3. **Improved User Experience**: Sub-5-second response times for most queries
4. **Scalability**: Performance remains consistent as data grows
5. **Maintenance-Free**: BigQuery handles optimization automatically

---

## Table of Contents

1. [BigQuery Architecture Overview](#bigquery-architecture-overview)
2. [Why BigQuery is Different](#why-bigquery-is-different)
3. [Optimization Strategy](#optimization-strategy)
4. [Table-by-Table Implementation](#table-by-table-implementation)
5. [Materialized Views](#materialized-views)
6. [Search Indexes](#search-indexes)
7. [Query Optimization Guide](#query-optimization-guide)
8. [Testing and Validation](#testing-and-validation)
9. [Cost Analysis](#cost-analysis)
10. [Rollback Procedures](#rollback-procedures)
11. [Maintenance Schedule](#maintenance-schedule)
12. [Implementation Timeline](#implementation-timeline)

---

## BigQuery Architecture Overview

### How BigQuery Differs from Traditional Databases

BigQuery uses a **columnar storage** architecture fundamentally different from traditional row-based databases (SQL Server, MySQL, PostgreSQL):

#### Traditional RDBMS (Row-Based)
```
Row 1: [ID=1, Name="Alameda", Date=2024-01-15, Amount=5000]
Row 2: [ID=2, Name="Oakland", Date=2024-01-16, Amount=3000]
Row 3: [ID=3, Name="Alameda", Date=2024-02-01, Amount=7000]
```
- Reads entire rows even if you only need one column
- B-Tree indexes speed up row lookups
- Optimized for OLTP (transactional workloads)

#### BigQuery (Column-Based)
```
ID Column:     [1, 2, 3]
Name Column:   ["Alameda", "Oakland", "Alameda"]
Date Column:   [2024-01-15, 2024-01-16, 2024-02-01]
Amount Column: [5000, 3000, 7000]
```
- Reads only the columns you query
- No traditional indexes needed
- Optimized for OLAP (analytical workloads)
- Massively parallel processing

### BigQuery Performance Techniques

Instead of indexes, BigQuery uses:

1. **Table Partitioning**: Divides tables into segments (usually by date)
2. **Table Clustering**: Orders data by frequently filtered columns
3. **Materialized Views**: Pre-computed query results
4. **Search Indexes**: Full-text search optimization (Beta)
5. **BI Engine**: In-memory analysis for small datasets

---

## Why BigQuery is Different

### What NOT to Do

❌ **Don't create B-Tree indexes** - BigQuery doesn't use them
❌ **Don't create full-text indexes** - Use Search Indexes instead
❌ **Don't use composite indexes** - Use clustering instead
❌ **Don't create filtered indexes** - Use partitioning instead

### What TO Do

✅ **Partition by DATE columns** - Dramatically reduces data scanned
✅ **Cluster by filtered columns** - Orders data for efficient scanning
✅ **Create materialized views** - Pre-compute common aggregations
✅ **Use Search Indexes** - Enable fast text search
✅ **Optimize query structure** - Use best practices for columnar databases

### Translation Table: SQL Server → BigQuery

| SQL Server Concept | BigQuery Equivalent | Purpose |
|-------------------|-------------------|---------|
| Clustered Index (PK) | Table Clustering (4 columns max) | Physical data ordering |
| Non-Clustered Index | Additional Clustering Columns | Access pattern optimization |
| Filtered Index | Table Partitioning | Partition pruning |
| Full-Text Index | Search Index (Beta) | Text search |
| Indexed View | Materialized View | Pre-computed results |
| Statistics | Automatic (no management) | Query optimization |
| Index Maintenance | N/A (automatic) | No maintenance needed |

---

## Optimization Strategy

### Priority Ranking

Tables are prioritized by:
1. **Query Frequency** (how often accessed)
2. **Data Volume** (larger = more benefit)
3. **Join Complexity** (hub tables = higher priority)
4. **User Impact** (dashboard queries = higher priority)

### Priority 1: CRITICAL (Implement Week 1)
1. **CVR_LOBBY_DISCLOSURE_CD** - Primary disclosure data (high volume, frequent queries)
2. **LPAY_CD** - Payment transactions (high volume, financial analysis)
3. **FILERS_CD / filername_cd** - Master registry (join hub, text search)
4. **CVR_REGISTRATION_CD** - Registration data (moderate volume, frequent joins)

### Priority 2: HIGH (Implement Week 2)
5. **LEXP_CD** - Expenditure transactions (high volume)
6. **LEMP_CD** - Employer relationships (moderate volume, complex joins)
7. **FILER_FILINGS_CD** - Filing index (join table)

### Priority 3: MEDIUM (Implement Week 3)
8. **LCCM_CD** - Campaign contributions (moderate queries)
9. **LOTH_CD** - Other payments (lower volume)
10. **FILER_ADDRESS_CD** - Address data (lookup table)

### Priority 4: LOW (Implement Week 4)
11. **LATT_CD** - Attachments (low query frequency)
12. **LOBBY_AMENDMENTS_CD** - Amendments (tracking table)
13. **NAMES_CD** - Name registry (reference table)

---

## Table-by-Table Implementation

### Priority 1: CVR_LOBBY_DISCLOSURE_CD

**Current State**: 7,560+ Alameda records, millions total
**Primary Use**: Disclosure cover pages, frequent text searches, date range filtering
**Optimization**: Partition by RPT_DATE, cluster by FILER_ID and ENTITY_CD

#### Implementation Script

```sql
-- ============================================================================
-- TABLE: CVR_LOBBY_DISCLOSURE_CD
-- OPTIMIZATION: Partition by reporting date, cluster by filer and entity
-- IMPACT: High - Primary query table with frequent date/filer filtering
-- ============================================================================

-- Step 1: Create optimized table with partitioning and clustering
CREATE OR REPLACE TABLE `ca-lobby.ca_lobby.CVR_LOBBY_DISCLOSURE_CD_OPTIMIZED`
PARTITION BY DATE(RPT_DATE)
CLUSTER BY FILER_ID, ENTITY_CD, FILING_ID, FORM_TYPE
OPTIONS(
  description = "Optimized lobbying disclosure cover pages - partitioned by reporting date",
  require_partition_filter = FALSE  -- Set TRUE to enforce partition filtering
)
AS
SELECT * FROM `ca-lobby.ca_lobby.CVR_LOBBY_DISCLOSURE_CD`;

-- Step 2: Verify table structure
SELECT
  table_name,
  partition_expiration_days,
  clustering_fields,
  ROUND(size_bytes / POW(10, 9), 2) as size_gb
FROM `ca-lobby.ca_lobby.INFORMATION_SCHEMA.TABLES`
WHERE table_name = 'CVR_LOBBY_DISCLOSURE_CD_OPTIMIZED';

-- Step 3: Test query performance (compare before/after)
-- BEFORE optimization
SELECT COUNT(*) as record_count, AVG(CAST(TOTAL_FEES AS FLOAT64)) as avg_fees
FROM `ca-lobby.ca_lobby.CVR_LOBBY_DISCLOSURE_CD`
WHERE RPT_DATE BETWEEN '2023-01-01' AND '2025-12-31'
  AND ENTITY_CD = 'FRM'
  AND FILER_ID = 1234567;  -- Example filer

-- AFTER optimization
SELECT COUNT(*) as record_count, AVG(CAST(TOTAL_FEES AS FLOAT64)) as avg_fees
FROM `ca-lobby.ca_lobby.CVR_LOBBY_DISCLOSURE_CD_OPTIMIZED`
WHERE RPT_DATE BETWEEN '2023-01-01' AND '2025-12-31'
  AND ENTITY_CD = 'FRM'
  AND FILER_ID = 1234567;

-- Step 4: Once verified, swap tables (OPTIONAL - see rollback section)
-- Not recommended initially - query both tables in parallel first
```

**Rationale**:
- **RPT_DATE partitioning**: Most queries filter by date ranges (quarters, years)
- **FILER_ID clustering**: Primary key, used in nearly all queries and joins
- **ENTITY_CD clustering**: Frequently filtered (FRM, LEM, LBY, etc.)
- **FILING_ID clustering**: Join key for detail tables
- **FORM_TYPE clustering**: Common filter for specific forms

**Expected Performance**:
- Date range queries: **90% faster** (partition pruning)
- Filer lookups: **70% faster** (clustering)
- Cost reduction: **80%** (only scan relevant partitions)

---

### Priority 1: LPAY_CD

**Current State**: 8,305+ Alameda records, high transaction volume
**Primary Use**: Payment tracking, financial analysis, aggregate queries
**Optimization**: No natural DATE column - use FILING_ID to join to disclosure dates

#### Implementation Script

```sql
-- ============================================================================
-- TABLE: LPAY_CD
-- OPTIMIZATION: Cluster by filer and filing (no date column for partitioning)
-- IMPACT: High - Transaction table with frequent aggregations
-- ============================================================================

-- Note: LPAY_CD doesn't have a natural date column
-- Strategy: Cluster by frequently filtered columns, consider denormalizing RPT_DATE

-- Option 1: Basic clustering (no partitioning)
CREATE OR REPLACE TABLE `ca-lobby.ca_lobby.LPAY_CD_OPTIMIZED`
CLUSTER BY FILER_ID, FILING_ID, AMEND_ID
OPTIONS(
  description = "Optimized payment records - clustered by filer and filing"
)
AS
SELECT * FROM `ca-lobby.ca_lobby.LPAY_CD`;

-- Option 2: Denormalize with RPT_DATE for partitioning (RECOMMENDED)
CREATE OR REPLACE TABLE `ca-lobby.ca_lobby.LPAY_CD_OPTIMIZED_WITH_DATE`
PARTITION BY DATE(RPT_DATE)
CLUSTER BY FILER_ID, FILING_ID, AMEND_ID
OPTIONS(
  description = "Optimized payment records with denormalized report date for partitioning"
)
AS
SELECT
  lp.*,
  cvr.RPT_DATE,
  cvr.FROM_DATE,
  cvr.THRU_DATE
FROM `ca-lobby.ca_lobby.LPAY_CD` lp
LEFT JOIN `ca-lobby.ca_lobby.CVR_LOBBY_DISCLOSURE_CD` cvr
  ON lp.FILING_ID = cvr.FILING_ID;

-- Verify clustering effectiveness
SELECT
  table_name,
  clustering_fields,
  ROUND(size_bytes / POW(10, 9), 2) as size_gb,
  row_count
FROM `ca-lobby.ca_lobby.INFORMATION_SCHEMA.TABLES`
WHERE table_name LIKE 'LPAY_CD_OPTIMIZED%';

-- Test query performance
SELECT
  FILER_ID,
  SUM(CAST(AMOUNT AS FLOAT64)) as total_payments,
  SUM(CAST(CUM_YTD AS FLOAT64)) as total_ytd,
  COUNT(*) as payment_count
FROM `ca-lobby.ca_lobby.LPAY_CD_OPTIMIZED_WITH_DATE`
WHERE RPT_DATE BETWEEN '2023-01-01' AND '2025-12-31'
  AND FILER_ID IN (SELECT FILER_ID FROM `ca-lobby.ca_lobby.filername_cd` WHERE UPPER(NAML) LIKE '%ALAMEDA%')
GROUP BY FILER_ID;
```

**Rationale**:
- **Denormalization**: Adding RPT_DATE enables powerful partition pruning
- **FILER_ID clustering**: Used in all aggregations and filters
- **FILING_ID clustering**: Join key to disclosure tables
- **AMEND_ID clustering**: Track latest amendments efficiently

**Expected Performance**:
- Aggregate queries: **85% faster** (clustering + partitioning)
- Join queries: **75% faster** (co-located data)
- Cost reduction: **70%** (partition pruning when filtering by date)

**Trade-offs**:
- **Pros**: Dramatic performance improvement, enables partition pruning
- **Cons**: 30% storage increase (duplicate RPT_DATE), update complexity
- **Recommendation**: Use denormalized version - query performance is worth it

---

### Priority 1: FILERS_CD / filername_cd

**Current State**: 46,679 Alameda records, millions total (master registry)
**Primary Use**: Text searches on names, join hub for all tables
**Optimization**: Cluster by FILER_ID, add Search Index for text search

#### Implementation Script

```sql
-- ============================================================================
-- TABLE: filername_cd (FILERS_CD)
-- OPTIMIZATION: Clustering + Search Index for text search
-- IMPACT: Critical - Join hub and primary text search table
-- ============================================================================

-- Step 1: Create clustered version
CREATE OR REPLACE TABLE `ca-lobby.ca_lobby.filername_cd_OPTIMIZED`
CLUSTER BY FILER_ID, FILER_TYPE, STATUS
OPTIONS(
  description = "Optimized filer registry - clustered by ID, type, status"
)
AS
SELECT * FROM `ca-lobby.ca_lobby.filername_cd`;

-- Step 2: Create Search Index for text search (BETA feature)
-- Note: Search indexes are currently in preview
-- Check if available in your project: https://cloud.google.com/bigquery/docs/search-intro

CREATE SEARCH INDEX alameda_filer_name_search
ON `ca-lobby.ca_lobby.filername_cd_OPTIMIZED`(NAML, NAMF, NAMT, NAMS)
OPTIONS(
  analyzer = 'LOG_ANALYZER',  -- Good for names with common words
  -- OR
  -- analyzer = 'NO_OP_ANALYZER'  -- Exact matching only
);

-- Alternative: If Search Index not available, use MATERIALIZED VIEW with UPPER() pre-computed
CREATE MATERIALIZED VIEW `ca-lobby.ca_lobby.filername_cd_SEARCH_MV`
CLUSTER BY FILER_ID
AS
SELECT
  *,
  UPPER(NAML) as NAML_UPPER,
  UPPER(NAMF) as NAMF_UPPER,
  UPPER(NAMT) as NAMT_UPPER,
  CONCAT(UPPER(NAML), ' ', UPPER(NAMF)) as FULL_NAME_UPPER
FROM `ca-lobby.ca_lobby.filername_cd_OPTIMIZED`;

-- Test queries

-- Option A: Using Search Index (if available)
SELECT FILER_ID, NAML, NAMF, FILER_TYPE
FROM `ca-lobby.ca_lobby.filername_cd_OPTIMIZED`
WHERE SEARCH(filername_cd_OPTIMIZED, 'ALAMEDA')
ORDER BY FILER_ID;

-- Option B: Using Materialized View with pre-computed UPPER()
SELECT FILER_ID, NAML, NAMF, FILER_TYPE
FROM `ca-lobby.ca_lobby.filername_cd_SEARCH_MV`
WHERE NAML_UPPER LIKE '%ALAMEDA%'
   OR NAMF_UPPER LIKE '%ALAMEDA%'
   OR FULL_NAME_UPPER LIKE '%ALAMEDA%';

-- Option C: Optimized LIKE query (if Search Index not available)
SELECT FILER_ID, NAML, NAMF, FILER_TYPE
FROM `ca-lobby.ca_lobby.filername_cd_OPTIMIZED`
WHERE UPPER(NAML) LIKE '%ALAMEDA%'
   OR UPPER(NAMF) LIKE '%ALAMEDA%'
LIMIT 10000;  -- Add limit to reduce initial scan
```

**Rationale**:
- **FILER_ID clustering**: Primary join key across all tables
- **FILER_TYPE clustering**: Common filter for entity type analysis
- **STATUS clustering**: Filter active vs inactive filers
- **Search Index**: Optimizes text search (when available)
- **Materialized View**: Alternative when Search Index unavailable

**Expected Performance**:
- Text search (LIKE '%ALAMEDA%'): **60-80% faster** with Search Index
- Text search (LIKE '%ALAMEDA%'): **40-60% faster** with Materialized View
- Join queries: **70% faster** (clustering)
- Cost reduction: **50-70%**

**Important Notes**:
- Search Indexes are **currently in Preview** - check availability
- Materialized Views are **auto-maintained** by BigQuery
- Consider both options based on your use case

---

### Priority 1: CVR_REGISTRATION_CD

**Current State**: 670 Alameda records, moderate volume
**Primary Use**: Registration lookups, employer-firm relationships
**Optimization**: Partition by RPT_DATE, cluster by FILER_ID and ENTITY_CD

#### Implementation Script

```sql
-- ============================================================================
-- TABLE: CVR_REGISTRATION_CD
-- OPTIMIZATION: Partition by report date, cluster by filer and entity
-- IMPACT: High - Frequently joined for registration details
-- ============================================================================

CREATE OR REPLACE TABLE `ca-lobby.ca_lobby.CVR_REGISTRATION_CD_OPTIMIZED`
PARTITION BY DATE(RPT_DATE)
CLUSTER BY FILER_ID, ENTITY_CD, FORM_TYPE, DATE_QUAL
OPTIONS(
  description = "Optimized registration records - partitioned by report date",
  require_partition_filter = FALSE
)
AS
SELECT * FROM `ca-lobby.ca_lobby.CVR_REGISTRATION_CD`;

-- Test query: Find all registrations for Alameda entities
SELECT
  reg.FILING_ID,
  reg.FILER_ID,
  fn.NAML as FILER_NAME,
  reg.FIRM_NAME,
  reg.ENTITY_CD,
  reg.DATE_QUAL,
  reg.RPT_DATE
FROM `ca-lobby.ca_lobby.CVR_REGISTRATION_CD_OPTIMIZED` reg
JOIN `ca-lobby.ca_lobby.filername_cd_OPTIMIZED` fn
  ON reg.FILER_ID = fn.FILER_ID
WHERE reg.RPT_DATE >= '2020-01-01'
  AND UPPER(fn.NAML) LIKE '%ALAMEDA%'
ORDER BY reg.RPT_DATE DESC;
```

**Rationale**:
- **RPT_DATE partitioning**: Filter by registration periods
- **FILER_ID clustering**: Join key and primary filter
- **ENTITY_CD clustering**: Filter by registrant type (FRM, LEM, etc.)
- **FORM_TYPE clustering**: Form-specific queries
- **DATE_QUAL clustering**: Registration date filtering

**Expected Performance**:
- Date range queries: **85% faster**
- Join queries: **70% faster**
- Cost reduction: **75%**

---

### Priority 2: LEXP_CD

**Current State**: 198 Alameda records, moderate volume
**Primary Use**: Expenditure tracking, aggregate analysis
**Optimization**: Denormalize with RPT_DATE, cluster by FILER_ID

#### Implementation Script

```sql
-- ============================================================================
-- TABLE: LEXP_CD
-- OPTIMIZATION: Denormalize with RPT_DATE for partitioning, cluster by filer
-- IMPACT: Medium-High - Financial analysis queries
-- ============================================================================

CREATE OR REPLACE TABLE `ca-lobby.ca_lobby.LEXP_CD_OPTIMIZED`
PARTITION BY DATE(RPT_DATE)
CLUSTER BY FILER_ID, FILING_ID, FORM_TYPE
OPTIONS(
  description = "Optimized expenditure records with denormalized report date"
)
AS
SELECT
  lexp.*,
  cvr.RPT_DATE,
  cvr.FROM_DATE,
  cvr.THRU_DATE,
  cvr.ENTITY_CD as FILER_ENTITY_CD
FROM `ca-lobby.ca_lobby.LEXP_CD` lexp
LEFT JOIN `ca-lobby.ca_lobby.CVR_LOBBY_DISCLOSURE_CD` cvr
  ON lexp.FILING_ID = cvr.FILING_ID;

-- Test query: Aggregate expenditures by filer
SELECT
  FILER_ID,
  EXTRACT(YEAR FROM RPT_DATE) as year,
  SUM(CAST(AMOUNT AS FLOAT64)) as total_expenditures,
  COUNT(*) as expenditure_count
FROM `ca-lobby.ca_lobby.LEXP_CD_OPTIMIZED`
WHERE RPT_DATE BETWEEN '2023-01-01' AND '2025-12-31'
GROUP BY FILER_ID, year
ORDER BY total_expenditures DESC;
```

---

### Priority 2: LEMP_CD

**Current State**: 100 Alameda records (sample), relationship table
**Primary Use**: Employer-lobbyist relationship tracking
**Optimization**: Cluster by FILER_ID and AGCY_NAML (employer name)

#### Implementation Script

```sql
-- ============================================================================
-- TABLE: LEMP_CD
-- OPTIMIZATION: Denormalize with RPT_DATE, cluster by filer and employer
-- IMPACT: Medium - Relationship queries
-- ============================================================================

CREATE OR REPLACE TABLE `ca-lobby.ca_lobby.LEMP_CD_OPTIMIZED`
PARTITION BY DATE(RPT_DATE)
CLUSTER BY FILER_ID, FILING_ID, FORM_TYPE
OPTIONS(
  description = "Optimized employer relationships with denormalized report date"
)
AS
SELECT
  lemp.*,
  cvr.RPT_DATE,
  cvr.FROM_DATE,
  cvr.THRU_DATE
FROM `ca-lobby.ca_lobby.LEMP_CD` lemp
LEFT JOIN `ca-lobby.ca_lobby.CVR_LOBBY_DISCLOSURE_CD` cvr
  ON lemp.FILING_ID = cvr.FILING_ID;

-- Alternative: Create materialized view for employer lookups
CREATE MATERIALIZED VIEW `ca-lobby.ca_lobby.LEMP_CD_EMPLOYER_SEARCH_MV`
CLUSTER BY FILER_ID
AS
SELECT
  *,
  UPPER(AGCY_NAML) as EMPLOYER_NAME_UPPER,
  UPPER(AGCY_NAMF) as EMPLOYER_FIRST_UPPER
FROM `ca-lobby.ca_lobby.LEMP_CD_OPTIMIZED`;
```

---

### Priority 2: FILER_FILINGS_CD

**Current State**: Filing index, moderate volume, critical join table
**Primary Use**: Link filers to their filings
**Optimization**: Cluster by FILER_ID and FILING_ID

#### Implementation Script

```sql
-- ============================================================================
-- TABLE: FILER_FILINGS_CD
-- OPTIMIZATION: Cluster by filer and filing IDs (primary join keys)
-- IMPACT: Medium - Join performance
-- ============================================================================

CREATE OR REPLACE TABLE `ca-lobby.ca_lobby.FILER_FILINGS_CD_OPTIMIZED`
CLUSTER BY FILER_ID, FILING_ID, PERIOD_ID, FORM_ID
OPTIONS(
  description = "Optimized filing index - clustered by primary join keys"
)
AS
SELECT * FROM `ca-lobby.ca_lobby.FILER_FILINGS_CD`;

-- Test join query
SELECT
  ff.FILING_ID,
  ff.FILER_ID,
  fn.NAML as FILER_NAME,
  ff.PERIOD_ID,
  cvr.RPT_DATE,
  cvr.ENTITY_CD
FROM `ca-lobby.ca_lobby.FILER_FILINGS_CD_OPTIMIZED` ff
JOIN `ca-lobby.ca_lobby.filername_cd_OPTIMIZED` fn
  ON ff.FILER_ID = fn.FILER_ID
JOIN `ca-lobby.ca_lobby.CVR_LOBBY_DISCLOSURE_CD_OPTIMIZED` cvr
  ON ff.FILING_ID = cvr.FILING_ID
WHERE UPPER(fn.NAML) LIKE '%ALAMEDA%'
  AND cvr.RPT_DATE >= '2023-01-01';
```

---

### Remaining Tables (Priority 3-4)

The following tables use similar patterns. Apply as needed based on query patterns:

#### LCCM_CD (Campaign Contributions)
```sql
CREATE OR REPLACE TABLE `ca-lobby.ca_lobby.LCCM_CD_OPTIMIZED`
PARTITION BY DATE(CTRIB_DATE)  -- Has native date column!
CLUSTER BY FILER_ID, CMTE_ID, FILING_ID
OPTIONS(description = "Optimized campaign contributions - partitioned by contribution date")
AS SELECT * FROM `ca-lobby.ca_lobby.LCCM_CD`;
```

#### LOTH_CD (Other Payments)
```sql
-- Similar pattern to LPAY_CD (denormalize with RPT_DATE)
CREATE OR REPLACE TABLE `ca-lobby.ca_lobby.LOTH_CD_OPTIMIZED`
PARTITION BY DATE(RPT_DATE)
CLUSTER BY FILER_ID, FILING_ID
AS
SELECT loth.*, cvr.RPT_DATE
FROM `ca-lobby.ca_lobby.LOTH_CD` loth
LEFT JOIN `ca-lobby.ca_lobby.CVR_LOBBY_DISCLOSURE_CD` cvr
  ON loth.FILING_ID = cvr.FILING_ID;
```

#### FILER_ADDRESS_CD
```sql
-- No date partitioning needed (reference table)
CREATE OR REPLACE TABLE `ca-lobby.ca_lobby.FILER_ADDRESS_CD_OPTIMIZED`
CLUSTER BY FILER_ID, CITY, ST
OPTIONS(description = "Optimized address data - clustered by filer and location")
AS SELECT * FROM `ca-lobby.ca_lobby.FILER_ADDRESS_CD`;
```

---

## Materialized Views

Materialized views pre-compute expensive queries and automatically stay synchronized with source tables.

### 1. Alameda Filer Registry (Most Critical)

```sql
-- ============================================================================
-- MATERIALIZED VIEW: Alameda Filer List
-- PURPOSE: Pre-compute list of all Alameda-related filers
-- BENEFIT: Eliminates repeated text searches in joins
-- REFRESH: Automatic (maintained by BigQuery)
-- ============================================================================

CREATE MATERIALIZED VIEW `ca-lobby.ca_lobby.MV_ALAMEDA_FILERS`
CLUSTER BY FILER_ID
OPTIONS(
  description = "Pre-computed list of all Alameda-related filers - auto-refreshed",
  enable_refresh = TRUE,
  refresh_interval_minutes = 60  -- Refresh hourly
)
AS
SELECT DISTINCT
  FILER_ID,
  NAML as LAST_NAME,
  NAMF as FIRST_NAME,
  NAMT as TITLE,
  FILER_TYPE,
  STATUS,
  EFFECT_DT,
  -- Pre-compute search flags
  CASE
    WHEN UPPER(NAML) LIKE '%ALAMEDA%' THEN 'LAST_NAME'
    WHEN UPPER(NAMF) LIKE '%ALAMEDA%' THEN 'FIRST_NAME'
    WHEN UPPER(NAMT) LIKE '%ALAMEDA%' THEN 'TITLE'
  END as ALAMEDA_MATCH_TYPE
FROM `ca-lobby.ca_lobby.filername_cd_OPTIMIZED`
WHERE UPPER(NAML) LIKE '%ALAMEDA%'
   OR UPPER(NAMF) LIKE '%ALAMEDA%'
   OR UPPER(NAMT) LIKE '%ALAMEDA%';

-- Usage example: Replace complex text search with simple join
SELECT
  cvr.FILING_ID,
  alameda.LAST_NAME,
  alameda.FIRST_NAME,
  cvr.ENTITY_CD,
  cvr.RPT_DATE,
  SUM(CAST(lp.AMOUNT AS FLOAT64)) as total_payments
FROM `ca-lobby.ca_lobby.MV_ALAMEDA_FILERS` alameda
JOIN `ca-lobby.ca_lobby.CVR_LOBBY_DISCLOSURE_CD_OPTIMIZED` cvr
  ON alameda.FILER_ID = cvr.FILER_ID
LEFT JOIN `ca-lobby.ca_lobby.LPAY_CD_OPTIMIZED_WITH_DATE` lp
  ON cvr.FILING_ID = lp.FILING_ID
WHERE cvr.RPT_DATE BETWEEN '2023-01-01' AND '2025-12-31'
GROUP BY cvr.FILING_ID, alameda.LAST_NAME, alameda.FIRST_NAME, cvr.ENTITY_CD, cvr.RPT_DATE;
```

**Impact**: **90% faster** - Eliminates text search overhead from every query

---

### 2. Payment Totals by Filer and Year

```sql
-- ============================================================================
-- MATERIALIZED VIEW: Annual Payment Totals
-- PURPOSE: Pre-aggregate payments by filer and year
-- BENEFIT: Instant access to summary statistics
-- ============================================================================

CREATE MATERIALIZED VIEW `ca-lobby.ca_lobby.MV_PAYMENT_TOTALS_BY_YEAR`
PARTITION BY filing_year
CLUSTER BY FILER_ID
OPTIONS(
  description = "Pre-aggregated annual payment totals by filer",
  enable_refresh = TRUE,
  refresh_interval_minutes = 360  -- Refresh every 6 hours
)
AS
SELECT
  lp.FILER_ID,
  fn.NAML as FILER_NAME,
  fn.FILER_TYPE,
  EXTRACT(YEAR FROM lp.RPT_DATE) as filing_year,
  COUNT(DISTINCT lp.FILING_ID) as total_filings,
  COUNT(*) as payment_count,
  SUM(CAST(lp.AMOUNT AS FLOAT64)) as total_payments,
  AVG(CAST(lp.AMOUNT AS FLOAT64)) as avg_payment,
  MAX(CAST(lp.AMOUNT AS FLOAT64)) as max_payment,
  MIN(CAST(lp.AMOUNT AS FLOAT64)) as min_payment
FROM `ca-lobby.ca_lobby.LPAY_CD_OPTIMIZED_WITH_DATE` lp
JOIN `ca-lobby.ca_lobby.filername_cd_OPTIMIZED` fn
  ON lp.FILER_ID = fn.FILER_ID
WHERE lp.RPT_DATE IS NOT NULL
GROUP BY lp.FILER_ID, fn.NAML, fn.FILER_TYPE, filing_year;

-- Usage: Get payment totals for Alameda entities
SELECT
  pt.FILER_NAME,
  pt.filing_year,
  pt.total_filings,
  pt.payment_count,
  ROUND(pt.total_payments, 2) as total_payments,
  ROUND(pt.avg_payment, 2) as avg_payment
FROM `ca-lobby.ca_lobby.MV_PAYMENT_TOTALS_BY_YEAR` pt
JOIN `ca-lobby.ca_lobby.MV_ALAMEDA_FILERS` alameda
  ON pt.FILER_ID = alameda.FILER_ID
WHERE pt.filing_year BETWEEN 2020 AND 2024
ORDER BY pt.filing_year DESC, pt.total_payments DESC;
```

**Impact**: **95% faster** - Aggregations are pre-computed

---

### 3. Comprehensive Activity Summary

```sql
-- ============================================================================
-- MATERIALIZED VIEW: Comprehensive Lobbying Activity Summary
-- PURPOSE: Complete activity rollup for dashboard queries
-- BENEFIT: Single-query access to all key metrics
-- ============================================================================

CREATE MATERIALIZED VIEW `ca-lobby.ca_lobby.MV_LOBBYING_ACTIVITY_SUMMARY`
PARTITION BY activity_year
CLUSTER BY FILER_ID, ENTITY_CD
OPTIONS(
  description = "Comprehensive lobbying activity summary by filer and year",
  enable_refresh = TRUE,
  refresh_interval_minutes = 720  -- Refresh every 12 hours
)
AS
WITH payment_summary AS (
  SELECT
    FILER_ID,
    EXTRACT(YEAR FROM RPT_DATE) as activity_year,
    COUNT(*) as payment_count,
    SUM(CAST(AMOUNT AS FLOAT64)) as total_payments
  FROM `ca-lobby.ca_lobby.LPAY_CD_OPTIMIZED_WITH_DATE`
  WHERE RPT_DATE IS NOT NULL
  GROUP BY FILER_ID, activity_year
),
expenditure_summary AS (
  SELECT
    FILER_ID,
    EXTRACT(YEAR FROM RPT_DATE) as activity_year,
    COUNT(*) as expenditure_count,
    SUM(CAST(AMOUNT AS FLOAT64)) as total_expenditures
  FROM `ca-lobby.ca_lobby.LEXP_CD_OPTIMIZED`
  WHERE RPT_DATE IS NOT NULL
  GROUP BY FILER_ID, activity_year
),
disclosure_summary AS (
  SELECT
    FILER_ID,
    EXTRACT(YEAR FROM RPT_DATE) as activity_year,
    ENTITY_CD,
    COUNT(DISTINCT FILING_ID) as filing_count,
    MIN(FROM_DATE) as first_period_start,
    MAX(THRU_DATE) as last_period_end
  FROM `ca-lobby.ca_lobby.CVR_LOBBY_DISCLOSURE_CD_OPTIMIZED`
  WHERE RPT_DATE IS NOT NULL
  GROUP BY FILER_ID, activity_year, ENTITY_CD
)
SELECT
  ds.FILER_ID,
  fn.NAML as FILER_NAME,
  ds.activity_year,
  ds.ENTITY_CD,
  ds.filing_count,
  COALESCE(ps.payment_count, 0) as payment_count,
  COALESCE(ps.total_payments, 0) as total_payments,
  COALESCE(es.expenditure_count, 0) as expenditure_count,
  COALESCE(es.total_expenditures, 0) as total_expenditures,
  ds.first_period_start,
  ds.last_period_end
FROM disclosure_summary ds
JOIN `ca-lobby.ca_lobby.filername_cd_OPTIMIZED` fn
  ON ds.FILER_ID = fn.FILER_ID
LEFT JOIN payment_summary ps
  ON ds.FILER_ID = ps.FILER_ID
  AND ds.activity_year = ps.activity_year
LEFT JOIN expenditure_summary es
  ON ds.FILER_ID = es.FILER_ID
  AND ds.activity_year = es.activity_year;

-- Usage: Complete Alameda activity report
SELECT
  summary.FILER_NAME,
  summary.activity_year,
  summary.ENTITY_CD,
  summary.filing_count,
  summary.payment_count,
  ROUND(summary.total_payments, 2) as total_payments,
  summary.expenditure_count,
  ROUND(summary.total_expenditures, 2) as total_expenditures
FROM `ca-lobby.ca_lobby.MV_LOBBYING_ACTIVITY_SUMMARY` summary
JOIN `ca-lobby.ca_lobby.MV_ALAMEDA_FILERS` alameda
  ON summary.FILER_ID = alameda.FILER_ID
WHERE summary.activity_year >= 2020
ORDER BY summary.activity_year DESC, summary.total_payments DESC;
```

**Impact**: **98% faster** - Complex multi-table joins pre-computed

---

### 4. Employer-Firm Relationships

```sql
-- ============================================================================
-- MATERIALIZED VIEW: Employer-Firm Relationship Mapping
-- PURPOSE: Pre-compute who hired whom for lobbying
-- BENEFIT: Instant relationship lookups
-- ============================================================================

CREATE MATERIALIZED VIEW `ca-lobby.ca_lobby.MV_EMPLOYER_FIRM_RELATIONSHIPS`
CLUSTER BY EMPLOYER_FILER_ID, FIRM_FILER_ID
OPTIONS(
  description = "Employer to lobbying firm relationship mapping",
  enable_refresh = TRUE,
  refresh_interval_minutes = 1440  -- Refresh daily
)
AS
SELECT DISTINCT
  reg.FILER_ID as EMPLOYER_FILER_ID,
  fn_emp.NAML as EMPLOYER_NAME,
  reg.ENTITY_CD as EMPLOYER_TYPE,
  reg.FIRM_ID as FIRM_FILER_ID,
  reg.FIRM_NAME,
  MIN(reg.DATE_QUAL) as relationship_start_date,
  MAX(reg.RPT_DATE) as last_filing_date,
  COUNT(DISTINCT reg.FILING_ID) as filing_count
FROM `ca-lobby.ca_lobby.CVR_REGISTRATION_CD_OPTIMIZED` reg
JOIN `ca-lobby.ca_lobby.filername_cd_OPTIMIZED` fn_emp
  ON reg.FILER_ID = fn_emp.FILER_ID
WHERE reg.ENTITY_CD IN ('LEM', 'LCO')  -- Employers and coalitions
  AND reg.FIRM_ID IS NOT NULL
GROUP BY
  reg.FILER_ID,
  fn_emp.NAML,
  reg.ENTITY_CD,
  reg.FIRM_ID,
  reg.FIRM_NAME;

-- Usage: Find which firms Alameda County hired
SELECT
  rel.EMPLOYER_NAME,
  rel.FIRM_NAME,
  rel.relationship_start_date,
  rel.last_filing_date,
  rel.filing_count,
  ROUND(SUM(CAST(lp.AMOUNT AS FLOAT64)), 2) as total_paid
FROM `ca-lobby.ca_lobby.MV_EMPLOYER_FIRM_RELATIONSHIPS` rel
JOIN `ca-lobby.ca_lobby.MV_ALAMEDA_FILERS` alameda
  ON rel.EMPLOYER_FILER_ID = alameda.FILER_ID
LEFT JOIN `ca-lobby.ca_lobby.LPAY_CD_OPTIMIZED_WITH_DATE` lp
  ON rel.EMPLOYER_FILER_ID = lp.FILER_ID
GROUP BY
  rel.EMPLOYER_NAME,
  rel.FIRM_NAME,
  rel.relationship_start_date,
  rel.last_filing_date,
  rel.filing_count
ORDER BY total_paid DESC;
```

**Impact**: **80% faster** - Relationship queries pre-computed

---

## Search Indexes

BigQuery Search Indexes enable fast full-text search (currently in Preview).

### When to Use Search Indexes

✅ **Use when**:
- Frequent text searches with LIKE '%term%'
- Multi-word searches
- Fuzzy matching needed

❌ **Don't use when**:
- Exact match queries (use clustering)
- Prefix searches like 'ALAMEDA%' (already fast)
- Low query frequency

### Implementation

```sql
-- ============================================================================
-- SEARCH INDEX: Filer Name Search
-- PURPOSE: Optimize text search on filer names
-- STATUS: Preview feature - check availability
-- ============================================================================

-- Check if Search Indexes are available
-- https://cloud.google.com/bigquery/docs/search-intro

CREATE SEARCH INDEX idx_filer_name_search
ON `ca-lobby.ca_lobby.filername_cd_OPTIMIZED`(NAML, NAMF, NAMT)
OPTIONS(
  analyzer = 'LOG_ANALYZER'  -- Best for names with spaces/punctuation
);

-- Usage with SEARCH() function
SELECT FILER_ID, NAML, NAMF, FILER_TYPE
FROM `ca-lobby.ca_lobby.filername_cd_OPTIMIZED`
WHERE SEARCH(filername_cd_OPTIMIZED, 'ALAMEDA')
ORDER BY FILER_ID
LIMIT 1000;

-- Multi-term search
SELECT FILER_ID, NAML, NAMF
FROM `ca-lobby.ca_lobby.filername_cd_OPTIMIZED`
WHERE SEARCH(filername_cd_OPTIMIZED, 'ALAMEDA COUNTY')
ORDER BY FILER_ID;

-- ============================================================================
-- SEARCH INDEX: Firm Name Search
-- PURPOSE: Optimize text search on firm names in disclosures
-- ============================================================================

CREATE SEARCH INDEX idx_firm_name_search
ON `ca-lobby.ca_lobby.CVR_LOBBY_DISCLOSURE_CD_OPTIMIZED`(FIRM_NAME, FILER_NAML, FILER_NAMF)
OPTIONS(
  analyzer = 'LOG_ANALYZER'
);

-- Usage
SELECT FILING_ID, FILER_ID, FIRM_NAME, RPT_DATE
FROM `ca-lobby.ca_lobby.CVR_LOBBY_DISCLOSURE_CD_OPTIMIZED`
WHERE SEARCH(CVR_LOBBY_DISCLOSURE_CD_OPTIMIZED, 'ALAMEDA')
  AND RPT_DATE >= '2023-01-01'
ORDER BY RPT_DATE DESC;

-- ============================================================================
-- SEARCH INDEX: Employer Name Search
-- PURPOSE: Optimize text search on employer names
-- ============================================================================

CREATE SEARCH INDEX idx_employer_name_search
ON `ca-lobby.ca_lobby.LEMP_CD_OPTIMIZED`(AGCY_NAML, AGCY_NAMF)
OPTIONS(
  analyzer = 'LOG_ANALYZER'
);
```

### Search Index Analyzer Options

| Analyzer | Best For | Example |
|----------|----------|---------|
| `LOG_ANALYZER` | Names with spaces, punctuation | "ALAMEDA COUNTY", "Smith & Jones" |
| `NO_OP_ANALYZER` | Exact matching, case-sensitive | "ALAMEDA" (exact) |
| `PATTERN_ANALYZER` | Custom regex patterns | Complex tokenization |

### Fallback: If Search Indexes Not Available

Use Materialized Views with pre-computed UPPER() columns (shown earlier):

```sql
-- Already created in filername_cd_SEARCH_MV
SELECT * FROM `ca-lobby.ca_lobby.filername_cd_SEARCH_MV`
WHERE NAML_UPPER LIKE '%ALAMEDA%'
   OR NAMF_UPPER LIKE '%ALAMEDA%'
   OR FULL_NAME_UPPER LIKE '%ALAMEDA%';
```

---

## Query Optimization Guide

### Pattern 1: Text Search → Optimized

❌ **BEFORE** (Slow - Full Table Scan)
```sql
SELECT *
FROM `ca-lobby.ca_lobby.CVR_LOBBY_DISCLOSURE_CD`
WHERE UPPER(FIRM_NAME) LIKE '%ALAMEDA%';
```
- Scans entire table
- Applies UPPER() to every row
- No partition pruning
- **Cost**: High (full scan)

✅ **AFTER** (Fast - Using Materialized View)
```sql
SELECT cvr.*
FROM `ca-lobby.ca_lobby.MV_ALAMEDA_FILERS` alameda
JOIN `ca-lobby.ca_lobby.CVR_LOBBY_DISCLOSURE_CD_OPTIMIZED` cvr
  ON alameda.FILER_ID = cvr.FILER_ID;
```
- Scans small pre-filtered list
- No text search overhead
- Leverages clustering
- **Cost**: Low (small table + join)
- **Improvement**: **90% faster, 85% cost reduction**

---

### Pattern 2: Date Range → Optimized

❌ **BEFORE** (Slow - No Partitioning)
```sql
SELECT FILER_ID, SUM(CAST(AMOUNT AS FLOAT64)) as total
FROM `ca-lobby.ca_lobby.LPAY_CD`
WHERE FILING_ID IN (
  SELECT FILING_ID
  FROM `ca-lobby.ca_lobby.CVR_LOBBY_DISCLOSURE_CD`
  WHERE RPT_DATE BETWEEN '2023-01-01' AND '2025-12-31'
)
GROUP BY FILER_ID;
```
- Scans entire LPAY_CD table
- Expensive subquery
- No partition pruning
- **Cost**: Very High

✅ **AFTER** (Fast - Partitioned Table)
```sql
SELECT FILER_ID, SUM(CAST(AMOUNT AS FLOAT64)) as total
FROM `ca-lobby.ca_lobby.LPAY_CD_OPTIMIZED_WITH_DATE`
WHERE RPT_DATE BETWEEN '2023-01-01' AND '2025-12-31'
GROUP BY FILER_ID;
```
- **Partition pruning**: Only scans 2023-2024 partitions
- Direct filter (no subquery)
- Clustering accelerates aggregation
- **Cost**: Low (only relevant partitions)
- **Improvement**: **95% faster, 90% cost reduction**

---

### Pattern 3: Complex Join → Optimized

❌ **BEFORE** (Slow - Multiple Full Scans)
```sql
SELECT
  f.FILER_NAML,
  cvr.FILING_ID,
  cvr.RPT_DATE,
  SUM(CAST(lp.AMOUNT AS FLOAT64)) as total_payments
FROM `ca-lobby.ca_lobby.FILERS_CD` f
JOIN `ca-lobby.ca_lobby.CVR_LOBBY_DISCLOSURE_CD` cvr
  ON f.FILER_ID = cvr.FILER_ID
LEFT JOIN `ca-lobby.ca_lobby.LPAY_CD` lp
  ON cvr.FILING_ID = lp.FILING_ID
WHERE UPPER(f.FILER_NAML) LIKE '%ALAMEDA%'
  AND cvr.RPT_DATE >= '2023-01-01'
GROUP BY f.FILER_NAML, cvr.FILING_ID, cvr.RPT_DATE;
```
- Text search on every query
- No partition pruning
- Un-optimized joins
- **Cost**: Very High
- **Time**: 60-180 seconds

✅ **AFTER** (Fast - Optimized Tables + MV)
```sql
SELECT
  alameda.LAST_NAME,
  cvr.FILING_ID,
  cvr.RPT_DATE,
  SUM(CAST(lp.AMOUNT AS FLOAT64)) as total_payments
FROM `ca-lobby.ca_lobby.MV_ALAMEDA_FILERS` alameda
JOIN `ca-lobby.ca_lobby.CVR_LOBBY_DISCLOSURE_CD_OPTIMIZED` cvr
  ON alameda.FILER_ID = cvr.FILER_ID
LEFT JOIN `ca-lobby.ca_lobby.LPAY_CD_OPTIMIZED_WITH_DATE` lp
  ON cvr.FILING_ID = lp.FILING_ID
WHERE cvr.RPT_DATE >= '2023-01-01'
GROUP BY alameda.LAST_NAME, cvr.FILING_ID, cvr.RPT_DATE;
```
- Pre-filtered Alameda list (MV)
- Partition pruning on both tables
- Clustering optimizes joins
- **Cost**: Low
- **Time**: 2-5 seconds
- **Improvement**: **95% faster, 85% cost reduction**

---

### Pattern 4: Aggregate Report → Optimized

❌ **BEFORE** (Slow - Real-time Aggregation)
```sql
WITH alameda_filers AS (
  SELECT FILER_ID
  FROM `ca-lobby.ca_lobby.FILERS_CD`
  WHERE UPPER(FILER_NAML) LIKE '%ALAMEDA%'
),
payments AS (
  SELECT FILER_ID, SUM(CAST(AMOUNT AS FLOAT64)) as total
  FROM `ca-lobby.ca_lobby.LPAY_CD`
  WHERE FILER_ID IN (SELECT FILER_ID FROM alameda_filers)
  GROUP BY FILER_ID
),
expenditures AS (
  SELECT FILER_ID, SUM(CAST(AMOUNT AS FLOAT64)) as total
  FROM `ca-lobby.ca_lobby.LEXP_CD`
  WHERE FILER_ID IN (SELECT FILER_ID FROM alameda_filers)
  GROUP BY FILER_ID
)
SELECT
  f.FILER_NAML,
  COALESCE(p.total, 0) as payments,
  COALESCE(e.total, 0) as expenditures
FROM alameda_filers af
JOIN `ca-lobby.ca_lobby.FILERS_CD` f ON af.FILER_ID = f.FILER_ID
LEFT JOIN payments p ON af.FILER_ID = p.FILER_ID
LEFT JOIN expenditures e ON af.FILER_ID = e.FILER_ID;
```
- Multiple CTEs with aggregations
- Text search every time
- Scans multiple large tables
- **Cost**: Very High
- **Time**: 90-180 seconds

✅ **AFTER** (Fast - Pre-computed MV)
```sql
SELECT
  summary.FILER_NAME,
  summary.activity_year,
  summary.payment_count,
  ROUND(summary.total_payments, 2) as payments,
  summary.expenditure_count,
  ROUND(summary.total_expenditures, 2) as expenditures
FROM `ca-lobby.ca_lobby.MV_LOBBYING_ACTIVITY_SUMMARY` summary
JOIN `ca-lobby.ca_lobby.MV_ALAMEDA_FILERS` alameda
  ON summary.FILER_ID = alameda.FILER_ID
WHERE summary.activity_year >= 2020
ORDER BY summary.activity_year DESC, summary.total_payments DESC;
```
- All aggregations pre-computed
- Simple join to pre-filtered list
- Minimal data scanning
- **Cost**: Very Low
- **Time**: < 1 second
- **Improvement**: **99% faster, 95% cost reduction**

---

### Pattern 5: Pagination → Optimized

❌ **BEFORE** (Slow - OFFSET/LIMIT)
```sql
SELECT *
FROM `ca-lobby.ca_lobby.CVR_LOBBY_DISCLOSURE_CD`
WHERE UPPER(FIRM_NAME) LIKE '%ALAMEDA%'
ORDER BY RPT_DATE DESC
LIMIT 100 OFFSET 1000;  -- Page 11
```
- Scans all rows up to offset
- Expensive for large offsets
- Repeated full scans
- **Cost**: High (increases with page number)

✅ **AFTER** (Fast - Keyset Pagination)
```sql
-- Page 1
SELECT *
FROM `ca-lobby.ca_lobby.CVR_LOBBY_DISCLOSURE_CD_OPTIMIZED` cvr
JOIN `ca-lobby.ca_lobby.MV_ALAMEDA_FILERS` alameda
  ON cvr.FILER_ID = alameda.FILER_ID
ORDER BY cvr.RPT_DATE DESC, cvr.FILING_ID DESC
LIMIT 100;

-- Page 2 (using last row from previous page)
SELECT *
FROM `ca-lobby.ca_lobby.CVR_LOBBY_DISCLOSURE_CD_OPTIMIZED` cvr
JOIN `ca-lobby.ca_lobby.MV_ALAMEDA_FILERS` alameda
  ON cvr.FILER_ID = alameda.FILER_ID
WHERE cvr.RPT_DATE < '2024-03-15'  -- Last RPT_DATE from page 1
   OR (cvr.RPT_DATE = '2024-03-15' AND cvr.FILING_ID < 123456)
ORDER BY cvr.RPT_DATE DESC, cvr.FILING_ID DESC
LIMIT 100;
```
- No OFFSET overhead
- Consistent performance across pages
- Uses clustering for efficient seeks
- **Cost**: Low (consistent)
- **Improvement**: **Consistent speed for all pages**

---

### General Query Best Practices

1. **Always filter by partition column first**
   ```sql
   WHERE RPT_DATE BETWEEN '2023-01-01' AND '2025-12-31'  -- Partition filter
     AND FILER_ID = 1234567  -- Then other filters
   ```

2. **Use materialized views for repeated queries**
   ```sql
   -- Instead of repeating this pattern:
   JOIN (SELECT FILER_ID FROM FILERS_CD WHERE UPPER(NAML) LIKE '%ALAMEDA%')

   -- Use:
   JOIN `ca-lobby.ca_lobby.MV_ALAMEDA_FILERS`
   ```

3. **Avoid SELECT \*** - Specify only needed columns
   ```sql
   -- Bad (reads all columns)
   SELECT * FROM table;

   -- Good (reads only needed columns = lower cost)
   SELECT FILER_ID, NAML, RPT_DATE FROM table;
   ```

4. **Use APPROX functions for large aggregations**
   ```sql
   -- Exact (slower, more expensive)
   SELECT COUNT(DISTINCT FILER_ID) FROM table;

   -- Approximate (faster, cheaper, 99%+ accurate)
   SELECT APPROX_COUNT_DISTINCT(FILER_ID) FROM table;
   ```

5. **Leverage clustering order in WHERE clauses**
   ```sql
   -- Table clustered by: FILER_ID, ENTITY_CD, FILING_ID

   -- Good (follows clustering order)
   WHERE FILER_ID = 123 AND ENTITY_CD = 'FRM' AND FILING_ID > 1000

   -- Less optimal (skips clustering order)
   WHERE ENTITY_CD = 'FRM' AND FILING_ID > 1000
   ```

---

## Testing and Validation

### Phase 1: Baseline Measurement (Before Optimization)

```sql
-- ============================================================================
-- BASELINE TESTING SCRIPT
-- RUN THIS BEFORE implementing optimizations
-- Save results for comparison
-- ============================================================================

-- Test 1: Simple text search
SET @@query_label = 'BASELINE_TEST_1_TEXT_SEARCH';
SELECT COUNT(*) as record_count
FROM `ca-lobby.ca_lobby.CVR_LOBBY_DISCLOSURE_CD`
WHERE UPPER(FIRM_NAME) LIKE '%ALAMEDA%';
-- Record: Execution time, bytes processed, slot time

-- Test 2: Date range filter
SET @@query_label = 'BASELINE_TEST_2_DATE_RANGE';
SELECT
  EXTRACT(YEAR FROM RPT_DATE) as year,
  COUNT(*) as filings,
  COUNT(DISTINCT FILER_ID) as unique_filers
FROM `ca-lobby.ca_lobby.CVR_LOBBY_DISCLOSURE_CD`
WHERE RPT_DATE BETWEEN '2020-01-01' AND '2025-12-31'
GROUP BY year;
-- Record: Execution time, bytes processed

-- Test 3: Complex join
SET @@query_label = 'BASELINE_TEST_3_COMPLEX_JOIN';
SELECT
  f.FILER_NAML,
  COUNT(DISTINCT cvr.FILING_ID) as filing_count,
  SUM(CAST(lp.AMOUNT AS FLOAT64)) as total_payments
FROM `ca-lobby.ca_lobby.FILERS_CD` f
JOIN `ca-lobby.ca_lobby.CVR_LOBBY_DISCLOSURE_CD` cvr
  ON f.FILER_ID = cvr.FILER_ID
LEFT JOIN `ca-lobby.ca_lobby.LPAY_CD` lp
  ON cvr.FILING_ID = lp.FILING_ID
WHERE UPPER(f.FILER_NAML) LIKE '%ALAMEDA%'
  AND cvr.RPT_DATE >= '2023-01-01'
GROUP BY f.FILER_NAML;
-- Record: Execution time, bytes processed, slot time

-- Test 4: Aggregate query
SET @@query_label = 'BASELINE_TEST_4_AGGREGATION';
SELECT
  FILER_ID,
  COUNT(*) as payment_count,
  SUM(CAST(AMOUNT AS FLOAT64)) as total_amount,
  AVG(CAST(AMOUNT AS FLOAT64)) as avg_amount
FROM `ca-lobby.ca_lobby.LPAY_CD`
WHERE FILER_ID IN (
  SELECT FILER_ID
  FROM `ca-lobby.ca_lobby.FILERS_CD`
  WHERE UPPER(FILER_NAML) LIKE '%ALAMEDA%'
)
GROUP BY FILER_ID;
-- Record: Execution time, bytes processed

-- Test 5: Relationship query
SET @@query_label = 'BASELINE_TEST_5_RELATIONSHIPS';
SELECT
  fn.FILER_NAML as employer,
  reg.FIRM_NAME as firm,
  COUNT(DISTINCT lp.FILING_ID) as payment_filings,
  SUM(CAST(lp.AMOUNT AS FLOAT64)) as total_paid
FROM `ca-lobby.ca_lobby.CVR_REGISTRATION_CD` reg
JOIN `ca-lobby.ca_lobby.FILERS_CD` fn
  ON reg.FILER_ID = fn.FILER_ID
LEFT JOIN `ca-lobby.ca_lobby.LPAY_CD` lp
  ON reg.FILER_ID = lp.FILER_ID
WHERE UPPER(fn.FILER_NAML) LIKE '%ALAMEDA%'
  AND reg.ENTITY_CD = 'LEM'
GROUP BY fn.FILER_NAML, reg.FIRM_NAME;
-- Record: Execution time, bytes processed
```

### Extract Baseline Metrics

```sql
-- View query history with statistics
SELECT
  creation_time,
  user_email,
  job_id,
  query,
  ROUND(total_bytes_processed / POW(10, 9), 2) as gb_processed,
  ROUND(total_slot_ms / 1000, 2) as slot_seconds,
  ROUND(total_bytes_billed / POW(10, 9), 2) as gb_billed,
  ROUND((total_bytes_billed / POW(10, 12)) * 5, 4) as estimated_cost_usd,
  ROUND(TIMESTAMP_DIFF(end_time, start_time, MILLISECOND) / 1000, 2) as duration_seconds
FROM `ca-lobby.region-us`.INFORMATION_SCHEMA.JOBS_BY_PROJECT
WHERE statement_type = 'SELECT'
  AND labels.key = 'query_label'
  AND labels.value LIKE 'BASELINE_TEST_%'
  AND creation_time >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 1 HOUR)
ORDER BY creation_time DESC;
```

---

### Phase 2: Post-Optimization Testing

Run the same queries against optimized tables:

```sql
-- ============================================================================
-- OPTIMIZED TESTING SCRIPT
-- RUN THIS AFTER implementing optimizations
-- Compare to baseline results
-- ============================================================================

-- Test 1: Text search (using materialized view)
SET @@query_label = 'OPTIMIZED_TEST_1_TEXT_SEARCH';
SELECT COUNT(*) as record_count
FROM `ca-lobby.ca_lobby.CVR_LOBBY_DISCLOSURE_CD_OPTIMIZED` cvr
JOIN `ca-lobby.ca_lobby.MV_ALAMEDA_FILERS` alameda
  ON cvr.FILER_ID = alameda.FILER_ID;

-- Test 2: Date range filter (using partitioning)
SET @@query_label = 'OPTIMIZED_TEST_2_DATE_RANGE';
SELECT
  EXTRACT(YEAR FROM RPT_DATE) as year,
  COUNT(*) as filings,
  APPROX_COUNT_DISTINCT(FILER_ID) as unique_filers
FROM `ca-lobby.ca_lobby.CVR_LOBBY_DISCLOSURE_CD_OPTIMIZED`
WHERE RPT_DATE BETWEEN '2020-01-01' AND '2025-12-31'
GROUP BY year;

-- Test 3: Complex join (using optimized tables)
SET @@query_label = 'OPTIMIZED_TEST_3_COMPLEX_JOIN';
SELECT
  alameda.LAST_NAME as FILER_NAME,
  COUNT(DISTINCT cvr.FILING_ID) as filing_count,
  SUM(CAST(lp.AMOUNT AS FLOAT64)) as total_payments
FROM `ca-lobby.ca_lobby.MV_ALAMEDA_FILERS` alameda
JOIN `ca-lobby.ca_lobby.CVR_LOBBY_DISCLOSURE_CD_OPTIMIZED` cvr
  ON alameda.FILER_ID = cvr.FILER_ID
LEFT JOIN `ca-lobby.ca_lobby.LPAY_CD_OPTIMIZED_WITH_DATE` lp
  ON cvr.FILING_ID = lp.FILING_ID
WHERE cvr.RPT_DATE >= '2023-01-01'
GROUP BY alameda.LAST_NAME;

-- Test 4: Aggregate query (using materialized view)
SET @@query_label = 'OPTIMIZED_TEST_4_AGGREGATION';
SELECT
  FILER_ID,
  payment_count,
  total_payments,
  ROUND(total_payments / payment_count, 2) as avg_amount
FROM `ca-lobby.ca_lobby.MV_PAYMENT_TOTALS_BY_YEAR`
JOIN `ca-lobby.ca_lobby.MV_ALAMEDA_FILERS` alameda
  USING(FILER_ID)
WHERE filing_year >= 2020;

-- Test 5: Relationship query (using materialized view)
SET @@query_label = 'OPTIMIZED_TEST_5_RELATIONSHIPS';
SELECT
  EMPLOYER_NAME,
  FIRM_NAME,
  filing_count,
  total_paid
FROM `ca-lobby.ca_lobby.MV_EMPLOYER_FIRM_RELATIONSHIPS` rel
JOIN `ca-lobby.ca_lobby.MV_ALAMEDA_FILERS` alameda
  ON rel.EMPLOYER_FILER_ID = alameda.FILER_ID
ORDER BY total_paid DESC;
```

---

### Phase 3: Performance Comparison

```sql
-- ============================================================================
-- PERFORMANCE COMPARISON REPORT
-- Compares baseline vs optimized query performance
-- ============================================================================

WITH baseline AS (
  SELECT
    labels.value as test_name,
    ROUND(AVG(total_bytes_processed / POW(10, 9)), 2) as avg_gb_processed,
    ROUND(AVG(total_slot_ms / 1000), 2) as avg_slot_seconds,
    ROUND(AVG(TIMESTAMP_DIFF(end_time, start_time, MILLISECOND) / 1000), 2) as avg_duration_sec,
    ROUND(AVG((total_bytes_billed / POW(10, 12)) * 5), 4) as avg_cost_usd
  FROM `ca-lobby.region-us`.INFORMATION_SCHEMA.JOBS_BY_PROJECT
  WHERE labels.key = 'query_label'
    AND labels.value LIKE 'BASELINE_TEST_%'
  GROUP BY labels.value
),
optimized AS (
  SELECT
    labels.value as test_name,
    ROUND(AVG(total_bytes_processed / POW(10, 9)), 2) as avg_gb_processed,
    ROUND(AVG(total_slot_ms / 1000), 2) as avg_slot_seconds,
    ROUND(AVG(TIMESTAMP_DIFF(end_time, start_time, MILLISECOND) / 1000), 2) as avg_duration_sec,
    ROUND(AVG((total_bytes_billed / POW(10, 12)) * 5), 4) as avg_cost_usd
  FROM `ca-lobby.region-us`.INFORMATION_SCHEMA.JOBS_BY_PROJECT
  WHERE labels.key = 'query_label'
    AND labels.value LIKE 'OPTIMIZED_TEST_%'
  GROUP BY labels.value
)
SELECT
  REPLACE(b.test_name, 'BASELINE_TEST_', '') as test,
  b.avg_duration_sec as baseline_duration_sec,
  o.avg_duration_sec as optimized_duration_sec,
  ROUND(((b.avg_duration_sec - o.avg_duration_sec) / b.avg_duration_sec) * 100, 1) as speed_improvement_pct,
  b.avg_gb_processed as baseline_gb,
  o.avg_gb_processed as optimized_gb,
  ROUND(((b.avg_gb_processed - o.avg_gb_processed) / b.avg_gb_processed) * 100, 1) as data_reduction_pct,
  b.avg_cost_usd as baseline_cost,
  o.avg_cost_usd as optimized_cost,
  ROUND(((b.avg_cost_usd - o.avg_cost_usd) / b.avg_cost_usd) * 100, 1) as cost_savings_pct
FROM baseline b
JOIN optimized o
  ON REPLACE(b.test_name, 'BASELINE_', '') = REPLACE(o.test_name, 'OPTIMIZED_', '')
ORDER BY test;
```

Expected output format:
```
test                | baseline_duration_sec | optimized_duration_sec | speed_improvement_pct | baseline_gb | optimized_gb | data_reduction_pct | baseline_cost | optimized_cost | cost_savings_pct
--------------------|-----------------------|------------------------|----------------------|-------------|--------------|-------------------|---------------|----------------|------------------
1_TEXT_SEARCH       | 45.3                  | 2.1                    | 95.4%                | 12.5        | 0.8          | 93.6%             | 0.0625        | 0.0040         | 93.6%
2_DATE_RANGE        | 32.1                  | 1.5                    | 95.3%                | 8.3         | 0.4          | 95.2%             | 0.0415        | 0.0020         | 95.2%
3_COMPLEX_JOIN      | 78.9                  | 5.2                    | 93.4%                | 25.7        | 2.1          | 91.8%             | 0.1285        | 0.0105         | 91.8%
4_AGGREGATION       | 28.5                  | 0.8                    | 97.2%                | 7.2         | 0.1          | 98.6%             | 0.0360        | 0.0005         | 98.6%
5_RELATIONSHIPS     | 52.3                  | 1.2                    | 97.7%                | 15.8        | 0.3          | 98.1%             | 0.0790        | 0.0015         | 98.1%
```

---

### Phase 4: Clustering Effectiveness Check

```sql
-- ============================================================================
-- CLUSTERING QUALITY CHECK
-- Measures how well data is clustered
-- ============================================================================

-- Check clustering ratio (lower = better clustered)
-- Target: < 10 (well clustered), 10-50 (acceptable), > 50 (needs re-clustering)

SELECT
  table_name,
  ROUND(SUM(total_logical_bytes) / POW(10, 9), 2) as total_gb,
  ROUND(SUM(total_logical_bytes) / SUM(total_partitions), 2) as avg_partition_bytes,
  ROUND(AVG(total_partitions), 0) as avg_partitions_scanned,
  -- Clustering ratio (internal metric - approximation)
  ROUND(SUM(total_logical_bytes) / SUM(total_physical_bytes), 2) as clustering_ratio
FROM `ca-lobby.ca_lobby`.INFORMATION_SCHEMA.TABLE_STORAGE
WHERE table_name IN (
  'CVR_LOBBY_DISCLOSURE_CD_OPTIMIZED',
  'LPAY_CD_OPTIMIZED_WITH_DATE',
  'filername_cd_OPTIMIZED'
)
GROUP BY table_name;
```

---

### Phase 5: Materialized View Freshness Check

```sql
-- ============================================================================
-- MATERIALIZED VIEW MONITORING
-- Checks refresh status and performance
-- ============================================================================

SELECT
  table_name,
  option_value as refresh_interval_minutes,
  DATE_DIFF(CURRENT_TIMESTAMP(), TIMESTAMP_MILLIS(CAST(last_refresh_time AS INT64)), MINUTE) as minutes_since_refresh,
  CASE
    WHEN DATE_DIFF(CURRENT_TIMESTAMP(), TIMESTAMP_MILLIS(CAST(last_refresh_time AS INT64)), MINUTE) < CAST(option_value AS INT64)
    THEN 'FRESH'
    ELSE 'STALE'
  END as freshness_status
FROM `ca-lobby.ca_lobby`.INFORMATION_SCHEMA.TABLE_OPTIONS
WHERE option_name = 'refresh_interval_minutes'
  AND table_name LIKE 'MV_%'
ORDER BY table_name;
```

---

## Cost Analysis

### Current State (Estimated)

Assumptions:
- 1,000 queries per month
- Average query scans 10 GB
- BigQuery pricing: $5 per TB scanned

```
Monthly query volume: 1,000 queries
Average data scanned: 10 GB per query
Total data scanned: 10,000 GB (10 TB)
Monthly cost: 10 TB × $5/TB = $50/month
Annual cost: $600/year
```

---

### Optimized State (Projected)

With partitioning, clustering, and materialized views:

#### Scenario 1: Text Search Queries (40% of total)
```
Queries: 400/month
Data scanned before: 12 GB per query
Data scanned after: 0.5 GB per query (Materialized View)
Reduction: 95.8%

Cost before: 400 × 12 GB = 4,800 GB = 4.8 TB × $5 = $24/month
Cost after: 400 × 0.5 GB = 200 GB = 0.2 TB × $5 = $1/month
Savings: $23/month = $276/year
```

#### Scenario 2: Date Range Queries (30% of total)
```
Queries: 300/month
Data scanned before: 8 GB per query (full table)
Data scanned after: 0.4 GB per query (partition pruning)
Reduction: 95%

Cost before: 300 × 8 GB = 2,400 GB = 2.4 TB × $5 = $12/month
Cost after: 300 × 0.4 GB = 120 GB = 0.12 TB × $5 = $0.60/month
Savings: $11.40/month = $136.80/year
```

#### Scenario 3: Aggregate Queries (20% of total)
```
Queries: 200/month
Data scanned before: 15 GB per query (multi-table joins)
Data scanned after: 0.2 GB per query (materialized view)
Reduction: 98.7%

Cost before: 200 × 15 GB = 3,000 GB = 3 TB × $5 = $15/month
Cost after: 200 × 0.2 GB = 40 GB = 0.04 TB × $5 = $0.20/month
Savings: $14.80/month = $177.60/year
```

#### Scenario 4: Other Queries (10% of total)
```
Queries: 100/month
Data scanned before: 10 GB per query
Data scanned after: 2 GB per query (clustering benefits)
Reduction: 80%

Cost before: 100 × 10 GB = 1,000 GB = 1 TB × $5 = $5/month
Cost after: 100 × 2 GB = 200 GB = 0.2 TB × $5 = $1/month
Savings: $4/month = $48/year
```

---

### Total Cost Savings Summary

| Category | Monthly Before | Monthly After | Monthly Savings | Annual Savings |
|----------|---------------|---------------|-----------------|----------------|
| Text Search (40%) | $24.00 | $1.00 | $23.00 | $276.00 |
| Date Range (30%) | $12.00 | $0.60 | $11.40 | $136.80 |
| Aggregates (20%) | $15.00 | $0.20 | $14.80 | $177.60 |
| Other (10%) | $5.00 | $1.00 | $4.00 | $48.00 |
| **TOTAL** | **$56.00** | **$2.80** | **$53.20** | **$638.40** |

**Overall Reduction**: **95% cost savings**

---

### Storage Cost Impact

Optimized tables and materialized views increase storage:

```
Original tables size: ~100 GB (estimated)
Optimized tables (with clustering): ~110 GB (+10%)
Denormalized tables (with RPT_DATE): ~140 GB (+40%)
Materialized views: ~20 GB (pre-computed aggregates)

Total storage: 270 GB (2.7× original)
```

BigQuery storage pricing:
- Active storage: $0.02 per GB per month
- Long-term storage (90+ days): $0.01 per GB per month

```
Storage cost (active): 270 GB × $0.02 = $5.40/month = $64.80/year
```

**Net Savings**: $638.40 - $64.80 = **$573.60/year**

**ROI**: 987% (save $10 for every $1 spent on storage)

---

### Break-Even Analysis

```
One-time implementation cost: ~$500 (labor)
Monthly savings: $53.20
Break-even: 10 months

After Year 1: $573.60 net savings
After Year 2: $1,212.00 cumulative savings
After Year 3: $1,850.40 cumulative savings
```

---

## Rollback Procedures

All optimizations are **non-destructive** - original tables remain unchanged.

### Quick Rollback: Keep Both Tables

**Recommended approach** - No downtime, instant rollback:

```sql
-- Original tables remain as-is:
SELECT * FROM `ca-lobby.ca_lobby.CVR_LOBBY_DISCLOSURE_CD`;

-- Optimized tables created alongside:
SELECT * FROM `ca-lobby.ca_lobby.CVR_LOBBY_DISCLOSURE_CD_OPTIMIZED`;

-- To "rollback", simply query original tables
-- No action needed!
```

**Storage cost**: Temporarily doubles (acceptable for risk mitigation)

---

### Gradual Cutover Strategy

Test optimized tables in parallel before full cutover:

**Week 1-2**: Dual-running
```sql
-- Run queries against BOTH old and new tables
-- Compare results for accuracy
-- Monitor performance metrics
```

**Week 3-4**: Gradual migration
```sql
-- Update applications to use optimized tables
-- Keep original tables as backup
```

**Week 5+**: Full migration
```sql
-- All queries use optimized tables
-- Original tables kept for 30 days
-- Then archived or deleted
```

---

### Delete Optimized Tables (Full Rollback)

If you need to completely remove optimizations:

```sql
-- ============================================================================
-- COMPLETE ROLLBACK SCRIPT
-- Removes all optimized tables and materialized views
-- USE WITH CAUTION - This is destructive
-- ============================================================================

-- Drop all optimized tables
DROP TABLE IF EXISTS `ca-lobby.ca_lobby.CVR_LOBBY_DISCLOSURE_CD_OPTIMIZED`;
DROP TABLE IF EXISTS `ca-lobby.ca_lobby.LPAY_CD_OPTIMIZED`;
DROP TABLE IF EXISTS `ca-lobby.ca_lobby.LPAY_CD_OPTIMIZED_WITH_DATE`;
DROP TABLE IF EXISTS `ca-lobby.ca_lobby.filername_cd_OPTIMIZED`;
DROP TABLE IF EXISTS `ca-lobby.ca_lobby.CVR_REGISTRATION_CD_OPTIMIZED`;
DROP TABLE IF EXISTS `ca-lobby.ca_lobby.LEXP_CD_OPTIMIZED`;
DROP TABLE IF EXISTS `ca-lobby.ca_lobby.LEMP_CD_OPTIMIZED`;
DROP TABLE IF EXISTS `ca-lobby.ca_lobby.FILER_FILINGS_CD_OPTIMIZED`;
DROP TABLE IF EXISTS `ca-lobby.ca_lobby.LCCM_CD_OPTIMIZED`;
DROP TABLE IF EXISTS `ca-lobby.ca_lobby.LOTH_CD_OPTIMIZED`;
DROP TABLE IF EXISTS `ca-lobby.ca_lobby.FILER_ADDRESS_CD_OPTIMIZED`;

-- Drop all materialized views
DROP MATERIALIZED VIEW IF EXISTS `ca-lobby.ca_lobby.MV_ALAMEDA_FILERS`;
DROP MATERIALIZED VIEW IF EXISTS `ca-lobby.ca_lobby.MV_PAYMENT_TOTALS_BY_YEAR`;
DROP MATERIALIZED VIEW IF EXISTS `ca-lobby.ca_lobby.MV_LOBBYING_ACTIVITY_SUMMARY`;
DROP MATERIALIZED VIEW IF EXISTS `ca-lobby.ca_lobby.MV_EMPLOYER_FIRM_RELATIONSHIPS`;
DROP MATERIALIZED VIEW IF EXISTS `ca-lobby.ca_lobby.filername_cd_SEARCH_MV`;
DROP MATERIALIZED VIEW IF EXISTS `ca-lobby.ca_lobby.LEMP_CD_EMPLOYER_SEARCH_MV`;

-- Drop search indexes (if created)
DROP SEARCH INDEX IF EXISTS idx_filer_name_search
  ON `ca-lobby.ca_lobby.filername_cd_OPTIMIZED`;
DROP SEARCH INDEX IF EXISTS idx_firm_name_search
  ON `ca-lobby.ca_lobby.CVR_LOBBY_DISCLOSURE_CD_OPTIMIZED`;
DROP SEARCH INDEX IF EXISTS idx_employer_name_search
  ON `ca-lobby.ca_lobby.LEMP_CD_OPTIMIZED`;

-- Verify deletion
SELECT table_name, table_type
FROM `ca-lobby.ca_lobby`.INFORMATION_SCHEMA.TABLES
WHERE table_name LIKE '%OPTIMIZED%' OR table_name LIKE 'MV_%';
-- Should return 0 rows
```

---

### Partial Rollback (Individual Tables)

Rollback specific tables while keeping others:

```sql
-- Example: Rollback only LPAY_CD optimization
DROP TABLE IF EXISTS `ca-lobby.ca_lobby.LPAY_CD_OPTIMIZED_WITH_DATE`;

-- Update queries to use original table
SELECT * FROM `ca-lobby.ca_lobby.LPAY_CD`;  -- Back to original
```

---

### Rollback Materialized View Only

```sql
-- Disable auto-refresh (stops updates but keeps data)
ALTER MATERIALIZED VIEW `ca-lobby.ca_lobby.MV_ALAMEDA_FILERS`
SET OPTIONS(enable_refresh = FALSE);

-- Or completely drop the materialized view
DROP MATERIALIZED VIEW `ca-lobby.ca_lobby.MV_ALAMEDA_FILERS`;

-- Queries automatically fall back to base tables
```

---

## Maintenance Schedule

### Daily: NONE REQUIRED

BigQuery handles all optimization automatically:
- ✅ Partition pruning: Automatic
- ✅ Clustering maintenance: Automatic (re-clustering as needed)
- ✅ Statistics updates: Automatic
- ✅ Materialized view refresh: Automatic (per configured schedule)

**No daily DBA tasks needed!**

---

### Weekly: Monitoring (5 minutes)

```sql
-- ============================================================================
-- WEEKLY HEALTH CHECK
-- Run every Monday morning
-- ============================================================================

-- 1. Check materialized view freshness
SELECT
  table_name,
  DATE_DIFF(CURRENT_TIMESTAMP(), TIMESTAMP_MILLIS(CAST(last_refresh_time AS INT64)), HOUR) as hours_since_refresh,
  option_value as refresh_interval_minutes
FROM `ca-lobby.ca_lobby`.INFORMATION_SCHEMA.TABLE_OPTIONS
WHERE option_name = 'refresh_interval_minutes'
  AND table_name LIKE 'MV_%'
ORDER BY hours_since_refresh DESC;

-- Alert if any MV is stale (> 2× refresh interval)

-- 2. Check query performance trends
SELECT
  DATE(creation_time) as query_date,
  COUNT(*) as query_count,
  ROUND(AVG(total_bytes_processed / POW(10, 9)), 2) as avg_gb_scanned,
  ROUND(AVG(total_slot_ms / 1000), 2) as avg_slot_seconds
FROM `ca-lobby.region-us`.INFORMATION_SCHEMA.JOBS_BY_PROJECT
WHERE DATE(creation_time) >= DATE_SUB(CURRENT_DATE(), INTERVAL 7 DAY)
  AND statement_type = 'SELECT'
GROUP BY query_date
ORDER BY query_date;

-- Look for sudden spikes in data scanned

-- 3. Check table sizes
SELECT
  table_name,
  ROUND(size_bytes / POW(10, 9), 2) as size_gb,
  row_count
FROM `ca-lobby.ca_lobby`.INFORMATION_SCHEMA.TABLES
WHERE table_name LIKE '%OPTIMIZED%' OR table_name LIKE 'MV_%'
ORDER BY size_gb DESC;

-- Monitor for unexpected growth
```

---

### Monthly: Performance Review (30 minutes)

```sql
-- ============================================================================
-- MONTHLY PERFORMANCE REVIEW
-- Run on first Monday of each month
-- ============================================================================

-- 1. Query cost analysis (last 30 days)
SELECT
  EXTRACT(WEEK FROM creation_time) as week_number,
  COUNT(*) as query_count,
  ROUND(SUM(total_bytes_billed / POW(10, 12)) * 5, 2) as estimated_cost_usd,
  ROUND(AVG(total_bytes_processed / POW(10, 9)), 2) as avg_gb_per_query
FROM `ca-lobby.region-us`.INFORMATION_SCHEMA.JOBS_BY_PROJECT
WHERE creation_time >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 30 DAY)
  AND statement_type = 'SELECT'
GROUP BY week_number
ORDER BY week_number;

-- 2. Most expensive queries
SELECT
  REGEXP_EXTRACT(query, r'FROM `[^`]+\.([^`]+)`') as table_queried,
  COUNT(*) as execution_count,
  ROUND(AVG(total_bytes_processed / POW(10, 9)), 2) as avg_gb_scanned,
  ROUND(SUM(total_bytes_billed / POW(10, 12)) * 5, 2) as total_cost_usd
FROM `ca-lobby.region-us`.INFORMATION_SCHEMA.JOBS_BY_PROJECT
WHERE creation_time >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 30 DAY)
  AND statement_type = 'SELECT'
GROUP BY table_queried
ORDER BY total_cost_usd DESC
LIMIT 20;

-- 3. Identify optimization opportunities
SELECT
  query,
  ROUND(total_bytes_processed / POW(10, 9), 2) as gb_scanned,
  ROUND(total_slot_ms / 1000, 2) as slot_seconds,
  ROUND((total_bytes_billed / POW(10, 12)) * 5, 4) as cost_usd
FROM `ca-lobby.region-us`.INFORMATION_SCHEMA.JOBS_BY_PROJECT
WHERE creation_time >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 30 DAY)
  AND statement_type = 'SELECT'
  AND total_bytes_processed > 5 * POW(10, 9)  -- Queries scanning > 5 GB
ORDER BY total_bytes_processed DESC
LIMIT 10;

-- Review these queries for further optimization
```

---

### Quarterly: Strategic Review (2 hours)

**Q1, Q2, Q3, Q4 Reviews**:

1. **Review materialized view usage**
   - Are all MVs being used?
   - Are new MVs needed?
   - Should refresh intervals change?

2. **Evaluate clustering effectiveness**
   - Run clustering quality checks
   - Consider re-clustering if ratio > 50

3. **Review partitioning strategy**
   - Are partition sizes optimal? (Target: 1-10 GB per partition)
   - Consider partition expiration for old data

4. **Cost-benefit analysis**
   - Calculate actual savings vs projections
   - Evaluate storage costs vs query savings

5. **Update optimization plan**
   - New query patterns emerged?
   - New tables added?
   - Adjust clustering/partitioning as needed

---

### Annual: Comprehensive Audit (1 day)

**Once per year**:

1. **Full performance re-benchmark**
   - Re-run baseline tests
   - Compare to Year 0 metrics
   - Document improvements

2. **Storage cleanup**
   - Archive old partitions (if not needed)
   - Remove unused materialized views
   - Clean up test tables

3. **Schema review**
   - Any new columns need clustering?
   - Any tables need partitioning changes?
   - Update documentation

4. **Cost analysis**
   - Full year cost comparison
   - ROI calculation
   - Budget planning for next year

5. **Training update**
   - Update team on new features
   - Review query best practices
   - Share performance wins

---

### Automated Monitoring (Optional)

Set up alerts using Cloud Monitoring:

```sql
-- Create BigQuery job alert
-- Alert when query scans > 50 GB (possible unoptimized query)

-- This is configured in Cloud Console, not SQL
-- Navigate to: Cloud Console > Monitoring > Alerting > Create Policy

Alert Condition:
  Metric: bigquery.googleapis.com/job/query/scanned_bytes
  Threshold: > 50 GB
  Duration: 1 minute

Notification:
  Email: your-team@example.com
  Message: "Large query detected - possible optimization opportunity"
```

---

## Implementation Timeline

### Week 1: Preparation and Priority 1 Tables

**Day 1: Setup and Baseline**
- [ ] Run baseline performance tests (all 5 tests)
- [ ] Document current query costs
- [ ] Export baseline metrics to spreadsheet
- [ ] Review and confirm table priorities

**Day 2: Critical Materialized View**
- [ ] Create `MV_ALAMEDA_FILERS` (most important optimization)
- [ ] Test queries using MV vs original
- [ ] Verify MV auto-refresh is working
- [ ] Update 2-3 most frequent queries to use MV

**Day 3: CVR_LOBBY_DISCLOSURE_CD**
- [ ] Create `CVR_LOBBY_DISCLOSURE_CD_OPTIMIZED` with partitioning and clustering
- [ ] Run test queries comparing old vs new
- [ ] Document performance improvements
- [ ] Keep both tables running in parallel

**Day 4: filername_cd (Filer Registry)**
- [ ] Create `filername_cd_OPTIMIZED` with clustering
- [ ] Attempt Search Index creation (if available)
- [ ] If Search Index not available, create `filername_cd_SEARCH_MV`
- [ ] Test text search performance

**Day 5: CVR_REGISTRATION_CD + Testing**
- [ ] Create `CVR_REGISTRATION_CD_OPTIMIZED`
- [ ] Run comprehensive tests on all Week 1 optimizations
- [ ] Compare performance metrics vs baseline
- [ ] Document wins and issues

---

### Week 2: Priority 2 Tables and Complex MVs

**Day 6: LPAY_CD (Payments)**
- [ ] Create `LPAY_CD_OPTIMIZED_WITH_DATE` (denormalized)
- [ ] Test date range queries
- [ ] Verify JOIN performance improvements
- [ ] Create `MV_PAYMENT_TOTALS_BY_YEAR`

**Day 7: LEXP_CD (Expenditures)**
- [ ] Create `LEXP_CD_OPTIMIZED` (denormalized)
- [ ] Test aggregate queries
- [ ] Compare performance to original table

**Day 8: LEMP_CD (Employers)**
- [ ] Create `LEMP_CD_OPTIMIZED`
- [ ] Create `LEMP_CD_EMPLOYER_SEARCH_MV` (if text search needed)
- [ ] Test employer-firm relationship queries

**Day 9: Complex Materialized Views**
- [ ] Create `MV_LOBBYING_ACTIVITY_SUMMARY`
- [ ] Create `MV_EMPLOYER_FIRM_RELATIONSHIPS`
- [ ] Test dashboard-style queries

**Day 10: Week 2 Testing**
- [ ] Run all test queries against new tables
- [ ] Compare Week 2 performance to baseline
- [ ] Document cumulative improvements

---

### Week 3: Priority 3 Tables and Validation

**Day 11: FILER_FILINGS_CD**
- [ ] Create `FILER_FILINGS_CD_OPTIMIZED`
- [ ] Test join performance improvements

**Day 12: LCCM_CD + LOTH_CD**
- [ ] Create `LCCM_CD_OPTIMIZED` (partition by CTRIB_DATE)
- [ ] Create `LOTH_CD_OPTIMIZED`
- [ ] Test queries

**Day 13: FILER_ADDRESS_CD + Supporting Tables**
- [ ] Create `FILER_ADDRESS_CD_OPTIMIZED`
- [ ] Optimize any remaining frequently-queried tables
- [ ] Create additional MVs if identified

**Day 14: Comprehensive Testing**
- [ ] Run ALL test queries (baseline vs optimized)
- [ ] Generate performance comparison report
- [ ] Calculate actual cost savings
- [ ] Verify all MVs are auto-refreshing

**Day 15: Documentation and Review**
- [ ] Update query documentation with optimized versions
- [ ] Document all changes made
- [ ] Share performance wins with team
- [ ] Plan cutover strategy

---

### Week 4: Migration and Training

**Day 16-17: Application Updates**
- [ ] Identify all applications querying the database
- [ ] Update queries to use optimized tables
- [ ] Test applications end-to-end
- [ ] Monitor for errors

**Day 18: Team Training**
- [ ] Train team on new query patterns
- [ ] Share materialized views and how to use them
- [ ] Review cost monitoring dashboards
- [ ] Distribute updated query examples

**Day 19: Monitoring Setup**
- [ ] Set up Cloud Monitoring alerts
- [ ] Create weekly health check script
- [ ] Document maintenance procedures
- [ ] Schedule recurring tasks

**Day 20: Final Validation and Handoff**
- [ ] Run final performance tests
- [ ] Generate final cost comparison report
- [ ] Document rollback procedures
- [ ] Schedule 30-day review
- [ ] Mark project complete!

---

### Month 2: Observation Period

**Weeks 5-8**:
- [ ] Monitor query performance daily (first week)
- [ ] Monitor query performance 3× per week (weeks 2-4)
- [ ] Collect user feedback on performance
- [ ] Fine-tune any underperforming queries
- [ ] Adjust MV refresh intervals if needed
- [ ] Document lessons learned

**30-Day Review**:
- [ ] Calculate actual vs projected savings
- [ ] Identify any new optimization opportunities
- [ ] Plan Phase 2 optimizations (if any)
- [ ] Decide on original table retention/deletion

---

### Months 3-12: Steady State

**Monthly** (ongoing):
- [ ] Run monthly performance review (30 min)
- [ ] Review query costs and trends
- [ ] Identify new optimization opportunities
- [ ] Update documentation as needed

**Quarterly** (4 times per year):
- [ ] Strategic review (2 hours)
- [ ] Evaluate MV effectiveness
- [ ] Cost-benefit re-analysis
- [ ] Plan next optimizations

**Annual** (once per year):
- [ ] Comprehensive audit (1 day)
- [ ] Full re-benchmark
- [ ] Update team training
- [ ] Budget planning

---

## Implementation Checklist

### Pre-Implementation

- [ ] Read this entire document
- [ ] Understand BigQuery partitioning and clustering
- [ ] Verify permissions to create tables and MVs
- [ ] Confirm BigQuery quota is sufficient
- [ ] Identify 5-10 most frequent queries
- [ ] Document baseline performance

### Phase 1: Critical Optimizations

- [ ] Create `MV_ALAMEDA_FILERS` materialized view
- [ ] Create `CVR_LOBBY_DISCLOSURE_CD_OPTIMIZED` table
- [ ] Create `filername_cd_OPTIMIZED` table
- [ ] Create `CVR_REGISTRATION_CD_OPTIMIZED` table
- [ ] Run baseline tests and compare
- [ ] Document improvements

### Phase 2: Transaction Tables

- [ ] Create `LPAY_CD_OPTIMIZED_WITH_DATE` table
- [ ] Create `LEXP_CD_OPTIMIZED` table
- [ ] Create `LEMP_CD_OPTIMIZED` table
- [ ] Create `MV_PAYMENT_TOTALS_BY_YEAR` materialized view
- [ ] Test aggregate queries
- [ ] Verify date range filtering works

### Phase 3: Comprehensive Views

- [ ] Create `MV_LOBBYING_ACTIVITY_SUMMARY`
- [ ] Create `MV_EMPLOYER_FIRM_RELATIONSHIPS`
- [ ] Create Search Indexes (if available)
- [ ] Test complex dashboard queries
- [ ] Verify MV auto-refresh schedules

### Phase 4: Remaining Tables

- [ ] Optimize remaining Priority 3-4 tables as needed
- [ ] Create any additional MVs identified
- [ ] Run comprehensive testing
- [ ] Generate performance report

### Phase 5: Migration

- [ ] Update application queries to use optimized tables
- [ ] Train team on new query patterns
- [ ] Set up monitoring and alerts
- [ ] Schedule maintenance tasks
- [ ] Document rollback procedures

### Post-Implementation

- [ ] Monitor performance for 30 days
- [ ] Collect user feedback
- [ ] Calculate actual cost savings
- [ ] Fine-tune as needed
- [ ] Plan Phase 2 optimizations
- [ ] Celebrate success! 🎉

---

## Success Metrics

### Performance Targets

- [ ] Text search queries < 5 seconds (baseline: 45+ seconds)
- [ ] Date range queries < 3 seconds (baseline: 30+ seconds)
- [ ] Complex joins < 10 seconds (baseline: 60-180 seconds)
- [ ] Aggregate queries < 2 seconds (baseline: 30+ seconds)
- [ ] Dashboard queries < 5 seconds (baseline: 90+ seconds)

### Cost Targets

- [ ] Query cost reduction ≥ 80% (target: 85%)
- [ ] Data scanned reduction ≥ 80% (target: 90%)
- [ ] Monthly query costs < $5 (baseline: $50+)
- [ ] ROI > 500% in Year 1

### Quality Targets

- [ ] Zero query result discrepancies
- [ ] 100% MV auto-refresh success rate
- [ ] Zero downtime during implementation
- [ ] Zero rollbacks needed

### Operational Targets

- [ ] Team trained on new query patterns
- [ ] Monitoring dashboards created
- [ ] Documentation complete and current
- [ ] Maintenance procedures automated

---

## FAQs

### Q: Will this break existing queries?

**A:** No! All optimizations create NEW tables alongside existing ones. Original tables remain unchanged. You can gradually migrate queries at your own pace.

---

### Q: Do I need to maintain indexes like in SQL Server?

**A:** No! BigQuery automatically maintains partitions, clustering, and statistics. Materialized views auto-refresh on schedule. Zero manual maintenance required.

---

### Q: What if Search Indexes aren't available in my project?

**A:** Use the Materialized View approach with pre-computed UPPER() columns. Performance is still excellent (40-60% improvement vs 60-80% with Search Indexes).

---

### Q: How much will storage costs increase?

**A:** Approximately 2.7× original size:
- Optimized tables: +10% (clustering)
- Denormalized tables: +40% (added columns)
- Materialized views: +20% (pre-computed)

At $0.02/GB/month, this is ~$5/month for 270 GB, easily offset by $50+/month in query savings.

---

### Q: Can I optimize just some tables, not all?

**A:** Absolutely! Start with Priority 1 tables (CVR_LOBBY_DISCLOSURE_CD, LPAY_CD, filername_cd) and the Alameda filers MV. You'll see 80% of the benefit from these alone.

---

### Q: How do I know if optimizations are working?

**A:** Run the testing scripts in the "Testing and Validation" section. The performance comparison report shows before/after metrics with cost savings.

---

### Q: What if performance gets worse?

**A:** Simply query the original tables - they're unchanged. Investigate the issue, and if needed, use the rollback scripts to remove optimizations. No permanent harm done.

---

### Q: How often should materialized views refresh?

**A:** Depends on data freshness needs:
- `MV_ALAMEDA_FILERS`: Hourly (low change frequency)
- `MV_PAYMENT_TOTALS_BY_YEAR`: Every 6 hours (moderate changes)
- `MV_LOBBYING_ACTIVITY_SUMMARY`: Every 12 hours (summary data)
- `MV_EMPLOYER_FIRM_RELATIONSHIPS`: Daily (relationships rarely change)

Adjust based on your requirements.

---

### Q: Can I partition by columns other than dates?

**A:** BigQuery partitioning requires:
- DATE column (most common)
- TIMESTAMP column
- INTEGER column (range partitioning)

For non-date columns, use **clustering** instead (up to 4 columns).

---

### Q: What's the difference between partitioning and clustering?

**A:**
- **Partitioning**: Physically separates data into segments (by date). BigQuery skips entire partitions when not needed. Dramatic cost reduction.
- **Clustering**: Sorts data within each partition by specified columns. Improves scan efficiency. Moderate cost reduction.

**Use both together** for maximum benefit!

---

### Q: How do I monitor costs after optimization?

**A:** Use the weekly/monthly monitoring queries in the "Maintenance Schedule" section. Key metrics:
- `total_bytes_billed` (cost driver)
- `total_slot_ms` (processing time)
- Query count trends

BigQuery Console also has built-in cost dashboards.

---

### Q: Can I use these techniques on other datasets?

**A:** Yes! The patterns in this plan apply to any BigQuery dataset:
1. Partition by DATE columns
2. Cluster by frequently filtered columns
3. Create MVs for repeated aggregations
4. Denormalize when it helps partitioning

Adjust specifics to your schema and query patterns.

---

## Additional Resources

### Official BigQuery Documentation

- [BigQuery Partitioning Guide](https://cloud.google.com/bigquery/docs/partitioned-tables)
- [BigQuery Clustering Guide](https://cloud.google.com/bigquery/docs/clustered-tables)
- [Materialized Views](https://cloud.google.com/bigquery/docs/materialized-views-intro)
- [Search Indexes (Preview)](https://cloud.google.com/bigquery/docs/search-intro)
- [Query Optimization Best Practices](https://cloud.google.com/bigquery/docs/best-practices-performance-overview)
- [Cost Optimization](https://cloud.google.com/bigquery/docs/best-practices-costs)

### Community Resources

- [BigQuery Optimization Reddit](https://www.reddit.com/r/bigquery/)
- [Google Cloud Community](https://cloud.google.com/community)
- [Stack Overflow - BigQuery Tag](https://stackoverflow.com/questions/tagged/google-bigquery)

### Training

- [Google Cloud Skills Boost - BigQuery](https://www.cloudskillsboost.google/course_templates/624)
- [Coursera - BigQuery for Data Analysis](https://www.coursera.org/learn/bigquery-basics-for-data-analysts)

---

## Conclusion

This optimization plan transforms the California lobbying database from a traditional SQL Server mindset to BigQuery's modern, columnar architecture. By leveraging partitioning, clustering, and materialized views, you'll achieve:

✅ **90-95% faster queries**
✅ **80-90% cost reduction**
✅ **Zero maintenance overhead**
✅ **Improved user experience**
✅ **Scalable performance**

**Key Success Factors**:

1. **Start with Priority 1** - Alameda filers MV + critical tables
2. **Test in parallel** - Keep original tables until confident
3. **Monitor continuously** - Use provided health check scripts
4. **Iterate and improve** - Optimize based on actual usage patterns

**Remember**: All optimizations are reversible. You can't break anything by trying. Start small, measure results, and expand from there.

Good luck! 🚀

---

**Questions or Issues?**
Refer to the FAQ section or contact your BigQuery administrator.

**Document Version**: 1.0
**Last Updated**: October 24, 2025
**Next Review**: January 24, 2026

---

## Appendix A: Quick Reference Commands

### Create Partitioned + Clustered Table
```sql
CREATE OR REPLACE TABLE `project.dataset.table_OPTIMIZED`
PARTITION BY DATE(date_column)
CLUSTER BY col1, col2, col3, col4
AS SELECT * FROM `project.dataset.table`;
```

### Create Materialized View
```sql
CREATE MATERIALIZED VIEW `project.dataset.MV_NAME`
CLUSTER BY key_column
OPTIONS(enable_refresh = TRUE, refresh_interval_minutes = 60)
AS SELECT ... FROM base_table;
```

### Create Search Index (Preview)
```sql
CREATE SEARCH INDEX index_name
ON `project.dataset.table`(text_column1, text_column2)
OPTIONS(analyzer = 'LOG_ANALYZER');
```

### Check Table Info
```sql
SELECT table_name, partition_expiration_days, clustering_fields
FROM `project.dataset`.INFORMATION_SCHEMA.TABLES
WHERE table_name = 'your_table';
```

### Check Query Costs
```sql
SELECT
  creation_time,
  query,
  ROUND(total_bytes_billed / POW(10, 9), 2) as gb_billed,
  ROUND((total_bytes_billed / POW(10, 12)) * 5, 4) as cost_usd
FROM `project.region-us`.INFORMATION_SCHEMA.JOBS_BY_PROJECT
WHERE creation_time >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 1 HOUR)
ORDER BY creation_time DESC;
```

---

## Appendix B: SQL Server to BigQuery Translation

| SQL Server | BigQuery Equivalent | Notes |
|------------|-------------------|-------|
| `CREATE CLUSTERED INDEX` | `CLUSTER BY` in table DDL | Primary data ordering |
| `CREATE NONCLUSTERED INDEX` | Add to `CLUSTER BY` (max 4) | Additional ordering |
| `CREATE INDEX ... INCLUDE` | Clustering + columnar storage | No INCLUDE needed |
| `CREATE FULLTEXT INDEX` | `CREATE SEARCH INDEX` | Preview feature |
| `CREATE FILTERED INDEX` | `PARTITION BY` | Partition pruning |
| `CREATE VIEW WITH SCHEMABINDING` | `CREATE MATERIALIZED VIEW` | Pre-computed |
| `UPDATE STATISTICS` | Automatic | No manual updates |
| `REBUILD INDEX` | Automatic re-clustering | No manual maintenance |
| `WHERE CONTAINS(col, 'term')` | `WHERE SEARCH(table, 'term')` | Search Index |
| `WHERE col LIKE '%term%'` | Use Search Index or MV | Avoid LIKE on large tables |

---

**END OF DOCUMENT**
