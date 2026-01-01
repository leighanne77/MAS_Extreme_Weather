# Agent Card Documentation

## Overview
Agent Cards are JSON metadata documents that describe an agent's identity, capabilities, skills, service endpoints, and authentication requirements. This document provides examples and guidelines for creating agent cards for our climate risk analysis system.

Special Note:  Since ToolContext is automatically injected by the ADK framework after the LLM decides to call the tool function, it is not relevant for the LLM's decision-making and including it can confuse the LLM.

Must Include for Tools: Referencing Tool in Agent’s Instructions¶
Within an agent's instructions, you can directly reference a tool by using its function name. If the tool's function name and docstring are sufficiently descriptive, your instructions can primarily focus on when the Large Language Model (LLM) should utilize the tool. This promotes clarity and helps the model understand the intended use of each tool.

It is crucial to clearly instruct the agent on how to handle different return values that a tool might produce. For example, if a tool returns an error message, your instructions should specify whether the agent should retry the operation, give up on the task, or request additional information from the user.

Furthermore, ADK supports the sequential use of tools, where the output of one tool can serve as the input for another. When implementing such workflows, it's important to describe the intended sequence of tool usage within the agent's instructions to guide the model through the necessary steps.

## Basic Example
```json
{
  "name": "weather_time_agent",
  "description": "Agent to answer questions about the time and weather in a city.",
  "url": "https://api.example.com/agents/weather_time",
  "version": "1.0.0",
  "provider": {
    "organization": "Climate Analysis Team",
    "url": "https://climate-analysis.example.com"
  },
  "capabilities": {
    "streaming": true,
    "pushNotifications": false,
    "stateTransitionHistory": true
  },
  "securitySchemes": {
    "bearer": {
      "type": "bearer",
      "description": "Bearer token authentication"
    }
  },
  "defaultInputModes": ["application/json", "text/plain"],
  "defaultOutputModes": ["application/json", "text/plain"],
  "skills": [
    {
      "name": "get_weather",
      "description": "Retrieves current weather data for a city",
      "parameters": {
        "city": "string",
        "country": "string"
      }
    },
    {
      "name": "get_current_time",
      "description": "Retrieves current time for a city",
      "parameters": {
        "city": "string",
        "timezone": "string"
      }
    }
  ]
}
```

## Climate Risk Analysis Agent Example
```json
{
  "name": "climate_risk_analyzer",
  "description": "Specialized agent for comprehensive climate risk analysis and assessment",
  "url": "https://api.climate-risk.example.com/agents/risk_analyzer",
  "version": "1.0.0",
  "provider": {
    "organization": "Climate Risk Analysis Team",
    "url": "https://climate-risk.example.com"
  },
  "capabilities": {
    "streaming": true,
    "pushNotifications": true,
    "stateTransitionHistory": true,
    "extensions": [
      {
        "uri": "https://climate-risk.example.com/extensions/weather",
        "description": "Weather data processing capabilities",
        "required": true,
        "params": {
          "max_stream_size": "10MB",
          "supported_formats": ["json", "csv"]
        }
      }
    ]
  },
  "securitySchemes": {
    "bearer": {
      "type": "bearer",
      "description": "Bearer token authentication",
      "requirements": {
        "token_format": "JWT",
        "expiration": "1h"
      }
    }
  },
  "defaultInputModes": ["application/json", "text/plain"],
  "defaultOutputModes": ["application/json", "text/plain"],
  "skills": [
    {
      "name": "analyze_current_risks",
      "description": "Analyzes current climate risks for a location",
      "parameters": {
        "location": {
          "type": "string",
          "description": "Geographic location identifier",
          "required": true
        },
        "timeframe": {
          "type": "string",
          "description": "Time period for analysis",
          "required": true
        },
        "risk_types": {
          "type": "array",
          "items": {
            "type": "string",
            "enum": ["flooding", "heat_wave", "storm", "drought"]
          },
          "description": "Types of risks to analyze"
        }
      }
    },
    {
      "name": "get_risk_thresholds",
      "description": "Retrieves risk thresholds for a location",
      "parameters": {
        "location": {
          "type": "string",
          "description": "Geographic location identifier",
          "required": true
        },
        "risk_type": {
          "type": "string",
          "description": "Type of risk threshold to retrieve",
          "required": true
        }
      }
    }
  ]
}
```

