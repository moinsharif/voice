"""Tests for Configuration system."""

import pytest
import json
import yaml
import tempfile
from pathlib import Path

from src.config.configuration import Configuration
from src.config.config_system import ConfigurationSystem, ValidationError


class TestConfiguration:
    """Tests for Configuration dataclass."""

    def test_configuration_defaults(self):
        """Test that Configuration has correct default values."""
        config = Configuration()
        assert config.version == "1.0.0"
        assert config.offline_mode is True
        assert config.language == "en"
        assert config.voice_id == "en_US-hfc_female-medium"
        assert config.speaking_rate == 1.0
        assert config.listening_sensitivity == 0.8
        assert config.enable_camera is True
        assert config.enable_audio_output is True
        assert config.enable_learning is True
        assert config.max_context_exchanges == 10
        assert config.response_timeout_seconds == 2
        assert config.encryption_enabled is True
        assert config.auto_delete_after_days is None
        assert config.whisper_model_path == "models/whisper-base"
        assert config.llama_model_path == "models/llama-2-7b-q4"
        assert config.piper_model_path == "models/piper-voices"
        assert config.mood_sensitivity == 0.8
        assert config.response_tone == "empathetic"

    def test_configuration_to_dict(self):
        """Test converting Configuration to dictionary."""
        config = Configuration()
        config_dict = config.to_dict()
        assert isinstance(config_dict, dict)
        assert config_dict["version"] == "1.0.0"
        assert config_dict["offline_mode"] is True
        assert config_dict["language"] == "en"

    def test_configuration_from_dict(self):
        """Test creating Configuration from dictionary."""
        data = {
            "version": "1.0.0",
            "offline_mode": True,
            "language": "en",
            "voice_id": "en_US-hfc_female-medium",
            "speaking_rate": 1.0,
            "listening_sensitivity": 0.8,
            "enable_camera": True,
            "enable_audio_output": True,
            "enable_learning": True,
            "max_context_exchanges": 10,
            "response_timeout_seconds": 2,
            "encryption_enabled": True,
            "auto_delete_after_days": None,
            "whisper_model_path": "models/whisper-base",
            "llama_model_path": "models/llama-2-7b-q4",
            "piper_model_path": "models/piper-voices",
            "mood_sensitivity": 0.8,
            "response_tone": "empathetic",
        }
        config = Configuration.from_dict(data)
        assert config.version == "1.0.0"
        assert config.language == "en"

    def test_configuration_custom_values(self):
        """Test Configuration with custom values."""
        config = Configuration(
            language="es",
            speaking_rate=1.5,
            enable_camera=False,
            response_tone="technical",
        )
        assert config.language == "es"
        assert config.speaking_rate == 1.5
        assert config.enable_camera is False
        assert config.response_tone == "technical"


