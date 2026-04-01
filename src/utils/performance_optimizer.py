"""Performance optimization utilities for Vask."""

import psutil
import gc
import sqlite3
import threading
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
from dataclasses import dataclass
from src.utils.logger import Logger


@dataclass
class MemoryProfile:
    """Memory profiling data."""
    timestamp: datetime
    rss_mb: float  # Resident Set Size in MB
    vms_mb: float  # Virtual Memory Size in MB
    percent: float  # Percentage of system memory
    available_mb: float  # Available system memory in MB


@dataclass
class PerformanceMetrics:
    """Performance metrics snapshot."""
    timestamp: datetime
    memory_profile: MemoryProfile
    cpu_percent: float
    active_sessions: int
    cached_responses: int
    database_size_mb: float


class MemoryProfiler:
    """Profiles memory usage of the application."""

    def __init__(self):
        """Initialize memory profiler."""
        self.logger = Logger("MemoryProfiler")
        self.process = psutil.Process()
        self.profiles: List[MemoryProfile] = []
        self.max_profiles = 1000  # Keep last 1000 profiles

    def profile(self) -> MemoryProfile:
        """Take a memory profile snapshot.
        
        Returns:
            MemoryProfile with current memory usage
        """
        try:
            mem_info = self.process.memory_info()
            mem_percent = self.process.memory_percent()
            available_mb = psutil.virtual_memory().available / (1024 * 1024)

            profile = MemoryProfile(
                timestamp=datetime.now(),
                rss_mb=mem_info.rss / (1024 * 1024),
                vms_mb=mem_info.vms / (1024 * 1024),
                percent=mem_percent,
                available_mb=available_mb
            )

            self.profiles.append(profile)
            if len(self.profiles) > self.max_profiles:
                self.profiles = self.profiles[-self.max_profiles:]

            return profile

        except Exception as e:
            self.logger.error(f"Failed to profile memory: {e}")
            return None

    def get_peak_memory(self) -> Optional[MemoryProfile]:
        """Get peak memory usage.
        
        Returns:
            MemoryProfile with highest RSS memory
        """
        if not self.profiles:
            return None
        return max(self.profiles, key=lambda p: p.rss_mb)

    def get_average_memory(self) -> Optional[MemoryProfile]:
        """Get average memory usage.
        
        Returns:
            MemoryProfile with average memory values
        """
        if not self.profiles:
            return None

        avg_rss = sum(p.rss_mb for p in self.profiles) / len(self.profiles)
        avg_vms = sum(p.vms_mb for p in self.profiles) / len(self.profiles)
        avg_percent = sum(p.percent for p in self.profiles) / len(self.profiles)
        avg_available = sum(p.available_mb for p in self.profiles) / len(self.profiles)

        return MemoryProfile(
            timestamp=datetime.now(),
            rss_mb=avg_rss,
            vms_mb=avg_vms,
            percent=avg_percent,
            available_mb=avg_available
        )

    def is_memory_critical(self, threshold_mb: float = 2000) -> bool:
        """Check if memory usage is critical.
        
        Args:
            threshold_mb: Memory threshold in MB
            
        Returns:
            True if current memory exceeds threshold
        """
        profile = self.profile()
        if not profile:
            return False
        return profile.rss_mb > threshold_mb

    def get_memory_report(self) -> Dict[str, Any]:
        """Get comprehensive memory report.
        
        Returns:
            Dictionary with memory statistics
        """
        current = self.profile()
        peak = self.get_peak_memory()
        average = self.get_average_memory()

        return {
            "current": {
                "rss_mb": current.rss_mb if current else 0,
                "vms_mb": current.vms_mb if current else 0,
                "percent": current.percent if current else 0,
                "available_mb": current.available_mb if current else 0,
            },
            "peak": {
                "rss_mb": peak.rss_mb if peak else 0,
                "timestamp": peak.timestamp.isoformat() if peak else None,
            },
            "average": {
                "rss_mb": average.rss_mb if average else 0,
                "vms_mb": average.vms_mb if average else 0,
                "percent": average.percent if average else 0,
            },
            "profile_count": len(self.profiles),
        }


