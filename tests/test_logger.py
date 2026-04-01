"""Tests for Logger utility."""

import pytest
import json
import tempfile
from pathlib import Path
from datetime import datetime, timedelta
from cryptography.fernet import Fernet

from src.utils.logger import Logger, LogLevel


@pytest.fixture
def temp_log_dir():
    """Create temporary log directory."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir


@pytest.fixture
def logger(temp_log_dir):
    """Create logger instance with temporary directory."""
    return Logger(log_dir=temp_log_dir)


class TestLoggerBasics:
    """Test basic logging functionality."""

    def test_logger_initialization(self, temp_log_dir):
        """Test logger initialization."""
        logger = Logger(log_dir=temp_log_dir)
        assert logger.log_dir.exists()
        assert logger.retention_days == 30

    def test_logger_custom_retention(self, temp_log_dir):
        """Test logger with custom retention period."""
        logger = Logger(log_dir=temp_log_dir, retention_days=7)
        assert logger.retention_days == 7

    def test_encryption_key_creation(self, temp_log_dir):
        """Test encryption key is created."""
        logger = Logger(log_dir=temp_log_dir)
        key_file = Path(temp_log_dir) / ".encryption_key"
        assert key_file.exists()

    def test_encryption_key_persistence(self, temp_log_dir):
        """Test encryption key is reused."""
        logger1 = Logger(log_dir=temp_log_dir)
        key_file = Path(temp_log_dir) / ".encryption_key"
        with open(key_file, "rb") as f:
            key1 = f.read()

        logger2 = Logger(log_dir=temp_log_dir)
        with open(key_file, "rb") as f:
            key2 = f.read()

        assert key1 == key2


class TestLogging:
    """Test logging operations."""

    def test_debug_logging(self, logger):
        """Test debug level logging."""
        logger.debug("Debug message")
        assert logger.current_log_file.exists()

    def test_info_logging(self, logger):
        """Test info level logging."""
        logger.info("Info message")
        assert logger.current_log_file.exists()

    def test_warning_logging(self, logger):
        """Test warning level logging."""
        logger.warning("Warning message")
        assert logger.current_log_file.exists()

    def test_error_logging(self, logger):
        """Test error level logging."""
        logger.error("Error message")
        assert logger.current_log_file.exists()

    def test_logging_with_context(self, logger):
        """Test logging with context data."""
        context = {"user_id": "user123", "action": "login"}
        logger.info("User action", context=context)
        assert logger.current_log_file.exists()

    def test_multiple_log_entries(self, logger):
        """Test multiple log entries."""
        logger.debug("Debug 1")
        logger.info("Info 1")
        logger.warning("Warning 1")
        logger.error("Error 1")

        entries = logger.read_logs()
        assert len(entries) == 4

    def test_log_entry_format(self, logger):
        """Test log entry format."""
        logger.info("Test message")
        entries = logger.read_logs()

        assert len(entries) == 1
        entry = entries[0]
        assert "timestamp" in entry
        assert entry["level"] == "INFO"
        assert entry["message"] == "Test message"


class TestEncryption:
    """Test encryption functionality."""

    def test_logs_are_encrypted(self, logger):
        """Test that logs are encrypted in file."""
        logger.info("Secret message")

        # Read raw file content
        with open(logger.current_log_file, "r") as f:
            raw_content = f.read()

        # Should not contain plaintext message
        assert "Secret message" not in raw_content

    def test_logs_can_be_decrypted(self, logger):
        """Test that encrypted logs can be decrypted."""
        logger.info("Decryptable message")
        entries = logger.read_logs()

        assert len(entries) == 1
        assert entries[0]["message"] == "Decryptable message"

    def test_custom_encryption_key(self, temp_log_dir):
        """Test logger with custom encryption key."""
        key = Fernet.generate_key()
        logger = Logger(log_dir=temp_log_dir, encryption_key=key)
        logger.info("Test message")

        entries = logger.read_logs()
        assert len(entries) == 1
        assert entries[0]["message"] == "Test message"


class TestLogFiltering:
    """Test log filtering functionality."""

    def test_filter_by_level(self, logger):
        """Test filtering logs by level."""
        logger.debug("Debug")
        logger.info("Info")
        logger.warning("Warning")
        logger.error("Error")

        error_entries = logger.read_logs(level=LogLevel.ERROR)
        assert len(error_entries) == 1
        assert error_entries[0]["level"] == "ERROR"

    def test_filter_by_multiple_levels(self, logger):
        """Test reading logs without filter."""
        logger.debug("Debug")
        logger.info("Info")
        logger.warning("Warning")

        all_entries = logger.read_logs()
        assert len(all_entries) == 3

    def test_empty_log_read(self, logger):
        """Test reading from empty log."""
        entries = logger.read_logs()
        assert entries == []


class TestLogRotation:
    """Test log rotation functionality."""

    def test_log_file_naming(self, logger):
        """Test log file naming convention."""
        logger.info("Test")
        filename = logger.current_log_file.name
        assert filename.startswith("vask_")
        assert filename.endswith(".log")

    def test_log_file_date_format(self, logger):
        """Test log file date format."""
        logger.info("Test")
        filename = logger.current_log_file.name
        # Extract date part: vask_YYYYMMDD.log
        date_str = filename.split("_")[1].split(".")[0]
        # Should be valid date format
        datetime.strptime(date_str, "%Y%m%d")


class TestCleanup:
    """Test log cleanup functionality."""

    def test_old_logs_cleanup(self, temp_log_dir):
        """Test that old logs are cleaned up."""
        logger = Logger(log_dir=temp_log_dir, retention_days=1)

        # Create old log file
        old_date = (datetime.now() - timedelta(days=2)).strftime("%Y%m%d")
        old_log = Path(temp_log_dir) / f"vask_{old_date}.log"
        old_log.write_text("old log content")

        # Create new logger (triggers cleanup)
        logger2 = Logger(log_dir=temp_log_dir, retention_days=1)

        # Old log should be deleted
        assert not old_log.exists()

    def test_recent_logs_preserved(self, temp_log_dir):
        """Test that recent logs are preserved."""
        logger = Logger(log_dir=temp_log_dir, retention_days=30)

        # Create recent log file
        recent_date = (datetime.now() - timedelta(days=1)).strftime("%Y%m%d")
        recent_log = Path(temp_log_dir) / f"vask_{recent_date}.log"
        recent_log.write_text("recent log content")

        # Create new logger (triggers cleanup)
        logger2 = Logger(log_dir=temp_log_dir, retention_days=30)

        # Recent log should still exist
        assert recent_log.exists()


class TestErrorHandling:
    """Test error handling in logger."""

    def test_logger_handles_write_errors(self, logger):
        """Test logger handles write errors gracefully."""
        # Make log directory read-only
        import os

        os.chmod(logger.log_dir, 0o444)

        try:
            # Should not raise exception
            logger.info("Test message")
        finally:
            # Restore permissions
            os.chmod(logger.log_dir, 0o755)

    def test_logger_handles_malformed_entries(self, logger):
        """Test logger handles malformed log entries."""
        # Write malformed entry
        with open(logger.current_log_file, "a") as f:
            f.write("malformed entry\n")

        # Should not raise exception
        entries = logger.read_logs()
        # Malformed entry should be skipped
        assert len(entries) == 0
