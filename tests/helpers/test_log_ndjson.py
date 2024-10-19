"""Tests for the log_ndjson function."""
import os
import json
import tempfile
from unittest.mock import patch, mock_open

import pytest

from helpers.log_ndjson import log_ndjson


def test_log_ndjson_success():
    """Test logging data to an NDJSON file successfully."""
    # Create a temporary file for testing
    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        file_path = temp_file.name

    data = {"event": "test_event", "status": "success"}

    # Log data to the NDJSON file
    log_ndjson(file_path, **data)

    # Verify that the data was logged correctly
    with open(file_path, "r") as file:
        logged_data = file.readline().strip()
        assert json.loads(logged_data) == data

    # Clean up the temporary file
    os.remove(file_path)


def test_log_ndjson_retry_on_failure():
    """Test that the log_ndjson function retries on failure."""
    data = {"event": "retry_event", "status": "retry"}

    # Simulate the first two write attempts failing, then succeeding
    with patch("builtins.open", mock_open()) as mocked_open:
        mocked_open.side_effect = [OSError("File error"), OSError("File error"), mock_open().return_value]

        # Call log_ndjson with retry logic
        log_ndjson("test_path.ndjson", retry=3, **data)

        # Verify that open was called three times (two failures, one success)
        assert mocked_open.call_count == 3


def test_log_ndjson_fails_after_max_retries():
    """Test that the log_ndjson function raises an IOError after max retries."""
    data = {"event": "failure_event", "status": "failure"}

    # Simulate all write attempts failing
    with patch("builtins.open", side_effect=OSError("File error")) as mocked_open:
        with pytest.raises(IOError, match="Failed to log data after 3 attempts"):
            log_ndjson("test_path.ndjson", retry=3, **data)

        # Verify that open was called three times (equal to the retry limit)
        assert mocked_open.call_count == 3


def test_log_ndjson_no_retry():
    """Test that log_ndjson does not retry if no retries are allowed (retry=1)."""
    data = {"event": "no_retry_event", "status": "no_retry"}

    # Simulate a write attempt failure
    with patch("builtins.open", side_effect=OSError("File error")) as mocked_open:
        with pytest.raises(IOError, match="Failed to log data after 1 attempts"):
            log_ndjson("test_path.ndjson", retry=1, **data)

        # Verify that open was called only once
        assert mocked_open.call_count == 1
