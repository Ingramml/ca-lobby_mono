# CA Lobby Database Strategy Recommendation

**Created**: October 28, 2025
**Purpose**: Recommend optimal database strategy using normalized CAL-ACCESS tables vs views
**Audience**: Database architects and developers

---

## Executive Summary

**Recommendation**: **Use a HYBRID approach** - Start with raw normalized tables for comprehensive data, then create optimized views for the web application.

**Rationale**:
- Raw tables ensure ALL data points are available
- Views provide optimized query performance for web app
- Flexibility to add new data points without restructuring

---

## Current State Analysis

### What We're Using Now

**Views Only** (Limited data):
- `v_payments_alameda.csv` - Payment line items
- `v_disclosures_alameda.csv` - Alameda-filtered disclosures (INCOMPLETE)
- `v_filers_alameda.csv` - Filer registry

**Problem Identified**:
The Alameda-filtered disclosure view **excludes** disclosures filed by non-Alameda lobbying firms, even when those firms work for Alameda organizations. This causes:
- ❌ NULL `firm_name` fields
- ❌ NULL `date`, `from_date`, `thru_date` fields
- ❌ Non-functional lobbyist network feature

---

## Normalized Database Structure

Based on California_Lobbying_Tables_Documentation.md, we have access to:

### Core Lobbying Tables

| Table | Purpose | Critical Fields | Records |
|-------|---------|----------------|---------|
| **CVR2_LOBBY_DISCLOSURE_CD** | Disclosure cover page | `filing_id`, `filer_id`, `period_start_date`, `period_end_date`, `firm_name`, `entity_code` | ~500K+ |
| **LPAY_CD** | Payment transactions | `filing_id`, `amount_paid`, `payee_name`, `payment_type` | ~100K+ |
| **LEMP_CD** | Employer-lobbyist relationships | `filing_id`, `employer_name`, `lobbyist_name`, `subcontracted` | ~50K+ |
| **LEXP_CD** | Lobbying expenditures | `filing_id`, `expense_type`, `amount`, `payee` | ~50K+ |
| **LOTH_CD** | Other payments | `filing_id`, `payment_amount`, `description` | ~200K+ |
| **CVR_REGISTRATION_CD** | Registration info | `filer_id`, `filer_name`, `address`, `business_class` | ~10K+ |

### Supporting Tables

| Table | Purpose | Why Important |
|-------|---------|---------------|
| **FILERS_CD** | Master filer registry | Links all entities across tables |
| **FILER_FILINGS_CD** | Filing index | Navigation between filers and filings |
| **TEXT_MEMO_CD** | Extended descriptions | Human-readable activity narratives |
| **LOOKUP_CODES_CD** | Code definitions | Decode form types, entity codes, payment types |
| **NAMES_CD** | Name information | Individual names for lobbyists |

---

## Recommended Database Strategy

### Phase 1: Import Full Normalized Tables

**Tables to Import** (Priority Order):

#### Essential (Import First):
1. **CVR2_LOBBY_DISCLOSURE_CD** - Disclosure cover pages
   - Contains: `firm_name`, `period_start_date`, `period_end_date`, `report_date`
   - Why: Fixes ALL missing data issues in current implementation

2. **LPAY_CD** - Payment transactions
   - Contains: Individual payment records with detail
   - Why: More granular than current payment data

3. **LEMP_CD** - Employer-lobbyist relationships
   - Contains: Links between organizations and their lobbyists
   - Why: Enables proper lobbyist network feature

4. **FILERS_CD** - Master filer registry
   - Contains: Complete entity information
   - Why: Foundation for all entity lookups

#### Important (Import Second):
5. **CVR_REGISTRATION_CD** - Registration information
   - Contains: Business classifications, addresses, industry codes
   - Why: Enriches organization profiles

6. **LEXP_CD** - Expenditures
   - Contains: Detailed spending by category
   - Why: Enables spending analysis by expense type

7. **TEXT_MEMO_CD** - Text descriptions
   - Contains: Extended narratives about lobbying activities
   - Why: Adds context to transactions

8. **LOOKUP_CODES_CD** - Code definitions
   - Contains: Human-readable labels for all codes
   - Why: Makes data more understandable

#### Nice to Have (Import Third):
9. **LCCM_CD** - Campaign contributions
   - Contains: Contributions made by lobbyists to campaigns
   - Why: Shows additional influence patterns

10. **LOTH_CD** - Other payments
    - Contains: Miscellaneous payments not in other categories
    - Why: Complete financial picture

### Phase 2: Create Optimized Views

After importing raw tables, create views optimized for web application:

