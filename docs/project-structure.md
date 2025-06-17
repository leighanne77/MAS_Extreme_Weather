# Project Structure

## Overview
This project implements an agentic data management system for climate risk analysis, leveraging advanced AI capabilities and modular agent design.

## Directory Structure
```
.
├── src/
│   └── agentic_data_management/
│       ├── __init__.py
│       ├── agents/
│       │   ├── __init__.py (if present)
│       │   ├── base_agent.py
│       │   ├── data_agent.py
│       │   ├── quality_agent.py
│       │   ├── security_agent.py
│       │   └── lifecycle_agent.py
│       ├── coordinator.py
│       ├── data_manager.py
│       ├── quality.py
│       ├── validators.py
│       ├── transformers.py
│       ├── schemas.py
│       ├── governance.py
│       ├── config.py
│       ├── workflows.py
│       └── integrations/
│           └── google_cloud.py
├── tests/
│   ├── test_agent_system.py
│   └── conftest.py
├── docs/
│   ├── project-structure.md
│   ├── terms_used.md
│   └── workflow_example.md
├── .env.example
├── pyproject.toml
└── README.md
```

## Core Components

### Agents (src/agentic_data_management/agents/)
- `base_agent.py`: Base class for all agents, providing shared logic and interface.
- `data_agent.py`: Handles core data operations (import, export, transformation, synchronization).
- `quality_agent.py`: Manages data quality, validation, and quality metrics.
- `security_agent.py`: Handles authentication, authorization, and security policies.
- `lifecycle_agent.py`: Manages data retention, versioning, backup, and cleanup.

### Data Management (src/agentic_data_management/)
- `data_manager.py`: Orchestrates data processing, validation, transformation, and quality assessment.
- `validators.py`: Data validation logic and rule management.
- `transformers.py`: Data transformation pipelines and logic.
- `schemas.py`: Schema management and versioning.
- `quality.py`: Data quality metrics and reporting.
- `governance.py`: Data governance and compliance policies.
- `config.py`: Configuration management.
- `workflows.py`: Workflow definitions and orchestration.
- `integrations/google_cloud.py`: Google Cloud integration utilities.

### Coordination
- `coordinator.py`: Orchestrates agent workflows and system operations.

## Testing
- All tests are in the `tests/` directory.
- `test_agent_system.py`: Main test suite for agent and workflow functionality.
- `conftest.py`: Pytest fixtures and configuration.

## Documentation
- All documentation is in the `docs/` directory, including:
  - `project-structure.md` (this file)
  - `terms_used.md` (glossary)
  - `workflow_example.md` (usage examples)

## Key Dependencies

### Core
- `numpy`, `pandas`, `matplotlib`, `seaborn`, `xarray`, `netCDF4`, `scipy`, `scikit-learn`, `cartopy`, `cfgrib`, `eccodes`, `pyproj`

### Google Cloud & AI
- `google-adk`, `a2a-sdk`, `google-cloud-aiplatform`, `google-cloud-core`, `google-api-core`, `google-auth`, `google-cloud-storage`, `google-cloud-logging`, `google-cloud-trace`, `google-cloud-bigquery`, `google-cloud-resource-manager`, `google-cloud-secret-manager`, `google-cloud-speech`, `google-genai`

### Observability
- `opentelemetry-api`, `opentelemetry-sdk`, `opentelemetry-exporter-gcp-trace`, `opentelemetry-instrumentation-aiohttp`, `opentelemetry-instrumentation-grpc`, `opentelemetry-instrumentation-sqlalchemy`, `opentelemetry-semantic-conventions`

### Utility
- `graphviz`, `mcp`, `pydantic`, `PyYAML`, `sqlalchemy`, `tzlocal`, `aiofiles`, `aiohttp`

### Testing
- `pytest`, `pytest-asyncio`, `pytest-cov`, `pytest-mock`, `pytest-timeout`, `pytest-xdist`, `pytest-benchmark`, `pytest-env`, `python-dotenv`

## Configuration
- Environment variables are managed via `.env.example` and loaded at runtime.
- Key settings: API keys, service endpoints, cache, logging, and performance parameters.

## Summary
This structure supports a modular, maintainable, and extensible agentic data management system, with clear separation of concerns and robust testing/documentation practices. 