class TestConfigurationSystemValidation:
    """Tests for ConfigurationSystem validation."""

    def test_validate_valid_configuration(self):
        """Test validation of valid configuration."""
        data = {
            "version": "1.0.0",
            "offline_mode": True,
            "language": "en",
            "voice_id": "en_US-hfc_female-medium",
            "speaking_rate": 1.0,
            "listening_sensitivity": 0.8,
            "enable_camera": True,
            "enable_audio_output": True,
            "enable_learning": True,
            "max_context_exchanges": 10,
            "response_timeout_seconds": 2,
            "encryption_enabled": True,
            "auto_delete_after_days": None,
            "whisper_model_path": "models/whisper-base",
            "llama_model_path": "models/llama-2-7b-q4",
            "piper_model_path": "models/piper-voices",
            "mood_sensitivity": 0.8,
            "response_tone": "empathetic",
        }
        # Should not raise
        ConfigurationSystem.validate_configuration(data)

    def test_validate_missing_required_field(self):
        """Test validation fails with missing required field."""
        data = {
            "version": "1.0.0",
            "offline_mode": True,
            # Missing language
            "voice_id": "en_US-hfc_female-medium",
            "speaking_rate": 1.0,
            "listening_sensitivity": 0.8,
            "enable_camera": True,
            "enable_audio_output": True,
            "enable_learning": True,
            "max_context_exchanges": 10,
            "response_timeout_seconds": 2,
            "encryption_enabled": True,
            "auto_delete_after_days": None,
            "whisper_model_path": "models/whisper-base",
            "llama_model_path": "models/llama-2-7b-q4",
            "piper_model_path": "models/piper-voices",
            "mood_sensitivity": 0.8,
            "response_tone": "empathetic",
        }
        with pytest.raises(ValidationError, match="Missing required field: language"):
            ConfigurationSystem.validate_configuration(data)

    def test_validate_invalid_type(self):
        """Test validation fails with invalid type."""
        data = {
            "version": "1.0.0",
            "offline_mode": "true",  # Should be bool
            "language": "en",
            "voice_id": "en_US-hfc_female-medium",
            "speaking_rate": 1.0,
            "listening_sensitivity": 0.8,
            "enable_camera": True,
            "enable_audio_output": True,
            "enable_learning": True,
            "max_context_exchanges": 10,
            "response_timeout_seconds": 2,
            "encryption_enabled": True,
            "auto_delete_after_days": None,
            "whisper_model_path": "models/whisper-base",
            "llama_model_path": "models/llama-2-7b-q4",
            "piper_model_path": "models/piper-voices",
            "mood_sensitivity": 0.8,
            "response_tone": "empathetic",
        }
        with pytest.raises(ValidationError, match="Invalid type for field"):
            ConfigurationSystem.validate_configuration(data)

    def test_validate_speaking_rate_below_minimum(self):
        """Test validation fails when speaking_rate is below minimum."""
        data = {
            "version": "1.0.0",
            "offline_mode": True,
            "language": "en",
            "voice_id": "en_US-hfc_female-medium",
            "speaking_rate": 0.2,  # Below minimum 0.5
            "listening_sensitivity": 0.8,
            "enable_camera": True,
            "enable_audio_output": True,
            "enable_learning": True,
            "max_context_exchanges": 10,
            "response_timeout_seconds": 2,
            "encryption_enabled": True,
            "auto_delete_after_days": None,
            "whisper_model_path": "models/whisper-base",
            "llama_model_path": "models/llama-2-7b-q4",
            "piper_model_path": "models/piper-voices",
            "mood_sensitivity": 0.8,
            "response_tone": "empathetic",
        }
        with pytest.raises(ValidationError, match="below minimum"):
            ConfigurationSystem.validate_configuration(data)

    def test_validate_speaking_rate_above_maximum(self):
        """Test validation fails when speaking_rate is above maximum."""
        data = {
            "version": "1.0.0",
            "offline_mode": True,
            "language": "en",
            "voice_id": "en_US-hfc_female-medium",
            "speaking_rate": 2.5,  # Above maximum 2.0
            "listening_sensitivity": 0.8,
            "enable_camera": True,
            "enable_audio_output": True,
            "enable_learning": True,
            "max_context_exchanges": 10,
            "response_timeout_seconds": 2,
            "encryption_enabled": True,
            "auto_delete_after_days": None,
            "whisper_model_path": "models/whisper-base",
            "llama_model_path": "models/llama-2-7b-q4",
            "piper_model_path": "models/piper-voices",
            "mood_sensitivity": 0.8,
            "response_tone": "empathetic",
        }
        with pytest.raises(ValidationError, match="above maximum"):
            ConfigurationSystem.validate_configuration(data)

    def test_validate_listening_sensitivity_invalid(self):
        """Test validation fails with invalid listening_sensitivity."""
        data = {
            "version": "1.0.0",
            "offline_mode": True,
            "language": "en",
            "voice_id": "en_US-hfc_female-medium",
            "speaking_rate": 1.0,
            "listening_sensitivity": 1.5,  # Above maximum 1.0
            "enable_camera": True,
            "enable_audio_output": True,
            "enable_learning": True,
            "max_context_exchanges": 10,
            "response_timeout_seconds": 2,
            "encryption_enabled": True,
            "auto_delete_after_days": None,
            "whisper_model_path": "models/whisper-base",
            "llama_model_path": "models/llama-2-7b-q4",
            "piper_model_path": "models/piper-voices",
            "mood_sensitivity": 0.8,
            "response_tone": "empathetic",
        }
        with pytest.raises(ValidationError, match="above maximum"):
            ConfigurationSystem.validate_configuration(data)

    def test_validate_invalid_response_tone(self):
        """Test validation fails with invalid response_tone."""
        data = {
            "version": "1.0.0",
            "offline_mode": True,
            "language": "en",
            "voice_id": "en_US-hfc_female-medium",
            "speaking_rate": 1.0,
            "listening_sensitivity": 0.8,
            "enable_camera": True,
            "enable_audio_output": True,
            "enable_learning": True,
            "max_context_exchanges": 10,
            "response_timeout_seconds": 2,
            "encryption_enabled": True,
            "auto_delete_after_days": None,
            "whisper_model_path": "models/whisper-base",
            "llama_model_path": "models/llama-2-7b-q4",
            "piper_model_path": "models/piper-voices",
            "mood_sensitivity": 0.8,
            "response_tone": "invalid_tone",
        }
        with pytest.raises(ValidationError, match="not in allowed values"):
            ConfigurationSystem.validate_configuration(data)

    def test_validate_unknown_field(self):
        """Test validation fails with unknown field."""
        data = {
            "version": "1.0.0",
            "offline_mode": True,
            "language": "en",
            "voice_id": "en_US-hfc_female-medium",
            "speaking_rate": 1.0,
            "listening_sensitivity": 0.8,
            "enable_camera": True,
            "enable_audio_output": True,
            "enable_learning": True,
            "max_context_exchanges": 10,
            "response_timeout_seconds": 2,
            "encryption_enabled": True,
            "auto_delete_after_days": None,
            "whisper_model_path": "models/whisper-base",
            "llama_model_path": "models/llama-2-7b-q4",
            "piper_model_path": "models/piper-voices",
            "mood_sensitivity": 0.8,
            "response_tone": "empathetic",
            "unknown_field": "value",
        }
        with pytest.raises(ValidationError, match="Unknown configuration field"):
            ConfigurationSystem.validate_configuration(data)


