"""
Setup Script for Navigation Assistant
Allows installation as a package: pip install -e .
"""
from setuptools import setup, find_packages
from pathlib import Path

# Read README for long description
readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text(encoding="utf-8") if readme_file.exists() else ""

setup(
    name="navigation-assistant",
    version="1.0.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="Real-time navigation assistant for the visually impaired using YOLO",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ibrandos/navigation-assistant",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "Intended Audience :: Healthcare Industry",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Scientific/Engineering :: Image Recognition",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=[
        "opencv-python>=4.8.0",
        "PyQt6>=6.5.0",
        "torch>=2.0.0",
        "torchvision>=0.15.0",
        "ultralytics>=8.0.0",
        "pyttsx3>=2.90",
        "numpy>=1.24.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "nav-assist=main:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["*.yaml", "*.json"],
    },
    project_urls={
        "Bug Reports": "https://github.com/ibrandos/navigation-assistant/issues",
        "Source": "https://github.com/ibrandos/navigation-assistant",
        "Documentation": "https://github.com/ibrandos/navigation-assistant/wiki",
    },
)