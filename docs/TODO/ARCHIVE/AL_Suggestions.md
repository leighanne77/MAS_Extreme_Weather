# Alabama Prototype Project Files - Reuse Analysis & Suggestions

**Date Created**: December 12, 2025  
**Date Last Updated**: December 14, 2025  
**Prototype**: Mobile Bay, Alabama - Private Equity Investor  
**Location**: Moved from `docs/3-EXPERIMENTS/0.6_Alabama/` to `docs/TODO/` and renamed to `AL_Suggestions.md`

## Overview

This document analyzes the Alabama prototype requirements against existing `src/` files to identify:
1. **Files that can be REUSED** (no new files needed)
2. **Files that need ENHANCEMENT** (extend existing files)
3. **Files that need to be CREATED** (new functionality required)
4. **Additional agents needed**
5. **Additional MCP/API integrations needed**

---

## ✅ FILES THAT CAN BE REUSED (No Changes Needed)

### **Core Agent Files** ✅
All existing agents can be reused as-is:
- `src/multi_agent_system/agents/base_agent.py` - Base agent class with ADK features
- `src/multi_agent_system/agents/risk_agent.py` - Risk analysis agent (handles hurricanes, heat, flooding)
- `src/multi_agent_system/agents/historical_agent.py` - Historical weather event analysis
- `src/multi_agent_system/agents/recommendation_agent.py` - Risk mitigation strategy recommendations
- `src/multi_agent_system/agents/validation_agent.py` - Cross-validation of risk assessments
- `src/multi_agent_system/agents/greeting_agent.py` - User onboarding
- `src/multi_agent_system/agents/farewell_agent.py` - Session closure
- `src/multi_agent_system/agents/news_agent.py` - News and information agent
- `src/multi_agent_system/agents/cards.py` - Agent card definitions
- `src/multi_agent_system/agents/tools.py` - Agent tools for risk analysis

**Rationale**: These agents are already designed to handle extreme weather risk analysis and can be configured for the Alabama prototype through configuration files.

### **A2A Communication Files** ✅
All A2A protocol files exist and can be reused:
- `src/multi_agent_system/a2a/message.py` - A2A message structure
- `src/multi_agent_system/a2a/multipart.py` - Multi-part message handling
- `src/multi_agent_system/a2a/parts.py` - Message parts
- `src/multi_agent_system/a2a/artifacts.py` - Artifact management
- `src/multi_agent_system/a2a/artifact_manager.py` - Artifact management utilities
- `src/multi_agent_system/a2a/router.py` - Message routing
- `src/multi_agent_system/a2a/task_manager.py` - Task management
- `src/multi_agent_system/a2a/content_handlers.py` - Content handling utilities
- `src/multi_agent_system/a2a/enums.py` - A2A enums and constants

**Rationale**: A2A protocol is prototype-agnostic and fully implemented.

### **Core System Files** ✅
Core infrastructure files exist and can be reused:
- `src/multi_agent_system/agent_team.py` - Agent team coordination
- `src/multi_agent_system/coordinator.py` - Coordinator agent
- `src/multi_agent_system/session_manager.py` - Session management
- `src/multi_agent_system/data_management.py` - Data source management
- `src/multi_agent_system/weather_risks.py` - Extreme weather risk analyzer
- `src/multi_agent_system/risk_definitions.py` - Risk thresholds and criteria
- `src/multi_agent_system/observability.py` - Monitoring and logging
- `src/multi_agent_system/communication.py` - Agent communication manager
- `src/multi_agent_system/config.py` - Configuration management
- `src/multi_agent_system/adk_integration.py` - ADK integration utilities
- `src/multi_agent_system/artifact_manager.py` - Artifact management
- `src/multi_agent_system/performance/` - Performance monitoring (all files)
- `src/multi_agent_system/utils/` - Utility functions
- `src/multi_agent_system/workflows/` - Workflow definitions

**Rationale**: Core system infrastructure is prototype-agnostic.

### **Data Source Base Files** ✅
Base data source infrastructure exists:
- `src/multi_agent_system/data/data_source.py` - Base data source class
- `src/multi_agent_system/data/data_sources.py` - Base data source classes
- `src/multi_agent_system/data/data_loader.py` - Data loading utilities
- `src/multi_agent_system/data/weather_data.py` - NOAA weather data integration
- `src/multi_agent_system/data/cmr_mcp.py` - NASA CMR MCP server integration ✅
- `src/multi_agent_system/data/enhanced_data_sources.py` - Enhanced data source manager (includes Federal Reserve regional data)
- `src/multi_agent_system/data/nature_based_solutions_source.py` - Nature-first resiliency options

**Rationale**: Base data source infrastructure is reusable.

### **Curated Data Files (JSON)** ✅
Existing JSON data files can be reused:
- `src/multi_agent_system/data/nature_based_solutions.json` - Nature-based solutions database with case studies
- `src/multi_agent_system/data/Biodiversity_Credit_Revenue_Streams.json` - Biodiversity credit revenue stream guidance
- `src/multi_agent_system/data/funding_sources_NSB.json` - Funding sources for nature-based solutions
- `src/multi_agent_system/data/historical_weather_events.json` - Historical weather event data
- `src/multi_agent_system/data/economic_impact_data.json` - Economic impact data
- `src/multi_agent_system/data/regional_risk_profiles.json` - Regional risk profiles

**Rationale**: These JSON files are already populated with relevant data and can be extended with geography-specific entries (Alabama, Philippines, Tamil Nadu, etc.).

---

## 🔄 FILES THAT NEED ENHANCEMENT (Extend Existing Files)

### **1. Enhanced Data Sources** 🔄
**File**: `src/multi_agent_system/data/enhanced_data_sources.py`

**Current State**: Contains `EconomicData`, `InfrastructureData`, `RegulatoryData`, `USDAWaterData`, `StateAgencyData` classes.

