# SQL Queries for ALAMEDA-Related Lobbying Organizations

## Overview
These queries search for all organizations containing "ALAMEDA" that either:
1. Received money to lobby (lobbying firms, lobbyists)
2. Spent money on lobbying (employers, clients, coalitions)
3. Are membership organizations involved in lobbying

All queries use FILING_ID to track the organization's activity.

---

## Table 1: CVR_LOBBY_DISCLOSURE_CD
**Purpose:** Find all lobbying disclosure filings involving ALAMEDA organizations

```sql
-- Find all disclosure filings where filer name contains ALAMEDA
SELECT 
    FILING_ID,
    FILER_ID,
    FILER_NAML as FILER_LAST_NAME,
    FILER_NAMF as FILER_FIRST_NAME,
    ENTITY_CD,
    FORM_TYPE,
    FROM_DATE,
    THRU_DATE,
    FIRM_NAME,
    RPT_DATE
FROM CVR_LOBBY_DISCLOSURE_CD
WHERE UPPER(FILER_NAML) LIKE '%ALAMEDA%'
   OR UPPER(FIRM_NAME) LIKE '%ALAMEDA%';

-- Find filings where firm/employer/coalition name contains ALAMEDA
SELECT 
    FILING_ID,
    FILER_ID,
    FIRM_ID,
    FIRM_NAME,
    FIRM_CITY,
    FIRM_ST,
    ENTITY_CD,
    FORM_TYPE,
    FROM_DATE,
    THRU_DATE
FROM CVR_LOBBY_DISCLOSURE_CD
WHERE UPPER(FIRM_NAME) LIKE '%ALAMEDA%';
```

---

## Table 2: CVR_REGISTRATION_CD
**Purpose:** Find all lobbying registration records for ALAMEDA organizations

```sql
-- Find all registrations where filer name contains ALAMEDA
SELECT 
    FILING_ID,
    FILER_ID,
    FILER_NAML as FILER_LAST_NAME,
    FILER_NAMF as FILER_FIRST_NAME,
    ENTITY_CD,
    FORM_TYPE,
    FIRM_NAME,
    A_T_FIRM as AUTHORIZED_FIRM,
    DATE_QUAL as DATE_QUALIFIED,
    RPT_DATE
FROM CVR_REGISTRATION_CD
WHERE UPPER(FILER_NAML) LIKE '%ALAMEDA%'
   OR UPPER(FIRM_NAME) LIKE '%ALAMEDA%'
   OR UPPER(A_T_FIRM) LIKE '%ALAMEDA%';

-- Find all registrations where employer/firm name contains ALAMEDA
SELECT 
    FILING_ID,
    FILER_ID,
    FIRM_NAME,
    ENTITY_CD,
    FORM_TYPE,
    DATE_QUAL,
    FIRM_CITY,
    FIRM_ST,
    FIRM_ZIP4
FROM CVR_REGISTRATION_CD
WHERE UPPER(FIRM_NAME) LIKE '%ALAMEDA%';
```

---

## Table 3: LEMP_CD
**Purpose:** Find lobbyist employer relationships involving ALAMEDA

```sql
-- Find all employer records where employer name contains ALAMEDA
SELECT 
    FILING_ID,
    FILER_ID,
    AGCY_NAML as EMPLOYER_LAST_NAME,
    AGCY_NAMF as EMPLOYER_FIRST_NAME,
    AMEND_ID,
    REC_TYPE,
    FORM_TYPE
FROM LEMP_CD
WHERE UPPER(AGCY_NAML) LIKE '%ALAMEDA%'
   OR UPPER(AGCY_NAMF) LIKE '%ALAMEDA%';
```

---

## Table 4: LPAY_CD
**Purpose:** Find all payments made or received by ALAMEDA organizations

