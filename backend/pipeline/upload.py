"""
BigQuery Upload Module

Uploads DataFrames to BigQuery tables with schema validation.
"""
import logging

from google.cloud import bigquery
from google.oauth2 import service_account
from google.api_core.exceptions import GoogleAPICallError, NotFound
from dotenv import load_dotenv

from determine_df import ensure_dataframe

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

load_dotenv()


def validate_schema(df, client, table_id):
    """
    Verify DataFrame columns match BigQuery table schema.

    Args:
        df: pandas DataFrame to validate
        client: BigQuery client
        table_id: Full table ID (project.dataset.table)

    Returns:
        bool: True if validation passes, False otherwise
    """
    try:
        table = client.get_table(table_id)
        expected_cols = {field.name for field in table.schema}
        actual_cols = set(df.columns)

        missing = expected_cols - actual_cols
        extra = actual_cols - expected_cols

        if missing:
            logger.warning(f"Missing columns in DataFrame: {missing}")
        if extra:
            logger.info(f"Extra columns (will be ignored by BigQuery): {extra}")

        # Return True if no critical missing columns
        return len(missing) == 0

    except NotFound:
        logger.error(f"Table not found: {table_id}")
        return False
    except Exception as e:
        logger.error(f"Schema validation error: {e}")
        return False


def upload_to_bigquery(inputfile, table_id, credentials_path, project_id):
    """
    Uploads a CSV file or DataFrame to a BigQuery table.

    Args:
        inputfile: Path to CSV file or pandas DataFrame
        table_id: The BigQuery table ID (e.g., "project.dataset.table_name")
        credentials_path: Path to the service account JSON key file
        project_id: The Google Cloud project ID

    Returns:
        bool: True if upload succeeded, False otherwise
    """
    try:
        # Load credentials
        credentials = service_account.Credentials.from_service_account_file(credentials_path)

        # Initialize BigQuery client
        client = bigquery.Client(credentials=credentials, project=project_id)

        # Ensure we have a DataFrame
        df = ensure_dataframe(inputfile)

        # Validate schema before upload
        if not validate_schema(df, client, table_id):
            logger.error(f"Schema validation failed for {table_id}")
            return False

        # Configure the load job
        job_config = bigquery.LoadJobConfig(
            write_disposition=bigquery.WriteDisposition.WRITE_APPEND
        )

        # Upload the DataFrame to BigQuery
        logger.info(f"Uploading {len(df)} rows to {table_id}...")
        job = client.load_table_from_dataframe(df, table_id, job_config=job_config)

        # Wait for the job to complete
        job.result()

        logger.info(f"Successfully uploaded {len(df)} rows to {table_id}")
        return True

    except FileNotFoundError:
        logger.error(f"File not found: {inputfile}")
        return False
    except GoogleAPICallError as e:
        logger.error(f"Google API error: {e}")
        return False
    except Exception as e:
        logger.error(f"Upload failed: {e}")
        return False



if __name__ == "__main__":
    """
    # Load environment variables from .env file
    load_dotenv()
    # Define your variables
    inputfile = "/Users/michaelingram/Documents/GitHub/CA_lobby/Downloaded_files/2025-05-14/2025-05-14_cvr_registration_cd.csv"
    table_id = "ca-lobby.ca_lobby.cvr_registration"  # Replace with your BigQuery table ID
    project_id = "ca-lobby"  # Replace with your Google Cloud project ID
    credentials_path = os.getenv('CREDENTIALS_LOCATION')  # Replace with the path to your service account key
    # Call the function to upload the CSV file to BigQuery
    upload_to_bigquery(inputfile, table_id, credentials_path,project_id)
    """