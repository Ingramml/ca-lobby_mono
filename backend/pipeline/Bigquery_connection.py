"""
BigQuery Connection Module

Manages BigQuery client connections and credential handling.
"""
import logging
import os

from google.cloud import bigquery
from google.oauth2 import service_account
from google.api_core.exceptions import GoogleAPICallError
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def bigquery_connect(credentials_path):
    """
    Create a BigQuery client connection.

    Args:
        credentials_path: Path to service account JSON key file

    Returns:
        bigquery.Client or None if connection fails
    """
    try:
        load_dotenv()

        project_id = get_project_id_from_credentials(credentials_path)
        if not project_id:
            return None

        credentials = service_account.Credentials.from_service_account_file(credentials_path)
        client = bigquery.Client(credentials=credentials, project=project_id)

        # Test the connection by listing datasets
        list(client.list_datasets())
        logger.info(f"Successfully connected to BigQuery project: {project_id}")

        return client

    except FileNotFoundError:
        logger.error(f"Credentials file not found: {credentials_path}")
        return None
    except GoogleAPICallError as e:
        logger.error(f"Google API error during connection: {e}")
        return None
    except Exception as e:
        logger.error(f"Failed to connect to BigQuery: {e}")
        return None



def get_project_id_from_credentials(credentials_path):
    """
    Extract the project ID from a service account JSON credentials file.

    Args:
        credentials_path: Path to the service account JSON key file

    Returns:
        str: The project ID, or None if extraction fails
    """
    try:
        credentials = service_account.Credentials.from_service_account_file(credentials_path)
        project_id = credentials.project_id
        logger.debug(f"Extracted project ID: {project_id}")
        return project_id

    except FileNotFoundError:
        logger.error(f"Credentials file not found: {credentials_path}")
        return None
    except Exception as e:
        logger.error(f"Failed to extract project ID: {e}")
        return None





if __name__ == "__main__":
    """
    # Load environment variables from .env file
    load_dotenv()

    # Get the credentials path from the .env file
    credentials_path = os.getenv('CREDENTIALS_LOCATION')  # Path to your service account JSON file

    if not credentials_path:
        print("❌ CREDENTIALS_LOCATION is not set in the .env file.")
    else:
        try:
            # Extract the project ID from the credentials
            project_id = get_project_id_from_credentials(credentials_path)

            # Load credentials
            credentials = service_account.Credentials.from_service_account_file(credentials_path)

            # Initialize BigQuery client with explicit credentials
            client = bigquery.Client(credentials=credentials, project=project_id)

            # Test the connection by listing datasets
            datasets = list(client.list_datasets())
            print(f"✅ Successfully connected to BigQuery project: {project_id}")
            print(f"Available datasets: {[dataset.dataset_id for dataset in datasets]}")

        except Exception as e:
            print(f"❌ An error occurred while connecting to BigQuery: {e}")
        """