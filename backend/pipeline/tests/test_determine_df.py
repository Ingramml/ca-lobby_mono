"""
Tests for determine_df module.
"""
import os
import tempfile

import pandas as pd
import pytest

# Add parent directory to path for imports
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from determine_df import ensure_dataframe


class TestEnsureDataframe:
    """Tests for ensure_dataframe function."""

    def test_returns_dataframe_unchanged(self, sample_dataframe):
        """Test that a DataFrame input is returned as-is."""
        result = ensure_dataframe(sample_dataframe)
        assert isinstance(result, pd.DataFrame)
        pd.testing.assert_frame_equal(result, sample_dataframe)

    def test_reads_csv_file(self, sample_csv_file):
        """Test that a CSV file path is read into a DataFrame."""
        result = ensure_dataframe(sample_csv_file)
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 3
        assert 'FILING_ID' in result.columns

    def test_raises_on_nonexistent_file(self):
        """Test that a non-existent file raises ValueError."""
        with pytest.raises(ValueError, match="Invalid file path"):
            ensure_dataframe("/nonexistent/path/file.csv")

    def test_raises_on_non_csv_file(self, tmp_path):
        """Test that a non-CSV file raises ValueError."""
        txt_file = tmp_path / "test.txt"
        txt_file.write_text("not a csv")
        with pytest.raises(ValueError, match="unsupported file type"):
            ensure_dataframe(str(txt_file))

    def test_raises_on_invalid_type(self):
        """Test that invalid input types raise TypeError."""
        with pytest.raises(TypeError, match="must be either"):
            ensure_dataframe(12345)

        with pytest.raises(TypeError, match="must be either"):
            ensure_dataframe(['list', 'of', 'items'])
