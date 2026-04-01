"""Tests for offline operation verification."""

import pytest
import tempfile
import os
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path

from src.verification.offline_operation_verifier import (
    OfflineOperationVerifier,
    VerificationResult
)
from src.main import VaskApplication


class TestOfflineOperationVerifier:
    """Tests for OfflineOperationVerifier class."""

    def test_verifier_initialization(self):
        """Test OfflineOperationVerifier initializes correctly."""
        verifier = OfflineOperationVerifier()
        assert verifier is not None
        assert verifier.verification_results == []

    def test_verifier_with_config(self):
        """Test OfflineOperationVerifier accepts configuration."""
        config = {"offline_mode": True}
        verifier = OfflineOperationVerifier(config=config)
        assert verifier.config == config

    def test_verification_result_creation(self):
        """Test VerificationResult dataclass creation."""
        result = VerificationResult(
            is_available=True,
            component_name="Test Component",
            error_message=None,
            installation_instructions=None
        )
        assert result.is_available is True
        assert result.component_name == "Test Component"
        assert result.error_message is None

    def test_verification_result_with_error(self):
        """Test VerificationResult with error information."""
        result = VerificationResult(
            is_available=False,
            component_name="Test Component",
            error_message="Component not found",
            installation_instructions="Install via pip"
        )
        assert result.is_available is False
        assert result.error_message == "Component not found"
        assert result.installation_instructions == "Install via pip"