class LazyModelLoader:
    """Lazy loading for AI models to reduce startup memory."""

    def __init__(self):
        """Initialize lazy model loader."""
        self.logger = Logger("LazyModelLoader")
        self.loaded_models: Dict[str, Any] = {}
        self.model_paths: Dict[str, str] = {}
        self.lock = threading.Lock()

    def register_model(self, model_name: str, model_path: str) -> None:
        """Register a model for lazy loading.
        
        Args:
            model_name: Name of the model
            model_path: Path to model file
        """
        self.model_paths[model_name] = model_path
        self.logger.info(f"Registered model: {model_name}")

    def load_model(self, model_name: str) -> Optional[Any]:
        """Load a model on demand.
        
        Args:
            model_name: Name of model to load
            
        Returns:
            Loaded model or None on error
        """
        with self.lock:
            # Return if already loaded
            if model_name in self.loaded_models:
                self.logger.info(f"Model {model_name} already loaded")
                return self.loaded_models[model_name]

            # Check if model is registered
            if model_name not in self.model_paths:
                self.logger.error(f"Model {model_name} not registered")
                return None

            try:
                model_path = self.model_paths[model_name]
                self.logger.info(f"Loading model {model_name} from {model_path}")

                # Load model based on type
                if model_name == "whisper":
                    model = self._load_whisper_model(model_path)
                elif model_name == "llama":
                    model = self._load_llama_model(model_path)
                elif model_name == "piper":
                    model = self._load_piper_model(model_path)
                else:
                    self.logger.warning(f"Unknown model type: {model_name}")
                    return None

                if model:
                    self.loaded_models[model_name] = model
                    self.logger.info(f"Successfully loaded model: {model_name}")

                return model

            except Exception as e:
                self.logger.error(f"Failed to load model {model_name}: {e}")
                return None

    def _load_whisper_model(self, model_path: str) -> Optional[Any]:
        """Load Whisper speech recognition model.
        
        Args:
            model_path: Path to Whisper model
            
        Returns:
            Loaded model or None
        """
        try:
            # In production, would use: import whisper; return whisper.load_model(model_path)
            # For now, return mock
            self.logger.info(f"Whisper model loaded from {model_path}")
            return {"type": "whisper", "path": model_path}
        except Exception as e:
            self.logger.error(f"Failed to load Whisper model: {e}")
            return None

    def _load_llama_model(self, model_path: str) -> Optional[Any]:
        """Load Llama 2 language model.
        
        Args:
            model_path: Path to Llama model
            
        Returns:
            Loaded model or None
        """
        try:
            # In production, would use: from llama_cpp import Llama; return Llama(model_path)
            # For now, return mock
            self.logger.info(f"Llama model loaded from {model_path}")
            return {"type": "llama", "path": model_path}
        except Exception as e:
            self.logger.error(f"Failed to load Llama model: {e}")
            return None

    def _load_piper_model(self, model_path: str) -> Optional[Any]:
        """Load Piper text-to-speech model.
        
        Args:
            model_path: Path to Piper model
            
        Returns:
            Loaded model or None
        """
        try:
            # In production, would use: from piper import PiperTTS; return PiperTTS(model_path)
            # For now, return mock
            self.logger.info(f"Piper model loaded from {model_path}")
            return {"type": "piper", "path": model_path}
        except Exception as e:
            self.logger.error(f"Failed to load Piper model: {e}")
            return None

    def unload_model(self, model_name: str) -> bool:
        """Unload a model to free memory.
        
        Args:
            model_name: Name of model to unload
            
        Returns:
            True if successful, False otherwise
        """
        with self.lock:
            if model_name in self.loaded_models:
                try:
                    del self.loaded_models[model_name]
                    self.logger.info(f"Unloaded model: {model_name}")
                    return True
                except Exception as e:
                    self.logger.error(f"Failed to unload model {model_name}: {e}")
                    return False
            return False

    def get_loaded_models(self) -> List[str]:
        """Get list of currently loaded models.
        
        Returns:
            List of loaded model names
        """
        return list(self.loaded_models.keys())

    def is_model_loaded(self, model_name: str) -> bool:
        """Check if a model is loaded.
        
        Args:
            model_name: Name of model to check
            
        Returns:
            True if model is loaded
        """
        return model_name in self.loaded_models