## Weather Data Processing Agent Example
```json
{
  "name": "weather_data_processor",
  "description": "Processes and analyzes weather data from multiple sources",
  "url": "https://api.climate-risk.example.com/agents/weather_processor",
  "version": "1.0.0",
  "provider": {
    "organization": "Climate Risk Analysis Team",
    "url": "https://climate-risk.example.com"
  },
  "capabilities": {
    "streaming": true,
    "pushNotifications": true,
    "stateTransitionHistory": true,
    "extensions": [
      {
        "uri": "https://climate-risk.example.com/extensions/data_processing",
        "description": "Advanced data processing capabilities",
        "required": true,
        "params": {
          "max_batch_size": "100MB",
          "supported_formats": ["json", "csv", "netcdf"]
        }
      }
    ]
  },
  "securitySchemes": {
    "bearer": {
      "type": "bearer",
      "description": "Bearer token authentication",
      "requirements": {
        "token_format": "JWT",
        "expiration": "1h"
      }
    }
  },
  "defaultInputModes": ["application/json", "text/plain", "application/netcdf"],
  "defaultOutputModes": ["application/json", "text/plain", "application/netcdf"],
  "skills": [
    {
      "name": "process_weather_data",
      "description": "Processes raw weather data into analysis-ready format",
      "parameters": {
        "data_source": {
          "type": "string",
          "description": "Source of weather data",
          "required": true
        },
        "data_format": {
          "type": "string",
          "description": "Format of input data",
          "required": true
        },
        "processing_options": {
          "type": "object",
          "description": "Processing configuration options",
          "properties": {
            "quality_checks": {
              "type": "boolean",
              "description": "Perform quality checks"
            },
            "normalization": {
              "type": "boolean",
              "description": "Normalize data values"
            }
          }
        }
      }
    },
    {
      "name": "validate_weather_data",
      "description": "Validates weather data for quality and consistency",
      "parameters": {
        "data": {
          "type": "object",
          "description": "Weather data to validate",
          "required": true
        },
        "validation_rules": {
          "type": "array",
          "description": "Rules to apply during validation",
          "items": {
            "type": "string"
          }
        }
      }
    }
  ]
}
```

## Implementation Guidelines

1. **Required Fields**
   - name: Human-readable name of the agent
   - description: Clear description of agent capabilities
   - url: Base URL for the agent's A2A service
   - version: Agent version string
   - capabilities: Supported A2A protocol features
   - defaultInputModes: Supported input media types
   - defaultOutputModes: Supported output media types
   - skills: Array of agent capabilities

2. **Security**
   - Always include securitySchemes for production
   - Use bearer token authentication
   - Specify token requirements
   - Include expiration policies

3. **Capabilities**
   - Enable streaming for real-time data
   - Configure push notifications
   - Enable state transition history
   - Define required extensions

4. **Skills**
   - Clear skill names and descriptions
   - Detailed parameter specifications
   - Required vs optional parameters
   - Parameter types and constraints

5. **Media Types**
   - Support JSON for structured data
   - Support plain text for natural language
   - Add support for domain-specific formats
   - Specify format requirements

## Best Practices

1. **Documentation**
   - Clear skill descriptions
   - Detailed parameter documentation
   - Example usage
   - Error handling

2. **Security**
   - Always use HTTPS
   - Implement proper authentication
   - Define access controls
   - Specify token requirements

3. **Capabilities**
   - Enable only needed features
   - Document extension requirements
   - Specify format support
   - Define size limits

4. **Skills**
   - Keep skills focused
   - Document dependencies
   - Specify error conditions
   - Include examples 