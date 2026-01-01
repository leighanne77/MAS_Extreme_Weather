# Pythia Multi-Agent System: Definitions

**Date Created:** December 20, 2025

This document defines the core Python objects, environment variables, classes, functions, agents, data sources, and governance rules for the Pythia multi-agent system for extreme weather risk analysis.

---

## 1. Python Objects & Names
- **AgentTeam**: Coordinates multiple agents for collaborative tasks.
- **SessionManager**: Manages user and agent sessions.
- **PerformanceBenchmark, LoadTester, CacheManager, PerformanceOptimizer, PerformanceMonitor**: Performance and monitoring utilities.
- **SimpleCache**: Shared in-memory cache utility for data providers.
- **BenchmarkResult, LoadTestResult, OptimizationResult, PerformanceMetric, SystemMetrics, ApplicationMetrics**: Data classes for metrics and results.
- **A2AMessage, A2AEnums, A2AMultipart, A2ARouter, Artifact, ArtifactManager, A2AParts, ContentHandler, TaskManager**: Agent-to-agent protocol, message, artifact, and routing objects.
- **WebAdapter, APIAdapter, IntegrationManager**: Web and API integration/adapters for tool_web interface.
- **NaturalLanguageProcessor**: Parses and interprets user queries (NLP for web interface).
- **BaseAgent**: Abstract base class for all agents.
- **Custom Enums**: For agent roles, message types, error codes, artifact events, etc.
- **DataLoader**: Loads static/reference data; specialized loaders for each data type.
- **Security Context Objects**: API key validation, credential management, and security context.
- **Test Utilities**: Fixtures, mocks, and test harnesses in `tests/`.
- **ERDDAPAdapter, OpenETAdapter, EPAAdapter**: Integrations for specific external APIs.
- **WebSession, SessionContext**: Manage user sessions in the web interface.
- **QueryParser, QueryContext**: Parse and structure user queries.
- **ArtifactEventEnum, ArtifactTypeEnum**: Enums for artifact event/type handling.
- **AgentRoleEnum, MessageTypeEnum, ErrorCodeEnum, RateLimitEnum**: Enum collections for agent roles, message types, error codes, rate limiting, etc.
- **CredentialManager, APIKeyValidator**: Security and credential management utilities.
- **NatureBasedSolutionsLoader, InfrastructureNeedsLoader**: Specialized data loaders for static/reference data.
- **MockAgent, TestSession, TestDataLoader**: Test and mock utilities for validation.
- **PrometheusExporter, PerformanceAlertHandler**: Metrics export and alerting.
- **AgentCard**: Metadata and capabilities for agents.
- **RouterLogic, MultipartLogic**: Multipart message and routing logic.

## 2. Environment Variables
- **BLS_API_KEY**: Bureau of Labor Statistics API key (required for BLS data access).
- **NOAA_API_KEY**: NOAA weather and climate data API key.
- **USGS_API_KEY**: USGS Water Services API key (if required for advanced endpoints).
- **NASS_API_KEY**: USDA NASS Crop Reports API key.
- **ERS_API_KEY**: USDA ERS API key (if required).
- **OPENET_API_KEY**: OpenET evapotranspiration data API key.
- **EPA_API_KEY**: EPA STORET/WQX API key.
- **CENSUS_API_KEY**: US Census data API key.
- **OPENFEMA_API_KEY**: OpenFEMA disaster data API key.
- **ERDDAP_API_KEY**: ERDDAP server API key (if required).
- **PYTHIA_ENV**: Name of the Python environment (for runtime context).
- **PYTHIA_CONFIG_PATH**: Path to custom configuration file (if used).
- **PYTHIA_LOG_LEVEL**: Logging level for system diagnostics.
- **PYTHIA_SESSION_DIR**: Directory for session storage.
- **PYTHIA_CACHE_DIR**: Directory for cache storage.
- **PYTHIA_WEB_PORT**: Port for web interface (if running as a service).
- **PYTHIA_SECRET_KEY**: Secret key for web/session security (if web interface is enabled).
- **Other API Keys**: See `credentials_template.txt` for all required keys (e.g., additional data providers, future integrations).

