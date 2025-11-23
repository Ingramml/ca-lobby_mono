# How to Track Who Cities/Counties Paid to Lobby for Them

## Executive Summary

To track who cities and counties paid for lobbying services in California, use the **LPAY_CD** (Lobbying Payments) table from the CAL-ACCESS database. This table contains payment records showing the employer/client (city/county) and the payee (lobbying firm).

## The Correct Data Structure

### LPAY_CD Table - Key Fields

| Field Name | Description | Example Value |
|------------|-------------|---------------|
| **EMPLR_NAML** | The organization/city/county that HIRED lobbying services (the employer/client) | "CITY OF ALAMEDA" |
| **PAYEE_NAML** | The lobbying firm or individual who RECEIVED the payment | "SHAW YODER ANTWIH SCHMELZER" |
| **PER_TOTAL** | Total payment amount for that period | 50000.00 |
| **FEES_AMT** | Fees portion of payment | 45000.00 |
| **REIMB_AMT** | Reimbursements portion | 3000.00 |
| **ADVAN_AMT** | Advances portion | 2000.00 |
| **CUM_TOTAL** | Cumulative total over time | 125000.00 |

### Understanding the Relationship

**Think of it this way:**
- **EMPLR_NAML** = Who is PAYING (the client/city/county)
- **PAYEE_NAML** = Who is GETTING PAID (the lobbying firm)

This is NOT the same as:
- ❌ FIRM_NAME in CVR_LOBBY_DISCLOSURE_CD (this is who filed the form)
- ❌ EMPLOYER_NAME in LEMP_CD (this tracks employer-lobbyist relationships, not payments)

## The Correct Query Pattern

### For Cities:

```sql
SELECT
    pay.EMPLR_NAML as city_name,           -- The city
    pay.PAYEE_NAML as lobbying_firm,       -- Who they paid
    SUM(CAST(pay.PER_TOTAL AS FLOAT64)) as total_amount
FROM `ca-lobby.ca_lobby.lpay_cd` pay
JOIN `ca-lobby.ca_lobby.cvr_lobby_disclosure_cd` d
    ON pay.FILING_ID = d.FILING_ID
    AND pay.AMEND_ID = d.AMEND_ID
WHERE pay.PAYEE_NAML IS NOT NULL
  AND pay.PER_TOTAL IS NOT NULL
  AND CAST(pay.PER_TOTAL AS FLOAT64) > 0
  AND d.RPT_DATE_DATE IS NOT NULL
  AND EXTRACT(YEAR FROM d.RPT_DATE_DATE) = 2025
  AND (
    UPPER(pay.EMPLR_NAML) LIKE '%CITY OF%'
    OR UPPER(pay.EMPLR_NAML) LIKE '%LEAGUE%CITIES%'
  )
GROUP BY city_name, lobbying_firm
ORDER BY total_amount DESC
```

### For Counties:

```sql
SELECT
    pay.EMPLR_NAML as county_name,         -- The county
    pay.PAYEE_NAML as lobbying_firm,       -- Who they paid
    SUM(CAST(pay.PER_TOTAL AS FLOAT64)) as total_amount
FROM `ca-lobby.ca_lobby.lpay_cd` pay
JOIN `ca-lobby.ca_lobby.cvr_lobby_disclosure_cd` d
    ON pay.FILING_ID = d.FILING_ID
    AND pay.AMEND_ID = d.AMEND_ID
WHERE pay.PAYEE_NAML IS NOT NULL
  AND pay.PER_TOTAL IS NOT NULL
  AND CAST(pay.PER_TOTAL AS FLOAT64) > 0
  AND d.RPT_DATE_DATE IS NOT NULL
  AND EXTRACT(YEAR FROM d.RPT_DATE_DATE) = 2025
  AND (
    UPPER(pay.EMPLR_NAML) LIKE '%COUNTY%'
    OR UPPER(pay.EMPLR_NAML) LIKE '%CSAC%'
    OR UPPER(pay.EMPLR_NAML) LIKE '%ASSOCIATION OF COUNTIES%'
  )
GROUP BY county_name, lobbying_firm
ORDER BY total_amount DESC
```

