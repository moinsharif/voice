"""Configuration system for parsing, validating, and managing application settings."""

import json
import yaml
from pathlib import Path
from typing import Dict, Any, Optional, Tuple
from dataclasses import fields

from .configuration import Configuration


class ValidationError(Exception):
    """Raised when configuration validation fails."""

    pass


class ConfigurationSystem:
    """Manages configuration parsing, validation, and persistence."""

    # Schema defining valid configuration fields and their constraints
    SCHEMA = {
        "version": {"type": str, "required": True},
        "offline_mode": {"type": bool, "required": True},
        "language": {"type": str, "required": True},
        "voice_id": {"type": str, "required": True},
        "speaking_rate": {
            "type": float,
            "required": True,
            "min": 0.5,
            "max": 2.0,
        },
        "listening_sensitivity": {
            "type": float,
            "required": True,
            "min": 0.0,
            "max": 1.0,
        },
        "enable_camera": {"type": bool, "required": True},
        "enable_audio_output": {"type": bool, "required": True},
        "enable_learning": {"type": bool, "required": True},
        "max_context_exchanges": {
            "type": int,
            "required": True,
            "min": 1,
        },
        "response_timeout_seconds": {
            "type": int,
            "required": True,
            "min": 1,
        },
        "encryption_enabled": {"type": bool, "required": True},
        "auto_delete_after_days": {
            "type": (int, type(None)),
            "required": True,
        },
        "whisper_model_path": {"type": str, "required": True},
        "llama_model_path": {"type": str, "required": True},
        "piper_model_path": {"type": str, "required": True},
        "mood_sensitivity": {
            "type": float,
            "required": True,
            "min": 0.0,
            "max": 1.0,
        },
        "response_tone": {
            "type": str,
            "required": True,
            "allowed_values": ["empathetic", "technical", "casual", "formal"],
        },
    }

    @staticmethod
    def parse_config_file(filepath: str) -> Configuration:
        """
        Parse a configuration file (YAML or JSON) into a Configuration object.

        Args:
            filepath: Path to the configuration file

        Returns:
            Configuration object

        Raises:
            ValidationError: If file is invalid or configuration is invalid
            FileNotFoundError: If file does not exist
        """
        path = Path(filepath)

        if not path.exists():
            raise FileNotFoundError(f"Configuration file not found: {filepath}")

        try:
            with open(path, "r") as f:
                if path.suffix.lower() == ".yaml" or path.suffix.lower() == ".yml":
                    data = yaml.safe_load(f)
                elif path.suffix.lower() == ".json":
                    data = json.load(f)
                else:
                    raise ValidationError(
                        f"Unsupported file format: {path.suffix}. "
                        "Supported formats: .yaml, .yml, .json"
                    )
        except yaml.YAMLError as e:
            raise ValidationError(f"YAML parsing error: {e}")
        except json.JSONDecodeError as e:
            raise ValidationError(f"JSON parsing error: {e}")

        if data is None:
            raise ValidationError("Configuration file is empty")

        if not isinstance(data, dict):
            raise ValidationError("Configuration must be a dictionary/object")

        # Validate the parsed data
        ConfigurationSystem.validate_configuration(data)

        # Create Configuration object
        try:
            config = Configuration.from_dict(data)
        except TypeError as e:
            raise ValidationError(f"Failed to create Configuration object: {e}")

        return config

    @staticmethod
    def validate_configuration(config_data: Dict[str, Any]) -> None:
        """
        Validate configuration data against schema.

        Args:
            config_data: Configuration dictionary to validate

        Raises:
            ValidationError: If validation fails
        """
        if not isinstance(config_data, dict):
            raise ValidationError("Configuration must be a dictionary")

        # Check for required fields
        for field_name, field_spec in ConfigurationSystem.SCHEMA.items():
            if field_spec.get("required", False):
                if field_name not in config_data:
                    raise ValidationError(f"Missing required field: {field_name}")

        # Validate each field
        for field_name, field_value in config_data.items():
            if field_name not in ConfigurationSystem.SCHEMA:
                raise ValidationError(f"Unknown configuration field: {field_name}")

            field_spec = ConfigurationSystem.SCHEMA[field_name]

            # Type validation
            expected_type = field_spec.get("type")
            if not isinstance(field_value, expected_type):
                raise ValidationError(
                    f"Invalid type for field '{field_name}': "
                    f"expected {expected_type}, got {type(field_value).__name__}"
                )

            # Range validation
            if "min" in field_spec and field_value < field_spec["min"]:
                raise ValidationError(
                    f"Field '{field_name}' value {field_value} is below minimum {field_spec['min']}"
                )

            if "max" in field_spec and field_value > field_spec["max"]:
                raise ValidationError(
                    f"Field '{field_name}' value {field_value} is above maximum {field_spec['max']}"
                )

            # Allowed values validation
            if "allowed_values" in field_spec:
                if field_value not in field_spec["allowed_values"]:
                    raise ValidationError(
                        f"Field '{field_name}' value '{field_value}' not in allowed values: "
                        f"{field_spec['allowed_values']}"
                    )

    @staticmethod
    def save_configuration(config: Configuration, filepath: str) -> None:
        """
        Save configuration to a file (YAML or JSON).

        Args:
            config: Configuration object to save
            filepath: Path where to save the configuration

        Raises:
            ValidationError: If file format is not supported
        """
        path = Path(filepath)
        config_dict = config.to_dict()

        try:
            path.parent.mkdir(parents=True, exist_ok=True)

            if path.suffix.lower() == ".yaml" or path.suffix.lower() == ".yml":
                with open(path, "w") as f:
                    yaml.dump(config_dict, f, default_flow_style=False, sort_keys=False)
            elif path.suffix.lower() == ".json":
                with open(path, "w") as f:
                    json.dump(config_dict, f, indent=2)
            else:
                raise ValidationError(
                    f"Unsupported file format: {path.suffix}. "
                    "Supported formats: .yaml, .yml, .json"
                )
        except IOError as e:
            raise ValidationError(f"Failed to save configuration: {e}")

    @staticmethod
    def load_configuration(filepath: str) -> Configuration:
        """
        Load configuration from file.

        Args:
            filepath: Path to the configuration file

        Returns:
            Configuration object

        Raises:
            ValidationError: If configuration is invalid
            FileNotFoundError: If file does not exist
        """
        return ConfigurationSystem.parse_config_file(filepath)

    @staticmethod
    def get_default_configuration() -> Configuration:
        """
        Get default configuration.

        Returns:
            Configuration object with default values
        """
        return Configuration()

    @staticmethod
    def reset_to_defaults() -> Configuration:
        """
        Reset configuration to defaults.

        Returns:
            Configuration object with default values
        """
        return ConfigurationSystem.get_default_configuration()
