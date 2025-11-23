# Cal-ACCESS Database Documentation

> Comprehensive documentation for the California Automated Lobbying and Campaign Contribution & Expenditure Search System (Cal-ACCESS) database.

---

## 📚 Documentation Index

This directory contains extracted knowledge, insights, and reference materials about the Cal-ACCESS lobbying database structure, based on expert analysis of the official schema documentation.

### Core Documentation

| Document | Description | When to Use |
|----------|-------------|-------------|
| **[Lessons Learned](./lessons_learned.md)** | Critical insights, patterns, pitfalls, and best practices | Start here! Read this first to understand the database |
| **[Database Structure](./database_structure.md)** | Complete schema overview, table relationships, form mappings | Understanding overall architecture |
| **[Field Mapping Guide](./field_mapping_guide.md)** | Complete field definitions with Cal Format mappings (v2.0) | Writing queries, understanding field meanings, looking up field definitions |
| **[Business Rules](./business_rules.md)** | Business logic, payment flows, filing requirements | Understanding how lobbying data works |

---

## 🚀 Quick Start

### New to Cal-ACCESS?

1. **Read**: [lessons_learned.md](./lessons_learned.md) - Get the critical insights
2. **Understand**: [database_structure.md](./database_structure.md) - Learn the architecture
3. **Query**: [business_rules.md](./business_rules.md) - See query patterns
4. **Reference**: [field_mapping_guide.md](./field_mapping_guide.md) - Look up field definitions

### Common Tasks

