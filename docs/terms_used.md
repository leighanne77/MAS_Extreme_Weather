# Terms Used in Multi-Agent Climate Risk Analysis System

## Core Components

### Agents

#### **Base Agent Classes**
- **BaseAgent**: The unified abstract base class for all agents in the system, located in `src/multi_agent_system/agents/base_agent.py`. Provides comprehensive ADK features, security, and A2A protocol support.

#### **Multi-Agent System Agents** (`src/multi_agent_system/agents/`)
- **RiskAnalyzerAgent**: Analyzes current climate risks and conditions using multiple data sources and risk assessment algorithms
- **HistoricalAnalyzerAgent**: Analyzes historical climate patterns and trends to provide context for current risk assessments
- **NewsMonitoringAgent**: Monitors real-time climate-related news and alerts from various sources
- **RecommendationAgent**: Generates actionable recommendations based on risk analysis and user requirements
- **ValidationAgent**: Ensures data quality and consistency across all data sources and analysis results
- **GreetingAgent**: Handles user greetings and initial interactions, setting up analysis sessions
- **FarewellAgent**: Handles user farewells and session cleanup, ensuring proper resource management

#### **Agentic Data Management Agents** (`src/agentic_data_management/agents/`)
- **DataAgent**: Manages core data operations including import, export, transformation, and synchronization
- **LifecycleAgent**: Manages data lifecycle operations including creation, updates, archival, and deletion
- **AuditAgent**: Performs data auditing and compliance checks, ensuring data integrity and regulatory compliance
- **SecurityAgent**: Manages data security and access control, implementing authentication and authorization
- **ValidateAgent**: Performs data validation and quality checks, ensuring data meets defined standards
- **VisualizationAgent**: Creates data visualizations and charts for analysis results and reports
- **AggregationAgent**: Aggregates data from multiple sources and performs data consolidation
- **EnrichmentAgent**: Enriches data with additional context, metadata, and derived information
- **TransformationAgent**: Transforms data between different formats and structures
- **ValidationAgent**: Performs comprehensive data validation (duplicate of ValidateAgent)
- **ErrorAgent**: Handles error conditions and provides error recovery mechanisms
- **PerformanceAgent**: Monitors system performance and optimizes data operations
- **NotificationAgent**: Manages notifications and alerts for system events and user communications
- **AccessAgent**: Controls data access permissions and manages user access rights
- **MetadataAgent**: Manages metadata for all data sources and data objects
- **QualityAgent**: Ensures data quality standards and performs quality assessments
- **IntegrationAgent**: Manages integration with external data sources and systems
- **ComplianceAgent**: Ensures regulatory compliance and manages compliance reporting
- **LineageAgent**: Tracks data lineage and maintains audit trails for data transformations
- **CatalogAgent**: Manages data catalog and provides data discovery capabilities

#### **Coordinator and Team Management**
- **CoordinatorAgent**: Enhanced coordinator that inherits from BaseAgent, providing parallel execution, token tracking, and A2A protocol support
- **AgentTeam**: Coordinates multiple agents for risk analysis with ADK features, managing a team of specialized agents that work together
- **AgentCapability**: Represents a specific capability of an agent with required tools and output keys

### Session Management
- **SessionManager**: Manages analysis sessions, state tracking, and agent coordination
- **AnalysisSession**: Represents a complete analysis session with agent states and context
- **AgentState**: Represents the state of an individual agent within a session
- **SessionState**: Enum for session states (CREATED, RUNNING, COMPLETED, FAILED)

### Communication
- **A2A Protocol**: Agent-to-Agent communication protocol for inter-agent messaging
- **A2AMessage**: Structured messages for agent communication
- **A2AMultiPartMessage**: Multi-part messages for complex data transmission
- **A2APart**: Individual parts of multi-part messages

### Data Management
- **DataManager**: Manages data sources and data operations with ADK features
- **DataSource**: Abstract base for data sources
- **NOAAWeatherData**: Weather data source implementation
- **NatureBasedSolutionsSource**: Nature-based solutions data source
- **EnhancedDataManager**: Manages enhanced data sources for international and specialized data
- **DataSourceManager**: Unified manager for all data sources including enhanced sources

### Tools
- **Function-based Tools**: Simple functions that ADK automatically wraps for agent use
- **RiskAnalysisTools**: Collection of tools for risk analysis operations
- **Enhanced Data Tools**: Tools for accessing enhanced data sources including:
  - `get_water_data_tool`: Access water-related data from USDA and state agencies
  - `get_economic_data_tool`: Access economic and financial data
  - `get_infrastructure_data_tool`: Access infrastructure and development data
  - `get_regulatory_data_tool`: Access regulatory and compliance data
  - `get_state_agency_data_tool`: Access state-specific agency data
  - `get_comprehensive_enhanced_data_tool`: Access comprehensive enhanced data

