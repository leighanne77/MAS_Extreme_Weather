# Tool - Multi-Agent Extreme Weather Risk Analysis System

---

## 🎯 Quick Demo

### Try the Web Dashboard
```bash
# Start the web interface
python -m uvicorn src.tool_web.interface:app --reload --host 0.0.0.0 --port 8000

# Open http://localhost:8000 in your browser
```

### Run Demo Scripts
```bash
# Basic system demo
python demo.py

# Test data files
python test_data_files.py

# Simple example
python simple_example.py
```

### Example User Journey: Private Equity Investor

1. **Select User Type**: Choose "Private Equity Investor" from the role selector
2. **Enter Location**: "Urban southern Brazil, coastal infrastructure, 7-year horizon"
3. **View Results**: 
   - Extreme Weather Risk Score (e.g., High)
   - Top Risks: Flooding, Heat, Storm Surge
   - Confidence Level: 0.87
   - ROI Analysis: Projected IRR impact, cost/benefit of resilience options
4. **Explore Solutions**: Mangrove Restoration (ROI: 15%, Payback: 4 years)
5. **Export Report**: PDF/JSON for stakeholders

---

## 🎯 What This System Does

- **Risk Assessment**: Analyzes extreme weather risks for specific locations
- **Nature-Based Solutions**: Provides proven adaptation strategies with cost/benefit analysis
- **Financial Analysis**: Calculates ROI for climate resilience investments
- **Data Integration**: Combines weather data, environmental data, and scientific research
- **Multi-Agent Intelligence**: Uses specialized AI agents for different aspects of risk analysis
- **Interactive Dashboard**: Web-based interface for data visualization and analysis
- **API-First Design**: RESTful API for programmatic access and integration
- **A2A Protocol**: Complete Agent-to-Agent communication protocol implementation
- **8 Specialized User Types**: Tailored experience for different professional roles

## 🚀 Quick Start

1. **Clone and setup:**
```bash
git clone <repository-url>
cd 004_MAS_Climate
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

2. **Start the web dashboard:**
```bash
python -m uvicorn src.tool_web.interface:app --reload --host 0.0.0.0 --port 8000
```

3. **Open your browser:**
Navigate to `http://localhost:8000` and start analyzing!

## Key Features

- **🌿 Nature-Based Solutions**: 500+ climate resilience solutions with cost/benefit analysis
- **💰 Financial Analysis**: ROI calculations for climate resilience investments
- **🤖 Multi-Agent Architecture**: Specialized agents for risk analysis and recommendations
- **📊 Advanced Analytics**: Historical trends, pattern detection, and risk assessment
- **🔧 ADK Integration**: Google's Agent Development Kit for enhanced performance
- **📈 Cost/Benefit Analysis**: Detailed financial analysis for resilience investments
- **🎯 Location-Specific**: Tailored solutions for any geographic area
- **⚡ Function-Based Tools**: Python functions automatically wrapped by ADK
- **🌐 Web Dashboard**: Interactive data visualization and analysis interface
- **📱 Mobile Responsive**: Works on desktop, tablet, and mobile devices
- **🔗 API-First Design**: RESTful API for programmatic access and integration
- **🔄 A2A Protocol**: Complete Agent-to-Agent communication protocol
- **📋 Task Management**: Complete task lifecycle with state tracking
- **📦 Artifact Management**: Full artifact lifecycle with storage and retrieval
- **🔄 Retry Logic**: Enhanced retry logic with exponential backoff
- **⚡ Caching System**: Performance optimization with session-level caching
- **🛡️ Security**: Comprehensive authentication, validation, and permission checking
- **📊 Performance Monitoring**: Real-time metrics and system health monitoring
- **👥 8 User Types**: Specialized configurations for different professional roles
- **🌍 Global Coverage**: International data sources and regional adaptations
- **📊 Data Management**: 20 specialized data management agents

## Technology Stack

### Backend
- **FastAPI**: High-performance Python web framework
- **Google ADK**: Agent Development Kit for multi-agent orchestration
- **A2A Protocol**: Complete Agent-to-Agent communication protocol
- **SQLite/PostgreSQL**: Database for artifacts and session data
- **Redis**: Caching and session management

### Frontend
- **Vanilla JavaScript**: Lightweight, no framework overhead
- **Chart.js**: Interactive data visualization
- **CSS Grid/Flexbox**: Responsive design
- **WebSocket**: Real-time data updates