| Task | Document | Section |
|------|----------|---------|
| Track city/county lobbying spending | [Business Rules](./business_rules.md) | Query Pattern 1 |
| Understand payment flow | [Lessons Learned](./lessons_learned.md) | Payment Flow Logic (#13) |
| Handle amendments correctly | [Business Rules](./business_rules.md) | Amendment Processing Rules |
| Look up entity codes | [Field Mapping Guide](./field_mapping_guide.md) | Code Fields Reference |
| Find top lobbying firms | [Business Rules](./business_rules.md) | Query Pattern 2 |

---

## 📖 Document Summaries

### [Lessons Learned](./lessons_learned.md)

**15 critical lessons** extracted from Cal-ACCESS schema documentation:

1. **System Architecture** - Three-tier subsystem design (EFS, AMS, Disclosure)
2. **Core Data Model** - Parent-child hierarchy (FILERS → FILINGS → Schedules)
3. **Entity Code System** - LEM (employer) vs FRM (firm) vs LBY (lobbyist)
4. **Form Type Structure** - 600 series (registration) vs disclosure forms
5. **Schedule Table Purposes** - LPAY, LEXP, LCCM, LOTH, LATT
6. **Amendment Tracking** - AMEND_ID: 0 = original, 1+ = amendments
7. **Historical Data Complexity** - Undocumented numbered tables (1/2/3 suffixes)
8. **Materialized Views** - Performance optimization patterns
9. **Supporting Infrastructure** - NAMES, ADDRESS, lookup tables
10. **Data Quality Caveats** - Known issues and validation needs
11. **Index Types** - Primary, foreign, alternate keys
12. **Date Field Confusion** - Multiple date fields with different meanings
13. **Payment Flow Logic** - Who pays whom (critical!)
14. **Database Conceptual Model** - Archive system analogy
15. **Critical Recommendations** - Best practices for your project

**Key Takeaway**: LPAY_CD is your critical table for tracking city/county lobbying payments.

---

### [Database Structure](./database_structure.md)

Expert overview of the Cal-ACCESS Oracle database schema (Model_1, February 2002).

**Covers**:
- System context and three subsystems
- Core filer and filing management tables
- Lobbying registration data (Forms 600 series)
- Lobbying disclosure data (Forms 615, 625, 635, 645)
- Lobbyist relationship and historical data
- Technical properties (columns, indexes, data types)

**Key Tables**:
- **FILERS_CD** - Master registry (FILER_ID)
- **FILINGS_CD** - Document registry (FILING_ID)
- **FILER_FILINGS_CD** - Junction table
- **CVR_LOBBY_DISCLOSURE_CD** - Disclosure cover pages
- **CVR_REGISTRATION_CD** - Registration cover pages
- **LPAY_CD** - Payments (CRITICAL)
- **LEXP_CD** - Expenditures
- **LCCM_CD** - Campaign contributions

**Conceptual Model**:
```
Master Registry (FILERS) ← All entities
    ↓
Junction Table (FILER_FILINGS) ← Links entities to documents
    ↓
Document Registry (FILINGS) ← All submitted forms
    ↓
Cover Pages (CVR_*) ← Form metadata
    ↓
Schedules (L*) ← Detailed line items
```

---

### [Field Mapping Guide](./field_mapping_guide.md)

**Version 2.0 (COMPLETE)** - Comprehensive field-level reference with complete Cal Format to Database Field mappings.

**Covers**:
- Field naming conventions (suffixes, prefixes)
- Common field patterns (primary keys, foreign keys)
- **Complete field definitions** for all lobbying tables:
  - CVR_REGISTRATION_CD (11 fields)
  - CVR_LOBBY_DISCLOSURE_CD (10 fields)
  - LPAY_CD (19 fields) - CRITICAL TABLE
  - LEXP_CD, LCCM_CD, LOTH_CD, LATT_CD, LEMP_CD
  - Amendment tables (LOBBY_AMENDMENTS_CD, F690P2_CD)
  - Additional names tables (CVR2_LOBBY_DISCLOSURE_CD, CVR2_REGISTRATION_CD)
- Date/Amount/Name/Address field references
- Code fields reference (ENTITY_CD, FORM_TYPE, AMEND_ID)
- Field relationships and joins
- **Data architecture analogy** (library cataloging system)
- **Critical fields summary** for city/county analysis
- Query best practices

**Key Patterns**:
- **_ID** = Identifier (NUMBER)
- **_CD** = Code (VARCHAR2)
- **_NAML** = Last/organization name
- **_AMT** = Amount (NUMBER)
- **_DATE** / **_DT** = Date field
- **_CB** = Checkbox boolean

**Most Important Fields**:
- `FILING_ID` + `AMEND_ID` = Primary navigation keys
- `EMPLR_NAML` = Who PAID (city/county) - **Use this for classification**
- `PAYEE_NAML` = Who WAS PAID (lobbying firm)
- `PER_TOTAL` = Payment amount for period
- `FROM_DATE` / `THRU_DATE` = Activity period

**Source**: Official Cal-ACCESS MapCalFormat2Fields.pdf documentation (via RTF extraction)

---

### [Business Rules](./business_rules.md)

Business logic, payment flows, filing requirements, and query patterns.

**Covers**:
1. **Lobbying Entity Types** - LEM vs FRM vs LBY relationships
2. **Payment Flow Logic** - Contract → Services → Payment → Contributions
3. **Form Types and Filing** - Registration vs Disclosure requirements
4. **Amendment Processing** - How amendments work
5. **Reporting Period Rules** - Quarterly and session periods
6. **Amount Calculation Rules** - PER_TOTAL vs CUM_TOTAL
7. **Registration vs Disclosure** - Different purposes and timing
8. **Data Validation Rules** - Required fields, valid ranges
9. **Query Business Logic** - Common query patterns with SQL examples

**Critical Business Rules**:
- Money flows FROM employer (LEM) TO firm (FRM)
- Quarterly filings due by end of month following quarter
- AMEND_ID = 0 is original, 1+ are amendments
- Always query for latest amendment (MAX(AMEND_ID))
- PER_TOTAL = FEES_AMT + REIMB_AMT + ADVAN_AMT
- Use FROM_DATE/THRU_DATE for activity periods

**Query Patterns Included**:
1. City/county lobbying expenditures
2. Top lobbying firms by revenue
3. Lobbying activity by topic
4. Campaign contributions by lobbyists
5. Trend analysis over time

---

## 📁 Source Files

Original documentation files are stored in [`/source/`](./source/):

| File | Description | Size |
|------|-------------|------|
| `Cal-ACCESS Lobbying Database Structure.rtf` | Expert overview of database structure | ~400 KB |
| `Overview of Cal-ACCESS Field Mappin.rtf` | Complete field mapping documentation | ~2.5 MB (84,451 tokens) |

**Note**: RTF files are source material. All critical information has been extracted into markdown documentation above.

---

## 🎯 Common Use Cases

### Use Case 1: Track Municipal Lobbying Spending

**Goal**: Find how much City of Oakland spent on lobbying in 2024

**Documents to reference**:
1. [Business Rules](./business_rules.md) - Query Pattern 1
2. [Field Mapping Guide](./field_mapping_guide.md) - LPAY_CD table
3. [Lessons Learned](./lessons_learned.md) - Payment Flow Logic

**Key query logic**:
```sql
SELECT emplr_naml, SUM(per_total) AS total_spent
FROM lpay_cd
WHERE emplr_naml LIKE '%Oakland%'
  AND amend_id = (SELECT MAX(amend_id) FROM lpay_cd p2 WHERE p2.filing_id = lpay_cd.filing_id)
GROUP BY emplr_naml
```

---

### Use Case 2: Identify Top Lobbying Firms

**Goal**: Which lobbying firms received the most revenue?

**Documents to reference**:
1. [Business Rules](./business_rules.md) - Query Pattern 2
2. [Lessons Learned](./lessons_learned.md) - Entity Code System
3. [Database Structure](./database_structure.md) - LPAY_CD definition

**Key understanding**: Query `PAYEE_NAML` (who was paid), not `EMPLR_NAML` (who paid).

---

### Use Case 3: Understand Amendment History

**Goal**: See how a filing changed over time

**Documents to reference**:
1. [Business Rules](./business_rules.md) - Amendment Processing Rules
2. [Lessons Learned](./lessons_learned.md) - Amendment Tracking System
3. [Field Mapping Guide](./field_mapping_guide.md) - AMEND_ID field

**Key concept**: AMEND_ID 0 = original, each higher number is a correction/update.

---

### Use Case 4: Analyze Campaign Contributions

**Goal**: Which candidates received contributions from lobbyists?

**Documents to reference**:
1. [Business Rules](./business_rules.md) - Query Pattern 4
2. [Database Structure](./database_structure.md) - LCCM_CD table
3. [Field Mapping Guide](./field_mapping_guide.md) - LCCM_CD fields

**Key tables**: LCCM_CD (contributions) joined with LPAY_CD (to find employer relationships).

---

## ⚠️ Critical Warnings

### The Three Cardinal Sins

1. **❌ Not filtering to latest AMEND_ID**
   - **Impact**: Counts amendments as separate filings, inflates totals
   - **Solution**: Always use `MAX(AMEND_ID)` pattern

2. **❌ Confusing EMPLR and PAYEE**
   - **Impact**: Gets backwards payment data (who paid vs who was paid)
   - **Solution**: LEM (employer) → EMPLR_NAML, FRM (firm) → PAYEE_NAML

3. **❌ Using CUM_TOTAL instead of PER_TOTAL**
   - **Impact**: Incorrect aggregations, double-counting
   - **Solution**: Aggregate on PER_TOTAL, calculate cumulative yourself

### Known Data Quality Issues

- Name variations (City of Oakland vs Oakland)
- Missing or incomplete fields
- Amendment calculation errors
- Undocumented table relationships (LOBBYIST_EMPLOYER1/2/3)
- Date field confusion (multiple date types)

**Recommendation**: Always validate results, cross-check totals, handle nulls explicitly.

---

## 🔗 Related Resources

### Internal Project Documentation

- **[California Lobbying Tables Documentation](../backend/docs/California_Lobbying_Tables_Documentation.md)** - Original project documentation
- **[BigQuery Views](../backend/queries/)** - 73 analytical views (Layers 1-4)
- **[Upload Pipeline](../backend/pipeline/upload_pipeline.py)** - Data ingestion process

### External Resources

- [Cal-ACCESS Official Website](https://cal-access.sos.ca.gov/)
- [California Secretary of State - Political Reform Division](https://www.sos.ca.gov/campaign-lobbying)
- [BigLocalNews Cal-ACCESS Data](https://biglocalnews.org/#/datasets/cal-access) - CSV exports

---

## 🛠️ For Developers

### Query Best Practices

1. **Always join through cover pages** (CVR_LOBBY_DISCLOSURE_CD)
2. **Filter to latest amendments** (MAX(AMEND_ID))
3. **Use proper date fields** (FROM_DATE/THRU_DATE for activity)
4. **Aggregate on PER_TOTAL** (not CUM_TOTAL)
5. **Handle entity codes correctly** (LEM = payer, FRM = payee)

### View Usage Recommendations

Use our BigQuery views instead of raw tables:

**Layer 1** (Base views):
- `v_filers`, `v_filings`, `v_payments`, `v_disclosures`

**Layer 2** (Integration views):
- `v_int_payment_details` - Pre-joined payment information
- `v_int_payment_with_latest_amendment` - Latest amendments only

**Layer 3** (Aggregation views):
- `v_summary_payments_by_year`
- `v_organization_summary` (116x faster than raw queries!)

**Layer 4** (Filtered views):
- `v_filter_alameda_filers`
- `v_filter_high_value_payments`

---

## 📊 Database Statistics

- **Database Type**: Google BigQuery (originally Oracle)
- **Original Schema Date**: February 21, 2002 (Model_1)
- **Core Lobbying Tables**: 13 main tables
- **Supporting Tables**: ~30+ infrastructure tables
- **Analytical Views**: 73 views (our BigQuery implementation)
- **Historical Data**: Covers 2000-present (20+ years)
- **Record Counts**:
  - CVR_LOBBY_DISCLOSURE_CD: ~4.3M rows
  - LPAY_CD: ~5.6M rows (CRITICAL TABLE)
  - LEXP_CD: ~millions of expenditure records

---

## 🤝 Contributing

To update this documentation:

1. **Add new insights** to appropriate markdown files
2. **Update README.md** with new sections or clarifications
3. **Cross-reference** between documents
4. **Validate** SQL examples against actual BigQuery data
5. **Commit** with descriptive messages

### Documentation Maintenance

- **Review quarterly** - Align with data updates
- **Validate annually** - Check against official Cal-ACCESS changes
- **Update examples** - Keep query patterns current
- **Track issues** - Document new data quality findings

---

## 📅 Document History

| Version | Date | Description |
|---------|------|-------------|
| 1.0 | November 2025 | Initial creation from RTF analysis |

---

## 📧 Contact

**Project**: Ca-Lobby Lobbying Tracking System
**Repository**: `/Users/michaelingram/Documents/GitHub/ca-lobby_mono`
**Documentation**: `/database_docs/`

---

## Quick Reference Card

### Most Critical Tables

| Table | Purpose | Key Field |
|-------|---------|-----------|
| **FILERS_CD** | Master registry | FILER_ID |
| **FILINGS_CD** | Document registry | FILING_ID |
| **LPAY_CD** | **Payments** (CRITICAL) | EMPLR_NAML, PAYEE_NAML, PER_TOTAL |
| **LEXP_CD** | Expenditures | PAYEE_NAML, AMOUNT |
| **LCCM_CD** | Campaign contributions | CTRIB_AMT, CAND_NAML |

### Entity Codes

- **LEM** = Lobbyist Employer (city/county that pays)
- **FRM** = Lobbying Firm (company that is paid)
- **LBY** = Lobbyist (individual)

### Amendment Rule

**ALWAYS use**: `MAX(AMEND_ID)` to get latest version only.

### Payment Direction

`EMPLR_NAML` (City) → pays → `PAYEE_NAML` (Firm)

---

**Happy Querying! 🎉**
