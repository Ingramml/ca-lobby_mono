"""
Row Type Force Module

Enforces BigQuery schema types on pandas DataFrames before upload.
"""
import logging
import os

import pandas as pd
from dotenv import load_dotenv

from Bigquery_connection import bigquery_connect
from determine_df import ensure_dataframe

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)



def _log_coercion(column_name, original_count, new_count, column_type):
    """Log warning if values were lost during type coercion."""
    lost = original_count - new_count
    if lost > 0:
        pct = (lost / original_count * 100) if original_count > 0 else 0
        logger.warning(
            f"Column '{column_name}': {lost} values coerced to NaN during {column_type} conversion ({pct:.1f}%)"
        )


def row_type_force(client, tablename, inputfile):
    """
    Forces the row type of a DataFrame to match the schema of a BigQuery table.

    Args:
        client: BigQuery client
        tablename: The name of the BigQuery table (project.dataset.table)
        inputfile: Path to CSV file or pandas DataFrame

    Returns:
        pd.DataFrame: The DataFrame with forced row types
    """
    df = ensure_dataframe(inputfile)

    # Get file info for saving cleaned version
    if isinstance(inputfile, str):
        working_dir = os.path.dirname(inputfile)
        filename = os.path.basename(inputfile)
    else:
        working_dir = '.'
        filename = 'dataframe.csv'

    # Get the schema of the BigQuery table
    table = client.get_table(tablename)
    schema = table.schema

    logger.info(f"Forcing types for {len(df)} rows to match {tablename} schema")

    # Iterate over the schema to get column names and types
    for field in schema:
        column_name = field.name
        column_type = field.field_type

        # Skip columns that don't exist in the DataFrame
        if column_name not in df.columns:
            logger.debug(f"Column '{column_name}' not in DataFrame, skipping")
            continue

        original_count = df[column_name].notna().sum()

        if column_type == 'STRING':
            # Replace NaN with empty string for string columns
            df[column_name] = df[column_name].fillna('').astype(str)
            # Convert 'nan' strings back to empty string
            df[column_name] = df[column_name].replace('nan', '')

        elif column_type == 'INTEGER':
            df[column_name] = pd.to_numeric(df[column_name], errors='coerce').astype('Int64')
            _log_coercion(column_name, original_count, df[column_name].notna().sum(), column_type)

        elif column_type == 'FLOAT':
            df[column_name] = pd.to_numeric(df[column_name], errors='coerce').astype('float64')
            _log_coercion(column_name, original_count, df[column_name].notna().sum(), column_type)

        elif column_type == 'BOOLEAN':
            df[column_name] = df[column_name].astype(bool)

        elif column_type == 'TIMESTAMP':
            df[column_name] = pd.to_datetime(df[column_name], errors='coerce')
            _log_coercion(column_name, original_count, df[column_name].notna().sum(), column_type)

        elif column_type == 'DATE':
            # Use string format for DATE to avoid Python date object issues
            df[column_name] = pd.to_datetime(df[column_name], errors='coerce').dt.strftime('%Y-%m-%d')
            _log_coercion(column_name, original_count, df[column_name].notna().sum(), column_type)

        elif column_type == 'DATETIME':
            df[column_name] = pd.to_datetime(df[column_name], errors='coerce')
            _log_coercion(column_name, original_count, df[column_name].notna().sum(), column_type)

        elif column_type == 'TIME':
            df[column_name] = pd.to_datetime(df[column_name], errors='coerce').dt.time
            _log_coercion(column_name, original_count, df[column_name].notna().sum(), column_type)

        elif column_type == 'BYTES':
            df[column_name] = df[column_name].apply(
                lambda x: x.encode('utf-8') if isinstance(x, str) else x
            )

    # Save cleaned file
    cleanedfile = os.path.join(working_dir, f"cleaned_{filename}")
    df.to_csv(cleanedfile, index=False)
    logger.info(f"Saved cleaned data to {cleanedfile}")

    return df


if __name__ == "__main__":
    """
    #inputfile='/Users/michaelingram/Documents/GitHub/CA_lobby/Downloaded_files/2025-05-14/2025-05-14_cvr_registration_cd.csv'
    # Load environment variables from .env file
    load_dotenv()
    # Define your variables
    credentials_path = os.getenv('CREDENTIALS_LOCATION')  # Replace with the path to your service account key
    project_id = os.getenv('PROJECT_ID')  # Replace with your Google Cloud project ID
    client = bigquery_connect(credentials_path)
    tablename = 'ca-lobby.ca_lobby.cvr_registration'
    row_type_force()
    """