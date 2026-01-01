# Terms Used - Tool Multi-Agent Extreme Weather Risk Analysis System

**Date Created**: June 20, 2025
**Date Last Updated**: December 12, 2025

## Overview
This document defines the approved terminology and definitions used throughout the Tool system. All communications, documentation, and user interfaces should use these standardized terms to ensure consistency and clarity.

## Core System Terminology

### **System Name and Branding**
- **Tool**: The official name of the multi-agent extreme weather risk analysis system
- **Multi-Agent System**: The core architecture using specialized AI agents for risk analysis
- **Extreme Weather Risk Analysis**: The primary focus area of the system

### **Key Terminology Guidelines**
- **USE**: "extreme weather-related risk" instead of "climate risk"
- **USE**: "extreme weather events" instead of "climate events"
- **USE**: "weather resilience" instead of "climate resilience"
- **USE**: "extreme weather adaptation" instead of "climate adaptation"
- **AVOID**: "climate change", "carbon", "climate markets", "carbon credits"

## Agentic AI Protocols and Frameworks

### **A2A (Agent2Agent Protocol)**
- **Definition**: Google's Agent2Agent (A2A) protocol for agent-to-agent communication
- **Purpose**: Enables agents to discover each other, negotiate tasks, exchange messages, and collaborate across systems
- **Key Function**: Defines how agents communicate with each other in a networked team
- **Analogy**: If MCP equips an agent to be powerful on its own, A2A enables that agent to become part of a networked team
- **Use Case**: Allows specialized agents (risk analysis, historical data, recommendations, validation) to coordinate and collaborate seamlessly
- **Relationship**: Works alongside MCP - A2A handles agent-to-agent communication while MCP handles tool access
- **Implementation**: See [A2A Integration Guide](../5-ENGINEERING/A2A_ADK/3.1_A2A_Integration.md) and [A2A Reference](../5-ENGINEERING/A2A_ADK/3.2_A2A_Reference.md)

### **MCP (Model Context Protocol)**
- **Definition**: Anthropic's Model Context Protocol (MCP) for agent-environment interface
- **Purpose**: Standardizes how agents interface with their environment - APIs, tools, file systems, databases, and more
- **Key Function**: Acts as a "universal adapter" or USB port that standardizes how agents "plug into" external resources
- **Analogy**: Like a universal adapter that allows agents to access the tools they need to think, reason, and act
- **Use Case**: Enables agents to access external data sources, tools, and services in a standardized way
- **Relationship**: Complementary to A2A - MCP focuses on how a single agent interfaces with its environment, while A2A focuses on agent-to-agent communication
- **Implementation**: Used for integrating data sources like CMR (NASA Earthdata), ERDDAP, Data.gov, NOAA, USGS, EPA, and Census Bureau

### **ADK (Agent Development Kit)**
- **Definition**: Google's Agent Development Kit (ADK) - a development framework for building agentic AI applications
- **Purpose**: Provides tools, libraries, and infrastructure for building, deploying, and managing AI agents
- **Key Features**: 
  - Model-agnostic flexibility (supports multiple AI models)
  - Multi-agent architecture support
  - Rich tool ecosystem (pre-built and custom tools)
  - Built-in performance monitoring and reliability features
  - Metrics collection, circuit breakers, worker pools, and monitoring