```sql
-- Find payments where payee contains ALAMEDA (organizations receiving money)
SELECT 
    FILING_ID,
    FILER_ID,
    PAYEE_NAML as PAYEE_LAST_NAME,
    PAYEE_NAMF as PAYEE_FIRST_NAME,
    AMOUNT,
    CUM_YTD as CUMULATIVE_YTD,
    AMEND_ID,
    BAKREF_TID as TRANSACTION_ID,
    FORM_TYPE
FROM LPAY_CD
WHERE UPPER(PAYEE_NAML) LIKE '%ALAMEDA%'
   OR UPPER(PAYEE_NAMF) LIKE '%ALAMEDA%';

-- Find all payments related to ALAMEDA (summary by filing)
SELECT 
    FILING_ID,
    FILER_ID,
    COUNT(*) as PAYMENT_COUNT,
    SUM(AMOUNT) as TOTAL_AMOUNT,
    SUM(CUM_YTD) as TOTAL_YTD
FROM LPAY_CD
WHERE UPPER(PAYEE_NAML) LIKE '%ALAMEDA%'
   OR UPPER(PAYEE_NAMF) LIKE '%ALAMEDA%'
GROUP BY FILING_ID, FILER_ID;
```

---

## Table 5: LEXP_CD
**Purpose:** Find lobbying expenditures by or for ALAMEDA organizations

```sql
-- Find expenditures where payee contains ALAMEDA
SELECT 
    FILING_ID,
    FILER_ID,
    PAYEE_NAML as PAYEE_LAST_NAME,
    PAYEE_NAMF as PAYEE_FIRST_NAME,
    AMOUNT,
    EXPN_DSCR as EXPENSE_DESCRIPTION,
    AMEND_ID,
    BAKREF_TID as TRANSACTION_ID
FROM LEXP_CD
WHERE UPPER(PAYEE_NAML) LIKE '%ALAMEDA%'
   OR UPPER(PAYEE_NAMF) LIKE '%ALAMEDA%'
   OR UPPER(EXPN_DSCR) LIKE '%ALAMEDA%';

-- Summary of expenditures related to ALAMEDA
SELECT 
    FILING_ID,
    FILER_ID,
    COUNT(*) as EXPENDITURE_COUNT,
    SUM(AMOUNT) as TOTAL_EXPENDITURES
FROM LEXP_CD
WHERE UPPER(PAYEE_NAML) LIKE '%ALAMEDA%'
   OR UPPER(PAYEE_NAMF) LIKE '%ALAMEDA%'
GROUP BY FILING_ID, FILER_ID;
```

---

## Table 6: LOTH_CD
**Purpose:** Find other lobbying payments involving ALAMEDA

```sql
-- Find other payments where payee contains ALAMEDA
SELECT 
    FILING_ID,
    FILER_ID,
    PAYEE_NAML as PAYEE_LAST_NAME,
    PAYEE_NAMF as PAYEE_FIRST_NAME,
    AMOUNT,
    AMEND_ID,
    BAKREF_TID as TRANSACTION_ID
FROM LOTH_CD
WHERE UPPER(PAYEE_NAML) LIKE '%ALAMEDA%'
   OR UPPER(PAYEE_NAMF) LIKE '%ALAMEDA%';
```

---

## Table 7: LCCM_CD
**Purpose:** Find campaign contributions by ALAMEDA lobbying entities

```sql
-- Find campaign contributions where contributor contains ALAMEDA
SELECT 
    FILING_ID,
    FILER_ID,
    CMTE_ID as COMMITTEE_ID,
    PAYOR_NAML as CONTRIBUTOR_LAST_NAME,
    PAYOR_NAMF as CONTRIBUTOR_FIRST_NAME,
    AMOUNT,
    CTRIB_DATE as CONTRIBUTION_DATE,
    AMEND_ID
FROM LCCM_CD
WHERE UPPER(PAYOR_NAML) LIKE '%ALAMEDA%'
   OR UPPER(PAYOR_NAMF) LIKE '%ALAMEDA%';

-- Summary of contributions by ALAMEDA entities
SELECT 
    FILING_ID,
    FILER_ID,
    COUNT(*) as CONTRIBUTION_COUNT,
    SUM(AMOUNT) as TOTAL_CONTRIBUTIONS
FROM LCCM_CD
WHERE UPPER(PAYOR_NAML) LIKE '%ALAMEDA%'
   OR UPPER(PAYOR_NAMF) LIKE '%ALAMEDA%'
GROUP BY FILING_ID, FILER_ID;
```