### ADK Features
- **MetricsCollector**: Collects performance metrics and resource usage
- **CircuitBreaker**: Implements circuit breaker pattern for fault tolerance
- **WorkerPool**: Manages a pool of workers for parallel processing
- **Monitoring**: Monitors system state and performance
- **Buffer**: Implements pipeline stage buffering

### Unified Architecture
- **Single Agent Hierarchy**: All agents now inherit from the comprehensive `BaseAgent` class
- **Consolidated Imports**: Updated all imports to use the unified agent structure
- **Simplified Tool System**: Function-based tools that ADK automatically wraps

## Workflow Components

### Workflows
- **SequentialWorkflow**: Executes workflow steps in sequence
- **ParallelWorkflow**: Executes workflow steps in parallel
- **LoopWorkflow**: Executes workflow steps in a loop
- **WorkflowManager**: Manages workflow execution and state

### Risk Analysis
- **ClimateRiskAnalyzer**: Analyzes climate risks using multiple data sources
- **RiskType**: Enum for different types of climate risks
- **RiskLevel**: Enum for risk severity levels
- **RiskSource**: Enum for sources of risk data
- **RiskThreshold**: Defines thresholds for risk assessment

## Security and Monitoring

### Security
- **SecurityContext**: Security context for sessions and operations
- **RequestValidator**: Validates incoming requests
- **RateLimiter**: Implements rate limiting for API calls
- **AuditLogger**: Logs security-relevant events

### Error Handling
- **ErrorContext**: Context for detailed error reporting
- **ErrorHandler**: Handles and processes errors
- **RetryPolicy**: Implements retry logic for failed operations

### Performance
- **PerformanceMonitor**: Monitors system performance
- **PerformanceTracker**: Tracks operation performance
- **TokenUsage**: Tracks token usage for agents and operations

## Data Structures

### Messages
- **RequestMessage**: Messages for requesting operations
- **ResponseMessage**: Messages for responding to requests
- **NotificationMessage**: Messages for notifications
- **HeartbeatMessage**: Messages for health checks

### Artifacts
- **Artifact**: Data artifacts generated by agents
- **ArtifactManager**: Manages artifact storage and retrieval
- **CompressedContext**: Manages compressed context data

## Integration Components

### External Services
- **Vertex AI**: Google Cloud AI platform integration
- **Google ADK**: Google Agent Development Kit integration
- **JWT**: JSON Web Token authentication

### File Management
- **aiofiles**: Asynchronous file operations
- **aiohttp**: Asynchronous HTTP client/server
- **pathlib**: Path manipulation utilities

## Risk Assessment Components

### Risk Definitions
- **RiskSource**: Represents a source of risk definition with metadata, including criteria, source, URL, and last updated timestamp
- **RiskThreshold**: Represents a risk threshold with ADK features, including value, unit, sources, and monitoring capabilities
- **RiskLevel**: Represents a risk level with ADK features, including name, description, thresholds, and metadata
- **RiskType**: Enum for different risk types (TEMPERATURE, PRECIPITATION, WIND, HUMIDITY, AIR_QUALITY) with ADK metadata

### Authoritative Sources
- **FEMA Definitions**: Federal Emergency Management Agency risk definitions for flooding, wildfire, extreme storms, and extreme heat
- **ISO Definitions**: Insurance Services Office risk definitions for property evaluation and catastrophe risk assessment
- **WHO Definitions**: World Health Organization definitions for extreme heat and health impacts
- **NOAA Definitions**: National Oceanic and Atmospheric Administration definitions for extreme weather events

### Risk Severity Levels
- **LOW**: Minimal risk conditions
- **MODERATE**: Moderate risk conditions requiring attention
- **HIGH**: High risk conditions requiring immediate action
- **EXTREME**: Extreme risk conditions requiring emergency response
- **SUPER_EXTREME**: Super extreme conditions (e.g., frequent 100-year flood levels)

## Nature-Based Solutions

### Solution Categories
- **Water Management Solutions**: Wetland restoration, living shorelines, rain gardens, bioswales, stormwater harvesting
- **Urban Infrastructure**: Green roofs, permeable pavement, green streets, green walls, tree canopy expansion
- **Agricultural Solutions**: Climate-smart agricultural practices, community gardens, urban agriculture
- **Coastal/Marine Solutions**: Eelgrass meadow restoration, oyster reef restoration, coral reef restoration, mangrove restoration
- **Land Management**: Forest health management, rangeland management, dryland restoration, slope stabilization

