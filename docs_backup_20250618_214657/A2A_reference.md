# A2A Reference Documentation

## Overview
This document provides reference information about how the Agent Development Kit (ADK) defines agent cards and tools, and how the A2A (Agent-to-Agent) protocol uses these definitions for agent communication.

## Agent Cards: ADK Definition and A2A Usage

### ADK Agent Card Definition
The ADK defines agent cards using TypeScript interfaces that A2A agents must implement:

```typescript
// ADK-defined interface that A2A agents must implement
export interface AgentCard {
  name: string;                    // Human readable name
  description: string;             // Human readable description
  url: string;                     // Base URL for A2A service
  iconUrl?: string;                // Optional icon URL
  provider?: AgentProvider;        // Service provider info
  version: string;                 // Agent version
  documentationUrl?: string;       // Documentation URL
  capabilities: AgentCapabilities; // Supported features
  securitySchemes?: { [scheme: string]: SecurityScheme };
  security?: { [scheme: string]: string[] }[];
  defaultInputModes: string[];     // Supported input types
  defaultOutputModes: string[];    // Supported output types
  skills: AgentSkill[];           // Agent capabilities
  supportsAuthenticatedExtendedCard?: boolean;
}
```

### A2A Agent Card Usage
A2A agents use these ADK-defined cards to:
1. Discover agent capabilities
2. Establish communication protocols
3. Validate security requirements
4. Determine supported features

## Tools: ADK Implementation and A2A Integration

### ADK Tool Implementation
In the ADK, tools are implemented as regular Python functions that the framework automatically wraps:

```python
# ADK Tool Implementation
def get_weather(location: str, units: str = "metric") -> Dict[str, Any]:
    """Get current weather for a location.
    
    Args:
        location: City name or coordinates
        units: Measurement units (metric/imperial)
        
    Returns:
        Weather data dictionary
    """
    # Tool implementation
    pass

# ADK automatically wraps this function as a tool when added to agent
agent = LlmAgent(
    name="weather_agent",
    tools=[get_weather]  # Function is automatically wrapped as a tool
)
```

### A2A Tool Integration
A2A agents use these ADK-wrapped tools through a standardized interface:

```python
# A2A Tool Usage
class A2AAgent:
    def __init__(self, adk_agent):
        self.adk_agent = adk_agent
        self.tools = self._wrap_adk_tools(adk_agent.tools)
    
    def _wrap_adk_tools(self, adk_tools):
        """Wrap ADK tools for A2A protocol."""
        return {
            tool.__name__: {
                "name": tool.__name__,
                "description": tool.__doc__,
                "parameters": self._extract_parameters(tool)
            }
            for tool in adk_tools
        }
    
    async def handle_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle A2A tool requests using ADK tools."""
        tool_name = request.get("tool")
        if tool_name not in self.tools:
            raise ValueError(f"Unknown tool: {tool_name}")
            
        # Execute ADK tool
        return await self.adk_agent.execute_tool(tool_name, request)
```

## Implementation Guidelines

### Agent Cards

1. **ADK Definition**
   - Define agent cards using ADK interfaces
   - Implement required fields
   - Specify capabilities
   - Configure security

2. **A2A Usage**
   - Use ADK-defined cards for discovery
   - Validate against ADK schema
   - Implement required protocols
   - Handle security requirements

### Tools

1. **ADK Implementation**
   - Implement tools as Python functions
   - Add proper type hints
   - Include docstrings
   - Handle errors appropriately

2. **A2A Integration**
   - Wrap ADK tools for A2A protocol
   - Handle tool requests
   - Manage tool context
   - Implement error handling

## Best Practices

### Agent Cards

1. **ADK Definition**
   - Follow ADK interface exactly
   - Document all fields
   - Specify capabilities clearly
   - Configure security properly

2. **A2A Usage**
   - Validate cards against schema
   - Handle all required fields
   - Implement security
   - Support extensions

### Tools

1. **ADK Implementation**
   - Write clear function signatures
   - Document parameters
   - Handle errors
   - Support async

2. **A2A Integration**
   - Wrap tools properly
   - Handle requests
   - Manage context
   - Log activity

## References

1. [ADK Types](https://github.com/google-a2a/A2A/blob/main/types/src/types.ts)
2. [A2A Sample Implementation](https://github.com/google-a2a/a2a-samples/blob/main/samples/python/agents/airbnb_planner_multiagent/weather_agent/weather_executor.py)
3. [Agent Card Documentation](docs/agentcard.md) 