"""
Offline Operation Verification Module

Verifies that all required models and dependencies are available for offline operation.
Provides clear error messages with installation instructions for missing components.
"""

import os
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass


@dataclass
class VerificationResult:
    """Result of a verification check."""
    is_available: bool
    component_name: str
    error_message: Optional[str] = None
    installation_instructions: Optional[str] = None


class OfflineOperationVerifier:
    """Verifies offline operation requirements and model availability."""

    # Model paths and their verification methods
    MODEL_CHECKS = {
        "whisper": {
            "description": "Whisper Speech Recognition Model",
            "paths": ["models/whisper-base", "models/whisper-tiny", "models/whisper-small"],
            "installation": """
To install Whisper model:
1. Install whisper: pip install openai-whisper
2. Download model: python -c "import whisper; whisper.load_model('base')"
   (Models are cached in ~/.cache/whisper/)
3. Or manually place model files in: models/whisper-base/
            """.strip()
        },
        "llama2": {
            "description": "Llama 2 Language Model",
            "paths": ["models/llama-2-7b", "models/llama-2-7b-chat"],
            "installation": """
To install Llama 2 model:
1. Install llama-cpp-python: pip install llama-cpp-python
2. Download quantized model from: https://huggingface.co/TheBloke/Llama-2-7B-Chat-GGUF
3. Place model file in: models/llama-2-7b/
   Example: models/llama-2-7b/llama-2-7b-chat.Q4_K_M.gguf
            """.strip()
        },
        "piper": {
            "description": "Piper Text-to-Speech Model",
            "paths": ["models/piper", "models/piper/en_US-lessac-medium.onnx"],
            "installation": """
To install Piper TTS model:
1. Install piper-tts: pip install piper-tts
2. Download voice model: piper --download-dir models/piper en_US-lessac-medium
3. Or manually download from: https://github.com/rhasspy/piper/releases
            """.strip()
        },
        "mediapipe": {
            "description": "MediaPipe Face Detection Models",
            "paths": ["models/mediapipe"],
            "installation": """
To install MediaPipe models:
1. Install mediapipe: pip install mediapipe
2. Models are automatically downloaded on first use
3. Or manually download from: https://github.com/google/mediapipe/tree/master/mediapipe/modules/face_detection
            """.strip()
        },
        "sqlite": {
            "description": "SQLite Database",
            "paths": None,  # SQLite is built-in to Python
            "installation": "SQLite is built-in to Python. No installation needed."
        }
    }

    def __init__(self, config: Optional[Dict] = None):
        """Initialize the verifier.
        
        Args:
            config: Configuration dictionary with model paths
        """
        self.config = config or {}
        self.verification_results: List[VerificationResult] = []

    def verify_offline_operation(self) -> Tuple[bool, List[VerificationResult]]:
        """Verify all requirements for offline operation.
        
        Returns:
            Tuple of (all_checks_passed, list_of_results)
        """
        self.verification_results = []
        
        # Check each required model
        self._check_whisper_model()
        self._check_llama2_model()
        self._check_piper_model()
        self._check_mediapipe_models()
        self._check_sqlite_database()
        self._check_no_external_calls()
        
        all_passed = all(result.is_available for result in self.verification_results)
        return all_passed, self.verification_results

    def _check_whisper_model(self) -> None:
        """Check Whisper model availability."""
        result = self._check_model_availability(
            "whisper",
            self.MODEL_CHECKS["whisper"]
        )
        self.verification_results.append(result)

    def _check_llama2_model(self) -> None:
        """Check Llama 2 model availability."""
        result = self._check_model_availability(
            "llama2",
            self.MODEL_CHECKS["llama2"]
        )
        self.verification_results.append(result)

    def _check_piper_model(self) -> None:
        """Check Piper TTS model availability."""
        result = self._check_model_availability(
            "piper",
            self.MODEL_CHECKS["piper"]
        )
        self.verification_results.append(result)

    def _check_mediapipe_models(self) -> None:
        """Check MediaPipe models availability."""
        result = self._check_model_availability(
            "mediapipe",
            self.MODEL_CHECKS["mediapipe"]
        )
        self.verification_results.append(result)

    def _check_sqlite_database(self) -> None:
        """Check SQLite availability (built-in to Python)."""
        try:
            import sqlite3
            result = VerificationResult(
                is_available=True,
                component_name="SQLite Database",
                error_message=None,
                installation_instructions=None
            )
        except ImportError:
            result = VerificationResult(
                is_available=False,
                component_name="SQLite Database",
                error_message="SQLite is not available in this Python installation",
                installation_instructions="SQLite is built-in to Python. Please reinstall Python."
            )
        self.verification_results.append(result)

    def _check_no_external_calls(self) -> None:
        """Verify that no external API calls are configured.
        
        This is a placeholder for future network monitoring.
        Currently just verifies offline_mode is enabled in config.
        """
        offline_mode = self.config.get("offline_mode", True)
        
        if offline_mode:
            result = VerificationResult(
                is_available=True,
                component_name="Offline Mode Configuration",
                error_message=None,
                installation_instructions=None
            )
        else:
            result = VerificationResult(
                is_available=False,
                component_name="Offline Mode Configuration",
                error_message="Offline mode is not enabled in configuration",
                installation_instructions="Set 'offline_mode: true' in your configuration file"
            )
        self.verification_results.append(result)

    def _check_model_availability(
        self,
        model_key: str,
        model_info: Dict
    ) -> VerificationResult:
        """Check if a model is available.
        
        Args:
            model_key: Key for the model in MODEL_CHECKS
            model_info: Model information dictionary
            
        Returns:
            VerificationResult with availability status
        """
        description = model_info["description"]
        paths = model_info.get("paths")
        installation = model_info.get("installation", "")
        
        # Special case for SQLite (no paths to check)
        if paths is None:
            return VerificationResult(
                is_available=True,
                component_name=description,
                error_message=None,
                installation_instructions=None
            )
        
        # Check if any of the model paths exist
        for path in paths:
            if self._path_exists(path):
                return VerificationResult(
                    is_available=True,
                    component_name=description,
                    error_message=None,
                    installation_instructions=None
                )
        
        # Model not found
        error_message = f"{description} not found in any of: {', '.join(paths)}"
        return VerificationResult(
            is_available=False,
            component_name=description,
            error_message=error_message,
            installation_instructions=installation
        )

    def _path_exists(self, path: str) -> bool:
        """Check if a path exists (file or directory).
        
        Args:
            path: Path to check
            
        Returns:
            True if path exists, False otherwise
        """
        return os.path.exists(path)

    def check_model_availability(self) -> Dict[str, bool]:
        """Check availability of each model.
        
        Returns:
            Dictionary mapping model names to availability status
        """
        availability = {}
        for result in self.verification_results:
            availability[result.component_name] = result.is_available
        return availability

    def get_error_messages(self) -> List[str]:
        """Get all error messages for missing components.
        
        Returns:
            List of error messages
        """
        errors = []
        for result in self.verification_results:
            if not result.is_available and result.error_message:
                errors.append(result.error_message)
        return errors

    def get_installation_instructions(self) -> str:
        """Get installation instructions for all missing components.
        
        Returns:
            Formatted string with installation instructions
        """
        instructions = []
        for result in self.verification_results:
            if not result.is_available and result.installation_instructions:
                instructions.append(f"\n{result.component_name}:")
                instructions.append(result.installation_instructions)
        
        if not instructions:
            return ""
        
        return "\n".join(instructions)

    def generate_verification_report(self) -> str:
        """Generate a detailed verification report.
        
        Returns:
            Formatted verification report
        """
        report_lines = [
            "=" * 70,
            "OFFLINE OPERATION VERIFICATION REPORT",
            "=" * 70,
            ""
        ]
        
        # Summary
        passed = sum(1 for r in self.verification_results if r.is_available)
        total = len(self.verification_results)
        report_lines.append(f"Status: {passed}/{total} checks passed")
        report_lines.append("")
        
        # Detailed results
        report_lines.append("DETAILED RESULTS:")
        report_lines.append("-" * 70)
        
        for result in self.verification_results:
            status = "✓ PASS" if result.is_available else "✗ FAIL"
            report_lines.append(f"{status}: {result.component_name}")
            
            if not result.is_available:
                if result.error_message:
                    report_lines.append(f"  Error: {result.error_message}")
                if result.installation_instructions:
                    report_lines.append(f"  Instructions: {result.installation_instructions}")
        
        report_lines.append("")
        report_lines.append("=" * 70)
        
        return "\n".join(report_lines)
