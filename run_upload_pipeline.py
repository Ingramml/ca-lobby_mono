#!/usr/bin/env python3
"""
Wrapper script to run full upload pipeline from project root.
Delegates to pipeline/upload_pipeline.py
"""

import sys
import os

# Add pipeline directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'pipeline'))

# Import and run the pipeline
import upload_pipeline

print("\n✅ Upload pipeline execution complete!")
print("\nNOTE: DATE columns need to be re-converted after upload.")
print("Run: python3 convert_date_columns.py")
