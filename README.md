# Climate Risk Analysis Multi-Agent System

A sophisticated multi-agent system for comprehensive climate risk analysis, featuring specialized agents for different aspects of risk assessment and management.

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

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details. 