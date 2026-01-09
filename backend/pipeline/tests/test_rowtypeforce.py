"""
Tests for rowtypeforce module.
"""
import os
from unittest.mock import Mock, patch

import pandas as pd
import pytest

# Add parent directory to path for imports
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from rowtypeforce import row_type_force, _log_coercion


class TestLogCoercion:
    """Tests for _log_coercion helper function."""

    def test_logs_warning_when_values_lost(self, caplog):
        """Test that warning is logged when values are coerced."""
        import logging
        caplog.set_level(logging.WARNING)

        _log_coercion('test_col', 100, 90, 'INTEGER')

        assert 'test_col' in caplog.text
        assert '10 values coerced' in caplog.text
        assert '10.0%' in caplog.text

    def test_no_log_when_no_values_lost(self, caplog):
        """Test that no warning is logged when all values preserved."""
        import logging
        caplog.set_level(logging.WARNING)

        _log_coercion('test_col', 100, 100, 'INTEGER')

        assert 'coerced' not in caplog.text


class TestRowTypeForce:
    """Tests for row_type_force function."""

    @pytest.fixture
    def mock_client(self, mock_bigquery_table):
        """Create a mock BigQuery client."""
        client = Mock()
        client.get_table.return_value = mock_bigquery_table
        return client

    def test_converts_integer_columns(self, mock_client, tmp_path):
        """Test INTEGER column conversion."""
        df = pd.DataFrame({'FILING_ID': ['1', '2', '3']})
        csv_path = tmp_path / "test.csv"
        df.to_csv(csv_path, index=False)

        result = row_type_force(mock_client, 'test.table', str(csv_path))

        assert result['FILING_ID'].dtype == 'Int64'

    def test_converts_float_columns(self, mock_client, tmp_path):
        """Test FLOAT column conversion."""
        df = pd.DataFrame({'AMOUNT': ['100.50', '200.75', '300.25']})
        csv_path = tmp_path / "test.csv"
        df.to_csv(csv_path, index=False)

        result = row_type_force(mock_client, 'test.table', str(csv_path))

        assert result['AMOUNT'].dtype == 'float64'

    def test_converts_string_columns(self, mock_client, tmp_path):
        """Test STRING column conversion."""
        df = pd.DataFrame({'FILER_NAML': [None, 'Test', 123]})
        csv_path = tmp_path / "test.csv"
        df.to_csv(csv_path, index=False)

        result = row_type_force(mock_client, 'test.table', str(csv_path))

        assert result['FILER_NAML'].dtype == 'object'
        # NaN should be converted to empty string
        assert result['FILER_NAML'].iloc[0] == ''

    def test_converts_date_columns(self, mock_client, tmp_path):
        """Test DATE column conversion to string format."""
        df = pd.DataFrame({'RPT_DATE': ['2025-01-01', '2025-01-02', 'invalid']})
        csv_path = tmp_path / "test.csv"
        df.to_csv(csv_path, index=False)

        result = row_type_force(mock_client, 'test.table', str(csv_path))

        # First two should be valid dates
        assert result['RPT_DATE'].iloc[0] == '2025-01-01'
        assert result['RPT_DATE'].iloc[1] == '2025-01-02'

    def test_skips_missing_columns(self, mock_client, tmp_path):
        """Test that missing columns in DataFrame are skipped."""
        # Create DataFrame without FILER_NAML column
        df = pd.DataFrame({'FILING_ID': [1, 2, 3]})
        csv_path = tmp_path / "test.csv"
        df.to_csv(csv_path, index=False)

        # Should not raise an error
        result = row_type_force(mock_client, 'test.table', str(csv_path))

        assert 'FILING_ID' in result.columns
        assert 'FILER_NAML' not in result.columns

    def test_saves_cleaned_file(self, mock_client, tmp_path):
        """Test that cleaned file is saved."""
        df = pd.DataFrame({'FILING_ID': ['1', '2', '3']})
        csv_path = tmp_path / "test.csv"
        df.to_csv(csv_path, index=False)

        row_type_force(mock_client, 'test.table', str(csv_path))

        cleaned_path = tmp_path / "cleaned_test.csv"
        assert cleaned_path.exists()

    def test_accepts_dataframe_input(self, mock_client, tmp_path):
        """Test that DataFrame can be passed directly."""
        df = pd.DataFrame({'FILING_ID': ['1', '2', '3']})

        # Change to tmp_path so cleaned file is saved there
        os.chdir(tmp_path)

        result = row_type_force(mock_client, 'test.table', df)

        assert result['FILING_ID'].dtype == 'Int64'
