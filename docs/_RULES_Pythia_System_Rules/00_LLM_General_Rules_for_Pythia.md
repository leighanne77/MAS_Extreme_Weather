# Cursor Rules for Pythia Work

**Date Created**: July 2, 2025
**Date Last Updated**: December 14, 2025

## Core Rules for Pythia System Operations With Users 


**Decision Support Boundaries**: Make sure the system tells the user this is a decision support tool, NOT decision making tool, and recommendations offered cannot be automated - they is for user review only

#### **Data Access Constraints:**
- **DO NOT** promise real-time data - will be on the roadmap later (current refresh: 1-6 hours)
- **DO NOT** promise results that require access to user's proprietary data that we cannot use
- **DO NOT** promise features that rely on user's proprietary data that we cannot access
- **DO NOT** suggest integrations that would require user to share confidential business information
- **INSTEAD**: Tool provides expert and external data sources (weather, environmental, scientific) to enhance user's existing proprietary data

#### **Terminology Constraints:**
- **DO NOT** reference carbon markets, carbon credits, carbon trading, or carbon-related financial instruments
- **Use** "extreme weather" 

- **DO NOT** Use the word "climate" or variations but instead use terms like "extreme weather-related risk"
- **DO NOT** promise carbon sequestration outcomes or carbon reduction metrics
- **USE INSTEAD**: Risks, risk mitigation, biodiversity, ecosystem services, and environmental benefits

#### **Data Privacy & Security:**
- **DO NOT** promise to store or process user's personal financial information
- **DO NOT** suggest features that would require access to user's proprietary data or access to it - instead offer external data sources only 
- **DO NOT** promise integration with user's internal systems without explicit permission
- **DO NOT** suggest features that would require user to share client information
 -**DO NOT** OFfer any real-time data access, batch only 

#### **Decision Support Boundaries:**
- Focus on how this is a decision support tool, NOT a decision making tool
- Cannot be automated into any systems
- Does not ever integrate into Private Equity banks or other financial services systems
- Current data refresh intervals: 1-6 hours depending on source
- Caching strategies implemented for performance optimization
- Fallback mechanisms available for data source failures

#### **Value Proposition Boundaries:**
- **DO NOT** go beyond the value propositions outlined in USER_STORIES_JOURNEYS_and_UX_NEEDS/1.01_All_User_Needs.md
- **DO NOT** promise features not explicitly mentioned in the user journey documentation
- **DO NOT** suggest capabilities that exceed the scope defined in the prototype documentation
- **STAY WITHIN** the defined user personas: Private Equity Investor and Government Funders
- **DO NOT** include private insurance or public insurance in user personas

#### **User Experience Boundaries:**
- **DO NOT** promise fully automated decision-making capabilities
- **DO NOT** suggest features that would replace professional judgment
- **DO NOT** promise instant results or immediate implementation
- **DO NOT** suggest features that require extensive user training

#### **Environmental Claims Constraints:**
- **DO NOT** make specific environmental impact promises without data validation
- **DO NOT** promise quantifiable environmental outcomes without measurement capabilities
- **DO NOT** suggest features that would require environmental certification
- **DO NOT** promise compliance with specific environmental standards

#### **Financial Promises Constraints:**
- **DO NOT** promise specific financial returns or ROI guarantees including but not limited to any specific percentages, you can offer ranges of likely outcomes
- **DO NOT** suggest features that would require financial licensing
- **DO NOT** promise access to specific financial products or services
- **DO NOT** suggest features that would require financial advisor certification

#### **Integration Limitations:**
- **DO NOT** promise seamless integration with user's existing systems
- **DO NOT** suggest features that would require API access to user's internal databases
- **DO NOT** promise features that would require user to modify their existing workflows
- **DO NOT** suggest capabilities that would require user to share their proprietary algorithms
- **DO NOT** promise direct integration with user's proprietary data systems
- **INSTEAD**: Tool provides external data feeds and insights that users can incorporate into their existing workflows and decision-making processes
- **INSTEAD**: Users can export Tool's analysis results and then manually include them, but cannot integrate them automatically into their own proprietary systems

  2. Rules for Data 
 

