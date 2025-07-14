# Todo Tomorrow - July 13, 2025

**Date Created**: June 20, 2025
**Date Last Updated**: July 13, 2025

## Onboarding Implementation & UX Requirements

Based on 2.3_Pythia_UX_More.md analysis, we have a comprehensive onboarding system designed but need to implement several key components to execute the full user experience. The current system has most backend components but lacks critical frontend elements for the complete onboarding flow.

also these - see bottom

https://google.github.io/adk-docs/evaluate/#what-to-evaluate

To Add to This list: revise 1.3_System_Do_Not_Dos.md as needed
 
0. indexing? 
1. explicit call out of explainability and how this is done in the scenario generation 
2. explicit call outs of the tech monkeys and where they are addressed
3. How task specific evals are - what is the methodology to build "on the fly" for the  use cases
4. Add Stanford Questions dataset and the Red Program dataset
5. Check how sparse/ distilled / fine tuned fitas in small is beautiful - rather than just relying on gemini's API and ADK/A2A
6. Check where GANs can help or if reasoning loops are enough

---

## **Priority 1: Critical Missing Components**

### **1. HTML Templates (CRITICAL - Blocking Onboarding)**
**Status**: ❌ NOT IMPLEMENTED  
**Impact**: Cannot execute onboarding without these templates

#### **Required Templates**:
- `src/pythia_web/templates/base.html` - Responsive base template with meta tags
- `src/pythia_web/templates/user_onboarding.html` - Mobile-optimized onboarding flow
- `src/pythia_web/templates/dashboard_mobile.html` - Mobile dashboard interface
- `src/pythia_web/templates/error_pages.html` - Mobile-friendly error handling
- `src/pythia_web/templates/reports/` - Report template directory

#### **Implementation Details**:
- **User Type Selection Interface**: 8 user types with role-specific onboarding
- **Geography Selection**: Natural language input with geocoding support
- **Profile Memory**: "Welcome back! Are you still a [User Type]?" functionality
- **Mobile-First Design**: Responsive layouts for all device types
- **Progressive Disclosure**: Show key insights first, expand for details

### **2. CSS Framework (CRITICAL - Blocking UI)**
**Status**: ❌ NOT IMPLEMENTED  
**Impact**: No styling without CSS framework

#### **Required CSS Files**:
- `src/pythia_web/static/css/responsive.css` - Mobile-first breakpoints
- `src/pythia_web/static/css/mobile-optimized.css` - Touch interactions
- `src/pythia_web/static/css/tablet-optimized.css` - Tablet layouts
- `src/pythia_web/static/css/desktop-enhanced.css` - Desktop features

#### **Design Requirements**:
- **Mobile-First**: Responsive design starting with mobile
- **Touch-Optimized**: Large buttons, swipe gestures
- **Progressive Disclosure**: Key insights first, details on demand
- **Role-Based Styling**: Different visual themes per user type

### **3. Enhanced JavaScript Components (HIGH PRIORITY)**
**Status**: 🔄 PARTIALLY IMPLEMENTED  
**Impact**: Missing key onboarding functionality

#### **Required New Components**:
- `src/pythia_web/static/js/user-onboarding.js` - Complete onboarding flow
- `src/pythia_web/static/js/mobile-navigation.js` - Mobile navigation system
- `src/pythia_web/static/js/touch-optimized.js` - Touch interactions
- `src/pythia_web/static/js/offline-cache.js` - Offline capability
- `src/pythia_web/static/js/voice-input.js` - Voice processing (future)
- `src/pythia_web/static/js/accessibility.js` - ARIA labels and screen reader support

#### **Enhanced Existing Components**:
- `src/pythia_web/static/js/dashboard.js` - Add mobile gesture support
- `src/pythia_web/static/js/simple-suggestions.js` - Add AI-powered suggestions
- `src/pythia_web/static/js/simple-filters.js` - Add user-specific filters

---

## **Priority 2: Data Source Integration**

### **4. Federal Reserve District APIs (HIGH PRIORITY)**
**Status**: ❌ NOT IMPLEMENTED  
**Impact**: Missing regional economic data for prototypes

#### **Required Integration**:
- **District 6 (Atlanta Federal Reserve Bank)**: Alabama, Florida, Georgia, Louisiana, Mississippi, Tennessee
- **District 11 (Dallas Federal Reserve Bank)**: Texas, northern Louisiana, southern New Mexico
- **District 5 (Richmond Federal Reserve Bank)**: Maryland, Virginia, North Carolina, South Carolina, West Virginia, District of Columbia
- **District 10 (Kansas City Federal Reserve Bank)**: Colorado, Kansas, Nebraska, Oklahoma, Wyoming, northern New Mexico, western Missouri

