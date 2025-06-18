"""
Multi-Agent System for Climate Risk Analysis

This module implements a coordinated multi-agent system for comprehensive climate risk analysis.
It defines specialized agents, their capabilities, and the orchestration of their interactions.

Key Components:
    - AgentCapability: Defines specific capabilities of agents
    - AgentTeam: Represents a team of specialized agents
    - AgentTeamManager: Manages the team and coordinates agent interactions

Agent Types:
    1. Root Orchestrator: Coordinates and delegates tasks to specialized agents
    2. Risk Analyzer: Analyzes current climate risks and conditions
    3. Historical Analyzer: Analyzes historical climate patterns
    4. News Monitor: Monitors real-time climate-related news
    5. Greeting Agent: Handles user interactions and session initialization
    6. Farewell Agent: Manages session conclusion and result compilation
    7. Validation Agent: Ensures data quality and consistency
    8. Recommendation Agent: Generates actionable recommendations

State Management:
    - Each agent maintains its own state
    - Shared state is managed through the session manager
    - State updates are coordinated through the team manager

Error Handling:
    - Agents implement retry mechanisms
    - Errors are logged and propagated appropriately
    - Failed operations can be retried based on configuration

Dependencies:
    - session_manager: For session and state management
    - weather_risks: For climate risk analysis
    - risk_definitions: For risk thresholds and definitions
    - agent: For base agent definition

Example Usage:
    ```python
    # Create and initialize the agent team
    team_manager = AgentTeamManager()
    
    # Create a new analysis session
    session = await team_manager.create_session(location="New York")
    
    # Run a comprehensive analysis
    result = await team_manager.run_analysis(session)
    ```

Configuration:
    - DEFAULT_MODEL: Default model for agent operations
    - LITE_MODEL: Lightweight model for simple tasks
    - MAX_CONCURRENT_AGENTS: Maximum number of concurrent agents
    - MAX_RETRY_ATTEMPTS: Maximum number of retry attempts
    - RETRY_DELAY: Delay between retry attempts
"""

import os
import asyncio
import logging
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass
from dotenv import load_dotenv
from datetime import datetime

from src.multi_agent_system.session_manager import SessionManager, AnalysisSession
from src.multi_agent_system.weather_risks import ClimateRiskAnalyzer
from src.multi_agent_system.risk_definitions import severity_levels, RiskSource, RiskThreshold
from src.multi_agent_system.agent import Agent
from src.multi_agent_system.utils.adk_features import MetricsCollector, CircuitBreaker, WorkerPool, Monitoring, Buffer
from .agents.tools import (
    validate_and_geocode,
    analyze_climate_risk,
    get_weather_data,
    get_nbs_solutions,
    calculate_cost_benefit,
    generate_recommendations
)

# Load environment variables
load_dotenv()

# Constants
DEFAULT_MODEL = os.getenv("DEFAULT_MODEL", "gemini-2.0-flash")
LITE_MODEL = os.getenv("LITE_MODEL", "gemini-2.0-flash")
MAX_CONCURRENT_AGENTS = int(os.getenv("MAX_CONCURRENT_AGENTS", "5"))
MAX_RETRY_ATTEMPTS = int(os.getenv("MAX_RETRY_ATTEMPTS", "3"))
RETRY_DELAY = int(os.getenv("RETRY_DELAY", "1"))

# --- Agent Definitions ---

# Root Orchestrator Agent
root_agent = Agent(
    name="root_orchestrator",
    description="""
    Delegates and coordinates climate risk analysis tasks. Matches user requests to specialized agents based on their capabilities. Combines and validates results from multiple agents.
    """,
    instructions="""
    You are the root orchestrator for climate risk analysis. Your ONLY responsibilities are:
    1. Analyze user requests to identify required capabilities
    2. Select appropriate specialized agents based on their descriptions
    3. Coordinate parallel execution of independent analyses
    4. Validate and combine results from multiple agents
    5. Handle errors and retry failed operations
    6. Maintain session context and state
    
    You MUST NOT:
    - Perform any analysis yourself
    - Make decisions about risk assessment
    - Generate recommendations
    - Validate data directly
    - Handle user interactions
    
    DELEGATION RULES:
    1. For Risk Analysis:
       - Delegate to risk_analyzer when:
         * User requests current risk assessment
         * Location-specific risk evaluation needed
         * Risk threshold monitoring required
         * Pattern identification requested
       - Always validate results with validation_agent
    
    2. For Historical Analysis:
       - Delegate to historical_analyzer when:
         * Long-term trend analysis requested
         * Historical pattern analysis needed
         * Climate change impact assessment required
         * Seasonal variation analysis requested
       - Combine with risk_analyzer for comprehensive assessment
    
    3. For News Monitoring:
       - Delegate to news_monitor when:
         * Real-time updates requested
         * Weather alerts needed
         * Emergency notifications required
         * Local climate events monitoring
       - Prioritize critical alerts
    
    4. For User Interactions:
       - Delegate to greeting_agent when:
         * New session initialization
         * User introduction needed
         * Capability explanation required
         * Initial context gathering
       
       - Delegate to farewell_agent when:
         * Session conclusion needed
         * Results compilation required
         * User feedback collection
         * Follow-up recommendations
    
    5. For Data Quality:
       - Delegate to validation_agent when:
         * Input data validation needed
         * Result verification required
         * Cross-source validation
         * Data consistency checks
       - Apply validation before combining results
    
    6. For Recommendations:
       - Delegate to recommendation_agent when:
         * Actionable recommendations needed
         * Resource identification required
         * Action prioritization requested
         * Mitigation strategies needed
       - Only after risk_analyzer and historical_analyzer complete
    
    EXECUTION ORDER:
    1. Always start with greeting_agent for new sessions
    2. Run risk_analyzer and historical_analyzer in parallel
    3. Run news_monitor concurrently with analysis
    4. Validate results using validation_agent
    5. Generate recommendations if requested
    6. Conclude with farewell_agent
    
    ERROR HANDLING:
    1. Retry failed operations up to MAX_RETRY_ATTEMPTS
    2. Log errors with specific agent and operation
    3. Maintain partial results for successful operations
    4. Notify user of partial results if full analysis fails
    
    RESULT COMBINATION:
    1. Combine results in order of priority:
       - Critical alerts first
       - Risk assessments second
       - Historical context third
       - Recommendations last
    2. Ensure all required validations are complete
    3. Check for data consistency across sources
    4. Format final response for user consumption
    """,
    model=DEFAULT_MODEL,
    agent_card={
        "name": "root_orchestrator",
        "description": "Delegates and coordinates climate risk analysis tasks. Matches user requests to specialized agents based on their capabilities. Combines and validates results from multiple agents.",
        "url": "https://api.climate-risk.example.com/agents/root_orchestrator",
        "version": "1.0.0",
        "provider": {
            "organization": "Climate Risk Analysis Team",
            "url": "https://climate-risk.example.com",
            "contact": {
                "email": "support@climate-risk.example.com",
                "phone": "+1-555-0123"
            },
            "documentation": "https://docs.climate-risk.example.com/agents/root_orchestrator"
        },
        "capabilities": {
            "streaming": True,
            "pushNotifications": True,
            "stateTransitionHistory": True,
            "extensions": [
                {
                    "uri": "https://climate-risk.example.com/extensions/orchestration",
                    "description": "Task orchestration and coordination capabilities",
                    "required": True,
                    "params": {
                        "max_concurrent_tasks": 5,
                        "task_timeout": "5m",
                        "retry_attempts": 3,
                        "retry_delay": "30s"
                    }
                },
                {
                    "uri": "https://climate-risk.example.com/extensions/error_handling",
                    "description": "Advanced error handling and recovery",
                    "required": True,
                    "params": {
                        "error_categories": ["timeout", "validation", "communication"],
                        "recovery_strategies": ["retry", "fallback", "degraded"]
                    }
                }
            ],
            "rateLimits": {
                "requests_per_minute": 60,
                "concurrent_sessions": 100
            }
        },
        "securitySchemes": {
            "bearer": {
                "type": "bearer",
                "description": "Bearer token authentication",
                "requirements": {
                    "token_format": "JWT",
                    "expiration": "1h",
                    "scopes": ["read", "write", "admin"]
                }
            },
            "apiKey": {
                "type": "apiKey",
                "description": "API key authentication",
                "requirements": {
                    "key_format": "uuid",
                    "rotation_period": "30d"
                }
            }
        },
        "defaultInputModes": ["application/json", "text/plain"],
        "defaultOutputModes": ["application/json", "text/plain"],
        "skills": [
            {
                "name": "delegate_tasks",
                "description": "Delegates tasks to specialized agents",
                "parameters": {
                    "request": {
                        "type": "object",
                        "description": "User request to process",
                        "required": True,
                        "properties": {
                            "type": {
                                "type": "string",
                                "enum": ["analysis", "monitoring", "validation", "recommendation"],
                                "description": "Type of request"
                            },
                            "priority": {
                                "type": "string",
                                "enum": ["low", "medium", "high", "critical"],
                                "description": "Request priority"
                            },
                            "deadline": {
                                "type": "string",
                                "format": "date-time",
                                "description": "Request deadline"
                            }
                        }
                    },
                    "context": {
                        "type": "object",
                        "description": "Current session context",
                        "required": True,
                        "properties": {
                            "session_id": {
                                "type": "string",
                                "description": "Session identifier"
                            },
                            "user_id": {
                                "type": "string",
                                "description": "User identifier"
                            },
                            "preferences": {
                                "type": "object",
                                "description": "User preferences"
                            }
                        }
                    }
                }
            },
            {
                "name": "coordinate_analysis",
                "description": "Coordinates parallel analysis tasks",
                "parameters": {
                    "tasks": {
                        "type": "array",
                        "description": "Tasks to coordinate",
                        "required": True,
                        "items": {
                            "type": "object",
                            "properties": {
                                "agent": {
                                    "type": "string",
                                    "description": "Agent to execute task"
                                },
                                "action": {
                                    "type": "string",
                                    "description": "Action to perform"
                                },
                                "parameters": {
                                    "type": "object",
                                    "description": "Task parameters"
                                },
                                "dependencies": {
                                    "type": "array",
                                    "items": {
                                        "type": "string"
                                    },
                                    "description": "Task dependencies"
                                }
                            }
                        }
                    },
                    "session_id": {
                        "type": "string",
                        "description": "Session identifier",
                        "required": True
                    },
                    "strategy": {
                        "type": "string",
                        "enum": ["parallel", "sequential", "hybrid"],
                        "description": "Execution strategy"
                    },
                    "timeout": {
                        "type": "string",
                        "description": "Overall timeout for all tasks"
                    }
                }
            },
            {
                "name": "combine_results",
                "description": "Combines and validates results from multiple agents",
                "parameters": {
                    "results": {
                        "type": "array",
                        "description": "Results to combine",
                        "required": True,
                        "items": {
                            "type": "object",
                            "properties": {
                                "agent": {
                                    "type": "string",
                                    "description": "Source agent"
                                },
                                "data": {
                                    "type": "object",
                                    "description": "Result data"
                                },
                                "confidence": {
                                    "type": "number",
                                    "description": "Result confidence"
                                }
                            }
                        }
                    },
                    "validation_rules": {
                        "type": "object",
                        "description": "Validation rules to apply"
                    },
                    "format": {
                        "type": "string",
                        "enum": ["detailed", "summary", "raw"],
                        "description": "Output format"
                    }
                }
            }
        ],
        "metrics": {
            "performance": {
                "response_time": "p95 < 2s",
                "throughput": "100 req/min",
                "error_rate": "< 0.1%"
            },
            "reliability": {
                "uptime": "99.9%",
                "recovery_time": "< 5m",
                "data_consistency": "100%"
            }
        }
    }
)

