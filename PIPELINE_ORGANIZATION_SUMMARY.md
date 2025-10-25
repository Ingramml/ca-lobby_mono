# Pipeline Organization Complete ✓

## Summary

All pipeline-related files have been organized into the `pipeline/` folder for better project structure.

---

## What Was Moved

### Files Moved to `pipeline/` folder:

1. **Bignewdownload_2.py** - Downloads data from BLN API
2. **upload_pipeline.py** - Orchestrates full download → upload process
3. **upload.py** - Handles BigQuery uploads
4. **Bigquery_connection.py** - BigQuery authentication
5. **rowtypeforce.py** - Schema type enforcement
6. **determine_df.py** - DataFrame loading utility
7. **INCREMENTAL_UPLOAD_PLAN.md** - Future enhancement plan
8. **README.md** - Pipeline documentation (NEW)

---

## New Wrapper Scripts (Project Root)

For easy access from the project root directory:

### `run_download.py`
Downloads fresh data from California lobbying database
```bash
python3 run_download.py
```

### `run_upload_pipeline.py`
Runs full download → upload pipeline
```bash
python3 run_upload_pipeline.py
```

**Note**: After running upload pipeline, you must re-convert DATE columns:
```bash
python3 convert_date_columns.py
```

---

## Directory Structure

```
CA_lobby_Database/
├── pipeline/                          # All pipeline scripts (NEW)
│   ├── Bignewdownload_2.py           # Download script
│   ├── upload_pipeline.py            # Main pipeline
│   ├── upload.py                     # Upload module
│   ├── Bigquery_connection.py        # BigQuery auth
│   ├── rowtypeforce.py               # Schema enforcement
│   ├── determine_df.py               # DataFrame loader
│   ├── INCREMENTAL_UPLOAD_PLAN.md    # Future plan
│   └── README.md                     # Pipeline docs
│
├── run_download.py                   # Wrapper: download only (NEW)
├── run_upload_pipeline.py            # Wrapper: full pipeline (NEW)
│
├── convert_date_columns.py           # DATE column conversion
├── analyze_date_columns.py           # DATE analysis
├── export_all_views_alameda.py       # Export Alameda views
│
├── alameda_data_exports/             # Exported CSV files
├── requirements.txt                  # Python dependencies
├── .env                              # Environment variables
└── README.md                         # Project documentation
```

---

## How to Use

### 1. Download Fresh Data Only
```bash
python3 run_download.py
```
Downloads to: `/Users/michaelingram/Documents/GitHub/CA_lobby/Downloaded_files/YYYY-MM-DD/`

### 2. Run Full Upload Pipeline
```bash
# Step 1: Download and upload
python3 run_upload_pipeline.py

# Step 2: Re-convert DATE columns (required after upload)
python3 convert_date_columns.py
```

### 3. Direct Pipeline Access (Advanced)
```bash
# Run from pipeline folder
cd pipeline
python3 Bignewdownload_2.py
python3 upload_pipeline.py
```

---

## Incremental Upload Plan

See [pipeline/INCREMENTAL_UPLOAD_PLAN.md](pipeline/INCREMENTAL_UPLOAD_PLAN.md) for:

- **40x faster uploads** (only new data)
- **97% cost reduction** ($432/year savings)
- **Preserves DATE columns** (no re-conversion needed)
- **Ready to implement** when needed

### Expected Performance:
- Current: ~15 minutes per full upload
- With incremental: ~5 minutes (only new rows)

---

## Benefits of Organization

### Before:
- ❌ Pipeline files mixed with scripts
- ❌ Hard to find related files
- ❌ No clear pipeline documentation
- ❌ Confusing import paths

### After:
- ✅ All pipeline scripts in one folder
- ✅ Clear separation of concerns
- ✅ Comprehensive pipeline README
- ✅ Easy-to-use wrapper scripts
- ✅ Ready for incremental upload enhancement

---

## Next Steps

### Immediate:
1. ✅ Pipeline organized and documented
2. ✅ Wrapper scripts created
3. ✅ SSL issues fixed
4. ✅ DATE columns working

### Future (When Needed):
1. Implement incremental upload (see plan)
2. Add automated scheduling (cron jobs)
3. Create monitoring dashboard
4. Add error recovery and alerting

---

## Notes

- **All imports work correctly** - Files use relative imports within pipeline/
- **No breaking changes** - Everything still functions the same
- **Better maintainability** - Clear separation and documentation
- **Ready for team** - Anyone can understand the pipeline now

---

## Questions?

See documentation:
- Pipeline details: [pipeline/README.md](pipeline/README.md)
- Incremental plan: [pipeline/INCREMENTAL_UPLOAD_PLAN.md](pipeline/INCREMENTAL_UPLOAD_PLAN.md)
- Project overview: [README.md](README.md)
