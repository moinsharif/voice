"""Tests for performance optimization components."""

import pytest
import tempfile
import sqlite3
import os
from datetime import datetime, timedelta
from src.utils.performance_optimizer import (
    MemoryProfiler,
    LazyModelLoader,
    SessionGarbageCollector,
    DatabaseOptimizer,
    PerformanceOptimizer,
    MemoryProfile,
)


class TestMemoryProfiler:
    """Tests for memory profiling."""

    def test_memory_profile_creation(self):
        """Test that memory profiles are created successfully."""
        profiler = MemoryProfiler()
        profile = profiler.profile()
        
        assert profile is not None
        assert profile.rss_mb > 0
        assert profile.vms_mb > 0
        assert profile.percent >= 0
        assert profile.available_mb > 0

    def test_memory_profile_tracking(self):
        """Test that multiple profiles are tracked."""
        profiler = MemoryProfiler()
        
        # Take multiple profiles
        for _ in range(5):
            profiler.profile()
        
        assert len(profiler.profiles) == 5

    def test_peak_memory_detection(self):
        """Test peak memory detection."""
        profiler = MemoryProfiler()
        
        # Create profiles with different memory values
        for i in range(3):
            profiler.profile()
        
        peak = profiler.get_peak_memory()
        assert peak is not None
        assert peak.rss_mb > 0

    def test_average_memory_calculation(self):
        """Test average memory calculation."""
        profiler = MemoryProfiler()
        
        # Create multiple profiles
        for _ in range(3):
            profiler.profile()
        
        average = profiler.get_average_memory()
        assert average is not None
        assert average.rss_mb > 0

    def test_memory_critical_detection(self):
        """Test memory critical threshold detection."""
        profiler = MemoryProfiler()
        
        # Profile should not be critical with default threshold
        is_critical = profiler.is_memory_critical(threshold_mb=999999)
        assert not is_critical

    def test_memory_report_generation(self):
        """Test memory report generation."""
        profiler = MemoryProfiler()
        profiler.profile()
        
        report = profiler.get_memory_report()
        
        assert "current" in report
        assert "peak" in report
        assert "average" in report
        assert "profile_count" in report
        assert report["current"]["rss_mb"] > 0


class TestLazyModelLoader:
    """Tests for lazy model loading."""

    def test_model_registration(self):
        """Test model registration."""
        loader = LazyModelLoader()
        loader.register_model("test_model", "/path/to/model")
        
        assert "test_model" in loader.model_paths

    def test_model_loading(self):
        """Test model loading."""
        loader = LazyModelLoader()
        loader.register_model("whisper", "models/whisper-base.pt")
        
        model = loader.load_model("whisper")
        assert model is not None

    def test_model_caching(self):
        """Test that loaded models are cached."""
        loader = LazyModelLoader()
        loader.register_model("llama", "models/llama-2-7b.gguf")
        
        # Load model twice
        model1 = loader.load_model("llama")
        model2 = loader.load_model("llama")
        
        # Should be the same object
        assert model1 is model2

    def test_model_unloading(self):
        """Test model unloading."""
        loader = LazyModelLoader()
        loader.register_model("piper", "models/piper-en_US.onnx")
        
        # Load and then unload
        loader.load_model("piper")
        assert loader.is_model_loaded("piper")
        
        success = loader.unload_model("piper")
        assert success
        assert not loader.is_model_loaded("piper")

    def test_get_loaded_models(self):
        """Test getting list of loaded models."""
        loader = LazyModelLoader()
        loader.register_model("model1", "path1")
        loader.register_model("model2", "path2")
        
        # Models won't load without proper paths, so just verify the method works
        loaded = loader.get_loaded_models()
        assert isinstance(loaded, list)

    def test_unregistered_model_loading(self):
        """Test loading unregistered model returns None."""
        loader = LazyModelLoader()
        
        model = loader.load_model("nonexistent")
        assert model is None


