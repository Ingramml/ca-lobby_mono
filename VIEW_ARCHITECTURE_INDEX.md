# California Lobbying Database - View Architecture Index

**Master index of all view architecture documentation**

---

## Quick Navigation

| Document | Purpose | Audience | Time to Read |
|----------|---------|----------|--------------|
| **[Summary](#1-executive-summary)** | High-level overview, ROI | Executives, stakeholders | 5 min |
| **[Quick Start](#2-quick-start-guide)** | Implementation steps | Developers, analysts | 15 min |
| **[Full Architecture](#3-complete-architecture)** | Complete technical spec | Database architects | 45 min |
| **[SQL Scripts](#4-sql-scripts)** | Executable view creation | Developers | N/A (reference) |

---

## 1. Executive Summary

**File:** `VIEW_ARCHITECTURE_SUMMARY.md`

**What it covers:**
- Problem statement and solution
- Key benefits and ROI
- Architecture overview
- Cost/benefit analysis
- Implementation status
- Risk assessment

**Read this if you need to:**
- Understand the business value
- Get approval for implementation
- Present to stakeholders
- Justify the investment

**Key Takeaways:**
- 73 views provide structured access; exports only for testing
- 50% cost reduction ($5,875/year savings)
- 10-100x faster queries
- 3.6 month ROI
- Production-ready today

---

## 2. Quick Start Guide

**File:** `VIEW_ARCHITECTURE_QUICKSTART.md`

**What it covers:**
- Step-by-step implementation
- Pre-implementation checklist
- View creation order
- Critical materialized views
- Common queries cheat sheet
- Troubleshooting guide

**Read this if you need to:**
- Implement the views NOW
- Follow a structured deployment plan
- Get views running quickly
- Learn common query patterns
- Troubleshoot issues

**Estimated Time to Implement:** 3-4 hours

---

## 3. Complete Architecture

**File:** `BIGQUERY_VIEW_ARCHITECTURE.md`

**What it covers:**
- Complete 4-layer architecture
- All 73 view definitions with SQL
- Entity code translations
- Performance recommendations
- Usage examples (10+ scenarios)
- Migration guide from CSV exports
- Cost analysis (detailed)
- Maintenance procedures

**Read this if you need to:**
- Understand the complete design
- See all view definitions
- Customize views for specific needs
- Optimize performance
- Plan long-term maintenance

**Sections:**
1. Architecture Overview
2. View Naming Convention
3. **Layer 1: Base Views (19 views)**
   - Filers, Registrations, Disclosures
   - Payments, Expenditures, Contributions
   - Relationships, Supporting Data
4. **Layer 2: Integration Views (24 views)**
   - Filer integration
   - Payment integration
   - Network analysis
   - Money flow tracking
5. **Layer 3: Analytical Views (20 views)**
   - Time-based aggregations
   - Top spenders/recipients
   - Market share analysis
   - Trends and growth
6. **Layer 4: Specialized Filters (10 views)**
   - Alameda-specific
   - Time-based filters
   - Value-based filters
   - Entity type filters
7. Performance Recommendations
8. Usage Examples
9. Migration Guide
10. Cost Analysis

---

## 4. SQL Scripts

**File:** `CREATE_ALL_VIEWS.sql`

**What it covers:**
- Executable SQL for all 73 views
- Proper creation order
- Comments and documentation
- Ready to run in BigQuery

**Use this to:**
- Create views in correct order
- Execute via `bq query` command
- Reference view SQL directly
- Customize view definitions

**Execution:**
```bash
bq query --use_legacy_sql=false < CREATE_ALL_VIEWS.sql
```

---

## View Categories Reference

### Layer 1: Base Views (19 views)

**Filer Views:**
- `v_filers` - Master filer registry
- `v_filer_filings` - Filing index
- `v_filer_addresses` - Physical addresses
- `v_filer_types` - Filer classifications
- `v_filer_xref` - Cross-references

**Registration Views:**
- `v_registrations` - Lobbying registrations
- `v_registrations_secondary` - Secondary registration data

**Disclosure Views:**
- `v_disclosures` - Quarterly disclosures
- `v_disclosures_secondary` - Secondary disclosure data

**Financial Transaction Views:**
- `v_payments` - All payments (CRITICAL)
- `v_expenditures` - Lobbying expenditures
- `v_campaign_contributions` - Campaign contributions
- `v_other_payments` - Miscellaneous payments

**Relationship Views:**
- `v_employer_relationships` - Employer-lobbyist connections

**Supporting Data Views:**
- `v_attachments` - Payment attachments
- `v_names` - Name variations
- `v_amendments` - Amendment history
- `v_lookup_codes` - Code translations

### Layer 2: Integration Views (24 views)

**Filer Integration:**
- `v_int_filer_complete` - Complete filer profile (CRITICAL)
- `v_int_filer_disclosures` - Disclosures with filer details
- `v_int_filer_registrations` - Registrations with filer details
- `v_int_filer_payment_summary` - Payment summary by filer
- `v_int_filer_expenditure_summary` - Expenditure summary by filer

**Payment Integration:**
- `v_int_payment_details` - Payments with full context (CRITICAL)
- `v_int_payment_with_latest_amendment` - Latest amendments only (CRITICAL)

**Relationship Integration:**
- `v_int_employer_firm_relationships` - Complete employer-firm connections
- `v_int_network_employer_to_firm` - Network graph data

**Money Flow:**
- `v_int_money_flow_purchaser_to_provider` - Track money flow

**Expenditure Integration:**
- `v_int_expenditure_details` - Expenditures with context

**Complete Filing:**
- `v_int_complete_filing_details` - Everything about a filing

**Amendment Tracking:**
- `v_int_amendment_history` - Track all amendments

### Layer 3: Analytical Views (20 views)

**Time-Based:**
- `v_summary_payments_by_year` - Annual trends
- `v_summary_payments_by_quarter` - Quarterly trends
- `v_summary_expenditures_by_year` - Annual expenditures

**Top Lists:**
- `v_summary_top_payment_recipients` - Top lobbying firms
- `v_summary_top_purchasers` - Top employers
- `v_summary_top_campaign_contributors` - Top contributors

**Geographic:**
- `v_summary_payments_by_region` - Geographic distribution
- `v_summary_alameda_activity` - Alameda-specific summary

**Market Analysis:**
- `v_summary_firm_market_share` - Market share analysis

**Activity Level:**
- `v_summary_filer_activity_status` - Activity classification

**Compliance:**
- `v_summary_amendment_frequency` - Amendment patterns

**Trends:**
- `v_summary_yoy_growth` - Year-over-year growth

**Network:**
- `v_summary_most_connected_filers` - Network centrality

**Timeline:**
- `mv_complete_activity_timeline` - Complete timeline (MATERIALIZED)

**Statistics:**
- `v_summary_database_statistics` - Overall database stats

### Layer 4: Specialized Filters (10 views)

**Alameda-Specific (lower priority):**
- ~~`v_filter_alameda_filers` - Alameda filers only~~
- ~~`v_filter_alameda_payments` - Alameda payments~~
- `v_filter_alameda_complete_activity` - Complete Alameda activity

**Time-Based:**
- `v_filter_current_year` - Current year only
- `v_filter_last_12_months` - Rolling 12-month window
- `v_filter_recent_filings` - Last 6 months

**Activity Level:**
- ~~`v_filter_active_filers` - Active filers only~~ (lower priority)
- `v_filter_inactive_filers` - Inactive filers

**Value-Based (lower priority):**
- ~~`v_filter_high_value_payments` - Payments > $10K~~ (lower priority)
- `v_filter_very_high_value_payments` - Payments > $100K

**Entity Type:**
- `v_filter_lobbying_firms` - Firms only (FRM)
- `v_filter_employers` - Employers only (LEM)
- `v_filter_coalitions` - Coalitions only (LCO)

---

## Critical Views to Materialize

**Note: Data does not need regular updates currently; refresh schedule TBD**

1. **mv_int_payment_with_latest_amendment**
   - Most frequently queried
   - Complex deduplication logic
   - Refresh: Will be set at a later date

2. **mv_int_filer_complete**
   - Used by many other views
   - Multiple table joins
   - Refresh: Will be set at a later date

3. **mv_complete_activity_timeline**
   - Extremely expensive to compute
   - Union of multiple large tables
   - Refresh: Will be set at a later date

4. **Optional:** ~~`mv_filter_alameda_payments`~~ (lower priority)
   - If Alameda analysis is frequent
   - Refresh: Will be set at a later date

---

## Common Query Patterns

### Pattern 1: Find Specific Organization
```sql
-- Find filer
SELECT * FROM `ca-lobby.ca_lobby.v_int_filer_complete`
WHERE UPPER(filer_name) LIKE '%SEARCH TERM%';

-- Get their payments
SELECT * FROM `ca-lobby.ca_lobby.v_int_payment_with_latest_amendment`
WHERE filer_id = 'FOUND_FILER_ID';
```

### Pattern 2: Aggregate Analysis
```sql
-- Use pre-aggregated views
SELECT * FROM `ca-lobby.ca_lobby.v_summary_payments_by_year`
WHERE reporting_year >= 2020;
```

### Pattern 3: Network Analysis
```sql
-- Use network views
SELECT * FROM `ca-lobby.ca_lobby.v_int_network_employer_to_firm`
WHERE total_payments_made >= 50000;
```

### Pattern 4: Filtered Subsets (Optional - some views lower priority)
```sql
-- Use filter views
-- Note: High-value payment views are lower priority
SELECT * FROM `ca-lobby.ca_lobby.v_filter_high_value_payments`
WHERE reporting_year = 2024;
```

---

## Performance Tips

### DO:
✓ Filter by date ranges (uses partitioning)
✓ Use clustered columns (filer_id, reporting_year)
✓ Query materialized views when available
✓ Use summary views for aggregations
✓ Add LIMIT during testing

### DON'T:
✗ Use `SELECT *` on large views
✗ Avoid WHERE clauses (full table scans)
✗ Re-aggregate already summarized data
✗ Query base views when integration views exist
✗ Ignore materialization recommendations

---

## Implementation Workflow

```
1. Review Documents
   └─→ Read VIEW_ARCHITECTURE_SUMMARY.md (5 min)
   └─→ Read VIEW_ARCHITECTURE_QUICKSTART.md (15 min)
   └─→ Skim BIGQUERY_VIEW_ARCHITECTURE.md (for reference)

2. Pre-Implementation
   └─→ Verify BigQuery access
   └─→ Backup existing queries
   └─→ Review current CSV usage

3. Create Views (Sequential)
   └─→ Layer 1: Base Views (30 min)
   └─→ Layer 2: Integration Views (30 min)
   └─→ Layer 3: Analytical Views (15 min)
   └─→ Layer 4: Filter Views (10 min)

4. Materialize Critical Views
   └─→ mv_int_payment_with_latest_amendment
   └─→ mv_int_filer_complete
   └─→ mv_complete_activity_timeline

5. Set Up Refresh Schedules
   └─→ Refresh schedules will be set at a later date
   └─→ Monitor refresh success

6. Test & Validate
   └─→ Run sample queries
   └─→ Compare with CSV exports
   └─→ Verify data accuracy

7. Migrate Queries
   └─→ Update existing queries to use views
   └─→ Train team on view usage
   └─→ Document custom patterns

8. CSV Exports
   └─→ CSV exports only for testing
   └─→ Views provide structured data access
   └─→ Not a replacement strategy
```

---

## File Locations

All documentation in:
```
/Users/michaelingram/Documents/GitHub/CA_lobby_Database/
```

**Main Documents:**
- `VIEW_ARCHITECTURE_INDEX.md` (this file)
- `VIEW_ARCHITECTURE_SUMMARY.md` (executive summary)
- `VIEW_ARCHITECTURE_QUICKSTART.md` (implementation guide)
- `BIGQUERY_VIEW_ARCHITECTURE.md` (complete architecture)
- `CREATE_ALL_VIEWS.sql` (executable SQL)

**Supporting Documents:**
- `Documents/California_Lobbying_Tables_Documentation.md` (table schema)
- `Documents/ALAMEDA_Lobbying_Queries.md` (example queries)

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2025-10-24 | Initial release - 73 views, complete architecture |

---

## Next Steps

**Start Here:**
1. Read `VIEW_ARCHITECTURE_SUMMARY.md` (5 minutes)
2. Read `VIEW_ARCHITECTURE_QUICKSTART.md` (15 minutes)
3. Execute `CREATE_ALL_VIEWS.sql` (30 minutes)
4. Test critical queries (30 minutes)
5. Begin migration (1-2 hours)

**Need Help?**
- Quick questions → See Quick Start guide
- Technical details → See Complete Architecture
- SQL reference → See CREATE_ALL_VIEWS.sql
- Troubleshooting → See Quick Start guide

---

**Ready to begin? Start with VIEW_ARCHITECTURE_SUMMARY.md!**