#### **Implementation Details**:
- Direct API integration for regional economic indicators
- Configure regional bank API endpoints in `src/multi_agent_system/data/regional_fed_apis.py`
- Add to data source registry in `src/multi_agent_system/data_management.py`
- Priority: High for Alabama prototype, Medium for other regional prototypes

### **5. Federal Reserve Economic Data (FRED) API (HIGH PRIORITY)**
**Status**: ❌ NOT IMPLEMENTED  
**Impact**: Missing essential economic indicators

#### **Required Implementation**:
- Install via pip: `pip install fredapi`
- Configure FRED API key in `src/multi_agent_system/data/fred_api.py`
- Add to data source registry in `src/multi_agent_system/data_management.py`
- Data Types: Interest rates, economic indicators, financial data, banking data, monetary policy data, regional economic data
- Access Requirements: Free public access, requires FRED API key registration

### **6. Federal Reserve Beige Book Integration (MEDIUM PRIORITY)**
**Status**: ❌ NOT IMPLEMENTED  
**Impact**: Missing qualitative economic assessments

#### **Required Implementation**:
- Web scraping or RSS feed integration
- Configure in `src/multi_agent_system/data/beige_book_api.py`
- Add to data source registry in `src/multi_agent_system/data_management.py`
- Data Types: Qualitative economic assessments, regional business conditions, economic outlook
- Access Requirements: Free public access, no registration required

---

## **Priority 3: MCP Server Integration**

### **7. Core MCP Servers (HIGH PRIORITY)**
**Status**: 🔄 PARTIALLY IMPLEMENTED (CMR MCP Server)  
**Impact**: Missing essential data sources for all prototypes

#### **Required MCP Servers**:
- **ERDDAP MCP Server**: Oceanographic and environmental data for coastal prototypes
  - Install via pip: `pip install erddap-mcp-server`
  - Configure server endpoints in `src/multi_agent_system/data/erddap_mcp.py`
  - Data Types: Sea surface temperature, salinity, currents, sea level, chlorophyll, wave heights, buoy data, glider data

- **Data.gov MCP Server**: Government dataset consolidation for all prototypes
  - Install via pip: `pip install datagov-mcp-server`
  - Configure API endpoints in `src/multi_agent_system/data/datagov_mcp.py`
  - Data Types: Environmental monitoring, economic indicators, infrastructure metrics, agricultural statistics, demographic data

- **NOAA MCP Server**: Weather, climate, and oceanographic data
  - Install via pip: `pip install noaa-mcp-server`
  - Configure NOAA API keys in `src/multi_agent_system/data/noaa_mcp.py`
  - Data Types: Weather forecasts, climate data, oceanographic data, atmospheric data, satellite data, radar data, buoy data

### **8. Specialized MCP Servers (MEDIUM PRIORITY)**
**Status**: ❌ NOT IMPLEMENTED  
**Impact**: Missing specialized data for risk assessment

#### **Required MCP Servers**:
- **USGS MCP Server**: Geological and hydrological data access
  - Install via pip: `pip install usgs-mcp-server`
  - Configure USGS API credentials in `src/multi_agent_system/data/usgs_mcp.py`
  - Data Types: Geological surveys, hydrological data, earthquake data, volcano data, mineral resources, water quality, streamflow data

- **EPA MCP Server**: Environmental protection data and compliance information
  - Install via pip: `pip install epa-mcp-server`
  - Configure EPA data access credentials in `src/multi_agent_system/data/epa_mcp.py`
  - Data Types: Air quality data, water quality data, toxic release inventory, environmental compliance, enforcement data, regulatory data

- **Census Bureau MCP Server**: Demographic and economic data
  - Install via pip: `pip install census-mcp-server`
  - Configure Census API key in `src/multi_agent_system/data/census_mcp.py`
  - Data Types: Population data, housing data, economic indicators, employment data, income data, education data, health data

---

## **Priority 4: Future Feature Integration**

### **9. Notification System (MEDIUM PRIORITY)**
**Status**: ❌ NOT IMPLEMENTED  
**Impact**: No proactive user engagement

#### **Required Features**:
- **Risk Monitoring**: Track specific risk factors identified in analysis
- **Strategy Effectiveness**: Monitor chosen derisking strategies
- **Data Updates**: Notify when new relevant data becomes available
- **Success Indicators**: Alert when positive trends emerge
- **User Control**: Enable/disable notifications, frequency options