class TestModelAvailabilityChecks:
    """Tests for model availability checking."""

    def test_check_whisper_model_available(self):
        """Test Whisper model detection when available."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create mock Whisper model directory
            whisper_path = os.path.join(tmpdir, "models", "whisper-base")
            os.makedirs(whisper_path)
            
            verifier = OfflineOperationVerifier()
            
            # Mock path checking
            with patch.object(verifier, '_path_exists', return_value=True):
                result = verifier._check_model_availability(
                    "whisper",
                    verifier.MODEL_CHECKS["whisper"]
                )
            
            assert result.is_available is True
            assert result.component_name == "Whisper Speech Recognition Model"

    def test_check_whisper_model_missing(self):
        """Test Whisper model detection when missing."""
        verifier = OfflineOperationVerifier()
        
        # Mock path checking to return False
        with patch.object(verifier, '_path_exists', return_value=False):
            result = verifier._check_model_availability(
                "whisper",
                verifier.MODEL_CHECKS["whisper"]
            )
        
        assert result.is_available is False
        assert "not found" in result.error_message.lower()
        assert result.installation_instructions is not None

    def test_check_llama2_model_available(self):
        """Test Llama 2 model detection when available."""
        verifier = OfflineOperationVerifier()
        
        with patch.object(verifier, '_path_exists', return_value=True):
            result = verifier._check_model_availability(
                "llama2",
                verifier.MODEL_CHECKS["llama2"]
            )
        
        assert result.is_available is True
        assert result.component_name == "Llama 2 Language Model"

    def test_check_llama2_model_missing(self):
        """Test Llama 2 model detection when missing."""
        verifier = OfflineOperationVerifier()
        
        with patch.object(verifier, '_path_exists', return_value=False):
            result = verifier._check_model_availability(
                "llama2",
                verifier.MODEL_CHECKS["llama2"]
            )
        
        assert result.is_available is False
        assert result.installation_instructions is not None

    def test_check_piper_model_available(self):
        """Test Piper TTS model detection when available."""
        verifier = OfflineOperationVerifier()
        
        with patch.object(verifier, '_path_exists', return_value=True):
            result = verifier._check_model_availability(
                "piper",
                verifier.MODEL_CHECKS["piper"]
            )
        
        assert result.is_available is True
        assert result.component_name == "Piper Text-to-Speech Model"

    def test_check_piper_model_missing(self):
        """Test Piper TTS model detection when missing."""
        verifier = OfflineOperationVerifier()
        
        with patch.object(verifier, '_path_exists', return_value=False):
            result = verifier._check_model_availability(
                "piper",
                verifier.MODEL_CHECKS["piper"]
            )
        
        assert result.is_available is False
        assert result.installation_instructions is not None

    def test_check_mediapipe_models_available(self):
        """Test MediaPipe models detection when available."""
        verifier = OfflineOperationVerifier()
        
        with patch.object(verifier, '_path_exists', return_value=True):
            result = verifier._check_model_availability(
                "mediapipe",
                verifier.MODEL_CHECKS["mediapipe"]
            )
        
        assert result.is_available is True
        assert result.component_name == "MediaPipe Face Detection Models"

    def test_check_mediapipe_models_missing(self):
        """Test MediaPipe models detection when missing."""
        verifier = OfflineOperationVerifier()
        
        with patch.object(verifier, '_path_exists', return_value=False):
            result = verifier._check_model_availability(
                "mediapipe",
                verifier.MODEL_CHECKS["mediapipe"]
            )
        
        assert result.is_available is False
        assert result.installation_instructions is not None


class TestSQLiteVerification:
    """Tests for SQLite database verification."""

    def test_sqlite_available(self):
        """Test SQLite availability check when available."""
        verifier = OfflineOperationVerifier()
        verifier._check_sqlite_database()
        
        # Find SQLite result
        sqlite_result = None
        for result in verifier.verification_results:
            if "SQLite" in result.component_name:
                sqlite_result = result
                break
        
        assert sqlite_result is not None
        assert sqlite_result.is_available is True

    def test_sqlite_unavailable(self):
        """Test SQLite availability check when unavailable."""
        verifier = OfflineOperationVerifier()
        
        # Mock import failure
        with patch('builtins.__import__', side_effect=ImportError("No module named 'sqlite3'")):
            verifier._check_sqlite_database()
        
        # Find SQLite result
        sqlite_result = None
        for result in verifier.verification_results:
            if "SQLite" in result.component_name:
                sqlite_result = result
                break
        
        assert sqlite_result is not None
        assert sqlite_result.is_available is False


class TestOfflineModeConfiguration:
    """Tests for offline mode configuration verification."""

    def test_offline_mode_enabled(self):
        """Test offline mode verification when enabled."""
        config = {"offline_mode": True}
        verifier = OfflineOperationVerifier(config=config)
        verifier._check_no_external_calls()
        
        # Find offline mode result
        offline_result = None
        for result in verifier.verification_results:
            if "Offline Mode" in result.component_name:
                offline_result = result
                break
        
        assert offline_result is not None
        assert offline_result.is_available is True

    def test_offline_mode_disabled(self):
        """Test offline mode verification when disabled."""
        config = {"offline_mode": False}
        verifier = OfflineOperationVerifier(config=config)
        verifier._check_no_external_calls()
        
        # Find offline mode result
        offline_result = None
        for result in verifier.verification_results:
            if "Offline Mode" in result.component_name:
                offline_result = result
                break
        
        assert offline_result is not None
        assert offline_result.is_available is False
        assert "not enabled" in offline_result.error_message.lower()

    def test_offline_mode_default(self):
        """Test offline mode defaults to True when not specified."""
        config = {}
        verifier = OfflineOperationVerifier(config=config)
        verifier._check_no_external_calls()
        
        # Find offline mode result
        offline_result = None
        for result in verifier.verification_results:
            if "Offline Mode" in result.component_name:
                offline_result = result
                break
        
        assert offline_result is not None
        assert offline_result.is_available is True


class TestCompleteVerification:
    """Tests for complete offline operation verification."""

    def test_verify_offline_operation_all_pass(self):
        """Test complete verification when all checks pass."""
        verifier = OfflineOperationVerifier(config={"offline_mode": True})
        
        # Mock all path checks to pass
        with patch.object(verifier, '_path_exists', return_value=True):
            all_passed, results = verifier.verify_offline_operation()
        
        assert all_passed is True
        assert len(results) > 0
        assert all(result.is_available for result in results)

    def test_verify_offline_operation_some_fail(self):
        """Test complete verification when some checks fail."""
        verifier = OfflineOperationVerifier(config={"offline_mode": True})
        
        # Mock path checks to fail
        with patch.object(verifier, '_path_exists', return_value=False):
            all_passed, results = verifier.verify_offline_operation()
        
        assert all_passed is False
        # Should have some failed results
        failed_results = [r for r in results if not r.is_available]
        assert len(failed_results) > 0

    def test_verify_offline_operation_offline_mode_disabled(self):
        """Test complete verification when offline mode is disabled."""
        verifier = OfflineOperationVerifier(config={"offline_mode": False})
        
        with patch.object(verifier, '_path_exists', return_value=True):
            all_passed, results = verifier.verify_offline_operation()
        
        assert all_passed is False
        # Should have offline mode failure
        offline_failures = [r for r in results if "Offline Mode" in r.component_name and not r.is_available]
        assert len(offline_failures) > 0


class TestErrorMessages:
    """Tests for error message generation."""

    def test_get_error_messages(self):
        """Test error message retrieval."""
        verifier = OfflineOperationVerifier()
        
        # Add some failed results
        verifier.verification_results = [
            VerificationResult(
                is_available=False,
                component_name="Test Component 1",
                error_message="Error 1",
                installation_instructions=None
            ),
            VerificationResult(
                is_available=True,
                component_name="Test Component 2",
                error_message=None,
                installation_instructions=None
            ),
            VerificationResult(
                is_available=False,
                component_name="Test Component 3",
                error_message="Error 3",
                installation_instructions=None
            )
        ]
        
        errors = verifier.get_error_messages()
        assert len(errors) == 2
        assert "Error 1" in errors
        assert "Error 3" in errors

    def test_get_installation_instructions(self):
        """Test installation instructions retrieval."""
        verifier = OfflineOperationVerifier()
        
        # Add some failed results with instructions
        verifier.verification_results = [
            VerificationResult(
                is_available=False,
                component_name="Test Component 1",
                error_message="Error 1",
                installation_instructions="Install via pip"
            ),
            VerificationResult(
                is_available=True,
                component_name="Test Component 2",
                error_message=None,
                installation_instructions=None
            )
        ]
        
        instructions = verifier.get_installation_instructions()
        assert "Install via pip" in instructions
        assert "Test Component 1" in instructions

    def test_generate_verification_report(self):
        """Test verification report generation."""
        verifier = OfflineOperationVerifier(config={"offline_mode": True})
        
        with patch.object(verifier, '_path_exists', return_value=True):
            verifier.verify_offline_operation()
        
        report = verifier.generate_verification_report()
        
        assert "OFFLINE OPERATION VERIFICATION REPORT" in report
        assert "DETAILED RESULTS" in report
        assert "✓ PASS" in report or "✗ FAIL" in report


class TestVaskApplicationOfflineVerification:
    """Tests for offline verification integration in VaskApplication."""

    def test_vask_app_offline_verification_on_init(self):
        """Test VaskApplication runs offline verification on initialization."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create config file
            config_path = os.path.join(tmpdir, "config.yaml")
            with open(config_path, 'w') as f:
                f.write("""version: "1.0.0"
offline_mode: true
language: "en"
voice_id: "en_US-lessac-medium"
speaking_rate: 1.0
listening_sensitivity: 0.8
mood_sensitivity: 0.7
response_tone: "empathetic"
enable_camera: false
enable_audio_output: false
enable_learning: true
max_context_exchanges: 10
response_timeout_seconds: 2
encryption_enabled: true
auto_delete_after_days: null
whisper_model_path: "models/whisper-base"
llama_model_path: "models/llama-2-7b"
piper_model_path: "models/piper"
""")
            
            # Mock path checking to pass
            with patch('src.verification.offline_operation_verifier.os.path.exists', return_value=True):
                with patch('src.main.PersistenceLayer'):
                    app = VaskApplication(config_path=config_path)
                    assert app.offline_verifier is not None

    def test_vask_app_verify_offline_operation_method(self):
        """Test VaskApplication.verify_offline_operation() method."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = os.path.join(tmpdir, "config.yaml")
            with open(config_path, 'w') as f:
                f.write("""version: "1.0.0"
