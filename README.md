# Multi-Agent Climate Risk Analysis System

This project implements a comprehensive multi-agent system for climate risk analysis, combining specialized agents, workflow management, and advanced coordination capabilities.

## Key Features

- **Function-Based Tools**: Tools are implemented as regular Python functions, which the ADK framework automatically wraps as tools when added to an agent's tools list.
- **Multi-Agent Architecture**: Specialized agent roles, coordinated execution, state management, and error handling.
- **Workflow Management**: Process orchestration, state tracking, error recovery, and progress monitoring.
- **Communication System**: Inter-agent messaging, state synchronization, error propagation, and heartbeat monitoring.
- **Artifact Management**: Output storage, version control, cleanup policies, and access control.
- **Observability**: Performance metrics, error tracking, pattern analysis, and system health monitoring.

## Example Usage

```python
from src.multi_agent_system.agent_team import AgentTeam
from google.adk.agents import Agent

# Create agent team
team = AgentTeam([
    Agent(
        model='gemini-2.0-flash',
        name='climate_agent',
        instruction='You are an expert climate risk analyst.',
        description='Agent for analyzing climate risks'
    )
])

# Execute analysis
result = team.execute_analysis(
    location="New York",
    time_period="2024-2025"
)
```

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/multi-agent-climate-risk.git
   cd multi-agent-climate-risk
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the tests:
   ```bash
   python tests/test_runner.py
   ```

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Overview
This system provides a multi-agent architecture for comprehensive climate risk analysis, featuring specialized agents for different aspects of risk assessment and management.

## Project Structure
```
project-root/
│
├── src/
│   └── multi_agent_system/
│       ├── agent_team.py
│       ├── agent_tools.py
│       ├── enhanced_coordinator.py
│       ├── communication.py
│       ├── artifact_manager.py
│       ├── workflows.py
│       ├── adk_integration.py
│       ├── session_manager.py
│       ├── risk_definitions.py
│       ├── weather_risks.py
│       └── observability.py
├── tests/
├── docs/
└── ...
```

## Installation

### Virtual Environment Setup (Required)
```bash
# Create a virtual environment
python -m venv venv

# Activate the virtual environment
# On Unix/macOS:
source venv/bin/activate
# On Windows:
# venv\Scripts\activate

# Verify activation (should show path to venv)
which python  # Unix/macOS
# where python  # Windows
```

### Package Installation
```bash
# Ensure you're in the virtual environment
pip install -e .
```

## Usage Example
```python
from src.multi_agent_system.agent_team import AgentTeam
from src.multi_agent_system.enhanced_coordinator import EnhancedADKCoordinator

team = AgentTeam([...])
coordinator = EnhancedADKCoordinator(team)
result = coordinator.execute_analysis(location="Orlando, FL", time_period="2024-2025")
```

## Documentation
See the [docs/](docs/) directory for detailed documentation.

## Documentation

All documentation is now organized in the `docs` directory. Please refer to the following sections:

- [Documentation Index](docs/index.md)
- [System Overview](docs/overview.md)
- [API Reference](docs/api-reference.md)
- [Data Definitions](docs/data-definitions.md)
- [Project Structure](docs/project-structure.md)
- [Project Timeline](docs/timeline.md)
- [TODO List](docs/todo.md)

## Quick Start

1. **Clone the repository**
```bash
git clone https://github.com/leighanne77/MAS_Extreme_Weather.git
cd MAS_Extreme_Weather
```

2. **Set up virtual environment (Required)**
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Unix/macOS:
source venv/bin/activate
# On Windows:
# venv\Scripts\activate

# Verify activation
which python  # Unix/macOS
# where python  # Windows
```

3. **Install the package**
```bash
# Install in development mode
pip install -e .

