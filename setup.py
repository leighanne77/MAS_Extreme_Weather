#!/usr/bin/env python3
"""
Setup script for Pythia Multi-Agent Extreme Weather Risk Analysis System

This package provides a comprehensive multi-agent system for extreme weather risk analysis
with A2A protocol support, web interface, and advanced data management capabilities.
"""

from setuptools import setup, find_packages
import os

# Read the README file
def read_readme():
    with open("README.md", "r", encoding="utf-8") as fh:
        return fh.read()

# Read requirements
def read_requirements():
    with open("requirements.txt", "r", encoding="utf-8") as fh:
        return [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="pythia-mas-climate",
    version="1.0.0",
    author="Pythia Development Team",
    author_email="team@pythia-climate.com",
    description="Multi-Agent System for Extreme Weather Risk Analysis",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/leighanne77/MAS_Extreme_Weather",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Financial and Insurance Industry",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Scientific/Engineering :: Information Analysis",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.10",
    install_requires=read_requirements(),
    extras_require={
        "web": [
            "fastapi>=0.104.0",
            "uvicorn[standard]>=0.24.0",
            "jinja2>=3.1.0",
            "python-multipart>=0.0.6",
            "aiofiles>=23.2.0",
            "starlette>=0.27.0",
            "pandas>=2.0.0",
            "numpy>=1.24.0",
            "plotly>=5.17.0",
            "matplotlib>=3.7.0",
            "seaborn>=0.12.0",
            "reportlab>=4.0.0",
            "openpyxl>=3.1.0",
            "python-docx>=1.1.0",
            "itsdangerous>=2.1.0",
            "python-jose[cryptography]>=3.3.0",
            "asyncio-mqtt>=0.16.0",
            "aiohttp>=3.9.0",
            "structlog>=23.2.0",
        ],
        "dev": [
            "pytest>=7.4.0",
            "pytest-asyncio>=0.21.0",
            "httpx>=0.25.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
            "pre-commit>=3.0.0",
        ],
        "performance": [
            "psutil>=5.9.0",
            "memory-profiler>=0.60.0",
            "line-profiler>=4.0.0",
        ],
        "monitoring": [
            "prometheus-client>=0.17.0",
            "structlog>=23.2.0",
            "sentry-sdk>=1.30.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "pythia-cli=multi_agent_system.cli:main",
            "pythia-web=src.pythia_web.interface:main",
        ],
    },
    include_package_data=True,
    package_data={
        "multi_agent_system": [
            "data/*.json",
            "config/*.yaml",
            "config/*.yml",
        ],
        "agentic_data_management": [
            "config/*.yaml",
            "config/*.yml",
        ],
    },
    keywords=[
        "climate",
        "weather",
        "risk",
        "analysis",
        "multi-agent",
        "ai",
        "machine-learning",
        "financial",
        "agriculture",
        "insurance",
        "sustainability",
        "extreme-weather",
        "a2a",
        "adk",
        "google-cloud",
    ],
    project_urls={
        "Bug Reports": "https://github.com/leighanne77/MAS_Extreme_Weather/issues",
        "Source": "https://github.com/leighanne77/MAS_Extreme_Weather",
        "Documentation": "https://github.com/leighanne77/MAS_Extreme_Weather/tree/main/docs",
    },
    zip_safe=False,
) 