---

## Table 8: LATT_CD
**Purpose:** Find payment attachments for ALAMEDA organizations

```sql
-- Find attachments related to ALAMEDA
SELECT 
    FILING_ID,
    FILER_ID,
    AMEND_ID,
    LINE_ITEM,
    REC_TYPE,
    FORM_TYPE
FROM LATT_CD
WHERE FILING_ID IN (
    SELECT DISTINCT FILING_ID 
    FROM CVR_LOBBY_DISCLOSURE_CD 
    WHERE UPPER(FIRM_NAME) LIKE '%ALAMEDA%'
       OR UPPER(FILER_NAML) LIKE '%ALAMEDA%'
);
```

---

## Table 9: LOBBY_AMENDMENTS_CD
**Purpose:** Find amendments to registrations for ALAMEDA organizations

```sql
-- Find all amendments for ALAMEDA organizations
SELECT 
    FILING_ID,
    FILER_ID,
    AMEND_ID,
    REC_TYPE,
    FORM_TYPE,
    EXEC_DATE as EXECUTION_DATE
FROM LOBBY_AMENDMENTS_CD
WHERE FILING_ID IN (
    SELECT DISTINCT FILING_ID 
    FROM CVR_REGISTRATION_CD 
    WHERE UPPER(FIRM_NAME) LIKE '%ALAMEDA%'
       OR UPPER(FILER_NAML) LIKE '%ALAMEDA%'
);
```

---

## Supporting Tables

### FILERS_CD
**Purpose:** Find all ALAMEDA filers in master registry

```sql
-- Find all filers with ALAMEDA in name
SELECT 
    FILER_ID,
    FILER_NAML as LAST_NAME,
    FILER_NAMF as FIRST_NAME,
    FILER_TYPE,
    STATUS,
    EFFECT_DT as EFFECTIVE_DATE,
    XREF_FILER_ID
FROM FILERS_CD
WHERE UPPER(FILER_NAML) LIKE '%ALAMEDA%';

-- Get filer type details
SELECT 
    f.FILER_ID,
    f.FILER_NAML as LAST_NAME,
    f.FILER_NAMF as FIRST_NAME,
    ft.FILER_TYPE,
    ft.DESCRIPTION
FROM FILERS_CD f
JOIN FILER_TO_FILER_TYPE_CD ftf ON f.FILER_ID = ftf.FILER_ID
JOIN FILER_TYPES_CD ft ON ftf.FILER_TYPE = ft.FILER_TYPE
WHERE UPPER(f.FILER_NAML) LIKE '%ALAMEDA%';
```

---

### FILER_FILINGS_CD
**Purpose:** Get all filings for ALAMEDA filers

```sql
-- Find all filings by ALAMEDA filers
SELECT 
    ff.FILING_ID,
    ff.FILER_ID,
    ff.PERIOD_ID,
    ff.FORM_ID,
    f.FILER_NAML as FILER_NAME
FROM FILER_FILINGS_CD ff
JOIN FILERS_CD f ON ff.FILER_ID = f.FILER_ID
WHERE UPPER(f.FILER_NAML) LIKE '%ALAMEDA%';
```

---

### FILER_ADDRESS_CD
**Purpose:** Find addresses for ALAMEDA organizations

```sql
-- Find addresses for ALAMEDA filers
SELECT 
    fa.FILER_ID,
    f.FILER_NAML as FILER_NAME,
    fa.ADRID as ADDRESS_ID,
    fa.CITY,
    fa.ST as STATE,
    fa.ZIP4,
    fa.PHON as PHONE,
    fa.EMAIL
FROM FILER_ADDRESS_CD fa
JOIN FILERS_CD f ON fa.FILER_ID = f.FILER_ID
WHERE UPPER(f.FILER_NAML) LIKE '%ALAMEDA%'
   OR UPPER(fa.CITY) LIKE '%ALAMEDA%';
```

---

### NAMES_CD
**Purpose:** Find name variations for ALAMEDA entities

