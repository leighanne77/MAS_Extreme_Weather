# Climate Risk Analysis Multi-Agent System

A sophisticated multi-agent system for comprehensive climate risk analysis, featuring specialized agents for different aspects of risk assessment and management.

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

2. **Create and activate virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
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
from multi_tool_agent.agent_team import AgentTeamManager

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

## Installation

### Prerequisites
- Python 3.11 or higher
- Virtual environment (recommended)
- Google Cloud credentials (for ADK integration)

### Setup Steps

1. **Clone the repository**
```bash
git clone https://github.com/leighanne77/MAS_Extreme_Weather.git
cd MAS_Extreme_Weather
```

2. **Create and activate virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
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
export GOOGLE_CLOUD_PROJECT="your-project-id"
```

### Development Setup

The project uses `setup.py` for package management and installation. This allows for:
- Easy installation of the package and its dependencies
- Development mode installation with `pip install -e .`
- Proper Python path resolution for imports
- Version management

To modify the package configuration:
1. Update `setup.py` with new dependencies
2. Update version number when making releases
3. Add new packages to `install_requires` as needed

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Multi-Agent Climate Risk Analysis System

This project implements a multi-agent system for climate risk analysis, using specialized agents to analyze climate risks for a given location.

## Features

- **Multi-Agent System:** Uses a team of specialized agents for climate risk analysis.
- **Session Management:** Manages analysis sessions and agent states.
- **Communication Mechanisms:** Implements ADK-style communication patterns.
- **Web Interface:** A minimal FastAPI app for entering an address and viewing results.

## System Architecture

### Coordinator/Dispatcher Pattern

- **Central Agent (Root Orchestrator):**  
  The system uses a central agent (`AgentTeamManager`) that acts as a coordinator. It receives incoming requests (e.g., an address for climate risk analysis) and routes them to the appropriate specialized agents based on the task or domain.

- **Specialized Agents:**  
  Multiple specialized agents (e.g., `RiskAnalysisAgent`, `HistoricalAnalysisAgent`, `NewsMonitoringAgent`) handle specific aspects of the analysis. The central agent dispatches tasks to these agents based on their capabilities.

- **Task Routing:**  
  The `AgentTeamManager` determines which agents are needed for a given request and delegates the work accordingly, exemplifying the Coordinator/Dispatcher pattern.

### Hierarchical Task Decomposition

- **Task Breakdown:**  
  The system breaks down complex goals (e.g., analyzing climate risks for a location) into simpler sub-tasks. For example, the central agent delegates tasks like historical data analysis, risk assessment, and news monitoring to different specialized agents.

- **Multi-Level Structure:**  
  The system has a clear hierarchy: the central agent at the top, followed by specialized agents that handle specific tasks. This hierarchical structure allows for efficient task decomposition and delegation.

### Why This Pattern?

- **Scalability:**  
  The Coordinator/Dispatcher pattern allows for easy addition of new specialized agents without changing the central logic.

- **Modularity:**  
  Each agent is responsible for a specific task, making the system modular and easier to maintain.

- **Flexibility:**  
  The hierarchical structure enables complex task decomposition, allowing the system to handle a wide range of climate risk analysis tasks.

## Installation

1. **Clone the Repository:**
   ```sh
   git clone <repository-url>
   cd <repository-directory>
   ```

2. **Install Dependencies:**
   ```sh
   pip install -r requirements.txt
   ```

## Running the System

### Clearing Cache

Before running the system, it's recommended to clear the cache to ensure a clean state:

1. **Clear Python Cache:**
   ```sh
   find . -type d -name "__pycache__" -exec rm -r {} +
   find . -type f -name "*.pyc" -delete
   ```

2. **Clear Session Data:**
   ```sh
   rm -rf sessions/*
   ```

3. **Clear Browser Cache (if testing the web interface):**
   - **Chrome:** `Ctrl+Shift+Delete` (Windows/Linux) or `Cmd+Shift+Delete` (Mac)
   - **Firefox:** `Ctrl+Shift+Delete` (Windows/Linux) or `Cmd+Shift+Delete` (Mac)
   - **Safari:** `Cmd+Option+E`

4. **Restart the Server:**
   ```sh
   python app.py
   ```

### Running the FastAPI App

1. **Start the FastAPI Server:**
   ```sh
   python app.py
   ```

2. **Open Your Browser:**
   Go to `http://localhost:8000`.

3. **Enter an Address:**
   Use the form to enter an address (e.g., `2038 Forest Club Drive, Orlando, FL 32804`) and click "Analyze".

4. **View Results:**
   The result from the agent system will be displayed on the page.

### Running Tests

To run the tests, use:
```sh
python -m pytest tests/
```

## Project Structure

- `multi_tool_agent/`: Core multi-agent system implementation.
- `tests/`: Test files for the system.
- `app.py`: FastAPI web application.
- `templates/`: HTML templates for the web interface.
- `requirements.txt`: Project dependencies.

## License

[Your License Here]

## Observability and Error Recovery
The system provides comprehensive observability and error recovery mechanisms:

#### State Management
- Durable state management through checkpoints
- Automatic state persistence and restoration
- Context preservation across tool calls
- Tool call history tracking

#### Error Handling
- Graceful error handling with severity-based recovery
- Automatic rollback to last known good state
- Detailed error context for debugging
- Configurable recovery strategies

#### Recovery Strategies
- Severity-based recovery configurations:
  - LOW: 2 retries, 1.2x backoff, 15s timeout
  - MEDIUM: 3 retries, 1.5x backoff, 30s timeout
  - HIGH: 4 retries, 1.8x backoff, 45s timeout
  - CRITICAL: 5 retries, 2.0x backoff, 60s timeout
- Custom recovery strategies for specific error types
- Fallback action sequences
- Automatic checkpoint-based rollback

#### Monitoring and Analysis
- Agent interaction pattern tracking
- Decision pattern analysis
- Token usage monitoring
- Context compression metrics
- Error pattern detection
- Performance analytics

## Acknowledgments

- Google ADK Framework
- Contributors and maintainers
- Open source community 