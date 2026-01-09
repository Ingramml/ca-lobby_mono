"""
Shared pytest fixtures for pipeline tests.
"""
import os
import tempfile

import pandas as pd
import pytest


@pytest.fixture
def sample_dataframe():
    """Create a sample DataFrame for testing."""
    return pd.DataFrame({
        'FILING_ID': [1, 2, 3],
        'AMEND_ID': [0, 0, 1],
        'FILER_NAML': ['Company A', 'Company B', 'Company C'],
        'RPT_DATE': ['2025-01-01', '2025-01-02', '2025-01-03'],
        'AMOUNT': [1000.50, 2000.75, 3000.25]
    })


@pytest.fixture
def sample_csv_file(sample_dataframe, tmp_path):
    """Create a temporary CSV file for testing."""
    csv_path = tmp_path / "test_data.csv"
    sample_dataframe.to_csv(csv_path, index=False)
    return str(csv_path)


@pytest.fixture
def mock_bigquery_schema():
    """Mock BigQuery schema fields."""
    class MockField:
        def __init__(self, name, field_type):
            self.name = name
            self.field_type = field_type

    return [
        MockField('FILING_ID', 'INTEGER'),
        MockField('AMEND_ID', 'INTEGER'),
        MockField('FILER_NAML', 'STRING'),
        MockField('RPT_DATE', 'DATE'),
        MockField('AMOUNT', 'FLOAT')
    ]


@pytest.fixture
def mock_bigquery_table(mock_bigquery_schema):
    """Mock BigQuery table object."""
    class MockTable:
        def __init__(self, schema):
            self.schema = schema

    return MockTable(mock_bigquery_schema)