```sql
-- Find all name records containing ALAMEDA
SELECT 
    NAMID as NAME_ID,
    NAML as LAST_NAME,
    NAMF as FIRST_NAME,
    NAMT as TITLE,
    NAMS as SUFFIX
FROM NAMES_CD
WHERE UPPER(NAML) LIKE '%ALAMEDA%'
   OR UPPER(NAMF) LIKE '%ALAMEDA%';
```

---

## Comprehensive Queries

### Master Query: All ALAMEDA Organizations That Received Money to Lobby

```sql
-- Organizations that received money as lobbying firms or lobbyists
SELECT DISTINCT
    'LPAY_CD' as SOURCE_TABLE,
    lp.FILING_ID,
    lp.FILER_ID,
    f.FILER_NAML as ORGANIZATION_NAME,
    'RECEIVED_PAYMENT' as TRANSACTION_TYPE,
    SUM(lp.AMOUNT) as TOTAL_AMOUNT,
    COUNT(*) as TRANSACTION_COUNT
FROM LPAY_CD lp
JOIN FILERS_CD f ON lp.FILER_ID = f.FILER_ID
WHERE UPPER(lp.PAYEE_NAML) LIKE '%ALAMEDA%'
   OR UPPER(f.FILER_NAML) LIKE '%ALAMEDA%'
GROUP BY lp.FILING_ID, lp.FILER_ID, f.FILER_NAML

UNION ALL

-- Organizations registered as lobbying firms
SELECT DISTINCT
    'CVR_REGISTRATION' as SOURCE_TABLE,
    cvr.FILING_ID,
    cvr.FILER_ID,
    cvr.FIRM_NAME as ORGANIZATION_NAME,
    'REGISTERED_FIRM' as TRANSACTION_TYPE,
    NULL as TOTAL_AMOUNT,
    NULL as TRANSACTION_COUNT
FROM CVR_REGISTRATION_CD cvr
WHERE UPPER(cvr.FIRM_NAME) LIKE '%ALAMEDA%'
  AND cvr.ENTITY_CD = 'FRM';
```

---

### Master Query: All ALAMEDA Organizations That Spent Money on Lobbying

```sql
-- Organizations that spent money on lobbyists (employers)
SELECT DISTINCT
    'LPAY_CD' as SOURCE_TABLE,
    lp.FILING_ID,
    lp.FILER_ID,
    f.FILER_NAML as ORGANIZATION_NAME,
    'PAID_FOR_LOBBYING' as TRANSACTION_TYPE,
    SUM(lp.AMOUNT) as TOTAL_SPENT,
    COUNT(*) as PAYMENT_COUNT
FROM LPAY_CD lp
JOIN FILERS_CD f ON lp.FILER_ID = f.FILER_ID
WHERE UPPER(f.FILER_NAML) LIKE '%ALAMEDA%'
GROUP BY lp.FILING_ID, lp.FILER_ID, f.FILER_NAML

UNION ALL

-- Organizations registered as employers/coalitions
SELECT DISTINCT
    'CVR_REGISTRATION' as SOURCE_TABLE,
    cvr.FILING_ID,
    cvr.FILER_ID,
    cvr.FIRM_NAME as ORGANIZATION_NAME,
    'REGISTERED_EMPLOYER' as TRANSACTION_TYPE,
    NULL as TOTAL_SPENT,
    NULL as PAYMENT_COUNT
FROM CVR_REGISTRATION_CD cvr
WHERE UPPER(cvr.FIRM_NAME) LIKE '%ALAMEDA%'
  AND cvr.ENTITY_CD IN ('LEM', 'LCO')

UNION ALL

-- Organizations with lobbying expenditures
SELECT DISTINCT
    'LEXP_CD' as SOURCE_TABLE,
    le.FILING_ID,
    le.FILER_ID,
    f.FILER_NAML as ORGANIZATION_NAME,
    'LOBBYING_EXPENDITURE' as TRANSACTION_TYPE,
    SUM(le.AMOUNT) as TOTAL_SPENT,
    COUNT(*) as PAYMENT_COUNT
FROM LEXP_CD le
JOIN FILERS_CD f ON le.FILER_ID = f.FILER_ID
WHERE UPPER(f.FILER_NAML) LIKE '%ALAMEDA%'
GROUP BY le.FILING_ID, le.FILER_ID, f.FILER_NAML;
```