### Data Sources
- **NOAA SWDI**: Weather and climate data
- **OpenWeatherMap**: Current weather information
- **Nature-Based Solutions Database**: 500+ proven adaptation strategies
- **Enhanced Data Sources**: International and specialized datasets
- **Regional Data**: Prototype-specific data for all geographic regions

## User Types

The system supports 8 specialized user types:

### 1. **Private Equity Investor**
- **Focus**: Investment analysis and asset protection
- **Example Query**: "What are hurricane risks for manufacturing facilities in Mobile Bay?"

### 2. **Loan Officer (Agricultural)**
- **Focus**: Agricultural and commercial lending support
- **Example Query**: "What are water scarcity risks for cattle operations in western Kansas?"

### 3. **Data Science Officer**
- **Focus**: Model validation and data integration
- **Example Query**: "Validate our agricultural risk models with extreme weather data"

### 4. **Chief Risk Officer**
- **Focus**: Portfolio-level risk management
- **Example Query**: "Assess portfolio-level extreme weather risks for agricultural lending"

### 5. **Chief Sustainability Officer**
- **Focus**: ESG compliance and green financing
- **Example Query**: "Develop ESG compliance strategies for sustainable lending programs"

### 6. **Crop Insurance Officer**
- **Focus**: Insurance risk assessment and claims analysis
- **Example Query**: "How do regenerative farming practices affect crop insurance risks?"

### 7. **Credit Officer**
- **Focus**: Seasonal credit and working capital analysis
- **Example Query**: "Manage seasonal credit lines for dairy operations in Wisconsin"

### 8. **Government Funder**
- **Focus**: Rural development and infrastructure planning
- **Example Query**: "Plan rural development investments in drought-affected districts"

## A2A Protocol Implementation

The system includes a **complete A2A (Agent-to-Agent) protocol implementation**:

### Core A2A Features ✅
- **Message Structure**: Complete A2A message envelope with headers and validation
- **Message Routing**: Agent registration, discovery, and message delivery
- **Task Management**: Full task lifecycle with state tracking and execution
- **Artifact Management**: Complete artifact lifecycle with storage and retrieval
- **Content Handlers**: Support for text, data, file, image, audio, and video content
- **Error Handling**: Comprehensive error recovery with retry logic and circuit breakers
- **Performance Optimization**: Caching, routing optimization, and monitoring

### A2A Usage Examples

```python
# Create and send A2A message
from multi_agent_system.a2a import create_request_message, create_text_part, MessageType

message = create_request_message(
    sender="risk_analyzer",
    recipients=["validation_agent"],
    parts=[create_text_part("Analyze flood risks for NYC")],
    message_type=MessageType.REQUEST
)

# Route message through system
success = await router.route_message(message)
```

## Function-Based Tools

Our system uses ADK's elegant function-based tool approach:

```python
# Simple function-based tool
def analyze_climate_risk(location: str, time_period: str) -> Dict[str, Any]:
    """Analyzes climate risks for a specific location and time period."""
    try:
        return {
            "status": "success",
            "data": {
                "location": location,
                "time_period": time_period,
                "risk_assessment": {
                    "flooding": "medium",
                    "heat_wave": "high",
                    "storm": "low"
                },
                "confidence": 0.85
            }
        }
    except Exception as e:
        return {"status": "error", "error_message": str(e)}

# Create agent with function-based tools
climate_agent = Agent(
    name="climate_analyzer",
    description="Expert in climate risk analysis",
    instruction="Analyze climate risks and provide recommendations",
    tools=[analyze_climate_risk]  # Function is automatically wrapped as a tool
)
```

### Available Tools

- **`analyze_climate_risk(location, time_period, risk_types)`**: Analyzes climate risks for a location
- **`get_weather_data(location, data_sources)`**: Retrieves current weather data
- **`get_nbs_solutions(location, risk_types, solution_scale)`**: Finds nature-based solutions
- **`calculate_cost_benefit(solution_id, property_value, timeframe_years)`**: Performs financial analysis
- **`generate_recommendations(risk_analysis, location, solution_types)`**: Creates comprehensive recommendations
- **`validate_and_geocode(address, validation_level, include_metadata)`**: Validates and geocodes addresses

## 📦 Installation

### Prerequisites
- Python 3.12 or higher
- Git
- Modern web browser (for dashboard access)
- Google Cloud account (optional - for advanced features)

### Step-by-Step Setup

1. **Clone the repository:**
```bash
git clone https://github.com/leighanne77/MAS_Extreme_Weather.git
cd MAS_Extreme_Weather
```

