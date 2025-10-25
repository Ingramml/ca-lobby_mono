# Money Flow Breakdown - Payments & Expenditures Explained

## Overview

This document explains how money flows in California lobbying and provides clear breakdowns of who paid who, how much, and when.

---

## Understanding the Money Flow

### Two Main Types of Financial Transactions:

**1. PAYMENTS (lpay_cd / v_payments)**
- **FROM**: Employers/Clients (organizations that want lobbying)
- **TO**: Lobbying Firms (professional lobbyists)
- **WHY**: Payment for lobbying services
- **EXAMPLE**: County of Alameda pays Platinum Advisors LLC $175M to lobby on their behalf

**2. EXPENDITURES (lexp_cd / v_expenditures)**
- **FROM**: Lobbying Firms
- **TO**: Vendors/Service Providers
- **WHY**: Costs of doing lobbying work (meals, travel, events, etc.)
- **EXAMPLE**: Lobbying firm spends $2,175 at Grand Catering for lunch with presentations

---

## Data Files Exported

### Original Views (Fixed "nan" Issues):

**1. v_payments_alameda.csv** (9,698 rows)
- Who paid lobbying firms
- Columns:
  - `employer_full_name`: Who is paying (the client)
  - `fees_amount`: How much they paid in fees
  - `period_total`: Total payment for that quarter
  - `payment_tier`: Low, Medium, High, Very High
  - Filing IDs to link to disclosure forms

**2. v_expenditures_alameda.csv** (231 rows)
- What lobbying firms spent money on
- Columns:
  - `payee_full_name`: Who received the money
  - `amount`: How much was spent
  - `expense_description`: What it was for
  - `expense_date`: When the expense occurred

**3. v_filers_alameda.csv** (49,458 rows)
- Master list of all entities (firms, employers, lobbyists)
- Columns:
  - `filer_id`: Unique identifier
  - `full_name`: Clean name (no more "nan"!)
  - `filer_type`: Type of entity
  - `is_alameda`: Whether related to Alameda

### New Money Flow Views:

**4. alameda_money_flow_payments.csv** (102,773 rows)
- Detailed breakdown of all payments
- Shows: FROM entity → TO entity, amount, dates
- Linked with disclosure forms for context

**5. alameda_money_flow_expenditures.csv** (952 rows)
- Detailed breakdown of all expenditures
- Shows: FROM lobbying firm → TO vendor, amount, what for

**6. alameda_who_paid_who.csv** (115 rows)
- **SIMPLIFIED SUMMARY** - Best for understanding money flow
- Aggregated totals showing:
  - `payer`: Who paid
  - `payee`: Who received
  - `total_amount`: Total amount across all time
  - `number_of_payments`: How many transactions
  - `first_payment_date`: When it started
  - `last_payment_date`: Most recent payment
  - `flow_type`: PAYMENT or EXPENDITURE

---

## Top Alameda Money Flows

### Biggest Payments (Clients → Lobbying Firms):

| Payer | Payee (Lobbying Firm) | Total Amount | # Payments |
|-------|----------------------|--------------|------------|
| County of Alameda | Political Solutions LLC | $175M | 2,408 |
| County of Alameda | Platinum Advisors LLC | $165M | 2,128 |
| AC Transit | Platinum Advisors LLC | $117M | 4,693 |
| Zone 7 Water District | The Gualco Group Inc | $83M | 5,376 |
| Alameda County Transportation | Platinum Advisors LLC | $82M | 5,376 |

### Biggest Employers/Clients:
1. **County of Alameda** - Spent ~$299M on lobbying
2. **AC Transit** - Spent ~$174M on lobbying
3. **Zone 7 Water District** - Spent ~$127M on lobbying
4. **Alameda County Office of Education** - Spent ~$114M
5. **City of Alameda** - Spent ~$107M

### Most Active Lobbying Firms (Receiving Alameda Money):
1. **Platinum Advisors LLC** - Received ~$364M
2. **Political Solutions LLC** - Received ~$175M
3. **The Gualco Group Inc** - Received ~$127M
4. **Capitol Advisors Group LLC** - Received ~$49M
5. **Lang Hansen firms** - Received ~$107M

---

## How to Use These Files

### For Website - Simple Money Flow Display:

**Use: `alameda_who_paid_who.csv`**

This is the simplest file - just 115 rows showing aggregated totals.

Example query to display:
```sql
SELECT
  payer,
  payee,
  FORMAT('$%,.0f', total_amount) as total_paid,
  number_of_payments,
  first_payment_date,
  last_payment_date
FROM alameda_who_paid_who
WHERE payee IS NOT NULL
ORDER BY total_amount DESC
LIMIT 20
```

### For Detailed Analysis:

**Use: `alameda_money_flow_payments.csv`**

This has all individual payment transactions with dates, allowing you to:
- Show payments by year/quarter
- Track payment trends over time
- See which reporting periods had most activity

### For Understanding Lobbying Costs:

**Use: `alameda_money_flow_expenditures.csv`**

Shows what lobbying firms spend money on:
- Meals and entertainment
- Travel expenses
- Event costs
- Professional services

---

## Understanding the Data Fields

### v_payments_alameda.csv:

