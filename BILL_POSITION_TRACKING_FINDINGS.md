# Bill Position Tracking - Database Analysis

## Summary

**CRITICAL FINDING:** The California CAL-ACCESS lobbying database **does not contain dedicated fields for tracking bill positions** (support/oppose/neutral) or structured bill tracking information.

## What IS Available

### 1. Lobbying Activity Description Field
**Table:** `cvr_lobby_disclosure_cd`
**Raw Field:** `LBY_ACTVTY`
**View Access:** `v_disclosures.lobbying_activity_description`

**Description:** Free-form text field where lobbyists describe their quarterly lobbying activities. This is the closest field to tracking what lobbyists are trying to influence.

**Limitations:**
- Unstructured text (not searchable by specific bill numbers)
- May or may not mention specific bills
- Does not include structured position codes (support/oppose/neutral)
- Narrative format varies by filer

**To Use This Data:**
- Export `v_disclosures` view
- Text search/NLP analysis required to find bill references
- Manual parsing needed to determine positions

### 2. Expenditure Description Field
**Table:** `lexp_cd`
**Raw Field:** `EXPN_DSCR`
**View Access:** `v_expenditures.expense_description`

**Description:** Text description of lobbying expenses that may reference specific bills or legislative efforts.

**Limitations:**
- Also unstructured text
- Primarily describes expense type, not lobbying goals
- Inconsistent mention of bills

### 3. Financial Payment Data
**Tables:** `lpay_cd`, `lexp_cd`
**Views:** `v_payments`, `v_expenditures`

**Available Fields:**
- Payment amounts (`fees_amount`, `period_total`, `cumulative_total`)
- Payer/payee information
- Dates

**Use Case:** Track financial flows to understand lobbying intensity, but not specific positions on bills.

## What Is NOT Available

The following data points are **NOT tracked** in the CAL-ACCESS database:

- ❌ Specific bill numbers being lobbied
- ❌ Position on bills (support/oppose/neutral)
- ❌ Legislative targets (specific legislators contacted)
- ❌ Structured bill tracking
- ❌ Vote recommendations
- ❌ Legislative priorities

## Alternative Data Sources

### External Bill Tracking Resources

1. **California Lobby Search**
   - Website: calobbysearch.org
   - Features: Bill tracking by company and lobbying firm
   - More structured than CAL-ACCESS for bill positions

2. **California Legislature Website**
   - Website: leginfo.legislature.ca.gov
   - Contains: Bill text, voting records, legislative history
   - Can be cross-referenced with CAL-ACCESS filer data

3. **Follow the Money / OpenSecrets**
   - National lobbying tracking
   - May have additional California-specific data

## Recommendations for Website Development

### Option 1: Display Available Text Fields
Export and display the narrative lobbying activity descriptions:
```sql
SELECT
  filer_name,
  reporting_quarter,
  lobbying_activity_description,
  total_fees
FROM v_disclosures
WHERE is_alameda = TRUE
```

### Option 2: Future Enhancement - NLP Analysis
Implement text analysis to:
- Extract bill numbers from descriptions (regex: AB-\d+, SB-\d+)
- Identify position keywords (support, oppose, neutral, monitor)
- Build bill tracking from unstructured data

### Option 3: Manual Data Entry
For Alameda-specific use case:
- Create custom table for bill positions
- Manually research and enter Alameda lobbying positions
- Link to CAL-ACCESS filer records by FILER_ID

### Option 4: API Integration
Integrate with external sources:
- California Lobby Search API (if available)
- Legislative data APIs
- Combine with CAL-ACCESS financial data

## Current Export Status

The following Alameda-filtered CSV exports are available:

### Currently Exported (7 files):
1. ✓ v_filers_alameda.csv (46,679 rows)
2. ✓ v_registrations_alameda.csv (670 rows)
3. ✓ v_payments_alameda.csv (8,305 rows)
4. ✓ v_expenditures_alameda.csv (198 rows)
5. ✓ v_employers_alameda.csv (3,563,888 rows)
6. ✓ v_attachments_alameda.csv (1,390,366 rows)
7. ✓ v_alameda_filers_direct.csv (46,679 rows)

### Not Yet Exported (4 files - schema issues):
- ❌ v_disclosures_alameda.csv (THIS WOULD CONTAIN ACTIVITY DESCRIPTIONS)
- ❌ v_campaign_contributions_alameda.csv
- ❌ v_other_payments_alameda.csv
- ❌ v_alameda_activity.csv

## Priority Action

**IMPORTANT:** The `v_disclosures` view is the most critical missing export because it contains the `lobbying_activity_description` field - the only place where bill-specific lobbying efforts might be documented.

**Next Steps:**
1. Fix schema issues with v_disclosures view creation
2. Export v_disclosures_alameda.csv
3. Review actual lobbying activity descriptions in the data
4. Determine if NLP/text analysis is needed for bill extraction

## Technical Notes

### Schema Issues Encountered
The v_disclosures view failed to create due to:
- DATE field type mismatches (STRING vs DATE)
- Need to check actual column types in `cvr_lobby_disclosure_cd` table

### Query to Check Actual Schema
```sql
SELECT column_name, data_type
FROM `ca-lobby.ca_lobby.INFORMATION_SCHEMA.COLUMNS`
WHERE table_name = 'cvr_lobby_disclosure_cd'
ORDER BY ordinal_position;
```
