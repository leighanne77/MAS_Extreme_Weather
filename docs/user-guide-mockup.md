# Pythia User Guide - Web Dashboard Interface

## Overview

Pythia is an AI-powered extreme weather risk assessment tool that helps capital market actors understand environmental risks and find nature-based resilience solutions. The web dashboard provides an intuitive interface for interacting with our multi-agent AI system through natural language queries and advanced filtering.

## Technology Stack

- **Frontend**: Vanilla JavaScript, Chart.js, CSS Grid/Flexbox
- **Backend**: FastAPI, Google ADK, A2A Protocol
- **Data Sources**: NOAA SWDI, Nature-Based Solutions Database, Enhanced Data Sources
- **Visualization**: Chart.js with dynamic chart selection
- **Mobile**: Responsive design for all devices
- **API**: RESTful endpoints with JSON responses

## Quick Start

### 1. Select Your User Type
Choose from 8 specialized user types, each with tailored features:
- **Private Equity**: Investment analysis and asset protection
- **Private Debt**: Debt risk assessment and collateral analysis
- **Loan Officer**: Agricultural and commercial lending support
- **Data Science**: Model validation and data integration
- **Risk Officer**: Portfolio-level risk management
- **Sustainability Officer**: ESG compliance and green financing
- **Credit Officer**: Seasonal credit and working capital analysis
- **Government Funder**: Rural development and infrastructure planning

### 2. Enter Location and Query
- **Location Input**: Text entry or interactive map selection
- **Natural Language Queries**: Ask about risks, adaptation strategies, or financial impacts
- **Query Suggestions**: AI-powered suggestions based on your user type
- **Time Range**: Select 5, 7, or 10 years for analysis

### 3. Apply Filters and Visualizations
- **Advanced Filtering**: Multiple filter categories for precise results
- **Dynamic Visualizations**: Choose from various chart types
- **Real-time Updates**: Refresh data and apply new filters
- **Export Options**: Download results in multiple formats

## Interface Components

### Sidebar Navigation

The sidebar contains all input controls and configuration options:

#### User Type Selection
```
┌─────────────────────────────────────────┐
│ User Type: [Private Equity ▼]           │
│                                         │
│ Available Types:                        │
│ • Private Equity                        │
│ • Private Debt                          │
│ • Loan Officer                          │
│ • Data Science                          │
│ • Risk Officer                          │
│ • Sustainability Officer                │
│ • Credit Officer                        │
│ • Government Funder                     │
└─────────────────────────────────────────┘
```

#### Location Input
```
┌─────────────────────────────────────────┐
│ Location: [Mobile Bay, Alabama]         │
│ [Select on Map]                         │
│                                         │
│ Selected: Mobile Bay, Alabama           │
│ Coordinates: 30.6954°N, 88.0399°W      │
└─────────────────────────────────────────┘
```

#### Query Input
```
┌─────────────────────────────────────────┐
│ Query:                                  │
│ [What are hurricane risks for           │
│  manufacturing facilities in Mobile     │
│  Bay and what adaptation strategies     │
│  would protect the investment?]         │
│                                         │
│ [Submit Query]                          │
└─────────────────────────────────────────┘
```

#### Query Suggestions
```
┌─────────────────────────────────────────┐
│ Suggested Queries:                      │
│ • Water scarcity risks for farm loans   │
│ • Hurricane protection strategies       │
│ • Drought impact on crop yields         │
│ • Flood risk assessment                 │
└─────────────────────────────────────────┘
```

### Advanced Filtering System

#### Filter Categories
```
┌─────────────────────────────────────────┐
│ Filters:                                │
│                                         │
│ Time Period: [All Years ▼]              │
│ Risk Level: [All Risk Levels ▼]         │
│ Category: [All Categories ▼]            │
│ Confidence: [All Confidence Levels ▼]   │
│ Financial Impact: [All Impact Levels ▼] │
│ Resilience Options: [All Options ▼]     │
│                                         │
│ [Apply Filters] [Clear All] [Save Preset]│
└─────────────────────────────────────────┘
```

