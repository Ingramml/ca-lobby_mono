"""
Tests for Bigquery_connection module.
"""
import os
from unittest.mock import Mock, patch

import pytest

# Add parent directory to path for imports
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from Bigquery_connection import bigquery_connect, get_project_id_from_credentials


class TestGetProjectIdFromCredentials:
    """Tests for get_project_id_from_credentials function."""

    @patch('Bigquery_connection.service_account.Credentials.from_service_account_file')
    def test_returns_project_id(self, mock_creds):
        """Test successful project ID extraction."""
        mock_credential = Mock()
        mock_credential.project_id = 'test-project'
        mock_creds.return_value = mock_credential

        result = get_project_id_from_credentials('/path/to/creds.json')

        assert result == 'test-project'

    def test_returns_none_for_nonexistent_file(self):
        """Test returns None when credentials file doesn't exist."""
        result = get_project_id_from_credentials('/nonexistent/path/creds.json')

        assert result is None


class TestBigqueryConnect:
    """Tests for bigquery_connect function."""

    @patch('Bigquery_connection.service_account.Credentials.from_service_account_file')
    @patch('Bigquery_connection.bigquery.Client')
    @patch('Bigquery_connection.get_project_id_from_credentials')
    def test_successful_connection(self, mock_get_project, mock_client_class, mock_creds):
        """Test successful BigQuery connection."""
        mock_get_project.return_value = 'test-project'
        mock_client = Mock()
        mock_client.list_datasets.return_value = iter([])
        mock_client_class.return_value = mock_client

        result = bigquery_connect('/path/to/creds.json')

        assert result is not None
        mock_client_class.assert_called_once()

    @patch('Bigquery_connection.get_project_id_from_credentials')
    def test_returns_none_when_project_id_fails(self, mock_get_project):
        """Test returns None when project ID extraction fails."""
        mock_get_project.return_value = None

        result = bigquery_connect('/path/to/creds.json')

        assert result is None

    def test_returns_none_for_nonexistent_credentials(self):
        """Test returns None when credentials file doesn't exist."""
        result = bigquery_connect('/nonexistent/path/creds.json')

        assert result is None

    @patch('Bigquery_connection.service_account.Credentials.from_service_account_file')
    @patch('Bigquery_connection.bigquery.Client')
    @patch('Bigquery_connection.get_project_id_from_credentials')
    def test_returns_none_on_api_error(self, mock_get_project, mock_client_class, mock_creds):
        """Test returns None when BigQuery API fails."""
        from google.api_core.exceptions import GoogleAPICallError

        mock_get_project.return_value = 'test-project'
        mock_client_class.side_effect = GoogleAPICallError('API Error')

        result = bigquery_connect('/path/to/creds.json')

        assert result is None