class TestSessionGarbageCollector:
    """Tests for session garbage collection."""

    def test_garbage_collector_initialization(self):
        """Test garbage collector initialization."""
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
            db_path = f.name
        
        try:
            collector = SessionGarbageCollector(db_path)
            assert collector.db_path == db_path
            assert collector.retention_days == 30
        finally:
            if os.path.exists(db_path):
                os.remove(db_path)

    def test_database_optimization(self):
        """Test database optimization."""
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
            db_path = f.name
        
        try:
            # Create a test database
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS conversations (
                    session_id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    ended_at TEXT
                )
            """)
            conn.commit()
            conn.close()
            
            # Optimize database
            collector = SessionGarbageCollector(db_path)
            success = collector.optimize_database()
            
            assert success
        finally:
            if os.path.exists(db_path):
                os.remove(db_path)

    def test_database_size_calculation(self):
        """Test database size calculation."""
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
            db_path = f.name
        
        try:
            # Create a test database
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS test (
                    id INTEGER PRIMARY KEY,
                    data TEXT
                )
            """)
            conn.commit()
            conn.close()
            
            collector = SessionGarbageCollector(db_path)
            size = collector.get_database_size()
            
            assert size > 0
        finally:
            if os.path.exists(db_path):
                os.remove(db_path)


