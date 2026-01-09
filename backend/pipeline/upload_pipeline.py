"""
CAL-ACCESS Data Upload Pipeline

Downloads CAL-ACCESS lobbying data files and uploads them to BigQuery.
"""
import os
import logging
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv

from upload import upload_to_bigquery
from rowtypeforce import row_type_force
from Bigquery_connection import bigquery_connect
from Bignewdownload_2 import Bignewdownload

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def extract_table_name(filepath):
    """
    Extract BigQuery table name from filename.

    Example: '2025-01-01_cvr_lobby_disclosure_cd.csv' -> 'cvr_lobby_disclosure_cd'
    """
    stem = Path(filepath).stem
    parts = stem.split("_", 1)
    return parts[1] if len(parts) > 1 else stem


def get_files_to_process(download_dir, today):
    """
    Get list of CSV files to process, excluding cleaned and project files.
    """
    import glob

    # Try downloading new files first
    downloaded_files = Bignewdownload(download_dir)

    if downloaded_files:
        all_files = downloaded_files
    else:
        all_files = glob.glob(f"{download_dir}/{today}/*.csv")

    # Filter out cleaned and project files
    files = [
        f for f in all_files
        if not (os.path.basename(f).startswith("clean") or
                os.path.basename(f).startswith("project"))
    ]

    return files


def main(dry_run=False):
    """
    Main pipeline execution.

    Args:
        dry_run: If True, skip actual uploads (for testing)
    """
    load_dotenv()

    # Configuration from environment
    download_dir = os.getenv('DOWNLOAD_DIR', './downloaded_files/')
    credentials_path = os.getenv('CREDENTIALS_LOCATION')
    project_id = os.getenv('BIGQUERY_PROJECT_ID', 'ca-lobby')

    if not credentials_path:
        logger.error("CREDENTIALS_LOCATION environment variable not set")
        return

    today = datetime.today().strftime('%Y-%m-%d')

    # Get files to process
    files_to_process = get_files_to_process(download_dir, today)

    if not files_to_process:
        logger.warning("No files to process")
        return

    logger.info(f"Found {len(files_to_process)} files to process")

    client = None
    try:
        client = bigquery_connect(credentials_path)

        if client is None:
            logger.error("Failed to connect to BigQuery")
            return

        for filepath in files_to_process:
            try:
                logger.info(f"Processing: {filepath}")

                # Extract table name from filename
                table_name = extract_table_name(filepath)
                full_table_id = f'ca-lobby.ca_lobby.{table_name}'

                logger.info(f"Target table: {full_table_id}")

                # Force row types to match BigQuery schema
                cleaned_df = row_type_force(client, full_table_id, filepath)

                if dry_run:
                    logger.info(f"[DRY RUN] Would upload {len(cleaned_df)} rows to {full_table_id}")
                else:
                    # Upload to BigQuery
                    upload_to_bigquery(cleaned_df, full_table_id, credentials_path, project_id)

            except Exception as e:
                logger.error(f"Failed to process {filepath}: {e}")
                continue  # Continue with next file

    except Exception as e:
        logger.error(f"Pipeline failed: {e}")
        raise
    finally:
        if client:
            client.close()
            logger.info("BigQuery client closed")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='CAL-ACCESS Data Upload Pipeline')
    parser.add_argument('--dry-run', action='store_true', help='Skip actual uploads')
    args = parser.parse_args()

    main(dry_run=args.dry_run)