class SessionGarbageCollector:
    """Garbage collection for completed sessions."""

    def __init__(self, db_path: str = "vask_data.db"):
        """Initialize session garbage collector.
        
        Args:
            db_path: Path to SQLite database
        """
        self.logger = Logger("SessionGarbageCollector")
        self.db_path = db_path
        self.retention_days = 30  # Keep sessions for 30 days by default

    def collect_garbage(self, older_than_days: Optional[int] = None) -> int:
        """Collect garbage from completed sessions.
        
        Args:
            older_than_days: Delete sessions older than this many days
            
        Returns:
            Number of sessions deleted
        """
        try:
            days = older_than_days or self.retention_days
            cutoff_date = (datetime.now() - timedelta(days=days)).isoformat()

            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Count sessions to delete
            cursor.execute("""
                SELECT COUNT(*) FROM conversations 
                WHERE ended_at IS NOT NULL AND ended_at < ?
            """, (cutoff_date,))
            count = cursor.fetchone()[0]

            # Delete old sessions
            cursor.execute("""
                DELETE FROM conversations 
                WHERE ended_at IS NOT NULL AND ended_at < ?
            """, (cutoff_date,))

            # Also delete associated mood history
            cursor.execute("""
                DELETE FROM mood_history 
                WHERE timestamp < ?
            """, (cutoff_date,))

            conn.commit()
            conn.close()

            self.logger.info(f"Garbage collection: deleted {count} sessions older than {days} days")
            return count

        except Exception as e:
            self.logger.error(f"Failed to collect garbage: {e}")
            return 0

    def optimize_database(self) -> bool:
        """Optimize database by running VACUUM and ANALYZE.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Run VACUUM to reclaim space
            cursor.execute("VACUUM")
            self.logger.info("Database VACUUM completed")

            # Run ANALYZE to update statistics
            cursor.execute("ANALYZE")
            self.logger.info("Database ANALYZE completed")

            conn.commit()
            conn.close()

            return True

        except Exception as e:
            self.logger.error(f"Failed to optimize database: {e}")
            return False

    def get_database_size(self) -> float:
        """Get database file size in MB.
        
        Returns:
            Database size in MB
        """
        try:
            import os
            size_bytes = os.path.getsize(self.db_path)
            return size_bytes / (1024 * 1024)
        except Exception as e:
            self.logger.error(f"Failed to get database size: {e}")
            return 0.0


class DatabaseOptimizer:
    """Optimize database queries with indexing and caching."""

    def __init__(self, db_path: str = "vask_data.db"):
        """Initialize database optimizer.
        
        Args:
            db_path: Path to SQLite database
        """
        self.logger = Logger("DatabaseOptimizer")
        self.db_path = db_path
        self.query_cache: Dict[str, tuple] = {}
        self.cache_ttl = timedelta(minutes=5)
        self.cache_timestamps: Dict[str, datetime] = {}

    def create_indexes(self) -> bool:
        """Create indexes on frequently queried columns.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Indexes for conversations table
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_conversations_user_id 
                ON conversations(user_id)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_conversations_created_at 
                ON conversations(created_at)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_conversations_ended_at 
                ON conversations(ended_at)
            """)

            # Indexes for mood_history table
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_mood_user_id 
                ON mood_history(user_id)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_mood_timestamp 
                ON mood_history(timestamp)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_mood_classification 
                ON mood_history(mood_classification)
            """)

            # Indexes for user_profiles table
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_user_profiles_user_id 
                ON user_profiles(user_id)
            """)

            conn.commit()
            conn.close()

            self.logger.info("Database indexes created successfully")
            return True

        except Exception as e:
            self.logger.error(f"Failed to create indexes: {e}")
            return False

    def cache_query(self, query_key: str, result: tuple) -> None:
        """Cache query result.
        
        Args:
            query_key: Unique key for query
            result: Query result to cache
        """
        self.query_cache[query_key] = result
        self.cache_timestamps[query_key] = datetime.now()

    def get_cached_query(self, query_key: str) -> Optional[tuple]:
        """Get cached query result if still valid.
        
        Args:
            query_key: Unique key for query
            
        Returns:
            Cached result or None if expired/not found
        """
        if query_key not in self.query_cache:
            return None

        timestamp = self.cache_timestamps.get(query_key)
        if not timestamp or datetime.now() - timestamp > self.cache_ttl:
            del self.query_cache[query_key]
            del self.cache_timestamps[query_key]
            return None

        return self.query_cache[query_key]

    def clear_cache(self) -> None:
        """Clear query cache."""
        self.query_cache.clear()
        self.cache_timestamps.clear()
        self.logger.info("Query cache cleared")

    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics.
        
        Returns:
            Dictionary with cache stats
        """
        return {
            "cached_queries": len(self.query_cache),
            "cache_size_bytes": sum(len(str(v)) for v in self.query_cache.values()),
        }