#### Filter Options
- **Time Period**: 5, 7, 10 years or custom ranges
- **Risk Level**: Low, Medium, High, Extreme
- **Category**: Weather, Climate, Infrastructure, etc.
- **Confidence Level**: 40-99% ranges
- **Financial Impact**: High (10%+), Medium (3-10%), Low (<3%)
- **Resilience Options**: Nature-based, Infrastructure, Hybrid

### Main Content Area

#### Visualization Controls
```
┌─────────────────────────────────────────┐
│ Visualization: [Risk Assessment ▼]      │
│ Timeframe: [2026-2032 ▼]                │
│ [Refresh Data]                          │
│ Last Updated: 2025-01-15 14:30          │
└─────────────────────────────────────────┘
```

#### Results Display
```
┌─────────────────────────────────────────┐
│ Risk Assessment Results                 │
│                                         │
│ Overall Risk: HIGH (85% confidence)     │
│                                         │
│ Risk Breakdown:                         │
│ • Hurricane: HIGH (90%)                 │
│ • Storm Surge: HIGH (85%)               │
│ • Sea Level Rise: MEDIUM (75%)          │
│                                         │
│ Resilience Options (3 found):           │
│ • Mangrove Restoration (ROI: 15.2%)     │
│ • Elevated Foundation (ROI: 8.7%)       │
│ • Rainwater Harvesting (ROI: 12.1%)     │
└─────────────────────────────────────────┘
```

## User Type-Specific Features

### Private Equity Investors
**Focus**: Asset protection and investment optimization
- **Query Examples**:
  - "What are hurricane risks for manufacturing facilities in Mobile Bay?"
  - "What adaptation strategies would protect our infrastructure investment?"
- **Key Features**:
  - Asset value impact analysis
  - Infrastructure adaptation options
  - Cost-benefit analysis
  - Timeline for implementation

### Loan Officers
**Focus**: Agricultural and commercial lending risk assessment
- **Query Examples**:
  - "What are water scarcity risks for a farm loan in West Kansas?"
  - "How will drought affect crop yields and loan repayment?"
- **Key Features**:
  - Collateral value risk assessment
  - Default probability timeline
  - Water management adaptation strategies
  - ROI analysis for adaptation investments

### Risk Officers
**Focus**: Portfolio-level risk management and compliance
- **Query Examples**:
  - "What are portfolio-level extreme weather risks for agricultural lending?"
  - "How should we allocate capital for climate resilience?"
- **Key Features**:
  - Portfolio risk distribution
  - Capital allocation recommendations
  - Stress testing scenarios
  - Regulatory compliance insights

### Data Science Officers
**Focus**: Model validation and data integration
- **Query Examples**:
  - "Validate our agricultural risk models with extreme weather data"
  - "What data sources should we integrate for better predictions?"
- **Key Features**:
  - Data quality metrics
  - Model performance benchmarks
  - Integration best practices
  - Validation dataset sources

## API Endpoints

### Core Endpoints

#### User Management
- `POST /api/user/onboarding` - Create user session
- `GET /api/user-types` - Get available user types

#### Query Processing
- `POST /api/query/process` - Process natural language queries
- `GET /api/session/{session_id}` - Get session status

#### Analysis Features
- `POST /api/scenarios/generate` - Generate analysis scenarios
- `POST /api/filters/apply` - Apply advanced filters
- `GET /api/agents/status` - Check agent system status

#### Export and Reporting
- `POST /api/export/report` - Generate reports (PDF, Excel, Presentation)

#### System Health
- `GET /api/health` - System health check

### Response Format
```json
{
  "status": "success",
  "result": {
    "risk_assessment": {...},
    "resilience_options": [...],
    "roi_analysis": {...},
    "confidence_levels": {...}
  },
  "formatted_response": "...",
  "intent": "risk_analysis"
}
```

## Understanding Results

### Risk Levels
- **LOW**: Minimal impact expected (<3% of asset value)
- **MEDIUM**: Moderate impact, monitoring recommended (3-10% of asset value)
- **HIGH**: Significant impact, action required (10-25% of asset value)
- **EXTREME**: Severe impact, immediate action needed (>25% of asset value)