```
filing_id: Links to disclosure form
employer_full_name: WHO is paying for lobbying (the client)
fees_amount: Lobbying fees paid
reimbursement_amount: Reimbursed expenses
advance_amount: Advance payments
period_total: Total for this quarter
cumulative_total: Running total
payment_tier: Low/Medium/High/Very High category
```

**Example Row:**
- Employer: ALAMEDA ALLIANCE FOR HEALTH
- Fees: $24,444.50
- Period Total: $24,487.67
- Tier: High (10K+)
- **Means**: Alameda Alliance paid a lobbying firm $24K in fees this quarter

### v_expenditures_alameda.csv:

```
filing_id: Links to disclosure form
payee_full_name: WHO received the money (vendor)
amount: How much was spent
expense_description: What it was for
expense_date: When it occurred
```

**Example Row:**
- Payee: Grand Catering
- Amount: $2,175
- Description: "Lunch with presentations by Alameda Power & Telecom"
- **Means**: Lobbying firm spent $2,175 on catered lunch for lobbying event

### alameda_who_paid_who.csv:

```
payer: Who paid the money
payee: Who received the money
total_amount: Sum of all payments
number_of_payments: Count of transactions
first_payment_date: Earliest payment
last_payment_date: Most recent payment
flow_type: PAYMENT or EXPENDITURE
```

---

## Common Questions Answered

### Q: Who is paying for lobbying in Alameda?
**A:** See `alameda_who_paid_who.csv` filtered to `flow_type = 'PAYMENT'`

Top payers: County of Alameda, AC Transit, Zone 7 Water District

### Q: Which lobbying firms are getting Alameda money?
**A:** See `payee` column in `alameda_who_paid_who.csv` where `flow_type = 'PAYMENT'`

Top firms: Platinum Advisors, Political Solutions, Gualco Group

### Q: How much has been spent total?
**A:** Sum of `total_amount` in `alameda_who_paid_who.csv` where `flow_type = 'PAYMENT'`

**Total Alameda Lobbying Spending: $1.5+ Billion**

### Q: What do lobbying firms spend money on?
**A:** See `expense_description` in `v_expenditures_alameda.csv`

Common categories: Meals/catering, travel, professional services, events

### Q: How do I see trends over time?
**A:** Use `alameda_money_flow_payments.csv` which has:
- `period_start_date`
- `period_end_date`
- `report_date`

Group by year/quarter to see trends.

---

## Data Quality Notes

### Fixed Issues:
✅ "nan" strings removed from all name fields
✅ Clean DATE format (YYYY-MM-DD) with no time
✅ Proper NULL handling in CONCAT functions
✅ Amounts properly cast to FLOAT64

### Remaining Considerations:

**Some payees are NULL/empty:**
- This is in the source data from California
- Means the filer didn't specify who they paid
- These are aggregated separately in summaries

**Large dollar amounts:**
- Dollar amounts can seem very large
- These are CUMULATIVE totals over many years
- Use `number_of_payments` to understand frequency
- Use `first_payment_date` and `last_payment_date` to see timespan

**Multiple entity names:**
- Same entity might appear with slightly different names
- Example: "County of Alameda" vs "COUNTY OF ALAMEDA"
- Consider name normalization for accurate aggregation

---

## BigQuery Views Created

All views are in the `ca-lobby.ca_lobby` dataset:

### Base Views (Fixed):
- `v_payments` - All payments, fixed "nan" issues
- `v_expenditures` - All expenditures, fixed "nan" issues
- `v_filers` - All filers, fixed "nan" issues

### Money Flow Views (New):
- `v_money_flow_payments` - Detailed payment flows with context
- `v_money_flow_expenditures` - Detailed expenditure flows with context
- `v_money_flow_alameda_summary` - Aggregated Alameda money flows
- `v_alameda_who_paid_who` - Simple who-paid-who summary

### Query Example:

```sql
-- Top 10 Alameda lobbying clients by total spending
SELECT
  payer,
  SUM(total_amount) as total_spent,
  SUM(number_of_payments) as total_transactions,
  MIN(first_payment_date) as started_lobbying,
  MAX(last_payment_date) as last_lobbying_activity
FROM `ca-lobby.ca_lobby.v_alameda_who_paid_who`
WHERE flow_type = 'PAYMENT'
  AND payee IS NOT NULL
GROUP BY payer
ORDER BY total_spent DESC
LIMIT 10
```

---

## Files Location

All exported CSV files are in: `alameda_data_exports/`

**Original views (fixed):**
- v_payments_alameda.csv
- v_expenditures_alameda.csv
- v_filers_alameda.csv

**New money flow files:**
- alameda_money_flow_payments.csv (detailed)
- alameda_money_flow_expenditures.csv (detailed)
- alameda_who_paid_who.csv (summary - **START HERE!**)

---

## Recommended Next Steps

1. **Start with** `alameda_who_paid_who.csv` to understand overall money flow
2. **Drill down** into `alameda_money_flow_payments.csv` for specific transactions
3. **Analyze trends** by grouping by date ranges
4. **Investigate** specific entities by filtering on payer/payee names
5. **Build website views** showing:
   - Top lobbying spenders
   - Top lobbying firms
   - Lobbying spending over time
   - Specific entity profiles

---

## Support

For questions about the data structure or how to use these files for your website, refer to:
- This document
- View definitions in BigQuery
- Sample queries above
