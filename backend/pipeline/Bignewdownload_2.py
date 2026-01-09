"""
CAL-ACCESS Data Downloader

Downloads lobbying data files from BLN (Balancing Act) API.
"""
import bln
import ssl
import datetime
import logging
import os

import pandas as pd
import urllib3
from bln import Client
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Disable SSL warnings (only for development)
# Note: SSL verification is disabled due to certificate issues with Python 3.13 and the BLN API
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def Bignewdownload(output_dir):
    """
    Download CAL-ACCESS data files from BLN API.

    Args:
        output_dir: Directory to save downloaded files

    Returns:
        list: Paths of successfully downloaded files
    """
    # Disable SSL certificate verification for this session
    # This is needed because some systems have certificate issues with Python 3.13
    ssl._create_default_https_context = ssl._create_unverified_context

    today = datetime.date.today()
    work_dir = os.path.join(output_dir, str(today))

    if not os.path.exists(work_dir):
        os.makedirs(work_dir)
        logger.info(f"Created directory: {work_dir}")

    # Load environment variables
    load_dotenv()

    api_key = os.getenv('BLN_API')
    if not api_key:
        logger.error("BLN_API environment variable not set")
        return []

    # Get project ID from environment (with fallback for backwards compatibility)
    project_id = os.getenv(
        'BLN_PROJECT_ID',
        'UHJvamVjdDo2MDVjNzdiYS0wODI4LTRlOTEtOGM3OC03ZjA4NGI2ZDEwZWE='
    )

    client = Client(api_key)
    bln.pandas.register(pd)

    # CAL-ACCESS lobbying data files
    file_names = [
        "cvr_lobby_disclosure_cd.csv",
        "cvr_registration_cd.csv",
        "latt_cd.csv",
        "lccm_cd.csv",
        "lemp_cd.csv",
        "lexp_cd.csv",
        "loth_cd.csv",
        "lpay_cd.csv",
        "filername_cd.csv"
    ]

    file_list = []

    for filename in file_names:
        downloaded_file = os.path.join(work_dir, f"{today}_{filename}")

        if os.path.exists(downloaded_file):
            logger.info(f"File already exists, skipping: {downloaded_file}")
            continue

        try:
            logger.info(f"Downloading {filename}...")
            df = pd.read_bln(project_id, filename, api_key, low_memory=False)
            df.to_csv(downloaded_file, index=False)
            file_list.append(downloaded_file)
            logger.info(f"Downloaded {len(df)} rows to {downloaded_file}")
        except Exception as e:
            logger.error(f"Failed to download {filename}: {e}")
            continue

    logger.info(f"Downloaded {len(file_list)} files")
    return file_list


# Backwards compatibility alias
Bignewdoanload = Bignewdownload


if __name__ == "__main__":
    load_dotenv()
    output_dir = os.getenv('DOWNLOAD_DIR', './downloaded_files/')
    Bignewdownload(output_dir)
