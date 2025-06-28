# Getting Started with Tool Multi-Agent Extreme Weather Risk Analysis System

## 🌍 Overview

Tool is a sophisticated multi-agent system designed to help professionals make data-driven decisions about extreme weather risks. The system provides location-based risk analysis, adaptation strategy recommendations, and financial impact assessments without requiring access to users' proprietary data.

## 🚀 Quick Start

### 1. Run the Demo (No Installation Required)

```bash
# Run the system overview demo
python demo.py

# Run a simple working example
python simple_example.py
```

### 2. System Requirements

- Python 3.8+
- macOS, Linux, or Windows
- Internet connection for data sources
- 4GB+ RAM recommended

### 3. Installation Steps

#### Option A: Full Installation (Recommended)

```bash
# Clone the repository (if not already done)
git clone <repository-url>
cd 004_MAS_Climate

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the web interface
python src/tool_web/interface.py

# Open browser to http://localhost:8000
```

#### Option B: Minimal Installation (For Development)

```bash
# Install only essential packages
pip install fastapi uvicorn jinja2 python-multipart

# Run with basic functionality
python src/tool_web/interface.py
```

## 👥 User Types

The system supports 8 specialized user types:

1. **Private Equity Investor** - Asset protection and ROI analysis
2. **Loan Officer** - Agricultural lending risk assessment
3. **Chief Risk Officer** - Portfolio-level risk management
4. **Chief Sustainability Officer** - ESG compliance and green financing
5. **Data Science Officer** - Model validation and data integration
6. **Crop Insurance Officer** - Claims optimization and premium setting
7. **Credit Officer** - Seasonal credit and working capital management
8. **Government Funder** - Rural development and infrastructure planning

## 🔍 Example Queries

### Private Equity Investor
```
"What are hurricane risks for manufacturing facilities in Mobile Bay?"
```

### Loan Officer
```
"What are water scarcity risks for cattle operations in western Kansas over the next 7 years?"
```

### Chief Risk Officer
```
"What are portfolio-level extreme weather risks for our agricultural lending?"
```

### Data Science Officer
```
"Validate our agricultural risk models with extreme weather data"
```

## 🏗️ System Architecture

### Frontend Layer
- **Web Interface (FastAPI)** - Main user interface
- **User Onboarding** - Role selection and preferences
- **Query Interface** - Natural language processing
- **Results Display** - Interactive visualizations
- **Export Functions** - PDF, Excel, JSON export

### Integration Layer
- **Natural Language Processing** - Query parsing and intent recognition
- **User Type Management** - Role-specific customization
- **Session Management** - State persistence and user preferences
- **Data Formatting** - Response formatting for different user types

### Agent Layer
- **Risk Agent** - Analyzes extreme weather risks
- **Historical Agent** - Provides historical context
- **News Agent** - Integrates current events
- **Recommendation Agent** - Suggests adaptation strategies
- **Validation Agent** - Cross-validates results

### Data Layer
- **NOAA Weather Data** - Historical and forecast data
- **Nature-Based Solutions** - Adaptation strategy database
- **Historical Records** - Past extreme weather events
- **Economic Impact Data** - Financial analysis frameworks

## 📊 Key Features

### Risk Analysis
- Location-specific extreme weather risk assessment
- Multi-agent analysis with confidence levels
- Historical context and trend analysis
- Real-time data integration (when available)

### Adaptation Strategies
- Nature-first solution recommendations
- Cost-benefit analysis and ROI calculations
- Implementation timelines and success stories
- Regional adaptation effectiveness data

### Financial Impact
- Asset value protection analysis
- Insurance premium impact assessment
- Operational continuity planning
- Investment timeline optimization

### User Experience
- Natural language query processing
- Role-specific interface customization
- Interactive data visualizations
- Export and reporting capabilities

## 🔧 Configuration

### Environment Variables

```bash
# Google Cloud Configuration (for full functionality)
export GOOGLE_CLOUD_PROJECT="your-project-id"
export GOOGLE_APPLICATION_CREDENTIALS="path/to/credentials.json"

# System Configuration
export TOOL_LOG_LEVEL="INFO"
export TOOL_MAX_CONCURRENT_TASKS="5"
```

### Configuration Files

- `src/multi_agent_system/config.py` - Agent configuration
- `src/tool_web/config.py` - Web interface settings
- `docs/Do_not_do.md` - System limitations and guidelines

## 📈 Value Propositions

| User Type | Value Proposition |
|-----------|-------------------|
| Private Equity Investor | 20% improvement in risk-adjusted returns |
| Loan Officer | 20% reduction in weather-related defaults |
| Chief Risk Officer | 15% improvement in portfolio returns |
| Data Science Officer | Improved model accuracy |
| Crop Insurance Officer | 10% improvement in loss ratios |
| Credit Officer | 15-25% reduction in inefficiencies |
| Government Funder | Improved development outcomes |

## 🛠️ Development

### Project Structure

```
004_MAS_Climate/
├── src/
│   ├── multi_agent_system/     # Core agent system
│   ├── tool_web/            # Web interface
│   └── agentic_data_management/ # Data management
├── docs/                      # Documentation
├── tests/                     # Test suite
├── requirements.txt           # Dependencies
└── README.md                 # Project overview
```

### Running Tests

```bash
# Run all tests
pytest tests/

# Run specific test categories
pytest tests/test_agents_and_team.py
pytest tests/test_data_and_utils.py
```

### Code Quality

```bash
# Format code
black src/
isort src/

# Lint code
flake8 src/
mypy src/
```

## 📚 Documentation

- **User Stories**: `docs/user_story.md` - Detailed user requirements
- **User Personas**: `docs/user_personas.md` - User type descriptions
- **System Description**: `docs/system_description.md` - Technical overview
- **Do Not Do Guidelines**: `docs/Do_not_do.md` - System limitations

## 🚨 Troubleshooting

### Common Issues

1. **Architecture Compatibility**
   ```bash
   # If you see architecture errors, try:
   pip install --force-reinstall pydantic fastapi
   ```

2. **Missing Dependencies**
   ```bash
   # Install minimal dependencies
   pip install fastapi uvicorn jinja2
   ```

3. **Port Already in Use**
   ```bash
   # Use different port
   python src/tool_web/interface.py --port 8001
   ```

### Getting Help

1. Check the demo scripts first: `python demo.py`
2. Review the documentation in the `docs/` folder
3. Check the system logs for error messages
4. Verify your Python environment and dependencies

## 🎯 Next Steps

1. **Start with the demos** to understand the system capabilities
2. **Review the documentation** to understand user types and value propositions
3. **Set up the development environment** for full functionality
4. **Explore the web interface** to see the complete user experience
5. **Customize for your needs** by modifying agent configurations

## ✨ Key Benefits

- **No Proprietary Data Required** - Works with external data sources
- **Role-Specific Insights** - Tailored for different professional needs
- **Actionable Recommendations** - Clear adaptation strategies with ROI
- **Confidence Transparency** - All results include confidence levels
- **Export Capabilities** - Results can be integrated into existing workflows

---

**Ready to start?** Run `python demo.py` to see the system in action! 