## 3. Classes & Functions
- **get_bls_data(series_ids, start_year, end_year)**: Fetches BLS time series data.
- **usgs_water_query(service, params, use_cache)**: Queries USGS Water Services API.
- **ers_query(endpoint, params, use_cache)**: Queries USDA ERS API.
- **nass_query(params, use_cache)**: Queries USDA NASS Crop Reports API.
- **get_site_instantaneous, get_farm_income, get_crop_yield**: Example safe query functions for each data provider.
- **CacheManager/SimpleCache.get/set**: Shared cache logic for repeated queries.
- **A2AMessage, A2AMultipart, A2ARouter, Artifact, ArtifactManager, A2AParts, ContentHandler, TaskManager**: Core agent-to-agent protocol and artifact management classes.
- **WebAdapter, APIAdapter, IntegrationManager**: Web/API integration and adapter classes.
- **NaturalLanguageProcessor, QueryParser, QueryContext**: NLP and query parsing classes.
- **BaseAgent, AgentCard**: Abstract agent base and agent metadata/capabilities classes.
- **CredentialManager, APIKeyValidator**: Security and credential management classes.
- **MockAgent, TestSession, TestDataLoader**: Test/mocking utility classes.
- **PrometheusExporter, PerformanceAlertHandler**: Metrics export and alerting classes.
- **RouterLogic, MultipartLogic**: Multipart message and routing logic classes.
- **NatureBasedSolutionsLoader, InfrastructureNeedsLoader**: Specialized data loader classes.
- **analyze_extreme_weather_risk(location, time_period, risk_types)**: Main risk analysis function.
- **get_recommendations(location, risk_type)**: Agent recommendation function.
- **validate_data_quality(data, quality_metrics)**: Data validation function.
- **export_analysis_for_deal_documentation(session_id, format)**: Export analysis results for documentation.
- **cross_reference_with_public_data(user_data, public_sources)**: Cross-reference user and public data.
- **list_available_capabilities()**: List agent/system capabilities.
- **get_active_agents(session_id)**: Get currently active agents for a session.
- **analyze_historical_data(location, start_date, end_date)**: Historical data analysis function.
- **calculate_ecosystem_service_value(location, service_types)**: Ecosystem service valuation function.
- **analyze_exit_value_impact(risk_assessment, exit_timeline)**: Exit value impact analysis function.
- **init_app(), main()**: Main entry points for initializing and running the application or web server.
- **load_config(path)**: Loads configuration from a file or environment variables.
- **authenticate_user(credentials)**: Handles user authentication (if applicable).
- **log_event(event_type, details)**: Centralized event logging function.
- **shutdown(), cleanup()**: Graceful shutdown or cleanup logic for the system.
- **register_agent(agent_class)**: Registers a new agent type with the system.
- **get_data_source(name)**: Retrieves a data source by name or type.
- **run_benchmark(), run_load_test()**: Triggers performance and load tests.

## 4. Agents
- **RiskAgent**: Analyzes extreme weather risks.
- **RecommendationAgent**: Suggests adaptation strategies.
- **DueDiligenceAgent**: Assesses project feasibility and compliance.
- **HistoricalAgent**: Provides historical weather/event analysis.
- **ProgressDisplayAgent**: Tracks and displays analysis progress.
- **ValidationAgent**: Validates data quality and results.
- **GreetingAgent, FarewellAgent, NewsAgent, QueryRefinementAgent**: User interaction and support roles.

## 5. Data Sources
- **BLS (Bureau of Labor Statistics)**: Economic and labor data (API, requires key).
- **USGS Water Services**: Hydrological data (API, public).
- **USDA ERS**: Farm income and economics (API, public).
- **USDA NASS**: Crop yield and production (API, key required).
- **EPA STORET/WQX, OpenFEMA, Census, OpenET, ERDDAP, etc.**: Additional APIs and reference datasets (see `src/multi_agent_system/data/`).
- **Reference Data**: Static JSON files for nature-based solutions, infrastructure needs, etc.

## 6. Major Governance Rules
- **Decision Support Only**: Pythia is a decision support tool, not a decision-making or automated system.
- **No Real-Time Promises**: Data refresh intervals are 1-6 hours; no real-time data feeds.
- **Terminology**: Use "extreme weather-related risk"; do not use "climate" or carbon finance terms.
- **Data Privacy**: No storage or processing of user proprietary or financial data without explicit permission.
- **Integration Limits**: Export-based integration only; no direct system connections.
- **User Personas**: Focus on Private Equity Investor and Government Funders; no insurance personas.
- **Documentation**: All changes must be logged and comply with system/cursor rules.

## 7. Other Important Items
- **.pylintrc**: Enforces style, disables, and ignores for async and third-party modules.
- **cache_utils.py**: Centralizes cache logic to reduce code duplication.
- **credentials_template.txt**: Lists all required API keys and credentials.
- **README.md/README_SUGGESTIONS.md**: Document system constraints, terminology, and usage.
- **Makefile**: Lint, format, test, and check API keys for compliance.
- **A2A Protocol**: Defines agent-to-agent message structure, enums, multipart logic, and router.
- **Performance Modules**: Provide benchmarking, load testing, caching, monitoring, and optimization.

## General Enums for Pythia System

All enums for data loaders, agents, communication, and observability are now defined in `src/enums.py` for clarity and reuse across all modules.

### Naming Conventions
- Enums are prefixed by domain (e.g., DataLoadStatus, AgentRole, ArtifactType) for clarity.
- Each enum and value is documented with a descriptive docstring.

