# View Architecture Quick Start Guide

**For immediate implementation of the California Lobbying Database view architecture**

---

## Step 1: Review the Architecture (10 minutes)

Read the main documentation:
```
/Users/michaelingram/Documents/GitHub/CA_lobby_Database/BIGQUERY_VIEW_ARCHITECTURE.md
```

**Key Points:**
- 73 views across 4 layers
- Views provide structured access; exports only for testing
- 50% cost reduction
- 10-100x faster queries

---

## Step 2: Pre-Implementation Checklist

- [ ] BigQuery project access: `ca-lobby.ca_lobby`
- [ ] Permissions: `roles/bigquery.dataEditor` or higher
- [ ] Backup existing queries/exports (if any)
- [ ] Review current CSV export usage patterns
- [ ] Identify which views to materialize first

---

## Step 3: Create Views (Sequential Order)

### Option A: Create All Views at Once (Automated)

```bash
# Execute the complete SQL script
bq query --use_legacy_sql=false < CREATE_ALL_VIEWS.sql
```

### Option B: Create Layer by Layer (Recommended for first deployment)

**Layer 1: Base Views (Required - ~5 minutes)**
```sql
-- Execute each view from CREATE_ALL_VIEWS.sql starting with:
-- v_filers, v_filer_filings, v_filer_addresses, etc.
-- Stop after v_lookup_codes
```

**Layer 2: Integration Views (Critical - ~10 minutes)**
```sql
-- MUST create in this exact order:
-- 1. v_int_filer_complete (many views depend on this)
-- 2. v_int_filer_disclosures
-- 3. v_int_payment_details
-- 4. v_int_payment_with_latest_amendment
-- Then remaining Layer 2 views
```

**Layer 3: Analytical Views (Optional - ~5 minutes)**
```sql
-- Create summary views as needed
-- Start with v_summary_payments_by_year
```

**Layer 4: Filtered Views (Optional - ~3 minutes)**
```sql
-- Create specialized filters
-- Note: Some views are lower priority/optional:
--   ~~v_filter_alameda_filers~~
--   ~~v_filter_alameda_payments~~
--   ~~v_filter_high_value_payments~~
--   ~~v_filter_active_filers~~
```

---

## Step 4: Create Critical Materialized Views

**Note: Data does not need regular updates currently; refresh schedule TBD**

### 1. Payment Details with Latest Amendment (CRITICAL)
```sql
CREATE MATERIALIZED VIEW `ca-lobby.ca_lobby.mv_int_payment_with_latest_amendment`
PARTITION BY DATE(period_start_date)
CLUSTER BY filer_id, reporting_year, payment_tier
AS
SELECT * FROM `ca-lobby.ca_lobby.v_int_payment_with_latest_amendment`;
```

### 2. Complete Filer Profiles (CRITICAL)
```sql
CREATE MATERIALIZED VIEW `ca-lobby.ca_lobby.mv_int_filer_complete`
CLUSTER BY filer_id, status
AS
SELECT * FROM `ca-lobby.ca_lobby.v_int_filer_complete`;
```

### 3. Alameda Payments (If frequently queried)
```sql
CREATE MATERIALIZED VIEW `ca-lobby.ca_lobby.mv_filter_alameda_payments`
PARTITION BY DATE(period_start_date)
CLUSTER BY filer_id, alameda_connection_type
AS
SELECT * FROM `ca-lobby.ca_lobby.v_filter_alameda_payments`;
```

---

## Step 5: Set Up Refresh Schedules

**In BigQuery Console:**

1. Go to **Scheduled Queries**
2. Click **Create Scheduled Query**
3. Set up refresh for materialized views:

```sql
-- Refresh schedule: Will be set at a later date
CALL BQ.REFRESH_MATERIALIZED_VIEW('ca-lobby.ca_lobby.mv_int_payment_with_latest_amendment');
CALL BQ.REFRESH_MATERIALIZED_VIEW('ca-lobby.ca_lobby.mv_int_filer_complete');
```

**Recommended Schedule:**
- **Critical views**: Will be set at a later date
- **Summary views**: Will be set at a later date
- **Network views**: Will be set at a later date

---

## Step 6: Test Critical Queries

### Test 1: Verify Alameda Data (Optional - lower priority)
```sql
-- Note: Alameda-specific views are deprioritized
SELECT COUNT(*) AS alameda_filer_count
FROM `ca-lobby.ca_lobby.v_filter_alameda_filers`;

-- Expected: >0 filers with "ALAMEDA" in name or city
```