class PerformanceOptimizer:
    """Main performance optimization coordinator."""

    def __init__(self, db_path: str = "vask_data.db"):
        """Initialize performance optimizer.
        
        Args:
            db_path: Path to SQLite database
        """
        self.logger = Logger("PerformanceOptimizer")
        self.memory_profiler = MemoryProfiler()
        self.lazy_loader = LazyModelLoader()
        self.gc_collector = SessionGarbageCollector(db_path)
        self.db_optimizer = DatabaseOptimizer(db_path)
        self.db_path = db_path

    def initialize(self) -> bool:
        """Initialize performance optimization.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            # Create database indexes
            if not self.db_optimizer.create_indexes():
                self.logger.warning("Failed to create database indexes")

            # Run initial garbage collection
            self.gc_collector.collect_garbage(older_than_days=30)

            # Optimize database
            self.gc_collector.optimize_database()

            self.logger.info("Performance optimizer initialized")
            return True

        except Exception as e:
            self.logger.error(f"Failed to initialize performance optimizer: {e}")
            return False

    def register_model(self, model_name: str, model_path: str) -> None:
        """Register a model for lazy loading.
        
        Args:
            model_name: Name of the model
            model_path: Path to model file
        """
        self.lazy_loader.register_model(model_name, model_path)

    def load_model(self, model_name: str) -> Optional[Any]:
        """Load a model on demand.
        
        Args:
            model_name: Name of model to load
            
        Returns:
            Loaded model or None
        """
        return self.lazy_loader.load_model(model_name)

    def unload_model(self, model_name: str) -> bool:
        """Unload a model to free memory.
        
        Args:
            model_name: Name of model to unload
            
        Returns:
            True if successful
        """
        return self.lazy_loader.unload_model(model_name)

    def get_performance_metrics(self) -> PerformanceMetrics:
        """Get current performance metrics.
        
        Returns:
            PerformanceMetrics snapshot
        """
        try:
            memory_profile = self.memory_profiler.profile()
            cpu_percent = psutil.cpu_percent(interval=0.1)
            db_size = self.gc_collector.get_database_size()

            return PerformanceMetrics(
                timestamp=datetime.now(),
                memory_profile=memory_profile,
                cpu_percent=cpu_percent,
                active_sessions=0,  # Would be updated by session manager
                cached_responses=0,  # Would be updated by AI model
                database_size_mb=db_size
            )

        except Exception as e:
            self.logger.error(f"Failed to get performance metrics: {e}")
            return None

    def get_performance_report(self) -> Dict[str, Any]:
        """Get comprehensive performance report.
        
        Returns:
            Dictionary with performance statistics
        """
        return {
            "memory": self.memory_profiler.get_memory_report(),
            "loaded_models": self.lazy_loader.get_loaded_models(),
            "database_size_mb": self.gc_collector.get_database_size(),
            "query_cache_stats": self.db_optimizer.get_cache_stats(),
            "timestamp": datetime.now().isoformat(),
        }

    def run_maintenance(self) -> bool:
        """Run maintenance tasks.
        
        Returns:
            True if successful
        """
        try:
            # Collect garbage
            self.gc_collector.collect_garbage()

            # Optimize database
            self.gc_collector.optimize_database()

            # Clear query cache
            self.db_optimizer.clear_cache()

            # Force garbage collection
            gc.collect()

            self.logger.info("Maintenance completed")
            return True

        except Exception as e:
            self.logger.error(f"Failed to run maintenance: {e}")
            return False