# Or install dependencies only
pip install -r requirements.txt
```

4. **Configure Google Cloud credentials**
```bash
# Set your Google Cloud credentials
export GOOGLE_APPLICATION_CREDENTIALS="path/to/your/credentials.json"
```

5. **Run the application**
```bash
python app.py
```

6. **Deactivate virtual environment when done**
```bash
deactivate
```

For more detailed information, please refer to the [documentation](docs/index.md).

## License

[Your License Here]

## Support

For support and questions:
- Email: support@example.com
- Documentation: https://docs.example.com
- Status: https://status.example.com

## Key Features

### Performance Optimization
- **Efficient Caching System**
  - Configurable cache durations for different types of data
  - Automatic cache invalidation based on data freshness requirements
  - Smart caching for frequently accessed data
  - Reduced API calls and database queries

### Personalized User Experience
- **User Preference Management**
  - Language preferences
  - Unit system preferences (metric/imperial)
  - Location-based customization
  - Historical interaction tracking
  - Personalized recommendations

### Advanced State Management
- **Robust Session Handling**
  - Persistent session state
  - Context-aware operations
  - State synchronization across agents
  - Efficient state updates
  - Automatic state cleanup

### Resource Efficiency
- **Optimized Resource Usage**
  - Concurrent task execution
  - Smart data caching
  - Efficient memory management
  - Reduced redundant operations
  - Optimized API calls

### Comprehensive Error Handling
- **Robust Error Management**
  - Graceful error recovery
  - Detailed error logging
  - Automatic retry mechanisms
  - User-friendly error messages
  - State preservation during errors

## System Architecture

### Core Components
- **Agent Team Manager**: Coordinates specialized agents
- **Session Manager**: Handles user sessions and state
- **Tool Manager**: Manages agent capabilities and tools
- **State Manager**: Handles data persistence and caching

### Specialized Agents
1. **Root Orchestrator**
   - Task delegation
   - Result validation
   - Error handling
   - State management

2. **Analysis Agents**
   - Risk Analyzer
   - Historical Analyzer
   - Data Validator

3. **Monitoring Agents**
   - News Monitor
   - Alert Monitor

4. **Interaction Agents**
   - Greeting Agent
   - Farewell Agent

5. **Support Agents**
   - Validation Agent
   - Recommendation Agent

## Usage

```python
from multi_agent_system.agent_team import AgentTeamManager

# Initialize the agent team
team_manager = AgentTeamManager()

# Handle a user request
response = await team_manager.handle_request(
    user_id="user123",
    request="Analyze climate risks in New York"
)
```

## Configuration

The system can be configured through environment variables:

```bash
# Cache durations (in seconds)
RISK_ANALYSIS_CACHE_DURATION=3600
HISTORICAL_DATA_CACHE_DURATION=86400
NEWS_CACHE_DURATION=1800
ALERTS_CACHE_DURATION=300

# API configurations
API_KEY=your_api_key
API_ENDPOINT=your_endpoint
```

## Best Practices

1. **State Management**
   - Use the provided caching mechanisms
   - Keep state updates atomic
   - Validate state changes
   - Clean up unused state

2. **Error Handling**
   - Use the built-in retry mechanisms
   - Log errors appropriately
   - Preserve state during errors
   - Provide user-friendly messages

3. **Performance**
   - Utilize caching effectively
   - Monitor cache hit rates
   - Adjust cache durations as needed
   - Clean up expired cache entries

4. **Resource Usage**
   - Monitor memory usage
   - Clean up unused resources
   - Use concurrent execution when appropriate
   - Optimize API calls

## Architecture Decision

### Hybrid Approach: Custom Core + ADK Coordination

We have chosen a hybrid architecture that combines our custom implementation with Google's Agent Development Kit (ADK) for the following reasons:

1. **Core Components (Custom)**
   - Climate-specific risk analysis logic
   - Weather data caching and processing
   - Specialized agent tools for climate analysis
   - Custom session management for climate data

   *Rationale: These components are highly specialized for climate risk analysis and have been optimized for our specific use case.*

2. **Agent Coordination (ADK)**
   - Multi-agent system orchestration
   - Event handling and communication
   - Workflow management
   - Session state management

   *Rationale: ADK provides robust, tested patterns for agent coordination while allowing us to maintain our specialized core functionality.*

### Migration Plan

#### Phase 1: Integration (Current)
- [ ] Keep core climate analysis logic
- [ ] Add ADK for agent coordination
- [ ] Set up parallel testing environment
- [ ] Implement basic ADK workflow patterns

#### Phase 2: Enhancement
- [ ] Integrate ADK's event system
- [ ] Implement advanced workflow patterns
- [ ] Maintain specialized tools
- [ ] Add monitoring and analytics

#### Phase 3: Optimization
- [ ] Identify best features from both systems
- [ ] Optimize performance
- [ ] Document hybrid architecture
- [ ] Implement automated testing

### Technical Details

#### Custom Components
```python
# Core climate analysis
class ClimateRiskAnalyzer:
    """Specialized risk analysis for climate data"""
    pass

