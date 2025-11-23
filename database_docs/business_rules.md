# Cal-ACCESS Business Rules Reference

> **Business logic and rules** for the Cal-ACCESS lobbying database
>
> **Purpose**: Document how lobbying data flows, filing requirements, and business rules
>
> **Audience**: Developers, analysts, and anyone querying Cal-ACCESS data

---

## Table of Contents

1. [Lobbying Entity Types and Relationships](#lobbying-entity-types-and-relationships)
2. [Payment Flow Logic](#payment-flow-logic)
3. [Form Types and Filing Requirements](#form-types-and-filing-requirements)
4. [Amendment Processing Rules](#amendment-processing-rules)
5. [Reporting Period Rules](#reporting-period-rules)
6. [Amount Calculation Rules](#amount-calculation-rules)
7. [Registration vs. Disclosure Rules](#registration-vs-disclosure-rules)
8. [Data Validation Rules](#data-validation-rules)
9. [Query Business Logic Patterns](#query-business-logic-patterns)

---

## Lobbying Entity Types and Relationships

### Entity Type Definitions

```
Three Primary Entity Types in Lobbying:

1. LOBBYIST EMPLOYER (LEM)
   - The entity that HIRES and PAYS for lobbying services
   - Examples: City of Oakland, County of Alameda, corporations
   - Files: Forms 603, 615, 635

2. LOBBYING FIRM (FRM)
   - The professional firm contracted to provide lobbying services
   - Examples: Nielsen Merksamer, Capitol Advocacy
   - Files: Forms 601, 625, 645

3. LOBBYIST (LBY)
   - Individual person who performs lobbying activities
   - Employed by or contracted with a lobbying firm
   - Files: Forms 602, 604
```

### Relationship Hierarchy

```
LOBBYIST EMPLOYER (LEM)
    │
    │ [Contracts with]
    │ [Pays money to]
    │
    ▼
LOBBYING FIRM (FRM)
    │
    │ [Employs]
    │ [Authorizes]
    │
    ▼
LOBBYIST (LBY)
    │
    │ [Lobbies on behalf of]
    │
    ▼
GOVERNMENT OFFICIALS
```

### Critical Business Rule

**Payment Direction**:
- Money flows FROM employer (LEM) TO firm (FRM)
- Firm (FRM) then compensates individual lobbyists (LBY)
- **In LPAY_CD**: `EMPLR_NAML` = payer (LEM), `PAYEE_NAML` = payee (FRM)

**Common Error**: Confusing LEM and FRM will reverse payment data!

---

## Payment Flow Logic

### Standard Lobbying Payment Flow

```
Step 1: CONTRACT FORMATION
└── Employer (City/County) signs contract with Lobbying Firm
    └── Recorded in LEMP_CD (Form 601 Parts 2A/2B)
        └── CON_PERIOD field shows contract duration

Step 2: LOBBYING SERVICES
└── Lobbyist performs lobbying activities
    └── May incur expenses (meals, gifts, travel)
        └── Recorded in LEXP_CD

Step 3: PAYMENT
└── Employer pays Lobbying Firm
    └── Recorded in LPAY_CD (Forms 625 P2, 635 P3B)
        └── FEES_AMT (retainer/fees)
        └── REIMB_AMT (reimbursements for expenses)
        └── ADVAN_AMT (advance payments)
        └── PER_TOTAL = total for quarter

Step 4: (Optional) CAMPAIGN CONTRIBUTIONS
└── Lobbyist/Firm makes campaign contributions
    └── Recorded in LCCM_CD
```

### LPAY_CD Payment Calculation

**Business Rule**:
```
PER_TOTAL = FEES_AMT + REIMB_AMT + ADVAN_AMT
```

**Components**:
- **FEES_AMT**: Monthly retainer, hourly fees, flat fees
- **REIMB_AMT**: Reimbursement for expenses incurred by firm
- **ADVAN_AMT**: Advance payments (prepayment for future services)

**Query Logic**:
```sql
-- To get total payments BY a city/county
SELECT
    emplr_naml AS city_or_county,
    SUM(per_total) AS total_paid
FROM lpay_cd
WHERE emplr_naml LIKE '%Oakland%'
    AND amend_id = (SELECT MAX(amend_id) FROM lpay_cd p2 WHERE p2.filing_id = lpay_cd.filing_id)
GROUP BY emplr_naml
```

---

## Form Types and Filing Requirements

### Registration Forms (600 Series) - One-Time or Annual

| Form | Who Files | When | Purpose |
|------|-----------|------|---------|
| **601** | Lobbying Firm (FRM) | Initial registration | Register as lobbying firm |
| **602** | Lobbyist (LBY) | Initial registration | Register as individual lobbyist |
| **603** | Employer (LEM) | Initial registration | Register as lobbying employer |
| **604** | Lobbyist (LBY) | After ethics training | Certify completion of ethics course |
| **605** | Any | When changes occur | Amend registration information |
| **606** | Firm (FRM) | For each lobbyist | Authorize lobbyist to represent firm |
| **607** | Firm/Employer | When relationship ends | Terminate lobbyist relationship |

**Business Rule**: Registration forms must be filed BEFORE lobbying activity begins.

### Disclosure Forms (Quarterly Reports) - Recurring

| Form | Who Files | Frequency | Covers |
|------|-----------|-----------|--------|
| **615** | Employer (LEM) | Quarterly | Expenditures and contributions |
| **625** | Firm (FRM) | Quarterly | Comprehensive firm activity (payments, expenses, contributions) |
| **635** | Employer (LEM) | Quarterly | Detailed employer activity (payments, expenses, contributions) |
| **645** | Firm (FRM) | Quarterly | Simplified firm report |
| **690** | Any | As needed | Amend previously filed disclosure |

**Business Rule**: Quarterly disclosures are due by the last day of the month following the end of each calendar quarter.

**Quarterly Schedule**:
- **Q1**: January 1 - March 31 (due April 30)
- **Q2**: April 1 - June 30 (due July 31)
- **Q3**: July 1 - September 30 (due October 31)
- **Q4**: October 1 - December 31 (due January 31)

### Form-to-Schedule Mapping

**Form 625 (Lobbying Firm Comprehensive)**:
- Part 2 → LPAY_CD (payments received from employers)
- Part 3A → LEXP_CD (activity expenditures)
- Part 3B → LOTH_CD (payments to other firms)
- Part 4B → LCCM_CD (campaign contributions)

**Form 635 (Employer Detailed)**:
- Part 3B → LPAY_CD (payments made to firms)
- Part 3C → LEXP_CD (activity expenditures)
- Part 4B → LCCM_CD (campaign contributions)

**Form 615 (Employer Simplified)**:
- Part 1 → LEXP_CD (expenditures)
- Part 2 → LCCM_CD (contributions)

**Business Rule**: Each form part maps to a specific schedule table. Use this mapping to join cover pages to detail records.

---

## Amendment Processing Rules

### Amendment Identifier (AMEND_ID) Rules

**Business Rule**: Every filing can be amended multiple times.

| AMEND_ID | Meaning | Status |
|----------|---------|--------|
| 0 | Original filing | First submission |
| 1 | First amendment | Corrects/updates original |
| 2 | Second amendment | Corrects/updates previous |
| ... | Subsequent amendments | Each supersedes previous |

### Amendment Types

**Registration Amendments (Form 605)**:
```
ADD_L_CB = Add a lobbyist
ADD_LE_CB = Add a lobbyist employer
ADD_LF_CB = Add a lobbying firm
DEL_L_CB = Delete a lobbyist
DEL_LE_CB = Delete a lobbyist employer
DEL_LF_CB = Delete a lobbying firm
```

**Disclosure Amendments (Form 690)**:
- Correct reported amounts
- Add missing line items
- Fix errors in original filing

### Amendment Query Rule

**Critical Business Rule**: Always query for the LATEST amendment only.

```sql
-- CORRECT: Get only latest amendments
WHERE (filing_id, amend_id) IN (
    SELECT filing_id, MAX(amend_id)
    FROM [table]
    GROUP BY filing_id
)

-- WRONG: Counts all amendments as separate filings
WHERE filing_id = 123456  -- Gets all amendments
```

**Why This Matters**:
- Counting all amendments will **inflate totals**
- Amendment 1 **replaces** Amendment 0 (not additive)
- Final amendment represents the **true/corrected** data

---

## Reporting Period Rules

### Quarterly Reporting Periods

**Business Rule**: Lobbying disclosure filings are quarterly, based on calendar quarters.

```
Q1: FROM_DATE = 01/01/YYYY, THRU_DATE = 03/31/YYYY
Q2: FROM_DATE = 04/01/YYYY, THRU_DATE = 06/30/YYYY
Q3: FROM_DATE = 07/01/YYYY, THRU_DATE = 09/30/YYYY
Q4: FROM_DATE = 10/01/YYYY, THRU_DATE = 12/31/YYYY
```

### Legislative Session Periods

**Business Rule**: California legislative sessions are 2-year periods.

```
Session = 2-year period beginning in odd-numbered years

Examples:
- 2023-2024 Legislative Session
- 2025-2026 Legislative Session
```

**Relevance**: Historical tables track session totals (SESSION_TOTAL_AMT).

### Date Field Usage Rules

| Analysis Type | Use These Fields | Example |
|---------------|------------------|---------|
| **Activity Period** | FROM_DATE, THRU_DATE | "Show all Q1 2024 payments" |
| **Filing Compliance** | FILING_DATE, SIG_DATE | "Check late filings" |
| **Registration Status** | EFF_DATE | "When did firm register?" |
| **Specific Transactions** | EXPN_DATE, CTRIB_DATE | "When was contribution made?" |

**Business Rule**: Always use FROM_DATE and THRU_DATE for time-series analysis of lobbying activity.

---

## Amount Calculation Rules

### Period Total (PER_TOTAL) Rules

**Business Rule**: PER_TOTAL represents the amount for the current reporting period only.

```
Q1 2024: PER_TOTAL = $50,000 (Jan-Mar activity)
Q2 2024: PER_TOTAL = $60,000 (Apr-Jun activity)
Q3 2024: PER_TOTAL = $55,000 (Jul-Sep activity)
Q4 2024: PER_TOTAL = $65,000 (Oct-Dec activity)

Annual Total = Sum of all PER_TOTAL = $230,000
```

### Cumulative Total (CUM_TOTAL) Rules

**Business Rule**: CUM_TOTAL is a running total within the legislative session.

```
Q1 2024: CUM_TOTAL = $50,000
Q2 2024: CUM_TOTAL = $110,000 ($50K + $60K)
Q3 2024: CUM_TOTAL = $165,000 ($110K + $55K)
Q4 2024: CUM_TOTAL = $230,000 ($165K + $65K)
```

**Warning**: CUM_TOTAL is complicated by:
- Amendments (may recalculate cumulative)
- Session boundaries (resets every 2 years)
- Data quality issues (manual entry errors)

**Recommendation**: Calculate your own cumulative totals from PER_TOTAL rather than trusting CUM_TOTAL.

### Aggregation Rules

**For accurate totals**:
```sql
-- Correct aggregation pattern
SELECT
    emplr_naml,
    EXTRACT(YEAR FROM from_date) AS year,
    SUM(per_total) AS annual_total
FROM lpay_cd
WHERE amend_id = (SELECT MAX(amend_id) FROM lpay_cd p2 WHERE p2.filing_id = lpay_cd.filing_id)
GROUP BY emplr_naml, EXTRACT(YEAR FROM from_date)
```

**Business Rule**: Always aggregate on PER_TOTAL, not CUM_TOTAL.

---

## Registration vs. Disclosure Rules

### Registration Filing Rules

**Purpose**: Establish identity and authorization to lobby

**Timing**:
- Must be filed BEFORE lobbying activity begins
- Renewed annually or when changes occur

**Content**:
- Entity information (name, address, contacts)
- Authorization relationships (who can lobby for whom)
- Ethics training certification
- Lobbying interests/topics

**Tables**: CVR_REGISTRATION_CD, LEMP_CD, LOBBY_AMENDMENTS_CD

### Disclosure Filing Rules

**Purpose**: Report actual lobbying activity and expenditures

**Timing**:
- Quarterly (due by end of month following quarter)
- Covers specific date range (FROM_DATE to THRU_DATE)

**Content**:
- Payments made/received (LPAY_CD)
- Activity expenditures (LEXP_CD)
- Campaign contributions (LCCM_CD)
- Payments to other firms (LOTH_CD)

**Tables**: CVR_LOBBY_DISCLOSURE_CD, LPAY_CD, LEXP_CD, LCCM_CD, LOTH_CD

### Relationship Between Registration and Disclosure

**Business Rule**: A valid registration must exist before disclosure filings.

```
Step 1: Register (Form 601/603)
    └── Creates entry in CVR_REGISTRATION_CD
        └── Authorizes lobbying activity

Step 2: Perform lobbying activities
    └── Quarterly throughout the year

Step 3: File disclosure reports (Forms 615/625/635/645)
    └── Creates entries in CVR_LOBBY_DISCLOSURE_CD
        └── Links to schedule tables (LPAY, LEXP, LCCM)
```

---

## Data Validation Rules

### Required Field Validation

**Business Rule**: Certain fields are mandatory (M) and must have values.

| Table | Mandatory Fields |
|-------|------------------|
| FILERS_CD | FILER_ID |
| FILINGS_CD | FILING_ID |
| LPAY_CD | FILING_ID, AMEND_ID, LINE_ITEM |
| LEXP_CD | FILING_ID, AMEND_ID, LINE_ITEM |

### Name Validation Rules

**Business Rule**: Organization names go in NAML only, person names use NAMF + NAML.

```
Organization:
- NAML = "City of Oakland"
- NAMF = NULL

Person:
- NAMF = "John"
- NAML = "Smith"
```

### Amount Validation Rules

**Business Rule**: Amounts should be non-negative (expenditures are positive values).

```sql
-- Validate amounts
SELECT filing_id, line_item, per_total
FROM lpay_cd
WHERE per_total < 0  -- Flag negative amounts as errors
```

### Date Validation Rules

**Business Rule**: Date ranges must be logical.

```sql
-- Validate date ranges
SELECT filing_id
FROM cvr_lobby_disclosure_cd
WHERE from_date > thru_date  -- Invalid: start after end
```

### Sum Validation Rules

**Business Rule**: Detail records should sum to cover page totals (though not always enforced).

```sql
-- Validate payment totals
SELECT
    c.filing_id,
    c.total_amt AS cover_total,
    SUM(p.per_total) AS detail_sum,
    c.total_amt - SUM(p.per_total) AS difference
FROM cvr_lobby_disclosure_cd c
LEFT JOIN lpay_cd p ON c.filing_id = p.filing_id
    AND p.amend_id = (SELECT MAX(amend_id) FROM lpay_cd WHERE filing_id = p.filing_id)
GROUP BY c.filing_id, c.total_amt
HAVING ABS(c.total_amt - SUM(p.per_total)) > 0.01  -- Allow for rounding
```

---

## Query Business Logic Patterns

### Pattern 1: City/County Lobbying Expenditures

**Business Question**: How much did City of Oakland spend on lobbying in 2024?

```sql
SELECT
    p.emplr_naml AS city_name,
    EXTRACT(YEAR FROM c.from_date) AS year,
    SUM(p.per_total) AS total_spent
FROM lpay_cd p
JOIN cvr_lobby_disclosure_cd c ON p.filing_id = c.filing_id AND p.amend_id = c.amend_id
WHERE p.emplr_naml LIKE '%Oakland%'
    AND c.entity_cd = 'LEM'
    AND EXTRACT(YEAR FROM c.from_date) = 2024
    AND p.amend_id = (SELECT MAX(amend_id) FROM lpay_cd WHERE filing_id = p.filing_id)
GROUP BY p.emplr_naml, EXTRACT(YEAR FROM c.from_date)
```

**Business Logic**:
- Query LPAY_CD for payments
- Filter to employer entity (LEM)
- Match on employer name (EMPLR_NAML)
- Use latest amendment only
- Sum PER_TOTAL amounts

### Pattern 2: Top Lobbying Firms by Revenue

**Business Question**: Which lobbying firms received the most money in 2024?

```sql
SELECT
    p.payee_naml AS lobbying_firm,
    COUNT(DISTINCT p.emplr_naml) AS num_clients,
    SUM(p.per_total) AS total_revenue
FROM lpay_cd p
JOIN cvr_lobby_disclosure_cd c ON p.filing_id = c.filing_id AND p.amend_id = c.amend_id
WHERE EXTRACT(YEAR FROM c.from_date) = 2024
    AND p.amend_id = (SELECT MAX(amend_id) FROM lpay_cd WHERE filing_id = p.filing_id)
GROUP BY p.payee_naml
ORDER BY total_revenue DESC
LIMIT 20
```

**Business Logic**:
- Query LPAY_CD for payments
- PAYEE_NAML is the lobbying firm (who was paid)
- Count distinct employers as clients
- Sum all payments received
- Use latest amendments only

### Pattern 3: Lobbying Activity by Topic

**Business Question**: Which issues is City of Oakland lobbying on?

```sql
SELECT
    e.emplr_naml AS employer,
    e.descrip AS lobbying_topic,
    COUNT(*) AS num_contracts
FROM lemp_cd e
JOIN cvr_registration_cd c ON e.filing_id = c.filing_id AND e.amend_id = c.amend_id
WHERE e.emplr_naml LIKE '%Oakland%'
GROUP BY e.emplr_naml, e.descrip
```

**Business Logic**:
- Query LEMP_CD for employer relationships
- DESCRIP field contains lobbying interests
- This is from registration forms (Form 601)

### Pattern 4: Campaign Contributions by Lobbyists

**Business Question**: Which candidates received contributions from lobbyists working for City of Oakland?

```sql
SELECT
    cc.cand_naml AS candidate_name,
    cc.office_cd AS office,
    SUM(cc.ctrib_amt) AS total_contributions
FROM lccm_cd cc
JOIN cvr_lobby_disclosure_cd c ON cc.filing_id = c.filing_id AND cc.amend_id = c.amend_id
JOIN lpay_cd p ON c.filing_id = p.filing_id AND c.amend_id = p.amend_id
WHERE p.emplr_naml LIKE '%Oakland%'
    AND cc.amend_id = (SELECT MAX(amend_id) FROM lccm_cd WHERE filing_id = cc.filing_id)
GROUP BY cc.cand_naml, cc.office_cd
ORDER BY total_contributions DESC
```

**Business Logic**:
- Start with LCCM_CD (contributions)
- Join to LPAY_CD to find which lobbyist firms received payments from Oakland
- Sum contributions made by those firms/lobbyists

### Pattern 5: Trend Analysis Over Time

**Business Question**: How has City of Oakland's lobbying spending changed over time?

```sql
SELECT
    EXTRACT(YEAR FROM c.from_date) AS year,
    EXTRACT(QUARTER FROM c.from_date) AS quarter,
    COUNT(DISTINCT p.payee_naml) AS num_firms_used,
    SUM(p.per_total) AS total_spent
FROM lpay_cd p
JOIN cvr_lobby_disclosure_cd c ON p.filing_id = c.filing_id AND p.amend_id = c.amend_id
WHERE p.emplr_naml LIKE '%Oakland%'
    AND c.entity_cd = 'LEM'
    AND p.amend_id = (SELECT MAX(amend_id) FROM lpay_cd WHERE filing_id = p.filing_id)
GROUP BY EXTRACT(YEAR FROM c.from_date), EXTRACT(QUARTER FROM c.from_date)
ORDER BY year, quarter
```

**Business Logic**:
- Group by year and quarter
- Count distinct firms engaged
- Sum spending per period
- Order chronologically to show trends

---

## Summary: Critical Business Rules

### The Five Commandments of Cal-ACCESS Queries

1. **Always filter to latest AMEND_ID** - Or you'll count amendments as duplicates
2. **Understand entity codes** - LEM pays, FRM gets paid (don't reverse!)
3. **Use correct date fields** - FROM_DATE/THRU_DATE for activity, FILING_DATE for compliance
4. **Aggregate on PER_TOTAL** - Not CUM_TOTAL (too unreliable)
5. **Join through cover pages** - FILING_ID + AMEND_ID must match across tables

### Common Business Logic Errors

| Error | Impact | Solution |
|-------|--------|----------|
| Not filtering to latest amendment | Inflated totals (counts amendments multiple times) | Always use MAX(AMEND_ID) |
| Confusing EMPLR vs PAYEE | Backwards payment data | LEM=payer, FRM=payee |
| Using CUM_TOTAL instead of PER_TOTAL | Incorrect aggregations | Sum PER_TOTAL yourself |
| Wrong date field | Incorrect time periods | Use FROM_DATE/THRU_DATE |
| Missing entity code filter | Wrong entity types in results | Filter on ENTITY_CD |

---

**Document Version**: 1.0
**Last Updated**: November 2025
**Maintained By**: Ca-Lobby Project Team