-
- Check against established "do not do" guidelines
- For historical reference, see `docs/_RULES_Pythia_System_Rules/ARCHIVE/1.3_System_DNU.md` (archived/legacy)
- **See `docs/00_cursor_rules.md` for Cursor-specific rules** (Architecture Constraints, Do Not Make Up Anything, No File Changes Without Approval, No Real-Time Data Promises, Documentation Maintenance, Do Not Promise Specific Outcome Percentages, No Truncation)

## Implementation Guidelines

### **When Suggesting Changes:**
1. Verify no financial promises or guarantees are being made
2. Confirm no environmental claims without validation
3. Ensure no integration promises that require proprietary data access
4. Check against Value Proposition Boundaries - ensure feature is within defined scope
5. Present clear options with pros/cons
6. Wait for explicit approval
7. Ask for feedback that signals approval before proceeding to the next step

### **When Researching Data Sources:**
1. Verify URLs and access methods
2. Check if sources actually exist
3. Confirm access requirements (free vs. paid, registration needed)
4. Do not invent or assume data availability

### **When Discussing System Capabilities:**
1. Be accurate about data refresh rates
2. Don't overpromise real-time features
3. Focus on actual implemented capabilities
4. Acknowledge system limitations honestly

## Enforcement Guidelines

**CRITICAL**: These guidelines must be followed for all Pythia development work:

- **Primary Reference**: All documentation should reference `docs/_RULES_Pythia_System_Rules/00_LLM_General_Rules_for_Pythia.md` (this file) when discussing new features and system constraints


### **Geographic Data Access - General Rules (Apply to All Locations):**

#### **General Data Access Principles:**
- **Cannot Access**: User-specific proprietary data, internal business models, confidential financial information, individual performance metrics
- **Can Provide**: 
  - Publicly available extreme weather risk data
  - Government-published environmental and infrastructure data
  - Scientific and research datasets
  - Compliance and regulatory information
  - Geographic-specific risk assessments
  - Infrastructure resilience metrics
  - Nature-based solutions data filtered by location

#### **Geographic Data Source Selection:**
- **Identify Primary Risks**: Determine dominant extreme weather risks for the geographic area (hurricanes, monsoons, droughts, floods, extreme heat, etc.)
- **Select Appropriate Data Sources**: Choose data sources that provide relevant risk data for the geographic area
  - Coastal areas: NOAA coastal data, storm surge models, sea level data
  - Inland areas: Precipitation data, temperature extremes, drought indices
  - Agricultural regions: Crop-specific weather data, soil moisture, growing season data
  - Urban areas: Heat island data, stormwater management data, infrastructure resilience metrics
- **Use Hierarchical Geography**: Support location hierarchy (country → region → state/province → city → specific location)
- **Filter by Bioregion**: Apply bioregional risk profiles when available

#### **Geographic Solution Filtering:**
- **Filter Nature-Based Solutions by Location Type**: 
  - Coastal locations: Coastal solutions (living shorelines, wetland restoration, barrier islands)
  - Riverine locations: Floodplain restoration, riparian buffers, river management
  - Urban locations: Green infrastructure, urban forests, stormwater management
  - Rural/Agricultural locations: Agricultural adaptation, soil conservation, water management
- **Consider Local Ecosystem Compatibility**: Solutions must be appropriate for local ecosystems and bioregions
- **Respect Cultural and Traditional Knowledge**: When available, incorporate location-specific traditional practices
- **Scale Appropriately**: Match solution scale to location (property, community, regional)

#### **Government Data Source Integration:**
- **Federal/National Level**: Use national meteorological services, federal environmental agencies, national statistical offices
- **State/Provincial Level**: Access state environmental departments, state commerce/economic development agencies, state extension services
- **Local/Municipal Level**: Use local planning departments, local environmental agencies, municipal infrastructure data
- **International Locations**: Use appropriate international data sources (e.g., Indian Meteorological Department for India, European agencies for EU locations)