---

### Complete Activity Report: All ALAMEDA Lobbying Activity

```sql
-- Comprehensive report of all ALAMEDA lobbying activity
WITH alameda_filers AS (
    SELECT DISTINCT FILER_ID, FILER_NAML as NAME
    FROM FILERS_CD
    WHERE UPPER(FILER_NAML) LIKE '%ALAMEDA%'
),
payments_received AS (
    SELECT 
        lp.FILER_ID,
        lp.FILING_ID,
        COUNT(*) as payment_count,
        SUM(lp.AMOUNT) as total_received
    FROM LPAY_CD lp
    WHERE UPPER(lp.PAYEE_NAML) LIKE '%ALAMEDA%'
    GROUP BY lp.FILER_ID, lp.FILING_ID
),
expenditures AS (
    SELECT 
        le.FILER_ID,
        le.FILING_ID,
        COUNT(*) as expenditure_count,
        SUM(le.AMOUNT) as total_spent
    FROM LEXP_CD le
    WHERE UPPER(le.PAYEE_NAML) LIKE '%ALAMEDA%'
       OR le.FILER_ID IN (SELECT FILER_ID FROM alameda_filers)
    GROUP BY le.FILER_ID, le.FILING_ID
),
contributions AS (
    SELECT 
        lc.FILER_ID,
        lc.FILING_ID,
        COUNT(*) as contribution_count,
        SUM(lc.AMOUNT) as total_contributions
    FROM LCCM_CD lc
    WHERE UPPER(lc.PAYOR_NAML) LIKE '%ALAMEDA%'
       OR lc.FILER_ID IN (SELECT FILER_ID FROM alameda_filers)
    GROUP BY lc.FILER_ID, lc.FILING_ID
)
SELECT 
    af.FILER_ID,
    af.NAME as ORGANIZATION_NAME,
    cvr.FILING_ID,
    cvr.ENTITY_CD,
    cvr.FROM_DATE,
    cvr.THRU_DATE,
    COALESCE(pr.payment_count, 0) as PAYMENTS_RECEIVED_COUNT,
    COALESCE(pr.total_received, 0) as TOTAL_MONEY_RECEIVED,
    COALESCE(ex.expenditure_count, 0) as EXPENDITURES_COUNT,
    COALESCE(ex.total_spent, 0) as TOTAL_MONEY_SPENT,
    COALESCE(co.contribution_count, 0) as CONTRIBUTIONS_COUNT,
    COALESCE(co.total_contributions, 0) as TOTAL_CONTRIBUTIONS
FROM alameda_filers af
LEFT JOIN CVR_LOBBY_DISCLOSURE_CD cvr ON af.FILER_ID = cvr.FILER_ID
LEFT JOIN payments_received pr ON cvr.FILING_ID = pr.FILING_ID
LEFT JOIN expenditures ex ON cvr.FILING_ID = ex.FILING_ID
LEFT JOIN contributions co ON cvr.FILING_ID = co.FILING_ID
ORDER BY af.NAME, cvr.FROM_DATE;
```

---

## Entity Type Filter Queries

### Query by Entity Type: Lobbying Firms (FRM)
```sql
SELECT DISTINCT
    cvr.FILING_ID,
    cvr.FILER_ID,
    cvr.FIRM_NAME,
    cvr.ENTITY_CD,
    'LOBBYING_FIRM' as ENTITY_TYPE
FROM CVR_REGISTRATION_CD cvr
WHERE UPPER(cvr.FIRM_NAME) LIKE '%ALAMEDA%'
  AND cvr.ENTITY_CD = 'FRM';
```

