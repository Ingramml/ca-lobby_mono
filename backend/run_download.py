#!/usr/bin/env python3
"""
Wrapper script to run download pipeline from project root.
Delegates to pipeline/Bignewdownload_2.py
"""

import sys
import os

# Add pipeline directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'pipeline'))

from Bignewdownload_2 import Bignewdoanload

if __name__ == "__main__":
    output_dir = '/Users/michaelingram/Documents/GitHub/CA_lobby/Downloaded_files'
    print("Starting download pipeline...")
    print(f"Output directory: {output_dir}")

    files = Bignewdoanload(output_dir)

    if files:
        print(f"\n✅ Download complete! {len(files)} files downloaded.")
        for f in files:
            print(f"  - {f}")
    else:
        print("\n✅ Download complete! Files already exist or were downloaded.")
