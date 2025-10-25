# Database Indexing Plan for CAL-ACCESS Lobbying Tables

## Executive Summary

This plan outlines a comprehensive strategy for adding indexes to the CAL-ACCESS lobbying database tables to optimize query performance, particularly for name-based searches (like "ALAMEDA") that are run frequently. Proper indexing can reduce query execution time from minutes to seconds on large tables.

---

## Table of Contents
1. [Current Performance Issues](#current-performance-issues)
2. [Indexing Strategy Overview](#indexing-strategy-overview)
3. [Priority Tables for Indexing](#priority-tables-for-indexing)
4. [Detailed Index Recommendations](#detailed-index-recommendations)
5. [Implementation Plan](#implementation-plan)
6. [Testing and Validation](#testing-and-validation)
7. [Maintenance Plan](#maintenance-plan)
8. [Performance Monitoring](#performance-monitoring)

---

## Current Performance Issues

### Problem Statement
- Text searches using `LIKE '%ALAMEDA%'` perform full table scans
- Large tables (millions of records) cause slow query response times
- Multiple table joins compound performance issues
- No current indexes on name fields in lobbying tables

### Expected Performance Gains
- **Without indexes:** 30-120 seconds for complex queries
- **With indexes:** 1-5 seconds for same queries
- **Improvement:** 85-95% reduction in query time

---

## Indexing Strategy Overview

### Types of Indexes to Implement

#### 1. **B-Tree Indexes** (Standard)
- Best for exact matches and range queries
- Use for: Primary keys, foreign keys, frequently filtered columns

#### 2. **Full-Text Indexes**
- Best for text searching within fields
- Use for: Name fields, description fields
- Supports: CONTAINS, FREETEXT operators

#### 3. **Composite Indexes**
- Combines multiple columns
- Use for: Common query patterns with multiple WHERE conditions

#### 4. **Filtered Indexes**
- Index subset of data based on conditions
- Use for: Specific entity types or date ranges

---

## Priority Tables for Indexing

### Priority Level 1: HIGH (Implement First)
These tables are queried most frequently and contain the most records:

1. **CVR_LOBBY_DISCLOSURE_CD** - Primary disclosure data
2. **CVR_REGISTRATION_CD** - Registration information
3. **FILERS_CD** - Master filer registry
4. **LPAY_CD** - Payment transactions (high volume)
5. **LEXP_CD** - Expenditure transactions (high volume)

### Priority Level 2: MEDIUM (Implement Second)
Supporting tables with moderate query frequency:

6. **LEMP_CD** - Employer relationships
7. **LCCM_CD** - Campaign contributions
8. **LOTH_CD** - Other payments
9. **FILER_FILINGS_CD** - Filing index
10. **FILER_ADDRESS_CD** - Address information

### Priority Level 3: LOW (Implement Last)
Less frequently queried tables:

11. **LATT_CD** - Attachments
12. **LOBBY_AMENDMENTS_CD** - Amendments
13. **NAMES_CD** - Name registry
14. **TEXT_MEMO_CD** - Text memos

---

## Detailed Index Recommendations

### Table 1: CVR_LOBBY_DISCLOSURE_CD

#### Existing Indexes (Assumed)
```sql
-- Primary Key (already exists)
CREATE UNIQUE INDEX PK_CVR_LOBBY_DISCLOSURE 
ON CVR_LOBBY_DISCLOSURE_CD(FILING_ID);
```

#### Recommended New Indexes

```sql
-- Index 1: Filer Name Full-Text Search
CREATE FULLTEXT INDEX FTI_CVR_LOBBY_FILER_NAME
ON CVR_LOBBY_DISCLOSURE_CD(FILER_NAML, FILER_NAMF)
KEY INDEX PK_CVR_LOBBY_DISCLOSURE;

-- Index 2: Firm Name Full-Text Search
CREATE FULLTEXT INDEX FTI_CVR_LOBBY_FIRM_NAME
ON CVR_LOBBY_DISCLOSURE_CD(FIRM_NAME)
KEY INDEX PK_CVR_LOBBY_DISCLOSURE;

-- Index 3: Composite - Filer ID and Date Range
CREATE INDEX IDX_CVR_LOBBY_FILER_DATE
ON CVR_LOBBY_DISCLOSURE_CD(FILER_ID, FROM_DATE, THRU_DATE);

-- Index 4: Entity Code and Form Type
CREATE INDEX IDX_CVR_LOBBY_ENTITY_FORM
ON CVR_LOBBY_DISCLOSURE_CD(ENTITY_CD, FORM_TYPE);

-- Index 5: Filing ID and Amendment
CREATE INDEX IDX_CVR_LOBBY_FILING_AMEND
ON CVR_LOBBY_DISCLOSURE_CD(FILING_ID, AMEND_ID);

-- Index 6: Firm ID for joins
CREATE INDEX IDX_CVR_LOBBY_FIRM_ID
ON CVR_LOBBY_DISCLOSURE_CD(FIRM_ID);
```

**Rationale:**
- Full-text indexes enable fast CONTAINS queries for name searches
- Composite indexes optimize common filter combinations
- Date range index supports time-based queries
- Firm ID index improves join performance

---

### Table 2: CVR_REGISTRATION_CD

#### Recommended Indexes

```sql
-- Index 1: Filer Name Full-Text Search
CREATE FULLTEXT INDEX FTI_CVR_REG_FILER_NAME
ON CVR_REGISTRATION_CD(FILER_NAML, FILER_NAMF)
KEY INDEX PK_CVR_REGISTRATION;

-- Index 2: Firm Name Full-Text Search
CREATE FULLTEXT INDEX FTI_CVR_REG_FIRM_NAME
ON CVR_REGISTRATION_CD(FIRM_NAME)
KEY INDEX PK_CVR_REGISTRATION;

-- Index 3: Authorized Firm Name
CREATE FULLTEXT INDEX FTI_CVR_REG_AUTH_FIRM
ON CVR_REGISTRATION_CD(A_T_FIRM)
KEY INDEX PK_CVR_REGISTRATION;

-- Index 4: Composite - Filer ID and Entity Type
CREATE INDEX IDX_CVR_REG_FILER_ENTITY
ON CVR_REGISTRATION_CD(FILER_ID, ENTITY_CD);

-- Index 5: Date Qualified
CREATE INDEX IDX_CVR_REG_DATE_QUAL
ON CVR_REGISTRATION_CD(DATE_QUAL);

-- Index 6: Entity Code Filter
CREATE INDEX IDX_CVR_REG_ENTITY
ON CVR_REGISTRATION_CD(ENTITY_CD)
INCLUDE (FILER_ID, FIRM_NAME);
```

**Rationale:**
- Multiple name fields require separate full-text indexes
- Entity code index enables fast filtering by organization type
- Date qualified supports time-based analysis

---

### Table 3: FILERS_CD (Master Registry)

#### Recommended Indexes

```sql
-- Index 1: Filer Name Full-Text Search
CREATE FULLTEXT INDEX FTI_FILERS_NAME
ON FILERS_CD(FILER_NAML, FILER_NAMF)
KEY INDEX PK_FILERS;

-- Index 2: Filer Type
CREATE INDEX IDX_FILERS_TYPE
ON FILERS_CD(FILER_TYPE)
INCLUDE (FILER_ID, FILER_NAML);

-- Index 3: Status and Effective Date
CREATE INDEX IDX_FILERS_STATUS_DATE
ON FILERS_CD(STATUS, EFFECT_DT);

-- Index 4: Cross-Reference ID
CREATE INDEX IDX_FILERS_XREF
ON FILERS_CD(XREF_FILER_ID);

-- Index 5: Composite - Name and Type
CREATE INDEX IDX_FILERS_NAME_TYPE
ON FILERS_CD(FILER_NAML, FILER_TYPE);
```

**Rationale:**
- Master table is joined frequently - needs comprehensive indexing
- Name search is most common query pattern
- Status and type filters are frequently used

---

### Table 4: LPAY_CD (Payments)

#### Recommended Indexes

```sql
-- Index 1: Payee Name Full-Text Search
CREATE FULLTEXT INDEX FTI_LPAY_PAYEE_NAME
ON LPAY_CD(PAYEE_NAML, PAYEE_NAMF)
KEY INDEX PK_LPAY;

-- Index 2: Composite - Filer and Filing
CREATE INDEX IDX_LPAY_FILER_FILING
ON LPAY_CD(FILER_ID, FILING_ID)
INCLUDE (AMOUNT, CUM_YTD);

-- Index 3: Amount Range Queries
CREATE INDEX IDX_LPAY_AMOUNT
ON LPAY_CD(AMOUNT)
WHERE AMOUNT > 0;

-- Index 4: Amendment Tracking
CREATE INDEX IDX_LPAY_AMEND
ON LPAY_CD(FILING_ID, AMEND_ID);

-- Index 5: Transaction ID
CREATE INDEX IDX_LPAY_TRANSACTION
ON LPAY_CD(BAKREF_TID);

-- Index 6: Form Type
CREATE INDEX IDX_LPAY_FORM_TYPE
ON LPAY_CD(FORM_TYPE);
```

**Rationale:**
- High-volume table requires multiple indexes
- INCLUDE clause adds frequently selected columns
- Filtered index on AMOUNT excludes zero-value records

---

### Table 5: LEXP_CD (Expenditures)

#### Recommended Indexes

```sql
-- Index 1: Payee Name Full-Text Search
CREATE FULLTEXT INDEX FTI_LEXP_PAYEE_NAME
ON LEXP_CD(PAYEE_NAML, PAYEE_NAMF)
KEY INDEX PK_LEXP;

-- Index 2: Expense Description Full-Text
CREATE FULLTEXT INDEX FTI_LEXP_DESCRIPTION
ON LEXP_CD(EXPN_DSCR)
KEY INDEX PK_LEXP;

-- Index 3: Composite - Filer and Filing
CREATE INDEX IDX_LEXP_FILER_FILING
ON LEXP_CD(FILER_ID, FILING_ID)
INCLUDE (AMOUNT);

-- Index 4: Amount for Summaries
CREATE INDEX IDX_LEXP_AMOUNT
ON LEXP_CD(AMOUNT)
WHERE AMOUNT > 0;

-- Index 5: Transaction Tracking
CREATE INDEX IDX_LEXP_TRANSACTION
ON LEXP_CD(BAKREF_TID);
```

**Rationale:**
- Description field often searched for specific keywords
- Similar structure to LPAY_CD for consistency

---

### Table 6: LEMP_CD (Employers)

#### Recommended Indexes

```sql
-- Index 1: Employer Name Full-Text Search
CREATE FULLTEXT INDEX FTI_LEMP_NAME
ON LEMP_CD(AGCY_NAML, AGCY_NAMF)
KEY INDEX PK_LEMP;

-- Index 2: Composite - Filer and Filing
CREATE INDEX IDX_LEMP_FILER_FILING
ON LEMP_CD(FILER_ID, FILING_ID);

-- Index 3: Form Type
CREATE INDEX IDX_LEMP_FORM_TYPE
ON LEMP_CD(FORM_TYPE);

-- Index 4: Record Type
CREATE INDEX IDX_LEMP_REC_TYPE
ON LEMP_CD(REC_TYPE);
```

---

### Table 7: LCCM_CD (Campaign Contributions)

#### Recommended Indexes

```sql
-- Index 1: Contributor Name Full-Text Search
CREATE FULLTEXT INDEX FTI_LCCM_CONTRIBUTOR_NAME
ON LCCM_CD(PAYOR_NAML, PAYOR_NAMF)
KEY INDEX PK_LCCM;

-- Index 2: Composite - Filer and Committee
CREATE INDEX IDX_LCCM_FILER_CMTE
ON LCCM_CD(FILER_ID, CMTE_ID)
INCLUDE (AMOUNT, CTRIB_DATE);

-- Index 3: Contribution Date
CREATE INDEX IDX_LCCM_DATE
ON LCCM_CD(CTRIB_DATE);

-- Index 4: Amount
CREATE INDEX IDX_LCCM_AMOUNT
ON LCCM_CD(AMOUNT)
WHERE AMOUNT > 0;
```

---

### Table 8: LOTH_CD (Other Payments)

#### Recommended Indexes

```sql
-- Index 1: Payee Name Full-Text Search
CREATE FULLTEXT INDEX FTI_LOTH_PAYEE_NAME
ON LOTH_CD(PAYEE_NAML, PAYEE_NAMF)
KEY INDEX PK_LOTH;

-- Index 2: Composite - Filer and Filing
CREATE INDEX IDX_LOTH_FILER_FILING
ON LOTH_CD(FILER_ID, FILING_ID)
INCLUDE (AMOUNT);

-- Index 3: Transaction ID
CREATE INDEX IDX_LOTH_TRANSACTION
ON LOTH_CD(BAKREF_TID);
```

---

### Table 9: FILER_FILINGS_CD (Filing Index)

#### Recommended Indexes

```sql
-- Index 1: Composite - Filer and Period
CREATE INDEX IDX_FILER_FILINGS_PERIOD
ON FILER_FILINGS_CD(FILER_ID, PERIOD_ID);

-- Index 2: Form ID
CREATE INDEX IDX_FILER_FILINGS_FORM
ON FILER_FILINGS_CD(FORM_ID);

-- Index 3: Filing ID (for reverse lookups)
CREATE INDEX IDX_FILER_FILINGS_FILING
ON FILER_FILINGS_CD(FILING_ID);
```

---

### Table 10: FILER_ADDRESS_CD

#### Recommended Indexes

```sql
-- Index 1: City Name
CREATE INDEX IDX_FILER_ADDR_CITY
ON FILER_ADDRESS_CD(CITY);

-- Index 2: State
CREATE INDEX IDX_FILER_ADDR_STATE
ON FILER_ADDRESS_CD(ST);

-- Index 3: ZIP Code
CREATE INDEX IDX_FILER_ADDR_ZIP
ON FILER_ADDRESS_CD(ZIP4);

-- Index 4: Composite - Filer and Address ID
CREATE INDEX IDX_FILER_ADDR_FILER
ON FILER_ADDRESS_CD(FILER_ID, ADRID);
```

---

### Supporting Tables (Lower Priority)

#### LATT_CD (Attachments)
```sql
CREATE INDEX IDX_LATT_FILING
ON LATT_CD(FILING_ID, AMEND_ID);

CREATE INDEX IDX_LATT_FORM_TYPE
ON LATT_CD(FORM_TYPE);
```

#### LOBBY_AMENDMENTS_CD
```sql
CREATE INDEX IDX_LOBBY_AMEND_FILING
ON LOBBY_AMENDMENTS_CD(FILING_ID, AMEND_ID);

CREATE INDEX IDX_LOBBY_AMEND_DATE
ON LOBBY_AMENDMENTS_CD(EXEC_DATE);
```

#### NAMES_CD
```sql
CREATE FULLTEXT INDEX FTI_NAMES
ON NAMES_CD(NAML, NAMF)
KEY INDEX PK_NAMES;
```

---

## Implementation Plan

### Phase 1: Assessment (Week 1)

#### Step 1.1: Analyze Current Database
```sql
-- Check current indexes
SELECT 
    t.name AS TableName,
    i.name AS IndexName,
    i.type_desc AS IndexType,
    COL_NAME(ic.object_id, ic.column_id) AS ColumnName
FROM sys.indexes i
JOIN sys.index_columns ic ON i.object_id = ic.object_id AND i.index_id = ic.index_id
JOIN sys.tables t ON i.object_id = t.object_id
WHERE t.name LIKE '%LOBBY%' OR t.name LIKE '%FILER%'
ORDER BY t.name, i.name, ic.key_ordinal;

-- Check table sizes
SELECT 
    t.name AS TableName,
    p.rows AS RowCount,
    SUM(a.total_pages) * 8 / 1024 AS TotalSpaceMB,
    SUM(a.used_pages) * 8 / 1024 AS UsedSpaceMB
FROM sys.tables t
JOIN sys.indexes i ON t.object_id = i.object_id
JOIN sys.partitions p ON i.object_id = p.object_id AND i.index_id = p.index_id
JOIN sys.allocation_units a ON p.partition_id = a.container_id
WHERE t.name LIKE '%LOBBY%' OR t.name LIKE '%FILER%'
GROUP BY t.name, p.rows
ORDER BY p.rows DESC;
```

#### Step 1.2: Benchmark Current Performance
```sql
-- Enable query execution statistics
SET STATISTICS TIME ON;
SET STATISTICS IO ON;

-- Run baseline queries and record results
-- Example:
SELECT COUNT(*) 
FROM CVR_LOBBY_DISCLOSURE_CD 
WHERE UPPER(FIRM_NAME) LIKE '%ALAMEDA%';

-- Record: Execution time, Logical reads, Physical reads
```

#### Step 1.3: Estimate Storage Requirements
```sql
-- Estimate index size
-- Rule of thumb: Each index adds 10-30% of table size
-- Full-text indexes: 20-50% of table size
-- Calculate total additional storage needed
```

---

### Phase 2: Priority 1 Implementation (Weeks 2-3)

#### Implementation Order
1. **Day 1-2:** FILERS_CD (Master table)
2. **Day 3-4:** CVR_LOBBY_DISCLOSURE_CD
3. **Day 5-6:** CVR_REGISTRATION_CD
4. **Day 7-8:** LPAY_CD
5. **Day 9-10:** LEXP_CD

#### Implementation Template

```sql
-- For each table, follow this process:

-- Step 1: Create full-text catalog (once per database)
CREATE FULLTEXT CATALOG CalAccessCatalog AS DEFAULT;

-- Step 2: Create indexes during off-peak hours
-- Schedule: Run between 2 AM - 6 AM

-- Step 3: Create indexes one at a time
-- Example for CVR_LOBBY_DISCLOSURE_CD:

BEGIN TRANSACTION;

-- Create index
CREATE FULLTEXT INDEX FTI_CVR_LOBBY_FILER_NAME
ON CVR_LOBBY_DISCLOSURE_CD(FILER_NAML, FILER_NAMF)
KEY INDEX PK_CVR_LOBBY_DISCLOSURE
WITH CHANGE_TRACKING AUTO;

-- Verify creation
IF EXISTS (
    SELECT 1 FROM sys.fulltext_indexes 
    WHERE object_id = OBJECT_ID('CVR_LOBBY_DISCLOSURE_CD')
)
    COMMIT TRANSACTION;
ELSE
    ROLLBACK TRANSACTION;

-- Step 4: Update statistics
UPDATE STATISTICS CVR_LOBBY_DISCLOSURE_CD;

-- Step 5: Test query performance
SET STATISTICS TIME ON;
SELECT COUNT(*) 
FROM CVR_LOBBY_DISCLOSURE_CD 
WHERE CONTAINS(FILER_NAML, 'ALAMEDA');
-- Compare to baseline
```

---

### Phase 3: Priority 2 Implementation (Week 4)

#### Implementation Schedule
- **Day 1:** LEMP_CD, LCCM_CD
- **Day 2:** LOTH_CD, FILER_FILINGS_CD
- **Day 3:** FILER_ADDRESS_CD
- **Day 4:** Verification and testing
- **Day 5:** Performance tuning

---

### Phase 4: Priority 3 Implementation (Week 5)

#### Implementation Schedule
- **Day 1-2:** Remaining tables
- **Day 3-4:** Full system testing
- **Day 5:** Documentation and handoff

---

### Phase 5: Optimization (Week 6)

#### Query Optimization

**Before Indexing:**
```sql
-- Old query (slow)
SELECT * 
FROM CVR_LOBBY_DISCLOSURE_CD 
WHERE UPPER(FIRM_NAME) LIKE '%ALAMEDA%';
```

**After Indexing:**
```sql
-- New query (fast) - using full-text search
SELECT * 
FROM CVR_LOBBY_DISCLOSURE_CD 
WHERE CONTAINS(FIRM_NAME, 'ALAMEDA');

-- Or for multiple terms:
SELECT * 
FROM CVR_LOBBY_DISCLOSURE_CD 
WHERE CONTAINS(FIRM_NAME, 'ALAMEDA OR "ALAMEDA COUNTY"');

-- For phrase search:
SELECT * 
FROM CVR_LOBBY_DISCLOSURE_CD 
WHERE CONTAINS(FIRM_NAME, '"CITY OF ALAMEDA"');
```

---

## Testing and Validation

### Test Plan

#### Test 1: Functionality Testing
```sql
-- Verify all indexes are created
SELECT 
    OBJECT_NAME(object_id) AS TableName,
    name AS IndexName,
    type_desc AS IndexType
FROM sys.indexes
WHERE OBJECT_NAME(object_id) LIKE '%LOBBY%'
ORDER BY TableName;

-- Verify full-text indexes
SELECT 
    OBJECT_NAME(object_id) AS TableName,
    is_enabled,
    change_tracking_state_desc
FROM sys.fulltext_indexes
WHERE OBJECT_NAME(object_id) LIKE '%LOBBY%';
```

#### Test 2: Performance Testing
```sql
-- Create test script
DECLARE @StartTime DATETIME;
DECLARE @EndTime DATETIME;
DECLARE @Duration INT;

-- Test Query 1: Simple name search
SET @StartTime = GETDATE();
SELECT COUNT(*) FROM CVR_LOBBY_DISCLOSURE_CD 
WHERE CONTAINS(FIRM_NAME, 'ALAMEDA');
SET @EndTime = GETDATE();
SET @Duration = DATEDIFF(MILLISECOND, @StartTime, @EndTime);
PRINT 'Query 1 Duration: ' + CAST(@Duration AS VARCHAR) + ' ms';

-- Test Query 2: Complex join
SET @StartTime = GETDATE();
SELECT f.FILER_NAML, COUNT(cvr.FILING_ID)
FROM FILERS_CD f
JOIN CVR_LOBBY_DISCLOSURE_CD cvr ON f.FILER_ID = cvr.FILER_ID
WHERE CONTAINS(f.FILER_NAML, 'ALAMEDA')
GROUP BY f.FILER_NAML;
SET @EndTime = GETDATE();
SET @Duration = DATEDIFF(MILLISECOND, @StartTime, @EndTime);
PRINT 'Query 2 Duration: ' + CAST(@Duration AS VARCHAR) + ' ms';

-- Continue for all test queries
```

#### Test 3: Load Testing
```sql
-- Run multiple concurrent queries
-- Measure: Response time, CPU usage, Memory usage, Disk I/O
```

---

## Maintenance Plan

### Daily Maintenance

#### Auto-Update Statistics
```sql
-- Enable auto-update statistics
ALTER DATABASE CalAccess 
SET AUTO_UPDATE_STATISTICS ON;

ALTER DATABASE CalAccess 
SET AUTO_UPDATE_STATISTICS_ASYNC ON;
```

### Weekly Maintenance

#### Rebuild Fragmented Indexes
```sql
-- Check index fragmentation
SELECT 
    OBJECT_NAME(ips.object_id) AS TableName,
    i.name AS IndexName,
    ips.avg_fragmentation_in_percent,
    ips.page_count
FROM sys.dm_db_index_physical_stats(
    DB_ID(), NULL, NULL, NULL, 'LIMITED'
) ips
JOIN sys.indexes i ON ips.object_id = i.object_id 
    AND ips.index_id = i.index_id
WHERE ips.avg_fragmentation_in_percent > 10
    AND ips.page_count > 1000
ORDER BY ips.avg_fragmentation_in_percent DESC;

-- Rebuild highly fragmented indexes
ALTER INDEX ALL ON CVR_LOBBY_DISCLOSURE_CD REBUILD 
WITH (ONLINE = ON, MAXDOP = 4);
```

### Monthly Maintenance

#### Full-Text Catalog Reorganization
```sql
-- Reorganize full-text catalogs
ALTER FULLTEXT CATALOG CalAccessCatalog REORGANIZE;

-- Update full-text index
ALTER FULLTEXT INDEX ON CVR_LOBBY_DISCLOSURE_CD 
START FULL POPULATION;
```

#### Statistics Update
```sql
-- Update statistics with full scan
UPDATE STATISTICS CVR_LOBBY_DISCLOSURE_CD WITH FULLSCAN;
UPDATE STATISTICS CVR_REGISTRATION_CD WITH FULLSCAN;
UPDATE STATISTICS FILERS_CD WITH FULLSCAN;
-- Continue for all tables
```

---

## Performance Monitoring

### Key Metrics to Track

#### Query Performance Metrics
```sql
-- Top 10 slowest queries
SELECT TOP 10
    qs.execution_count,
    qs.total_elapsed_time / 1000000.0 AS total_elapsed_time_sec,
    qs.total_elapsed_time / qs.execution_count / 1000000.0 AS avg_elapsed_time_sec,
    SUBSTRING(qt.text, qs.statement_start_offset/2 + 1,
        (CASE WHEN qs.statement_end_offset = -1
            THEN LEN(CONVERT(NVARCHAR(MAX), qt.text)) * 2
            ELSE qs.statement_end_offset
        END - qs.statement_start_offset)/2
    ) AS query_text
FROM sys.dm_exec_query_stats qs
CROSS APPLY sys.dm_exec_sql_text(qs.sql_handle) qt
WHERE qt.text LIKE '%CVR_LOBBY%' OR qt.text LIKE '%FILER%'
ORDER BY qs.total_elapsed_time DESC;
```

#### Index Usage Statistics
```sql
-- Check which indexes are being used
SELECT 
    OBJECT_NAME(s.object_id) AS TableName,
    i.name AS IndexName,
    s.user_seeks,
    s.user_scans,
    s.user_lookups,
    s.user_updates,
    s.last_user_seek,
    s.last_user_scan
FROM sys.dm_db_index_usage_stats s
JOIN sys.indexes i ON s.object_id = i.object_id 
    AND s.index_id = i.index_id
WHERE OBJECT_NAME(s.object_id) LIKE '%LOBBY%'
ORDER BY s.user_seeks + s.user_scans + s.user_lookups DESC;

-- Identify unused indexes
SELECT 
    OBJECT_NAME(i.object_id) AS TableName,
    i.name AS IndexName,
    i.type_desc
FROM sys.indexes i
LEFT JOIN sys.dm_db_index_usage_stats s 
    ON i.object_id = s.object_id AND i.index_id = s.index_id
WHERE OBJECT_NAME(i.object_id) LIKE '%LOBBY%'
    AND s.index_id IS NULL
    AND i.type_desc != 'HEAP';
```

#### Storage Monitoring
```sql
-- Monitor index sizes
SELECT 
    t.name AS TableName,
    i.name AS IndexName,
    SUM(ps.used_page_count) * 8 / 1024 AS IndexSizeMB
FROM sys.dm_db_partition_stats ps
JOIN sys.indexes i ON ps.object_id = i.object_id 
    AND ps.index_id = i.index_id
JOIN sys.tables t ON ps.object_id = t.object_id
WHERE t.name LIKE '%LOBBY%'
GROUP BY t.name, i.name
ORDER BY IndexSizeMB DESC;
```

---

## Rollback Plan

### If Performance Degrades

```sql
-- Disable specific index
ALTER INDEX IDX_CVR_LOBBY_FILER_NAME 
ON CVR_LOBBY_DISCLOSURE_CD DISABLE;

-- Drop problematic index
DROP INDEX IDX_CVR_LOBBY_FILER_NAME 
ON CVR_LOBBY_DISCLOSURE_CD;

-- Drop full-text index
DROP FULLTEXT INDEX ON CVR_LOBBY_DISCLOSURE_CD;
```

### Complete Rollback Script

```sql
-- Drop all custom indexes (keep primary keys)
DECLARE @SQL NVARCHAR(MAX);
DECLARE @TableName NVARCHAR(128);
DECLARE @IndexName NVARCHAR(128);

DECLARE index_cursor CURSOR FOR
SELECT 
    OBJECT_NAME(object_id) AS TableName,
    name AS IndexName
FROM sys.indexes
WHERE OBJECT_NAME(object_id) LIKE '%LOBBY%'
    AND type_desc != 'CLUSTERED'
    AND is_primary_key = 0;

OPEN index_cursor;
FETCH NEXT FROM index_cursor INTO @TableName, @IndexName;

WHILE @@FETCH_STATUS = 0
BEGIN
    SET @SQL = 'DROP INDEX ' + @IndexName + ' ON ' + @TableName;
    PRINT @SQL;
    EXEC sp_executesql @SQL;
    
    FETCH NEXT FROM index_cursor INTO @TableName, @IndexName;
END

CLOSE index_cursor;
DEALLOCATE index_cursor;
```

---

## Success Criteria

### Performance Targets
- [ ] Name-based queries execute in < 5 seconds
- [ ] Complex joins complete in < 15 seconds
- [ ] Full-text searches return results in < 2 seconds
- [ ] Report generation time reduced by 80%

### Quality Targets
- [ ] All indexes created successfully
- [ ] No data integrity issues
- [ ] Query results match pre-index results
- [ ] No increase in failed queries

### Operational Targets
- [ ] Index maintenance automated
- [ ] Monitoring dashboards created
- [ ] Documentation completed
- [ ] Team trained on new query syntax

---

## Training and Documentation

### Team Training Topics

1. **Full-Text Search Syntax**
   - CONTAINS vs LIKE
   - Boolean operators (AND, OR, NOT)
   - Phrase searches
   - Proximity searches

2. **Query Optimization**
   - Using indexed columns in WHERE clauses
   - Avoiding functions on indexed columns
   - Understanding execution plans

3. **Maintenance Procedures**
   - When to rebuild indexes
   - How to check fragmentation
   - Monitoring index usage

### Documentation Deliverables

- [ ] Index inventory spreadsheet
- [ ] Query optimization guide
- [ ] Maintenance runbook
- [ ] Performance baseline report
- [ ] Before/after comparison report

---

## Cost-Benefit Analysis

### Implementation Costs
- **Development Time:** 2-3 weeks (120-180 hours)
- **Testing Time:** 1 week (40 hours)
- **Storage Requirements:** +20-40% of current database size
- **Downtime:** Minimal (indexes created during off-peak hours)

### Benefits
- **Time Savings:** 85-95% reduction in query time
- **User Productivity:** Analysts can run 10x more queries per day
- **System Capacity:** Database can handle more concurrent users
- **Report Generation:** Reports complete in minutes vs hours

### ROI Calculation
```
Annual analyst hours saved: 500 hours
Average hourly cost: $75
Annual cost savings: $37,500

Implementation cost: $15,000
ROI: 150% in year 1
Payback period: 5 months
```

---

## Appendix A: Glossary

**B-Tree Index:** Binary tree index structure for fast data retrieval

**Full-Text Index:** Specialized index for searching text within columns

**Composite Index:** Index on multiple columns

**Filtered Index:** Index on subset of rows meeting specific criteria

**Fragmentation:** Disorder in index pages reducing performance

**Cardinality:** Number of unique values in a column

**Selectivity:** Percentage of rows matching a query condition

---

## Appendix B: SQL Server Specific Commands

### For SQL Server

```sql
-- Enable full-text search (one time)
EXEC sp_fulltext_database 'enable';

-- Check full-text status
SELECT * FROM sys.fulltext_catalogs;

-- Force full-text index update
ALTER FULLTEXT INDEX ON table_name START FULL POPULATION;
```

### For PostgreSQL

```sql
-- Create GIN index for text search
CREATE INDEX idx_name ON table_name 
USING GIN(to_tsvector('english', column_name));

-- Query using text search
SELECT * FROM table_name 
WHERE to_tsvector('english', column_name) @@ to_tsquery('alameda');
```

### For MySQL

```sql
-- Create full-text index
CREATE FULLTEXT INDEX idx_name ON table_name(column_name);

-- Query using full-text
SELECT * FROM table_name 
WHERE MATCH(column_name) AGAINST('alameda' IN BOOLEAN MODE);
```

---

## Appendix C: Performance Benchmarks

### Expected Results

| Query Type | Before Index | After Index | Improvement |
|------------|-------------|-------------|-------------|
| Simple name search | 45 sec | 1.2 sec | 97% |
| Complex join (2 tables) | 120 sec | 5 sec | 96% |
| Aggregate query | 90 sec | 3 sec | 97% |
| Date range filter | 60 sec | 2 sec | 97% |
| Multi-condition WHERE | 180 sec | 8 sec | 96% |

---

## Document Control

**Document Version:** 1.0  
**Last Updated:** October 24, 2025  
**Author:** Database Administrator  
**Reviewed By:** [Pending]  
**Approved By:** [Pending]  
**Next Review Date:** January 24, 2026

---

## Change Log

| Date | Version | Changes | Author |
|------|---------|---------|--------|
| 2025-10-24 | 1.0 | Initial document creation | DBA Team |