### Query by Entity Type: Lobbyist Employers (LEM)
```sql
SELECT DISTINCT
    cvr.FILING_ID,
    cvr.FILER_ID,
    cvr.FIRM_NAME,
    cvr.ENTITY_CD,
    'EMPLOYER' as ENTITY_TYPE
FROM CVR_REGISTRATION_CD cvr
WHERE UPPER(cvr.FIRM_NAME) LIKE '%ALAMEDA%'
  AND cvr.ENTITY_CD = 'LEM';
```

### Query by Entity Type: Lobbying Coalitions (LCO)
```sql
SELECT DISTINCT
    cvr.FILING_ID,
    cvr.FILER_ID,
    cvr.FIRM_NAME,
    cvr.ENTITY_CD,
    'COALITION' as ENTITY_TYPE
FROM CVR_REGISTRATION_CD cvr
WHERE UPPER(cvr.FIRM_NAME) LIKE '%ALAMEDA%'
  AND cvr.ENTITY_CD = 'LCO';
```

### Query by Entity Type: Individual Lobbyists (LBY)
```sql
SELECT DISTINCT
    cvr.FILING_ID,
    cvr.FILER_ID,
    cvr.FILER_NAML as LAST_NAME,
    cvr.FILER_NAMF as FIRST_NAME,
    cvr.ENTITY_CD,
    'INDIVIDUAL_LOBBYIST' as ENTITY_TYPE
FROM CVR_REGISTRATION_CD cvr
WHERE UPPER(cvr.FILER_NAML) LIKE '%ALAMEDA%'
  AND cvr.ENTITY_CD = 'LBY';
```

---

## Time-Based Queries

### Current Year Activity
```sql
SELECT 
    cvr.FILING_ID,
    cvr.FILER_ID,
    f.FILER_NAML as ORGANIZATION,
    cvr.FROM_DATE,
    cvr.THRU_DATE,
    cvr.ENTITY_CD
FROM CVR_LOBBY_DISCLOSURE_CD cvr
JOIN FILERS_CD f ON cvr.FILER_ID = f.FILER_ID
WHERE UPPER(f.FILER_NAML) LIKE '%ALAMEDA%'
  AND YEAR(cvr.FROM_DATE) = YEAR(GETDATE());
```

### Historical Activity (Last 5 Years)
```sql
SELECT 
    cvr.FILING_ID,
    cvr.FILER_ID,
    f.FILER_NAML as ORGANIZATION,
    cvr.FROM_DATE,
    cvr.THRU_DATE,
    cvr.ENTITY_CD,
    YEAR(cvr.FROM_DATE) as YEAR
FROM CVR_LOBBY_DISCLOSURE_CD cvr
JOIN FILERS_CD f ON cvr.FILER_ID = f.FILER_ID
WHERE UPPER(f.FILER_NAML) LIKE '%ALAMEDA%'
  AND cvr.FROM_DATE >= DATEADD(YEAR, -5, GETDATE())
ORDER BY cvr.FROM_DATE DESC;
```

---

## Notes on Query Usage

### Search Pattern Tips
- `UPPER()` function ensures case-insensitive search
- `%ALAMEDA%` matches "ALAMEDA" anywhere in the text
- Can modify to `'ALAMEDA%'` to match only names starting with ALAMEDA
- Can modify to `'%ALAMEDA'` to match only names ending with ALAMEDA

### Common Variations to Search
You may want to search for variations:
```sql
WHERE UPPER(field) LIKE '%ALAMEDA%'
   OR UPPER(field) LIKE '%ALAMEDA COUNTY%'
   OR UPPER(field) LIKE '%CITY OF ALAMEDA%'
   OR UPPER(field) LIKE '%ALAMEDA CITY%'
```

### Performance Considerations
- These queries search text fields, which can be slow on large tables
- Consider adding indexes on name fields if running frequently
- Use `DISTINCT` to avoid duplicate records
- Limit results with `TOP` or `LIMIT` clauses for initial testing

### Data Quality Notes
- Some organization names may be abbreviated
- Check for spelling variations
- Some records may have incomplete name data
- Always verify FILING_ID to ensure you're getting complete filing information

---

**Document Version:** 1.0  
**Last Updated:** October 24, 2025  
**Purpose:** Find all lobbying organizations containing "ALAMEDA" in CAL-ACCESS database