### Key Enums
- DataLoadStatus: Loader/agent operation status
- DataProvenance: Origin of data
- DataDomain: Domain/type of data
- DataErrorType: Type of error
- DataUpdateFrequency: Data refresh interval
- DataFormat: Data format
- DataAccessLevel: Data permissions
- ArtifactType: Output type
- ErrorSeverity: Error severity
- AgentRole: Agent role
- InteractionType: Agent interaction pattern
- DecisionPattern: Agent decision pattern
- MessageType: A2A message type
- PriorityLevel: Message/task priority

See `src/enums.py` for full definitions and usage examples.

## Data Loader and Agent Enums

The following enums are used throughout the Pythia data loader and agent system to standardize return values, error handling, provenance, and metadata:

- **DataLoadStatus**: Loader result status (`SUCCESS`, `ERROR`)
- **ProvenanceType**: Source of data (`API`, `MCP`, `STATIC`, `MANUAL`)
- **DataSourceType**: Domain/type of data (`AGRICULTURE`, `WATER`, `ECONOMIC`, `ENVIRONMENTAL`, `OTHER`)
- **UpdateFrequency**: How often data is updated (`REALTIME`, `HOURLY`, `DAILY`, `WEEKLY`, `MONTHLY`, `ANNUAL`, `MANUAL`)
- **DataFormat**: Format of returned data (`JSON`, `CSV`, `XML`, `PARQUET`, `OTHER`)
- **ErrorType**: Nature of error (`NETWORK`, `PARSING`, `VALIDATION`, `PERMISSION`, `UNKNOWN`)
- **AccessLevel**: Data access permissions (`PUBLIC`, `RESTRICTED`, `PRIVATE`, `INTERNAL`)
- **ArtifactType**: Type of produced artifact (`DATASET`, `MODEL`, `REPORT`, `VISUALIZATION`, `LOG`)
- **ErrorSeverity**: Severity of error (`LOW`, `MEDIUM`, `HIGH`, `CRITICAL`)
- **InteractionType**: Agent interaction pattern (`SEQUENTIAL`, `PARALLEL`, `BRANCHING`, `RECURSIVE`)
- **DecisionPattern**: Agent decision-making pattern (`LINEAR`, `BRANCHING`, `BACKTRACKING`, `OPTIMIZATION`)
- **MessageType**: Type of A2A message (see a2a/enums.py)
- **Priority**: Message/task priority (see a2a/enums.py)

All loader and agent return values should use these enums for their respective fields. See `src/multi_agent_system/data/data_enums.py` for definitions and usage examples.

---

## Implementation: Multi-Step Agent Chaining and Data Aggregation

The Pythia system implements a comprehensive multi-step agent chaining and data aggregation architecture as documented in `docs/2-DATA/GEE A2A ADK.md`.

### Key Components

#### 1. Standardized Enums (`src/enums.py`)
All data loaders and agents use standardized enums for:
- `DataLoadStatus`: SUCCESS, ERROR
- `DataProvenance`: API, MCP, STATIC, MANUAL
- `DataDomain`: AGRICULTURE, WATER, ECONOMIC, ENVIRONMENTAL, OTHER
- `DataErrorType`: NETWORK, PARSING, VALIDATION, PERMISSION, UNKNOWN
- `DataUpdateFrequency`: REALTIME, HOURLY, DAILY, WEEKLY, MONTHLY, ANNUAL, MANUAL
- `DataFormat`: JSON, CSV, XML, PARQUET, OTHER
- `DataAccessLevel`: PUBLIC, RESTRICTED, PRIVATE, INTERNAL
- `ArtifactType`: DATASET, MODEL, REPORT, VISUALIZATION, LOG

#### 2. Data Loader Tools (`src/multi_agent_system/data/loader_tools.py`)
- `@adk_tool` decorator for registering functions as ADK tools
- `LoaderMetrics` dataclass for call/error/latency tracking
- `DataLoaderAgentCard` for AgentCard-compatible metadata
- Pre-registered cards for ERS and NASS loaders

#### 3. Batch Processing (`src/multi_agent_system/data/batch_orchestration.py`)
- `BatchProcessor`: Parallel batch execution with error aggregation
- `WorkflowOrchestrator`: Multi-step workflow execution with provenance tracking
- `WorkflowStep`, `StepResult`, `WorkflowResult`: Dataclasses for workflow management

#### 4. Agent Cards (`src/multi_agent_system/agents/cards.py`)
- `DATA_LOADER_AGENT_CARDS`: AgentCards for data loaders
- `ALL_AGENT_CARDS`: Combined registry for all agents
- Helper functions: `get_agent_card()`, `get_all_agent_cards()`, `get_data_loader_cards()`

### References
- [Google Cloud Agent SDK Documentation](https://cloud.google.com/agent-sdk/docs)
- [Google Cloud Agent Engine Documentation](https://cloud.google.com/agent-engine/docs)

---
