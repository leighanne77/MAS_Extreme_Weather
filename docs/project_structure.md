# Project Structure Documentation

## Overview
This document outlines the complete structure of the Multi-Agent Climate Risk Analysis System, including all directories, files, and their purposes.

## Root Directory Structure

```
004_MAS_Climate/
├── app.py                          # Main application entry point
├── phase5_demo.py                  # Demo application for Phase 5
├── phase5_implementation.py        # Phase 5 implementation
├── risk_definitions.py             # Risk definitions and thresholds
├── pyproject.toml                  # Project configuration and dependencies
├── requirements.txt                # Python dependencies
├── setup.py                        # Package setup configuration
├── Makefile                        # Build and development commands
├── README.md                       # Project overview and setup instructions
├── TODO.md                         # Development tasks and roadmap
├── frontend-cleanup-plan.md        # Frontend cleanup strategy
├── frontend-updates-summary.md     # Frontend update summary
├── GCP to do.md                    # Google Cloud Platform tasks
├── artifacts.db                    # SQLite database for artifacts
├── artifacts/                      # Generated artifacts storage
├── benchmark_results/              # Performance benchmark results
├── checkpoints/                    # Model checkpoints and state
├── htmlcov/                        # Test coverage reports
├── sessions/                       # User session data
├── test_sessions/                  # Test session data
├── user_manuals/                   # User documentation
├── venv/                          # Python virtual environment
├── docs/                          # Documentation directory
├── src/                           # Source code directory
├── tests/                         # Test files
└── src_backup_20250618_214639/    # Backup of source code
```

## Documentation Directory (`docs/`)

```
docs/
├── a2a_integration.md              # Agent-to-Agent protocol documentation
├── A2A_reference.md                # A2A protocol reference
├── ADK_A2A_Usage_Table.md          # ADK and A2A usage guidelines
├── agent_guidelines.md             # Agent development guidelines
├── agentcard.md                    # Agent card documentation
├── archived_old_engineering_roadmap_ideas.md  # Archived roadmap ideas
├── Do_not_do.md                    # Project restrictions and guidelines
├── DRAFT_Prototypes_Data_Sources.md # Data sources for prototypes
├── DRAFT_prototypes_user_journeys.md # User journey documentation
├── DRAFT_UX_ideas.md               # UX design ideas
├── Draft_value_propositions.md     # Value propositions
├── Engineering_Draft_Devops.md     # DevOps engineering documentation
├── Engineering_Roadmap.md          # Engineering roadmap
├── future_UX.md                    # Future UX plans
├── project_structure.md            # This file - project structure
├── prototypes.md                   # Prototype documentation
├── terms_used.md                   # Terminology and definitions
├── user-guide-mockup.md            # User guide mockup
└── docs_backup_20250618_214657/    # Documentation backup
```

## Source Code Directory (`src/`)

### Main Multi-Agent System (`src/multi_agent_system/`)

```
src/multi_agent_system/
├── __init__.py                     # Package initialization
├── config.py                       # Configuration settings
├── coordinator.py                  # Agent coordination system
├── agent_team.py                   # Agent team management
├── session_manager.py              # Session management
├── communication.py                # Communication protocols
├── data_management.py              # Data management with ADK features
├── adk_integration.py              # Google ADK integration
├── observability.py                # Observability and monitoring
├── risk_definitions.py             # Risk definitions and types
├── weather_risks.py                # Weather risk analysis
├── artifact_manager.py             # Artifact management
├── agents/                         # Agent implementations
│   ├── __init__.py                 # Agents package
│   ├── base_agent.py               # Base agent class
│   ├── risk_agent.py               # Risk analysis agent
│   ├── historical_agent.py         # Historical analysis agent
│   ├── news_agent.py               # News monitoring agent
│   ├── recommendation_agent.py     # Recommendation agent
│   ├── validation_agent.py         # Validation agent
│   ├── greeting_agent.py           # Greeting agent
│   ├── farewell_agent.py           # Farewell agent
│   ├── tools.py                    # Agent tools
│   └── cards.py                    # Agent cards
├── data/                           # Data sources and management
│   ├── __init__.py                 # Data package
│   ├── data_source.py              # Base data source class
│   ├── data_sources.py             # Data source manager
│   ├── weather_data.py             # Weather data integration
│   ├── nature_based_solutions_source.py  # Nature-based solutions
│   ├── enhanced_data_sources.py    # Enhanced data sources
│   ├── data_sources.py             # Data source integration
│   └── nature_based_solutions.json # Nature-based solutions data
├── a2a/                            # Agent-to-Agent protocol
│   ├── __init__.py                 # A2A package
│   ├── message.py                  # Message definitions
│   ├── multipart.py                # Multi-part message handling
│   ├── parts.py                    # Message parts
│   ├── router.py                   # Message routing
│   ├── task_manager.py             # Task management
│   ├── artifacts.py                # Artifact handling
│   ├── artifact_manager.py         # Artifact management
│   ├── content_handlers.py         # Content handling
│   └── enums.py                    # A2A enumerations
├── utils/                          # Utility functions
│   ├── __init__.py                 # Utils package
│   └── adk_features.py             # ADK feature implementations
├── performance/                    # Performance monitoring
│   ├── __init__.py                 # Performance package
│   ├── benchmarking.py             # Performance benchmarking
│   ├── caching.py                  # Caching mechanisms
│   ├── load_testing.py             # Load testing
│   ├── monitoring.py               # Performance monitoring
│   └── optimization.py             # Performance optimization
└── workflows/                      # Workflow management
    ├── __init__.py                 # Workflows package
    └── workflows.py                # Workflow definitions
```