# Risk Analysis Agent
risk_analyzer = Agent(
    name="risk_analyzer",
    description="""
    Analyzes current climate risks and conditions. Evaluates risk severity, monitors thresholds, and identifies emerging patterns. Provides real-time risk assessments for specific locations.
    """,
    instructions="""
    You are a climate risk analysis specialist. Your ONLY responsibilities are:
    1. Analyze current climate conditions for specified locations
    2. Compare conditions against established risk thresholds
    3. Classify risks by type and severity
    4. Identify emerging risk patterns
    5. Validate risk assessments against multiple sources
    
    You MUST NOT:
    - Make recommendations
    - Handle user interactions
    - Process historical data
    - Monitor news sources
    - Validate data quality
    """,
    model=DEFAULT_MODEL,
    agent_card={
        "name": "risk_analyzer",
        "description": "Specialized agent for comprehensive climate risk analysis and assessment",
        "url": "https://api.climate-risk.example.com/agents/risk_analyzer",
        "version": "1.0.0",
        "provider": {
            "organization": "Climate Risk Analysis Team",
            "url": "https://climate-risk.example.com",
            "contact": {
                "email": "support@climate-risk.example.com",
                "phone": "+1-555-0123"
            },
            "documentation": "https://docs.climate-risk.example.com/agents/risk_analyzer"
        },
        "capabilities": {
            "streaming": True,
            "pushNotifications": True,
            "stateTransitionHistory": True,
            "extensions": [
                {
                    "uri": "https://climate-risk.example.com/extensions/risk_analysis",
                    "description": "Climate risk analysis capabilities",
                    "required": True,
                    "params": {
                        "max_stream_size": "10MB",
                        "supported_formats": ["json", "csv"],
                        "analysis_depth": ["basic", "detailed", "comprehensive"],
                        "update_frequency": "5m"
                    }
                },
                {
                    "uri": "https://climate-risk.example.com/extensions/pattern_detection",
                    "description": "Pattern detection and analysis",
                    "required": True,
                    "params": {
                        "pattern_types": ["trend", "cycle", "anomaly"],
                        "confidence_threshold": 0.8
                    }
                }
            ],
            "rateLimits": {
                "requests_per_minute": 30,
                "concurrent_analyses": 10
            }
        },
        "securitySchemes": {
            "bearer": {
                "type": "bearer",
                "description": "Bearer token authentication",
                "requirements": {
                    "token_format": "JWT",
                    "expiration": "1h",
                    "scopes": ["read", "analysis"]
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
                        "required": True,
                        "format": "geojson"
                    },
                    "timeframe": {
                        "type": "string",
                        "description": "Time period for analysis",
                        "required": True,
                        "enum": ["immediate", "24h", "7d", "30d"]
                    },
                    "risk_types": {
                        "type": "array",
                        "items": {
                            "type": "string",
                            "enum": ["flooding", "heat_wave", "storm", "drought", "wildfire", "coastal"]
                        },
                        "description": "Types of risks to analyze"
                    },
                    "analysis_depth": {
                        "type": "string",
                        "enum": ["basic", "detailed", "comprehensive"],
                        "description": "Depth of analysis"
                    },
                    "include_historical": {
                        "type": "boolean",
                        "description": "Include historical context"
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
                        "required": True,
                        "format": "geojson"
                    },
                    "risk_type": {
                        "type": "string",
                        "description": "Type of risk threshold to retrieve",
                        "required": True,
                        "enum": ["flooding", "heat_wave", "storm", "drought", "wildfire", "coastal"]
                    },
                    "time_period": {
                        "type": "string",
                        "description": "Time period for thresholds",
                        "enum": ["daily", "weekly", "monthly", "seasonal"]
                    },
                    "include_metadata": {
                        "type": "boolean",
                        "description": "Include threshold metadata"
                    }
                }
            },
            {
                "name": "detect_patterns",
                "description": "Detects emerging risk patterns",
                "parameters": {
                    "location": {
                        "type": "string",
                        "description": "Geographic location identifier",
                        "required": True,
                        "format": "geojson"
                    },
                    "pattern_type": {
                        "type": "string",
                        "enum": ["trend", "cycle", "anomaly"],
                        "description": "Type of pattern to detect"
                    },
                    "time_range": {
                        "type": "string",
                        "description": "Time range for pattern detection",
                        "required": True
                    },
                    "confidence_threshold": {
                        "type": "number",
                        "description": "Minimum confidence for pattern detection",
                        "minimum": 0,
                        "maximum": 1
                    }
                }
            }
        ],
        "metrics": {
            "performance": {
                "analysis_time": "p95 < 30s",
                "pattern_detection": "p95 < 1m",
                "accuracy": "> 95%"
            },
            "reliability": {
                "data_freshness": "< 5m",
                "threshold_accuracy": "> 99%",
                "pattern_confidence": "> 90%"
            }
        }
    }
)

