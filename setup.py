"""
Setup configuration for Vask Voice-Based AI Companion
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read the README file
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding="utf-8") if (this_directory / "README.md").exists() else ""

setup(
    name="vask",
    version="1.0.0",
    description="Voice-Based AI Companion - A locally-run conversational AI system with mood analysis",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Vask Development Team",
    url="https://github.com/vask/vask",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.8",
    install_requires=[
        "openai-whisper==20231117",
        "llama-cpp-python==0.2.36",
        "opencv-python==4.8.1.78",
        "mediapipe==0.10.8",
        "piper-tts==1.2.0",
        "cryptography==41.0.7",
        "pyyaml==6.0.1",
    ],
    extras_require={
        "dev": [
            "pytest==7.4.3",
            "pytest-cov==4.1.0",
            "black==23.12.0",
            "flake8==6.1.0",
            "mypy==1.7.1",
        ],
    },
    entry_points={
        "console_scripts": [
            "vask=main:main",
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: End Users/Desktop",
        "Topic :: Multimedia :: Sound/Audio :: Speech",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
)