## Common Mistakes to Avoid

### ❌ Mistake 1: Using FIRM_NAME from CVR_LOBBY_DISCLOSURE_CD

**Wrong:**
```sql
SELECT p.FIRM_NAME as city_name
FROM `ca-lobby.ca_lobby.cvr_lobby_disclosure_cd` p
WHERE UPPER(p.FIRM_NAME) LIKE '%CITY OF%'
```

**Why it's wrong:** FIRM_NAME is who FILED the lobbying disclosure form, not necessarily who paid or who got paid.

### ❌ Mistake 2: Trying to use non-existent PAYEE_NAME field

**Wrong:**
```sql
SELECT pay.PAYEE_NAME as recipient
FROM `ca-lobby.ca_lobby.lpay_cd` pay
```

**Why it's wrong:** The field is called **PAYEE_NAML** (payee name last), not PAYEE_NAME.

### ❌ Mistake 3: Using LEMP_CD for payment tracking

**Wrong:**
```sql
SELECT emp.EMPLOYER_NAME, cvr.FIRM_NAME
FROM `ca-lobby.ca_lobby.lemp_cd` emp
JOIN `ca-lobby.ca_lobby.cvr_lobby_disclosure_cd` cvr
```

**Why it's wrong:** LEMP_CD tracks employer-lobbyist relationships, not actual payment amounts.

## The Forms and Filing Process

### How Cities/Counties File:

1. **Cities/counties file Form 635** (Report of Lobbyist Employer)
   - This is a quarterly report
   - They file as the "employer" or "client"

2. **Payment data goes into LPAY_CD**
   - Schedule F635P3A contains payment information
   - Each payment has:
     - Who paid (EMPLR_NAML = the city/county)
     - Who received payment (PAYEE_NAML = the lobbying firm)
     - How much (PER_TOTAL, FEES_AMT, etc.)

3. **Cover page goes into CVR_LOBBY_DISCLOSURE_CD**
   - Contains FILING_ID that links to payment records
   - Contains reporting dates (FROM_DATE, THRU_DATE, RPT_DATE_DATE)
   - Has AMEND_ID for tracking amendments

## Real-World Example

Let's say the **City of Sacramento** paid **Governmental Advocates** $75,000 in Q1 2025:

### How it appears in the database:

**CVR_LOBBY_DISCLOSURE_CD** (Cover page)
- FILING_ID: 12345678
- FIRM_NAME: "CITY OF SACRAMENTO" (who filed)
- RPT_DATE_DATE: 2025-04-30
- AMEND_ID: 0

**LPAY_CD** (Payment record)
- FILING_ID: 12345678 (links to cover page)
- AMEND_ID: 0
- **EMPLR_NAML: "CITY OF SACRAMENTO"** (who paid)
- **PAYEE_NAML: "GOVERNMENTAL ADVOCATES"** (who got paid)
- **PER_TOTAL: 75000.00** (amount)
- FEES_AMT: 70000.00
- REIMB_AMT: 5000.00

### To find this payment:

```sql
SELECT
    pay.EMPLR_NAML,      -- Returns: "CITY OF SACRAMENTO"
    pay.PAYEE_NAML,      -- Returns: "GOVERNMENTAL ADVOCATES"
    pay.PER_TOTAL        -- Returns: 75000.00
FROM `ca-lobby.ca_lobby.lpay_cd` pay
WHERE pay.FILING_ID = 12345678
```

## Implementation in Dashboard

The California Lobbying Dashboard now uses this correct approach in two endpoints:

### 1. Top City Recipients
**Endpoint:** `/api/analytics?type=top_city_recipients`

**Returns:** Top 10 lobbying firms that received the most money from cities in 2025

**Query logic:**
- Filters LPAY_CD where EMPLR_NAML contains "CITY OF" or "LEAGUE%CITIES"
- Groups by PAYEE_NAML (the recipient)
- Sums PER_TOTAL (payment amounts)

