"""
Tests for upload module.
"""
import os
from unittest.mock import Mock, patch, MagicMock

import pandas as pd
import pytest

# Add parent directory to path for imports
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from upload import upload_to_bigquery, validate_schema


class TestValidateSchema:
    """Tests for validate_schema function."""

    def test_returns_true_when_all_columns_present(self, sample_dataframe, mock_bigquery_schema):
        """Test validation passes when all columns are present."""
        mock_client = Mock()
        mock_table = Mock()
        mock_table.schema = mock_bigquery_schema
        mock_client.get_table.return_value = mock_table

        result = validate_schema(sample_dataframe, mock_client, 'test.table')

        assert result is True

    def test_returns_false_when_columns_missing(self, mock_bigquery_schema):
        """Test validation fails when required columns are missing."""
        mock_client = Mock()
        mock_table = Mock()
        mock_table.schema = mock_bigquery_schema
        mock_client.get_table.return_value = mock_table

        # DataFrame missing FILING_ID column
        df = pd.DataFrame({'AMEND_ID': [1, 2, 3]})

        result = validate_schema(df, mock_client, 'test.table')

        assert result is False

    def test_allows_extra_columns(self, sample_dataframe, mock_bigquery_schema):
        """Test validation passes when DataFrame has extra columns."""
        mock_client = Mock()
        mock_table = Mock()
        mock_table.schema = mock_bigquery_schema
        mock_client.get_table.return_value = mock_table

        # Add extra column
        df = sample_dataframe.copy()
        df['EXTRA_COL'] = [1, 2, 3]

        result = validate_schema(df, mock_client, 'test.table')

        assert result is True

    def test_handles_table_not_found(self):
        """Test handling when table doesn't exist."""
        from google.api_core.exceptions import NotFound

        mock_client = Mock()
        mock_client.get_table.side_effect = NotFound('Table not found')

        df = pd.DataFrame({'col': [1, 2, 3]})
        result = validate_schema(df, mock_client, 'nonexistent.table')

        assert result is False


class TestUploadToBigquery:
    """Tests for upload_to_bigquery function."""

    @patch('upload.service_account.Credentials.from_service_account_file')
    @patch('upload.bigquery.Client')
    @patch('upload.validate_schema')
    def test_successful_upload(self, mock_validate, mock_client_class, mock_creds, sample_dataframe, tmp_path):
        """Test successful upload returns True."""
        mock_validate.return_value = True
        mock_client = Mock()
        mock_client_class.return_value = mock_client
        mock_job = Mock()
        mock_client.load_table_from_dataframe.return_value = mock_job

        # Create temp credentials file
        creds_path = tmp_path / "creds.json"
        creds_path.write_text('{}')

        result = upload_to_bigquery(
            sample_dataframe,
            'project.dataset.table',
            str(creds_path),
            'project'
        )

        assert result is True
        mock_job.result.assert_called_once()

    @patch('upload.service_account.Credentials.from_service_account_file')
    @patch('upload.bigquery.Client')
    @patch('upload.validate_schema')
    def test_upload_fails_on_validation_error(self, mock_validate, mock_client_class, mock_creds, sample_dataframe, tmp_path):
        """Test upload returns False when schema validation fails."""
        mock_validate.return_value = False

        creds_path = tmp_path / "creds.json"
        creds_path.write_text('{}')

        result = upload_to_bigquery(
            sample_dataframe,
            'project.dataset.table',
            str(creds_path),
            'project'
        )

        assert result is False

    def test_upload_fails_on_missing_credentials(self, sample_dataframe):
        """Test upload returns False when credentials file doesn't exist."""
        result = upload_to_bigquery(
            sample_dataframe,
            'project.dataset.table',
            '/nonexistent/creds.json',
            'project'
        )

        assert result is False