### Solution Attributes
- **Risk Types**: Categories of risks that solutions address (flooding, extreme_heat, drought, etc.)
- **Suitable Locations**: Types of locations where solutions can be implemented (urban, rural, coastal, agricultural_lands)
- **Scale**: Implementation scale (local, city, regional)
- **Implementation Level**: Who can implement the solution (property_owner, community, city_regional, agency_regional)
- **Benefits**: Environmental and economic benefits of the solution
- **Implementation Steps**: Step-by-step guidance for implementation
- **Maintenance Requirements**: Ongoing maintenance needs
- **Cost Factors**: Factors affecting implementation costs
- **Effectiveness Metrics**: Measurable outcomes and effectiveness indicators

## Weather and Environmental Data

### Data Sources
- **OpenWeather API**: Current weather data and forecasts
- **NOAA SWDI**: Severe Weather Data Inventory for historical weather events
- **NOAA National Hurricane Center**: Hurricane tracking and intensity data
- **USGS**: Geological data, sea level rise projections, and water data
- **National Weather Service**: Extreme weather frequency and duration data
- **FEMA**: Flood risk assessments and mapping
- **EPA**: Water quality and environmental compliance data

### Enhanced Data Sources
- **USDA Water Data**: Drought monitoring, crop water requirements, soil survey data
- **State Agency Data**: State-specific water, agricultural, and environmental data
- **Economic Data**: Regional economic indicators, agricultural finance data
- **Infrastructure Data**: Infrastructure resilience, development project data
- **Regulatory Data**: Environmental compliance, Opportunity Zone data

### Weather Parameters
- **Temperature**: Current and historical temperature data
- **Humidity**: Relative humidity measurements
- **Wind Speed**: Wind velocity measurements
- **Precipitation**: Rainfall amounts and patterns
- **Weather Conditions**: Current weather state descriptions

### Risk Analysis Methods
- **Historical Data Analysis**: Analysis of past weather events and patterns
- **Frequency Analysis**: Assessment of how often extreme events occur
- **Threshold Comparison**: Comparison of current conditions against established risk thresholds
- **Multi-Source Validation**: Cross-validation using multiple data sources

## Frontend Components (Simplified)

### Core Display Components
- **ResilienceOptions**: Displays resilience strategies and adaptation options returned by agents
- **ConfidenceLevels**: Displays confidence levels returned by agents
- **ROIDisplay**: Displays ROI and financial metrics calculated by agents
- **LocationHandler**: Handles location input and validation

### Simplified Components
- **SimpleFilters**: Basic filtering with 3 filter types (time, risk level, solution type)
- **SimpleSuggestions**: Basic query suggestions (10 general suggestions)
- **SimpleCharts**: Basic chart display for agent data (risk, ROI, timeline)
- **ConsolidatedDashboard**: Main dashboard that combines all simplified components

### Frontend Responsibilities
- **Simple Data Display**: Display agent analysis results in clean format
- **Basic User Interactions**: Handle form submissions and user input
- **Export Functionality**: Export results as JSON for integration
- **Loading States**: Show loading indicators during analysis
- **Error Messages**: Display error messages for failed operations

### Agent Responsibilities (Complex Processing)
- **Complex Filtering**: Filter data based on user queries and parameters
- **Data Processing**: Process and analyze environmental data
- **Risk Calculations**: Calculate risk levels and confidence scores
- **ROI Analysis**: Calculate financial metrics and returns
- **Recommendation Generation**: Generate actionable recommendations

## User Interface Terms

### Query Interface
- **Natural Language Input**: Users can ask questions in plain English
- **Location Specification**: Enter specific locations (city, county, coordinates)
- **Time Range Selection**: Choose 5, 7, or 10 year analysis periods
- **Query Suggestions**: Pre-written example queries for guidance

### Results Display
- **Risk Assessment Card**: Shows overall risk level and breakdown by risk type
- **Resilience Options**: Lists adaptation strategies with costs and ROI
- **Confidence Display**: Shows confidence levels for analysis results
- **ROI Analysis**: Displays financial impact and return metrics
- **Recommendations**: Lists specific actions to take

### Data Visualization
- **Risk Assessment Chart**: Simple chart showing risk levels by category
- **ROI Comparison Chart**: Chart comparing returns on different solutions
- **Timeline Chart**: Chart showing risk progression over time