### Test 2: Verify Payment Data
```sql
SELECT
  reporting_year,
  COUNT(*) AS payment_count,
  SUM(total_payment_amount) AS total_amount
FROM `ca-lobby.ca_lobby.v_int_payment_with_latest_amendment`
GROUP BY reporting_year
ORDER BY reporting_year DESC
LIMIT 5;

-- Expected: Recent years with payment data
```

### Test 3: Compare with CSV Export (if available)
```sql
-- Count total payments in view
SELECT COUNT(*) FROM `ca-lobby.ca_lobby.v_payments`;

-- Compare with row count in your CSV exports
-- Should match (or view count should be higher if CSV filtered)
```

---

## Step 7: Migrate Your Queries

### Old CSV-Based Workflow:
1. Run export script → Wait 5-10 minutes
2. Download CSV → 1-2 minutes
3. Load into Pandas/Excel → 1-5 minutes
4. Filter/aggregate data → Variable time
5. **Total: 10-20+ minutes per analysis**

### New View-Based Workflow:
1. Query view directly → Instant
2. Results in seconds
3. **Total: <1 minute per analysis**

### Example Migration:

**OLD (CSV):**
```python
import pandas as pd

# Load CSV (slow)
df = pd.read_csv('Alameda_LPAY_CD.csv')

# Filter
alameda_2024 = df[
    (df['FILER_NAML'].str.contains('ALAMEDA')) &
    (df['FROM_DATE'] >= '2024-01-01')
]

# Aggregate
summary = alameda_2024.groupby('FILER_ID')['PERIOD_TOTAL'].sum()
```

**NEW (View):**
```sql
SELECT
  filer_id,
  filer_name,
  SUM(total_payment_amount) AS total_payments
FROM `ca-lobby.ca_lobby.v_filter_alameda_payments`
WHERE reporting_year = 2024
GROUP BY filer_id, filer_name
ORDER BY total_payments DESC;
```

---

## Step 8: Update Documentation

### Update your internal docs with:

**View Quick Reference:**
```
Common Tasks -> View to Use

~~Find Alameda activity        -> v_filter_alameda_payments~~ (lower priority)
Latest payment data          -> v_int_payment_with_latest_amendment
Complete filer info          -> v_int_filer_complete
Year-over-year trends        -> v_summary_yoy_growth
Top lobbying firms           -> v_summary_firm_market_share
Network analysis             -> v_int_network_employer_to_firm
~~High-value transactions      -> v_filter_high_value_payments~~ (lower priority)
Current year only            -> v_filter_current_year
~~Active filers                -> v_filter_active_filers~~ (lower priority)
```

---

## Step 9: CSV Exports

**Note: CSV exports are only for testing purposes**

Views provide structured access to the database. CSV exports should only be used for testing and validation, not as a primary data access method.

---

## Common Queries Cheat Sheet

### Get all Alameda lobbying activity (Optional - lower priority)
```sql
-- Note: Alameda-specific views are deprioritized
SELECT *
FROM `ca-lobby.ca_lobby.v_filter_alameda_payments`
ORDER BY period_start_date DESC;
```

### Top 10 lobbying firms by revenue
```sql
SELECT
  filer_name,
  SUM(total_payment_amount) AS total_revenue,
  COUNT(DISTINCT employer_full_name) AS client_count
FROM `ca-lobby.ca_lobby.v_int_payment_with_latest_amendment`
WHERE filer_organization_type = 'PROVIDER'
GROUP BY filer_name
ORDER BY total_revenue DESC
LIMIT 10;
```

### Payments to specific firm in 2024
```sql
SELECT
  reporting_period,
  employer_full_name AS client,
  total_payment_amount,
  payment_tier
FROM `ca-lobby.ca_lobby.v_int_payment_with_latest_amendment`
WHERE filer_name = 'YOUR FIRM NAME HERE'
  AND reporting_year = 2024
ORDER BY period_start_date DESC;
```

### High-value transactions this quarter (Optional - lower priority)
```sql
-- Note: High-value transaction views are deprioritized
SELECT
  filer_name,
  employer_full_name,
  total_payment_amount,
  reporting_period
FROM `ca-lobby.ca_lobby.v_filter_high_value_payments`
WHERE reporting_year = EXTRACT(YEAR FROM CURRENT_DATE())
  AND reporting_quarter = EXTRACT(QUARTER FROM CURRENT_DATE())
ORDER BY total_payment_amount DESC;
```

### Year-over-year growth
```sql
SELECT
  reporting_year,
  grand_total_payments,
  growth_percent,
  unique_filers
FROM `ca-lobby.ca_lobby.v_summary_yoy_growth`
ORDER BY reporting_year DESC
LIMIT 10;
```

---

## Troubleshooting

### Error: "View not found"
**Solution:** Create views in order (Layer 1 before Layer 2, etc.)