offline_mode: true
language: "en"
voice_id: "en_US-lessac-medium"
speaking_rate: 1.0
listening_sensitivity: 0.8
mood_sensitivity: 0.7
response_tone: "empathetic"
enable_camera: false
enable_audio_output: false
enable_learning: true
max_context_exchanges: 10
response_timeout_seconds: 2
encryption_enabled: true
auto_delete_after_days: null
whisper_model_path: "models/whisper-base"
llama_model_path: "models/llama-2-7b"
piper_model_path: "models/piper"
""")
            
            with patch('src.verification.offline_operation_verifier.os.path.exists', return_value=True):
                with patch('src.main.PersistenceLayer'):
                    app = VaskApplication(config_path=config_path)
                    result = app.verify_offline_operation()
                    assert isinstance(result, bool)

    def test_vask_app_check_model_availability(self):
        """Test VaskApplication.check_model_availability() method."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = os.path.join(tmpdir, "config.yaml")
            with open(config_path, 'w') as f:
                f.write("""version: "1.0.0"
offline_mode: true
language: "en"
voice_id: "en_US-lessac-medium"
speaking_rate: 1.0
listening_sensitivity: 0.8
mood_sensitivity: 0.7
response_tone: "empathetic"
enable_camera: false
enable_audio_output: false
enable_learning: true
max_context_exchanges: 10
response_timeout_seconds: 2
encryption_enabled: true
auto_delete_after_days: null
whisper_model_path: "models/whisper-base"
llama_model_path: "models/llama-2-7b"
piper_model_path: "models/piper"
""")
            
            with patch('src.verification.offline_operation_verifier.os.path.exists', return_value=True):
                with patch('src.main.PersistenceLayer'):
                    app = VaskApplication(config_path=config_path)
                    availability = app.check_model_availability()
                    assert isinstance(availability, dict)

    def test_vask_app_check_no_external_calls(self):
        """Test VaskApplication.check_no_external_calls() method."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = os.path.join(tmpdir, "config.yaml")
            with open(config_path, 'w') as f:
                f.write("""version: "1.0.0"
