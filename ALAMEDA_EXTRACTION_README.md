# Alameda Lobbying Data Extraction

**Generated**: October 24, 2025
**Purpose**: Extract sample data for all California lobbying tables containing Alameda organizations

---

## Overview

This extraction identifies all lobbying entities (firms, employers, coalitions, individuals) associated with "Alameda" and exports their data from the California lobbying disclosure database to CSV files.

**Output**: 10 CSV files in `alameda_data_exports/` directory

---

## Extraction Categories

Organizations are classified into two categories:

### PURCHASER (Buying Lobbying Services)
- **LEM**: Lobbyist Employers - Organizations hiring lobbyists
- **LCO**: Lobbying Coalitions - Groups of organizations
- **IND**: Individuals spending >$5,000 on lobbying

### PROVIDER (Selling Lobbying Services)
- **FRM**: Lobbying Firms - Companies providing lobbying services
- **LBY**: Lobbyists - Individual lobbyists

---

## Prerequisites

### 1. Google Cloud Setup
- Google Cloud project with BigQuery API enabled
- Service account with BigQuery Data Viewer and Job User permissions
- Service account JSON key file

### 2. Python Environment
```bash
pip install google-cloud-bigquery pandas python-dotenv
```

### 3. Environment Configuration
Create `.env` file in project root:
```
GOOGLE_APPLICATION_CREDENTIALS=/path/to/your/service-account-key.json
GCP_PROJECT_ID=your-project-id
BQ_DATASET=your-dataset-name
```

**Security Note**: `.env` is already in `.gitignore` - never commit credentials

---

## Usage

### Method 1: Python Script (Recommended)

```bash
python extract_alameda_data.py
```

**What it does:**
1. Creates `alameda_data_exports/` directory
2. Connects to BigQuery using credentials from `.env`
3. Runs 10 extraction queries
4. Exports each table to CSV
5. Displays progress and statistics

**Expected Output:**
```
Starting Alameda data extraction...
Created output directory: alameda_data_exports/

[1/10] Extracting master filers registry...
✓ Exported 15 rows to Alameda_Filers.csv

[2/10] Extracting lobby disclosure filings...
✓ Exported 127 rows to Alameda_Lobby_Disclosures.csv

...

Extraction Complete!
Total tables exported: 10
Total rows extracted: 1,247
Output directory: alameda_data_exports/
```

### Method 2: Direct SQL (BigQuery Console)

1. Open [extract_alameda_data.sql](extract_alameda_data.sql)
2. Copy queries to BigQuery console
3. Update `EXPORT DATA` statements with your GCS bucket path
4. Run each query individually

---

## Output Files

### 1. Alameda_Filers.csv
Master registry of all Alameda-associated entities
- **Columns**: FILER_ID, FILER_NAML, ENTITY_CD, ALAMEDA_RELATION
- **Use**: Reference table showing all Alameda organizations

### 2. Alameda_Lobby_Disclosures.csv
Quarterly lobbying disclosure filings
- **Columns**: Filing details, date ranges, cumulative totals
- **Use**: Primary source for lobbying activity periods

### 3. Alameda_Registrations.csv
Lobbyist registration records
- **Columns**: Registration dates, authorization info, employer relationships
- **Use**: Track when lobbying relationships were established

### 4. Alameda_Payments.csv (KEY TABLE)
Payments from employers to lobbying firms
- **Columns**: EMPLR_NAML, FEES_AMT, REIMB_AMT, ADVAN_AMT, PER_TOTAL, CUM_TOTAL
- **Use**: Follow the money - who paid whom for lobbying

### 5. Alameda_Expenditures.csv
Detailed lobbying expenditures
- **Columns**: Payee names, expense types, amounts, dates
- **Use**: Understand how lobbying money was spent

### 6. Alameda_Employers.csv
Employer-lobbyist relationships
- **Columns**: Employer details, lobby firm assignments
- **Use**: Map relationships between employers and firms

### 7. Alameda_Campaign_Contributions.csv
Campaign contributions made by lobbyists/firms
- **Columns**: Contributor, recipient, amount, date
- **Use**: Track political contributions tied to lobbying

### 8. Alameda_Other_Payments.csv
Miscellaneous payments and fees
- **Columns**: Payment types, recipients, amounts
- **Use**: Capture additional financial relationships

### 9. Alameda_Addresses.csv
Contact information for filers
- **Columns**: Address, city, state, zip, phone, email
- **Use**: Contact details for all Alameda entities

### 10. Alameda_Summary.csv
Aggregated statistics across all tables
- **Columns**: FILER_ID, ENTITY_TYPE, TOTAL_FILINGS, TOTAL_PAYMENTS, TOTAL_EXPENDITURES, etc.
- **Use**: Quick overview of each organization's lobbying activity

---

## Data Dictionary

### Key Identifiers
- **FILER_ID**: Unique identifier for each lobbying entity (PRIMARY KEY)
- **FILING_ID**: Unique identifier for each disclosure filing
- **AMEND_ID**: Amendment version (0 = original, 1-999 = amendments)

### Entity Codes (ENTITY_CD)
- **FRM**: Lobbying Firm (PROVIDER)
- **LEM**: Lobbyist Employer (PURCHASER)
- **LCO**: Lobbying Coalition (PURCHASER)
- **LBY**: Lobbyist (PROVIDER)
- **IND**: Individual spending >$5,000 (PURCHASER)

### Financial Fields
- **FEES_AMT**: Lobbying fees paid to firm
- **REIMB_AMT**: Reimbursements
- **ADVAN_AMT**: Advances/retainers
- **PER_TOTAL**: Period total (quarterly)
- **CUM_TOTAL**: Cumulative total (year-to-date)

