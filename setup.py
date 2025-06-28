#!/usr/bin/env python3
"""
Setup script for Tool Multi-Agent Extreme Weather Risk Analysis System

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
    name="tool-mas-climate",
    version="1.0.0",
    author="Tool Development Team",
    author_email="team@tool-climate.com",
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
        "Programming Language :: Python :: 3.12",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Scientific/Engineering :: Information Analysis",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.12",
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
            "dash>=2.14.0",
            "dash-bootstrap-components>=1.5.0",
            "networkx>=3.0.0",
            "passlib[bcrypt]>=1.7.4",
            "cryptography>=41.0.0",
            "pyjwt>=2.8.0",
            "bcrypt>=4.1.2",
        ],
        "dev": [
            "pytest>=7.4.0",
            "pytest-asyncio>=0.21.0",
            "pytest-cov>=4.0.0",
            "pytest-mock>=3.10.0",
            "pytest-xdist>=2.5.0",
            "pytest-benchmark>=5.1.0",
            "coverage>=6.3.0",
            "httpx>=0.25.0",
            "black>=23.0.0",
            "isort>=5.12.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
            "pylint>=3.1.0",
            "ruff>=0.1.0",
            "pre-commit>=3.0.0",
        ],
        "performance": [
            "psutil>=5.9.0",
            "memory-profiler>=0.60.0",
            "line-profiler>=4.0.0",
            "py-spy>=0.3.14",
            "locust>=2.17.0",
        ],
        "monitoring": [
            "prometheus-client>=0.17.0",
            "structlog>=23.2.0",
            "sentry-sdk>=1.30.0",
            "python-json-logger>=2.0.0",
        ],
        "data": [
            "xarray>=2024.1.0",
            "netCDF4>=1.6.5",
            "cartopy>=0.22.0",
            "cfgrib>=0.9.11.0",
            "eccodes>=1.6.1",
            "pyproj>=3.6.1",
            "great-expectations>=0.18.0",
            "polars>=0.20.0",
            "pyarrow>=14.0.0",
            "fastparquet>=2023.0.0",
        ],
        "google-cloud": [
            "google-adk>=0.1.0",
            "google-cloud-aiplatform[agent-engines]>=1.95.1",
            "google-cloud-core>=2.4.0",
            "google-api-core>=2.17.0",
            "google-auth>=2.27.0",
            "google-cloud-storage>=2.14.0",
            "google-generativeai>=0.3.0",
            "vertexai>=0.0.1",
            "google-cloud-bigquery>=3.0.0",
            "google-cloud-firestore>=2.0.0",
            "google-cloud-pubsub>=2.0.0",
        ],
        "database": [
            "sqlalchemy>=2.0.0",
            "alembic>=1.12.0",
            "psycopg2-binary>=2.9.0",
            "redis>=5.0.1",
        ],
    },
    entry_points={
        "console_scripts": [
            "tool-cli=multi_agent_system.cli:main",
            "tool-web=tool_web.interface:app",
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
        "tool_web": [
            "static/css/*.css",
            "static/js/*.js",
            "templates/*.html",
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
        "fastapi",
        "web-dashboard",
        "chartjs",
        "vanilla-javascript",
        "nature-based-solutions",
        "environmental-risk",
        "investment-analysis",
        "loan-assessment",
        "property-risk",
        "climate-resilience",
        "biodiversity",
        "ecosystem-services",
    ],
    project_urls={
        "Bug Reports": "https://github.com/leighanne77/MAS_Extreme_Weather/issues",
        "Source": "https://github.com/leighanne77/MAS_Extreme_Weather",
        "Documentation": "https://github.com/leighanne77/MAS_Extreme_Weather/tree/main/docs",
    },
    zip_safe=False,
) 