offline_mode: true
language: "en"
voice_id: "en_US-lessac-medium"
speaking_rate: 1.0
listening_sensitivity: 0.8
mood_sensitivity: 0.7
response_tone: "empathetic"
enable_camera: false
enable_audio_output: false
enable_learning: true
max_context_exchanges: 10
response_timeout_seconds: 2
encryption_enabled: true
auto_delete_after_days: null
whisper_model_path: "models/whisper-base"
llama_model_path: "models/llama-2-7b"
piper_model_path: "models/piper"
""")
            
            with patch('src.verification.offline_operation_verifier.os.path.exists', return_value=True):
                with patch('src.main.PersistenceLayer'):
                    app = VaskApplication(config_path=config_path)
                    result = app.check_no_external_calls()
                    assert isinstance(result, bool)
                    assert result is True

    def test_vask_app_get_offline_verification_report(self):
        """Test VaskApplication.get_offline_verification_report() method."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = os.path.join(tmpdir, "config.yaml")
            with open(config_path, 'w') as f:
                f.write("""version: "1.0.0"
offline_mode: true
language: "en"
voice_id: "en_US-lessac-medium"
speaking_rate: 1.0
listening_sensitivity: 0.8
mood_sensitivity: 0.7
response_tone: "empathetic"
enable_camera: false
enable_audio_output: false
enable_learning: true
max_context_exchanges: 10
response_timeout_seconds: 2
encryption_enabled: true
auto_delete_after_days: null
whisper_model_path: "models/whisper-base"
llama_model_path: "models/llama-2-7b"
piper_model_path: "models/piper"
""")
            
            with patch('src.verification.offline_operation_verifier.os.path.exists', return_value=True):
                with patch('src.main.PersistenceLayer'):
                    app = VaskApplication(config_path=config_path)
                    report = app.get_offline_verification_report()
                    assert isinstance(report, str)
                    assert "OFFLINE OPERATION VERIFICATION REPORT" in report


class TestPathExistence:
    """Tests for path existence checking."""

    def test_path_exists_file(self):
        """Test path existence check for files."""
        with tempfile.NamedTemporaryFile() as tmp:
            verifier = OfflineOperationVerifier()
            assert verifier._path_exists(tmp.name) is True

    def test_path_exists_directory(self):
        """Test path existence check for directories."""
        with tempfile.TemporaryDirectory() as tmpdir:
            verifier = OfflineOperationVerifier()
            assert verifier._path_exists(tmpdir) is True

    def test_path_not_exists(self):
        """Test path existence check for non-existent path."""
        verifier = OfflineOperationVerifier()
        assert verifier._path_exists("/nonexistent/path/to/file") is False
