"""
DataFrame Utility Module

Ensures input data is a pandas DataFrame.
"""
import logging
import os

import pandas as pd

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def ensure_dataframe(input_data):
    """
    Ensure the input is a pandas DataFrame.

    If the input is a CSV file path, reads the file into a DataFrame.
    If the input is already a DataFrame, returns it as-is.

    Args:
        input_data: Either a pandas DataFrame or path to a CSV file

    Returns:
        pandas.DataFrame

    Raises:
        ValueError: If file path is invalid or file type is unsupported
        TypeError: If input is neither a DataFrame nor a string path
    """
    if isinstance(input_data, pd.DataFrame):
        logger.debug("Input is already a DataFrame")
        return input_data

    elif isinstance(input_data, str):
        if os.path.isfile(input_data) and input_data.lower().endswith('.csv'):
            logger.info(f"Reading CSV file: {input_data}")
            return pd.read_csv(input_data, encoding='utf-8')
        else:
            raise ValueError(f"Invalid file path or unsupported file type: {input_data}")

    else:
        raise TypeError("Input must be either a pandas DataFrame or a CSV file path.")

if __name__ == "__main__":
    """
    
    """    