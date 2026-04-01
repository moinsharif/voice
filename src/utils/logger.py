"""Logging utility with encryption and automatic rotation."""

import os
import json
import gzip
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Optional
from cryptography.fernet import Fernet
import hashlib


class LogLevel(Enum):
    """Log level enumeration."""

    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"


class Logger:
    """Logger utility with encryption and automatic rotation.
    
    Features:
    - Multiple log levels (DEBUG, INFO, WARNING, ERROR)
    - Encrypted file logging with AES-256
    - Automatic log rotation (30-day retention)
    - Structured JSON logging
    """

    def __init__(
        self,
        log_dir: str = "logs",
        encryption_key: Optional[bytes] = None,
        retention_days: int = 30,
    ):
        """Initialize logger.
        
        Args:
            log_dir: Directory to store log files
            encryption_key: Encryption key for log files (generated if not provided)
            retention_days: Number of days to retain logs (default: 30)
        """
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.retention_days = retention_days
        self.current_log_file = self.log_dir / f"vask_{datetime.now().strftime('%Y%m%d')}.log"

        # Initialize encryption
        if encryption_key is None:
            encryption_key = self._load_or_create_key()
        self.cipher = Fernet(encryption_key)

        # Clean up old logs
        self._cleanup_old_logs()

    def _load_or_create_key(self) -> bytes:
        """Load or create encryption key."""
        key_file = self.log_dir / ".encryption_key"

        if key_file.exists():
            with open(key_file, "rb") as f:
                return f.read()

        # Generate new key
        key = Fernet.generate_key()
        with open(key_file, "wb") as f:
            f.write(key)
        # Restrict permissions
        os.chmod(key_file, 0o600)
        return key

    def _cleanup_old_logs(self) -> None:
        """Remove log files older than retention period."""
        cutoff_date = datetime.now() - timedelta(days=self.retention_days)

        for log_file in self.log_dir.glob("vask_*.log*"):
            try:
                # Extract date from filename
                date_str = log_file.stem.split("_")[1]
                file_date = datetime.strptime(date_str, "%Y%m%d")

                if file_date < cutoff_date:
                    log_file.unlink()
            except (ValueError, IndexError):
                # Skip files that don't match expected format
                pass

    def _rotate_if_needed(self) -> None:
        """Rotate log file if date has changed."""
        new_log_file = self.log_dir / f"vask_{datetime.now().strftime('%Y%m%d')}.log"

        if new_log_file != self.current_log_file:
            # Compress old log file
            if self.current_log_file.exists():
                self._compress_log(self.current_log_file)
            self.current_log_file = new_log_file

    def _compress_log(self, log_file: Path) -> None:
        """Compress log file with gzip."""
        gz_file = Path(str(log_file) + ".gz")

        try:
            with open(log_file, "rb") as f_in:
                with gzip.open(gz_file, "wb") as f_out:
                    f_out.writelines(f_in)
            log_file.unlink()
        except Exception as e:
            print(f"Failed to compress log file: {e}")

    def _encrypt_message(self, message: str) -> str:
        """Encrypt log message."""
        encrypted = self.cipher.encrypt(message.encode())
        return encrypted.decode()

    def _format_log_entry(
        self, level: LogLevel, message: str, context: Optional[dict] = None
    ) -> str:
        """Format log entry as JSON."""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "level": level.value,
            "message": message,
        }

        if context:
            entry["context"] = context

        return json.dumps(entry)

    def _write_to_file(self, formatted_entry: str) -> None:
        """Write encrypted log entry to file."""
        self._rotate_if_needed()

        try:
            encrypted_entry = self._encrypt_message(formatted_entry)
            with open(self.current_log_file, "a") as f:
                f.write(encrypted_entry + "\n")
        except Exception as e:
            print(f"Failed to write log entry: {e}")

    def debug(self, message: str, context: Optional[dict] = None) -> None:
        """Log debug message."""
        formatted = self._format_log_entry(LogLevel.DEBUG, message, context)
        self._write_to_file(formatted)

    def info(self, message: str, context: Optional[dict] = None) -> None:
        """Log info message."""
        formatted = self._format_log_entry(LogLevel.INFO, message, context)
        self._write_to_file(formatted)

    def warning(self, message: str, context: Optional[dict] = None) -> None:
        """Log warning message."""
        formatted = self._format_log_entry(LogLevel.WARNING, message, context)
        self._write_to_file(formatted)

    def error(self, message: str, context: Optional[dict] = None) -> None:
        """Log error message."""
        formatted = self._format_log_entry(LogLevel.ERROR, message, context)
        self._write_to_file(formatted)

    def read_logs(self, level: Optional[LogLevel] = None) -> list[dict]:
        """Read and decrypt log entries.
        
        Args:
            level: Filter by log level (None for all)
            
        Returns:
            List of decrypted log entries
        """
        entries = []

        for log_file in sorted(self.log_dir.glob("vask_*.log")):
            try:
                with open(log_file, "r") as f:
                    for line in f:
                        try:
                            decrypted = self.cipher.decrypt(line.strip().encode()).decode()
                            entry = json.loads(decrypted)

                            if level is None or entry["level"] == level.value:
                                entries.append(entry)
                        except Exception:
                            # Skip malformed entries
                            pass
            except Exception as e:
                print(f"Failed to read log file {log_file}: {e}")

        return entries