#### **Implementation Details**:
- **When to Offer Notifications**: After risk analysis, after derisking strategy selection, after implementation
- **Notification Types**: Risk monitoring, strategy effectiveness, data updates, success indicators
- **Notification Settings**: Weekly, monthly, quarterly, or on significant changes
- **Confidentiality**: All notifications stay within Tool tool, not shared externally
- **Customization**: Users can choose which specific metrics to monitor

### **10. Advanced Monitoring Features (LOW PRIORITY)**
**Status**: ❌ NOT IMPLEMENTED  
**Impact**: Limited ongoing user engagement

#### **Required Features**:
- **Progress Tracking**: Monitor implementation progress of chosen strategies
- **Trend Analysis**: Track long-term trends in risk factors and mitigation effectiveness
- **Alert System**: Immediate notifications for significant changes in risk factors
- **Reporting System**: Automated generation of progress reports and effectiveness summaries

---

## **Priority 5: Onboarding Flow Implementation**

### **11. User Profile Memory System (HIGH PRIORITY)**
**Status**: ✅ IMPLEMENTED (Backend) / ❌ NOT IMPLEMENTED (Frontend)  
**Impact**: Cannot provide personalized experience

#### **Required Implementation**:
- **First-Time User Flow**: Full user type selection with onboarding
- **Returning User Flow**: "Welcome back! Are you still a [User Type]?"
- **Profile Persistence**: Remember user preferences and common queries
- **Adaptive Interface**: Adjust language, metrics, and filters based on user type

#### **User Type-Specific Onboarding**:
```
8 User Types with Custom Onboarding:
1. Private Equity Investors - IRR-focused metrics
2. Loan Officers - Default risk and collateral protection
3. Data Science Officers - Model validation and data quality
4. Chief Risk Officers - Portfolio risk assessment
5. Chief Sustainability Officers - ESG compliance and biodiversity
6. Private Insurer - Insurance Agents - Claims risk assessment
7. Banking - Credit Officers (Operating) - Cash flow and seasonal planning
8. Public - Gov Funders - Economic development impact
```

### **12. Geography Selection Enhancement (MEDIUM PRIORITY)**
**Status**: ✅ IMPLEMENTED (Basic) / 🔄 NEEDS ENHANCEMENT  
**Impact**: Limited geographic precision

#### **Required Enhancements**:
- **Approximate Locations**: No exact addresses required
- **Asset-Specific Regions**: Pre-defined regions relevant to asset classes
- **Extreme Weather Zones**: Broader geographic groupings
- **Flexible Boundaries**: Multiple regions or broad areas
- **Natural Language Processing**: "Kansas agriculture" → specific regions

### **13. Scenario Generation System (MEDIUM PRIORITY)**
**Status**: ✅ IMPLEMENTED (Basic) / 🔄 NEEDS ENHANCEMENT  
**Impact**: Limited scenario exploration

#### **Required Enhancements**:
- **Baseline + Risks Scenario**: Extreme weather trajectory visualization
- **Extreme Weather Resilience Success Scenario**: Success path visualization
- **Interactive Scenario Exploration**: "What if" variations
- **Timeline Sliders**: 5-7 year investment horizons
- **Risk Tolerance Adjusters**: Modify risk appetite
- **Double-Click Details**: Access confidence levels and data sources

---

## **Priority 6: Advanced UX Features**

### **14. Mobile Responsiveness (HIGH PRIORITY)**
**Status**: ❌ NOT IMPLEMENTED  
**Impact**: Cannot support mobile-first users

#### **Required Features**:
- **Voice Input**: "Tell me about extreme weather risks in Kansas agriculture"
- **Swipe Navigation**: Swipe between scenarios, tap to expand details
- **Progressive Loading**: Load key insights first, details on demand
- **Quick Filters**: Pre-set filter combinations based on user profile
- **Offline Mode**: Cache scenarios and basic data for field use
- **Push Notifications**: Alert users to new extreme weather data
- **Profile Quick-Switch**: Easy user type confirmation on mobile

### **15. Advanced Data Visualization (MEDIUM PRIORITY)**
**Status**: ❌ NOT IMPLEMENTED  
**Impact**: Limited data comprehension

#### **Required Features**:
- **Interactive Maps**: Leaflet.js integration with risk overlays
- **Advanced Charts**: 3D visualizations, animated charts
- **Dashboard Customization**: User preferences and widget system
- **Multi-Panel Layout**: Side-by-side scenario comparison (desktop)
- **Real-time Updates**: Live data visualization updates

---

## **Priority 7: Technical Infrastructure**

### **16. Performance Optimization (MEDIUM PRIORITY)**
**Status**: 🔄 PARTIALLY IMPLEMENTED  
**Impact**: User experience degradation