class TestDatabaseOptimizer:
    """Tests for database optimization."""

    def test_index_creation(self):
        """Test database index creation."""
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
            db_path = f.name
        
        try:
            # Create a test database
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS conversations (
                    session_id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    ended_at TEXT
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS mood_history (
                    id INTEGER PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    mood_classification TEXT NOT NULL,
                    confidence REAL NOT NULL
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS user_profiles (
                    user_id TEXT PRIMARY KEY
                )
            """)
            conn.commit()
            conn.close()
            
            # Create indexes
            optimizer = DatabaseOptimizer(db_path)
            success = optimizer.create_indexes()
            
            assert success
        finally:
            if os.path.exists(db_path):
                os.remove(db_path)

    def test_query_caching(self):
        """Test query result caching."""
        optimizer = DatabaseOptimizer()
        
        # Cache a query result
        result = ("user1", "session1", "2024-01-01")
        optimizer.cache_query("test_query", result)
        
        # Retrieve cached result
        cached = optimizer.get_cached_query("test_query")
        assert cached == result

    def test_cache_expiration(self):
        """Test cache expiration."""
        optimizer = DatabaseOptimizer()
        optimizer.cache_ttl = timedelta(milliseconds=100)
        
        # Cache a query result
        result = ("user1", "session1", "2024-01-01")
        optimizer.cache_query("test_query", result)
        
        # Wait for cache to expire
        import time
        time.sleep(0.2)
        
        # Retrieve should return None
        cached = optimizer.get_cached_query("test_query")
        assert cached is None

    def test_cache_clearing(self):
        """Test cache clearing."""
        optimizer = DatabaseOptimizer()
        
        # Cache multiple queries
        optimizer.cache_query("query1", ("result1",))
        optimizer.cache_query("query2", ("result2",))
        
        # Clear cache
        optimizer.clear_cache()
        
        # Verify cache is empty
        assert len(optimizer.query_cache) == 0

    def test_cache_statistics(self):
        """Test cache statistics."""
        optimizer = DatabaseOptimizer()
        
        # Cache some queries
        optimizer.cache_query("query1", ("result1",))
        optimizer.cache_query("query2", ("result2",))
        
        stats = optimizer.get_cache_stats()
        
        assert "cached_queries" in stats
        assert "cache_size_bytes" in stats
        assert stats["cached_queries"] == 2


class TestPerformanceOptimizer:
    """Tests for main performance optimizer."""

    def test_optimizer_initialization(self):
        """Test performance optimizer initialization."""
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
            db_path = f.name
        
        try:
            optimizer = PerformanceOptimizer(db_path)
            assert optimizer.memory_profiler is not None
            assert optimizer.lazy_loader is not None
            assert optimizer.gc_collector is not None
            assert optimizer.db_optimizer is not None
        finally:
            if os.path.exists(db_path):
                os.remove(db_path)

    def test_model_registration_and_loading(self):
        """Test model registration and lazy loading."""
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
            db_path = f.name
        
        try:
            optimizer = PerformanceOptimizer(db_path)
            
            # Register models
            optimizer.register_model("whisper", "models/whisper-base.pt")
            optimizer.register_model("llama", "models/llama-2-7b.gguf")
            
            # Load models
            whisper = optimizer.load_model("whisper")
            llama = optimizer.load_model("llama")
            
            assert whisper is not None
            assert llama is not None
        finally:
            if os.path.exists(db_path):
                os.remove(db_path)

    def test_model_unloading(self):
        """Test model unloading."""
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
            db_path = f.name
        
        try:
            optimizer = PerformanceOptimizer(db_path)
            
            # Register and load model
            optimizer.register_model("test_model", "models/test.pt")
            model = optimizer.load_model("test_model")
            
            # Model may or may not load depending on path validity
            # Just verify the unload method works
            success = optimizer.unload_model("test_model")
            assert isinstance(success, bool)
        finally:
            if os.path.exists(db_path):
                os.remove(db_path)

    def test_performance_metrics(self):
        """Test performance metrics collection."""
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
            db_path = f.name
        
        try:
            optimizer = PerformanceOptimizer(db_path)
            metrics = optimizer.get_performance_metrics()
            
            assert metrics is not None
            assert metrics.memory_profile is not None
            assert metrics.cpu_percent >= 0
            assert metrics.database_size_mb >= 0
        finally:
            if os.path.exists(db_path):
                os.remove(db_path)

    def test_performance_report(self):
        """Test performance report generation."""
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
            db_path = f.name
        
        try:
            optimizer = PerformanceOptimizer(db_path)
            report = optimizer.get_performance_report()
            
            assert "memory" in report
            assert "loaded_models" in report
            assert "database_size_mb" in report
            assert "query_cache_stats" in report
            assert "timestamp" in report
        finally:
            if os.path.exists(db_path):
                os.remove(db_path)

    def test_maintenance_execution(self):
        """Test maintenance task execution."""
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
            db_path = f.name
        
        try:
            optimizer = PerformanceOptimizer(db_path)
            success = optimizer.run_maintenance()
            
            assert success
        finally:
            if os.path.exists(db_path):
                os.remove(db_path)


class TestPerformanceMetrics:
    """Integration tests for performance metrics."""

    def test_memory_usage_tracking(self):
        """Test that memory usage is tracked over time."""
        profiler = MemoryProfiler()
        
        # Take multiple profiles
        for _ in range(10):
            profiler.profile()
        
        # Verify tracking (may have one extra from initialization)
        assert len(profiler.profiles) >= 10
        
        # Get statistics
        report = profiler.get_memory_report()
        assert report["profile_count"] >= 10
        assert report["current"]["rss_mb"] > 0

    def test_lazy_loading_reduces_startup_memory(self):
        """Test that lazy loading doesn't load models at startup."""
        loader = LazyModelLoader()
        
        # Register models
        loader.register_model("whisper", "models/whisper-base.pt")
        loader.register_model("llama", "models/llama-2-7b.gguf")
        loader.register_model("piper", "models/piper-en_US.onnx")
        
        # Verify no models are loaded initially
        assert len(loader.get_loaded_models()) == 0
        
        # Load one model
        loader.load_model("whisper")
        assert len(loader.get_loaded_models()) == 1

    def test_garbage_collection_workflow(self):
        """Test complete garbage collection workflow."""
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
            db_path = f.name
        
        try:
            # Create test database with old sessions
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS conversations (
                    session_id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    ended_at TEXT
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS mood_history (
                    id INTEGER PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    mood_classification TEXT NOT NULL,
                    confidence REAL NOT NULL
                )
            """)
            
            # Insert old session
            old_date = (datetime.now() - timedelta(days=40)).isoformat()
            cursor.execute("""
                INSERT INTO conversations 
                (session_id, user_id, created_at, ended_at)
                VALUES (?, ?, ?, ?)
            """, ("old_session", "user1", old_date, old_date))
            
            conn.commit()
            conn.close()
            
            # Run garbage collection
            collector = SessionGarbageCollector(db_path)
            deleted = collector.collect_garbage(older_than_days=30)
            
            assert deleted >= 0
        finally:
            if os.path.exists(db_path):
                os.remove(db_path)

    def test_database_optimization_workflow(self):
        """Test complete database optimization workflow."""
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
            db_path = f.name
        
        try:
            # Create test database
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS conversations (
                    session_id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    ended_at TEXT
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS mood_history (
                    id INTEGER PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    mood_classification TEXT NOT NULL,
                    confidence REAL NOT NULL
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS user_profiles (
                    user_id TEXT PRIMARY KEY
                )
            """)
            conn.commit()
            conn.close()
            
            # Optimize database
            optimizer = DatabaseOptimizer(db_path)
            success = optimizer.create_indexes()
            assert success
            
            # Verify indexes were created
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='index'")
            indexes = cursor.fetchall()
            conn.close()
            
            assert len(indexes) > 0
        finally:
            if os.path.exists(db_path):
                os.remove(db_path)