2. **Create and activate virtual environment:**
```bash
python3.12 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies:**
```bash
pip install -r requirements.txt
```

4. **Set up environment variables (optional):**
```bash
cp .env.example .env
# Edit .env with your settings
```

5. **Verify installation:**
```bash
python -c "from src.multi_agent_system import agent_team; print('Installation successful!')"
```

## 🚀 Usage

### Web Dashboard (Recommended)

1. **Start the web server:**
```bash
python -m uvicorn src.tool_web.interface:app --reload --host 0.0.0.0 --port 8000
```

2. **Open your browser:**
Navigate to `http://localhost:8000` to access the interactive dashboard

3. **Use the dashboard:**
- Select your user type from 8 specialized options
- Enter a location (e.g., "Kansas City, MO")
- Ask questions in natural language
- View interactive charts and recommendations
- Export results in various formats

### API Usage

```python
import requests

# Get available user types
response = requests.get("http://localhost:8000/api/user-types")
user_types = response.json()

# Process a user query
response = requests.post("http://localhost:8000/api/query/process", data={
    "query": "What are hurricane risks for manufacturing facilities in Mobile Bay?",
    "session_id": "test_session",
    "user_type": "private_equity"
})

result = response.json()
```

### Programmatic Usage

```python
from src.multi_agent_system import agent_team
from src.multi_agent_system.session_manager import SessionManager

# Create a session
session_manager = SessionManager()
session = session_manager.create_session("test_user")

# Get the agent team
team = agent_team.get_agent_team()

# Analyze a location
result = team.analyze_location(
    session=session,
    location="Kansas City, MO",
    analysis_type="comprehensive"
)

print(f"Risk Level: {result['risk_level']}")
print(f"Recommendations: {len(result['recommendations'])} found")
```

## 🎯 What You Can Do

### For Financial Institutions
- Assess extreme weather risks for loan portfolios
- Evaluate collateral value impacts from environmental factors
- Calculate ROI for climate resilience investments
- Generate risk reports for regulatory compliance
- Access interactive dashboard for portfolio analysis
- Use specialized user types for different roles

### For Property Owners
- Identify location-specific weather risks
- Find proven nature-based solutions
- Calculate cost/benefit of resilience measures
- Get implementation guidance
- Use web dashboard for property analysis

### For Investors
- Analyze environmental risks in investment decisions
- Evaluate climate resilience as investment criteria
- Assess long-term value impacts
- Compare risk profiles across locations
- Access API for integration with existing systems
- Use specialized analysis for different investment types

### Data Sources Available
- **Weather Data**: NOAA SWDI, historical weather patterns
- **Nature-Based Solutions**: 500+ proven adaptation strategies
- **Environmental Data**: Ecosystem services, biodiversity metrics
- **Financial Data**: Cost/benefit analysis, ROI calculations
- **Enhanced Data**: International and specialized datasets
- **Regional Data**: Prototype-specific data for all geographic regions

## ⚠️ Important Limitations

### What This System Does NOT Do
- **No Carbon Trading**: Does not provide carbon credits or carbon market analysis
- **No Proprietary Data Access**: Does not access your internal business data
- **No Real-Time Feeds**: Weather data is cached and updated periodically
- **No Automated Decisions**: Provides insights to support human decision-making
- **No Financial Advice**: Does not provide investment or financial advice

### Data Privacy
- All analysis is performed on external data sources
- No personal or proprietary information is stored
- Results can be exported for integration with your systems
- No access to your internal databases or systems

### Technical Limitations
- Requires internet connection for data updates
- Frontend requires modern web browser with JavaScript enabled
- Dashboard optimized for desktop but mobile-responsive
- Some features require Google Cloud setup
- Performance depends on data source availability
- Not designed for real-time trading or high-frequency analysis

## 🔧 Troubleshooting

### Common Issues

**Import Errors:**
```bash
# Make sure you're in the virtual environment
source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
```

**Web Dashboard Issues:**
```bash
# Check if server is running
curl http://localhost:8000/api/health

# Check browser console for JavaScript errors
# Ensure JavaScript is enabled in your browser
```

**Data Source Errors:**
```bash
# Check internet connection
# Verify API keys if using external services
# Check data source availability
```

**Google Cloud Issues:**
```bash
# Verify credentials are set correctly
echo $GOOGLE_APPLICATION_CREDENTIALS

# Check project permissions
gcloud auth list
```

### Getting Help
- Open an issue on GitHub for bugs

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support, please open an issue in the GitHub repository or contact the maintainers. 