### Agentic Data Management (`src/agentic_data_management/`)

```
src/agentic_data_management/
├── __init__.py                     # Package initialization
├── config.py                       # Configuration settings
├── coordinator.py                  # Data coordination
├── data_manager.py                 # Data management
├── governance.py                   # Data governance
├── quality.py                      # Data quality management
├── schemas.py                      # Data schemas
├── transformers.py                 # Data transformers
├── validators.py                   # Data validators
├── workflows.py                    # Data workflows
├── agents/                         # Data management agents
│   ├── base_agent.py               # Base agent for data management
│   ├── access_agent.py             # Data access control
│   ├── aggregation_agent.py        # Data aggregation
│   ├── audit_agent.py              # Data auditing
│   ├── catalog_agent.py            # Data cataloging
│   ├── compliance_agent.py         # Compliance management
│   ├── data_agent.py               # Core data operations
│   ├── enrichment_agent.py         # Data enrichment
│   ├── error_agent.py              # Error handling
│   ├── integration_agent.py        # Data integration
│   ├── lifecycle_agent.py          # Data lifecycle
│   ├── lineage_agent.py            # Data lineage
│   ├── metadata_agent.py           # Metadata management
│   ├── notification_agent.py       # Notifications
│   ├── performance_agent.py        # Performance monitoring
│   ├── quality_agent.py            # Data quality
│   ├── security_agent.py           # Data security
│   ├── transformation_agent.py     # Data transformation
│   ├── validate_agent.py           # Data validation
│   ├── validation_agent.py         # Validation (duplicate)
│   └── visualization_agent.py      # Data visualization
└── integrations/                   # External integrations
    └── google_cloud.py             # Google Cloud integration
```

### Web Application (`src/pythia_web/`)

```
src/pythia_web/
├── __init__.py                     # Package initialization
├── app.py                          # Web application
├── config.py                       # Web configuration
├── routes/                         # Web routes
├── templates/                      # HTML templates
├── static/                         # Static assets
│   ├── css/                        # Stylesheets
│   ├── js/                         # JavaScript files
│   └── images/                     # Images
└── utils/                          # Web utilities
```

## Test Directory (`tests/`)

```
tests/
├── conftest.py                     # Test configuration
├── README.md                       # Test documentation
├── test_a2a_and_artifacts.py       # A2A and artifacts tests
├── test_agents_and_team.py         # Agent and team tests
├── test_data_and_utils.py          # Data and utilities tests
├── test_frontend_simplified.py     # Frontend tests
├── test_integration_and_observability.py  # Integration tests
└── test_readme.md                  # Test readme
```

## Key Files and Their Purposes

### Configuration Files
- **pyproject.toml**: Project metadata, dependencies, and build configuration
- **requirements.txt**: Python package dependencies
- **setup.py**: Package installation configuration
- **Makefile**: Build, test, and development commands

### Main Application Files
- **app.py**: Main application entry point
- **phase5_demo.py**: Demo application for Phase 5
- **phase5_implementation.py**: Phase 5 implementation
- **risk_definitions.py**: Risk definitions and thresholds

