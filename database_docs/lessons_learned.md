# Cal-ACCESS Database: Lessons Learned

> **Source**: Expert analysis of Cal-ACCESS lobbying database schema documentation (RTF documents produced by LLM analysis)
>
> **Date**: November 2025
>
> **Purpose**: Document critical insights, patterns, and caveats for working with the California Automated Lobbying and Campaign Contribution & Expenditure Search System (Cal-ACCESS) database

---

## Table of Contents

1. [System Architecture](#1-system-architecture-insights)
2. [Core Data Model Pattern](#2-core-data-model-pattern)
3. [Entity Code System](#3-entity-code-system)
4. [Form Type Structure](#4-form-type-structure)
5. [Schedule Table Purposes](#5-schedule-table-purposes)
6. [Amendment Tracking System](#6-amendment-tracking-system)
7. [Historical Data Complexity](#7-historical-data-complexity)
8. [Materialized Views for Performance](#8-materialized-views-for-performance)
9. [Supporting Infrastructure](#9-supporting-infrastructure)
10. [Data Quality Caveats](#10-data-quality-caveats)
11. [Index Types and Performance](#11-index-types-and-performance)
12. [Date Field Confusion](#12-date-field-confusion)
13. [Payment Flow Logic](#13-payment-flow-logic)
14. [Database Conceptual Model](#14-database-conceptual-model)
15. [Critical Recommendations](#15-critical-recommendations)

---

## 1. System Architecture Insights

### Three-Tier Subsystem Design

The Cal-ACCESS system is designed around three primary subsystems that interact with the central database:

| Subsystem | Purpose | Key Characteristics |
|-----------|---------|---------------------|
| **EFS** (Electronic Filing Subsystem) | Accepts and validates electronic filings | Submitted by filers (often via vendors) |
| **AMS** (Agency Management Subsystem) | PRD business processes | Tables prefixed with `AMS_` (e.g., `AMS_PROCESSING_STATUS`, `AMS_SYSTEM_PARMS`) |
| **Disclosure Subsystem** | Public access to accepted filings | Internet-facing public disclosure |

### Key Architectural Insight

**The database was designed in 2002** (Model_1, February 21, 2002) using **Oracle database technology**, which explains:
- Older naming conventions
- Use of Oracle-specific features (materialized views, cluster indexes)
- Potential technical debt accumulated over 20+ years
- Design patterns common to early 2000s database architecture

---

## 2. Core Data Model Pattern

### Parent-Child Hierarchy

Everything in the Cal-ACCESS database follows a strict hierarchical pattern:

```
FILERS_CD (Master Registry)
    └── FILER_ID ← THE PRIMARY KEY
         │
         ├──→ FILER_FILINGS_CD (Index/Junction Table)
         │         └── Links FILER_ID to FILING_ID
         │
         ├──→ FILER_TO_FILER_TYPE (Characteristics over time)
         │
         └──→ FILER_ETHICS_CLASS (Ethics training dates)

FILINGS_CD (Document Registry)
    └── FILING_ID ← THE SECONDARY KEY
         │
         ├──→ CVR_REGISTRATION_CD (Registration cover pages)
         │         └── Forms 601, 602, 603, 604, 606, 607
         │
         ├──→ CVR_LOBBY_DISCLOSURE_CD (Disclosure cover pages)
         │         └── Forms 615, 625, 635, 645
         │
         └──→ Schedule Tables (Detailed data)
                  ├── LEXP_CD (Expenditures)
                  ├── LPAY_CD (Payments) ← CRITICAL FOR CITY/COUNTY TRACKING
                  ├── LOTH_CD (Other payments)
                  ├── LCCM_CD (Campaign contributions)
                  └── LATT_CD (Attachments)
```

### Critical Lesson

**`FILER_ID` and `FILING_ID` are the two master keys** for navigating the entire database. Every query should start with one of these two identifiers.

---

## 3. Entity Code System

### Critical Entity Codes (ENTITY_CD)

Understanding entity codes is **CRITICAL** for correct querying:

| Code | Meaning | Example | Usage Context |
|------|---------|---------|---------------|
| **LBY** | Lobbyist | Individual registered lobbyist | Person who lobbies |
| **LEM** | Lobbyist Employer | City of Oakland, County of Alameda | **Entity that HIRED the lobbyist** |
| **FRM** | Lobbying Firm | Nielsen Merksamer, Capitol Advocacy | **Firm that WAS HIRED** |
| **LCO** | Lobbying Coalition | Coalition of organizations | Group lobbying entity |
| **PTN** | Partner | Partner in lobbying firm | Disclosure forms |
| **OWN** | Owner | Owner of lobbying firm | Disclosure forms |
| **OFF** | Officer | Officer of lobbying firm | Disclosure forms |
| **EMP** | Employee | Employee of lobbying firm | Disclosure forms |

### Payment Flow Understanding

```
City/County (LEM - Employer)
    → PAYS MONEY TO →
Lobbying Firm (FRM)
    → WHICH EMPLOYS →
Individual Lobbyists (LBY)
```

### Critical Distinction

- **LEM** = The city, county, or organization that **pays for** lobbying services
- **FRM** = The lobbying firm that **receives payment** for lobbying services
- **LBY** = The individual lobbyist **employed by** the firm

**Common Error**: Confusing LEM and FRM will give you backwards payment data!

---

## 4. Form Type Structure

### Registration Forms (600 Series)

| Form | Purpose | Primary Table | Schedule Tables |
|------|---------|---------------|-----------------|
| **601** | Lobbying firm registration | CVR_REGISTRATION_CD | LEMP_CD (Parts 2A, 2B) |
| **602** | Lobbyist registration | CVR_REGISTRATION_CD | - |
| **603** | Lobbyist employer registration | CVR_REGISTRATION_CD | - |
| **604** | Lobbyist certification | CVR_REGISTRATION_CD | - |
| **605** | Registration amendment | - | LOBBY_AMENDMENTS_CD (Part I) |
| **606** | Lobbyist authorization | CVR_REGISTRATION_CD | - |
| **607** | Lobbyist termination | CVR_REGISTRATION_CD | - |

### Disclosure Forms (Quarterly Reports)

| Form | Filer Type | Primary Table | Schedule Tables | Purpose |
|------|------------|---------------|-----------------|---------|
| **615** | Lobbyist employer | CVR_LOBBY_DISCLOSURE_CD | LEXP_CD (P1), LCCM_CD (P2) | Employer quarterly activity |
| **625** | Lobbying firm | CVR_LOBBY_DISCLOSURE_CD | LPAY_CD (P2), LEXP_CD (P3A), LOTH_CD (P3B), LCCM_CD (P4B) | Firm comprehensive report |
| **635** | Lobbyist employer | CVR_LOBBY_DISCLOSURE_CD | LPAY_CD (P3B), LEXP_CD (P3C), LCCM_CD (P4B) | Employer detailed activity |
| **645** | Lobbying firm | CVR_LOBBY_DISCLOSURE_CD | LEXP_CD (P2A), LCCM_CD (P3B) | Firm simplified report |
| **690** | Amendment | - | F690P2_CD | Disclosure amendment |

### Critical Insight

**Form numbers directly map to schedule tables**. Understanding which form uses which schedule is essential for correct joins.

**Example**: If you see Form 625 Part 2 (P2), you know the data is in `LPAY_CD`.

---

## 5. Schedule Table Purposes

### Complete Schedule Table Reference

| Table | Full Name | Purpose | Key Fields | Forms Using It |
|-------|-----------|---------|------------|----------------|
| **LEXP_CD** | Lobbying Activity Expenditures | Expenses for lobbying activities | `PAYEE_*`, `EXPN_DSCR`, `BENE_NAME`, `BENE_POSIT`, `AMOUNT` | F615 P1, F625 P3A, F635 P3C, F645 P2A |
| **LPAY_CD** | Lobbying Payments | **Payments to/from lobbying firms** | `EMPLR_NAML`, `PAYEE_NAML`, `FEES_AMT`, `REIMB_AMT`, `ADVAN_AMT`, `PER_TOTAL` | F625 P2, F635 P3B |
| **LOTH_CD** | Other Payments | Payments to other lobbying firms | Payment details | F625 P3B |
| **LCCM_CD** | Lobbying Campaign Contributions | Campaign contributions made by lobbyists | Contribution date, amount, contributor, committee | F615 P2, F625 P4B, F635 P4B, F645 P3B |
| **LATT_CD** | Lobbying Attachments | Supporting documentation for payments | Attachment details | S630, S635, S640 |
| **LEMP_CD** | Lobbyist Employers/Clients | Employer or client relationships | `CON_PERIOD`, `DESCRIP`, client address | F601 Parts 2A/2B |

### LPAY_CD: The Most Critical Table

**For tracking city/county lobbying:**

```sql
-- LPAY_CD structure (conceptual)
FILING_ID         -- Links to filing
AMEND_ID          -- Amendment number (0 = original)
EMPLR_NAML        -- The city/county that PAID (LEM entity)
PAYEE_NAML        -- The lobbying firm that was PAID (FRM entity)
FEES_AMT          -- Fees paid
REIMB_AMT         -- Reimbursements
ADVAN_AMT         -- Advance payments
PER_TOTAL         -- Total for period
CUM_TOTAL         -- Cumulative total
```

**Critical Lesson**: To find city/county lobbying expenses, query `LPAY_CD` where the employer (`EMPLR_NAML`) is a city/county entity.

---

## 6. Amendment Tracking System

### AMEND_ID Pattern

Every filing can be amended multiple times:

| AMEND_ID | Meaning |
|----------|---------|
| **0** | Original filing (first submission) |
| **1** | First amendment |
| **2** | Second amendment |
| **...** | Subsequent amendments |
| **999** | Maximum amendment number |

### Amendment Logic Tables

**LOBBY_AMENDMENTS_CD** (Form 605 Part I) tracks registration amendments:

| Field | Purpose |
|-------|---------|
| `ADD_L_CB` | Checkbox: Adding lobbyist |
| `ADD_LE_CB` | Checkbox: Adding lobbyist employer |
| `ADD_LF_CB` | Checkbox: Adding lobbying firm |
| `DEL_L_CB` | Checkbox: Deleting lobbyist |
| `DEL_LE_CB` | Checkbox: Deleting lobbyist employer |
| `DEL_LF_CB` | Checkbox: Deleting lobbying firm |
| `EFF_DATE` | Effective date of change |

**F690P2_CD** tracks disclosure filing amendments (Form 690).

### Critical Query Pattern

**ALWAYS filter for the LATEST amendment**:

```sql
-- Example: Get latest amendment only
SELECT *
FROM lpay_cd
WHERE (filing_id, amend_id) IN (
    SELECT filing_id, MAX(amend_id)
    FROM lpay_cd
    GROUP BY filing_id
)
```

**Our BigQuery view pattern**:
```sql
-- v_int_payment_with_latest_amendment uses this pattern
```

### Common Error

**Counting all amendments as separate payments** will inflate totals. Always use `MAX(AMEND_ID)` or filter to latest amendment.

---

## 7. Historical Data Complexity

### The Mysterious Numbered Tables

The documentation explicitly notes **UNDOCUMENTED COMPLEXITY**:

> "Matt needs to describe the relationship between the multiple tables"

### Pattern Found

Multiple sets of numbered tables exist:

| Table Set | Purpose (Apparent) | Key Fields |
|-----------|-------------------|------------|
| `LOBBYIST_EMPLOYER1` <br> `LOBBYIST_EMPLOYER2` <br> `LOBBYIST_EMPLOYER3` | Quarterly, yearly, session totals for employers | `QUARTER_AMT`, `YR_1_YTD_AMT`, `YR_2_YTD_AMT`, `SESSION_TOTAL_AMT`, interest codes |
| `LOBBYIST_FIRM1` <br> `LOBBYIST_FIRM2` <br> `LOBBYIST_FIRM3` | Quarterly, yearly, session totals for firms | Aggregated amounts by period |
| `LOBBYIST_CONTRIBUTIONS1` <br> `LOBBYIST_CONTRIBUTIONS2` <br> `LOBBYIST_CONTRIBUTIONS3` | Contribution tracking (1/2 marked "temporary") | Contribution totals |

### Temporal/Aggregation Layers (Hypothesis)

The numbered suffixes appear to represent:
- **Different aggregation levels** (quarterly → yearly → session)
- **Different calculation methods** (raw → adjusted → final)
- **Processing stages** (temporary → validated → published)

### Critical Warning

**Use these tables with extreme caution**:
- Their exact relationship is not documented even in the original Oracle schema
- May contain duplicate or overlapping data
- Prefer using the schedule tables (LEXP, LPAY, LCCM) and creating your own aggregations
- If you must use them, validate results against schedule table aggregations

### Investigation Task

**TODO**: Analyze the actual data in these numbered tables to determine:
1. What distinguishes `*_EMPLOYER1` from `*_EMPLOYER2` from `*_EMPLOYER3`
2. Whether they're additive or mutually exclusive
3. Which one to use for which purpose

---

## 8. Materialized Views for Performance

### Oracle Materialized View Tables

The database uses Oracle's materialized view (MVIEW) feature for pre-aggregated snapshots:

| Materialized View | Purpose | Contains |
|------------------|---------|----------|
| `MVIEW_LOBBYIST_CONTRIB` | Snapshot of lobbyist contributions | Filing IDs, session IDs, amounts |
| `MV_SMRY_F635` | Form 635 summary data | Pre-aggregated Form 635 data |

### Performance Implication

**The existence of materialized views suggests**:
- Querying raw schedule tables for aggregations is SLOW
- Pre-aggregation is necessary for acceptable query performance
- Large datasets (millions of rows)

### Our BigQuery Implementation

We've created **73 analytical views** in 4 layers that serve a similar purpose:

1. **Layer 1**: Base views with clean column names
2. **Layer 2**: Pre-joined integration views
3. **Layer 3**: Aggregation views
4. **Layer 4**: Filtered specialty views

**Example**: `v_organization_summary` provides 116x faster performance than raw queries.

### Lesson

**For production queries**: Always use pre-aggregated views rather than querying schedule tables directly.

---

## 9. Supporting Infrastructure

### Critical Supporting Tables

| Table | Purpose | Key Usage |
|-------|---------|-----------|
| **NAMES_CD** | All entity names for searching | Handles name variations, supports name-based lookups |
| **ADDRESS_CD** | All addresses in the system | Location-based searches, address display in AMS |
| **FILER_TO_FILER_TYPE_CD** | Links filers to characteristics | Historical tracking of filer types over time |
| **FILER_ETHICS_CLASS_CD** | Ethics training tracking | Stores `ETHICS_DATE` for lobbyist ethics course completion |
| **LOBBYING_CHG_LOG_CD** | Web display change log | Tracks ADD/DELETE/CHANGE actions for attributes (NAME, ADDRESS, LINK) |
| **FILER_TYPES_CD** | Filer classifications | Lookup table for filer type codes |
| **LOOKUP_CODES_CD** | Code translations | Translates coded values to human-readable text |

### Query Pattern Recommendations

**For name searches**:
```sql
-- ❌ WRONG: Don't query names directly from FILERS
SELECT * FROM filers_cd WHERE filer_naml LIKE '%Oakland%'

-- ✅ CORRECT: Use NAMES table
SELECT f.*
FROM filers_cd f
JOIN names_cd n ON f.filer_id = n.filer_id
WHERE n.naml LIKE '%Oakland%'
```

**For address searches**:
```sql
-- Use ADDRESS_CD table, not embedded addresses in other tables
SELECT f.*, a.city, a.st, a.zip4
FROM filers_cd f
JOIN address_cd a ON f.filer_id = a.filer_id
WHERE a.city = 'Oakland'
```

### Why This Matters

- **Normalization**: Prevents data duplication
- **Name variations**: Handles "City of Oakland" vs "Oakland" vs "Oakland, City of"
- **Address history**: Tracks address changes over time
- **Data quality**: Centralized location for data cleaning

---

## 10. Data Quality Caveats

### Known Issues

| Issue Category | Description | Impact |
|----------------|-------------|--------|
| **Redundancy** | Multiple similar tables with unclear relationships | Confusion about which table to use |
| **Incomplete Documentation** | Original schema has gaps ("Matt needs to describe...") | Requires empirical investigation |
| **Legacy System** | Oracle database from 2002, 20+ years old | Accumulated technical debt |
| **Temporary Tables** | `LOBBYIST_CONTRIBUTIONS1/2` marked "temporary" but persist | May contain stale data |
| **Name Variations** | Same entity with multiple name spellings | Requires fuzzy matching |
| **Missing Data** | Not all fields populated in all filings | Null handling essential |
| **Data Entry Errors** | Manual entry introduces typos, inconsistencies | Validation required |

### Specific Data Quality Patterns

**Name inconsistencies**:
- "City of Oakland" vs "Oakland" vs "Oakland, City of"
- "County of Alameda" vs "Alameda County"
- Misspellings, typos, abbreviations

**Address inconsistencies**:
- Different formats for same address
- Missing zip codes
- PO Box vs street address variations

**Date issues**:
- Multiple date fields with unclear semantics
- Date ranges that overlap or contradict
- Missing signature dates

**Amount discrepancies**:
- `PER_TOTAL` vs `CUM_TOTAL` calculation errors
- Amended filings with different totals
- Rounding differences

### Validation Recommendations

1. **Always validate sums**: Check that detail records sum to cover page totals
2. **Handle nulls explicitly**: Don't assume fields are populated
3. **Use fuzzy matching for names**: Levenshtein distance, soundex, etc.
4. **Cross-reference multiple sources**: Verify critical data points
5. **Track data quality metrics**: Log anomalies for investigation

---

## 11. Index Types and Performance

### Index Types Used in Cal-ACCESS

The Oracle schema uses specific index conventions:

| Index Type | Code | Purpose | Example |
|------------|------|---------|---------|
| **Primary key** | P | Uniquely identifies a row | `FILER_ID` in FILERS_CD |
| **Foreign key** | F | Links to another table's primary key | `FILER_ID` in FILER_FILINGS_CD |
| **Alternate key** | A | Unique identifier (not primary) | Alternative unique constraint |
| **Unique** | U | No duplicate values allowed | All primary keys must be unique |
| **Cluster** | C | Physical order = logical order | Performance optimization |

### Column Properties

| Property | Code | Meaning |
|----------|------|---------|
| **Mandatory** | M | Field must have a value (NOT NULL) |
| **Primary** | P | Part of primary key |
| **Foreign** | F | Foreign key reference |

### Performance Implications

**Query performance depends on using indexed fields**:

✅ **Fast queries** (use indexed fields):
```sql
SELECT * FROM lpay_cd WHERE filing_id = 123456
SELECT * FROM filers_cd WHERE filer_id = 98765
SELECT * FROM filer_filings_cd WHERE filer_id = 98765 AND filing_id = 123456
```

❌ **Slow queries** (full table scans):
```sql
SELECT * FROM lpay_cd WHERE emplr_naml LIKE '%Oakland%'  -- No index on EMPLR_NAML
SELECT * FROM lexp_cd WHERE expn_dscr LIKE '%consultant%'  -- No index on descriptions
```

### BigQuery Considerations

In our BigQuery implementation:
- Clustering on `filer_id`, `filing_id`, `amend_id` improves query performance
- Partitioning by date fields reduces scan cost
- Materialized views (or our view layers) are essential for complex aggregations

---

## 12. Date Field Confusion

### Multiple Date Fields with Different Meanings

| Field Name | Meaning | Example Usage | Context |
|------------|---------|---------------|---------|
| **RPT_DATE** | Report date | Date the report covers | Cover pages |
| **FROM_DATE** | Period start date | Beginning of reporting quarter | Quarterly disclosures |
| **THRU_DATE** | Period end date | End of reporting quarter | Quarterly disclosures |
| **SIG_DATE** | Signature date | When filer signed the form | Cover pages |
| **EFF_DATE** | Effective date | When authorization/termination takes effect | Registrations, amendments |
| **COMPLET_DT** | Completion date | Ethics course completion | Form 604 |
| **FILING_DATE** | When filed | Date submitted to Secretary of State | FILINGS table |
| **CON_PERIOD** | Contract period | Duration of lobbying contract | LEMP table |

### Critical Distinctions

```
Example Filing Timeline:
- FROM_DATE: 2024-01-01 (quarter starts)
- THRU_DATE: 2024-03-31 (quarter ends)
- SIG_DATE: 2024-04-15 (filer signs form)
- FILING_DATE: 2024-04-18 (submitted to state)
- RPT_DATE: 2024-03-31 (report covers through this date)
```

### Common Errors

❌ **Using the wrong date for time-based analysis**:
```sql
-- WRONG: Using signature date for activity period
SELECT * FROM lpay_cd WHERE sig_date BETWEEN '2024-01-01' AND '2024-03-31'

-- CORRECT: Using report period dates
SELECT * FROM lpay_cd WHERE from_date >= '2024-01-01' AND thru_date <= '2024-03-31'
```

### Recommendations

1. **For activity analysis**: Use `FROM_DATE` and `THRU_DATE`
2. **For filing compliance**: Use `FILING_DATE` and `SIG_DATE`
3. **For registration status**: Use `EFF_DATE`
4. **Always clarify**: Document which date field you're using and why

---

## 13. Payment Flow Logic

### Understanding Who Pays Whom

```
LOBBYING PAYMENT FLOW:

City/County/Organization (LEM - Lobbyist Employer)
    │
    │ PAYS MONEY (via LPAY_CD)
    │
    ▼
Lobbying Firm (FRM - Firm)
    │
    │ EMPLOYS
    │
    ▼
Individual Lobbyists (LBY - Lobbyist)
    │
    │ INCURS EXPENSES (via LEXP_CD)
    │
    ▼
Vendors/Recipients of Lobbying Expenditures
```

### LPAY_CD Table Structure (Conceptual)

```sql
LPAY_CD (Lobbying Payments)
├── FILING_ID              -- Links to CVR_LOBBY_DISCLOSURE
├── AMEND_ID               -- Amendment tracking
├── LINE_ITEM              -- Line number on form
│
├── EMPLR_ID               -- Employer filer ID (who PAID)
├── EMPLR_NAML             -- Employer name (City of Oakland)
├── EMPLR_NAMF             -- Employer first name (if individual)
│
├── PAYEE_NAML             -- Payee name (Nielsen Merksamer)
├── PAYEE_NAMF             -- Payee first name
├── PAYEE_ADR1/2           -- Payee address
│
├── FEES_AMT               -- Fees paid to lobbying firm
├── REIMB_AMT              -- Reimbursements
├── ADVAN_AMT              -- Advance payments
├── PER_TOTAL              -- Total for THIS period
└── CUM_TOTAL              -- Cumulative total (year-to-date)
```

### Query Pattern for City/County Lobbying

**To find all lobbying payments BY a city/county**:

```sql
SELECT
    p.emplr_naml AS city_or_county,
    p.payee_naml AS lobbying_firm,
    p.per_total AS amount_paid,
    d.from_date,
    d.thru_date
FROM lpay_cd p
JOIN cvr_lobby_disclosure_cd d ON p.filing_id = d.filing_id
JOIN filers_cd f ON p.emplr_id = f.filer_id
WHERE f.entity_cd = 'LEM'  -- Lobbyist Employer
    AND p.emplr_naml LIKE '%Oakland%'
    AND p.amend_id = (
        SELECT MAX(amend_id)
        FROM lpay_cd
        WHERE filing_id = p.filing_id
    )
```

### Critical Understanding

- **EMPLR_NAML** = The entity that HIRED and PAID for lobbying (the city/county)
- **PAYEE_NAML** = The entity that WAS PAID (the lobbying firm)
- **PER_TOTAL** = Amount for this quarter
- **CUM_TOTAL** = Running total (can be confusing across amendments)

### Common Mistake

**Reversing the employer and payee** will give you the opposite of what you want:
- ❌ Querying `payee_naml` for cities will find payments TO cities (wrong)
- ✅ Querying `emplr_naml` for cities finds payments BY cities (correct)

---

## 14. Database Conceptual Model

### Analogy from Documentation

The original documentation provides an excellent conceptual model:

| Database Component | Real-World Equivalent | Purpose |
|-------------------|----------------------|---------|
| **FILERS_CD** | Master register of people | Registry of all entities involved |
| **FILINGS_CD** | Log of submitted documents | Inventory of all reports filed |
| **CVR_LOBBY_DISCLOSURE_CD** <br> **CVR_REGISTRATION_CD** | Filing cabinets for cover pages | Standardized form metadata |
| **L* schedules** <br> (LEXP, LPAY, LCCM) | Detailed receipts and ledgers | Line-item proof of activities |
| **NAMES_CD** | Card catalog for name searches | Finding entities by various name forms |
| **ADDRESS_CD** | Address book | Location tracking and contact info |

### Mental Model

Think of Cal-ACCESS as a **digital archive system**, not a transactional database:

- **Not designed for**: Real-time updates, financial transactions, application workflows
- **Designed for**: Historical record-keeping, compliance tracking, public disclosure
- **Optimized for**: Batch imports, periodic reporting, archival queries

### Query Strategy

When querying Cal-ACCESS data:

1. **Start with filers**: Who are the entities involved?
2. **Find their filings**: What reports did they submit?
3. **Get cover page metadata**: What type of form, what period?
4. **Drill into schedules**: What are the specific line items?
5. **Cross-reference supporting tables**: Names, addresses, codes

---

## 15. Critical Recommendations

### For Your Cal-ACCESS Lobbying Project

Based on all lessons learned, here are the critical recommendations:

#### 1. Focus on LPAY_CD for City/County Tracking

**This is your primary data source** for tracking municipal lobbying expenditures:
- `EMPLR_NAML` contains city/county names
- `PER_TOTAL` is the payment amount
- Always filter to latest `AMEND_ID`

#### 2. Always Handle Amendments Correctly

```sql
-- ALWAYS use this pattern
WHERE (filing_id, amend_id) IN (
    SELECT filing_id, MAX(amend_id)
    FROM [table]
    GROUP BY filing_id
)
```

**Or use our view**: `v_int_payment_with_latest_amendment`

#### 3. Use Entity Codes Correctly

- **LEM** = Cities/counties that HIRED lobbyists (employers)
- **FRM** = Lobbying firms that WERE HIRED
- **LBY** = Individual lobbyists

**Don't confuse these or your payment data will be backwards!**

#### 4. Leverage Your 73 Existing Views

You've already created excellent view layers:
- **Layer 1**: `v_filers`, `v_payments`, `v_disclosures`
- **Layer 2**: `v_int_payment_details`, `v_int_payment_with_latest_amendment`
- **Layer 3**: `v_summary_payments_by_year`
- **Layer 4**: `v_filter_alameda_filers`

**Use these instead of querying raw tables directly.**

#### 5. Document Unknowns

The numbered suffix tables (`LOBBYIST_EMPLOYER1/2/3`) need investigation:
- What distinguishes them?
- Which should we use for what purpose?
- Do they contain duplicate data?

**TODO**: Create analysis script to compare these tables.

#### 6. Expect and Validate Data Quality

Build data quality checks into your pipeline:
- Name normalization (City of Oakland → Oakland)
- Null handling
- Sum validation (detail lines = cover page totals)
- Date range validation
- Amount reasonableness checks

#### 7. Use Materialized Views for Performance

Our BigQuery view layers serve the same purpose as Oracle MVIEWs:
- Pre-aggregate common metrics
- Pre-join frequently used tables
- Consider clustering/partitioning for large views

**Example**: `v_organization_summary` provides 116x speedup.

#### 8. Test Thoroughly

The complexity of form → table mappings means bugs are easy:
- Verify payment totals match source documents
- Cross-check against Cal-ACCESS public website
- Validate entity classifications
- Test amendment handling edge cases

#### 9. Create Field-Level Documentation

Document critical fields in your views:
```sql
CREATE OR REPLACE VIEW v_payments AS
SELECT
    filing_id,
    amend_id,
    emplr_naml AS employer_name,  -- City/county that PAID for lobbying
    payee_naml AS firm_name,      -- Lobbying firm that WAS PAID
    per_total AS period_amount,   -- Amount for this quarter
    cum_total AS cumulative_amount -- Running total (use with caution)
FROM lpay_cd
```

#### 10. Maintain This Knowledge Base

As you discover new insights:
- Update this lessons_learned.md document
- Add to field_mapping_guide.md
- Document in business_rules.md
- Update view comments in BigQuery

---

## Summary: Most Critical Takeaways

### The Three Cardinal Rules

1. **ALWAYS use FILER_ID and FILING_ID** - These are your navigational keys
2. **ALWAYS filter to latest AMEND_ID** - Or you'll count amendments as duplicates
3. **ALWAYS understand entity codes** - LEM = payer, FRM = payee (don't reverse!)

### The Most Important Tables

| Priority | Table | Why Critical |
|----------|-------|--------------|
| 1 | **LPAY_CD** | Payment tracking - core data for city/county lobbying |
| 2 | **FILERS_CD** | Master registry - links everything |
| 3 | **FILER_FILINGS_CD** | Junction table - connects filers to filings |
| 4 | **CVR_LOBBY_DISCLOSURE_CD** | Cover pages - form metadata |
| 5 | **LEXP_CD** | Expenditures - detailed spending |

### The Biggest Pitfalls

1. ❌ Counting all amendments instead of latest only → Inflated totals
2. ❌ Confusing LEM and FRM entity codes → Backwards payment data
3. ❌ Using wrong date fields → Incorrect time periods
4. ❌ Querying raw tables without views → Slow performance
5. ❌ Ignoring data quality issues → Inaccurate results

### Success Pattern

```
Query Strategy:
1. Start with your views (v_int_payment_with_latest_amendment)
2. Filter by entity type (LEM for cities/counties)
3. Filter by date range (FROM_DATE, THRU_DATE)
4. Aggregate carefully (watch for nulls, amendments)
5. Validate results (cross-check totals, spot-check names)
```

---

**Last Updated**: November 2025
**Source**: Cal-ACCESS schema documentation analysis
**Maintained By**: Ca-Lobby Project Team
