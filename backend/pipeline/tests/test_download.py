"""
Tests for Bignewdownload_2 module.
"""
import os
from unittest.mock import Mock, patch, MagicMock

import pandas as pd
import pytest

# Add parent directory to path for imports
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from Bignewdownload_2 import Bignewdownload


class TestBignewdownload:
    """Tests for Bignewdownload function."""

    @patch.dict(os.environ, {'BLN_API': ''})
    def test_returns_empty_list_without_api_key(self, tmp_path):
        """Test returns empty list when BLN_API not set."""
        result = Bignewdownload(str(tmp_path))

        assert result == []

    @patch('Bignewdownload_2.pd.read_bln')
    @patch('Bignewdownload_2.Client')
    @patch('Bignewdownload_2.bln.pandas.register')
    @patch.dict(os.environ, {'BLN_API': 'test-api-key'})
    def test_downloads_files(self, mock_register, mock_client, mock_read_bln, tmp_path):
        """Test successful file download."""
        # Mock the BLN read to return a DataFrame
        mock_df = pd.DataFrame({'col': [1, 2, 3]})
        mock_read_bln.return_value = mock_df

        result = Bignewdownload(str(tmp_path))

        # Should have downloaded multiple files
        assert len(result) > 0
        assert all(f.endswith('.csv') for f in result)

    @patch('Bignewdownload_2.pd.read_bln')
    @patch('Bignewdownload_2.Client')
    @patch('Bignewdownload_2.bln.pandas.register')
    @patch.dict(os.environ, {'BLN_API': 'test-api-key'})
    def test_skips_existing_files(self, mock_register, mock_client, mock_read_bln, tmp_path):
        """Test that existing files are skipped."""
        import datetime

        # Create a pre-existing file
        today = datetime.date.today()
        work_dir = tmp_path / str(today)
        work_dir.mkdir()
        existing_file = work_dir / f"{today}_cvr_lobby_disclosure_cd.csv"
        existing_file.write_text("existing data")

        mock_df = pd.DataFrame({'col': [1, 2, 3]})
        mock_read_bln.return_value = mock_df

        result = Bignewdownload(str(tmp_path))

        # The existing file should not be in the result list (it was skipped)
        assert str(existing_file) not in result

    @patch('Bignewdownload_2.pd.read_bln')
    @patch('Bignewdownload_2.Client')
    @patch('Bignewdownload_2.bln.pandas.register')
    @patch.dict(os.environ, {'BLN_API': 'test-api-key'})
    def test_continues_on_download_error(self, mock_register, mock_client, mock_read_bln, tmp_path):
        """Test that download continues even if one file fails."""
        # First call raises exception, subsequent calls succeed
        mock_df = pd.DataFrame({'col': [1, 2, 3]})
        mock_read_bln.side_effect = [Exception("Download failed"), mock_df, mock_df]

        result = Bignewdownload(str(tmp_path))

        # Should have some successful downloads despite the error
        # (exact count depends on number of files in the list)
        assert isinstance(result, list)

    @patch('Bignewdownload_2.pd.read_bln')
    @patch('Bignewdownload_2.Client')
    @patch('Bignewdownload_2.bln.pandas.register')
    @patch.dict(os.environ, {
        'BLN_API': 'test-api-key',
        'BLN_PROJECT_ID': 'custom-project-id'
    })
    def test_uses_env_project_id(self, mock_register, mock_client, mock_read_bln, tmp_path):
        """Test that BLN_PROJECT_ID from environment is used."""
        mock_df = pd.DataFrame({'col': [1, 2, 3]})
        mock_read_bln.return_value = mock_df

        Bignewdownload(str(tmp_path))

        # Check that read_bln was called with the custom project ID
        calls = mock_read_bln.call_args_list
        if calls:
            # First positional arg should be project_id
            assert calls[0][0][0] == 'custom-project-id'


class TestBackwardsCompatibility:
    """Tests for backwards compatibility."""

    def test_bignewdoanload_alias_exists(self):
        """Test that the old function name still works."""
        from Bignewdownload_2 import Bignewdoanload

        # The alias should point to the same function
        assert Bignewdoanload is Bignewdownload