### Documentation Files
- **README.md**: Project overview and setup instructions
- **TODO.md**: Development tasks and roadmap
- **docs/**: Comprehensive documentation directory

### Data and Artifacts
- **artifacts.db**: SQLite database for storing artifacts
- **artifacts/**: Directory for generated artifacts
- **sessions/**: User session data
- **test_sessions/**: Test session data

### Development and Testing
- **tests/**: Comprehensive test suite
- **htmlcov/**: Test coverage reports
- **benchmark_results/**: Performance benchmark results

## Architecture Overview

### Multi-Agent System Architecture
The system follows a multi-agent architecture with:
- **Base Agent Class**: Unified agent implementation with ADK features
- **Specialized Agents**: Domain-specific agents for different functions
- **Agent Teams**: Coordinated groups of agents working together
- **A2A Protocol**: Inter-agent communication protocol
- **Session Management**: User session handling and state management

### Frontend Architecture
The frontend system is built with a **Vanilla JavaScript + FastAPI** approach:

#### **Technology Stack Decision**
- **Vanilla JavaScript**: Lightweight, no framework overhead, easy maintenance
- **FastAPI Backend**: High-performance Python web framework with automatic API documentation
- **Chart.js Integration**: For data visualization and interactive charts
- **Responsive Design**: Mobile-first approach with CSS Grid and Flexbox

#### **Frontend Components**
- **Dashboard Interface**: Main user interface for risk analysis and data visualization
- **Data Visualization**: Interactive charts and graphs for risk metrics
- **Form Components**: Location selection, parameter configuration, and filtering
- **API Integration**: RESTful API communication with FastAPI backend
- **Real-time Updates**: WebSocket connections for live data updates

#### **Frontend Structure**
```
src/pythia_web/
├── static/
│   ├── css/
│   │   └── dashboard.css          # Main dashboard styles
│   └── js/
│       ├── dashboard.js           # Main dashboard functionality
│       ├── simple-charts.js       # Chart.js integration
│       ├── location-handler.js    # Location selection and validation
│       ├── confidence-levels.js   # Confidence score display
│       ├── resilience-options.js  # Nature-based solutions display
│       ├── roi-display.js         # ROI calculations and display
│       ├── simple-filters.js      # Data filtering functionality
│       └── query-suggestions.js   # Natural language query assistance
├── templates/
│   ├── dashboard.html             # Main dashboard template
│   └── dashboard-simplified.html  # Simplified dashboard view
└── interface.py                   # FastAPI application entry point
```

#### **Frontend Features**
- **Natural Language Queries**: Users can ask questions in plain English
- **Interactive Maps**: Location-based risk visualization
- **Real-time Data**: Live updates from weather and environmental APIs
- **Export Capabilities**: CSV, JSON, and PDF report generation
- **Mobile Responsive**: Works seamlessly on desktop, tablet, and mobile devices

### Data Management Architecture
The data management system includes:
- **Data Sources**: Multiple data source integrations
- **Enhanced Data Sources**: International and specialized data
- **Data Agents**: Specialized agents for data operations
- **Data Governance**: Quality, security, and compliance management

### Integration Architecture
The system integrates with:
- **Google Cloud Platform**: Vertex AI, ADK, and cloud services
- **External APIs**: Weather, environmental, and economic data
- **Web Interface**: User-facing web application with FastAPI backend

### Full-Stack Architecture
The complete system architecture follows a **separation of concerns** pattern:

#### **Backend Layer (FastAPI)**
- **API Endpoints**: RESTful API for frontend communication
- **Agent Orchestration**: Multi-agent system coordination
- **Data Processing**: Weather data, risk calculations, and analysis
- **Authentication**: User session management and security
- **Database Integration**: SQLite for artifacts, PostgreSQL for production

#### **Frontend Layer (Vanilla JavaScript)**
- **User Interface**: Dashboard and data visualization
- **API Communication**: HTTP requests to FastAPI backend
- **Data Visualization**: Chart.js for interactive charts
- **Form Handling**: User input validation and processing
- **Real-time Updates**: WebSocket connections for live data

#### **Data Layer**
- **External APIs**: NOAA, NASA, and environmental data sources
- **Local Storage**: SQLite database for artifacts and sessions
- **Cloud Storage**: Google Cloud Storage for large datasets
- **Caching**: Redis for performance optimization

#### **Agent Layer**
- **Specialized Agents**: Risk analysis, historical data, recommendations
- **A2A Protocol**: Inter-agent communication
- **ADK Integration**: Google Agent Development Kit
- **Observability**: Monitoring and logging across all agents

### Security Architecture
- **HTTPS Only**: All communications encrypted
- **API Authentication**: Bearer token authentication
- **Input Validation**: Comprehensive validation on all user inputs
- **Data Privacy**: No storage of proprietary user data
- **Confidential Compute**: Google Cloud Confidential Space for sensitive data

### Performance Architecture
- **Caching Strategy**: Multi-level caching (Redis, browser, CDN)
- **Load Balancing**: Horizontal scaling capabilities
- **Database Optimization**: Indexed queries and connection pooling
- **Frontend Optimization**: Minified assets and lazy loading
- **API Rate Limiting**: Protection against abuse

### Deployment Architecture
- **Containerization**: Docker containers for consistent deployment
- **Cloud Native**: Designed for Google Cloud Platform
- **CI/CD Pipeline**: Automated testing and deployment
- **Monitoring**: Prometheus and Grafana for observability
- **Logging**: Structured logging with correlation IDs

## Development Workflow

### Code Organization
- **src/multi_agent_system/**: Core multi-agent system
- **src/agentic_data_management/**: Data management system
- **src/pythia_web/**: Web application interface
- **tests/**: Comprehensive test suite
- **docs/**: Complete documentation

### Build and Deployment
- **Makefile**: Standardized build commands
- **pyproject.toml**: Modern Python packaging
- **requirements.txt**: Dependency management
- **setup.py**: Package installation

### Testing and Quality
- **tests/**: Unit, integration, and end-to-end tests
- **htmlcov/**: Coverage reporting
- **benchmark_results/**: Performance testing

This structure provides a comprehensive, scalable foundation for the Multi-Agent Climate Risk Analysis System with clear separation of concerns, modular design, and comprehensive documentation.