# Weather data management
class WeatherDataCache:
    """Optimized caching for weather data"""
    pass

# Custom session management
class SessionManager:
    """Climate-specific session handling"""
    pass
```

#### ADK Integration
```python
from google.adk.agents import SequentialAgent, LlmAgent

class HybridAgentTeamManager:
    """Combines custom components with ADK coordination"""
    def __init__(self):
        # Custom components
        self.risk_analyzer = ClimateRiskAnalyzer()
        self.session_manager = SessionManager()
        
        # ADK workflow
        self.workflow = SequentialAgent(
            name="ClimateAnalysis",
            sub_agents=[
                LlmAgent(name="RiskAnalyzer", tools=[self.risk_analyzer.get_tools()]),
                LlmAgent(name="Recommendation", tools=[self.recommendation_tools])
            ]
        )
```

## Virtual Environment Management

### Best Practices
1. **Always use a virtual environment**
   - Prevents conflicts between project dependencies
   - Ensures reproducible development environment
   - Isolates project-specific packages

2. **Activation**
   - Always activate the virtual environment before working on the project
   - Verify activation by checking Python path
   - Deactivate when switching to other projects

3. **Dependencies**
   - Keep requirements.txt updated
   - Use `pip freeze > requirements.txt` to update dependencies
   - Install new packages only when virtual environment is active

4. **Troubleshooting**
   - If you see "command not found: python", ensure virtual environment is activated
   - If packages are not found, verify virtual environment activation
   - If you get permission errors, check virtual environment ownership

### Common Commands
```bash
# Create new virtual environment
python -m venv venv

# Activate
source venv/bin/activate  # Unix/macOS
# venv\Scripts\activate  # Windows

# Deactivate
deactivate

# Check installed packages
pip list

# Update requirements
pip freeze > requirements.txt
```

## Function-Based Tools

The ADK framework automatically wraps regular Python functions as tools when they are added to an agent's tools list. This approach provides flexibility and quick integration.

### Example: Creating and Using Function-Based Tools

```python
from multi_agent_system.adk_integration import ADKClient

# Define a function-based tool
def analyze_climate_risk(location: str, time_period: str) -> dict:
    """
    Analyzes climate risks for a specified location and time period.
    
    Args:
        location (str): The location to analyze
        time_period (str): The time period for analysis
        
    Returns:
        dict: Analysis results including risk levels and recommendations
    """
    try:
        # Implementation
        return {
            "status": "success",
            "risk_level": "high",
            "recommendations": ["action1", "action2"]
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }

# Create an agent with the function-based tool
climate_agent = ADKClient(
    model="gemini-pro",
    name="Climate Analyst",
    instruction="Analyze climate risks and provide recommendations",
    description="Expert in climate risk analysis",
    tools=[analyze_climate_risk]  # Function is automatically wrapped as a tool
)

# Use the agent
response = climate_agent.analyze_risk("New York", "2024")
print(response)
```

### Tool Parameters

When defining function-based tools:
- Use standard JSON-serializable types (string, integer, list, dictionary)
- Avoid default values for parameters
- Include clear type hints
- Document parameter requirements in docstrings

### Tool Return Values

Functions should return dictionaries with:
- A "status" key indicating success or error
- Relevant data in the response
- Proper error handling
- Consistent return formats