### Error: "Syntax error"
**Solution:** Ensure you're using BigQuery Standard SQL (not Legacy SQL)
```sql
-- At top of query:
#standardSQL
```

### Slow query performance
**Solution:** Materialize the view
```sql
CREATE MATERIALIZED VIEW `ca-lobby.ca_lobby.mv_your_view_name`
AS
SELECT * FROM `ca-lobby.ca_lobby.v_your_view_name`;
```

### Data doesn't match CSV exports
**Solution:** Check amendment handling
- Views include all amendments by default
- Use `v_int_payment_with_latest_amendment` for latest only
- Compare amendment_id in both sources

### Running out of BigQuery quota
**Solution:**
1. Use materialized views (cached results)
2. Add WHERE clauses to filter by date
3. Avoid `SELECT *` - specify needed columns
4. Use `LIMIT` during testing

---

## Performance Optimization Tips

### 1. Always filter by date
```sql
-- Good: Uses partition pruning
WHERE period_start_date >= '2024-01-01'

-- Bad: Full table scan
WHERE reporting_year = 2024  -- (if not partitioned by year)
```

### 2. Use clustered columns in WHERE
```sql
-- Good: Uses clustering
WHERE filer_id = '12345' AND reporting_year = 2024

-- Less optimal: Not clustered
WHERE employer_full_name = 'ABC Corp'
```

### 3. Use materialized views for complex queries
```sql
-- Instead of querying v_int_payment_details repeatedly
-- Query mv_int_payment_with_latest_amendment (materialized)
```

### 4. Limit result size during exploration
```sql
SELECT *
FROM `ca-lobby.ca_lobby.v_int_payment_details`
WHERE reporting_year = 2024
LIMIT 100;  -- Add limit for testing
```

---

## Cost Monitoring

### Check query costs:
```sql
-- In BigQuery Console, after running query:
-- Look at "Bytes processed" in job details
-- Cost = Bytes processed × $5 per TB
```

### Monitor materialized view refresh costs:
```sql
-- BigQuery Console > Scheduled Queries > View History
-- Check "Bytes processed" for each refresh
```

### Set up billing alerts:
1. GCP Console > Billing > Budgets & alerts
2. Set alert at $10/month (or your threshold)
3. Get notified before costs exceed budget

---

## Next Steps After Implementation

**Week 1-2: Parallel Operation**
- Run both CSV exports and views
- Compare results
- Build confidence in views

**Week 3-4: Full Migration**
- Update all queries to use views
- Train team on view usage
- Create custom views for specific needs

**Month 2+: Optimization**
- Materialize additional views based on usage
- Adjust refresh schedules
- Add new analytical views as needed

---

## Support Resources

**Documentation:**
- Main: `BIGQUERY_VIEW_ARCHITECTURE.md`
- SQL Script: `CREATE_ALL_VIEWS.sql`
- This guide: `VIEW_ARCHITECTURE_QUICKSTART.md`

**BigQuery Resources:**
- Standard SQL Reference: https://cloud.google.com/bigquery/docs/reference/standard-sql
- Materialized Views: https://cloud.google.com/bigquery/docs/materialized-views
- Best Practices: https://cloud.google.com/bigquery/docs/best-practices-performance-overview

**Internal:**
- Database Schema: `Documents/California_Lobbying_Tables_Documentation.md`
- Example Queries: `Documents/ALAMEDA_Lobbying_Queries.md`

---

## Success Metrics

Track these to measure success:

- [ ] **Time savings**: Avg query time reduced from 10-20 min to <1 min
- [ ] **Cost reduction**: 50% reduction in data processing costs
- [ ] **Data freshness**: Real-time vs weekly CSV exports
- [ ] **Team satisfaction**: Easier to query, less maintenance
- [ ] **Query accuracy**: No version mismatch issues

---

## Rollback Plan (If Needed)

If critical issues arise:

1. **Keep CSV export scripts** for first 30 days
2. **Don't delete CSV files** immediately
3. **Document issues** encountered
4. **Fix views** rather than rolling back if possible
5. **Only rollback** if data integrity issues found

To rollback:
```bash
# Re-enable CSV export cron jobs
# Resume CSV-based workflows
# Keep views for parallel testing/debugging
```

---

**Estimated Implementation Time:**
- **Reading docs**: 30 minutes
- **Creating views**: 30 minutes
- **Testing**: 30 minutes
- **Migration**: 1-2 hours
- **Total**: 3-4 hours for complete implementation

**ROI Timeframe:**
- Setup cost: $1,600 (one-time)
- Annual savings: $5,875
- **Break-even: 3.6 months**

---

**Ready to begin? Start with Step 1 above!**