**Enhancements Needed**:
1. **Add Local-Specific Government Data Methods** (Generic for all states/locations):
   - `get_state_environmental_data(state: str)` - State Department of Environmental Management/Protection data (e.g., ADEM for Alabama, EPA state equivalents)
   - `get_state_commerce_data(state: str)` - State Department of Commerce/Economic Development data
   - `get_state_transportation_data(state: str)` - State Department of Transportation data
   - `get_state_emergency_mgmt_data(state: str)` - State Emergency Management data
   - `get_local_government_data(location: str, agency_type: str)` - Generic method for local/municipal government data

2. **Add Opportunity Zone Data Methods**:
   - `get_opportunity_zone_data(census_tract: str)` - Opportunity Zone designation data
   - `get_qof_investment_trends()` - Qualified Opportunity Fund investment trends
   - `get_oz_compliance_data()` - Opportunity Zone compliance requirements

3. **Add Manufacturing/Infrastructure-Specific Methods**:
   - `get_manufacturing_facility_risk_data(location: str, facility_type: str)` - Manufacturing facility risk profiles
   - `get_shipbuilding_industry_data()` - Shipbuilding industry-specific data
   - `get_construction_cost_data(location: str, facility_type: str)` - Construction cost estimates

**Implementation Approach**: Add new generic methods to existing `StateAgencyData` class (which already exists in `enhanced_data_sources.py`) that accept state/location parameters. This allows reuse across all prototypes (Alabama, India, etc.). The methods should handle state-specific API endpoints and data formats through configuration.

**Reference**: See `docs/2-DATA/2.1_First_Data_Sources.md` for data source requirements. Note: `StateAgencyData` class already exists in `enhanced_data_sources.py` - enhance it with these generic methods.

---

### **2. Risk Agent** 🔄
**File**: `src/multi_agent_system/agents/risk_agent.py`

**Enhancements Needed**:
1. **Add Generic Coastal Risk Analysis Tools** (Geography-agnostic, works for any coastal area):
   - `analyze_tropical_cyclone_risk(location: str, geography: str, time_horizon: str)` - Generic tropical cyclone/hurricane/typhoon risk analysis (works for Mobile Bay, Alabama; Philippines; Tamil Nadu, India; and any coastal area with cyclone/hurricane risk)
   - `analyze_storm_surge_risk(location: str, geography: str)` - Generic storm surge risk analysis for any coastal geography
   - `analyze_coastal_erosion_risk(location: str, geography: str)` - Generic coastal erosion risk analysis for any coastal geography
   - `analyze_extreme_heat_risk(location: str, geography: str, facility_type: str)` - Generic extreme heat impact analysis (works for manufacturing, agriculture, or other facility types)
   
   **Note**: The system should prompt for `geography` parameter to identify the region (e.g., "mobile_bay_alabama", "philippines", "tamil_nadu_india") which determines data sources, risk thresholds, and historical patterns to use.

2. **Add Exit Value Impact Analysis**:
   - `analyze_exit_value_impact(risk_assessment: dict, exit_timeline: str)` - Exit value impact analysis for specified timeline (generic, works for any exit timeline)

**Implementation Approach**: Add new generic tool methods to `RiskAnalyzerAgent` class that accept a `geography` parameter. The geography parameter determines:
- Which data sources to use (NOAA for US, IMD for India, PAGASA for Philippines, etc.)
- Which risk thresholds to apply (region-specific historical patterns)
- Which historical event databases to query
- Which terminology to use (hurricane vs. cyclone vs. typhoon)

The methods should use configuration files or data source routing to select appropriate data sources based on geography, making them reusable across all coastal prototypes.

**Reference**: See `docs/3-EXPERIMENTS/0.6_Alabama/0.61_AL_CapZone_Manu_Shipyard_User_Story_Journey_Data_Needs/0.61_AL_CapZone_Manu_Shipyard_User_Story_Journey_Data_Needs.md` for user journey requirements. Also see `docs/2-DATA/2.1_First_Data_Sources.md` for geography-specific data source requirements.

---

### **3. Recommendation Agent** 🔄
**File**: `src/multi_agent_system/agents/recommendation_agent.py`

**Enhancements Needed**:
1. **Add Generic Investor Recommendations** (Works for all investor types):
   - `generate_investor_recommendations(risk_assessment: dict, investment_timeline: str, investor_type: str)` - Generic investor recommendations (works for Private Equity, Private Debt, etc.)
   - `generate_qoz_recommendations(risk_assessment: dict, investment_timeline: str, census_tract: str)` - Opportunity Zone-specific recommendations and compliance guidance
   - `prioritize_nature_based_solutions_for_exit_value(risk_types: list, exit_timeline: str)` - Nature-based solutions prioritized for exit value enhancement
   - `calculate_roi_framework_for_mitigations(mitigation_strategies: list, property_value: float)` - ROI analysis frameworks (no guarantees)

2. **Add Success Story Integration**:
   - `find_similar_successful_investments(location: str, facility_type: str, geography: str)` - Find similar successful investments in similar geographies
   - `get_peer_comparison_data(location: str, investment_type: str)` - Peer comparison data

**Implementation Approach**: Add new tool methods to `RecommendationAgent` class.

**Reference**: See user journey document for success story integration requirements.

---

### **4. Historical Agent** 🔄
**File**: `src/multi_agent_system/agents/historical_agent.py`

**Enhancements Needed**:
1. **Add Generic Coastal Historical Data Methods** (Geography-agnostic):
   - `get_tropical_cyclone_history(location: str, geography: str, years: int)` - Generic historical tropical cyclone/hurricane/typhoon data (works for any coastal area: Mobile Bay, Alabama; Philippines; Tamil Nadu, India; etc.)
   - `get_coastal_storm_surge_history(location: str, geography: str)` - Generic historical coastal storm surge data for any coastal geography
   - `get_coastal_erosion_history(location: str, geography: str)` - Generic historical coastal erosion data for any coastal geography
   
   **Note**: The `geography` parameter determines which data sources to query (NOAA for US, IMD for India, PAGASA for Philippines, etc.) and which historical databases to access.

**Implementation Approach**: Extend existing historical analysis methods with geography-agnostic parameters. Use data source routing based on geography to select appropriate historical databases and APIs. This makes the methods reusable across all coastal prototypes.

---