### Export and Integration
- **JSON Export**: Download complete analysis results in JSON format
- **Integration Ready**: Data format designed for financial modeling tools
- **API Access**: Programmatic access to analysis results

## Performance Terms

### ADK Features
- **Definition**: Google ADK (Agent Development Kit) features
- **Components**: MetricsCollector, CircuitBreaker, WorkerPool, Monitoring, Buffer
- **Purpose**: Performance monitoring and system reliability
- **Implementation**: `src/multi_agent_system/utils/adk_features.py`

### Performance Monitoring
- **Definition**: Real-time system performance tracking
- **Metrics**: Response times, throughput, error rates, resource usage
- **Purpose**: System optimization and reliability
- **Implementation**: `src/multi_agent_system/performance/`

### Load Testing
- **Definition**: Testing system performance under load
- **Purpose**: Validate scalability and performance requirements
- **Implementation**: `src/multi_agent_system/performance/load_testing.py`

## Development Terms

### Phase 5 Implementation
- **Definition**: Advanced system enhancement and production readiness
- **Components**: Performance optimization, security enhancement, comprehensive testing
- **Purpose**: Production deployment preparation
- **Implementation**: `phase5_implementation.py`

### Engineering Roadmap
- **Definition**: Technical implementation plan across phases
- **Phases**: 1 (A2A/ADK), 2 (Google Cloud), 3 (Performance), 4 (Production), 5 (Advanced)
- **Purpose**: Structured development approach
- **Documentation**: `docs/Engineering_Roadmap.md`

### PRD (Product Requirements Document)
- **Definition**: Product requirements and specifications
- **Purpose**: Define system capabilities and user needs
- **Components**: User journeys, technical requirements, delivery model
- **Documentation**: `docs/PRD.md`

## Extreme Weather Terms

### Extreme Weather
- **Definition**: Severe weather events affecting business operations
- **Types**: Droughts, floods, hurricanes, heat waves, storms
- **Impact**: Asset values, operational continuity, financial performance
- **Analysis**: Risk assessment and mitigation strategies

### Nature-Based Solutions (NBS)
- **Definition**: Natural approaches to climate resilience
- **Examples**: Wetland restoration, reforestation, sustainable agriculture
- **Purpose**: Cost-effective climate adaptation strategies
- **Data**: `src/multi_agent_system/data/nature_based_solutions.json`

### Risk Definitions
- **Definition**: Categorized risk types and severity levels
- **Categories**: Water risk, heat risk, storm risk, flood risk
- **Purpose**: Standardized risk assessment framework
- **Implementation**: `risk_definitions.py`

## Geographic Terms

### Prototype Regions
- **West Kansas**: Water management and farming finance
- **Caribbean Islands + South Florida**: Hospitality and investment
- **North Carolina (Inland)**: Data center infrastructure
- **Mobile Bay, Alabama**: Infrastructure manufacturing development
- **Deccan Plateau, India**: Rural agricultural development

### Bioregional
- **Definition**: Geographic regions with similar environmental characteristics
- **Purpose**: Tailored analysis and recommendations
- **Application**: Risk assessment and adaptation strategies

## Financial Terms

### IRR (Internal Rate of Return)
- **Definition**: Financial metric for investment performance
- **Purpose**: Evaluate investment profitability
- **Application**: Climate resilience investment analysis

### ROI (Return on Investment)
- **Definition**: Financial return relative to investment cost
- **Purpose**: Assess investment effectiveness
- **Application**: Adaptation strategy evaluation

### Collateral Value
- **Definition**: Asset value used as loan security
- **Purpose**: Risk assessment and loan valuation
- **Impact**: Affected by extreme weather events

## Technical Terms

### FastAPI
- **Definition**: Modern Python web framework
- **Purpose**: API development and web interface
- **Usage**: Both `app.py` and `src/pythia_web/interface.py`

### SQLite
- **Definition**: Lightweight database for metadata storage
- **Purpose**: Artifact metadata and session data
- **Location**: `artifacts.db`

### JSON
- **Definition**: Data format for configuration and communication
- **Purpose**: Agent messages, session data, configuration
- **Usage**: Throughout the system for data exchange

### Gitignore
- **Definition**: Git configuration for excluding files
- **Purpose**: Prevent sensitive or development files from version control
- **Files**: UX mockups, web interface, development configurations

---

## Related Documentation

- [Do_not_do.md](Do_not_do.md) - Guidelines for what not to do in this project
- [Draft_value_propositions.md](Draft_value_propositions.md) - Common value propositions across all prototype users