### 2. Top County Recipients
**Endpoint:** `/api/analytics?type=top_county_recipients`

**Returns:** Top 10 lobbying firms that received the most money from counties in 2025

**Query logic:**
- Filters LPAY_CD where EMPLR_NAML contains "COUNTY" or "CSAC" or "ASSOCIATION OF COUNTIES"
- Groups by PAYEE_NAML (the recipient)
- Sums PER_TOTAL (payment amounts)

## Field Naming Conventions

CAL-ACCESS uses abbreviated field name suffixes:

| Suffix | Meaning | Example Field |
|--------|---------|---------------|
| _NAML | Name Last | EMPLR_NAML, PAYEE_NAML |
| _NAMF | Name First | EMPLR_NAMF, PAYEE_NAMF |
| _CITY | City | EMPLR_CITY, PAYEE_CITY |
| _ST | State | EMPLR_ST, PAYEE_ST |
| _ZIP4 | ZIP Code | EMPLR_ZIP4, PAYEE_ZIP4 |
| _PHON | Phone | EMPLR_PHON |
| _AMT | Amount | FEES_AMT, REIMB_AMT, ADVAN_AMT |
| _ID | Identifier | FILING_ID, FILER_ID, EMPLR_ID |
| _CD | Code/Table | LPAY_CD, LEXP_CD, LEMP_CD |

## Additional Analysis Options

### Get payment breakdown by type:
```sql
SELECT
    pay.PAYEE_NAML as firm,
    SUM(CAST(pay.FEES_AMT AS FLOAT64)) as total_fees,
    SUM(CAST(pay.REIMB_AMT AS FLOAT64)) as total_reimbursements,
    SUM(CAST(pay.ADVAN_AMT AS FLOAT64)) as total_advances,
    SUM(CAST(pay.PER_TOTAL AS FLOAT64)) as total_all
FROM `ca-lobby.ca_lobby.lpay_cd` pay
WHERE UPPER(pay.EMPLR_NAML) LIKE '%CITY OF%'
GROUP BY firm
```

### Track payments over time:
```sql
SELECT
    EXTRACT(QUARTER FROM d.RPT_DATE_DATE) as quarter,
    pay.PAYEE_NAML as firm,
    SUM(CAST(pay.PER_TOTAL AS FLOAT64)) as amount
FROM `ca-lobby.ca_lobby.lpay_cd` pay
JOIN `ca-lobby.ca_lobby.cvr_lobby_disclosure_cd` d
    ON pay.FILING_ID = d.FILING_ID
WHERE UPPER(pay.EMPLR_NAML) LIKE '%CITY OF%'
  AND EXTRACT(YEAR FROM d.RPT_DATE_DATE) = 2025
GROUP BY quarter, firm
ORDER BY quarter, amount DESC
```

### Find which specific cities paid whom:
```sql
SELECT
    pay.EMPLR_NAML as city,
    pay.PAYEE_NAML as lobbying_firm,
    COUNT(*) as payment_count,
    SUM(CAST(pay.PER_TOTAL AS FLOAT64)) as total_amount
FROM `ca-lobby.ca_lobby.lpay_cd` pay
JOIN `ca-lobby.ca_lobby.cvr_lobby_disclosure_cd` d
    ON pay.FILING_ID = d.FILING_ID
WHERE UPPER(pay.EMPLR_NAML) LIKE '%CITY OF%'
  AND EXTRACT(YEAR FROM d.RPT_DATE_DATE) = 2025
GROUP BY city, lobbying_firm
ORDER BY total_amount DESC
```

## Summary

**The key insight:** In LPAY_CD, use **EMPLR_NAML** to identify the city/county client and **PAYEE_NAML** to identify who received their money. Join to CVR_LOBBY_DISCLOSURE_CD for reporting dates and other metadata.

This approach correctly tracks the flow of money FROM cities/counties TO lobbying firms and consultants.

---

**Document Created:** 2025-11-20
**Author:** California Lobbying Dashboard Team
**Status:** Production Implementation Complete