### **5. Nature-Based Solutions Source** 🔄
**File**: `src/multi_agent_system/data/nature_based_solutions_source.py`

**Enhancements Needed**:
1. **Add Geography-Based Filtering** (Generic for all locations):
   - Filter solutions by geography tag (e.g., `"mobile_bay_alabama"`, `"philippines"`, `"tamil_nadu_india"`)
   - Prioritize solutions with geography-specific case studies
   - Filter by facility/industry type compatibility (manufacturing, agriculture, etc.)
   - Filter by risk type (hurricane/cyclone/typhoon, storm surge, coastal erosion, etc.)
   
   **Note**: The system should accept a `geography` parameter to determine which solutions to prioritize. The `nature_based_solutions.json` file already contains case studies from multiple geographies, so this is primarily filtering and prioritization logic.

**Implementation Approach**: Add generic filtering methods that accept `geography`, `risk_types`, and `facility_type` parameters. The methods should check JSON data for geography tags, case studies, and compatibility indicators. This makes the filtering reusable across all prototypes.

---

## 🆕 FILES THAT NEED TO BE CREATED (New Functionality)

### **1. MCP Server Integration Files** 🆕 #TO_DO

> **🚀 IMPORTANT UPDATE - Google's Managed MCP Servers**: As of December 10, 2025, Google has announced [fully-managed, remote MCP servers](https://cloud.google.com/blog/products/ai-machine-learning/announcing-official-mcp-support-for-google-services) that provide a unified layer across all Google and Google Cloud services. Instead of installing and managing individual MCP servers locally, we can now leverage Google's globally-consistent and enterprise-ready endpoints. See section **1.0. Google Managed MCP Servers** below for details on how to leverage these new capabilities.

#### **1.0. Google Managed MCP Servers** 🆕 **RECOMMENDED APPROACH**