class TestConfigurationSystemParsing:
    """Tests for ConfigurationSystem file parsing."""

    def test_parse_yaml_file(self):
        """Test parsing a YAML configuration file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "config.yaml"
            config_data = {
                "version": "1.0.0",
                "offline_mode": True,
                "language": "en",
                "voice_id": "en_US-hfc_female-medium",
                "speaking_rate": 1.0,
                "listening_sensitivity": 0.8,
                "enable_camera": True,
                "enable_audio_output": True,
                "enable_learning": True,
                "max_context_exchanges": 10,
                "response_timeout_seconds": 2,
                "encryption_enabled": True,
                "auto_delete_after_days": None,
                "whisper_model_path": "models/whisper-base",
                "llama_model_path": "models/llama-2-7b-q4",
                "piper_model_path": "models/piper-voices",
                "mood_sensitivity": 0.8,
                "response_tone": "empathetic",
            }
            with open(config_path, "w") as f:
                yaml.dump(config_data, f)

            config = ConfigurationSystem.parse_config_file(str(config_path))
            assert config.version == "1.0.0"
            assert config.language == "en"
            assert config.speaking_rate == 1.0

    def test_parse_json_file(self):
        """Test parsing a JSON configuration file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "config.json"
            config_data = {
                "version": "1.0.0",
                "offline_mode": True,
                "language": "en",
                "voice_id": "en_US-hfc_female-medium",
                "speaking_rate": 1.0,
                "listening_sensitivity": 0.8,
                "enable_camera": True,
                "enable_audio_output": True,
                "enable_learning": True,
                "max_context_exchanges": 10,
                "response_timeout_seconds": 2,
                "encryption_enabled": True,
                "auto_delete_after_days": None,
                "whisper_model_path": "models/whisper-base",
                "llama_model_path": "models/llama-2-7b-q4",
                "piper_model_path": "models/piper-voices",
                "mood_sensitivity": 0.8,
                "response_tone": "empathetic",
            }
            with open(config_path, "w") as f:
                json.dump(config_data, f)

            config = ConfigurationSystem.parse_config_file(str(config_path))
            assert config.version == "1.0.0"
            assert config.language == "en"

    def test_parse_nonexistent_file(self):
        """Test parsing a nonexistent file raises FileNotFoundError."""
        with pytest.raises(FileNotFoundError):
            ConfigurationSystem.parse_config_file("/nonexistent/path/config.yaml")

    def test_parse_invalid_yaml(self):
        """Test parsing invalid YAML raises ValidationError."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "config.yaml"
            with open(config_path, "w") as f:
                f.write("invalid: yaml: content: [")

            with pytest.raises(ValidationError, match="YAML parsing error"):
                ConfigurationSystem.parse_config_file(str(config_path))

    def test_parse_invalid_json(self):
        """Test parsing invalid JSON raises ValidationError."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "config.json"
            with open(config_path, "w") as f:
                f.write("{invalid json}")

            with pytest.raises(ValidationError, match="JSON parsing error"):
                ConfigurationSystem.parse_config_file(str(config_path))

    def test_parse_unsupported_format(self):
        """Test parsing unsupported file format raises ValidationError."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "config.txt"
            with open(config_path, "w") as f:
                f.write("some content")

            with pytest.raises(ValidationError, match="Unsupported file format"):
                ConfigurationSystem.parse_config_file(str(config_path))

    def test_parse_empty_file(self):
        """Test parsing empty file raises ValidationError."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "config.yaml"
            with open(config_path, "w") as f:
                f.write("")

            with pytest.raises(ValidationError, match="Configuration file is empty"):
                ConfigurationSystem.parse_config_file(str(config_path))

    def test_parse_non_dict_content(self):
        """Test parsing non-dict content raises ValidationError."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "config.yaml"
            with open(config_path, "w") as f:
                f.write("- item1\n- item2")

            with pytest.raises(ValidationError, match="Configuration must be a dictionary"):
                ConfigurationSystem.parse_config_file(str(config_path))


class TestConfigurationSystemSaving:
    """Tests for ConfigurationSystem file saving."""

    def test_save_yaml_file(self):
        """Test saving configuration to YAML file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "config.yaml"
            config = Configuration(language="es", speaking_rate=1.5)

            ConfigurationSystem.save_configuration(config, str(config_path))

            assert config_path.exists()
            with open(config_path, "r") as f:
                data = yaml.safe_load(f)
            assert data["language"] == "es"
            assert data["speaking_rate"] == 1.5

    def test_save_json_file(self):
        """Test saving configuration to JSON file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "config.json"
            config = Configuration(language="fr", enable_camera=False)

            ConfigurationSystem.save_configuration(config, str(config_path))

            assert config_path.exists()
            with open(config_path, "r") as f:
                data = json.load(f)
            assert data["language"] == "fr"
            assert data["enable_camera"] is False

    def test_save_creates_parent_directories(self):
        """Test saving creates parent directories if they don't exist."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "nested" / "dir" / "config.yaml"
            config = Configuration()

            ConfigurationSystem.save_configuration(config, str(config_path))

            assert config_path.exists()

    def test_save_unsupported_format(self):
        """Test saving with unsupported format raises ValidationError."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "config.txt"
            config = Configuration()

            with pytest.raises(ValidationError, match="Unsupported file format"):
                ConfigurationSystem.save_configuration(config, str(config_path))


class TestConfigurationSystemRoundTrip:
    """Tests for configuration round-trip (save and load)."""

    def test_yaml_round_trip(self):
        """Test YAML round-trip: save then load produces equivalent config."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "config.yaml"
            original = Configuration(
                language="de",
                speaking_rate=1.2,
                listening_sensitivity=0.6,
                enable_camera=False,
                response_tone="technical",
            )

            ConfigurationSystem.save_configuration(original, str(config_path))
            loaded = ConfigurationSystem.load_configuration(str(config_path))

            assert loaded.language == original.language
            assert loaded.speaking_rate == original.speaking_rate
            assert loaded.listening_sensitivity == original.listening_sensitivity
            assert loaded.enable_camera == original.enable_camera
            assert loaded.response_tone == original.response_tone

    def test_json_round_trip(self):
        """Test JSON round-trip: save then load produces equivalent config."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "config.json"
            original = Configuration(
                language="it",
                speaking_rate=0.8,
                mood_sensitivity=0.5,
                enable_learning=False,
            )

            ConfigurationSystem.save_configuration(original, str(config_path))
            loaded = ConfigurationSystem.load_configuration(str(config_path))

            assert loaded.language == original.language
            assert loaded.speaking_rate == original.speaking_rate
            assert loaded.mood_sensitivity == original.mood_sensitivity
            assert loaded.enable_learning == original.enable_learning

    def test_full_round_trip_all_fields(self):
        """Test round-trip with all fields modified."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "config.yaml"
            original = Configuration(
                version="2.0.0",
                offline_mode=False,
                language="ja",
                voice_id="custom_voice",
                speaking_rate=0.7,
                listening_sensitivity=0.3,
                enable_camera=False,
                enable_audio_output=False,
                enable_learning=False,
                max_context_exchanges=20,
                response_timeout_seconds=5,
                encryption_enabled=False,
                auto_delete_after_days=30,
                whisper_model_path="custom/whisper",
                llama_model_path="custom/llama",
                piper_model_path="custom/piper",
                mood_sensitivity=0.2,
                response_tone="casual",
            )

            ConfigurationSystem.save_configuration(original, str(config_path))
            loaded = ConfigurationSystem.load_configuration(str(config_path))

            assert loaded.to_dict() == original.to_dict()


class TestConfigurationSystemDefaults:
    """Tests for default configuration."""

    def test_get_default_configuration(self):
        """Test getting default configuration."""
        config = ConfigurationSystem.get_default_configuration()
        assert config.version == "1.0.0"
        assert config.offline_mode is True
        assert config.language == "en"

    def test_reset_to_defaults(self):
        """Test resetting to defaults."""
        config = ConfigurationSystem.reset_to_defaults()
        assert config.version == "1.0.0"
        assert config.offline_mode is True
        assert config.language == "en"
