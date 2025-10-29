# Data Pipeline - California Lobbying Database

This folder contains all scripts for downloading, processing, and uploading California lobbying data to BigQuery.

## Pipeline Files

### Core Pipeline Scripts

**1. `Bignewdownload_2.py`** - Main download script
- Downloads fresh data from California lobbying database via BLN API
- Handles SSL certificate issues
- Saves CSVs to `Downloaded_files/YYYY-MM-DD/`
- **Usage**: `python3 pipeline/Bignewdownload_2.py`

**2. `upload_pipeline.py`** - Full upload orchestrator
- Coordinates download → type forcing → upload
- Processes all 9 tables sequentially
- **Usage**: `python3 pipeline/upload_pipeline.py`

**3. `upload.py`** - BigQuery upload module
- Uploads DataFrames to BigQuery tables
- **Current**: Full table replacement (WRITE_TRUNCATE)
- **Future**: Will support incremental mode
- **Usage**: Called by `upload_pipeline.py`

### Helper Modules

**4. `Bigquery_connection.py`** - BigQuery connection handler
- Manages BigQuery client authentication
- Loads credentials from environment variables
- **Usage**: `client = bigquery_connect(credentials_path)`

**5. `rowtypeforce.py`** - Schema type enforcement
- Converts DataFrame column types to match BigQuery schema
- **Fixed**: Now skips non-existent columns (like *_DATE columns)
- Saves cleaned CSVs for debugging
- **Usage**: Called by `upload_pipeline.py`

**6. `determine_df.py`** - DataFrame loader
- Ensures input is converted to pandas DataFrame
- Handles CSV files and DataFrame objects
- **Usage**: `df = ensure_dataframe(input_file)`

## Documentation

**7. `INCREMENTAL_UPLOAD_PLAN.md`** - Future enhancement plan
- Detailed plan for incremental uploads (only upload new data)
- Expected improvements: 40x faster, 97% cost reduction
- Preserves DATE columns created in BigQuery
- Ready to implement when needed

---

## Pipeline Flow

```
┌─────────────────────────────────────────────────────────────┐
│                    CURRENT PIPELINE                          │
└─────────────────────────────────────────────────────────────┘

1. DOWNLOAD (Bignewdownload_2.py)
   ↓
   Downloads 9 CSV files (~755 MB)
   ↓
   Saves to: Downloaded_files/2025-10-24/

2. TYPE FORCING (rowtypeforce.py)
   ↓
   Reads BigQuery table schema
   ↓
   Converts DataFrame column types to match
   ↓
   Saves cleaned CSV

3. UPLOAD (upload.py)
   ↓
   Uploads DataFrame to BigQuery
   ↓
   Mode: WRITE_TRUNCATE (full replacement)
   ↓
   ⚠️  LOSES DATE COLUMNS

4. DATE CONVERSION (convert_date_columns.py - not in pipeline/)
   ↓
   Re-converts 17 DATE columns
   ↓
   Converts 50M+ rows (slow)
```

---

## Tables Processed

| Table | Typical Size | Primary Key |
|-------|-------------|-------------|
| cvr_lobby_disclosure_cd | 538K rows | FILING_ID + AMEND_ID |
| cvr_registration_cd | 96K rows | FILING_ID + AMEND_ID |
| filername_cd | 1.3M rows | FILER_ID + EFFECT_DT |
| lpay_cd | 811K rows | FILING_ID + AMEND_ID + LINE_ITEM |
| lexp_cd | 258K rows | FILING_ID + AMEND_ID + LINE_ITEM |
| lemp_cd | 604K rows | FILING_ID + AMEND_ID + LINE_ITEM |
| lccm_cd | 121K rows | FILING_ID + AMEND_ID + LINE_ITEM |
| loth_cd | 25K rows | FILING_ID + AMEND_ID + LINE_ITEM |
| latt_cd | 201K rows | FILING_ID + AMEND_ID + LINE_ITEM |

**Total: ~4 million rows per upload**

---

## Environment Variables Required

Add these to `.env` file in project root:

```bash
# BLN API Key for data downloads
BLN_API='your_api_key_here'

# Google Cloud credentials
CREDENTIALS_LOCATION='/path/to/service-account-key.json'

# Project ID
PROJECT_ID='ca-lobby'
```