#### View 1: Complete Organization Profile Data
```sql
CREATE OR REPLACE VIEW v_org_profiles_complete AS
SELECT
  -- Organization identification
  e.employer_full_name as organization_name,
  e.employer_id as filer_id,
  f.business_class as organization_type,

  -- Disclosure information
  d.filing_id,
  d.amendment_id,
  d.period_start_date,
  d.period_end_date,
  d.report_date as filing_date,
  d.firm_name,
  d.form_type,
  d.entity_code,

  -- Payment details
  p.line_item,
  p.fees_amount,
  p.reimbursement_amount,
  p.advance_amount,
  (p.fees_amount + p.reimbursement_amount + p.advance_amount) as period_total,
  p.cumulative_total,

  -- Lobbyist information
  l.lobbyist_last_name,
  l.lobbyist_first_name,
  (l.lobbyist_first_name || ' ' || l.lobbyist_last_name) as lobbyist_name,

  -- Activity description
  t.text_description

FROM
  LEMP_CD e  -- Employer relationships
  INNER JOIN CVR2_LOBBY_DISCLOSURE_CD d ON e.filing_id = d.filing_id
  LEFT JOIN LPAY_CD p ON d.filing_id = p.filing_id
  LEFT JOIN NAMES_CD l ON e.lobbyist_id = l.filer_id
  LEFT JOIN CVR_REGISTRATION_CD f ON e.employer_id = f.filer_id
  LEFT JOIN TEXT_MEMO_CD t ON d.filing_id = t.filing_id

WHERE
  -- Filter for Alameda County organizations (by location, not by who files)
  e.employer_full_name IN (
    SELECT employer_name
    FROM alameda_organizations_list
  )
  OR f.city = 'ALAMEDA'
  OR f.county = 'ALAMEDA'

ORDER BY d.period_start_date DESC;
```

**Key Difference**: This joins by EMPLOYER (the organization), not by FILER (the lobbying firm). This ensures we get ALL disclosures for Alameda organizations, regardless of which firm filed them.

#### View 2: Lobbyist Network Data
```sql
CREATE OR REPLACE VIEW v_lobbyist_network AS
SELECT
  e.employer_full_name as organization_name,
  d.firm_name as lobbying_firm,
  (l.lobbyist_first_name || ' ' || l.lobbyist_last_name) as lobbyist_name,
  COUNT(DISTINCT d.filing_id) as filing_count,
  SUM(p.fees_amount) as total_fees_paid,
  MIN(d.period_start_date) as first_activity,
  MAX(d.period_end_date) as last_activity,

  -- Relationship type
  CASE
    WHEN e.subcontracted = 'Y' THEN 'Subcontracted'
    ELSE 'Direct Hire'
  END as relationship_type

FROM
  LEMP_CD e
  INNER JOIN CVR2_LOBBY_DISCLOSURE_CD d ON e.filing_id = d.filing_id
  LEFT JOIN LPAY_CD p ON d.filing_id = p.filing_id
  LEFT JOIN NAMES_CD l ON e.lobbyist_id = l.filer_id

WHERE
  e.employer_full_name IN (SELECT employer_name FROM alameda_organizations_list)

GROUP BY
  e.employer_full_name,
  d.firm_name,
  lobbyist_name,
  e.subcontracted

ORDER BY
  e.employer_full_name,
  total_fees_paid DESC;
```

#### View 3: Activity Timeline Data
```sql
CREATE OR REPLACE VIEW v_activity_timeline AS
SELECT
  e.employer_full_name as organization_name,
  d.filing_id,
  d.amendment_id,
  d.period_start_date,
  d.period_end_date,
  d.report_date,
  d.firm_name,
  d.form_type,

  -- Aggregated payment info
  SUM(p.fees_amount) as total_fees,
  SUM(p.reimbursement_amount) as total_reimbursements,
  SUM(p.advance_amount) as total_advances,
  SUM(p.fees_amount + p.reimbursement_amount + p.advance_amount) as total_payments,
  COUNT(p.line_item) as payment_line_items,

  -- Activity description
  MAX(t.text_description) as activity_description

FROM
  LEMP_CD e
  INNER JOIN CVR2_LOBBY_DISCLOSURE_CD d ON e.filing_id = d.filing_id
  LEFT JOIN LPAY_CD p ON d.filing_id = p.filing_id
  LEFT JOIN TEXT_MEMO_CD t ON d.filing_id = t.filing_id

WHERE
  e.employer_full_name IN (SELECT employer_name FROM alameda_organizations_list)
  AND d.amendment_id = (
    SELECT MAX(amendment_id)
    FROM CVR2_LOBBY_DISCLOSURE_CD d2
    WHERE d2.filing_id = d.filing_id
  )  -- Get only latest amendments

GROUP BY
  e.employer_full_name,
  d.filing_id,
  d.amendment_id,
  d.period_start_date,
  d.period_end_date,
  d.report_date,
  d.firm_name,
  d.form_type

ORDER BY
  d.period_start_date DESC;
```