### Confidence Levels
- **95-99%**: Very high confidence - Strong data support
- **80-94%**: High confidence - Good data quality
- **60-79%**: Moderate confidence - Some uncertainty
- **40-59%**: Low confidence - Limited data
- **<40%**: Very low confidence - Emerging risks

### ROI Interpretation
- **Positive ROI**: Investment pays for itself over time
- **High ROI (>10%)**: Excellent investment opportunity
- **Moderate ROI (5-10%)**: Good investment with clear benefits
- **Low ROI (<5%)**: Consider alternatives or longer timeframes

## Advanced Features

### Session Management
- **Persistent Sessions**: User preferences and history saved
- **Cross-Browser**: Sessions work across different browsers
- **Export History**: Download previous analyses
- **Filter Presets**: Save and reuse filter configurations

### Map Integration
- **Interactive Selection**: Click on map to select locations
- **Coordinate Display**: Shows exact latitude/longitude
- **Address Validation**: Automatic address verification
- **Boundary Detection**: Identifies city/county boundaries

### Visualization System
- **Dynamic Charts**: Multiple chart types available
- **Interactive Elements**: Hover for details, click to drill down
- **Export Options**: Download charts as images
- **Real-time Updates**: Refresh data without page reload

### Export Capabilities
- **JSON Export**: Complete analysis data
- **PDF Reports**: Formatted reports with charts
- **Excel Spreadsheets**: Tabular data for analysis
- **Presentation Slides**: Ready-to-use slides

## Troubleshooting

### Common Issues

**"No results found"**
- Check location spelling and format
- Try a broader location (county instead of city)
- Ensure query is specific enough
- Verify user type selection

**"Analysis failed"**
- Check internet connection
- Verify system status at `/api/health`
- Try again in a few minutes
- Contact support if persistent

**"Low confidence results"**
- This is normal for emerging risks
- Consider multiple scenarios
- Focus on high-confidence aspects
- Use longer time periods for better data

**"Filters not working"**
- Ensure filters are applied after query
- Check filter combinations
- Clear filters and try again
- Verify session is active

### Getting Better Results

1. **Be Specific**: Include asset type, location, and time period
2. **Use Appropriate User Type**: Select the user type that matches your role
3. **Ask About Solutions**: Include "adaptation strategies" or "resilience options"
4. **Consider Multiple Scenarios**: Ask about different time periods
5. **Focus on ROI**: Include "financial impact" or "ROI" in queries
6. **Use Query Suggestions**: Start with suggested queries for your user type

## Best Practices

### Query Formulation
✅ **Good:** "What are drought risks for a cattle operation in West Kansas over the next 7 years?"
❌ **Poor:** "What about weather?"

✅ **Good:** "What adaptation strategies would protect a data center from extreme heat in Phoenix?"
❌ **Poor:** "How to protect from heat?"

### Location Specification
✅ **Good:** "Mobile Bay, Alabama" or "Kansas City, Kansas"
❌ **Poor:** "The South" or "Kansas"

### Time Periods
- **5 Years**: Short-term planning and immediate risks
- **7 Years**: Standard investment horizon (recommended)
- **10 Years**: Long-term strategic planning

### Filter Usage
- **Start Broad**: Begin with minimal filters
- **Refine Gradually**: Add filters based on initial results
- **Save Presets**: Save useful filter combinations
- **Clear Regularly**: Reset filters for new queries

## Support and Documentation

### Documentation
- This user guide
- API documentation (for developers)
- Case studies and examples
- Video tutorials

### Contact Information
- **Technical Support**: support@pythia.com
- **Feature Requests**: feedback@pythia.com
- **Business Inquiries**: sales@pythia.com
- **API Support**: api-support@pythia.com

### System Requirements
- **Browser**: Modern browser with JavaScript enabled
- **Internet**: Stable internet connection required
- **Screen**: Minimum 1024px width for optimal experience
- **Mobile**: Responsive design for tablets and phones

---

**Remember**: Pythia's AI agents do the heavy lifting. The web interface is designed to make their insights accessible and actionable. Focus on asking good questions, using appropriate filters, and interpreting the results for your specific needs.