---

## Common Commands

### Full Pipeline Run
```bash
# Download and upload all data
python3 pipeline/upload_pipeline.py
```

### Download Only
```bash
# Just download CSVs, don't upload
python3 pipeline/Bignewdownload_2.py
```

### Upload from Existing CSVs
```bash
# Edit upload_pipeline.py to skip download section
# Or manually call upload functions
```

### Test Single Table
```python
from pipeline.upload import upload_to_bigquery
import os

upload_to_bigquery(
    inputfile='path/to/file.csv',
    table_id='ca-lobby.ca_lobby.table_name',
    credentials_path=os.getenv('CREDENTIALS_LOCATION'),
    project_id='ca-lobby'
)
```

---

## Known Issues & Fixes

### Issue 1: SSL Certificate Error (FIXED ✓)
**Error**: `ssl.SSLCertVerificationError: certificate verify failed`

**Fix**: Added to `Bignewdownload_2.py`:
```python
ssl._create_default_https_context = ssl._create_unverified_context
```

### Issue 2: DATE Columns Lost on Upload (KNOWN)
**Problem**: Upload replaces entire table, deleting *_DATE columns

**Workaround**: Re-run `convert_date_columns.py` after each upload

**Solution**: Implement incremental uploads (see INCREMENTAL_UPLOAD_PLAN.md)

### Issue 3: rowtypeforce KeyError (FIXED ✓)
**Error**: `KeyError: 'PMT_DATE_DATE'`

**Fix**: Added column existence check in `rowtypeforce.py`:
```python
if column_name not in df.columns:
    continue
```

---

## Performance Metrics

### Current Performance:
- **Download**: 3-5 minutes (755 MB)
- **Type Forcing**: 2-3 minutes
- **Upload**: 3-5 minutes
- **DATE Conversion**: 5-10 minutes
- **Total**: ~15 minutes per full refresh

### With Incremental (Planned):
- **Download**: 3-5 minutes (same - API limitation)
- **Incremental Filter**: 10 seconds
- **Upload**: 30 seconds (only new rows)
- **DATE Conversion**: 10 seconds (only new rows)
- **Total**: ~5 minutes (3x faster)

---

## Future Enhancements

See [INCREMENTAL_UPLOAD_PLAN.md](INCREMENTAL_UPLOAD_PLAN.md) for details:

1. ✅ **Incremental Upload Strategy**
   - Only upload new FILING_IDs
   - Preserve existing DATE columns
   - 40x faster, 97% cost reduction

2. 📋 **Metadata Tracking**
   - Track last upload date per table
   - Monitor upload success/failure
   - Record row counts and growth

3. 📋 **Error Recovery**
   - Retry logic for network failures
   - Checkpoint/resume for large uploads
   - Alert on schema changes

4. 📋 **Automated Scheduling**
   - Daily cron job for downloads
   - Incremental uploads only
   - Email notifications on completion

---

## Maintenance

### Weekly Tasks:
- [ ] Check upload logs for errors
- [ ] Verify DATE columns exist in all tables
- [ ] Monitor BigQuery storage usage

### Monthly Tasks:
- [ ] Review upload performance metrics
- [ ] Check for schema changes in source data
- [ ] Update API key if expired

### Quarterly Tasks:
- [ ] Implement incremental upload feature
- [ ] Optimize BigQuery table partitioning
- [ ] Review and clean up old downloaded CSVs

---

## Troubleshooting

### Pipeline fails at download step
1. Check BLN_API key in `.env`
2. Verify internet connection
3. Check SSL certificate fix is applied

### Pipeline fails at upload step
1. Check CREDENTIALS_LOCATION in `.env`
2. Verify BigQuery permissions
3. Check table schemas haven't changed

### DATE columns missing after upload
- This is expected (current limitation)
- Run: `python3 convert_date_columns.py`
- **Better solution**: Implement incremental uploads

---

## Contact & Support

- **Project**: California Lobbying Database
- **BigQuery Project**: ca-lobby
- **Dataset**: ca_lobby
- **Documentation**: See root README.md for full project docs