#### **Required Optimizations**:
- **Lazy Loading**: Component lazy loading for faster initial load
- **Caching Strategy**: Browser caching and CDN optimization
- **Performance Monitoring**: Real-time performance tracking
- **Memory Management**: Optimize memory usage for large datasets
- **Load Balancing**: Distribute computational load across agents

### **17. Error Handling and Recovery (MEDIUM PRIORITY)**
**Status**: 🔄 PARTIALLY IMPLEMENTED  
**Impact**: Poor user experience during errors

#### **Required Features**:
- **Error Detection**: Frontend error handling and reporting
- **Fallback Systems**: Partial results when full analysis unavailable
- **Graceful Degradation**: Feature fallbacks for mobile/offline
- **User Guidance**: Contextual help and error resolution
- **Retry Mechanisms**: Automatic retries for failed operations

### **18. Accessibility Features (LOW PRIORITY)**
**Status**: ❌ NOT IMPLEMENTED  
**Impact**: Limited accessibility compliance

#### **Required Features**:
- **ARIA Labels**: Screen reader support
- **Keyboard Navigation**: Keyboard-only navigation
- **Color Contrast**: Accessibility compliance

---

## **Priority 8: Data Provider Onboarding Agent**

### **19. Data Provider Onboarding Agent Development (HIGH PRIORITY)**
**Status**: ❌ NOT IMPLEMENTED  
**Priority**: HIGH  
**Files**: New agent implementation needed

#### **Required Implementation**:
- Create specialized onboarding agent for three data provider types:
  1. **Scientists** - Academic/research data providers with technical expertise
  2. **Local Knowledge Experts** - Community members with practical experience
  3. **Indigenous Knowledge Holders** - Cultural experts with traditional wisdom

#### **Agent Requirements**:
- **Type-Specific Onboarding Flows**: Different onboarding processes for each provider type
- **Credential Verification**: Academic credentials for scientists, community validation for locals, cultural authority verification for indigenous experts
- **Data Quality Standards**: Quality assessment protocols for each provider type
- **Payment Integration**: Google Pay APIs integration for volume-based compensation
- **Cultural Sensitivity**: Cultural protocol integration for indigenous knowledge holders
- **Confidentiality Protocols**: Zero-knowledge architecture and cross-verification processes
- **Collaboration Features**: Secure networking between data providers
- **Quality Assessment**: Automated quality metrics and verification processes

#### **Implementation Notes**:
- Integration with existing multi-agent system architecture
- Google Cloud Platform integration for secure processing
- Cultural protocol compliance for indigenous knowledge holders
- Collective payment distribution for indigenous communities

---

## **Priority 9: Documentation and System Updates**

### **20. Table of Contents Requirement (MEDIUM PRIORITY)**
**Status**: ❌ NOT IMPLEMENTED  
**Impact**: Poor documentation organization

#### **Required Implementation**:
- Add comprehensive table of contents to all documentation files
- Ensure consistent navigation across all prototype files
- Update documentation structure for better organization
- Implement cross-referencing between related documents

### **21. System Documentation Updates (MEDIUM PRIORITY)**
**Status**: 🔄 PARTIALLY IMPLEMENTED  
**Impact**: Outdated system documentation

#### **Required Updates**:
- Update 3.0_GCP_Leveraged_For_User_Needs.md file with current GCP integration status
- Review and update engineering roadmap with current implementation status
- Update technical PRD with latest system capabilities
- Ensure all documentation reflects current system architecture

---

## Change Log

### **July 13, 2025**
- **Reorganization**: Completely restructured todo file with new priority system
- **Data Source Integration**: Added Priority 2 section for Federal Reserve APIs and economic data sources
- **MCP Server Integration**: Added Priority 3 section for core and specialized MCP servers
- **Future Feature Integration**: Added Priority 4 section for notification system and monitoring features
- **Documentation Updates**: Added Priority 9 section for documentation and system updates
- **Removed Items**: Removed specific user story completion items for 0.65, 0.71, and 0.711 as requested

### **July 12, 2025**
- **Date Update**: Updated last modified date to reflect current work session
- **File Reference**: Added to 0.6_All_Prototypes.md overview
- **Initial Creation**: Created India prototype documentation file with date headers and change log structure
- **Content Implementation**: Added sections 4, 5, and 5.1 with extreme weather risk data sources and multi-agent system information

### **June 29, 2025**
- **Initial Creation**: Established comprehensive todo framework for Pythia development work
- **Priority Definition**: Defined priority system for development tasks
- **Component Documentation**: Documented critical missing components and implementation requirements