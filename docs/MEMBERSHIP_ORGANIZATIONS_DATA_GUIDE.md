# Membership Organizations Payment Data Guide

**Created:** October 30, 2025
**Purpose:** Document the location and structure of membership organization payment data
**Examples:** League of California Cities, California State Association of Counties (CSAC)

---

## Table of Contents

1. [Quick Answer](#quick-answer)
2. [What Are Membership Organizations?](#what-are-membership-organizations)
3. [Where the Data Lives](#where-the-data-lives)
4. [Table Structure Details](#table-structure-details)
5. [How to Query This Data](#how-to-query-this-data)
6. [Common Membership Organizations](#common-membership-organizations)
7. [Data Architecture Reasoning](#data-architecture-reasoning)
8. [Use Cases](#use-cases)

---

## Quick Answer

**Question:** Which table has payments to membership organizations such as League of Cities or League of Counties?

**Answer:** **`LPAY_CD` table** - Look in the **`EMPLR_NAML`** (Employer Name Last) column

**Reasoning:** Membership organizations (like League of Cities, CSAC) act as **lobbying employers** who hire lobbyists and firms. Their payments appear in `LPAY_CD` where they are listed as the employer making payments to lobbying firms or individual lobbyists.

---

## What Are Membership Organizations?

### Definition

Membership organizations in the lobbying context are:
- **Associations** representing multiple member entities
- **Coalitions** pooling resources to hire lobbyists
- **Professional groups** advocating for member interests

### Common Types

1. **Municipal Associations**
   - League of California Cities
   - Regional city associations
   - Special municipal groups

2. **County Associations**
   - California State Association of Counties (CSAC)
   - Regional county groups

3. **Professional Associations**
   - Trade associations
   - Industry coalitions
   - Professional societies

### How They Operate

```
Member Cities/Counties
    ↓ (pay dues)
League/Association
    ↓ (hires and pays)
Lobbying Firms/Lobbyists
    ↓ (lobby)
State Legislature/Agencies
```

---

## Where the Data Lives

### Primary Location: LPAY_CD Table

**Table:** `ca-lobby.ca_lobby.LPAY_CD`
**Full Name:** Lobbying Payments Code
**Purpose:** Payments made or received by lobbying firms

### Key Columns for Membership Organizations

| Column | Purpose | Example Value |
|--------|---------|---------------|
| **EMPLR_NAML** | Employer Name Last | "LEAGUE OF CALIFORNIA CITIES" |
| **EMPLR_NAMF** | Employer Name First | NULL (for organizations) |
| **EMPLR_CITY** | Employer City | "SACRAMENTO" |
| **EMPLR_ST** | Employer State | "CA" |
| **PAYEE_NAML** | Recipient Name Last | "SHAW YODER ANTWIH SCHMELZER" |
| **PAYEE_NAMF** | Recipient Name First | NULL (for firms) |
| **AMOUNT** | Payment Amount | 50000.00 |
| **FILING_ID** | Filing Identifier | 2945123 |
| **AMEND_ID** | Amendment Number | 0 |
| **FORM_TYPE** | Form Type | "F625P2" or "F635P3A" |

### What This Means

- **EMPLR_NAML**: The membership organization (e.g., "LEAGUE OF CALIFORNIA CITIES")
- **PAYEE_NAML**: The lobbying firm they hired (e.g., "SHAW YODER ANTWIH SCHMELZER")
- **AMOUNT**: How much they paid the lobbying firm

---

## Table Structure Details

### LPAY_CD Overview

**Fields:** 27 fields
**Records:** Millions of payment transactions
**Update Frequency:** Daily (as new filings are submitted)

### Associated Forms

Payments in LPAY_CD come from these disclosure forms:

1. **Form 625 (F625P2)** - Report of Lobbying Firm
   - Filed by the lobbying firm
   - Shows payments received from clients (employers)
   - Quarterly filing requirement

2. **Form 635 (F635P3A)** - Report of Lobbyist Employer
   - Filed by the employer organization
   - Shows payments made to lobbying firms
   - Quarterly filing requirement

### Why LPAY_CD (Not Other Tables)?

| Table | Contains | Why Not This Table? |
|-------|----------|---------------------|
| **LATT_CD** | Lobbying coalition payment attachments | Only for specific schedule attachments (635C), not main payment records |
| **LEXP_CD** | Lobbying expenditures | Activity expenses (meals, travel), not payments to firms |
| **LOTH_CD** | Other lobbying payments | Miscellaneous payments, not standard employer-to-firm payments |
| **LCCM_CD** | Campaign contributions | Political contributions, not lobbying service payments |
| **LPAY_CD** | ✅ Payments to/from firms | **Primary payment records** |

---

## How to Query This Data

### Query 1: Find All Membership Organizations

```sql
SELECT
    DISTINCT EMPLR_NAML,
    EMPLR_CITY,
    EMPLR_ST,
    COUNT(*) as payment_count,
    SUM(AMOUNT) as total_amount
FROM `ca-lobby.ca_lobby.LPAY_CD`
WHERE
    (UPPER(EMPLR_NAML) LIKE '%LEAGUE%'
     OR UPPER(EMPLR_NAML) LIKE '%ASSOCIATION OF COUNTIES%'
     OR UPPER(EMPLR_NAML) LIKE '%ASSOCIATION OF CITIES%'
     OR UPPER(EMPLR_NAML) LIKE '%CSAC%')
    AND EMPLR_NAML IS NOT NULL
GROUP BY EMPLR_NAML, EMPLR_CITY, EMPLR_ST
ORDER BY total_amount DESC
```

**Returns:** List of all membership organizations with payment totals

### Query 2: Find Payments by Specific Organization

```sql
SELECT
    FILING_ID,
    AMEND_ID,
    LINE_ITEM,
    FORM_TYPE,
    EMPLR_NAML as membership_org,
    PAYEE_NAML as lobbying_firm,
    PAYEE_CITY,
    PAYEE_ST,
    AMOUNT,
    CUM_YTD,
    MEMO_REFNO
FROM `ca-lobby.ca_lobby.LPAY_CD`
WHERE
    UPPER(EMPLR_NAML) LIKE '%LEAGUE OF CALIFORNIA CITIES%'
ORDER BY AMOUNT DESC
LIMIT 100
```

**Returns:** All payments made by League of California Cities

### Query 3: Get Payment Details with Dates

To get date information, join with disclosure table:

```sql
SELECT
    p.FILING_ID,
    p.LINE_ITEM,
    p.EMPLR_NAML as membership_org,
    p.PAYEE_NAML as lobbying_firm,
    p.AMOUNT,
    d.FROM_DATE as period_start,
    d.THRU_DATE as period_end,
    d.RPT_DATE as report_date
FROM `ca-lobby.ca_lobby.LPAY_CD` p
INNER JOIN `ca-lobby.ca_lobby.CVR_LOBBY_DISCLOSURE_CD` d
    ON p.FILING_ID = d.FILING_ID
    AND p.AMEND_ID = d.AMEND_ID
WHERE
    UPPER(p.EMPLR_NAML) LIKE '%LEAGUE%'
ORDER BY d.FROM_DATE DESC, p.AMOUNT DESC
```

**Returns:** Payments with reporting period dates

---

## Common Membership Organizations

### Search Patterns

Use these patterns to find membership organizations in `LPAY_CD.EMPLR_NAML`:

| Pattern | Matches | Example Organizations |
|---------|---------|----------------------|
| `%LEAGUE%` | City/municipal leagues | League of California Cities |
| `%ASSOCIATION OF COUNTIES%` | County associations | California State Association of Counties |
| `%ASSOCIATION OF CITIES%` | City associations | Regional city associations |
| `%CSAC%` | CSAC abbreviation | California State Association of Counties |
| `%COALITION%` | Lobbying coalitions | Various coalitions of organizations |
| `%CONFERENCE%` | Conference groups | Conference of California Bar Associations |

### Likely Top Organizations

Based on CA lobbying patterns, expect to find:

1. **League of California Cities**
   - Represents 482 California cities
   - Major lobbying presence in Sacramento

2. **California State Association of Counties (CSAC)**
   - Represents all 58 California counties
   - Significant lobbying budget

3. **Regional Associations**
   - Bay Area city associations
   - Southern California city associations
   - County supervisor associations

4. **Special District Associations**
   - Water district associations
   - School district associations
   - Transit district associations

---

## Data Architecture Reasoning

### Why LPAY_CD Contains This Data

#### 1. Legal Reporting Requirements

**Political Reform Act of 1974** requires:
- Lobbying employers must disclose payments to lobbyists/firms
- Lobbying firms must disclose payments received from clients
- Both file quarterly reports

#### 2. Dual Reporting System

```
Membership Organization              Lobbying Firm
(League of Cities)                   (Shaw Yoder)
        ↓                                   ↓
Files Form 635                       Files Form 625
"We paid Shaw Yoder $50K"           "We received $50K from League"
        ↓                                   ↓
    LPAY_CD Record                      LPAY_CD Record
    EMPLR_NAML = League                 EMPLR_NAML = League
    PAYEE_NAML = Shaw Yoder             PAYEE_NAML = Shaw Yoder
```

Both filings create records in LPAY_CD with the **employer** (membership org) in `EMPLR_NAML`.

#### 3. Table Design Logic

**LPAY_CD structure:**
- **EMPLR_* columns**: Who is paying (the client/employer)
- **PAYEE_* columns**: Who is receiving payment (the firm/lobbyist)
- **AMOUNT**: Payment amount
- **FILING_ID**: Links to disclosure cover page

This design captures the employer-to-firm financial relationship.

### Why NOT Other Tables?

#### LATT_CD - Payment Attachments
- **Purpose**: Supporting schedule attachments
- **Scope**: Schedule 635C (lobbying coalition receipts), Schedule 640 (agency reporting)
- **Limitation**: Supplementary detail, not primary payment records
- **Use Case**: Additional breakdown for coalition payments

#### LEXP_CD - Expenditures
- **Purpose**: Activity-related expenses
- **Scope**: Meals with officials, travel costs, event expenses
- **Limitation**: Direct lobbying costs, not payments to firms
- **Use Case**: Tracking gift limits and direct lobbying expenses

#### LOTH_CD - Other Payments
- **Purpose**: Miscellaneous payments not fitting standard categories
- **Scope**: Unusual or one-time payments
- **Limitation**: Not standard employer-to-firm relationships
- **Use Case**: Edge cases and special circumstances

---

## Use Cases

### Use Case 1: Municipal Lobbying Analysis

**Question:** How much does the League of California Cities spend on lobbying?

**Query Location:** `LPAY_CD.EMPLR_NAML = 'LEAGUE OF CALIFORNIA CITIES'`

**Analysis:**
```sql
SELECT
    SUM(AMOUNT) as total_lobbying_spend,
    COUNT(DISTINCT PAYEE_NAML) as unique_firms,
    COUNT(*) as payment_count
FROM `ca-lobby.ca_lobby.LPAY_CD`
WHERE UPPER(EMPLR_NAML) LIKE '%LEAGUE OF CALIFORNIA CITIES%'
```

### Use Case 2: County vs City Lobbying

**Question:** Do counties or cities spend more on lobbying through their associations?

**Query Location:** Compare `EMPLR_NAML` patterns

**Analysis:**
```sql
-- County associations
SELECT 'Counties' as group_type, SUM(AMOUNT) as total
FROM `ca-lobby.ca_lobby.LPAY_CD`
WHERE UPPER(EMPLR_NAML) LIKE '%ASSOCIATION OF COUNTIES%'
   OR UPPER(EMPLR_NAML) LIKE '%CSAC%'

UNION ALL

-- City associations
SELECT 'Cities' as group_type, SUM(AMOUNT) as total
FROM `ca-lobby.ca_lobby.LPAY_CD`
WHERE UPPER(EMPLR_NAML) LIKE '%LEAGUE%CITIES%'
   OR UPPER(EMPLR_NAML) LIKE '%ASSOCIATION OF CITIES%'
```

### Use Case 3: Which Firms Do Membership Organizations Hire?

**Question:** What lobbying firms do membership organizations prefer?

**Query Location:** `LPAY_CD` with `EMPLR_NAML` (org) and `PAYEE_NAML` (firm)

**Analysis:**
```sql
SELECT
    PAYEE_NAML as lobbying_firm,
    COUNT(DISTINCT EMPLR_NAML) as org_clients,
    SUM(AMOUNT) as total_revenue,
    COUNT(*) as payment_count
FROM `ca-lobby.ca_lobby.LPAY_CD`
WHERE
    (UPPER(EMPLR_NAML) LIKE '%LEAGUE%'
     OR UPPER(EMPLR_NAML) LIKE '%ASSOCIATION%')
GROUP BY PAYEE_NAML
ORDER BY total_revenue DESC
LIMIT 20
```

### Use Case 4: Membership Organization Network

**Question:** Build a network graph of membership organizations and their lobbying firms

**Data Source:** `LPAY_CD`

**Nodes:**
- Membership organizations (from `EMPLR_NAML`)
- Lobbying firms (from `PAYEE_NAML`)

**Edges:**
- Payment amounts (from `AMOUNT`)
- Payment frequency (count of records)

**Implementation:**
```python
# Example: Create network visualization
import pandas as pd
from google.cloud import bigquery

client = bigquery.Client()

query = """
SELECT
    EMPLR_NAML as source,
    PAYEE_NAML as target,
    SUM(AMOUNT) as weight,
    COUNT(*) as edge_count
FROM `ca-lobby.ca_lobby.LPAY_CD`
WHERE
    (UPPER(EMPLR_NAML) LIKE '%LEAGUE%'
     OR UPPER(EMPLR_NAML) LIKE '%ASSOCIATION%')
    AND PAYEE_NAML IS NOT NULL
GROUP BY EMPLR_NAML, PAYEE_NAML
HAVING SUM(AMOUNT) > 10000
"""

df = client.query(query).to_dataframe()
# Use networkx or d3.js for visualization
```

---

## Integration with Production Views

### Existing Views

The 5 production BigQuery views created on October 29, 2025:

1. **v_organization_summary** (37,295 organizations)
2. **v_org_profiles_complete** (44.8M records)
3. **v_lobbyist_network** (83,650 relationships)
4. **v_activity_timeline** (657,151 activities)
5. **v_expenditure_categories** (211.9M expenses)

### How to Integrate Membership Data

#### Option 1: Filter Existing Views

```sql
-- Get membership organizations from v_organization_summary
SELECT *
FROM `ca-lobby.ca_lobby.v_organization_summary`
WHERE
    UPPER(organization_name) LIKE '%LEAGUE%'
    OR UPPER(organization_name) LIKE '%ASSOCIATION%'
ORDER BY total_payments DESC
```

#### Option 2: Create New Membership-Specific View

```sql
CREATE OR REPLACE VIEW `ca-lobby.ca_lobby.v_membership_organizations` AS
SELECT
    EMPLR_NAML as organization_name,
    EMPLR_CITY as city,
    EMPLR_ST as state,
    COUNT(DISTINCT FILING_ID) as filing_count,
    COUNT(*) as payment_count,
    SUM(AMOUNT) as total_payments,
    AVG(AMOUNT) as avg_payment,
    MIN(AMOUNT) as min_payment,
    MAX(AMOUNT) as max_payment,
    COUNT(DISTINCT PAYEE_NAML) as unique_firms
FROM `ca-lobby.ca_lobby.LPAY_CD`
WHERE
    (UPPER(EMPLR_NAML) LIKE '%LEAGUE%'
     OR UPPER(EMPLR_NAML) LIKE '%ASSOCIATION OF COUNTIES%'
     OR UPPER(EMPLR_NAML) LIKE '%ASSOCIATION OF CITIES%'
     OR UPPER(EMPLR_NAML) LIKE '%CSAC%'
     OR UPPER(EMPLR_NAML) LIKE '%COALITION%')
    AND EMPLR_NAML IS NOT NULL
GROUP BY EMPLR_NAML, EMPLR_CITY, EMPLR_ST
ORDER BY total_payments DESC
```

---

## Summary

### Key Points

1. ✅ **Table:** `LPAY_CD` (Lobbying Payments Code)
2. ✅ **Column:** `EMPLR_NAML` (Employer Name Last)
3. ✅ **Search:** Use LIKE patterns (`%LEAGUE%`, `%ASSOCIATION%`)
4. ✅ **Reasoning:** Membership organizations are lobbying employers
5. ✅ **Integration:** Compatible with existing production views

### Quick Reference

```sql
-- Find all League of Cities payments
SELECT *
FROM `ca-lobby.ca_lobby.LPAY_CD`
WHERE UPPER(EMPLR_NAML) LIKE '%LEAGUE%CITIES%'

-- Find all CSAC payments
SELECT *
FROM `ca-lobby.ca_lobby.LPAY_CD`
WHERE UPPER(EMPLR_NAML) LIKE '%CSAC%'
   OR UPPER(EMPLR_NAML) LIKE '%ASSOCIATION OF COUNTIES%'
```

### Documentation References

- [California_Lobbying_Tables_Documentation.md](Documents/California_Lobbying_Tables_Documentation.md) - LPAY_CD table details
- [DATA_ARCHITECTURE_GUIDE.md](Data Arch/DATA_ARCHITECTURE_GUIDE.md) - Overall data architecture
- [PRODUCTION_VIEWS_SESSION_SUMMARY.md](PRODUCTION_VIEWS_SESSION_SUMMARY.md) - Production views (Oct 29, 2025)

---

**Document Version:** 1.0
**Last Updated:** October 30, 2025
**Related Files:**
- `query_membership_organizations.py` - Query script for testing
- `LPAY_CD` table in BigQuery
- Production views for frontend integration