#### **MCP Server Integration - Geographic Filtering:**
- **[ERDDAP MCP Server](https://lobehub.com/mcp/yourusername-erddap2mcp)**: Oceanographic and environmental data for coastal and marine locations
- **[CMR MCP Server](https://github.com/podaac/cmr-mcp)**: NASA Earth science data for all locations with satellite remote sensing and global coverage
- **[Data.gov MCP Server](https://github.com/melaodoidao/datagov-mcp-server)**: Government dataset consolidation (country-specific versions available)
- **Geographic Data Filtering**: All MCP servers support filtering by geographic boundaries (coordinates, administrative boundaries, watersheds)
- **Economic Problem Alignment**: MCP servers prioritize data relevant to user type economic problems within the geographic context
- **Reference Files**: See [`src/multi_agent_system/data/weather_data.py`](../src/multi_agent_system/data/weather_data.py) for current NOAA SWDI integration capabilities
- **Reference Files**: See [`src/multi_agent_system/data/nature_based_solutions_source.py`](../src/multi_agent_system/data/nature_based_solutions_source.py) for current nature-based solutions data structure
- **Reference Files**: See [`src/multi_agent_system/data/enhanced_data_sources.py`](../src/multi_agent_system/data/enhanced_data_sources.py) for current enhanced data source capabilities

### **Prototype-Specific Examples (For Reference):**

#### **Mobile Bay, Alabama Prototype - Example:**
- **Data Access for Private Equity Investors:**
  - **Cannot Access**: QOF performance data, individual investment performance data, internal risk models
  - **Can Provide**: 
    - Opportunity zone compliance data
    - Hurricane risk assessments
    - Manufacturing infrastructure resilience metrics
    - Hurricane risks, coastal flooding data, manufacturing infrastructure weather resilience, opportunity zone weather impacts
    - Coastal manufacturing resilience, opportunity zone green infrastructure, hurricane-resistant industrial development

- **Geographic-Specific NOAA Data Access:**
  - **Mobile Bay**: Hurricane risks, coastal flooding data, manufacturing infrastructure weather resilience, opportunity zone weather impacts

- **Geographic-Specific Solution Filtering:**
  - **Mobile Bay**: Coastal manufacturing resilience, opportunity zone green infrastructure, hurricane-resistant industrial development

- **State Agency Integration:**
  - **Alabama**: Alabama Department of Environmental Management, Alabama Department of Commerce, Alabama Cooperative Extension System

#### **Deccan Plateau, India Prototype - Example:**
- **Geographic-Specific Data Access:**
  - **Deccan Plateau**: Monsoon patterns, agricultural weather, rural development weather impacts, Indian Meteorological Department data

- **Geographic-Specific Solution Filtering:**
  - **Deccan Plateau**: Rural agricultural adaptation, monsoon water management, sustainable farming practices, community-based ecosystem restoration

- **Government Agency Integration:**
  - **India**: Indian Meteorological Department, Central Water Commission, Ministry of Agriculture, National Bank for Agriculture and Rural Development

### **Economic Problem-Specific Data Access Guidelines - General Rules:**

#### **General Principles for All User Types:**
- **Cannot Access**: User-specific proprietary data, internal business models, confidential financial information, individual performance metrics, internal risk models
- **Can Provide**: 
  - Public market analysis and trends
  - Land and property value trends (aggregated, not individual)
  - Natural assets availability and impact assessments
  - Extreme weather risk assessments (hurricanes, monsoons, droughts, floods, extreme heat)
  - Property value trends (aggregated)
  - Extreme weather tracking data
  - Storm surge and flood modeling
  - Development risk frameworks
  - Biodiversity data
  - Ecosystem health indicators
  - Sustainable business practices benchmarks
  - Energy infrastructure data
  - Extreme weather impact assessments

#### **User Type-Specific Examples (For Reference):**

**Private Equity Investors:**
- **Cannot Access**: Individual investment performance data, internal risk models, QOF performance data
- **Can Provide**: Agricultural market analysis, land value trends, natural assets availability impact assessments, days of extreme heat, hurricane risk assessments, property value trends, hurricane tracking data, storm surge modeling, coastal development risk frameworks, biodiversity data, ecosystem health indicators, sustainable business practices benchmarks, energy infrastructure data, extreme heat impact assessments

**Mobile Bay, Alabama Prototype - Infrastructure Manufacturing Example:**
- **Private Equity Investor (Opportunity Zone Specialist)**: Cannot access QOF performance data, but can provide opportunity zone compliance data, hurricane risk assessments, and manufacturing infrastructure resilience metrics

**Deccan Plateau, India Prototype - Rural Agricultural Development Example:**
- **District Collectors**: Cannot access local government coordination data, but can provide agricultural productivity data, extreme weather impact assessments, and rural development program effectiveness metrics

## Change Log

### **December 14, 2025**
- **Geographic Rules Generalized**: Added general rules for geographic data access that apply to any location, while keeping Mobile Bay and India examples as reference:
  - General Data Access Principles (applies to all locations)
  - Geographic Data Source Selection (identify risks, select sources, hierarchical geography, bioregional profiles)
  - Geographic Solution Filtering (filter by location type, ecosystem compatibility, cultural knowledge, scale)
  - Government Data Source Integration (federal/national, state/provincial, local/municipal, international)
  - MCP Server Integration with geographic filtering capabilities
  - Economic Problem-Specific Data Access Guidelines generalized with examples
- **Prototype Examples Preserved**: Mobile Bay, Alabama and Deccan Plateau, India examples kept as specific reference examples
- **Cursor Rules Extracted**: Moved Cursor-specific rules to `docs/00_cursor_rules.md`:
  - Architecture Constraints (lines 12-16)
  - Do Not Make Up Anything (section 2)
  - No File Changes Without Explicit Approval (section 3)
  - No Real-Time Data Feed Promises (section 4)
  - Documentation Maintenance (section 5)
  - Do Not Promise Specific Outcome Percentages (section 6)
  - No Truncation enforcement guideline (line 158)
- **Reference Added**: Added reference to `docs/00_cursor_rules.md` in section 1

### **December 12, 2025**
- **File Renamed**: Changed from `00_Cursor_rules_for_Pythia_Work.md` to `00_LLM_General_Rules_for_Pythia.md`
- **Migration to Primary Reference**: Updated all references across codebase (11 files, 18+ references) to point to this file as primary reference
- **Legacy File Marked**: Added header note to `1.3_System_DNU.md` marking it as legacy/archived
- **Updated Enforcement Guidelines**: Changed primary reference from `1.3_System_Do_Not_Dos.md` to this file
- **Added Section 0**: System Constraints and Restrictions with consolidated key constraints from 1.3_System_Do_Not_Dos.md
  - Architecture constraints
  - Data access constraints
  - Terminology constraints
  - Data privacy & security constraints
  - Decision support boundaries (with data refresh details)
  - Value proposition boundaries
  - User experience boundaries
  - Environmental claims constraints
  - Financial promises constraints
  - Integration limitations
- **Updated Rule 1**: Changed from referencing 1.3_System_DNU.md to referencing Section 0 of this file as primary source
- **Updated Enforcement Guidelines**: Changed primary reference from 1.3_System_DNU.md to this file (00_LLM_General_Rules_for_Pythia.md)
- **Added Prototype Contexts**: Added Mobile Bay, Alabama and Deccan Plateau, India Prototype-specific constraints sections
  - Geographic-specific NOAA data access
  - Geographic-specific solution filtering
  - State agency integration
  - MCP server integration capabilities with reference files
- **Added Economic Problem-Specific Data Access**: Guidelines for Private Equity Investors and prototype-specific data access constraints
- **Added Enforcement Guidelines**: Critical guidelines for all Pythia development work
- **Enhanced "When Suggesting Changes"**: Added validation checks and approval feedback step
- **Made 00_LLM Primary Reference**: This file is now the primary reference for system constraints; 1.3_System_DNU.md is maintained for historical context only

### **January 15, 2025**
- **Rule Consolidation**: Merged overlapping rules 2, 4, and 7 into a single comprehensive rule about not making things up
- **Rule Renumbering**: Renumbered rules after consolidation (now 6 core rules instead of 10)
- **Formatting Fixes**: Fixed capitalization inconsistencies, typos ("a a" → "a"), and standardized "Do not" usage
- **Clarity Improvements**: Clarified Rule 6 about user personas/stories, added cross-reference to System_Do_Not_Dos.md
- **Cross-Reference Consistency**: Standardized all references to use full path `docs/_RULES_Pythia_System_Rules/ARCHIVE/1.3_System_DNU.md`
- **Change Log Update**: Updated outdated entry that referenced "four key rules" to reflect current state

### **July 12, 2025**
- **Date Update**: Updated last modified date to reflect current work session

### **July 2, 2025**
- **Initial Creation**: Established core rules for Pythia development work
- **Rule Definition**: Defined core rules for safe and accurate development 