#### View 4: Expenditure Categories
```sql
CREATE OR REPLACE VIEW v_expenditure_categories AS
SELECT
  e.employer_full_name as organization_name,
  d.period_start_date,
  d.period_end_date,

  -- Expenditure breakdown
  exp.expense_type,
  lc.code_description as expense_type_description,
  SUM(exp.amount) as total_amount,
  COUNT(*) as expense_count,
  AVG(exp.amount) as average_amount,

  -- Payee information
  exp.payee_name,
  exp.payee_city,
  exp.payee_state

FROM
  LEMP_CD e
  INNER JOIN CVR2_LOBBY_DISCLOSURE_CD d ON e.filing_id = d.filing_id
  INNER JOIN LEXP_CD exp ON d.filing_id = exp.filing_id
  LEFT JOIN LOOKUP_CODES_CD lc ON exp.expense_type = lc.code

WHERE
  e.employer_full_name IN (SELECT employer_name FROM alameda_organizations_list)

GROUP BY
  e.employer_full_name,
  d.period_start_date,
  d.period_end_date,
  exp.expense_type,
  lc.code_description,
  exp.payee_name,
  exp.payee_city,
  exp.payee_state

ORDER BY
  e.employer_full_name,
  d.period_start_date DESC,
  total_amount DESC;
```

---

## Data Points Now Available

### Currently Missing (Will Be Fixed):

| Data Point | Source Table | Field | Impact |
|-----------|--------------|-------|--------|
| Firm Names | CVR2_LOBBY_DISCLOSURE_CD | `firm_name` | ✅ Enables lobbyist network |
| Activity Dates | CVR2_LOBBY_DISCLOSURE_CD | `period_start_date`, `period_end_date` | ✅ Enables timeline sorting |
| Filing Dates | CVR2_LOBBY_DISCLOSURE_CD | `report_date` | ✅ Enables activity chronology |
| Lobbyist Names | NAMES_CD | `filer_name` | ✅ Shows individual lobbyists |
| Form Types | CVR2_LOBBY_DISCLOSURE_CD | `form_type` | ✅ Better categorization |

### New Data Points (Not Currently Used):

| Data Point | Source Table | Field | Potential Feature |
|-----------|--------------|-------|-------------------|
| Business Classification | CVR_REGISTRATION_CD | `business_class` | Better organization categorization |
| Industry Codes | CVR_REGISTRATION_CD | `industry_code` | Industry analysis |
| Agencies Lobbied | CVR_REGISTRATION_CD | `agencies` | Show which agencies targeted |
| Subcontracted Work | LEMP_CD | `subcontracted` | Relationship type visualization |
| Expense Categories | LEXP_CD | `expense_type` | Spending breakdown by type |
| Campaign Contributions | LCCM_CD | `amount`, `recipient` | Influence pattern analysis |
| Activity Descriptions | TEXT_MEMO_CD | `text_description` | Human-readable narratives |
| Ethics Training | CVR_REGISTRATION_CD | `ethics_date` | Lobbyist compliance tracking |

---

## Implementation Recommendation

### Immediate Actions (Week 1)

1. **Import Core Tables to BigQuery**:
   ```bash
   # Priority 1: Disclosure and payment data
   bq load --source_format=CSV \
     --skip_leading_rows=1 \
     ca_lobby.CVR2_LOBBY_DISCLOSURE_CD \
     CVR2_LOBBY_DISCLOSURE_CD.txt

   bq load --source_format=CSV \
     ca_lobby.LPAY_CD \
     LPAY_CD.txt

   bq load --source_format=CSV \
     ca_lobby.LEMP_CD \
     LEMP_CD.txt
   ```

2. **Create Complete Organization Profile View**:
   - Use SQL from "View 1" above
   - Export to CSV for web app

3. **Update Web Application**:
   - Run existing `generate_individual_transactions.py` with new CSV
   - All NULL fields will be populated automatically

### Short-term Enhancements (Week 2-3)

4. **Implement Lobbyist Network Feature**:
   - Create "View 2: Lobbyist Network Data"
   - Update `LobbyistNetwork.js` component
   - Enable expand/collapse functionality

5. **Add Timeline Visualization**:
   - Use "View 3: Activity Timeline Data"
   - Replace demo trend data with real quarterly data
   - Implement date-based filtering

6. **Expense Category Breakdown**:
   - Use "View 4: Expenditure Categories"
   - Add new chart showing spending by category
   - Enable drill-down to see payees

### Long-term Features (Month 2+)

