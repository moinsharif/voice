"""SQLite-based persistence layer with encryption."""

import sqlite3
import json
import hashlib
import os
from datetime import datetime
from typing import List, Optional, Dict, Any
from pathlib import Path

from src.models.data_models import Session, UserProfile, Mood, MoodEntry
from src.utils.encryption import EncryptionManager
from src.utils.logger import Logger


class PersistenceLayer:
    """Handles all data persistence with encryption."""

    def __init__(self, db_path: str = "vask_data.db", encryption_key: Optional[str] = None):
        """Initialize persistence layer.
        
        Args:
            db_path: Path to SQLite database file
            encryption_key: Encryption key for sensitive data
        """
        self.db_path = db_path
        self.encryption_manager = EncryptionManager(encryption_key) if encryption_key else None
        self.logger = Logger("PersistenceLayer")
        self._initialize_database()

    def _initialize_database(self) -> None:
        """Initialize database schema."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Conversations table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS conversations (
                    session_id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    ended_at TEXT,
                    encrypted_data BLOB NOT NULL,
                    data_hash TEXT NOT NULL
                )
            """)
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_conversations_user_id ON conversations(user_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_conversations_created_at ON conversations(created_at)")

            # User profiles table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS user_profiles (
                    user_id TEXT PRIMARY KEY,
                    encrypted_data BLOB NOT NULL,
                    data_hash TEXT NOT NULL,
                    last_updated TEXT NOT NULL
                )
            """)

            # Mood history table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS mood_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    mood_classification TEXT NOT NULL,
                    confidence REAL NOT NULL,
                    encrypted_data BLOB NOT NULL
                )
            """)
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_mood_user_id ON mood_history(user_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_mood_timestamp ON mood_history(timestamp)")

            # Configuration table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS configuration (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL,
                    last_updated TEXT NOT NULL
                )
            """)

            # Backups table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS backups (
                    backup_id TEXT PRIMARY KEY,
                    created_at TEXT NOT NULL,
                    backup_path TEXT NOT NULL,
                    data_hash TEXT NOT NULL
                )
            """)

            conn.commit()
            conn.close()
            self.logger.info("Database initialized successfully")
        except Exception as e:
            self.logger.error(f"Failed to initialize database: {e}")
            raise

    def save_conversation(self, session: Session) -> None:
        """Save conversation session to database.
        
        Args:
            session: Session object to save
        """
        try:
            session_json = session.to_json()
            encrypted_data = self.encryption_manager.encrypt(session_json) if self.encryption_manager else session_json.encode()
            data_hash = self._calculate_hash(session_json)

            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute("""
                INSERT OR REPLACE INTO conversations 
                (session_id, user_id, created_at, ended_at, encrypted_data, data_hash)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                session.session_id,
                session.user_id,
                session.created_at.isoformat(),
                session.ended_at.isoformat() if session.ended_at else None,
                encrypted_data,
                data_hash
            ))

            conn.commit()
            conn.close()
            self.logger.info(f"Saved conversation {session.session_id}")
        except Exception as e:
            self.logger.error(f"Failed to save conversation: {e}")
            raise

    def load_conversation(self, session_id: str) -> Optional[Session]:
        """Load conversation session from database.
        
        Args:
            session_id: ID of session to load
            
        Returns:
            Session object or None if not found
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute("""
                SELECT encrypted_data, data_hash FROM conversations WHERE session_id = ?
            """, (session_id,))

            row = cursor.fetchone()
            conn.close()

            if not row:
                return None

            encrypted_data, data_hash = row
            decrypted_data = self.encryption_manager.decrypt(encrypted_data) if self.encryption_manager else encrypted_data
            
            if isinstance(decrypted_data, bytes):
                decrypted_data = decrypted_data.decode()

            # Verify hash
            if self._calculate_hash(decrypted_data) != data_hash:
                self.logger.warning(f"Data hash mismatch for session {session_id}")

            session = Session.from_json(decrypted_data)
            self.logger.info(f"Loaded conversation {session_id}")
            return session
        except Exception as e:
            self.logger.error(f"Failed to load conversation: {e}")
            return None

    def save_user_profile(self, profile: UserProfile) -> None:
        """Save user profile to database.
        
        Args:
            profile: UserProfile object to save
        """
        try:
            profile_json = profile.to_json()
            encrypted_data = self.encryption_manager.encrypt(profile_json) if self.encryption_manager else profile_json.encode()
            data_hash = self._calculate_hash(profile_json)

            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute("""
                INSERT OR REPLACE INTO user_profiles 
                (user_id, encrypted_data, data_hash, last_updated)
                VALUES (?, ?, ?, ?)
            """, (
                profile.user_id,
                encrypted_data,
                data_hash,
                datetime.now().isoformat()
            ))

            conn.commit()
            conn.close()
            self.logger.info(f"Saved user profile {profile.user_id}")
        except Exception as e:
            self.logger.error(f"Failed to save user profile: {e}")
            raise

    def load_user_profile(self, user_id: str) -> Optional[UserProfile]:
        """Load user profile from database.
        
        Args:
            user_id: ID of user
            
        Returns:
            UserProfile object or None if not found
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute("""
                SELECT encrypted_data, data_hash FROM user_profiles WHERE user_id = ?
            """, (user_id,))

            row = cursor.fetchone()
            conn.close()

            if not row:
                return None

            encrypted_data, data_hash = row
            decrypted_data = self.encryption_manager.decrypt(encrypted_data) if self.encryption_manager else encrypted_data
            
            if isinstance(decrypted_data, bytes):
                decrypted_data = decrypted_data.decode()

            # Verify hash
            if self._calculate_hash(decrypted_data) != data_hash:
                self.logger.warning(f"Data hash mismatch for user profile {user_id}")

            profile = UserProfile.from_json(decrypted_data)
            self.logger.info(f"Loaded user profile {user_id}")
            return profile
        except Exception as e:
            self.logger.error(f"Failed to load user profile: {e}")
            return None

    def search_conversations(self, user_id: str, query: Optional[str] = None, 
                            start_date: Optional[datetime] = None,
                            end_date: Optional[datetime] = None,
                            mood: Optional[str] = None) -> List[Session]:
        """Search conversations with filters.
        
        Args:
            user_id: User ID to search for
            query: Keyword to search in messages
            start_date: Start date filter
            end_date: End date filter
            mood: Mood classification filter
            
        Returns:
            List of matching Session objects
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            sql = "SELECT session_id, encrypted_data FROM conversations WHERE user_id = ?"
            params = [user_id]

            if start_date:
                sql += " AND created_at >= ?"
                params.append(start_date.isoformat())

            if end_date:
                sql += " AND created_at <= ?"
                params.append(end_date.isoformat())

            cursor.execute(sql, params)
            rows = cursor.fetchall()
            conn.close()

            sessions = []
            for session_id, encrypted_data in rows:
                try:
                    decrypted_data = self.encryption_manager.decrypt(encrypted_data) if self.encryption_manager else encrypted_data
                    if isinstance(decrypted_data, bytes):
                        decrypted_data = decrypted_data.decode()
                    
                    session = Session.from_json(decrypted_data)

                    # Apply text and mood filters
                    if query:
                        if not any(query.lower() in exchange.user_message.lower() or 
                                 query.lower() in exchange.ai_response.lower()
                                 for exchange in session.exchanges):
                            continue

                    if mood:
                        if session.mood_summary and session.mood_summary.primary_mood != mood:
                            continue

                    sessions.append(session)
                except Exception as e:
                    self.logger.warning(f"Failed to deserialize session {session_id}: {e}")
                    continue

            self.logger.info(f"Found {len(sessions)} conversations for user {user_id}")
            return sessions
        except Exception as e:
            self.logger.error(f"Failed to search conversations: {e}")
            return []

    def delete_conversation(self, session_id: str) -> bool:
        """Securely delete a conversation.
        
        Args:
            session_id: ID of session to delete
            
        Returns:
            True if successful, False otherwise
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute("DELETE FROM conversations WHERE session_id = ?", (session_id,))
            conn.commit()
            conn.close()

            self.logger.info(f"Deleted conversation {session_id}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to delete conversation: {e}")
            return False

    def export_conversations(self, user_id: str, format: str = "json") -> Optional[str]:
        """Export user conversations in specified format.
        
        Args:
            user_id: User ID to export
            format: Export format ("json" or "csv")
            
        Returns:
            Exported data as string or None on error
        """
        try:
            sessions = self.search_conversations(user_id)

            if format == "json":
                data = {
                    'user_id': user_id,
                    'export_date': datetime.now().isoformat(),
                    'sessions': [s.to_dict() for s in sessions]
                }
                return json.dumps(data, indent=2)

            elif format == "csv":
                import csv
                from io import StringIO

                output = StringIO()
                writer = csv.writer(output)
                writer.writerow(['Session ID', 'Created At', 'Exchange Count', 'Primary Mood', 'Duration'])

                for session in sessions:
                    duration = (session.ended_at - session.created_at).total_seconds() if session.ended_at else 0
                    mood = session.mood_summary.primary_mood if session.mood_summary else "unknown"
                    writer.writerow([
                        session.session_id,
                        session.created_at.isoformat(),
                        len(session.exchanges),
                        mood,
                        duration
                    ])

                return output.getvalue()

            else:
                self.logger.error(f"Unsupported export format: {format}")
                return None

        except Exception as e:
            self.logger.error(f"Failed to export conversations: {e}")
            return None

    def create_backup(self) -> Optional[str]:
        """Create database backup.
        
        Returns:
            Backup ID or None on error
        """
        try:
            backup_dir = Path("backups")
            backup_dir.mkdir(exist_ok=True)

            backup_id = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = backup_dir / f"vask_backup_{backup_id}.db"

            # Copy database file
            import shutil
            shutil.copy2(self.db_path, str(backup_path))

            # Calculate hash
            data_hash = self._calculate_file_hash(str(backup_path))

            # Record backup
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO backups (backup_id, created_at, backup_path, data_hash)
                VALUES (?, ?, ?, ?)
            """, (backup_id, datetime.now().isoformat(), str(backup_path), data_hash))
            conn.commit()
            conn.close()

            self.logger.info(f"Created backup {backup_id}")
            return backup_id
        except Exception as e:
            self.logger.error(f"Failed to create backup: {e}")
            return None

    def restore_backup(self, backup_id: str) -> bool:
        """Restore database from backup.
        
        Args:
            backup_id: ID of backup to restore
            
        Returns:
            True if successful, False otherwise
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute("""
                SELECT backup_path FROM backups WHERE backup_id = ?
            """, (backup_id,))

            row = cursor.fetchone()
            conn.close()

            if not row:
                self.logger.error(f"Backup {backup_id} not found")
                return False

            backup_path = row[0]

            # Verify backup exists and hash matches
            if not os.path.exists(backup_path):
                self.logger.error(f"Backup file not found: {backup_path}")
                return False

            # Restore backup
            import shutil
            shutil.copy2(backup_path, self.db_path)

            self.logger.info(f"Restored backup {backup_id}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to restore backup: {e}")
            return False

    def _calculate_hash(self, data: str) -> str:
        """Calculate SHA-256 hash of data."""
        return hashlib.sha256(data.encode()).hexdigest()

    def _calculate_file_hash(self, filepath: str) -> str:
        """Calculate SHA-256 hash of file."""
        sha256_hash = hashlib.sha256()
        with open(filepath, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()

    def save_configuration(self, key: str, value: Any) -> None:
        """Save configuration value.
        
        Args:
            key: Configuration key
            value: Configuration value
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute("""
                INSERT OR REPLACE INTO configuration (key, value, last_updated)
                VALUES (?, ?, ?)
            """, (key, json.dumps(value), datetime.now().isoformat()))

            conn.commit()
            conn.close()
        except Exception as e:
            self.logger.error(f"Failed to save configuration: {e}")

    def load_configuration(self, key: str) -> Optional[Any]:
        """Load configuration value.
        
        Args:
            key: Configuration key
            
        Returns:
            Configuration value or None if not found
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute("SELECT value FROM configuration WHERE key = ?", (key,))
            row = cursor.fetchone()
            conn.close()

            if not row:
                return None

            return json.loads(row[0])
        except Exception as e:
            self.logger.error(f"Failed to load configuration: {e}")
            return None