**Reference**: [Google Cloud Blog - Official MCP Support for Google Services](https://cloud.google.com/blog/products/ai-machine-learning/announcing-official-mcp-support-for-google-services)

**Available Now**:
1. **Google Maps Grounding Lite MCP Server** - ✅ **HIGH PRIORITY**
   - **Purpose**: Geospatial data, places, weather forecasts, routing (distance, travel time)
   - **Use Case**: Location validation, weather queries, routing analysis for investment locations
   - **Implementation**: Point agents to Google's managed MCP endpoint for Maps Platform
   - **Benefits**: No local installation, enterprise-ready, globally consistent
   - **File**: `src/multi_agent_system/data/google_maps_mcp.py` (wrapper for Google's managed endpoint)

2. **BigQuery MCP Server** - ✅ **HIGH PRIORITY**
   - **Purpose**: Native schema interpretation and query execution against enterprise data
   - **Use Case**: Economic data analysis, forecasting, data aggregation for risk assessment
   - **Implementation**: Point agents to Google's managed MCP endpoint for BigQuery
   - **Benefits**: Data remains in-place and governed, direct access to BigQuery features
   - **File**: `src/multi_agent_system/data/google_bigquery_mcp.py` (wrapper for Google's managed endpoint)

3. **Google Compute Engine (GCE) MCP Server** - 🔄 **MEDIUM PRIORITY**
   - **Purpose**: Autonomous infrastructure management (provisioning, resizing)
   - **Use Case**: Infrastructure scaling for data processing workloads
   - **Implementation**: Point agents to Google's managed MCP endpoint for GCE
   - **File**: `src/multi_agent_system/data/google_gce_mcp.py` (wrapper for Google's managed endpoint)

4. **Google Kubernetes Engine (GKE) MCP Server** - 🔄 **MEDIUM PRIORITY**
   - **Purpose**: Autonomous container operations, structured Kubernetes API interface
   - **Use Case**: Container orchestration for multi-agent system deployment
   - **Implementation**: Point agents to Google's managed MCP endpoint for GKE
   - **File**: `src/multi_agent_system/data/google_gke_mcp.py` (wrapper for Google's managed endpoint)

**Coming Soon** (Next Few Months):
- **Cloud Run, Cloud Storage, Cloud Resource Manager** - Infrastructure management
- **AlloyDB, Cloud SQL, Spanner** - Database access
- **Pub/Sub, Dataplex Universal Catalog** - Data pipeline and catalog access
- **Cloud Logging, Cloud Monitoring** - Observability
- **Looker** - Analytics and reporting

**Implementation Strategy**:
1. **Use Google's Managed Endpoints**: Instead of installing local MCP servers, create wrapper modules that connect to Google's managed MCP endpoints
2. **Leverage Cloud API Registry**: Use Google's Cloud API Registry to discover trusted MCP tools
3. **Access Control**: Use Google Cloud IAM for access management
4. **Observability**: Leverage built-in audit logging and Google Cloud Model Armor for security
5. **Apigee Integration**: For enterprise customers, leverage Apigee API Hub to expose custom APIs as MCP tools

**Benefits Over Local MCP Servers**:
- ✅ No local installation or management burden
- ✅ Globally consistent, enterprise-ready endpoints
- ✅ Built-in security and observability
- ✅ Unified discovery through Cloud API Registry
- ✅ Automatic updates and maintenance by Google
- ✅ Reduced implementation complexity

**Migration Path**:
- Phase 1: Implement Google Maps and BigQuery MCP servers (highest priority for prototype)
- Phase 2: Evaluate other Google managed MCP servers as they become available
- Phase 3: Consider migrating from local MCP servers to Google managed endpoints where available

---

#### **1.1. ERDDAP MCP Server** 🆕
**File**: `src/multi_agent_system/data/erddap_mcp.py`

**Purpose**: Oceanographic and environmental data consolidation for coastal prototypes.

**Implementation**:
- **Option A (Recommended)**: If ERDDAP data becomes available through Google's managed MCP servers, use Google's endpoint
- **Option B**: Install: `pip install erddap-mcp-server` (or use existing MCP client) for local/community MCP server
- Configure ERDDAP MCP server endpoint
- Add to data source registry in `data_management.py`

**Priority**: HIGH - Important for coastal data (storm surge, water quality, oceanographic data)

**Note**: Check if ERDDAP data can be accessed through Google's Dataplex Universal Catalog MCP server (coming soon) before implementing local server.

**Agent Processing**: `EnvironmentalDataAgent` handles ERDDAP data collection

**Reference**: `docs/2-DATA/2.1_First_Data_Sources.md` - ERDDAP MCP Server section

---

#### **1.2. Data.gov MCP Server** 🆕
**File**: `src/multi_agent_system/data/datagov_mcp.py`

**Purpose**: Government dataset consolidation for all prototypes.

**Implementation**:
- **Option A (Recommended)**: Evaluate if Data.gov datasets can be accessed through Google's managed MCP servers or Apigee API Hub
- **Option B**: Install: `pip install datagov-mcp-server` (or use existing MCP client) for local/community MCP server
- Configure Data.gov MCP server endpoint
- Add to data source registry in `data_management.py`

**Priority**: MEDIUM - Consolidates multiple government data sources

**Note**: Consider leveraging Apigee API Hub to expose Data.gov APIs as MCP tools for enterprise customers.

**Agent Processing**: Multiple agents can use Data.gov data

**Reference**: `docs/2-DATA/2.1_First_Data_Sources.md` - Data.gov MCP Server section

---

#### **1.3. USGS MCP Server** 🆕
**File**: `src/multi_agent_system/data/usgs_mcp.py`

**Purpose**: Geological and hydrological data access (storm surge modeling, coastal erosion).

**Implementation**:
- Install: `pip install usgs-mcp-server` (or use existing MCP client)
- Configure USGS API credentials
- Add to data source registry in `data_management.py`

**Priority**: HIGH - Essential for storm surge modeling and coastal erosion data

**Agent Processing**: `InfrastructureDataAgent` handles USGS data collection

**Reference**: `docs/2-DATA/2.1_First_Data_Sources.md` - USGS MCP Server section

---

#### **1.4. EPA MCP Server** 🆕
**File**: `src/multi_agent_system/data/epa_mcp.py`

**Purpose**: Environmental protection data (water quality, air quality, compliance).

**Implementation**:
- Install: `pip install epa-mcp-server` (or use existing MCP client)
- Configure EPA data access credentials
- Add to data source registry in `data_management.py`

**Priority**: MEDIUM - Important for water quality monitoring (red tide, water quality)

**Agent Processing**: `EnvironmentalDataAgent` handles EPA data collection

**Reference**: `docs/2-DATA/2.1_First_Data_Sources.md` - EPA MCP Server section

---

#### **1.5. NOAA MCP Server** 🆕
**File**: `src/multi_agent_system/data/noaa_mcp.py`

**Purpose**: Weather, climate, and oceanographic data (beyond existing NOAA SWDI integration).

**Implementation**:
- Install: `pip install noaa-mcp-server` (or use existing MCP client)
- Configure NOAA API keys
- Add to data source registry in `data_management.py`

**Priority**: HIGH - Essential for weather and climate data (complements existing NOAA SWDI)

**Agent Processing**: `RiskAnalyzerAgent` handles NOAA data collection

**Reference**: `docs/2-DATA/2.1_First_Data_Sources.md` - NOAA MCP Server section

---

#### **1.6. Census Bureau MCP Server** 🆕
**File**: `src/multi_agent_system/data/census_mcp.py`

**Purpose**: Census data (Opportunity Zone census tract data, demographic data).

**Implementation**:
- Install: `pip install census-mcp-server` (or use existing MCP client)
- Configure Census API credentials
- Add to data source registry in `data_management.py`

**Priority**: MEDIUM - Important for Opportunity Zone census tract data

**Agent Processing**: `EconomicDataAgent` handles Census data collection

**Reference**: `docs/2-DATA/2.1_First_Data_Sources.md` - Census Bureau MCP Server section

---

### **2. Direct API Integration Files** 🆕 #TO_DO

#### **2.1. FRED API Integration** 🆕
**File**: `src/multi_agent_system/data/fred_api.py`

**Purpose**: Federal Reserve Economic Data (FRED) API for economic indicators.

**Implementation**:
- Use `fredapi>=0.5.0` (already in requirements.txt)
- Create `FREDDataSource` class inheriting from `DataSource`
- Add methods for:
  - `get_economic_indicators(location: str, indicators: list)`
  - `get_regional_economic_data(state: str)`
  - `get_irr_calculation_data()` - Data for IRR calculations (not IRR calculations themselves)

**Priority**: HIGH - Essential for economic data and IRR calculation support data

**Agent Processing**: `EconomicDataAgent` handles FRED data collection

**Reference**: `docs/2-DATA/2.1_First_Data_Sources.md` - FRED API section

---

#### **2.2. Opportunity Zone API Integration** 🆕
**File**: `src/multi_agent_system/data/opportunity_zone_api.py` OR enhance existing `RegulatoryData` class

**Purpose**: All Opportunity Zone data (8,764 zones across 50 states + 5 U.S. possessions) - census tract designations, QOF data, investment trends.

**Existing Functionality in `src/`**:
- ✅ `src/multi_agent_system/data/enhanced_data_sources.py` - `RegulatoryData` class has `get_opportunity_zone_data(state: str)` method (line 402)
- ✅ `src/multi_agent_system/agents/tools.py` - `get_regulatory_data_tool()` includes QOZ data (line 527-530)
- ✅ `src/multi_agent_system/data/funding_sources_NSB.json` - Contains Opportunity Zone funding sources (lines 205-272)

**Implementation Options**:
- **Option A (Recommended)**: Enhance existing `RegulatoryData.get_opportunity_zone_data()` in `enhanced_data_sources.py`
  - Add API integration to existing method
  - Support all Opportunity Zones (not just Alabama)
  - Change signature to: `get_opportunity_zone_data(census_tract: str = None, state: str = None, region: str = None)`
  - Add methods: `get_oz_designation(census_tract: str)`, `get_qof_data()`, `get_oz_investment_trends()`
- **Option B**: Create separate `OpportunityZoneDataSource` class if more specialized functionality needed

**Data Sources to Integrate**:
- Census Bureau Opportunity Zone data (8,764 designated zones)
- Novogradac QOF Tracking Data (Qualified Opportunity Funds database)
- Novogradac Residential Investment Trends (5 years of QOZ investment patterns)
- Cresa Industrial Impacts Analysis (manufacturing/warehouse QOZ examples)

**Priority**: HIGH - Essential for Private Equity Investor prototype (QOZ specialist)

**Agent Processing**: `EconomicDataAgent` handles Opportunity Zone data collection (via `RegulatoryData` class)

**Do We Need a Separate Opportunity Zone Agent?** ❌ **NO**
- ✅ **Existing `RegulatoryData` class** (`enhanced_data_sources.py`) already has `get_opportunity_zone_data()` method
- ✅ **Existing `recommendation_agent.py`** already has `generate_qoz_recommendations()` method (see section 3.3)
- ✅ **Existing `tools.py`** already integrates OZ data via `get_regulatory_data_tool()`
- ✅ **Existing `EconomicDataAgent`** can handle OZ data collection and processing

**Conclusion**: No separate Opportunity Zone agent needed. Existing agents and data sources can handle all OZ functionality. Just need to enhance `RegulatoryData.get_opportunity_zone_data()` to support all 8,764 zones (not just Alabama) and connect to actual APIs.

**Reference**: `docs/2-DATA/2.1_First_Data_Sources.md` - Opportunity Zone data section

---

#### **2.3. FEMA Flood Maps API** 🆕
**File**: `src/multi_agent_system/data/fema_flood_maps.py`

**Purpose**: FEMA flood maps and flood risk data.

**Implementation**:
- Research FEMA Flood Map Service API
- Create `FEMAFloodMapsDataSource` class inheriting from `DataSource`
- Add methods for:
  - `get_flood_zone(location: str)`
  - `get_flood_risk_assessment(location: str)`

**Priority**: HIGH - Essential for flood risk assessment

**Agent Processing**: `RiskAnalyzerAgent` handles FEMA flood map data collection

**Reference**: `docs/2-DATA/2.1_First_Data_Sources.md` - FEMA Flood Maps section

---

#### **2.4. NOAA Digital Coast API** 🆕
**File**: `src/multi_agent_system/data/noaa_digital_coast.py`

**Purpose**: Coastal erosion data, coastal resilience data.

**Implementation**:
- Research NOAA Digital Coast API
- Create `NOAADigitalCoastDataSource` class inheriting from `DataSource`
- Add methods for:
  - `get_coastal_erosion_data(location: str)`
  - `get_coastal_resilience_data(location: str)`

**Priority**: HIGH - Essential for coastal erosion risk assessment

**Agent Processing**: `InfrastructureDataAgent` handles NOAA Digital Coast data collection

**Reference**: `docs/2-DATA/2.1_First_Data_Sources.md` - Coastal Erosion Data section

---

### **3. Additional Agent Files** 🆕

#### **3.1. Query Refinement Agent** 🆕
**File**: `src/multi_agent_system/agents/query_refinement_agent.py`

**Purpose**: Interactive dialogue to help users refine their initial query into a precise one.

**Functionality**:
- Ask clarifying questions (QOZ status, exit timeline, facility type, location, risks, primary concern)
- Optionally prompt for operational data (Enterprise Edition feature)
- Refine broad queries into specific ones

**Implementation**:
- Create `QueryRefinementAgent` class inheriting from `BaseAgent`
- Add tools:
  - `refine_user_query(initial_query: str, user_type: str) -> dict`
  - `ask_clarifying_questions(query_context: dict) -> list[str]`
  - `check_enterprise_features(user_query: dict) -> dict`

**Reference**: User journey Step 1.2.a in `0.61_AL_CapZone_Manu_Shipyard_User_Story_Journey_Data_Needs.md`

**Priority**: HIGH - Core user journey feature

---

#### **3.2. Multisolving Agent** 🆕
**File**: `src/multi_agent_system/agents/multisolving_agent.py`

**Purpose**: Identify multisolving opportunities AND generate recommendations for how to add more mitigations to create bigger positive impacts on exit values and nature-based solutions.

**Functionality**:
1. **Opportunity Identification**:
   - Ask users if they want to multisolve for additional stakeholder needs (US Navy, Local Fishermen/Oystermen, etc.)
   - Identify multisolving opportunities that address multiple goals simultaneously
   - Identify co-benefits across stakeholders (economic, environmental, social)

2. **Recommendation Generation**:
   - Generate specific recommendations for how to add more mitigations to existing strategies
   - Show how combining mitigations creates bigger positive impacts on exit values
   - Demonstrate how nature-based solutions can address multiple stakeholder needs simultaneously
   - Calculate cumulative benefits when multiple mitigations are combined
   - Provide implementation guidance for multisolving approaches

3. **Impact Quantification**:
   - Quantify how adding multisolving mitigations increases exit value
   - Calculate nature-based solution benefits across multiple dimensions (resilience, biodiversity, water quality, etc.)
   - Show ROI improvements when multisolving approaches are used

**Implementation**:
- Create `MultisolvingAgent` class inheriting from `BaseAgent`
- Add tools:
  - `identify_multisolving_opportunities(risk_assessment: dict, location: str, stakeholder_needs: list) -> dict` - Identify opportunities for multisolving
  - `generate_multisolving_recommendations(primary_mitigations: list, stakeholder_needs: list, location: str) -> dict` - Generate specific recommendations for adding mitigations
  - `calculate_cumulative_benefits(mitigation_combinations: list, stakeholders: list) -> dict` - Calculate benefits when multiple mitigations are combined
  - `quantify_exit_value_impact(mitigation_combinations: list, exit_timeline: str) -> dict` - Quantify how multisolving increases exit value
  - `get_multisolving_case_studies(location: str, risk_types: list) -> dict` - Retrieve relevant multisolving case studies from data source
  - `integrate_stakeholder_needs(primary_analysis: dict, stakeholder_needs: list) -> dict` - Integrate stakeholder needs into analysis

**Data Sources**:
- **Multisolving Case Studies Database**: `src/multi_agent_system/data/multisolving_case_studies.json` (see Data Files section below)
- **Nature-Based Solutions Database**: `src/multi_agent_system/data/nature_based_solutions.json` (already exists)
- **Multisolving Institute Resources**: [Multisolving for Climate Resilience](https://www.multisolving.org/resources/multisovling-for-climate-resilience/) - Case studies including:
  - Goldbug Living Shoreline, South Carolina
  - Borrego Springs Microgrid, California
  - Baltimore Orchard Project, Maryland
  - Nashville Home Uplift, Tennessee

**Reference**: User journey Step 1.2 Part b in `0.61_AL_CapZone_Manu_Shipyard_User_Story_Journey_Data_Needs.md`

**Priority**: HIGH - Important for maximizing exit value and nature-based solution effectiveness through multisolving approaches

---

#### **3.3. Transparency/Progress Display Agent** 🆕
**File**: `src/multi_agent_system/agents/progress_display_agent.py`

**Purpose**: Show Pythia's working process (active agents, data sources, progress stages).

**Functionality**:
- Display progress bar with stages
- Show active agents (EnvironmentalDataAgent, InfrastructureDataAgent, etc.)
- Show data source indicators ("Best in Class Climate Risk Modeling + Weather Forecasting, Data, and AI Models" for Google data, "Local Data, Shipbuilding Industry Experts, Local Bioregional Experts, Scientists, NGOs" for local data)
- Show completion indicators (Ballpark ROI, optional Enterprise Edition integration)

**Implementation**:
- Create `ProgressDisplayAgent` class inheriting from `BaseAgent`
- Add tools:
  - `get_analysis_progress(session_id: str) -> dict`
  - `get_active_agents(session_id: str) -> list`
  - `get_data_source_status(session_id: str) -> dict`
  - `get_progress_stages(session_id: str) -> dict`

**Reference**: User journey Step 1.4 in `0.61_AL_CapZone_Manu_Shipyard_User_Story_Journey_Data_Needs.md`

**Priority**: HIGH - Core user experience feature

---

#### **3.4. Due Diligence Privacy Agent** 🆕
**File**: `src/multi_agent_system/agents/due_diligence_agent.py`

**Purpose**: Support due diligence workflow with complete privacy protection.

**Functionality**:
- Ensure user's proprietary data remains private
- Support cross-referencing with global + local data while keeping work private
- Provide confidentiality guarantees

**Implementation**:
- Create `DueDiligenceAgent` class inheriting from `BaseAgent`
- Add tools:
  - `create_private_workspace(user_id: str) -> dict`
  - `cross_reference_with_public_data(user_data: dict, public_sources: list) -> dict`
  - `export_analysis_for_deal_documentation(session_id: str, format: str) -> dict`

**Reference**: User journey Step 3 in `0.61_AL_CapZone_Manu_Shipyard_User_Story_Journey_Data_Needs.md`

**Priority**: HIGH - Critical for Private Equity Investor user requirements

---

### **4. Configuration Files** 🔄

#### **4.1. Enhance Existing Configuration Files** 🔄
**Files**: `config/data_sources.yaml` (create if doesn't exist) or enhance `src/multi_agent_system/config.py`

**Purpose**: Generic, reusable configuration with hierarchical geography structure (works for all prototypes).

**Approach**: Instead of creating prototype-specific YAML files, enhance existing configuration files with a generic, hierarchical geography structure.

**Content Structure** (for `config/data_sources.yaml` or addition to `config.py`):
```yaml
# Generic geography configuration (reusable for all prototypes)
geography:
  # Hierarchical structure for flexible location matching
  location_types:
    - "coastal"
    - "inland"
    - "urban"
    - "rural"
  
  # Example: Mobile Bay, Alabama
  regions:
    - location_type: "coastal"
      region: "Coastal_USA"
      subregion: "Southeast"
      sub_subregion: "Gulf"
      specific_location: "Mobile_Bay_Alabama"  # Optional: for very specific data
      data_sources:
        priority:
          - "noaa_swdi"
          - "cmr_mcp"
          - "nature_based_solutions"
          - "enhanced_data_sources"
        regional_specific:
          - "usgs_mcp"  # For storm surge modeling
          - "noaa_digital_coast"  # For coastal erosion
      primary_risks:
        - "hurricane"
        - "storm_surge"
        - "coastal_erosion"
        - "extreme_heat"
  
  # Example: Tamil Nadu, India (for future prototype)
    - location_type: "coastal"
      region: "Coastal_India"
      subregion: "South"
      sub_subregion: "Bay_of_Bengal"
      specific_location: "Tamil_Nadu"  # Optional
      data_sources:
        priority:
          - "imd_api"  # Indian Meteorological Department
          - "cmr_mcp"
          - "nature_based_solutions"
        regional_specific:
          - "central_water_commission"
      primary_risks:
        - "cyclone"
        - "storm_surge"
        - "monsoon_flooding"
        - "extreme_heat"

# Agent team configuration (can be user-type or geography-specific)
agent_teams:
  private_equity_investor:
    default_team:
      - "risk_agent"
      - "recommendation_agent"
      - "historical_agent"
      - "query_refinement_agent"
      - "progress_display_agent"
      - "due_diligence_agent"
      - "multisolving_agent"
    coastal_team_additions:
      - "multisolving_agent"  # Especially important for coastal areas
```

**Benefits of This Approach**:
- ✅ **Reusable**: One configuration file works for all prototypes
- ✅ **Hierarchical Geography**: Flexible matching from broad (Coastal_USA) to specific (Mobile_Bay_Alabama)
- ✅ **Scalable**: Easy to add new regions without creating new files
- ✅ **Maintainable**: Single source of truth for geography and data source mapping
- ✅ **Flexible**: Can match by region, subregion, or specific location as needed

**Implementation**:
- If `config/data_sources.yaml` doesn't exist, create it with this structure
- If it exists, enhance it with the hierarchical geography structure
- Update `src/multi_agent_system/config.py` to load and parse this YAML structure
- Add helper functions to match geography (e.g., `get_geography_config(region, subregion, sub_subregion)`)

**Priority**: MEDIUM - Enhances existing configuration rather than creating new prototype-specific files

---

### **5. Data Files (JSON)** 🆕

#### **5.1. Bioregional Risk Profiles** 🔄
**File**: `src/multi_agent_system/data/regional_risk_profiles.json` (EXTEND EXISTING)

**Purpose**: Major historical risks for most bioregions, with hierarchical geography tagging (region → subregion → sub-subregion).

**Approach**: Extend existing `regional_risk_profiles.json` with bioregional risk data, using hierarchical geography structure.

**Content Structure**:
```json
{
  "bioregions": [
    {
      "region": "Coastal_USA",
      "subregion": "Southeast",
      "sub_subregion": "Gulf_Coast",
      "geography_type": "coastal",
      "major_historical_risks": {
        "hurricane": {
          "frequency": "high",
          "season": "June-November",
          "historical_events": [...],
          "thresholds": {...}
        },
        "storm_surge": {
          "frequency": "high",
          "correlation_with_hurricane": true,
          "historical_data": {...}
        },
        "coastal_erosion": {
          "frequency": "ongoing",
          "rate_cm_per_year": {...},
          "historical_data": {...}
        },
        "extreme_heat": {
          "frequency": "seasonal",
          "peak_months": ["July", "August"],
          "historical_data": {...}
        }
      },
      "specific_locations": [
        {
          "name": "Mobile_Bay_Alabama",
          "additional_risks": [...],
          "local_variations": {...}
        }
      ]
    },
    {
      "region": "Coastal_India",
      "subregion": "South",
      "sub_subregion": "Bay_of_Bengal",
      "geography_type": "coastal",
      "major_historical_risks": {
        "cyclone": {...},
        "monsoon_flooding": {...},
        "storm_surge": {...},
        "extreme_heat": {...}
      }
    },
    {
      "region": "Coastal_Philippines",
      "subregion": "Luzon",
      "sub_subregion": "Pacific_Coast",
      "geography_type": "coastal",
      "major_historical_risks": {
        "typhoon": {...},
        "storm_surge": {...},
        "coastal_erosion": {...},
        "extreme_heat": {...}
      }
    }
  ]
}
```

**Priority**: MEDIUM - Extend existing file rather than creating new one

**Implementation**: Add bioregional risk data to existing `regional_risk_profiles.json` with hierarchical geography structure.

---

#### **5.2. Opportunity Zone Data** 🔄 **REVIEW NEEDED**

**Existing Functionality in `src/`**:
- ✅ `src/multi_agent_system/data/enhanced_data_sources.py` - `RegulatoryData` class has `get_opportunity_zone_data(state: str)` method (line 402)
- ✅ `src/multi_agent_system/agents/tools.py` - `get_regulatory_data_tool()` includes QOZ data (line 527-530)
- ✅ `src/multi_agent_system/data/funding_sources_NSB.json` - Contains Opportunity Zone funding sources (lines 205-272)

**Current Implementation Status**:
- **Basic OZ data method exists**: `RegulatoryData.get_opportunity_zone_data()` returns simulated data
- **Tools integrate OZ data**: `get_regulatory_data_tool()` already includes OZ data
- **Funding sources documented**: OZ funding sources are in `funding_sources_NSB.json`

**Recommendation**: 
- ❌ **DO NOT CREATE** `alabama_opportunity_zones.json` - Instead, enhance existing `RegulatoryData.get_opportunity_zone_data()` to:
  1. Accept census tract parameter (not just state)
  2. Connect to actual Opportunity Zone APIs (Census Bureau, Novogradac, etc.)
  3. Support all 8,764 Opportunity Zones across all states (not just Alabama)
  4. Return comprehensive OZ data including designation, compliance requirements, investment trends

**Enhancement Needed** (instead of new JSON file):
- 🔄 **Enhance** `src/multi_agent_system/data/enhanced_data_sources.py` - `RegulatoryData.get_opportunity_zone_data()`:
  - Change signature to: `get_opportunity_zone_data(census_tract: str = None, state: str = None, region: str = None)`
  - Add support for all Opportunity Zones (8,764 zones across 50 states + 5 U.S. possessions)
  - Integrate with Opportunity Zone API (see section 2.2 below)
  - Return comprehensive data: designation, compliance, investment trends, QOF data

**Priority**: HIGH - Enhance existing functionality rather than creating new JSON file

**Note**: The Opportunity Zone API integration (section 2.2) should provide the data source, eliminating the need for a static JSON file.

---

#### **5.3. Manufacturing Facility Templates** 🆕
**File**: `src/multi_agent_system/data/manufacturing_facility_templates.json`

**Purpose**: Manufacturing facility type templates and risk profiles.

**Content Structure**:
```json
{
  "facility_types": {
    "shipbuilding": {
      "vulnerabilities": [...],
      "resilience_strategies": [...],
      "cost_factors": {...}
    },
    "general_manufacturing": {...}
  }
}
```

**Priority**: MEDIUM - Can enhance risk assessment accuracy

---

## 📋 SUMMARY: REUSE vs. CREATE

### ✅ **REUSE (No Changes)**: 35+ files
- All core agent files (9 files)
- All A2A communication files (9 files)
- All core system files (15+ files)
- Base data source files (7 files)
- Existing JSON data files (6 files)

### 🔄 **ENHANCE (Extend Existing)**: 6 files
1. `enhanced_data_sources.py` - Add generic local government data methods (reusable for all states/locations), enhance OZ data methods (all 8,764 zones), manufacturing data
2. `risk_agent.py` - Add generic coastal risk analysis tools (geography-agnostic)
3. `recommendation_agent.py` - Add generic investor recommendations and QOZ-specific recommendations
4. `historical_agent.py` - Add generic coastal historical data methods (geography-agnostic)
5. `nature_based_solutions_source.py` - Add geography-based filtering (generic for all locations)
6. `regional_risk_profiles.json` - Add bioregional risk profiles with hierarchical geography structure

### 🆕 **CREATE (New Files)**: 15+ files

#### **MCP Server Integrations** (6 files):
1. `erddap_mcp.py` - HIGH priority
2. `datagov_mcp.py` - MEDIUM priority
3. `usgs_mcp.py` - HIGH priority
4. `epa_mcp.py` - MEDIUM priority
5. `noaa_mcp.py` - HIGH priority
6. `census_mcp.py` - MEDIUM priority

#### **Direct API Integrations** (4 files):
1. `fred_api.py` - HIGH priority
2. `opportunity_zone_api.py` - HIGH priority
3. `fema_flood_maps.py` - HIGH priority
4. `noaa_digital_coast.py` - HIGH priority

#### **New Agents** (4 files):
1. `query_refinement_agent.py` - HIGH priority
2. `multisolving_agent.py` - HIGH priority (expanded to generate recommendations, not just identify opportunities)
3. `multisolving_case_studies.json` - HIGH priority (data source for multisolving examples)
3. `progress_display_agent.py` - HIGH priority
4. `due_diligence_agent.py` - HIGH priority

#### **Configuration Files** (1 file):
1. 🔄 Enhance `config/data_sources.yaml` (or `config.py`) with hierarchical geography structure - MEDIUM priority

#### **Data Files (JSON)** (2 files):
1. 🔄 **Extend** `regional_risk_profiles.json` - Add bioregional risk profiles with hierarchical geography (MEDIUM priority)
2. `manufacturing_facility_templates.json` - MEDIUM priority

**Note**: `alabama_opportunity_zones.json` is **NOT NEEDED** - Enhance existing `RegulatoryData.get_opportunity_zone_data()` method instead (see section 5.2).

---

## 🎯 IMPLEMENTATION PRIORITIES

### **Phase 1: Critical Path (Must Have)**
1. ✅ Reuse existing agents and core files
2. 🔄 Enhance `risk_agent.py` with generic coastal risk analysis tools (geography-agnostic)
3. 🔄 Enhance `recommendation_agent.py` with generic investor recommendations and QOZ-specific recommendations
4. 🆕 Create `query_refinement_agent.py`
5. 🆕 Create `progress_display_agent.py`
6. 🆕 Create `due_diligence_agent.py`
7. 🆕 Create `fred_api.py`
8. 🆕 Create `opportunity_zone_api.py`
9. 🆕 Create `fema_flood_maps.py`
10. 🆕 Create `noaa_digital_coast.py`
11. 🆕 **Create `google_maps_mcp.py`** - Use Google's managed MCP server for Maps Grounding Lite (HIGH PRIORITY)
12. 🆕 **Create `google_bigquery_mcp.py`** - Use Google's managed MCP server for BigQuery (HIGH PRIORITY)
13. 🆕 Create `usgs_mcp.py` (or evaluate if available through Google managed MCP)
14. 🆕 Create `noaa_mcp.py` (or evaluate if available through Google managed MCP)
15. 🔄 Enhance `RegulatoryData.get_opportunity_zone_data()` to support all Opportunity Zones (8,764 zones across all states, not just Alabama)
16. 🔄 Extend `regional_risk_profiles.json` with bioregional risk profiles (hierarchical geography: region → subregion → sub-subregion)

### **Phase 2: Important (Should Have)**
1. 🔄 Enhance `enhanced_data_sources.py` with generic local government data methods (reusable for all states/locations)
2. 🔄 Enhance `historical_agent.py` with generic coastal historical data methods (geography-agnostic)
3. 🆕 Create `erddap_mcp.py`
4. 🆕 Create `epa_mcp.py`
5. 🆕 Create `census_mcp.py`
6. 🆕 Create `multisolving_agent.py` - Generate recommendations for combining mitigations to maximize exit value and nature-based benefits
7. 🆕 Create `multisolving_case_studies.json` - Database of multisolving examples from Multisolving Institute
8. 🆕 Create `alabama_risk_profiles.json` (or extend existing)
8. 🆕 Create `manufacturing_facility_templates.json`

### **Phase 3: Nice to Have (Can Wait)**
1. 🆕 Create `datagov_mcp.py`
2. 🔄 Enhance `config/data_sources.yaml` (or `config.py`) with hierarchical geography structure (Coastal_USA -> Southeast -> Gulf)
3. 🔄 Enhance `nature_based_solutions_source.py` with Mobile Bay filtering

---

## 📚 REFERENCES

### **System Constraints**
- `docs/_RULES_Pythia_System_Rules/00_LLM_General_Rules_for_Pythia.md` - Primary reference for system constraints
- `docs/_RULES_Pythia_System_Rules/ARCHIVE/1.3_System_DNU.md` - Legacy/archived constraints (historical reference)

### **Agent Requirements**
- `docs/1-USER_STORIES_and_PRODUCT/AGENT/Agents_Req_for_Pythia.md` - Agent guidelines
- `docs/5-ENGINEERING/A2A_ADK/2.4_Agentcard_Definition_Doc_Tool_Instructions.md` - Agent card definitions
- `docs/5-ENGINEERING/A2A_ADK/3.2_A2A_Reference.md` - A2A protocol reference

### **Technical Requirements**
- `docs/1-USER_STORIES_and_PRODUCT/2.1_Technical_PRD.md` - Technical PRD
- `docs/1-USER_STORIES_and_PRODUCT/PRD/2.1_Technical_PRD_Pythia_UX_Flow_Diagram.md` - UX flow diagram

### **Data Sources**
- `docs/2-DATA/2.1_First_Data_Sources.md` - Comprehensive data source documentation

### **User Journey**
- `docs/3-EXPERIMENTS/0.6_Alabama/0.61_AL_CapZone_Manu_Shipyard_User_Story_Journey_Data_Needs/0.61_AL_CapZone_Manu_Shipyard_User_Story_Journey_Data_Needs.md` - User story and journey

---

## Change Log

### **December 12, 2025**
- **Initial Creation**: Comprehensive analysis of reuse opportunities vs. new file requirements
- **Reuse Analysis**: Identified 35+ files that can be reused as-is
- **Enhancement Analysis**: Identified 5 files that need enhancement
- **New File Analysis**: Identified 15+ new files needed
- **Priority Phasing**: Organized implementation into 3 phases
- **References**: Added comprehensive reference section

---