- **Relationship**: ADK provides the development framework that agents use, while A2A defines how those agents communicate, and MCP defines how agents access external resources
- **Implementation**: See [ADK Features](#adk-features) section and [A2A/ADK Rational](../5-ENGINEERING/A2A_ADK/2.3_A2A_ADK_Rational.md)

### **How A2A, MCP, and ADK Work Together**
- **ADK**: Provides the foundation - the development framework and tools for building agents
- **MCP**: Enables agents to access external resources (data sources, APIs, tools) in a standardized way
- **A2A**: Enables agents to communicate and collaborate with each other across systems
- **Together**: These three technologies provide a complete agentic application architecture:
  - ADK builds the agents
  - MCP connects agents to their environment
  - A2A connects agents to each other

## User Journey Structure

### **Three-Part Journey Framework**
- **Basic**: Initial risk assessment and data gathering phase
- **Better**: Risk mitigation and solution recommendation phase  
- **Advanced**: Ongoing monitoring and resilience tracking phase


## User Types and Roles

### **Primary User Types: three (3) total 
1. investors/funders
2. Expert Data providers
3. Indigenous Data Providers
4. Operators**


1. Investors - Four Types
#### **1.a. Private Equity Investor**
- **Display Name**: "Private Equity"
- **Focus**: Asset protection and investment optimization
- **Key Concerns**: ROI, asset value protection, investment timelines
- **Example Query**: "What are hurricane risks for manufacturing facilities in Mobile Bay?"
- **Journey Structure**: Basic (Risk Assessment) → Better (Risk Mitigation) → Advanced (Resilience Tracking)

#### **1.b. Private Debt Investor**
- **Display Name**: "Private Debt"
- **Focus**: Debt investment risk assessment
- **Key Concerns**: Default risk, cash flow, collateral value
- **Example Query**: "I am evaluating a private debt investment in a coastal manufacturing facility that faces hurricane risks."

#### **1.c. Government Funder**
- **Display Name**: "Government Funder"
- **Focus**: Rural development and infrastructure funding
- **Key Concerns**: Economic impact, social impact, budget efficiency
- **Example Query**: "I am planning rural development investments in drought-affected districts of Maharashtra, India, what are the top ROI ways to help the persistent drought issue?"  

#### **1.d. District Collector (India)**
- **Display Name**: "District Collector"
- **Focus**: Rural development and agricultural community resilience
- **Key Concerns**: Economic impact, social impact, bioregional health, population health
- **Example Query**: "What are major risks from climate change and other extreme weather for the district of Ramanathapuram in South India?"
- **Journey Structure**: Basic (Climate Risk Analysis) → Better (Risk Mitigation) → Advanced (Resilience and Impact)
- **Reference**: [3-EXPERIMENTS/0.7_india/0.71_India_prototype/0.71_India_prototype.md](../3-EXPERIMENTS/0.7_india/0.71_India_prototype/0.71_India_prototype.md) - Complete user journey for District Collectors

2. Data Providers: Two Types

#### **2.a. Data Provider (Scientists and Local Knowledge Experts)**
- **Display Name**: "Data Provider"
- **Focus**: Secure data contribution and expertise monetization
- **Key Concerns**: Data security, confidentiality, fair compensation, bioregional impact
- **Example Query**: "I am a marine biologist with 20 years of experience studying Mobile Bay ecosystems. I want to contribute this data securely and be compensated for my expertise."
- **Journey Structure**: Basic (Secure Data Submission) → Better (Advanced Data Integration) → Advanced (Ongoing Expertise)
- **Reference**: [3-EXPERIMENTS/0.6_Alabama/0.62.1_AL_Expert_Local_Knowledge_Provider_incl_Role_as_Data_Provider/0.62.1_AL_Expert_Local_Knowledge_Provider_incl_Role_as_Data_Provider.md](../3-EXPERIMENTS/0.6_Alabama/0.62.1_AL_Expert_Local_Knowledge_Provider_incl_Role_as_Data_Provider/0.62.1_AL_Expert_Local_Knowledge_Provider_incl_Role_as_Data_Provider.md) - Complete user journey for Expert Local Knowledge Providers (including role as Data Providers)

#### **2.b. Indigenous Knowledge Holder**
- **Display Name**: "Indigenous Knowledge Holder"
- **Focus**: Traditional knowledge sharing and cultural protocol compliance
- **Key Concerns**: Cultural sensitivity, collective benefit, traditional knowledge sovereignty, ancestral land protection
- **Example Query**: "I am a cultural knowledge keeper for our tribe, with deep understanding of Mobile Bay ecosystems passed down through generations."
- **Journey Structure**: Basic (Respectful Knowledge Submission) → Better (Advanced Knowledge Integration) → Advanced (Cultural Expertise and Impact)
- **Reference**: [3-EXPERIMENTS/0.6_Alabama/0.62.2_AL_Indigenous_Local_Knowledge_Provider_incl_Role_as_Data_Provider/0.62.2_AL_Indigenous_Local_Knowledge_Provider_incl_Role_as_Data_Provider.md](../3-EXPERIMENTS/0.6_Alabama/0.62.2_AL_Indigenous_Local_Knowledge_Provider_incl_Role_as_Data_Provider/0.62.2_AL_Indigenous_Local_Knowledge_Provider_incl_Role_as_Data_Provider.md) - Complete user journey for Indigenous Local Knowledge Providers (including role as Data Providers)

3. Operators - who are running operations for investors or government funders

4. OTHERS - not in the top users, four types

#### **4.a. Bank Loan Officer**
- **Display Name**: "Loan Officer"
- **Focus**: Agricultural and commercial lending risk assessment
- **Key Concerns**: Default prevention, collateral value, borrower support
- **Example Query**: "I am evaluating a loan for a 500-acre corn farm in western Kansas that needs water management improvements."

#### **4.b. Data Science Officer**
- **Display Name**: "Data Science"
- **Focus**: Model validation and data integration
- **Key Concerns**: Data quality, model accuracy, validation
- **Example Query**: "I need extreme weather risk data validation for our agricultural risk models covering the Midwest region over the next 5 years."

#### **4.c. Chief Risk Officer**
- **Display Name**: "Risk Officer"
- **Focus**: Portfolio-level risk management and compliance
- **Key Concerns**: Portfolio risk, capital allocation, regulatory compliance
- **Example Query**: "I am assessing portfolio-level extreme weather risks for our agricultural lending portfolio across the Great Plains region."

#### **4.d. Chief Sustainability Officer**
- **Display Name**: "Sustainability Officer"
- **Focus**: ESG compliance and sustainability initiatives
- **Key Concerns**: ESG metrics, biodiversity, green financing
- **Example Query**: "I am developing ESG compliance strategies for sustainable lending programs in drought-prone regions of California."

#### **4.e. Credit Officer**
- **Display Name**: "Credit Officer"
- **Focus**: Seasonal credit and working capital management
- **Key Concerns**: Cash flow, seasonal planning, working capital
- **Example Query**: "I am managing seasonal credit lines for dairy operations in Wisconsin that face extreme weather challenges."

## Risk Categories and Definitions

### **Primary Risk Types**

#### **1. Extreme Heat**
- **Definition**: Elevated temperatures that exceed normal ranges and pose health and operational risks
- **Sources**: FEMA, WHO, NOAA, ISO
- **Thresholds**: 
  - High: >100°F (37.8°C) for 3+ consecutive days
  - Medium: >95°F (35°C) for 3+ consecutive days

#### **2. Flooding**
- **Definition**: Water overflow that submerges normally dry land
- **Sources**: FEMA, ISO
- **Thresholds**:
  - High: >40mm rainfall in 1 hour or 100-year floodplain
  - Medium: >25mm rainfall in 1 hour or 500-year floodplain

#### **3. Wildfire**
- **Definition**: Uncontrolled fires that spread rapidly through vegetation
- **Sources**: FEMA, ISO
- **Thresholds**:
  - High: Relative humidity <25% with winds >25 mph
  - Medium: Relative humidity <35% with winds >20 mph

#### **4. Extreme Storms**
- **Definition**: Severe weather events including thunderstorms, hurricanes, and windstorms
- **Sources**: NOAA, ISO
- **Thresholds**:
  - High: Wind speeds >50 mph or hail >1 inch
  - Medium: Wind speeds >40 mph or hail >0.75 inch

### **Risk Severity Levels**
- **Low**: Minimal risk with standard precautions
- **Medium**: Elevated risk requiring attention
- **High**: Significant risk requiring immediate action
- **Extreme**: Severe risk requiring emergency response
- **Super Extreme**: Exceptional risk with frequent extreme events

## Geographic Prototypes

### **1. Mobile Bay, Alabama - Infrastructure Manufacturing**
- **Focus**: Manufacturing and defense infrastructure
- **Key Risks**: Hurricanes, storm surge, supply chain disruption, red tide/water pollution
- **User Types**: Private Equity Investors (QOZ specialists), Data Providers, Indigenous Knowledge Holders

### **2. India - Rural Agricultural Development**
- **Focus**: Rural development and agricultural communities
- **Key Risks**: Drought, water scarcity, agricultural productivity, monsoon variability, marine heat stress
- **User Types**: Government Funders, District Collectors
- **Reference**: [3-EXPERIMENTS/0.7_india/0.71_India_prototype/0.71_India_prototype.md](../3-EXPERIMENTS/0.7_india/0.71_India_prototype/0.71_India_prototype.md) - Complete prototype documentation

More in this spreadsheet: TBD

### **Archived for Now: West Kansas - Agricultural Lending**
- **Focus**: Agricultural operations and lending
- **Key Risks**: Water scarcity, drought, extreme heat
- **User Types**: Loan Officers, Chief Risk Officers, Credit Officers

### **Archived for Now: Caribbean Islands + South Florida - Hospitality & Investment**
- **Focus**: Hospitality properties and tourism
- **Key Risks**: Hurricanes, sea level rise, coral reef health
- **User Types**: Private Equity Investors, Chief Risk Officers, Chief Sustainability Officers

### **Archived for Now: North Carolina (Inland) - Data Center Infrastructure**
- **Focus**: Technology infrastructure and data centers
- **Key Risks**: Extreme heat, power outages, cooling efficiency
- **User Types**: Private Equity Investors, Data Science Officers

## Technical Terms

### **System Architecture**
- **Agent Team**: Collection of specialized AI agents working together
- **Session Management**: User session tracking and state persistence
- **A2A Protocol**: Agent-to-Agent communication protocol
- **Multi-Agent System**: Distributed AI system with specialized agents

### **Data and Analysis**
- **Confidence Levels**: Measure of data reliability and analysis certainty
- **ROI Analysis**: Return on Investment calculations for adaptation strategies
- **Cost-Benefit Analysis**: Financial evaluation of adaptation options
- **Scenario Generation**: Creation of "what-if" analysis scenarios

### **Data Provider Integration**
- **Google Cloud Confidential Compute**: Secure processing environments where data cannot be accessed by unauthorized parties
- **Zero-Knowledge Architecture**: Data never stored permanently by Pythia, only processed for analysis
- **Cross-Verification**: Data verified against multiple third-party sources without retention
- **Cultural Protocol Integration**: Traditional knowledge sharing follows established cultural protocols
- **Collective Compensation**: Payments distributed to collective groups, not individuals
- **Reference**: [3-EXPERIMENTS/0.6_Alabama/0.62.1_AL_Expert_Local_Knowledge_Provider_incl_Role_as_Data_Provider/0.62.1_AL_Expert_Local_Knowledge_Provider_incl_Role_as_Data_Provider.md](../3-EXPERIMENTS/0.6_Alabama/0.62.1_AL_Expert_Local_Knowledge_Provider_incl_Role_as_Data_Provider/0.62.1_AL_Expert_Local_Knowledge_Provider_incl_Role_as_Data_Provider.md) - Complete data provider integration details

### **Evaluation Methodology for Multi-Agent Systems**
- **Definition**: A systematic framework for assessing the performance, reliability, and effectiveness of multi-agent AI systems through both trajectory analysis and final output evaluation. Unlike traditional software testing with deterministic pass/fail criteria, multi-agent evaluation requires qualitative assessment of decision-making processes, tool usage patterns, and iterative reasoning quality.

- **Key Challenges Addressed**:
  - **Observability Trilemma**: Balancing completeness, timeliness, and low overhead through ADK features
  - **Communication Overload**: Managing exponential message growth with structured A2A protocols
  - **Resource Attribution**: Tracking individual and shared resource usage across agents
  - **Consistency and State Management**: Maintaining system state across distributed agents
  - **Scalability of Monitoring**: Distributing monitoring load across hierarchical levels

- **Key Challenges NOT Addressed**:
  - **Advanced Security Vulnerabilities**: Advanced prompt injection protection, sophisticated agent impersonation detection, advanced data extraction protection (basic security implemented in Phase 1.2)
  - **Advanced Timing Issues**: Advanced distributed tracing systems, temporal logic frameworks, sophisticated timing anomaly detection (basic performance monitoring implemented in Phase 1.1)

- **ADK Features with Evaluation Components**:
  - **Metrics collection** using ADK MetricsCollector
  - **Circuit breaker pattern** for fault tolerance evaluation
  - **Worker pool performance monitoring**
  - **Request tracking** and performance analysis
- **Key Example File**: [src/multi_agent_system/utils/adk_features.py](../src/multi_agent_system/utils/adk_features.py)

### **User Interface**
- **Natural Language Processing**: Query understanding without technical syntax
- **Interactive Visualization**: Dynamic charts and data displays
- **Filter System**: User-selectable criteria for result filtering
- **Export Capabilities**: Data export in multiple formats (JSON, PDF, Excel)

## Technical Implementation Components

### **Core Components**

#### **Base Agent Classes**
- **BaseAgent**: The unified abstract base class for all agents in the system, located in `src/multi_agent_system/agents/base_agent.py`. Provides comprehensive ADK features, security, and A2A protocol support.

#### **Multi-Agent System Agents** (`src/multi_agent_system/agents/`)
- **RiskAnalyzerAgent**: Analyzes current extreme weather risks and conditions using multiple data sources and risk assessment algorithms
- **HistoricalAnalyzerAgent**: Analyzes historical weather patterns and trends to provide context for current risk assessments
- **NewsMonitoringAgent**: Monitors real-time weather-related news and alerts from various sources
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

### **Session Management**
- **SessionManager**: Manages analysis sessions, state tracking, and agent coordination
- **AnalysisSession**: Represents a complete analysis session with agent states and context
- **AgentState**: Represents the state of an individual agent within a session
- **SessionState**: Enum for session states (CREATED, RUNNING, COMPLETED, FAILED)

### **Communication**
- **A2A Protocol**: Agent-to-Agent communication protocol for inter-agent messaging (see [A2A (Agent2Agent Protocol)](#a2a-agent2agent-protocol) section above for detailed definition)
- **A2AMessage**: Structured messages for agent communication following the A2A protocol
- **A2AMultiPartMessage**: Multi-part messages for complex data transmission between agents
- **A2APart**: Individual parts of multi-part messages in A2A protocol
- **AgentCard**: JSON metadata documents that describe an agent's identity, capabilities, skills, service endpoints, and authentication requirements - See [2.4_Agentcard_Definition_Doc_Tool_Instructions.md](../5-ENGINEERING/A2A_ADK/2.4_Agentcard_Definition_Doc_Tool_Instructions.md) for comprehensive AgentCard documentation and examples

### **Data Management**
- **DataManager**: Manages data sources and data operations with ADK features
- **DataSource**: Abstract base for data sources
- **NOAAWeatherData**: Weather data source implementation
- **NatureBasedSolutionsSource**: Nature-based solutions data source
- **EnhancedDataManager**: Manages enhanced data sources for international and specialized data
- **DataSourceManager**: Unified manager for all data sources including enhanced sources

### **Tools**
- **Function-based Tools**: Simple functions that ADK automatically wraps for agent use
- **RiskAnalysisTools**: Collection of tools for risk analysis operations
- **Enhanced Data Tools**: Tools for accessing enhanced data sources including:
  - `get_water_data_tool`: Access water-related data from USDA and state agencies
  - `get_economic_data_tool`: Access economic and financial data
  - `get_infrastructure_data_tool`: Access infrastructure and development data
  - `get_regulatory_data_tool`: Access regulatory and compliance data
  - `get_state_agency_data_tool`: Access state-specific agency data
  - `get_comprehensive_enhanced_data_tool`: Access comprehensive enhanced data

### **ADK Features**
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

### **Reasoning Loops**
- **Definition**: Computational patterns where AI agents iteratively refine their reasoning process through multiple cycles of analysis, evaluation, and adjustment. Enables systems to improve reasoning through multiple passes, self-correct initial conclusions, build upon previous reasoning steps, and handle complex multi-step problems requiring iterative analysis.
- **Implementation**: [LoopWorkflow](../src/multi_agent_system/workflows/workflows.py) - Manages iterative climate analysis tasks with termination conditions and context accumulation
- **Key Features**: 
  - Iterative execution of agents in sequence
  - Context accumulation where each iteration builds on previous results
  - Termination conditions to stop when convergence criteria are met
  - Maximum iteration limits to prevent infinite loops
  - Pattern tracking for recursive and backtracking decision processes

### Risk Analysis
- **ClimateRiskAnalyzer**: Analyzes climate risks using multiple data sources
- **RiskType**: Enum for different types of climate risks
- **RiskLevel**: Enum for risk severity levels
- **RiskSource**: Enum for sources of risk data
- **RiskThreshold**: Defines thresholds for risk assessment

## Security and Monitoring

### **Security**
- **SecurityContext**: Security context for sessions and operations
- **RequestValidator**: Validates incoming requests
- **RateLimiter**: Implements rate limiting for API calls
- **AuditLogger**: Logs security-relevant events

### **Error Handling**
- **ErrorContext**: Context for detailed error reporting
- **ErrorHandler**: Handles and processes errors
- **RetryPolicy**: Implements retry logic for failed operations

### **Performance**
- **PerformanceMonitor**: Monitors system performance
- **PerformanceTracker**: Tracks operation performance
- **TokenUsage**: Tracks token usage for agents and operations

## Data Structures

### **Messages**
- **RequestMessage**: Messages for requesting operations
- **ResponseMessage**: Messages for responding to requests
- **NotificationMessage**: Messages for notifications
- **HeartbeatMessage**: Messages for health checks

### **Artifacts**
- **Artifact**: Data artifacts generated by agents
- **ArtifactManager**: Manages artifact storage and retrieval
- **CompressedContext**: Manages compressed context data

## Integration Components

### **External Services**
- **Vertex AI**: Google Cloud AI platform integration
- **Google ADK**: Google Agent Development Kit integration
- **JWT**: JSON Web Token authentication

### **File Management**
- **aiofiles**: Asynchronous file operations
- **aiohttp**: Asynchronous HTTP client/server
- **pathlib**: Path manipulation utilities

## Risk Assessment Components

### **Risk Definitions**
- **RiskSource**: Represents a source of risk definition with metadata, including criteria, source, URL, and last updated timestamp
- **RiskThreshold**: Represents a risk threshold with ADK features, including value, unit, sources, and monitoring capabilities
- **RiskLevel**: Represents a risk level with ADK features, including name, description, thresholds, and metadata
- **RiskType**: Enum for different risk types (TEMPERATURE, PRECIPITATION, WIND, HUMIDITY, AIR_QUALITY) with ADK metadata

### **Authoritative Sources**
- **FEMA Definitions**: Federal Emergency Management Agency risk definitions for flooding, wildfire, extreme storms, and extreme heat
- **ISO Definitions**: Insurance Services Office risk definitions for property evaluation and catastrophe risk assessment
- **WHO Definitions**: World Health Organization definitions for extreme heat and health impacts
- **NOAA Definitions**: National Oceanic and Atmospheric Administration definitions for extreme storms and weather events

**Note**: For detailed criteria and thresholds from these sources, see the [Criteria for Risks](#criteria-for-risks) section (starting at line 678).
- **NOAA Definitions**: National Oceanic and Atmospheric Administration definitions for extreme weather events

### **Risk Severity Levels**
- **LOW**: Minimal risk conditions
- **MODERATE**: Moderate risk conditions requiring attention
- **HIGH**: High risk conditions requiring immediate action
- **EXTREME**: Extreme risk conditions requiring emergency response
- **SUPER_EXTREME**: Super extreme conditions (e.g., frequent 100-year flood levels)

## Nature-Based Solutions

### **Solution Categories**
- **Water Management Solutions**: Wetland restoration, living shorelines, rain gardens, bioswales, stormwater harvesting
- **Urban Infrastructure**: Green roofs, permeable pavement, green streets, green walls, tree canopy expansion
- **Agricultural Solutions**: Climate-smart agricultural practices, community gardens, urban agriculture
- **Coastal/Marine Solutions**: Eelgrass meadow restoration, oyster reef restoration, coral reef restoration, mangrove restoration
- **Land Management**: Forest health management, rangeland management, dryland restoration, slope stabilization

### **Solution Attributes**
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

### **Data Sources**
- **OpenWeather API**: Current weather data and forecasts
- **NOAA SWDI**: Severe Weather Data Inventory for historical weather events
- **NOAA National Hurricane Center**: Hurricane tracking and intensity data
- **USGS**: Geological data, sea level rise projections, and water data
- **National Weather Service**: Extreme weather frequency and duration data
- **FEMA**: Flood risk assessments and mapping
- **EPA**: Water quality and environmental compliance data

### **Enhanced Data Sources**
- **USDA Water Data**: Drought monitoring, crop water requirements, soil survey data
- **State Agency Data**: State-specific water, agricultural, and environmental data
- **Economic Data**: Regional economic indicators, agricultural finance data
- **Infrastructure Data**: Infrastructure resilience, development project data
- **Regulatory Data**: Environmental compliance, Opportunity Zone data

### **Weather Parameters**
- **Temperature**: Current and historical temperature data
- **Humidity**: Relative humidity measurements
- **Wind Speed**: Wind velocity measurements
- **Precipitation**: Rainfall amounts and patterns
- **Weather Conditions**: Current weather state descriptions

### **Risk Analysis Methods**
- **Historical Data Analysis**: Analysis of past weather events and patterns
- **Frequency Analysis**: Assessment of how often extreme events occur
- **Threshold Comparison**: Comparison of current conditions against established risk thresholds
- **Multi-Source Validation**: Cross-validation using multiple data sources

## Frontend Components (Simplified)

### **Core Display Components**
- **ResilienceOptions**: Displays resilience strategies and adaptation options returned by agents
- **ConfidenceLevels**: Displays confidence levels returned by agents
- **ROIDisplay**: Displays ROI and financial metrics calculated by agents
- **LocationHandler**: Handles location input and validation

### **Simplified Components**
- **SimpleFilters**: Basic filtering with 3 filter types (time, risk level, solution type)
- **SimpleSuggestions**: Basic query suggestions (10 general suggestions)
- **SimpleCharts**: Basic chart display for agent data (risk, ROI, timeline)
- **ConsolidatedDashboard**: Main dashboard that combines all simplified components

### **Frontend Responsibilities**
- **Simple Data Display**: Display agent analysis results in clean format
- **Basic User Interactions**: Handle form submissions and user input
- **Export Functionality**: Export results as JSON for integration
- **Loading States**: Show loading indicators during analysis
- **Error Messages**: Display error messages for failed operations

### **Agent Responsibilities (Complex Processing)**
- **Complex Filtering**: Filter data based on user queries and parameters
- **Data Processing**: Process and analyze environmental data
- **Risk Calculations**: Calculate risk levels and confidence scores
- **ROI Analysis**: Calculate financial metrics and returns
- **Recommendation Generation**: Generate actionable recommendations

## User Interface Terms

### **Query Interface**
- **Natural Language Input**: Users can ask questions in plain English
- **Location Specification**: Enter specific locations (city, county, coordinates)
- **Time Range Selection**: Choose 5, 7, or 10 year analysis periods
- **Query Suggestions**: Pre-written example queries for guidance

### **Results Display**
- **Risk Assessment Card**: Shows overall risk level and breakdown by risk type
- **Resilience Options**: Lists adaptation strategies with costs and ROI
- **Confidence Display**: Shows confidence levels for analysis results
- **ROI Analysis**: Displays financial impact and return metrics
- **Recommendations**: Lists specific actions to take

### **Data Visualization**
- **Risk Assessment Chart**: Simple chart showing risk levels by category
- **ROI Comparison Chart**: Chart comparing returns on different solutions
- **Timeline Chart**: Chart showing risk progression over time

### **Export and Integration**
- **JSON Export**: Download complete analysis results in JSON format
- **Integration Ready**: Data format designed for financial modeling tools
- **API Access**: Programmatic access to analysis results

## Performance Terms

### **ADK Features**
- **Definition**: Google ADK (Agent Development Kit) features (see [ADK (Agent Development Kit)](#adk-agent-development-kit) section above for detailed definition)
- **Components**: MetricsCollector, CircuitBreaker, WorkerPool, Monitoring, Buffer
- **Purpose**: Performance monitoring and system reliability
- **Implementation**: `src/multi_agent_system/utils/adk_features.py`

### **Performance Monitoring**
- **Definition**: Real-time system performance tracking
- **Metrics**: Response times, throughput, error rates, resource usage
- **Purpose**: System optimization and reliability
- **Implementation**: `src/multi_agent_system/performance/`

### **Load Testing**
- **Definition**: Testing system performance under load
- **Purpose**: Validate scalability and performance requirements
- **Implementation**: `src/multi_agent_system/performance/load_testing.py`

## Development Terms

### **Phase 5 Implementation**
- **Definition**: Advanced system enhancement and production readiness
- **Components**: Performance optimization, security enhancement, comprehensive testing
- **Purpose**: Production deployment preparation
- **Implementation**: `phase5_implementation.py`

### **Engineering Roadmap**
- **Definition**: Technical implementation plan across phases
- **Phases**: 1 (A2A/ADK), 2 (Google Cloud), 3 (Performance), 4 (Production), 5 (Advanced)
- **Purpose**: Structured development approach
- **Documentation**: `docs/Engineering_Roadmap.md`

### **PRD (Product Requirements Document)**
- **Definition**: Product requirements and specifications
- **Purpose**: Define system capabilities and user needs
- **Components**: User journeys, technical requirements, delivery model
- **Documentation**: `docs/PRD.md`

## Adaptation and Resilience Terms

### **Strategy Types**
- **Nature-Based Solutions**: Ecosystem-based adaptation approaches
- **Infrastructure Solutions**: Engineering-based adaptation approaches
- **Operational Solutions**: Process and management-based approaches

### **Success Metrics**
- **ROI**: Return on Investment percentage
- **NPV**: Net Present Value calculations
- **IRR**: Internal Rate of Return
- **Payback Period**: Time to recover investment costs

## Data Sources and Attribution

### **Primary Data Sources**
- **NOAA**: National Oceanic and Atmospheric Administration
- **FEMA**: Federal Emergency Management Agency
- **WHO**: World Health Organization
- **ISO**: Insurance Services Office

### **Data Quality Indicators**
- **High Confidence**: Multiple authoritative sources agree
- **Medium Confidence**: Single authoritative source or multiple non-authoritative sources
- **Low Confidence**: Limited or uncertain data availability

## Value Propositions

### **Quantified Benefits**
- **20% improvement in risk-adjusted returns** (Private Equity Investors)
- **20% reduction in extreme weather-related loan defaults** (Loan Officers)
- **15% improvement in portfolio risk-adjusted returns** (Chief Risk Officers)
- **10% improvement in loss ratios** (Crop Insurance Officers)

### **Economic Impact Metrics**
- **ROI Calculations**: 15-35% ROI over 5-7 years for nature-based solutions
- **Cost Reduction**: 15-30% reduction in operational costs
- **Risk Reduction**: 20-40% reduction in extreme weather-related losses
- **Efficiency Gains**: 15-25% improvement in decision-making efficiency

## Communication Guidelines

### **User-Facing Language**
- Use clear, non-technical language when possible
- Provide context for technical terms when used
- Focus on actionable insights and practical recommendations
- Emphasize external data and expert sources

### **Professional Terminology**
- Use industry-standard terms for each user type
- Maintain consistency across all communications
- Provide definitions for specialized terms
- Use appropriate formality level for each user type

## Compliance and Regulatory Terms

### **Regulatory Frameworks**
- **ESG Compliance**: Environmental, Social, and Governance requirements
- **Regulatory Reporting**: Required reporting for financial institutions
- **Capital Allocation**: Regulatory capital requirements and optimization
- **Risk Disclosure**: Required risk disclosure for stakeholders

### **Industry Standards**
- **ISO Standards**: International Organization for Standardization guidelines
- **FEMA Guidelines**: Federal Emergency Management Agency standards
- **WHO Recommendations**: World Health Organization health guidelines
- **NOAA Protocols**: National Oceanic and Atmospheric Administration procedures

## System Status and Health

### **Operational Terms**
- **System Health**: Overall system performance and availability
- **Agent Status**: Individual agent operational status
- **Data Availability**: Current data source accessibility
- **Processing Status**: Analysis and computation progress

### **Error Handling**
- **Graceful Degradation**: System continues operating with reduced functionality
- **Fallback Analysis**: Alternative analysis when primary methods fail
- **Error Recovery**: Automatic recovery from system errors
- **User Guidance**: Helpful error messages and resolution suggestions

## Technical Infrastructure

### **FastAPI**
- **Definition**: Modern Python web framework
- **Purpose**: API development and web interface
- **Usage**: Both `app.py` and `src/pythia_web/interface.py`

### **SQLite**
- **Definition**: Lightweight database for metadata storage
- **Purpose**: Artifact metadata and session data
- **Location**: `artifacts.db`

### **JSON**
- **Definition**: Data format for configuration and communication
- **Purpose**: Agent messages, session data, configuration
- **Usage**: Throughout the system for data exchange

### **Gitignore**
- **Definition**: Git configuration for excluding files
- **Purpose**: Prevent sensitive or development files from version control
- **Files**: UX mockups, web interface, development configurations

## Financial Terms

### **IRR (Internal Rate of Return)**
- **Definition**: Financial metric for investment performance
- **Purpose**: Evaluate investment profitability
- **Application**: Extreme weather resilience investment analysis

### **ROI (Return on Investment)**
- **Definition**: Financial return relative to investment cost
- **Purpose**: Assess investment effectiveness
- **Application**: Adaptation strategy evaluation

### **Collateral Value**
- **Definition**: Asset value used as loan security
- **Purpose**: Risk assessment and loan valuation
- **Impact**: Affected by extreme weather events

## Criteria for Risks

This section documents the standardized risk criteria and thresholds used by Pythia for risk assessment. These definitions are derived from authoritative sources including FEMA (Federal Emergency Management Agency), ISO (Insurance Services Office), WHO (World Health Organization), and NOAA (National Oceanic and Atmospheric Administration).

**Source**: Definitions are implemented in [`risk_definitions.py`](../../risk_definitions.py) and [`src/multi_agent_system/risk_definitions.py`](../../src/multi_agent_system/risk_definitions.py).

### **Flooding Risk Criteria**

#### **FEMA Definitions**
- **High Severity**: Flash flood warning issued or > 50mm rainfall in 1 hour
  - **Source**: FEMA Flood Hazard Mapping
  - **URL**: https://www.fema.gov/flood-maps
- **Medium Severity**: Flood watch issued or > 20mm rainfall in 1 hour
  - **Source**: FEMA Flood Hazard Mapping
  - **URL**: https://www.fema.gov/flood-maps

#### **ISO Definitions**
- **High Severity**: 100-year floodplain or > 40mm rainfall in 1 hour
  - **Source**: ISO Property Evaluation Schedule
  - **URL**: https://www.iso.com/
- **Medium Severity**: 500-year floodplain or > 25mm rainfall in 1 hour
  - **Source**: ISO Property Evaluation Schedule
  - **URL**: https://www.iso.com/

#### **Consensus Thresholds**
- **High Severity**: > 50mm rainfall in 1 hour
  - **Sources**: FEMA, ISO
- **Medium Severity**: > 25mm rainfall in 1 hour
  - **Sources**: FEMA, ISO

### **Wildfire Risk Criteria**

#### **FEMA Definitions**
- **High Severity**: Red Flag Warning issued or Fire Weather Watch with relative humidity < 20% and winds > 30 mph
  - **Source**: FEMA Wildfire Risk to Communities
  - **URL**: https://wildfirerisk.org/
- **Medium Severity**: Elevated fire weather conditions with relative humidity < 30% and winds > 20 mph
  - **Source**: FEMA Wildfire Risk to Communities
  - **URL**: https://wildfirerisk.org/

#### **ISO Definitions**
- **High Severity**: ISO Wildfire Risk Score > 80 or relative humidity < 25% with winds > 25 mph
  - **Source**: ISO Wildfire Risk Assessment
  - **URL**: https://www.iso.com/
- **Medium Severity**: ISO Wildfire Risk Score > 60 or relative humidity < 35% with winds > 20 mph
  - **Source**: ISO Wildfire Risk Assessment
  - **URL**: https://www.iso.com/

#### **Consensus Thresholds**
- **High Severity**: Temperature > 35°C, relative humidity < 30%, wind speed > 30 km/h
  - **Sources**: FEMA
- **Medium Severity**: Temperature > 30°C, relative humidity < 40%, wind speed > 20 km/h
  - **Sources**: ISO

### **Extreme Storms Risk Criteria**

#### **FEMA Definitions**
- **High Severity**: Severe Thunderstorm Warning issued or wind speeds > 58 mph
  - **Source**: National Weather Service
  - **URL**: https://www.weather.gov/safety/thunderstorm
- **Medium Severity**: Severe Thunderstorm Watch issued or wind speeds > 40 mph
  - **Source**: National Weather Service
  - **URL**: https://www.weather.gov/safety/thunderstorm

#### **ISO Definitions**
- **High Severity**: Hail > 1 inch or wind speeds > 50 mph
  - **Source**: ISO Catastrophe Risk Evaluation
  - **URL**: https://www.iso.com/
- **Medium Severity**: Hail > 0.75 inch or wind speeds > 40 mph
  - **Source**: ISO Catastrophe Risk Evaluation
  - **URL**: https://www.iso.com/

#### **NOAA Definitions**
- **High Severity**: Severe Thunderstorm Warning or wind speeds > 58 mph
  - **Source**: NOAA Storm Prediction Center
  - **URL**: https://www.spc.noaa.gov/
- **Medium Severity**: Severe Thunderstorm Watch or wind speeds > 40 mph
  - **Source**: NOAA Storm Prediction Center
  - **URL**: https://www.spc.noaa.gov/

#### **Consensus Thresholds**
- **High Severity**: Wind speed > 120 km/h
  - **Sources**: NOAA
- **Medium Severity**: Wind speed > 80 km/h
  - **Sources**: ISO

### **Extreme Heat Risk Criteria**

#### **FEMA Definitions**
- **High Severity**: Excessive Heat Warning issued or heat index > 105°F (40.6°C)
  - **Source**: National Weather Service
  - **URL**: https://www.weather.gov/safety/heat
- **Medium Severity**: Heat Advisory issued or heat index > 100°F (37.8°C)
  - **Source**: National Weather Service
  - **URL**: https://www.weather.gov/safety/heat

#### **ISO Definitions**
- **High Severity**: Temperature > 100°F (37.8°C) for 3+ consecutive days
  - **Source**: ISO Catastrophe Risk Evaluation
  - **URL**: https://www.iso.com/
- **Medium Severity**: Temperature > 95°F (35°C) for 3+ consecutive days
  - **Source**: ISO Catastrophe Risk Evaluation
  - **URL**: https://www.iso.com/

#### **WHO Definitions**
- **High Severity**: Temperature > 40°C or heat index > 54°C
  - **Source**: WHO Heat Health Action Plans
  - **URL**: https://www.who.int/health-topics/heatwaves
- **Medium Severity**: Temperature > 35°C or heat index > 41°C
  - **Source**: WHO Heat Health Action Plans
  - **URL**: https://www.who.int/health-topics/heatwaves

#### **Consensus Thresholds**
- **High Severity**: Temperature > 35°C
  - **Sources**: WHO, FEMA
- **Medium Severity**: Temperature > 30°C
  - **Sources**: ISO

### **Risk Severity Levels**

The system uses the following severity levels for risk assessment:
- **Low**: Below medium threshold
- **Moderate**: Meets medium threshold criteria
- **High**: Meets high threshold criteria
- **Extreme**: Exceeds high threshold significantly
- **Super Extreme**: For cases like frequent 100-year flood levels

---

**Last Updated**: December 12, 2025
**Version**: 1.0
**Status**: Complete terminology documentation based on system implementation
**Next Review**: February 2025

## Change Log

### **December 12, 2025**
- **New Section Added**: Added "Criteria for Risks" section (starting at line 678) documenting standardized risk criteria and thresholds from FEMA, ISO, WHO, and NOAA sources
- **Risk Definitions**: Extracted and documented risk criteria for flooding, wildfire, extreme storms, and extreme heat from `risk_definitions.py`

For a complete history of all changes, improvements, and fixes, see [00_CHANGELOG.md](../b_CHANGE_LOG/00_CHANGELOG.md).

---

## Related Documentation
- [1.3_System_Do_Not_Dos.md](../_Cursor/1.3_System_Do_Not_Dos.md) - Guidelines for what not to do
- [0.4_DRAFT_DNU_user_personas.md](0.4_DRAFT_DNU_user_personas.md) - Detailed user persona definitions
- [0.5_DRAFT_DNU_User_Stories.md](0.5_DRAFT_DNU_User_Stories.md) - User story documentation
- [risk_definitions.py](../src/multi_agent_system/risk_definitions.py) - Technical risk definitions
- [Criteria for Risks](#criteria-for-risks) - Standardized risk criteria and thresholds (see section starting at line 678)
- [prototypes.md](prototypes.md) - Geographic prototype definitions