7. **Advanced Analytics**:
   - Campaign contribution tracking (LCCM_CD)
   - Subcontractor network visualization
   - Agency targeting analysis
   - Industry comparison tools

8. **Enhanced Search**:
   - Search by lobbyist name
   - Filter by firm
   - Date range queries
   - Expense type filtering

9. **Compliance Dashboard**:
   - Ethics training status
   - Filing timeliness
   - Amendment tracking

---

## Views vs Raw Tables: Decision Matrix

| Consideration | Raw Tables | Views | Recommendation |
|--------------|------------|-------|----------------|
| **Data Completeness** | ✅ All fields available | ⚠️ May filter out data | Use raw tables as source |
| **Query Performance** | ❌ Slower (complex joins) | ✅ Optimized queries | Create views for app |
| **Flexibility** | ✅ Can create any query | ⚠️ Limited to view definition | Keep raw tables accessible |
| **Maintenance** | ⚠️ More complex queries | ✅ Simpler application code | Use views in application |
| **Data Updates** | ✅ Single source of truth | ✅ Auto-updates from tables | Best of both worlds |
| **Storage Cost** | ❌ Higher storage | ✅ No additional storage | Views are virtual |
| **Development Speed** | ❌ Complex SQL in app | ✅ Simple queries in app | Views speed development |

### Winner: HYBRID APPROACH

**Strategy**:
1. Import all raw normalized tables to BigQuery
2. Create optimized views for web application needs
3. Export views to CSV for current architecture
4. Future: Connect web app directly to BigQuery views (Phase 3)

---

## Migration Plan

### Step 1: Audit Current Data Gaps
- [x] Identified NULL fields (firm names, dates)
- [x] Documented root cause (filtered views)
- [x] Confirmed normalized tables contain missing data

### Step 2: Import Normalized Tables
- [ ] CVR2_LOBBY_DISCLOSURE_CD
- [ ] LPAY_CD
- [ ] LEMP_CD
- [ ] FILERS_CD
- [ ] NAMES_CD
- [ ] TEXT_MEMO_CD
- [ ] LOOKUP_CODES_CD

### Step 3: Create Optimized Views
- [ ] v_org_profiles_complete
- [ ] v_lobbyist_network
- [ ] v_activity_timeline
- [ ] v_expenditure_categories

### Step 4: Export Views to CSV
- [ ] Run export queries
- [ ] Download CSVs to Sample data/
- [ ] Validate data completeness

### Step 5: Update Web Application
- [ ] Run generate_individual_transactions.py with new data
- [ ] Verify NULL fields now populated
- [ ] Test lobbyist network component
- [ ] Verify timeline sorting works
- [ ] Build and deploy

### Step 6: Enable New Features
- [ ] Lobbyist network visualization
- [ ] Real timeline charts
- [ ] Expense category breakdown
- [ ] Enhanced search filters

---

## Cost-Benefit Analysis

### Benefits of Normalized Tables Approach

**Data Quality**:
- ✅ 100% complete data (no NULL fields)
- ✅ All relationship information preserved
- ✅ Access to TEXT_MEMO descriptions
- ✅ Campaign contribution data available

**Features Enabled**:
- ✅ Lobbyist network visualization (currently broken)
- ✅ Timeline charts with real dates (currently demo data)
- ✅ Expense category analysis (new feature)
- ✅ Search by lobbyist name (new feature)
- ✅ Agency targeting analysis (new feature)

**Development**:
- ✅ Flexibility to add new features without restructuring
- ✅ Can create custom views for any use case
- ✅ Single source of truth for all data

### Costs

**Setup Time**:
- ~2 hours: Import tables to BigQuery
- ~4 hours: Create and test views
- ~2 hours: Update web application
- **Total: ~1 day** of development time

**Storage**:
- Raw tables: ~500MB (minimal cost)
- Views: 0 bytes (virtual)
- **Total: < $1/month** in BigQuery storage

**Maintenance**:
- Views auto-update when tables update
- No additional maintenance burden

---

## Conclusion

**Recommended Approach**: Import full normalized tables + Create optimized views

**Why**:
1. **Ensures ALL data points available** - No more NULL fields or missing data
2. **Fixes current issues** - Lobbyist network and timeline features will work
3. **Enables future features** - Expense analysis, agency tracking, etc.
4. **Minimal cost** - ~1 day setup time, <$1/month storage
5. **Best practice** - Normalized tables with view abstraction is industry standard

**Next Step**: Import the 7 core tables listed in "Step 2: Import Normalized Tables" and create the 4 views in "Step 3: Create Optimized Views".

---

**Document Status**: Ready for Implementation
**Estimated ROI**: High (fixes critical data gaps, enables multiple new features)
**Risk Level**: Low (non-breaking change, existing features continue working)
