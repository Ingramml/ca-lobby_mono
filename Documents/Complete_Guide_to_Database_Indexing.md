# Complete Guide to Database Indexing: From Fundamentals to Implementation

## Table of Contents
1. [What Are Database Indexes?](#what-are-database-indexes)
2. [Why Indexes Matter](#why-indexes-matter)
3. [How Indexes Work Under the Hood](#how-indexes-work-under-the-hood)
4. [Types of Indexes Explained](#types-of-indexes-explained)
5. [Index Design Principles](#index-design-principles)
6. [Step-by-Step Index Creation](#step-by-step-index-creation)
7. [Understanding Query Execution](#understanding-query-execution)
8. [Common Pitfalls and Solutions](#common-pitfalls-and-solutions)
9. [Hands-On Examples](#hands-on-examples)
10. [Advanced Concepts](#advanced-concepts)

---

## What Are Database Indexes?

### The Book Analogy

Imagine you have a 1,000-page encyclopedia and you need to find all mentions of "Alameda, California."

**WITHOUT an index:**
- You must read every single page from start to finish
- Time required: Hours
- Pages examined: All 1,000 pages

**WITH an index:**
- You look up "Alameda" in the alphabetical index at the back
- The index tells you: "See pages 47, 203, 891"
- You jump directly to those pages
- Time required: Minutes
- Pages examined: Only 3 pages

**This is exactly what a database index does!**

### Technical Definition

A database index is a **separate data structure** that stores:
1. **Key values** (the data you're searching for)
2. **Pointers** (memory addresses pointing to the actual rows)

Think of it as a "fast lookup table" that helps the database find data without scanning every row.

---

## Why Indexes Matter

### The Performance Problem

Let's use real numbers from our CAL-ACCESS database:

```
CVR_LOBBY_DISCLOSURE_CD table:
- Rows: 500,000 records
- Row size: ~2KB per record
- Total size: ~1GB

Query: Find all records where FIRM_NAME contains "ALAMEDA"
```

### Without an Index (Full Table Scan)

```
What the database does:
1. Start at row 1
2. Read FIRM_NAME column
3. Check if it contains "ALAMEDA"
4. Move to row 2
5. Repeat steps 2-4 for ALL 500,000 rows

Time breakdown:
- Disk reads: 500,000 rows × 0.1ms = 50 seconds
- CPU string comparison: 500,000 × 0.05ms = 25 seconds
- Total: ~75 seconds
```

### With an Index

```
What the database does:
1. Look up "ALAMEDA" in the index (binary search)
2. Index returns pointer to 12 matching rows
3. Database jumps directly to those 12 rows
4. Returns results

Time breakdown:
- Index lookup: ~20 binary searches × 0.01ms = 0.2 seconds
- Retrieve 12 rows: 12 × 0.1ms = 1.2 seconds
- Total: ~1.4 seconds

Speed improvement: 75 seconds → 1.4 seconds (98% faster!)
```

### Real-World Impact

```
Scenario: Analyst runs 20 queries per day

Without indexes:
- 20 queries × 75 seconds = 1,500 seconds (25 minutes per day)
- Per year: 100+ hours of waiting

With indexes:
- 20 queries × 1.4 seconds = 28 seconds per day
- Per year: 2 hours of waiting

Time saved: 98+ hours per year per analyst!
```

---

## How Indexes Work Under the Hood

### Understanding Data Structures

#### 1. The Heap (No Index)

When a table has no index, data is stored in a **heap** - an unordered collection:

```
Visual representation of table without index:

Row | FILER_ID | FIRM_NAME              | AMOUNT
----|----------|------------------------|--------
1   | 1234     | ABC Consulting         | 5000
2   | 5678     | Alameda County         | 12000
3   | 9012     | Bay Area Lobbying      | 8000
4   | 3456     | California Strategies  | 15000
... (496,996 more rows)
500000 | 7890  | Alameda City Council   | 9000

To find "ALAMEDA", must check ALL 500,000 rows
```

#### 2. The B-Tree Index

Most databases use a **B-Tree** (Balanced Tree) structure for indexes:

```
B-Tree Structure Visualization:

Level 0 (Root):
                    [M]
                   /   \
Level 1:         [D]    [S]
                / \     / \
Level 2:      [A] [H] [N] [Z]
             /|   |\   |\  |\
Level 3:   (leaf nodes with pointers to actual data)

How it works:
1. Looking for "ALAMEDA"? Start at root [M]
2. "A" comes before "M", go left to [D]
3. "A" comes before "D", go left to [A]
4. Leaf node [A] contains all entries starting with A
5. Find "ALAMEDA" → pointer → jump to actual row
```

### Why B-Trees Are Fast

**Binary Search Math:**
- 500,000 records in heap: Must check up to 500,000 rows
- 500,000 records in B-Tree: log₂(500,000) ≈ 19 comparisons

**The Power of Logarithms:**
```
Records     | Heap Lookups | B-Tree Lookups | Speedup
------------|--------------|----------------|----------
1,000       | 1,000        | 10             | 100x
10,000      | 10,000       | 13             | 769x
100,000     | 100,000      | 17             | 5,882x
1,000,000   | 1,000,000    | 20             | 50,000x
10,000,000  | 10,000,000   | 23             | 434,783x
```

### Index Storage

```
Original Table: CVR_LOBBY_DISCLOSURE_CD (1 GB)

Index: IDX_FIRM_NAME
Structure:
┌─────────────────────────────────────┐
│ Index Entry                         │
├─────────────────────────────────────┤
│ Key: "ALAMEDA COUNTY"               │
│ Pointer: 0x1A2B3C4D (row location)  │
├─────────────────────────────────────┤
│ Key: "ALAMEDA CITY"                 │
│ Pointer: 0x5E6F7A8B (row location)  │
├─────────────────────────────────────┤
│ ... (more entries) ...              │
└─────────────────────────────────────┘

Index size: ~150 MB (15% of table size)
Total storage: 1 GB + 150 MB = 1.15 GB
```

---

## Types of Indexes Explained

### 1. Single-Column Index (Basic)

**What it does:** Indexes one column

**Example:**
```sql
CREATE INDEX IDX_FIRM_NAME 
ON CVR_LOBBY_DISCLOSURE_CD(FIRM_NAME);
```

**How it helps:**
```sql
-- This query is FAST with the index:
SELECT * FROM CVR_LOBBY_DISCLOSURE_CD 
WHERE FIRM_NAME = 'Alameda County';

-- The database uses the index to jump directly to matching rows
```

**Visual:**
```
Index Structure (simplified):
FIRM_NAME          → Row Location
─────────────────────────────────
"ABC Lobbying"     → Row 15234
"Alameda City"     → Row 87912
"Alameda County"   → Row 2341
"Bay Consulting"   → Row 45678
...
```

### 2. Composite Index (Multi-Column)

**What it does:** Indexes multiple columns together

**Example:**
```sql
CREATE INDEX IDX_FILER_DATE 
ON CVR_LOBBY_DISCLOSURE_CD(FILER_ID, FROM_DATE, THRU_DATE);
```

**How it helps:**
```sql
-- These queries use the composite index:

-- ✓ Uses index (searches all 3 columns in order)
SELECT * FROM CVR_LOBBY_DISCLOSURE_CD 
WHERE FILER_ID = 1234 
  AND FROM_DATE = '2024-01-01' 
  AND THRU_DATE = '2024-03-31';

-- ✓ Uses index (searches first 2 columns)
SELECT * FROM CVR_LOBBY_DISCLOSURE_CD 
WHERE FILER_ID = 1234 
  AND FROM_DATE = '2024-01-01';

-- ✓ Uses index (searches first column)
SELECT * FROM CVR_LOBBY_DISCLOSURE_CD 
WHERE FILER_ID = 1234;

-- ✗ CANNOT use index (doesn't start with first column)
SELECT * FROM CVR_LOBBY_DISCLOSURE_CD 
WHERE FROM_DATE = '2024-01-01';
```

**The Phone Book Rule:**

Composite indexes work like a phone book:
- Phone books are sorted by: (LAST_NAME, FIRST_NAME)
- You can find "Smith, John" quickly
- You can find all "Smith" entries quickly
- You CANNOT find all "John" entries quickly (would need full scan)

**Visual:**
```
Composite Index: (FILER_ID, FROM_DATE)
FILER_ID | FROM_DATE  → Row Location
─────────────────────────────────────
1001     | 2024-01-01 → Row 100
1001     | 2024-04-01 → Row 250
1001     | 2024-07-01 → Row 387
1002     | 2024-01-01 → Row 101
1002     | 2024-04-01 → Row 255
...

Sorted first by FILER_ID, then by FROM_DATE within each FILER_ID
```

### 3. Full-Text Index

**What it does:** Optimized for searching words within text

**Why regular indexes don't work for text search:**
```sql
-- This is SLOW even with a regular index:
SELECT * FROM CVR_LOBBY_DISCLOSURE_CD 
WHERE FIRM_NAME LIKE '%ALAMEDA%';

-- Problem: The '%' at the beginning means "match anything before ALAMEDA"
-- Database cannot use index because it doesn't know where to start looking
```

**How full-text indexes work:**

```
Original text in FIRM_NAME:
"Alameda County Supervisors Association"

Full-text index breaks it into tokens:
Token          → Document IDs
────────────────────────────
"alameda"      → [2341, 7829, 45123]
"county"       → [2341, 8912, 34567]
"supervisors"  → [2341, 9876]
"association"  → [2341, 5432, 7890]

Now searching for "alameda" is instant!
```

**Example:**
```sql
-- Create full-text index
CREATE FULLTEXT INDEX FTI_FIRM_NAME
ON CVR_LOBBY_DISCLOSURE_CD(FIRM_NAME)
KEY INDEX PK_CVR_LOBBY_DISCLOSURE;

-- Use it with CONTAINS (fast)
SELECT * FROM CVR_LOBBY_DISCLOSURE_CD 
WHERE CONTAINS(FIRM_NAME, 'ALAMEDA');

-- Multiple words (AND search)
SELECT * FROM CVR_LOBBY_DISCLOSURE_CD 
WHERE CONTAINS(FIRM_NAME, 'ALAMEDA AND COUNTY');

-- Multiple words (OR search)
SELECT * FROM CVR_LOBBY_DISCLOSURE_CD 
WHERE CONTAINS(FIRM_NAME, 'ALAMEDA OR BERKELEY');

-- Phrase search
SELECT * FROM CVR_LOBBY_DISCLOSURE_CD 
WHERE CONTAINS(FIRM_NAME, '"ALAMEDA COUNTY"');
```

**Full-Text vs Regular Index:**
```
Query: Find "ALAMEDA" in 500,000 rows

Regular Index with LIKE:
- Time: 45 seconds (still needs to scan many rows)
- Reason: Cannot use index efficiently with wildcard

Full-Text Index with CONTAINS:
- Time: 1.2 seconds
- Reason: Direct lookup in word index

Speed improvement: 37x faster!
```

### 4. Filtered Index

**What it does:** Indexes only rows that meet specific criteria

**Example:**
```sql
CREATE INDEX IDX_ACTIVE_PAYMENTS 
ON LPAY_CD(FILER_ID, AMOUNT)
WHERE AMOUNT > 0;
```

**Why this helps:**
```
Without filter:
- Index size: 200 MB
- Includes 1,000,000 rows (including 300,000 rows with AMOUNT = 0)

With filter:
- Index size: 140 MB (30% smaller)
- Includes only 700,000 rows where AMOUNT > 0
- Faster to search
- Uses less disk space
- Faster to update
```

**Use cases:**
```sql
-- Good: Index only active records
CREATE INDEX IDX_ACTIVE_FILERS 
ON FILERS_CD(FILER_ID)
WHERE STATUS = 'ACTIVE';

-- Good: Index only recent data
CREATE INDEX IDX_RECENT_FILINGS 
ON CVR_LOBBY_DISCLOSURE_CD(FILING_ID, FROM_DATE)
WHERE FROM_DATE >= '2020-01-01';

-- Good: Index only lobbying firms
CREATE INDEX IDX_FIRMS_ONLY 
ON CVR_REGISTRATION_CD(FILER_ID, FIRM_NAME)
WHERE ENTITY_CD = 'FRM';
```

### 5. Covering Index (Including Columns)

**What it does:** Stores additional columns in the index

**Problem without covering:**
```sql
CREATE INDEX IDX_FILER 
ON LPAY_CD(FILER_ID);

-- Query:
SELECT FILER_ID, AMOUNT, PAYEE_NAML 
FROM LPAY_CD 
WHERE FILER_ID = 1234;

-- What happens:
1. Look up FILER_ID in index → finds 50 matching rows
2. For EACH row, jump to main table to get AMOUNT and PAYEE_NAML
3. 50 random disk seeks (slow!)
```

**Solution with covering index:**
```sql
CREATE INDEX IDX_FILER_COVERING 
ON LPAY_CD(FILER_ID)
INCLUDE (AMOUNT, PAYEE_NAML);

-- Same query:
SELECT FILER_ID, AMOUNT, PAYEE_NAML 
FROM LPAY_CD 
WHERE FILER_ID = 1234;

-- What happens:
1. Look up FILER_ID in index → finds 50 matching rows
2. ALL data (FILER_ID, AMOUNT, PAYEE_NAML) is in the index!
3. No need to access main table
4. Returns results immediately

Speed improvement: 10-50x faster!
```

**Visual:**
```
Regular Index:
FILER_ID → Row Pointer
─────────────────────
1234     → Row 5000
1234     → Row 5001
1234     → Row 5002

(Must read rows 5000, 5001, 5002 from main table)

Covering Index:
FILER_ID | AMOUNT | PAYEE_NAML       → Row Pointer
──────────────────────────────────────────────────
1234     | 5000   | "ABC Company"    → Row 5000
1234     | 12000  | "XYZ Firm"       → Row 5001
1234     | 8000   | "Acme Lobbying"  → Row 5002

(All data is in the index - no need to read main table!)
```

### 6. Unique Index

**What it does:** Ensures no duplicate values

**Example:**
```sql
CREATE UNIQUE INDEX UQ_FILER_EMAIL 
ON FILERS_CD(EMAIL);
```

**How it works:**
```sql
-- First insert succeeds:
INSERT INTO FILERS_CD (FILER_ID, EMAIL) 
VALUES (1001, 'lobbyist@example.com');

-- Second insert with same email FAILS:
INSERT INTO FILERS_CD (FILER_ID, EMAIL) 
VALUES (1002, 'lobbyist@example.com');

-- Error: Violation of UNIQUE KEY constraint
```

**Benefits:**
1. **Data integrity:** Prevents duplicates
2. **Performance:** Unique indexes are slightly faster than non-unique

---

## Index Design Principles

### The Column Selection Criteria

**Good candidates for indexing:**
```
✓ Columns in WHERE clauses
✓ Columns in JOIN conditions
✓ Columns in ORDER BY clauses
✓ Columns in GROUP BY clauses
✓ Columns with high cardinality (many unique values)
✓ Columns frequently searched
```

**Poor candidates for indexing:**
```
✗ Columns rarely searched
✗ Columns with low cardinality (few unique values)
✗ Columns frequently updated
✗ Very small tables (< 1,000 rows)
✗ Columns that are mostly NULL
```

### Understanding Cardinality

**High Cardinality (GOOD for indexing):**
```
Column: FILER_ID
Values: 1, 2, 3, 4, 5, 6, 7, 8, 9, 10 ... (all unique)
Cardinality: 500,000 unique values in 500,000 rows
Selectivity: 500,000 / 500,000 = 100%

Index effectiveness: EXCELLENT
Each lookup returns very few rows
```

**Low Cardinality (BAD for indexing):**
```
Column: ENTITY_CD
Values: 'FRM', 'LEM', 'LCO', 'LBY', 'IND' (only 5 unique values)
Cardinality: 5 unique values in 500,000 rows
Selectivity: 5 / 500,000 = 0.001%

Index effectiveness: POOR
Each lookup returns ~100,000 rows (20% of table)
Database might ignore index and do full scan anyway
```

**Real-world example:**
```sql
-- BAD: Index on low-cardinality column
CREATE INDEX IDX_ENTITY 
ON CVR_LOBBY_DISCLOSURE_CD(ENTITY_CD);

-- Query:
SELECT * FROM CVR_LOBBY_DISCLOSURE_CD 
WHERE ENTITY_CD = 'FRM';

-- Returns: 100,000 rows out of 500,000
-- Database says: "Index won't help, I'll just scan the whole table"

-- BETTER: Composite index with additional columns
CREATE INDEX IDX_ENTITY_FILER 
ON CVR_LOBBY_DISCLOSURE_CD(ENTITY_CD, FILER_ID, FROM_DATE);

-- Query:
SELECT * FROM CVR_LOBBY_DISCLOSURE_CD 
WHERE ENTITY_CD = 'FRM' 
  AND FILER_ID = 1234 
  AND FROM_DATE = '2024-01-01';

-- Returns: 1 row
-- Database says: "Great! Index is very helpful!"
```

### The Column Order Rule (Composite Indexes)

**Rule:** Put most selective columns first

**Example:**
```sql
-- Table with 1,000,000 rows

Column statistics:
- ENTITY_CD: 5 unique values (low selectivity)
- FILER_ID: 50,000 unique values (high selectivity)
- FROM_DATE: 365 unique values (medium selectivity)

-- WRONG order (least selective first):
CREATE INDEX IDX_WRONG 
ON table(ENTITY_CD, FROM_DATE, FILER_ID);

Filtering steps:
1. ENTITY_CD = 'FRM' → 200,000 rows (filtered to 20%)
2. FROM_DATE = '2024-01-01' → 548 rows (filtered to 0.27%)
3. FILER_ID = 1234 → 1 row (filtered to 0.0001%)

-- RIGHT order (most selective first):
CREATE INDEX IDX_RIGHT 
ON table(FILER_ID, FROM_DATE, ENTITY_CD);

Filtering steps:
1. FILER_ID = 1234 → 20 rows (filtered to 0.002%)
2. FROM_DATE = '2024-01-01' → 1 row (filtered to 0.0001%)
3. ENTITY_CD = 'FRM' → 1 row (filtered to 0.0001%)

Result: RIGHT index filters faster because it eliminates most rows earlier
```

**Exception - The Access Pattern Rule:**

Sometimes you should violate the selectivity rule based on how queries are written:

```sql
-- Most common query pattern:
SELECT * FROM table 
WHERE ENTITY_CD = 'FRM' 
  AND FROM_DATE >= '2024-01-01';

-- Less common query:
SELECT * FROM table 
WHERE FILER_ID = 1234;

-- BEST index for your workload:
CREATE INDEX IDX_ACCESS_PATTERN 
ON table(ENTITY_CD, FROM_DATE, FILER_ID);

Reason: Optimizes the most frequent query pattern
```

### The Index Cost-Benefit Analysis

**Costs of indexes:**
1. **Storage space:** Each index adds 10-50% of table size
2. **Write performance:** Every INSERT/UPDATE/DELETE must update all indexes
3. **Maintenance overhead:** Indexes need rebuilding when fragmented

**Example:**
```
Table: LPAY_CD (1 GB, 1,000,000 rows)

No indexes:
- Storage: 1 GB
- INSERT time: 10ms per row
- UPDATE time: 15ms per row
- SELECT time: 45 seconds (full scan)

With 5 indexes:
- Storage: 1.5 GB (50% overhead)
- INSERT time: 25ms per row (2.5x slower)
- UPDATE time: 40ms per row (2.7x slower)
- SELECT time: 1.2 seconds (37x faster)

Trade-off: Slower writes for MUCH faster reads
```

**When to add an index:**
- Table is read 10x more than written
- Query runs frequently (daily or more)
- Query takes > 5 seconds
- Users complain about performance

**When NOT to add an index:**
- Table is written to constantly (high-volume transaction table)
- Query runs rarely (monthly reports)
- Table is very small (< 1,000 rows)
- Column has very low cardinality

---

## Step-by-Step Index Creation

### Phase 1: Analysis

#### Step 1: Identify Slow Queries

```sql
-- Find slowest queries in your database
-- (Example for SQL Server)
SELECT TOP 10
    total_elapsed_time / 1000000.0 AS total_elapsed_time_seconds,
    total_elapsed_time / execution_count / 1000000.0 AS avg_elapsed_time_seconds,
    execution_count,
    SUBSTRING(text, 1, 500) AS query_text
FROM sys.dm_exec_query_stats
CROSS APPLY sys.dm_exec_sql_text(sql_handle)
ORDER BY total_elapsed_time DESC;
```

#### Step 2: Analyze Query Patterns

```sql
-- Look at the slow query:
SELECT 
    cvr.FILING_ID,
    cvr.FILER_ID,
    cvr.FIRM_NAME,
    cvr.FROM_DATE,
    cvr.THRU_DATE
FROM CVR_LOBBY_DISCLOSURE_CD cvr
WHERE UPPER(cvr.FIRM_NAME) LIKE '%ALAMEDA%'
  AND cvr.FROM_DATE >= '2024-01-01'
ORDER BY cvr.FROM_DATE DESC;

-- Questions to ask:
-- 1. Which columns are in WHERE clause? → FIRM_NAME, FROM_DATE
-- 2. Which columns are in ORDER BY? → FROM_DATE
-- 3. Which columns are in SELECT? → FILING_ID, FILER_ID, FIRM_NAME, FROM_DATE, THRU_DATE
-- 4. How many rows does it return? → Let's say 50 rows
-- 5. How long does it take? → 45 seconds (too slow!)
```

#### Step 3: Check Current Indexes

```sql
-- List existing indexes on the table
SELECT 
    i.name AS index_name,
    COL_NAME(ic.object_id, ic.column_id) AS column_name,
    i.type_desc AS index_type
FROM sys.indexes i
JOIN sys.index_columns ic ON i.object_id = ic.object_id 
    AND i.index_id = ic.index_id
WHERE i.object_id = OBJECT_ID('CVR_LOBBY_DISCLOSURE_CD')
ORDER BY i.name, ic.key_ordinal;
```

#### Step 4: Review Execution Plan

```sql
-- Turn on execution plan
SET SHOWPLAN_TEXT ON;

-- Run your query
SELECT * FROM CVR_LOBBY_DISCLOSURE_CD 
WHERE UPPER(FIRM_NAME) LIKE '%ALAMEDA%';

-- Look for:
-- - "Table Scan" or "Clustered Index Scan" = BAD (scanning entire table)
-- - "Index Seek" = GOOD (using index efficiently)
-- - "Key Lookup" = OK but could be better (needs covering index)
```

### Phase 2: Design

#### Step 5: Design the Index

Based on our analysis:
```sql
-- Problem: Text search in FIRM_NAME

-- Solution Option 1: Full-text index (best for text search)
CREATE FULLTEXT INDEX FTI_FIRM_NAME
ON CVR_LOBBY_DISCLOSURE_CD(FIRM_NAME)
KEY INDEX PK_CVR_LOBBY_DISCLOSURE;

-- Solution Option 2: Composite index for date filtering
CREATE INDEX IDX_DATE_FILER
ON CVR_LOBBY_DISCLOSURE_CD(FROM_DATE, FILER_ID)
INCLUDE (FIRM_NAME, THRU_DATE);

-- We'll create BOTH to optimize different query patterns
```

### Phase 3: Implementation

#### Step 6: Test in Development Environment

```sql
-- NEVER create indexes directly in production!
-- Always test first

-- 1. Restore production backup to test environment
-- 2. Create index in test
CREATE FULLTEXT INDEX FTI_FIRM_NAME
ON CVR_LOBBY_DISCLOSURE_CD(FIRM_NAME)
KEY INDEX PK_CVR_LOBBY_DISCLOSURE;

-- 3. Test the query
SET STATISTICS TIME ON;
SET STATISTICS IO ON;

SELECT * FROM CVR_LOBBY_DISCLOSURE_CD 
WHERE CONTAINS(FIRM_NAME, 'ALAMEDA');

-- 4. Record results:
-- - Execution time: 1.2 seconds (was 45 seconds)
-- - Logical reads: 150 (was 125,000)
-- - CPU time: 200ms (was 8,500ms)
```

#### Step 7: Estimate Impact

```sql
-- Check index size
SELECT 
    i.name AS index_name,
    SUM(ps.used_page_count) * 8 / 1024 AS index_size_mb
FROM sys.dm_db_partition_stats ps
JOIN sys.indexes i ON ps.object_id = i.object_id 
    AND ps.index_id = i.index_id
WHERE i.object_id = OBJECT_ID('CVR_LOBBY_DISCLOSURE_CD')
GROUP BY i.name;

-- Estimate maintenance impact
-- Run test INSERTs and UPDATEs to measure overhead
```

#### Step 8: Create in Production

```sql
-- Schedule during off-peak hours (2 AM - 6 AM)

-- Start transaction (for safety)
BEGIN TRANSACTION;

-- Create the index
CREATE FULLTEXT INDEX FTI_FIRM_NAME
ON CVR_LOBBY_DISCLOSURE_CD(FIRM_NAME)
KEY INDEX PK_CVR_LOBBY_DISCLOSURE
WITH (
    CHANGE_TRACKING = AUTO,
    STOPLIST = SYSTEM
);

-- Verify it was created
IF EXISTS (
    SELECT 1 FROM sys.fulltext_indexes 
    WHERE object_id = OBJECT_ID('CVR_LOBBY_DISCLOSURE_CD')
)
    PRINT 'Index created successfully';
ELSE
    PRINT 'Index creation failed';

-- Commit if successful
COMMIT TRANSACTION;
```

### Phase 4: Validation

#### Step 9: Verify Performance

```sql
-- Test the query again in production
SET STATISTICS TIME ON;
SET STATISTICS IO ON;

SELECT * FROM CVR_LOBBY_DISCLOSURE_CD 
WHERE CONTAINS(FIRM_NAME, 'ALAMEDA');

-- Compare to baseline:
-- Before: 45 seconds, 125,000 logical reads
-- After: 1.2 seconds, 150 logical reads
-- Improvement: 97% faster, 99.9% fewer reads
```

#### Step 10: Monitor Usage

```sql
-- Check if index is being used
SELECT 
    OBJECT_NAME(s.object_id) AS table_name,
    i.name AS index_name,
    s.user_seeks,
    s.user_scans,
    s.user_lookups,
    s.last_user_seek
FROM sys.dm_db_index_usage_stats s
JOIN sys.indexes i ON s.object_id = i.object_id 
    AND s.index_id = i.index_id
WHERE OBJECT_NAME(s.object_id) = 'CVR_LOBBY_DISCLOSURE_CD'
ORDER BY s.user_seeks + s.user_scans + s.user_lookups DESC;
```

---

## Understanding Query Execution

### How the Database Chooses to Use (or Not Use) an Index

#### The Query Optimizer

Every database has a **query optimizer** - a smart component that:
1. Looks at your query
2. Checks available indexes
3. Estimates costs of different execution strategies
4. Chooses the fastest plan

**Example:**

```sql
-- Your query:
SELECT * FROM CVR_LOBBY_DISCLOSURE_CD 
WHERE FIRM_NAME = 'Alameda County';

-- Optimizer considers:

-- Option 1: Full Table Scan
Cost estimate:
- Read all 500,000 rows
- Check each FIRM_NAME
- Cost: 500,000 row reads = 50,000 cost units

-- Option 2: Use Index on FIRM_NAME
Cost estimate:
- Look up 'Alameda County' in index: 20 comparisons
- Find 5 matching rows
- Read those 5 rows from table
- Cost: 20 + 5 = 25 cost units

-- Optimizer chooses: Option 2 (200x cheaper!)
```

### Reading an Execution Plan

```sql
-- Enable execution plan
SET SHOWPLAN_TEXT ON;

SELECT * FROM CVR_LOBBY_DISCLOSURE_CD 
WHERE FIRM_NAME = 'Alameda County';

-- Sample execution plan output:
```

```
Execution Plan:
|--Nested Loops (Inner Join)
   |--Index Seek (OBJECT: FTI_FIRM_NAME)
      Seek Keys: FIRM_NAME = 'Alameda County'
      Estimated Rows: 5
      Cost: 0.003 (0.1%)
   |--RID Lookup (OBJECT: CVR_LOBBY_DISCLOSURE_CD)
      Estimated Rows: 5
      Cost: 2.5 (99.9%)

Total Cost: 2.503
Estimated Execution Time: 0.05 seconds
```

**Reading the plan:**
1. **Index Seek** = GOOD! Using the index
2. **0.003 cost** = Very cheap to find rows in index
3. **RID Lookup** = Going to table to get full row data
4. **2.5 cost** = More expensive to fetch actual rows
5. **Total 2.503** = Much better than 50,000 for full scan!

### When the Database Ignores Your Index

**Reason 1: Function on indexed column**

```sql
-- BAD: Function prevents index use
SELECT * FROM CVR_LOBBY_DISCLOSURE_CD 
WHERE UPPER(FIRM_NAME) = 'ALAMEDA COUNTY';

-- GOOD: No function, index can be used
SELECT * FROM CVR_LOBBY_DISCLOSURE_CD 
WHERE FIRM_NAME = 'Alameda County';

-- OR create computed column with index:
ALTER TABLE CVR_LOBBY_DISCLOSURE_CD 
ADD FIRM_NAME_UPPER AS UPPER(FIRM_NAME);

CREATE INDEX IDX_FIRM_NAME_UPPER 
ON CVR_LOBBY_DISCLOSURE_CD(FIRM_NAME_UPPER);
```

**Reason 2: Leading wildcard in LIKE**

```sql
-- BAD: Cannot use regular index
SELECT * FROM CVR_LOBBY_DISCLOSURE_CD 
WHERE FIRM_NAME LIKE '%ALAMEDA%';

-- GOOD: Can use regular index
SELECT * FROM CVR_LOBBY_DISCLOSURE_CD 
WHERE FIRM_NAME LIKE 'ALAMEDA%';

-- BEST: Use full-text index for any-position search
SELECT * FROM CVR_LOBBY_DISCLOSURE_CD 
WHERE CONTAINS(FIRM_NAME, 'ALAMEDA');
```

**Reason 3: Too many matching rows**

```sql
-- Query would return 60% of table rows
SELECT * FROM CVR_LOBBY_DISCLOSURE_CD 
WHERE ENTITY_CD IN ('FRM', 'LEM', 'LCO');

-- Optimizer says:
-- "Using the index will require reading index + looking up 300,000 rows
--  It's faster to just scan the whole table once"
-- Result: Index is ignored, full table scan performed
```

**Reason 4: Outdated statistics**

```sql
-- Statistics tell optimizer about data distribution
-- If statistics are old, optimizer makes bad choices

-- Fix: Update statistics
UPDATE STATISTICS CVR_LOBBY_DISCLOSURE_CD;

-- Or rebuild index (which updates statistics)
ALTER INDEX FTI_FIRM_NAME 
ON CVR_LOBBY_DISCLOSURE_CD REBUILD;
```

---

## Common Pitfalls and Solutions

### Pitfall 1: Over-Indexing

**Problem:**
```sql
-- Developer creates an index for EVERY query
CREATE INDEX IDX1 ON table(col1);
CREATE INDEX IDX2 ON table(col2);
CREATE INDEX IDX3 ON table(col3);
CREATE INDEX IDX4 ON table(col1, col2);
CREATE INDEX IDX5 ON table(col1, col3);
CREATE INDEX IDX6 ON table(col2, col3);
CREATE INDEX IDX7 ON table(col1, col2, col3);

-- Result:
-- - Storage: 2x table size just for indexes
-- - INSERT performance: 8x slower (must update 7 indexes)
-- - Maintenance: Hours of index rebuilds nightly
```

**Solution:**
```sql
-- Create only essential indexes
-- One composite index often serves multiple queries

CREATE INDEX IDX_MAIN ON table(col1, col2, col3);

-- This ONE index can serve:
-- WHERE col1 = x
-- WHERE col1 = x AND col2 = y
-- WHERE col1 = x AND col2 = y AND col3 = z
```

### Pitfall 2: Index Fragmentation

**What is fragmentation?**

```
Fresh index (well-organized):
Page 1: [A B C D E F]
Page 2: [G H I J K L]
Page 3: [M N O P Q R]
→ Reads: 3 pages = 3 disk operations

After many INSERTs/DELETEs (fragmented):
Page 1: [A _ C _ E F]
Page 5: [B]
Page 3: [_ H I _ K L]
Page 8: [G]
Page 2: [M N _ P _ _]
Page 7: [O]
Page 9: [Q R]
→ Reads: 7 pages = 7 disk operations (2.3x slower!)
```

**How it happens:**
1. Insert "B" between "A" and "C"
2. Page is full, so "B" goes to a new page
3. Over time, data spreads across many pages
4. More pages to read = slower queries

**Solution:**
```sql
-- Check fragmentation
SELECT 
    OBJECT_NAME(object_id) AS table_name,
    index_id,
    avg_fragmentation_in_percent,
    page_count
FROM sys.dm_db_index_physical_stats(
    DB_ID(), 
    OBJECT_ID('CVR_LOBBY_DISCLOSURE_CD'),
    NULL, NULL, 'LIMITED'
);

-- If fragmentation > 30% and page_count > 1000:
ALTER INDEX IDX_FIRM_NAME 
ON CVR_LOBBY_DISCLOSURE_CD REBUILD;

-- Schedule weekly:
-- - Reorganize if fragmentation 10-30%
-- - Rebuild if fragmentation > 30%
```

### Pitfall 3: Missing Statistics

**Problem:**
```sql
-- Optimizer doesn't know data distribution
-- Makes poor decisions about using indexes

-- Example: Optimizer thinks query returns 100 rows
-- Actually returns 500,000 rows (whole table)
-- Chooses index when full scan would be faster
-- Result: Query is 10x slower than necessary
```

**Solution:**
```sql
-- Update statistics regularly
UPDATE STATISTICS CVR_LOBBY_DISCLOSURE_CD WITH FULLSCAN;

-- Enable auto-update (recommended)
ALTER DATABASE YourDB 
SET AUTO_UPDATE_STATISTICS ON;

-- Check statistics last updated
DBCC SHOW_STATISTICS ('CVR_LOBBY_DISCLOSURE_CD', 'IDX_FIRM_NAME');
```

### Pitfall 4: Wrong Index Type

**Problem:**
```sql
-- Using regular B-Tree index for text search
CREATE INDEX IDX_FIRM_NAME 
ON CVR_LOBBY_DISCLOSURE_CD(FIRM_NAME);

-- Query:
SELECT * FROM CVR_LOBBY_DISCLOSURE_CD 
WHERE FIRM_NAME LIKE '%ALAMEDA%';

-- Result: Still slow! (Index cannot be used efficiently)
```

**Solution:**
```sql
-- Use full-text index for text search
CREATE FULLTEXT INDEX FTI_FIRM_NAME
ON CVR_LOBBY_DISCLOSURE_CD(FIRM_NAME)
KEY INDEX PK_CVR_LOBBY_DISCLOSURE;

-- Query:
SELECT * FROM CVR_LOBBY_DISCLOSURE_CD 
WHERE CONTAINS(FIRM_NAME, 'ALAMEDA');

-- Result: Fast!
```

---

## Hands-On Examples

### Example 1: Simple Index Creation

**Scenario:** Find all filings for a specific filer

```sql
-- Current slow query (no index):
SELECT * FROM CVR_LOBBY_DISCLOSURE_CD 
WHERE FILER_ID = 1234;

-- Execution time: 35 seconds (full table scan)

-- Check current indexes:
EXEC sp_helpindex 'CVR_LOBBY_DISCLOSURE_CD';

-- Result: No index on FILER_ID

-- Create index:
CREATE INDEX IDX_FILER_ID 
ON CVR_LOBBY_DISCLOSURE_CD(FILER_ID);

-- Monitor creation (takes a few minutes):
SELECT 
    session_id,
    command,
    percent_complete,
    estimated_completion_time / 1000 / 60 AS estimated_minutes_left
FROM sys.dm_exec_requests
WHERE command LIKE '%INDEX%';

-- After index is created, test query:
SELECT * FROM CVR_LOBBY_DISCLOSURE_CD 
WHERE FILER_ID = 1234;

-- Execution time: 0.8 seconds (index seek)
-- Improvement: 43x faster!
```

### Example 2: Composite Index

**Scenario:** Find filings for a filer within a date range

```sql
-- Query pattern:
SELECT * FROM CVR_LOBBY_DISCLOSURE_CD 
WHERE FILER_ID = 1234 
  AND FROM_DATE >= '2024-01-01'
  AND THRU_DATE <= '2025-12-31';

-- Step 1: Analyze query
-- - Filter columns: FILER_ID (high selectivity), FROM_DATE, THRU_DATE
-- - Order: FILER_ID first (most selective), then dates

-- Step 2: Create composite index
CREATE INDEX IDX_FILER_DATE_RANGE 
ON CVR_LOBBY_DISCLOSURE_CD(FILER_ID, FROM_DATE, THRU_DATE);

-- Step 3: Test query
SET STATISTICS IO ON;
SET STATISTICS TIME ON;

SELECT * FROM CVR_LOBBY_DISCLOSURE_CD 
WHERE FILER_ID = 1234 
  AND FROM_DATE >= '2024-01-01'
  AND THRU_DATE <= '2025-12-31';

-- Results:
-- Before: 
--   CPU time: 8,200 ms
--   Logical reads: 125,000
--   Time: 45 seconds

-- After:
--   CPU time: 150 ms
--   Logical reads: 45
--   Time: 0.9 seconds

-- Improvement: 50x faster!
```

### Example 3: Full-Text Index

**Scenario:** Search for organizations containing specific words

```sql
-- Step 1: Enable full-text search on database
EXEC sp_fulltext_database 'enable';

-- Step 2: Create full-text catalog
CREATE FULLTEXT CATALOG ftCatalog AS DEFAULT;

-- Step 3: Create full-text index
CREATE FULLTEXT INDEX ON CVR_LOBBY_DISCLOSURE_CD(FIRM_NAME)
KEY INDEX PK_CVR_LOBBY_DISCLOSURE
WITH CHANGE_TRACKING AUTO;

-- Step 4: Wait for population (check status)
SELECT 
    OBJECT_NAME(object_id) AS table_name,
    * 
FROM sys.fulltext_indexes;

-- Step 5: Test queries

-- Query 1: Simple word search
SELECT * FROM CVR_LOBBY_DISCLOSURE_CD 
WHERE CONTAINS(FIRM_NAME, 'ALAMEDA');
-- Time: 1.1 seconds

-- Query 2: Multiple words (AND)
SELECT * FROM CVR_LOBBY_DISCLOSURE_CD 
WHERE CONTAINS(FIRM_NAME, 'ALAMEDA AND COUNTY');
-- Time: 1.3 seconds

-- Query 3: Multiple words (OR)
SELECT * FROM CVR_LOBBY_DISCLOSURE_CD 
WHERE CONTAINS(FIRM_NAME, 'ALAMEDA OR BERKELEY OR OAKLAND');
-- Time: 1.8 seconds

-- Query 4: Phrase search
SELECT * FROM CVR_LOBBY_DISCLOSURE_CD 
WHERE CONTAINS(FIRM_NAME, '"ALAMEDA COUNTY"');
-- Time: 0.9 seconds

-- Query 5: Proximity search (words near each other)
SELECT * FROM CVR_LOBBY_DISCLOSURE_CD 
WHERE CONTAINS(FIRM_NAME, 'NEAR((ALAMEDA, CITY), 2)');
-- Time: 1.2 seconds
```

### Example 4: Covering Index

**Scenario:** Dashboard query that runs 1,000 times per day

```sql
-- Frequently run query:
SELECT 
    FILER_ID,
    FIRM_NAME,
    FROM_DATE,
    THRU_DATE,
    ENTITY_CD
FROM CVR_LOBBY_DISCLOSURE_CD 
WHERE FILER_ID IN (1234, 5678, 9012)
ORDER BY FROM_DATE DESC;

-- Step 1: Create base index
CREATE INDEX IDX_FILER_DATE 
ON CVR_LOBBY_DISCLOSURE_CD(FILER_ID, FROM_DATE DESC);

-- Test:
-- Time: 5.2 seconds
-- Problem: Must look up FIRM_NAME, THRU_DATE, ENTITY_CD from main table

-- Step 2: Add covering columns
DROP INDEX IDX_FILER_DATE ON CVR_LOBBY_DISCLOSURE_CD;

CREATE INDEX IDX_FILER_DATE_COVERING 
ON CVR_LOBBY_DISCLOSURE_CD(FILER_ID, FROM_DATE DESC)
INCLUDE (FIRM_NAME, THRU_DATE, ENTITY_CD);

-- Test:
-- Time: 0.4 seconds
-- Improvement: 13x faster!
-- Reason: All data in index, no table lookups needed

-- Verify it's covering:
SET SHOWPLAN_TEXT ON;
-- Look for "Index Seek" with no "RID Lookup" or "Key Lookup"
```

### Example 5: Filtered Index

**Scenario:** Most queries only care about recent data

```sql
-- 90% of queries filter on recent data:
SELECT * FROM CVR_LOBBY_DISCLOSURE_CD 
WHERE FROM_DATE >= '2020-01-01'
  AND FILER_ID = 1234;

-- Step 1: Create filtered index (only recent data)
CREATE INDEX IDX_RECENT_FILINGS 
ON CVR_LOBBY_DISCLOSURE_CD(FILER_ID, FROM_DATE)
INCLUDE (FIRM_NAME, ENTITY_CD)
WHERE FROM_DATE >= '2020-01-01';

-- Benefits:
-- - Index size: 80 MB (vs 200 MB for unfiltered)
-- - Maintenance: Faster (smaller index)
-- - Query speed: Same or better

-- Test query:
SELECT * FROM CVR_LOBBY_DISCLOSURE_CD 
WHERE FROM_DATE >= '2020-01-01'
  AND FILER_ID = 1234;

-- Time: 0.6 seconds (was 12 seconds)

-- Note: Old data queries still work, just use different index or table scan
SELECT * FROM CVR_LOBBY_DISCLOSURE_CD 
WHERE FROM_DATE >= '2015-01-01'
  AND FILER_ID = 1234;
-- (This query won't use filtered index, which is fine since it's rare)
```

---

## Advanced Concepts

### Indexed Views (Materialized Views)

**What it is:** A view with a clustered index that stores actual data

```sql
-- Problem: Complex aggregation query runs daily
SELECT 
    FILER_ID,
    YEAR(FROM_DATE) AS YEAR,
    COUNT(*) AS filing_count,
    SUM(AMOUNT) AS total_amount
FROM CVR_LOBBY_DISCLOSURE_CD cvr
JOIN LPAY_CD lp ON cvr.FILING_ID = lp.FILING_ID
GROUP BY FILER_ID, YEAR(FROM_DATE);

-- Execution time: 5 minutes

-- Solution: Create indexed view
CREATE VIEW vw_YearlyFilingSummary
WITH SCHEMABINDING
AS
SELECT 
    cvr.FILER_ID,
    YEAR(cvr.FROM_DATE) AS YEAR,
    COUNT_BIG(*) AS filing_count,
    SUM(lp.AMOUNT) AS total_amount
FROM dbo.CVR_LOBBY_DISCLOSURE_CD cvr
JOIN dbo.LPAY_CD lp ON cvr.FILING_ID = lp.FILING_ID
GROUP BY cvr.FILER_ID, YEAR(cvr.FROM_DATE);

-- Create clustered index on view (this "materializes" it)
CREATE UNIQUE CLUSTERED INDEX IX_vw_YearlyFilingSummary
ON vw_YearlyFilingSummary(FILER_ID, YEAR);

-- Now query the view:
SELECT * FROM vw_YearlyFilingSummary 
WHERE FILER_ID = 1234;

-- Execution time: 0.1 seconds!
-- Data is pre-aggregated and indexed
```

### Columnstore Indexes

**What it is:** Stores data by column instead of by row (for analytics)

```sql
-- Traditional row store:
Row 1: [1234, 'ABC Firm', '2024-01-01', 5000]
Row 2: [5678, 'XYZ Corp', '2024-01-02', 12000]
Row 3: [9012, 'QRS Inc', '2024-01-03', 8000]
-- Good for: SELECT * queries, transactional workload

-- Columnstore:
Column FILER_ID: [1234, 5678, 9012, ...]
Column FIRM_NAME: ['ABC Firm', 'XYZ Corp', 'QRS Inc', ...]
Column FROM_DATE: ['2024-01-01', '2024-01-02', '2024-01-03', ...]
Column AMOUNT: [5000, 12000, 8000, ...]
-- Good for: Aggregations, analytics, data warehouse queries

-- Create columnstore index:
CREATE COLUMNSTORE INDEX CCI_CVR_LOBBY
ON CVR_LOBBY_DISCLOSURE_CD(FILER_ID, FIRM_NAME, FROM_DATE, AMOUNT);

-- Query that benefits:
SELECT 
    YEAR(FROM_DATE) AS year,
    COUNT(*) AS filings,
    AVG(AMOUNT) AS avg_amount
FROM CVR_LOBBY_DISCLOSURE_CD
GROUP BY YEAR(FROM_DATE);

-- Before: 45 seconds
-- After: 2 seconds (22x faster)
-- Bonus: 70% compression (saves storage)
```

### Partitioned Indexes

**What it is:** Splits large table/index into smaller pieces

```sql
-- Problem: Table has 10 million rows spanning 10 years
-- Maintenance is slow, queries are slow

-- Solution: Partition by year
-- Step 1: Create partition function
CREATE PARTITION FUNCTION pfYears(DATE)
AS RANGE RIGHT FOR VALUES 
('2020-01-01', '2021-01-01', '2022-01-01', '2023-01-01', '2024-01-01', '2025-01-01');

-- Step 2: Create partition scheme
CREATE PARTITION SCHEME psYears
AS PARTITION pfYears
ALL TO ([PRIMARY]);

-- Step 3: Create partitioned table/index
CREATE INDEX IDX_DATE_PARTITIONED
ON CVR_LOBBY_DISCLOSURE_CD(FROM_DATE)
ON psYears(FROM_DATE);

-- Benefits:
-- - Query for 2024 only scans 2024 partition
-- - Can rebuild one partition at a time
-- - Can archive old partitions easily

-- Query automatically uses partition:
SELECT * FROM CVR_LOBBY_DISCLOSURE_CD 
WHERE FROM_DATE >= '2024-01-01' 
  AND FROM_DATE < '2025-01-01';
-- Only scans 2024 partition!
```

---

## Summary: The Index Design Checklist

### Before Creating an Index

- [ ] Identify slow query (execution time > 5 seconds)
- [ ] Check if index already exists
- [ ] Verify table is large enough (> 10,000 rows)
- [ ] Confirm query runs frequently (daily or more)
- [ ] Analyze column selectivity (high cardinality is better)
- [ ] Check table write volume (high writes = indexes more costly)
- [ ] Estimate index size and storage impact

### Choosing Index Type

- [ ] **B-Tree Index:** For exact matches, ranges, sorting
- [ ] **Full-Text Index:** For text searching with wildcards
- [ ] **Composite Index:** For multi-column filtering
- [ ] **Covering Index:** For frequently selected columns
- [ ] **Filtered Index:** For subset of data (e.g., recent records)
- [ ] **Unique Index:** For enforcing uniqueness

### Index Design Decisions

- [ ] Determine column order (most selective first)
- [ ] Decide which columns to INCLUDE (covering)
- [ ] Consider filtered WHERE clause (for partial index)
- [ ] Plan for multiple query patterns (may need multiple indexes)

### Implementation

- [ ] Test in development environment first
- [ ] Create during off-peak hours
- [ ] Monitor creation progress
- [ ] Verify index was created successfully
- [ ] Update statistics after creation
- [ ] Test query performance improvement

### Ongoing Maintenance

- [ ] Monitor index usage (is it being used?)
- [ ] Check for fragmentation weekly
- [ ] Rebuild if fragmentation > 30%
- [ ] Update statistics monthly
- [ ] Review and remove unused indexes quarterly
- [ ] Adjust based on changing query patterns

---

## Final Thoughts

**Key Takeaways:**

1. **Indexes are not magic** - They trade storage and write performance for read performance
2. **Choose wisely** - Too many indexes can hurt performance
3. **Right tool for the job** - Different index types for different query patterns
4. **Test everything** - Never create indexes directly in production
5. **Monitor and maintain** - Indexes need regular care to stay effective

**Common Mistakes to Avoid:**

- Creating indexes without measuring performance
- Using functions on indexed columns (breaks index usage)
- Ignoring index maintenance (fragmentation)
- Over-indexing (too many indexes)
- Wrong column order in composite indexes
- Using LIKE with leading wildcard instead of full-text

**When Indexes Help Most:**

- Large tables (> 100,000 rows)
- Frequently run queries
- Complex joins
- Aggregations and grouping
- Sorting large result sets
- Text searching

**When Indexes Don't Help:**

- Very small tables (< 1,000 rows)
- Queries returning most of the table
- Columns with low cardinality
- Tables with high write volume and few reads
- Ad-hoc queries that never repeat

---

**You're now equipped to design, implement, and maintain database indexes effectively!**

Remember: The best way to learn is by doing. Start with one slow query, create an index, measure the improvement, and build from there.

---

**Document Version:** 1.0 - Educational Guide  
**Last Updated:** October 24, 2025  
**Intended Audience:** Database learners, analysts, junior DBAs  
**Prerequisites:** Basic SQL knowledge  
**Next Steps:** Practice on test data, read execution plans, experiment!