### Date Fields
- **RPT_DATE**: Report filing date
- **FROM_DATE**: Period start date
- **THRU_DATE**: Period end date
- **CUM_BEG_DT**: Cumulative period begin date

---

## Understanding the Data

### Lobbying Relationship Flow

```
PURCHASER Organizations          PROVIDER Organizations
(Buying lobbying services)  →    (Selling lobbying services)
━━━━━━━━━━━━━━━━━━━━━━━━━━━     ━━━━━━━━━━━━━━━━━━━━━━━━━━
┌─────────────────────┐          ┌─────────────────────┐
│ LEM: Alameda County │          │ FRM: Smith & Jones  │
│ (Employer)          │  ────→   │ (Lobbying Firm)     │
└─────────────────────┘          └─────────────────────┘
         │                                  │
         │ Hires                            │ Employs
         │                                  │
         ▼                                  ▼
    Pays fees to                    ┌─────────────────────┐
    lobbying firm                   │ LBY: Jane Lobbyist  │
    (see LPAY_CD)                   │ (Individual)        │
                                    └─────────────────────┘
```

### Example Analysis Queries

**1. Total lobbying spending by Alameda entities:**
```sql
SELECT
    FILER_NAML,
    SUM(CAST(PER_TOTAL AS FLOAT64)) as total_spent
FROM Alameda_Payments.csv
WHERE ALAMEDA_RELATION = 'PURCHASER'
GROUP BY FILER_NAML
ORDER BY total_spent DESC;
```

**2. Which firms did Alameda County hire?**
```sql
SELECT DISTINCT
    p.EMPLR_NAML as alameda_employer,
    d.FIRM_NAME as lobbying_firm,
    p.PER_TOTAL as quarterly_payment
FROM Alameda_Payments.csv p
JOIN Alameda_Lobby_Disclosures.csv d
    ON p.FILING_ID = d.FILING_ID
WHERE p.EMPLR_NAML LIKE '%ALAMEDA%';
```

**3. Campaign contributions from Alameda lobbyists:**
```sql
SELECT
    CTRIB_NAML as contributor,
    RECIP_NAML as recipient,
    AMOUNT,
    CTRIB_DATE
FROM Alameda_Campaign_Contributions.csv
ORDER BY CAST(AMOUNT AS FLOAT64) DESC;
```

---

## Troubleshooting

### Error: "Could not find credentials"
**Solution**: Verify `.env` file exists with correct `GOOGLE_APPLICATION_CREDENTIALS` path

### Error: "Permission denied on BigQuery"
**Solution**: Service account needs BigQuery Data Viewer and Job User roles

### Empty CSV files
**Possible causes**:
1. Dataset name in `.env` doesn't match actual BigQuery dataset
2. No data in tables containing "ALAMEDA" (unlikely)
3. Check BigQuery table names match script expectations

### Script hangs on specific table
**Solution**:
- Check BigQuery query logs for errors
- Verify table exists in dataset
- Some tables may be legitimately empty for Alameda entities

---

## Updating the Extraction

### Add new tables
1. Identify table name and primary Alameda-related column
2. Add query to `extract_alameda_data.py`:
```python
queries.append({
    'query': """
        WITH alameda_filers AS (
            SELECT DISTINCT FILER_ID FROM `{project}.{dataset}.FILERS_CD`
            WHERE UPPER(FILER_NAML) LIKE '%ALAMEDA%'
        )
        SELECT t.*
        FROM `{project}.{dataset}.YOUR_TABLE_NAME` t
        WHERE t.FILER_ID IN (SELECT FILER_ID FROM alameda_filers)
    """,
    'filename': 'Alameda_YourTableName.csv',
    'description': 'your table description'
})
```

### Filter by date range
Add WHERE clause to queries:
```sql
AND RPT_DATE BETWEEN '2024-01-01' AND '2025-12-31'
```

### Export to different format
Modify `export_table()` function:
```python
# For JSON
df.to_json(output_path, orient='records', indent=2)

# For Excel
df.to_excel(output_path, index=False)
```

---

## Related Files

- [extract_alameda_data.py](extract_alameda_data.py) - Python extraction script
- [extract_alameda_data.sql](extract_alameda_data.sql) - Raw SQL queries
- [SQL Queries/Payment to Lobbyist.sql](SQL%20Queries/Payment%20to%20Lobbyist.sql) - Example query pattern
- [Documents/California_Lobbying_Tables_Documentation.md](Documents/California_Lobbying_Tables_Documentation.md) - Full schema documentation

---

## Next Steps

### 1. Run Initial Extraction
```bash
python extract_alameda_data.py
```

### 2. Review Output
Check `alameda_data_exports/` directory for CSV files

### 3. Analyze Data
Load CSVs into your analysis tool:
- Excel/Google Sheets for quick review
- Python pandas for detailed analysis
- Tableau/Power BI for visualization

### 4. Ask SQL Expert for Help
If you need custom queries or analysis:
```
"@sql-database-expert help me analyze payment patterns in the Alameda lobbying data"
```

---

## Support

**Questions about the data structure?**
See [Documents/California_Lobbying_Tables_Documentation.md](Documents/California_Lobbying_Tables_Documentation.md)

**Need custom queries?**
Use the sql-database-expert agent: `@sql-database-expert`

**Want to understand table relationships?**
The SQL expert prioritizes relationship analysis - just ask!

---

**Generated by**: Claude Code
**Last Updated**: October 24, 2025