# Historical Analysis Agent
historical_analyzer = Agent(
    name="historical_analyzer",
    description="""
    Analyzes historical climate patterns and trends. Identifies long-term changes, seasonal variations, and climate change impacts. Provides context for current conditions.
    """,
    instructions="""
    You are a historical climate analysis specialist. Your ONLY responsibilities are:
    1. Analyze historical climate data
    2. Identify long-term trends
    3. Compare current conditions to historical patterns
    4. Assess climate change impacts
    5. Provide historical context
    
    You MUST NOT:
    - Make predictions
    - Handle real-time data
    - Process current conditions
    - Monitor news sources
    - Validate data quality
    """,
    model=DEFAULT_MODEL,
    agent_card={
        "name": "historical_analyzer",
        "description": "Specialized agent for historical climate pattern analysis and trend identification",
        "url": "https://api.climate-risk.example.com/agents/historical_analyzer",
        "version": "1.0.0",
        "provider": {
            "organization": "Climate Risk Analysis Team",
            "url": "https://climate-risk.example.com"
        },
        "capabilities": {
            "streaming": True,
            "pushNotifications": True,
            "stateTransitionHistory": True,
            "extensions": [
                {
                    "uri": "https://climate-risk.example.com/extensions/historical_analysis",
                    "description": "Historical data analysis capabilities",
                    "required": True,
                    "params": {
                        "max_data_size": "1GB",
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
        "defaultInputModes": ["application/json", "text/plain"],
        "defaultOutputModes": ["application/json", "text/plain"],
        "skills": [
            {
                "name": "analyze_trends",
                "description": "Analyzes historical climate trends",
                "parameters": {
                    "location": {
                        "type": "string",
                        "description": "Geographic location identifier",
                        "required": True
                    },
                    "time_period": {
                        "type": "string",
                        "description": "Historical time period to analyze",
                        "required": True
                    },
                    "metrics": {
                        "type": "array",
                        "items": {
                            "type": "string",
                            "enum": ["temperature", "precipitation", "humidity", "wind"]
                        },
                        "description": "Climate metrics to analyze"
                    }
                }
            },
            {
                "name": "compare_patterns",
                "description": "Compares current conditions to historical patterns",
                "parameters": {
                    "location": {
                        "type": "string",
                        "description": "Geographic location identifier",
                        "required": True
                    },
                    "current_data": {
                        "type": "object",
                        "description": "Current climate data to compare",
                        "required": True
                    },
                    "historical_period": {
                        "type": "string",
                        "description": "Historical period for comparison",
                        "required": True
                    }
                }
            }
        ]
    }
)

# News Monitoring Agent
news_monitor = Agent(
    name="news_monitor",
    description="""
    Monitors news sources for climate-related events and developments. Tracks media coverage, identifies relevant news, and extracts key information about climate risks and impacts.
    """,
    instructions="""
    You are a climate news monitoring specialist. Your ONLY responsibilities are:
    1. Monitor real-time climate news
    2. Track weather alerts
    3. Process emergency notifications
    4. Identify significant events
    5. Provide timely updates
    
    You MUST NOT:
    - Analyze risks
    - Process historical data
    - Make recommendations
    - Validate data quality
    - Handle user interactions
    """,
    model=DEFAULT_MODEL,
    agent_card={
        "name": "news_monitor",
        "description": "Climate news monitoring and analysis agent",
        "url": "https://api.climate-risk.example.com/agents/news_monitor",
        "version": "1.0.0",
        "provider": {
            "organization": "Climate Risk Analysis Team",
            "url": "https://climate-risk.example.com",
            "contact": {
                "email": "support@climate-risk.example.com",
                "phone": "+1-555-0123"
            },
            "documentation": "https://docs.climate-risk.example.com/agents/news_monitor"
        },
        "capabilities": {
            "streaming": True,
            "pushNotifications": True,
            "stateTransitionHistory": True,
            "extensions": [
                {
                    "uri": "https://climate-risk.example.com/extensions/news_monitoring",
                    "description": "News monitoring capabilities",
                    "required": True,
                    "params": {
                        "update_frequency": "5m",
                        "sources": ["news_apis", "rss_feeds", "social_media"],
                        "languages": ["en", "es", "fr", "de"],
                        "max_articles": 1000
                    }
                },
                {
                    "uri": "https://climate-risk.example.com/extensions/sentiment_analysis",
                    "description": "News sentiment analysis",
                    "required": True,
                    "params": {
                        "sentiment_levels": ["positive", "neutral", "negative"],
                        "confidence_threshold": 0.7,
                        "update_frequency": "15m"
                    }
                }
            ],
            "rateLimits": {
                "requests_per_minute": 60,
                "concurrent_monitors": 30
            }
        },
        "securitySchemes": {
            "bearer": {
                "type": "bearer",
                "description": "Bearer token authentication",
                "requirements": {
                    "token_format": "JWT",
                    "expiration": "1h",
                    "scopes": ["read", "monitor"]
                }
            }
        },
        "defaultInputModes": ["application/json", "text/plain"],
        "defaultOutputModes": ["application/json", "text/plain"],
        "skills": [
            {
                "name": "monitor_news",
                "description": "Monitors news sources for climate-related content",
                "parameters": {
                    "sources": {
                        "type": "array",
                        "items": {
                            "type": "string",
                            "enum": ["news_apis", "rss_feeds", "social_media"]
                        },
                        "description": "News sources to monitor"
                    },
                    "keywords": {
                        "type": "array",
                        "items": {
                            "type": "string"
                        },
                        "description": "Keywords to track"
                    },
                    "timeframe": {
                        "type": "string",
                        "enum": ["realtime", "1h", "24h", "7d"],
                        "description": "Timeframe for news monitoring"
                    },
                    "languages": {
                        "type": "array",
                        "items": {
                            "type": "string",
                            "enum": ["en", "es", "fr", "de"]
                        },
                        "description": "Languages to monitor"
                    }
                }
            },
            {
                "name": "analyze_sentiment",
                "description": "Analyzes sentiment in news articles",
                "parameters": {
                    "articles": {
                        "type": "array",
                        "description": "Articles to analyze",
                        "required": True,
                        "items": {
                            "type": "object",
                            "properties": {
                                "title": {
                                    "type": "string"
                                },
                                "content": {
                                    "type": "string"
                                },
                                "source": {
                                    "type": "string"
                                },
                                "timestamp": {
                                    "type": "string",
                                    "format": "date-time"
                                }
                            }
                        }
                    },
                    "sentiment_levels": {
                        "type": "array",
                        "items": {
                            "type": "string",
                            "enum": ["positive", "neutral", "negative"]
                        },
                        "description": "Sentiment levels to detect"
                    },
                    "min_confidence": {
                        "type": "number",
                        "description": "Minimum confidence for sentiment analysis",
                        "minimum": 0,
                        "maximum": 1
                    }
                }
            },
            {
                "name": "extract_entities",
                "description": "Extracts relevant entities from news articles",
                "parameters": {
                    "articles": {
                        "type": "array",
                        "description": "Articles to process",
                        "required": True,
                        "items": {
                            "type": "object",
                            "properties": {
                                "content": {
                                    "type": "string"
                                },
                                "metadata": {
                                    "type": "object"
                                }
                            }
                        }
                    },
                    "entity_types": {
                        "type": "array",
                        "items": {
                            "type": "string",
                            "enum": ["location", "event", "organization", "person"]
                        },
                        "description": "Types of entities to extract"
                    },
                    "min_confidence": {
                        "type": "number",
                        "description": "Minimum confidence for entity extraction",
                        "minimum": 0,
                        "maximum": 1
                    }
                }
            }
        ],
        "metrics": {
            "performance": {
                "monitoring_latency": "< 5m",
                "sentiment_analysis": "p95 < 30s",
                "entity_extraction": "p95 < 1m"
            },
            "reliability": {
                "source_availability": "> 99%",
                "sentiment_accuracy": "> 85%",
                "entity_accuracy": "> 90%"
            }
        }
    }
)

# Greeting Agent
greeting_agent = Agent(
    name="greeting_agent",
    description="""
    Handles initial user interactions and session setup. Greets users, explains system capabilities, and gathers initial context. Manages session initialization.
    """,
    instructions="""
    You are a user interaction specialist. Your ONLY responsibilities are:
    1. Greet users and introduce the system
    2. Initialize new sessions
    3. Explain available capabilities
    4. Clarify user intentions
    5. Gather initial context
    
    You MUST NOT:
    - Perform any analysis
    - Make recommendations
    - Validate data
    - Handle session conclusions
    - Process user requests
    
    Focus ONLY on:
    - Professional communication
    - Clear capability explanation
    - User intent understanding
    - Context gathering
    - Session initialization
    """,
    model=LITE_MODEL
)

# Farewell Agent
farewell_agent = Agent(
    name="farewell_agent",
    description="""
    Manages session conclusion and result presentation. Summarizes activities, compiles results, and provides follow-up recommendations. Handles session cleanup.
    """,
    instructions="""
    You are a session conclusion specialist. Your ONLY responsibilities are:
    1. Summarize session activities
    2. Compile analysis results
    3. Collect user feedback
    4. Clean up session resources
    5. Provide follow-up recommendations
    
    You MUST NOT:
    - Perform any analysis
    - Validate data
    - Handle user interactions
    - Initialize sessions
    - Process new requests
    
    Focus ONLY on:
    - Comprehensive summaries
    - Clear result presentation
    - User feedback collection
    - Resource cleanup
    - Future recommendations
    """,
    model=LITE_MODEL
)

# Data Validation Agent
validation_agent = Agent(
    name="validation_agent",
    description="""
    Ensures data quality and consistency across the system. Validates inputs, verifies results, and maintains data integrity. Provides quality assurance for all analyses.
    """,
    instructions="""
    You are a data validation specialist. Your ONLY responsibilities are:
    1. Validate input data
    2. Verify analysis results
    3. Check data consistency
    4. Ensure quality standards
    5. Report validation issues
    
    You MUST NOT:
    - Perform analysis
    - Make recommendations
    - Handle user interactions
    - Process historical data
    - Monitor news sources
    """,
    model=DEFAULT_MODEL,
    agent_card={
        "name": "validation_agent",
        "description": "Specialized agent for data validation and quality assurance",
        "url": "https://api.climate-risk.example.com/agents/validation_agent",
        "version": "1.0.0",
        "provider": {
            "organization": "Climate Risk Analysis Team",
            "url": "https://climate-risk.example.com"
        },
        "capabilities": {
            "streaming": True,
            "pushNotifications": True,
            "stateTransitionHistory": True,
            "extensions": [
                {
                    "uri": "https://climate-risk.example.com/extensions/validation",
                    "description": "Data validation capabilities",
                    "required": True,
                    "params": {
                        "max_batch_size": "100MB",
                        "validation_timeout": "30s"
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
                "name": "validate_data",
                "description": "Validates input data against quality standards",
                "parameters": {
                    "data": {
                        "type": "object",
                        "description": "Data to validate",
                        "required": True
                    },
                    "rules": {
                        "type": "array",
                        "items": {
                            "type": "object"
                        },
                        "description": "Validation rules to apply"
                    },
                    "strict_mode": {
                        "type": "boolean",
                        "description": "Whether to use strict validation"
                    }
                }
            },
            {
                "name": "verify_results",
                "description": "Verifies analysis results for consistency",
                "parameters": {
                    "results": {
                        "type": "object",
                        "description": "Results to verify",
                        "required": True
                    },
                    "criteria": {
                        "type": "object",
                        "description": "Verification criteria",
                        "required": True
                    },
                    "tolerance": {
                        "type": "number",
                        "description": "Allowed deviation from expected values"
                    }
                }
            }
        ]
    }
)

# Recommendation Agent
recommendation_agent = Agent(
    name="recommendation_agent",
    description="""
    Generates actionable recommendations based on analysis results. Identifies resources, prioritizes actions, and suggests mitigation strategies. Provides clear, practical guidance.
    """,
    instructions="""
    You are a recommendation specialist. Your ONLY responsibilities are:
    1. Generate actionable recommendations
    2. Identify relevant resources
    3. Prioritize actions
    4. Suggest mitigation strategies
    5. Provide clear guidance
    
    You MUST NOT:
    - Perform analysis
    - Validate data
    - Handle user interactions
    - Process historical data
    - Monitor news sources
    """,
    model=DEFAULT_MODEL,
    agent_card={
        "name": "recommendation_agent",
        "description": "Specialized agent for generating actionable recommendations",
        "url": "https://api.climate-risk.example.com/agents/recommendation_agent",
        "version": "1.0.0",
        "provider": {
            "organization": "Climate Risk Analysis Team",
            "url": "https://climate-risk.example.com"
        },
        "capabilities": {
            "streaming": True,
            "pushNotifications": True,
            "stateTransitionHistory": True,
            "extensions": [
                {
                    "uri": "https://climate-risk.example.com/extensions/recommendations",
                    "description": "Recommendation generation capabilities",
                    "required": True,
                    "params": {
                        "max_recommendations": 10,
                        "priority_levels": 5
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
                "name": "generate_recommendations",
                "description": "Generates actionable recommendations",
                "parameters": {
                    "analysis": {
                        "type": "object",
                        "description": "Analysis results to base recommendations on",
                        "required": True
                    },
                    "context": {
                        "type": "object",
                        "description": "User context and constraints",
                        "required": True
                    },
                    "priority": {
                        "type": "string",
                        "enum": ["low", "medium", "high", "critical"],
                        "description": "Priority level for recommendations"
                    }
                }
            },
            {
                "name": "prioritize_actions",
                "description": "Prioritizes recommended actions",
                "parameters": {
                    "recommendations": {
                        "type": "array",
                        "description": "Recommendations to prioritize",
                        "required": True
                    },
                    "criteria": {
                        "type": "object",
                        "description": "Prioritization criteria",
                        "required": True
                    },
                    "constraints": {
                        "type": "object",
                        "description": "Resource and time constraints"
                    }
                }
            }
        ]
    }
)

# Weather Monitor Agent
weather_monitor = Agent(
    name="weather_monitor",
    description="""
    Monitors real-time weather conditions and forecasts. Tracks temperature, precipitation, wind, and other meteorological factors. Provides early warnings for severe weather events.
    """,
    instructions="""
    You are a weather monitoring specialist. Your ONLY responsibilities are:
    1. Monitor real-time weather conditions
    2. Track weather forecasts
    3. Provide early warnings for severe weather events
    4. Validate weather data
    5. Maintain weather monitoring system
    
    You MUST NOT:
    - Perform risk analysis
    - Process historical data
    - Make recommendations
    - Validate risk data
    - Handle user interactions
    """,
    model=DEFAULT_MODEL,
    agent_card={
        "name": "weather_monitor",
        "description": "Real-time weather monitoring and forecasting agent",
        "url": "https://api.climate-risk.example.com/agents/weather_monitor",
        "version": "1.0.0",
        "provider": {
            "organization": "Climate Risk Analysis Team",
            "url": "https://climate-risk.example.com",
            "contact": {
                "email": "support@climate-risk.example.com",
                "phone": "+1-555-0123"
            },
            "documentation": "https://docs.climate-risk.example.com/agents/weather_monitor"
        },
        "capabilities": {
            "streaming": True,
            "pushNotifications": True,
            "stateTransitionHistory": True,
            "extensions": [
                {
                    "uri": "https://climate-risk.example.com/extensions/weather_monitoring",
                    "description": "Weather monitoring capabilities",
                    "required": True,
                    "params": {
                        "update_frequency": "1m",
                        "data_sources": ["satellite", "radar", "stations", "models"],
                        "forecast_horizon": "7d",
                        "resolution": ["hourly", "daily"]
                    }
                },
                {
                    "uri": "https://climate-risk.example.com/extensions/alert_system",
                    "description": "Weather alert system",
                    "required": True,
                    "params": {
                        "alert_levels": ["info", "warning", "severe", "extreme"],
                        "notification_channels": ["email", "sms", "push", "webhook"],
                        "cooldown_period": "15m"
                    }
                }
            ],
            "rateLimits": {
                "requests_per_minute": 120,
                "concurrent_monitors": 50
            }
        },
        "securitySchemes": {
            "bearer": {
                "type": "bearer",
                "description": "Bearer token authentication",
                "requirements": {
                    "token_format": "JWT",
                    "expiration": "1h",
                    "scopes": ["read", "monitor", "alert"]
                }
            }
        },
        "defaultInputModes": ["application/json", "text/plain"],
        "defaultOutputModes": ["application/json", "text/plain"],
        "skills": [
            {
                "name": "get_current_conditions",
                "description": "Retrieves current weather conditions",
                "parameters": {
                    "location": {
                        "type": "string",
                        "description": "Geographic location identifier",
                        "required": True,
                        "format": "geojson"
                    },
                    "metrics": {
                        "type": "array",
                        "items": {
                            "type": "string",
                            "enum": ["temperature", "precipitation", "wind", "humidity", "pressure", "visibility"]
                        },
                        "description": "Weather metrics to retrieve"
                    },
                    "units": {
                        "type": "string",
                        "enum": ["metric", "imperial"],
                        "description": "Measurement units"
                    },
                    "include_forecast": {
                        "type": "boolean",
                        "description": "Include forecast data"
                    }
                }
            },
            {
                "name": "monitor_conditions",
                "description": "Monitors weather conditions for changes",
                "parameters": {
                    "location": {
                        "type": "string",
                        "description": "Geographic location identifier",
                        "required": True,
                        "format": "geojson"
                    },
                    "metrics": {
                        "type": "array",
                        "items": {
                            "type": "string",
                            "enum": ["temperature", "precipitation", "wind", "humidity", "pressure", "visibility"]
                        },
                        "description": "Weather metrics to monitor"
                    },
                    "thresholds": {
                        "type": "object",
                        "description": "Alert thresholds for each metric"
                    },
                    "callback_url": {
                        "type": "string",
                        "description": "URL to notify of changes",
                        "format": "uri"
                    }
                }
            },
            {
                "name": "get_forecast",
                "description": "Retrieves weather forecast",
                "parameters": {
                    "location": {
                        "type": "string",
                        "description": "Geographic location identifier",
                        "required": True,
                        "format": "geojson"
                    },
                    "timeframe": {
                        "type": "string",
                        "enum": ["24h", "48h", "72h", "7d", "14d"],
                        "description": "Forecast timeframe"
                    },
                    "resolution": {
                        "type": "string",
                        "enum": ["hourly", "daily"],
                        "description": "Forecast resolution"
                    },
                    "include_probability": {
                        "type": "boolean",
                        "description": "Include probability data"
                    }
                }
            }
        ],
        "metrics": {
            "performance": {
                "data_freshness": "< 1m",
                "forecast_accuracy": "> 90%",
                "alert_latency": "< 30s"
            },
            "reliability": {
                "uptime": "99.99%",
                "data_availability": "> 99.9%",
                "alert_delivery": "> 99.9%"
            }
        }
    }
)

# Risk Validator Agent
risk_validator = Agent(
    name="risk_validator",
    description="""
    Validates risk assessments and predictions. Cross-references multiple data sources, checks for consistency, and identifies potential errors or anomalies in risk analysis.
    """,
    instructions="""
    You are a risk validation specialist. Your ONLY responsibilities are:
    1. Validate risk assessments
    2. Verify risk predictions
    3. Detect anomalies in risk data
    4. Maintain risk validation system
    5. Report validation results
    
    You MUST NOT:
    - Perform risk analysis
    - Make recommendations
    - Handle user interactions
    - Process historical data
    - Monitor news sources
    """,
    model=DEFAULT_MODEL,
    agent_card={
        "name": "risk_validator",
        "description": "Validation and verification of climate risk assessments",
        "url": "https://api.climate-risk.example.com/agents/risk_validator",
        "version": "1.0.0",
        "provider": {
            "organization": "Climate Risk Analysis Team",
            "url": "https://climate-risk.example.com",
            "contact": {
                "email": "support@climate-risk.example.com",
                "phone": "+1-555-0123"
            },
            "documentation": "https://docs.climate-risk.example.com/agents/risk_validator"
        },
        "capabilities": {
            "streaming": True,
            "pushNotifications": True,
            "stateTransitionHistory": True,
            "extensions": [
                {
                    "uri": "https://climate-risk.example.com/extensions/validation",
                    "description": "Risk validation capabilities",
                    "required": True,
                    "params": {
                        "validation_methods": ["cross_reference", "statistical", "expert_review"],
                        "confidence_threshold": 0.95,
                        "max_validation_time": "2m"
                    }
                },
                {
                    "uri": "https://climate-risk.example.com/extensions/anomaly_detection",
                    "description": "Anomaly detection system",
                    "required": True,
                    "params": {
                        "detection_methods": ["statistical", "machine_learning", "rule_based"],
                        "sensitivity_level": ["low", "medium", "high"],
                        "min_confidence": 0.8
                    }
                }
            ],
            "rateLimits": {
                "requests_per_minute": 40,
                "concurrent_validations": 20
            }
        },
        "securitySchemes": {
            "bearer": {
                "type": "bearer",
                "description": "Bearer token authentication",
                "requirements": {
                    "token_format": "JWT",
                    "expiration": "1h",
                    "scopes": ["read", "validate"]
                }
            }
        },
        "defaultInputModes": ["application/json", "text/plain"],
        "defaultOutputModes": ["application/json", "text/plain"],
        "skills": [
            {
                "name": "validate_assessment",
                "description": "Validates a risk assessment",
                "parameters": {
                    "assessment": {
                        "type": "object",
                        "description": "Risk assessment to validate",
                        "required": True,
                        "properties": {
                            "risk_type": {
                                "type": "string",
                                "enum": ["flooding", "heat_wave", "storm", "drought", "wildfire", "coastal"]
                            },
                            "location": {
                                "type": "string",
                                "format": "geojson"
                            },
                            "probability": {
                                "type": "number",
                                "minimum": 0,
                                "maximum": 1
                            },
                            "impact": {
                                "type": "string",
                                "enum": ["low", "medium", "high", "severe"]
                            }
                        }
                    },
                    "validation_method": {
                        "type": "string",
                        "enum": ["cross_reference", "statistical", "expert_review"],
                        "description": "Validation method to use"
                    },
                    "confidence_threshold": {
                        "type": "number",
                        "description": "Minimum confidence for validation",
                        "minimum": 0,
                        "maximum": 1
                    }
                }
            },
            {
                "name": "detect_anomalies",
                "description": "Detects anomalies in risk data",
                "parameters": {
                    "data": {
                        "type": "array",
                        "description": "Risk data to analyze",
                        "required": True,
                        "items": {
                            "type": "object",
                            "properties": {
                                "timestamp": {
                                    "type": "string",
                                    "format": "date-time"
                                },
                                "value": {
                                    "type": "number"
                                },
                                "context": {
                                    "type": "object"
                                }
                            }
                        }
                    },
                    "detection_method": {
                        "type": "string",
                        "enum": ["statistical", "machine_learning", "rule_based"],
                        "description": "Anomaly detection method"
                    },
                    "sensitivity": {
                        "type": "string",
                        "enum": ["low", "medium", "high"],
                        "description": "Detection sensitivity"
                    }
                }
            },
            {
                "name": "verify_prediction",
                "description": "Verifies a risk prediction",
                "parameters": {
                    "prediction": {
                        "type": "object",
                        "description": "Risk prediction to verify",
                        "required": True,
                        "properties": {
                            "risk_type": {
                                "type": "string",
                                "enum": ["flooding", "heat_wave", "storm", "drought", "wildfire", "coastal"]
                            },
                            "location": {
                                "type": "string",
                                "format": "geojson"
                            },
                            "timeframe": {
                                "type": "string",
                                "format": "date-time"
                            },
                            "probability": {
                                "type": "number",
                                "minimum": 0,
                                "maximum": 1
                            }
                        }
                    },
                    "verification_method": {
                        "type": "string",
                        "enum": ["historical", "model", "expert"],
                        "description": "Verification method"
                    },
                    "confidence_threshold": {
                        "type": "number",
                        "description": "Minimum confidence for verification",
                        "minimum": 0,
                        "maximum": 1
                    }
                }
            }
        ],
        "metrics": {
            "performance": {
                "validation_time": "p95 < 1m",
                "anomaly_detection": "p95 < 30s",
                "accuracy": "> 98%"
            },
            "reliability": {
                "false_positive_rate": "< 1%",
                "false_negative_rate": "< 0.1%",
                "verification_confidence": "> 95%"
            }
        }
    }
)

# Historical Data Processor Agent
historical_processor = Agent(
    name="historical_processor",
    description="""
    Processes and analyzes historical climate and risk data. Identifies patterns, trends, and correlations in past events. Provides context for current risk assessments.
    """,
    instructions="""
    You are a historical climate analysis specialist. Your ONLY responsibilities are:
    1. Analyze historical climate data
    2. Identify long-term trends
    3. Compare current conditions to historical patterns
    4. Assess climate change impacts
    5. Provide historical context
    
    You MUST NOT:
    - Make predictions
    - Handle real-time data
    - Process current conditions
    - Monitor news sources
    - Validate data quality
    """,
    model=DEFAULT_MODEL,
    agent_card={
        "name": "historical_processor",
        "description": "Historical climate and risk data processing agent",
        "url": "https://api.climate-risk.example.com/agents/historical_processor",
        "version": "1.0.0",
        "provider": {
            "organization": "Climate Risk Analysis Team",
            "url": "https://climate-risk.example.com",
            "contact": {
                "email": "support@climate-risk.example.com",
                "phone": "+1-555-0123"
            },
            "documentation": "https://docs.climate-risk.example.com/agents/historical_processor"
        },
        "capabilities": {
            "streaming": True,
            "pushNotifications": True,
            "stateTransitionHistory": True,
            "extensions": [
                {
                    "uri": "https://climate-risk.example.com/extensions/historical_analysis",
                    "description": "Historical data analysis capabilities",
                    "required": True,
                    "params": {
                        "max_data_points": 1000000,
                        "time_resolution": ["hourly", "daily", "monthly", "yearly"],
                        "analysis_methods": ["statistical", "machine_learning", "pattern_recognition"],
                        "storage_format": ["parquet", "csv", "json"]
                    }
                },
                {
                    "uri": "https://climate-risk.example.com/extensions/trend_analysis",
                    "description": "Trend analysis capabilities",
                    "required": True,
                    "params": {
                        "trend_types": ["linear", "seasonal", "cyclical", "exponential"],
                        "min_data_points": 100,
                        "confidence_level": 0.95
                    }
                }
            ],
            "rateLimits": {
                "requests_per_minute": 20,
                "concurrent_analyses": 10
            }
        },
        "securitySchemes": {
            "bearer": {
                "type": "bearer",
                "description": "Bearer token authentication",
                "requirements": {
                    "token_format": "JWT",
                    "expiration": "1h",
                    "scopes": ["read", "process"]
                }
            }
        },
        "defaultInputModes": ["application/json", "text/plain"],
        "defaultOutputModes": ["application/json", "text/plain"],
        "skills": [
            {
                "name": "analyze_historical_data",
                "description": "Analyzes historical climate and risk data",
                "parameters": {
                    "data_source": {
                        "type": "string",
                        "description": "Source of historical data",
                        "required": True,
                        "enum": ["climate", "weather", "risk_events", "impact_data"]
                    },
                    "time_range": {
                        "type": "object",
                        "description": "Time range for analysis",
                        "required": True,
                        "properties": {
                            "start": {
                                "type": "string",
                                "format": "date-time"
                            },
                            "end": {
                                "type": "string",
                                "format": "date-time"
                            }
                        }
                    },
                    "location": {
                        "type": "string",
                        "description": "Geographic location identifier",
                        "required": True,
                        "format": "geojson"
                    },
                    "analysis_type": {
                        "type": "string",
                        "enum": ["trend", "pattern", "correlation", "impact"],
                        "description": "Type of analysis to perform"
                    },
                    "resolution": {
                        "type": "string",
                        "enum": ["hourly", "daily", "monthly", "yearly"],
                        "description": "Time resolution for analysis"
                    }
                }
            },
            {
                "name": "identify_patterns",
                "description": "Identifies patterns in historical data",
                "parameters": {
                    "data": {
                        "type": "array",
                        "description": "Historical data to analyze",
                        "required": True,
                        "items": {
                            "type": "object",
                            "properties": {
                                "timestamp": {
                                    "type": "string",
                                    "format": "date-time"
                                },
                                "value": {
                                    "type": "number"
                                },
                                "metadata": {
                                    "type": "object"
                                }
                            }
                        }
                    },
                    "pattern_type": {
                        "type": "string",
                        "enum": ["seasonal", "cyclical", "trend", "anomaly"],
                        "description": "Type of pattern to identify"
                    },
                    "min_confidence": {
                        "type": "number",
                        "description": "Minimum confidence for pattern detection",
                        "minimum": 0,
                        "maximum": 1
                    }
                }
            },
            {
                "name": "correlate_events",
                "description": "Correlates historical events",
                "parameters": {
                    "events": {
                        "type": "array",
                        "description": "Events to correlate",
                        "required": True,
                        "items": {
                            "type": "object",
                            "properties": {
                                "type": {
                                    "type": "string",
                                    "enum": ["climate", "weather", "risk", "impact"]
                                },
                                "timestamp": {
                                    "type": "string",
                                    "format": "date-time"
                                },
                                "location": {
                                    "type": "string",
                                    "format": "geojson"
                                },
                                "severity": {
                                    "type": "number",
                                    "minimum": 0,
                                    "maximum": 1
                                }
                            }
                        }
                    },
                    "correlation_type": {
                        "type": "string",
                        "enum": ["temporal", "spatial", "causal"],
                        "description": "Type of correlation to analyze"
                    },
                    "time_window": {
                        "type": "string",
                        "description": "Time window for correlation analysis"
                    }
                }
            }
        ],
        "metrics": {
            "performance": {
                "processing_time": "p95 < 5m",
                "pattern_detection": "p95 < 2m",
                "correlation_analysis": "p95 < 3m"
            },
            "reliability": {
                "data_accuracy": "> 99%",
                "pattern_confidence": "> 90%",
                "correlation_confidence": "> 85%"
            }
        }
    }
)

# Impact Assessor Agent
impact_assessor = Agent(
    name="impact_assessor",
    description="""
    Assesses potential impacts of climate risks on various sectors and systems. Evaluates vulnerability, exposure, and potential consequences. Provides detailed impact analysis and severity assessments.
    """,
    instructions="""
    // ... existing instructions ...
    """,
    model=DEFAULT_MODEL,
    agent_card={
        "name": "impact_assessor",
        "description": "Climate risk impact assessment agent",
        "url": "https://api.climate-risk.example.com/agents/impact_assessor",
        "version": "1.0.0",
        "provider": {
            "organization": "Climate Risk Analysis Team",
            "url": "https://climate-risk.example.com",
            "contact": {
                "email": "support@climate-risk.example.com",
                "phone": "+1-555-0123"
            },
            "documentation": "https://docs.climate-risk.example.com/agents/impact_assessor"
        },
        "capabilities": {
            "streaming": True,
            "pushNotifications": True,
            "stateTransitionHistory": True,
            "extensions": [
                {
                    "uri": "https://climate-risk.example.com/extensions/impact_analysis",
                    "description": "Impact analysis capabilities",
                    "required": True,
                    "params": {
                        "sectors": ["infrastructure", "agriculture", "health", "economy", "ecosystem"],
                        "impact_types": ["direct", "indirect", "cascading"],
                        "timeframes": ["immediate", "short_term", "long_term"],
                        "severity_levels": ["low", "medium", "high", "severe"]
                    }
                },
                {
                    "uri": "https://climate-risk.example.com/extensions/vulnerability_assessment",
                    "description": "Vulnerability assessment capabilities",
                    "required": True,
                    "params": {
                        "assessment_methods": ["expert", "statistical", "model_based"],
                        "vulnerability_factors": ["exposure", "sensitivity", "adaptive_capacity"],
                        "confidence_threshold": 0.8
                    }
                }
            ],
            "rateLimits": {
                "requests_per_minute": 30,
                "concurrent_assessments": 15
            }
        },
        "securitySchemes": {
            "bearer": {
                "type": "bearer",
                "description": "Bearer token authentication",
                "requirements": {
                    "token_format": "JWT",
                    "expiration": "1h",
                    "scopes": ["read", "assess"]
                }
            }
        },
        "defaultInputModes": ["application/json", "text/plain"],
        "defaultOutputModes": ["application/json", "text/plain"],
        "skills": [
            {
                "name": "assess_impact",
                "description": "Assesses potential impacts of climate risks",
                "parameters": {
                    "risk": {
                        "type": "object",
                        "description": "Risk to assess",
                        "required": True,
                        "properties": {
                            "type": {
                                "type": "string",
                                "enum": ["flooding", "heat_wave", "storm", "drought", "wildfire", "coastal"]
                            },
                            "location": {
                                "type": "string",
                                "format": "geojson"
                            },
                            "probability": {
                                "type": "number",
                                "minimum": 0,
                                "maximum": 1
                            }
                        }
                    },
                    "sectors": {
                        "type": "array",
                        "items": {
                            "type": "string",
                            "enum": ["infrastructure", "agriculture", "health", "economy", "ecosystem"]
                        },
                        "description": "Sectors to assess"
                    },
                    "timeframe": {
                        "type": "string",
                        "enum": ["immediate", "short_term", "long_term"],
                        "description": "Timeframe for impact assessment"
                    },
                    "include_cascading": {
                        "type": "boolean",
                        "description": "Include cascading effects"
                    }
                }
            },
            {
                "name": "evaluate_vulnerability",
                "description": "Evaluates vulnerability to climate risks",
                "parameters": {
                    "location": {
                        "type": "string",
                        "description": "Geographic location identifier",
                        "required": True,
                        "format": "geojson"
                    },
                    "sectors": {
                        "type": "array",
                        "items": {
                            "type": "string",
                            "enum": ["infrastructure", "agriculture", "health", "economy", "ecosystem"]
                        },
                        "description": "Sectors to evaluate"
                    },
                    "assessment_method": {
                        "type": "string",
                        "enum": ["expert", "statistical", "model_based"],
                        "description": "Vulnerability assessment method"
                    },
                    "include_adaptive_capacity": {
                        "type": "boolean",
                        "description": "Include adaptive capacity assessment"
                    }
                }
            },
            {
                "name": "analyze_cascading_effects",
                "description": "Analyzes cascading effects of climate impacts",
                "parameters": {
                    "primary_impact": {
                        "type": "object",
                        "description": "Primary impact to analyze",
                        "required": True,
                        "properties": {
                            "type": {
                                "type": "string",
                                "enum": ["infrastructure", "agriculture", "health", "economy", "ecosystem"]
                            },
                            "severity": {
                                "type": "string",
                                "enum": ["low", "medium", "high", "severe"]
                            },
                            "location": {
                                "type": "string",
                                "format": "geojson"
                            }
                        }
                    },
                    "max_depth": {
                        "type": "integer",
                        "description": "Maximum depth of cascading effects",
                        "minimum": 1,
                        "maximum": 5
                    },
                    "include_probability": {
                        "type": "boolean",
                        "description": "Include probability estimates"
                    }
                }
            }
        ],
        "metrics": {
            "performance": {
                "assessment_time": "p95 < 2m",
                "vulnerability_evaluation": "p95 < 1m",
                "cascading_analysis": "p95 < 3m"
            },
            "reliability": {
                "impact_accuracy": "> 90%",
                "vulnerability_confidence": "> 85%",
                "cascading_confidence": "> 80%"
            }
        }
    }
)

# Recommendation Engine Agent
recommendation_engine = Agent(
    name="recommendation_engine",
    description="""
    Generates actionable recommendations based on risk assessments and impact analysis. Provides mitigation strategies, adaptation measures, and response plans. Prioritizes recommendations based on effectiveness and feasibility.
    """,
    instructions="""
    // ... existing instructions ...
    """,
    model=DEFAULT_MODEL,
    agent_card={
        "name": "recommendation_engine",
        "description": "Climate risk recommendation generation agent",
        "url": "https://api.climate-risk.example.com/agents/recommendation_engine",
        "version": "1.0.0",
        "provider": {
            "organization": "Climate Risk Analysis Team",
            "url": "https://climate-risk.example.com",
            "contact": {
                "email": "support@climate-risk.example.com",
                "phone": "+1-555-0123"
            },
            "documentation": "https://docs.climate-risk.example.com/agents/recommendation_engine"
        },
        "capabilities": {
            "streaming": True,
            "pushNotifications": True,
            "stateTransitionHistory": True,
            "extensions": [
                {
                    "uri": "https://climate-risk.example.com/extensions/recommendation_generation",
                    "description": "Recommendation generation capabilities",
                    "required": True,
                    "params": {
                        "recommendation_types": ["mitigation", "adaptation", "response"],
                        "priority_levels": ["low", "medium", "high", "critical"],
                        "timeframes": ["immediate", "short_term", "long_term"],
                        "max_recommendations": 10
                    }
                },
                {
                    "uri": "https://climate-risk.example.com/extensions/feasibility_analysis",
                    "description": "Recommendation feasibility analysis",
                    "required": True,
                    "params": {
                        "feasibility_factors": ["cost", "time", "resources", "complexity"],
                        "scoring_method": "weighted",
                        "min_confidence": 0.7
                    }
                }
            ],
            "rateLimits": {
                "requests_per_minute": 20,
                "concurrent_generations": 10
            }
        },
        "securitySchemes": {
            "bearer": {
                "type": "bearer",
                "description": "Bearer token authentication",
                "requirements": {
                    "token_format": "JWT",
                    "expiration": "1h",
                    "scopes": ["read", "recommend"]
                }
            }
        },
        "defaultInputModes": ["application/json", "text/plain"],
        "defaultOutputModes": ["application/json", "text/plain"],
        "skills": [
            {
                "name": "generate_recommendations",
                "description": "Generates recommendations based on risk assessment",
                "parameters": {
                    "assessment": {
                        "type": "object",
                        "description": "Risk assessment to base recommendations on",
                        "required": True,
                        "properties": {
                            "risk_type": {
                                "type": "string",
                                "enum": ["flooding", "heat_wave", "storm", "drought", "wildfire", "coastal"]
                            },
                            "severity": {
                                "type": "string",
                                "enum": ["low", "medium", "high", "severe"]
                            },
                            "location": {
                                "type": "string",
                                "format": "geojson"
                            }
                        }
                    },
                    "recommendation_type": {
                        "type": "string",
                        "enum": ["mitigation", "adaptation", "response"],
                        "description": "Type of recommendations to generate"
                    },
                    "timeframe": {
                        "type": "string",
                        "enum": ["immediate", "short_term", "long_term"],
                        "description": "Timeframe for recommendations"
                    },
                    "max_recommendations": {
                        "type": "integer",
                        "description": "Maximum number of recommendations",
                        "minimum": 1,
                        "maximum": 10
                    }
                }
            },
            {
                "name": "analyze_feasibility",
                "description": "Analyzes feasibility of recommendations",
                "parameters": {
                    "recommendations": {
                        "type": "array",
                        "description": "Recommendations to analyze",
                        "required": True,
                        "items": {
                            "type": "object",
                            "properties": {
                                "action": {
                                    "type": "string"
                                },
                                "type": {
                                    "type": "string",
                                    "enum": ["mitigation", "adaptation", "response"]
                                },
                                "timeframe": {
                                    "type": "string",
                                    "enum": ["immediate", "short_term", "long_term"]
                                }
                            }
                        }
                    },
                    "feasibility_factors": {
                        "type": "array",
                        "items": {
                            "type": "string",
                            "enum": ["cost", "time", "resources", "complexity"]
                        },
                        "description": "Factors to consider in feasibility analysis"
                    },
                    "scoring_method": {
                        "type": "string",
                        "enum": ["weighted", "threshold", "composite"],
                        "description": "Method for scoring feasibility"
                    }
                }
            },
            {
                "name": "prioritize_recommendations",
                "description": "Prioritizes recommendations based on effectiveness and feasibility",
                "parameters": {
                    "recommendations": {
                        "type": "array",
                        "description": "Recommendations to prioritize",
                        "required": True,
                        "items": {
                            "type": "object",
                            "properties": {
                                "action": {
                                    "type": "string"
                                },
                                "effectiveness": {
                                    "type": "number",
                                    "minimum": 0,
                                    "maximum": 1
                                },
                                "feasibility": {
                                    "type": "number",
                                    "minimum": 0,
                                    "maximum": 1
                                }
                            }
                        }
                    },
                    "prioritization_method": {
                        "type": "string",
                        "enum": ["effectiveness", "feasibility", "balanced"],
                        "description": "Method for prioritization"
                    },
                    "include_ranking": {
                        "type": "boolean",
                        "description": "Include ranking in output"
                    }
                }
            }
        ],
        "metrics": {
            "performance": {
                "generation_time": "p95 < 1m",
                "feasibility_analysis": "p95 < 30s",
                "prioritization": "p95 < 15s"
            },
            "reliability": {
                "recommendation_quality": "> 90%",
                "feasibility_accuracy": "> 85%",
                "prioritization_accuracy": "> 90%"
            }
        }
    }
)

# --- Agent Capabilities ---
@dataclass
class AgentCapability:
    """Represents a specific capability of an agent."""
    name: str
    description: str
    required_tools: List[str]
    required_model: str = DEFAULT_MODEL
    output_key: Optional[str] = None  # Key for auto-saving agent response to session state

@dataclass
class AgentTeam:
    """Coordinates multiple agents for risk analysis with ADK features.
    
    This class manages a team of specialized agents that work together to analyze
    climate risks and provide recommendations. It includes ADK features for
    performance optimization, reliability, and monitoring.
    
    Attributes:
        session_manager (SessionManager): Manages analysis sessions
        metrics_collector (MetricsCollector): ADK metrics collector
        circuit_breaker (CircuitBreaker): ADK circuit breaker
        worker_pool (WorkerPool): ADK worker pool
        monitoring (Monitoring): ADK monitoring
        buffer (Buffer): ADK buffer
        agents (Dict[str, Agent]): Dictionary of available agents
    """
    
    def __init__(self):
        """Initialize the agent team with ADK features."""
        self.session_manager = SessionManager()
        
        # Initialize ADK features
        self.metrics_collector = MetricsCollector()
        self.circuit_breaker = CircuitBreaker(
            failure_threshold=5,
            reset_timeout=300
        )
        self.worker_pool = WorkerPool(max_workers=MAX_CONCURRENT_AGENTS)
        self.monitoring = Monitoring()
        self.buffer = Buffer()
        
        # Initialize agents
        self.agents = self._initialize_agents()
        
    def _initialize_agents(self) -> Dict[str, Agent]:
        """Initialize agents with ADK features and function-based tools."""
        return {
            "risk_analyzer": Agent(
                name="risk_analyzer",
                description="""
                Analyzes current climate risks and conditions. Evaluates risk severity, monitors thresholds, and identifies emerging patterns. Provides real-time risk assessments for specific locations.
                """,
                instruction="""
                You are a climate risk analysis specialist. Your ONLY responsibilities are:
                1. Analyze current climate conditions for specified locations
                2. Compare conditions against established risk thresholds
                3. Classify risks by type and severity
                4. Identify emerging risk patterns
                5. Validate risk assessments against multiple sources
                
                Use the available tools:
                - analyze_climate_risk(location, time_period, risk_types) to assess risks
                - get_weather_data(location, data_sources) to get current conditions
                
                Always check the status field in tool responses. If status is "error", 
                provide a helpful message and suggest alternatives.
                
                You MUST NOT:
                - Make recommendations
                - Handle user interactions
                - Process historical data
                - Monitor news sources
                - Validate data quality
                """,
                model=DEFAULT_MODEL,
                tools=[analyze_climate_risk, get_weather_data],  # Function-based tools
                metrics_collector=self.metrics_collector,
                circuit_breaker=self.circuit_breaker,
                worker_pool=self.worker_pool,
                monitoring=self.monitoring,
                buffer=self.buffer
            ),
            
            "historical_agent": Agent(
                name="historical_agent",
                description="""
                Analyzes historical climate data and identifies patterns, trends, and anomalies. Provides context for current conditions and future predictions.
                """,
                instruction="""
                You are a historical climate data analyst. Your responsibilities are:
                1. Analyze historical weather patterns and trends
                2. Identify climate anomalies and extreme events
                3. Provide context for current conditions
                4. Support risk assessment with historical data
                5. Identify long-term climate trends
                
                Use the available tools:
                - get_weather_data(location, data_sources) to access historical data
                
                Always provide confidence levels for your historical analysis.
                """,
                model=DEFAULT_MODEL,
                tools=[get_weather_data],  # Function-based tools
                metrics_collector=self.metrics_collector,
                circuit_breaker=self.circuit_breaker,
                worker_pool=self.worker_pool,
                monitoring=self.monitoring,
                buffer=self.buffer
            ),
            
            "news_agent": Agent(
                name="news_agent",
                description="""
                Monitors and analyzes climate-related news, alerts, and emergency information. Provides real-time updates on climate events and their potential impacts.
                """,
                instruction="""
                You are a climate news and alert monitor. Your responsibilities are:
                1. Monitor climate-related news and alerts
                2. Analyze emergency information and warnings
                3. Provide real-time updates on climate events
                4. Assess potential impacts of climate events
                5. Prioritize information by relevance and urgency
                
                Focus on actionable information that affects risk assessment.
                """,
                model=DEFAULT_MODEL,
                tools=[],  # No specific tools needed for news monitoring
                metrics_collector=self.metrics_collector,
                circuit_breaker=self.circuit_breaker,
                worker_pool=self.worker_pool,
                monitoring=self.monitoring,
                buffer=self.buffer
            ),
            
            "recommendation_agent": Agent(
                name="recommendation_agent",
                description="""
                Generates comprehensive climate resilience recommendations based on risk analysis. Prioritizes nature-based solutions and provides cost-benefit analysis.
                """,
                instruction="""
                You are a climate resilience recommendation specialist. Your responsibilities are:
                1. Generate comprehensive recommendations based on risk analysis
                2. Prioritize nature-based solutions over structural solutions
                3. Provide cost-benefit analysis for all recommendations
                4. Consider local context and constraints
                5. Include implementation guidance and timelines
                
                Use the available tools:
                - get_nbs_solutions(location, risk_types, solution_scale) to find nature-based solutions
                - calculate_cost_benefit(solution_id, property_value, timeframe_years) for financial analysis
                - generate_recommendations(risk_analysis, location, solution_types) for comprehensive recommendations
                
                Always prioritize nature-based solutions first, then structural solutions, then emergency preparedness.
                Provide clear cost estimates and ROI calculations for investor decision-making.
                """,
                model=DEFAULT_MODEL,
                tools=[get_nbs_solutions, calculate_cost_benefit, generate_recommendations],  # Function-based tools
                metrics_collector=self.metrics_collector,
                circuit_breaker=self.circuit_breaker,
                worker_pool=self.worker_pool,
                monitoring=self.monitoring,
                buffer=self.buffer
            ),
            
            "validation_agent": Agent(
                name="validation_agent",
                description="""
                Validates and quality-checks all data, analysis results, and recommendations. Ensures accuracy, consistency, and reliability of all outputs.
                """,
                instruction="""
                You are a data validation and quality assurance specialist. Your responsibilities are:
                1. Validate location data and geocoding results
                2. Quality-check risk analysis results
                3. Verify recommendation accuracy and feasibility
                4. Ensure data consistency across all sources
                5. Flag potential issues or inconsistencies
                
                Use the available tools:
                - validate_and_geocode(address, validation_level, include_metadata) to validate locations
                
                Always provide confidence scores for your validation results.
                Flag any data quality issues or inconsistencies.
                """,
                model=DEFAULT_MODEL,
                tools=[validate_and_geocode],  # Function-based tools
                metrics_collector=self.metrics_collector,
                circuit_breaker=self.circuit_breaker,
                worker_pool=self.worker_pool,
                monitoring=self.monitoring,
                buffer=self.buffer
            ),
            
            "greeting_agent": Agent(
                name="greeting_agent",
                description="""
                Handles initial user interactions, explains system capabilities, and guides users through the analysis process.
                """,
                instruction="""
                You are a friendly climate analysis assistant. Your responsibilities are:
                1. Welcome users and explain system capabilities
                2. Guide users through the analysis process
                3. Collect necessary information for analysis
                4. Set appropriate expectations for results
                5. Provide helpful context and explanations
                
                Be welcoming, informative, and helpful. Explain what the system can do and how it works.
                """,
                model=DEFAULT_MODEL,
                tools=[],  # No specific tools needed for greetings
                metrics_collector=self.metrics_collector,
                circuit_breaker=self.circuit_breaker,
                worker_pool=self.worker_pool,
                monitoring=self.monitoring,
                buffer=self.buffer
            ),
            
            "farewell_agent": Agent(
                name="farewell_agent",
                description="""
                Handles user session completion, provides summary of results, and offers next steps or follow-up actions.
                """,
                instruction="""
                You are a session completion specialist. Your responsibilities are:
                1. Summarize analysis results and key findings
                2. Provide clear next steps and recommendations
                3. Offer follow-up options and resources
                4. Ensure user satisfaction with results
                5. Provide contact information for additional support
                
                Be thorough in summarizing results and clear about next steps.
                """,
                model=DEFAULT_MODEL,
                tools=[],  # No specific tools needed for farewells
                metrics_collector=self.metrics_collector,
                circuit_breaker=self.circuit_breaker,
                worker_pool=self.worker_pool,
                monitoring=self.monitoring,
                buffer=self.buffer
            )
        }
        
    async def analyze_risks(self, location: str, time_period: str) -> Dict[str, Any]:
        """Analyze risks using the agent team with ADK features.
        
        Args:
            location (str): Location to analyze
            time_period (str): Time period for analysis
            
        Returns:
            Dict[str, Any]: Analysis results with ADK metrics
        """
        try:
            # Check circuit breaker
            if not self.circuit_breaker.is_allowed("risk_analysis"):
                raise Exception("Circuit breaker is open")
                
            # Track operation with metrics collector
            with self.metrics_collector.track_operation("analyze_risks"):
                # Create new session
                session = await self.session_manager.create_session()
                
                # Use worker pool for parallel agent execution
                async def execute_agent(agent_name: str) -> Dict[str, Any]:
                    agent = self.agents[agent_name]
                    return await agent.handle_request({
                        "location": location,
                        "time_period": time_period
                    })
                
                # Run agents in parallel
                agent_tasks = [
                    execute_agent(agent_name)
                    for agent_name in self.agents.keys()
                ]
                results = await self.worker_pool.execute_parallel(agent_tasks)
                
                # Combine results
                analysis_results = {
                    agent_name: result
                    for agent_name, result in zip(self.agents.keys(), results)
                }
                
                # Update monitoring
                self.monitoring.track_workflow("risk_analysis", {
                    "location": location,
                    "time_period": time_period,
                    "agents_executed": len(results),
                    "successful_agents": sum(1 for r in results if r.get("status") == "success")
                })
                
                # Get ADK metrics
                metrics = {
                    "performance": self.metrics_collector.get_metrics(),
                    "circuit_breaker": self.circuit_breaker.get_status(),
                    "monitoring": self.monitoring.get_metrics(),
                    "resource_usage": self.worker_pool.get_resource_usage()
                }
                
                return {
                    "status": "success",
                    "results": analysis_results,
                    "metrics": metrics
                }
                
        except Exception as e:
            # Record failure in circuit breaker
            self.circuit_breaker.record_failure("risk_analysis")
            logger.error(f"Error in risk analysis: {str(e)}")
            return {
                "status": "error",
                "error": str(e),
                "metrics": self.get_metrics()
            }
            
    def get_metrics(self) -> Dict[str, Any]:
        """Get ADK metrics for the agent team.
        
        Returns:
            Dict[str, Any]: Metrics including performance, resource usage, and circuit breaker status
        """
        return {
            "performance": self.metrics_collector.get_metrics(),
            "circuit_breaker": self.circuit_breaker.get_status(),
            "monitoring": self.monitoring.get_metrics(),
            "resource_usage": self.worker_pool.get_resource_usage(),
            "session_metrics": self.session_manager.get_metrics()
        }

class AgentTeamManager:
    """Manages the team of specialized agents."""
    
    def __init__(self):
        """Initialize the agent team manager."""
        self.session_manager = SessionManager()
        self.team = self._create_agent_team()
    
    def _create_agent_team(self) -> AgentTeam:
        """Create the agent team with specialized agents."""
        return AgentTeam(
            name="Climate Risk Analysis Team",
            description="A team of specialized agents for comprehensive climate risk analysis",
            capabilities=[
                AgentCapability(
                    name="risk_analysis",
                    description="Analyzes current climate risks and conditions",
                    required_tools=["analyze_current_risks", "get_risk_thresholds"],
                    output_key="risk_analysis_result"
                ),
                AgentCapability(
                    name="historical_analysis",
                    description="Analyzes historical climate patterns and trends",
                    required_tools=["get_historical_data", "analyze_trends"],
                    output_key="historical_analysis_result"
                ),
                AgentCapability(
                    name="news_monitoring",
                    description="Monitors real-time climate-related news and alerts",
                    required_tools=["search_risk_news", "get_weather_alerts"],
                    output_key="news_monitoring_result"
                ),
                AgentCapability(
                    name="user_interaction",
                    description="Handles user interactions and session management",
                    required_tools=["say_hello", "offer_assistance", "say_goodbye"],
                    output_key="user_interaction_result"
                ),
                AgentCapability(
                    name="data_validation",
                    description="Ensures data quality and consistency",
                    required_tools=["validate_location", "validate_risk_data"],
                    output_key="validation_result"
                ),
                AgentCapability(
                    name="recommendation",
                    description="Generates actionable recommendations",
                    required_tools=["generate_recommendations", "get_local_resources"],
                    output_key="recommendation_result"
                )
            ],
            agents=[
                root_agent,
                risk_analyzer,
                historical_analyzer,
                news_monitor,
                greeting_agent,
                farewell_agent,
                validation_agent,
                recommendation_agent
            ]
        )
    
    async def handle_request(
        self,
        request: Dict[str, Any],
        session_id: str,
        user_id: str
    ) -> Dict[str, Any]:
        """Handle a user request using the agent team."""
        # Get or create session
        try:
            session = self.session_manager.get_session(session_id)
        except ValueError:
            session = await self.session_manager.create_session(
                user_id=user_id,
                session_id=session_id,
                runner=self,
                initial_state={
                    "request_history": [],
                    "preferred_units": "metric",
                    "preferred_language": "en"
                }
            )
        
        # Update session state with new request
        await self.session_manager.add_to_history(session_id, {
            "type": "request",
            "content": request
        })
        
        # Determine required capabilities
        required_capabilities = self._determine_required_capabilities(request)
        
        # Run agents based on capabilities
        results = {}
        errors = {}
        
        for capability in required_capabilities:
            try:
                result = await self._run_capability(
                    capability=capability,
                    request=request,
                    session=session
                )
                results[capability.name] = result
                
                # Update session state with capability result
                if capability.output_key:
                    await self.session_manager.update_session_state(
                        session_id=session_id,
                        updates={capability.output_key: result}
                    )
                
            except Exception as e:
                errors[capability.name] = str(e)
                await self.session_manager.update_session_state(
                    session_id=session_id,
                    updates={f"{capability.name}_error": str(e)}
                )
        
        # Combine results
        final_result = self._combine_results(results, errors)
        
        # Update session state with final result
        await self.session_manager.add_to_history(session_id, {
            "type": "response",
            "content": final_result
        })
        
        return final_result
    
    def _determine_required_capabilities(
        self,
        request: Dict[str, Any]
    ) -> List[AgentCapability]:
        """Determine which capabilities are required for the request."""
        required = []
        
        # Map request intents to capabilities
        intent = request.get("intent", "")
        parameters = request.get("parameters", {})
        
        if "risk" in intent.lower():
            required.append(self.team.capabilities[0])  # risk_analysis
            required.append(self.team.capabilities[4])  # data_validation
        
        if "historical" in intent.lower():
            required.append(self.team.capabilities[1])  # historical_analysis
            required.append(self.team.capabilities[4])  # data_validation
        
        if "news" in intent.lower() or "alert" in intent.lower():
            required.append(self.team.capabilities[2])  # news_monitoring
        
        if "recommend" in intent.lower():
            required.append(self.team.capabilities[5])  # recommendation
        
        # Always include user interaction for new sessions
        if not parameters.get("is_continuation", False):
            required.append(self.team.capabilities[3])  # user_interaction
        
        return required
    
    async def _run_capability(
        self,
        capability: AgentCapability,
        request: Dict[str, Any],
        session: AnalysisSession
    ) -> Dict[str, Any]:
        """Run a specific capability using appropriate agents."""
        # Get session context
        context = self.session_manager.get_session_context(session.session_id)
        
        # Find agents with required tools
        agents = [
            agent for agent in self.team.agents
            if all(tool in agent.tools for tool in capability.required_tools)
        ]
        
        if not agents:
            raise ValueError(f"No agents found for capability: {capability.name}")
        
        # Run agents in parallel
        async with session.semaphore:
            tasks = [
                self._run_agent(
                    agent=agent,
                    request=request,
                    context=context
                )
                for agent in agents
            ]
            results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Combine results from all agents
        combined_result = {}
        for result in results:
            if isinstance(result, Exception):
                raise result
            combined_result.update(result)
        
        return combined_result
    
    async def _run_agent(
        self,
        agent: Agent,
        request: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Run a specific agent with retry logic."""
        for attempt in range(MAX_RETRY_ATTEMPTS):
            try:
                # Add session context to request
                request_with_context = {
                    **request,
                    "session_context": context
                }
                
                result = await agent.run(request_with_context)
                return result
                
            except Exception as e:
                if attempt == MAX_RETRY_ATTEMPTS - 1:
                    raise e
                await asyncio.sleep(RETRY_DELAY)
    
    def _combine_results(
        self,
        results: Dict[str, Any],
        errors: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Combine results from multiple capabilities."""
        return {
            "status": "success" if not errors else "partial_success",
            "results": results,
            "errors": errors,
            "timestamp": datetime.now().isoformat()
        }
    
    async def get_session_status(self, session_id: str) -> Dict[str, Any]:
        """Get the current status of a session."""
        return self.session_manager.get_session_context(session_id)
    
    async def get_active_sessions(self) -> List[Dict[str, Any]]:
        """Get all active sessions."""
        return [
            self.session_manager.get_session_context(session.session_id)
            for session in self.session_manager.sessions.values()
        ]
    
    async def reset_agent(
        self,
        session_id: str,
        agent_name: str
    ) -> None:
        """Reset a specific agent in a session."""
        session = self.session_manager.get_session(session_id)
        if agent_name in session.agents:
            session.agents[agent_name] = AgentState()
        await self.session_manager._persist_session(session) 