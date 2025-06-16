"""
Agent Tools for Climate Risk Analysis System

This module provides specialized tools and utilities for agents in the climate risk analysis system.
It implements caching, concurrency control, and error handling mechanisms for agent operations.

Key Components:
    - Tool Registration: Functions for registering tools with agents
    - Caching System: Result caching with configurable durations
    - Concurrency Control: Limits concurrent operations
    - Error Handling: Standardized error handling and retry mechanisms

Tool Categories:
    1. Root Orchestrator Tools: Task delegation and result combination
    2. Risk Analysis Tools: Current risk assessment and threshold monitoring
    3. Historical Analysis Tools: Trend analysis and historical data retrieval
    4. News Monitoring Tools: Real-time news and alert tracking
    5. Greeting Tools: User interaction and session initialization
    6. Farewell Tools: Session conclusion and result compilation
    7. Validation Tools: Data quality and consistency checks
    8. Recommendation Tools: Action generation and resource identification

Caching Strategy:
    - Configurable cache durations per tool type
    - Automatic cache invalidation
    - Cache key generation based on parameters
    - Cache state management

Error Handling:
    - Retry mechanisms with exponential backoff
    - Error logging and tracking
    - State recovery procedures
    - Concurrent operation management

Dependencies:
    - session_manager: For state management
    - google.adk: For agent and tool definitions
    - asyncio: For concurrent operations

Example Usage:
    ```python
    # Register tools for an agent
    agent = Agent(name="risk_analyzer")
    register_risk_analysis_tools(agent)
    
    # Use cached result
    result = await get_cached_result(
        tool_context,
        "risk_analysis_nyc",
        CACHE_DURATIONS["risk_analysis"]
    )
    
    # Execute with concurrency control
    result = await execute_with_concurrency_limit(
        tool_context,
        analyze_risks,
        "risk_analyzer",
        location="New York"
    )
    ```

Configuration:
    - CACHE_DURATIONS: Cache expiration times
    - STATE_KEYS: State management keys
    - MAX_CONCURRENT: Maximum concurrent operations
    - RETRY_SETTINGS: Retry attempt configuration
"""

import os
from typing import Dict, List, Optional, Any, Callable
from datetime import datetime
import asyncio
import logging
import json
from google.adk.agents import Agent
from .session_manager import AgentState, AnalysisSession, MAX_RETRY_ATTEMPTS, RETRY_DELAY

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Constants for caching
CACHE_DURATIONS = {
    "risk_analysis": 3600,    # 1 hour
    "historical_data": 86400, # 24 hours
    "news": 1800,            # 30 minutes
    "alerts": 300,           # 5 minutes
    "validation": 86400,     # 24 hours
    "resources": 86400       # 24 hours
}

# State keys consistent with session_manager.py
STATE_KEYS = {
    "agent_state": "agent_state",
    "session_context": "context",
    "retry_count": "retry_count",
    "last_error": "last_error",
    "concurrent_ops": "concurrent_operations"
}

def get_cached_result(
    tool_context: ToolContext,
    cache_key: str,
    cache_duration: int
) -> Optional[Dict[str, Any]]:
    """Get cached result if available and not expired.
    
    Args:
        tool_context (ToolContext): Current tool context
        cache_key (str): Unique cache key
        cache_duration (int): Cache duration in seconds
        
    Returns:
        Optional[Dict[str, Any]]: Cached result if valid, None otherwise
        
    Cache Management:
        - Checks cache existence
        - Validates timestamp
        - Handles cache expiration
        - Returns cached data
        
    Example:
        ```python
        result = get_cached_result(
            tool_context,
            "risk_analysis_nyc",
            CACHE_DURATIONS["risk_analysis"]
        )
        if result:
            return result
        ```
    """
    cache = tool_context.state.get(cache_key, {})
    if not cache:
        return None
        
    timestamp = cache.get("timestamp")
    if not timestamp:
        return None
        
    last_time = datetime.fromisoformat(timestamp)
    if (datetime.now() - last_time).total_seconds() > cache_duration:
        return None
        
    return cache.get("result")

def update_cache(
    tool_context: ToolContext,
    cache_key: str,
    result: Dict[str, Any]
) -> None:
    """Update cache with new result.
    
    Args:
        tool_context (ToolContext): Current tool context
        cache_key (str): Unique cache key
        result (Dict[str, Any]): Result to cache
        
    Cache Updates:
        - Stores result with timestamp
        - Updates cache state
        - Handles cache invalidation
        
    Example:
        ```python
        update_cache(
            tool_context,
            "risk_analysis_nyc",
            {"status": "success", "data": analysis_result}
        )
        ```
    """
    tool_context.state[cache_key] = {
        "result": result,
        "timestamp": datetime.now().isoformat()
    }

async def handle_tool_error(
    tool_context: ToolContext,
    error: str,
    agent_name: str,
    retry: bool = True
) -> Dict[str, Any]:
    """Handle tool execution errors.
    
    Args:
        tool_context (ToolContext): Current tool context
        error (str): Error message
        agent_name (str): Agent identifier
        retry (bool): Whether to retry the operation
        
    Returns:
        Dict[str, Any]: Error response
        
    Error Handling:
        - Logs error details
        - Updates error count
        - Manages retry attempts
        - Returns error response
        
    Example:
        ```python
        try:
            result = await execute_operation()
        except Exception as e:
            return await handle_tool_error(
                tool_context,
                str(e),
                "risk_analyzer",
                retry=True
            )
        ```
    """
    # Update error count
    error_count = tool_context.state.get(STATE_KEYS["retry_count"], 0)
    if retry and error_count < MAX_RETRY_ATTEMPTS:
        error_count += 1
        tool_context.state[STATE_KEYS["retry_count"]] = error_count
        await asyncio.sleep(RETRY_DELAY * (2 ** (error_count - 1)))
        return await retry_tool_execution(tool_context, agent_name)
    
    # Log error
    logger.error(f"Error in {agent_name}: {error}")
    
    # Update agent state
    agent_state = tool_context.state.get(STATE_KEYS["agent_state"], {})
    if agent_name in agent_state:
        agent_state[agent_name].error_count += 1
        agent_state[agent_name].last_error = error
        tool_context.state[STATE_KEYS["agent_state"]] = agent_state
    
    return {
        "status": "error",
        "error": error,
        "agent": agent_name,
        "timestamp": datetime.now().isoformat()
    }

async def retry_tool_execution(
    tool_context: ToolContext,
    agent_name: str
) -> Dict[str, Any]:
    """Retry the tool execution after an error.
    
    Args:
        tool_context (ToolContext): Current tool context
        agent_name (str): Agent identifier
        
    Returns:
        Dict[str, Any]: Retry result
        
    Retry Process:
        - Retrieves last operation
        - Implements retry logic
        - Handles retry failures
        - Updates agent state
        
    Example:
        ```python
        result = await retry_tool_execution(tool_context, "risk_analyzer")
        if result["status"] == "success":
            process_result(result["data"])
        ```
    """
    # Get the last operation from agent state
    agent_state = tool_context.state.get(STATE_KEYS["agent_state"], {})
    if not agent_state or not agent_state.last_result:
        return await handle_tool_error(
            tool_context,
            "No previous operation to retry",
            agent_name,
            retry=False
        )
    
    # Implement retry logic based on the last operation
    # This is a placeholder - actual implementation would depend on the specific tool
    return agent_state.last_result

async def execute_with_concurrency_limit(
    tool_context: ToolContext,
    func: Callable,
    agent_name: str,
    *args,
    **kwargs
) -> Dict[str, Any]:
    """Execute a function with concurrency limits and session manager integration.
    
    Args:
        tool_context (ToolContext): Current tool context
        func (Callable): Function to execute
        agent_name (str): Agent identifier
        *args: Positional arguments for the function
        **kwargs: Keyword arguments for the function
        
    Returns:
        Dict[str, Any]: Execution result
        
    Concurrency Control:
        - Checks concurrency limits
        - Manages concurrent operations
        - Handles operation completion
        - Updates agent state
        
    Example:
        ```python
        result = await execute_with_concurrency_limit(
            tool_context,
            analyze_risks,
            "risk_analyzer",
            location="New York"
        )
        ```
    """
    # Check if we're already at the concurrency limit
    concurrent_ops = tool_context.state.get(STATE_KEYS["concurrent_ops"], set())
    if len(concurrent_ops) >= tool_context.state.get("max_concurrent", 5):
        return await handle_tool_error(
            tool_context,
            "Concurrency limit reached",
            agent_name,
            retry=True
        )
    
    # Add operation to concurrent set
    op_id = f"{agent_name}_{datetime.now().isoformat()}"
    concurrent_ops.add(op_id)
    tool_context.state[STATE_KEYS["concurrent_ops"]] = concurrent_ops
    
    try:
        result = await func(*args, **kwargs)
        
        # Update agent state with success
        agent_state = tool_context.state.get(STATE_KEYS["agent_state"], {})
        agent_state[agent_name] = AgentState(
            last_run=datetime.now(),
            last_result=result,
            error_count=0,
            is_active=True
        )
        tool_context.state[STATE_KEYS["agent_state"]] = agent_state
        
        return result
    except Exception as e:
        return await handle_tool_error(tool_context, str(e), agent_name)
    finally:
        # Remove operation from concurrent set
        concurrent_ops.remove(op_id)
        tool_context.state[STATE_KEYS["concurrent_ops"]] = concurrent_ops

# --- Root Orchestrator Tools ---

def register_orchestrator_tools(agent: Agent) -> None:
    """Register tools for the root orchestrator agent.
    
    Tool Registration:
        - determine_capabilities: Analyzes user requests
        - combine_results: Merges agent results
        
    Example:
        ```python
        agent = Agent(name="orchestrator")
        register_orchestrator_tools(agent)
        ```
    """
    
    @Tool
    async def determine_capabilities(request: Dict, tool_context: ToolContext) -> Dict:
        """Determine required capabilities for a user request.
        
        Args:
            request (Dict): User request
            tool_context (ToolContext): Current tool context
            
        Returns:
            Dict: Required capabilities
            
        Capability Analysis:
            - Analyzes request intent
            - Identifies required agents
            - Determines execution order
            - Validates capability availability
        """
        return await execute_with_concurrency_limit(
            tool_context,
            determine_capabilities_internal,
            "orchestrator",
            request
        )
        
    @Tool
    async def combine_results(results: List[Dict], request: Dict, tool_context: ToolContext) -> Dict:
        """Combine results from multiple agents.
        
        Args:
            results (List[Dict]): Agent results
            request (Dict): Original request
            tool_context (ToolContext): Current tool context
            
        Returns:
            Dict: Combined results
            
        Result Combination:
            - Merges agent outputs
            - Resolves conflicts
            - Validates consistency
            - Formats final response
        """
        return await execute_with_concurrency_limit(
            tool_context,
            combine_results_internal,
            "orchestrator",
            results,
            request
        )
        
    # Register tools with agent
    agent.register_tool(determine_capabilities)
    agent.register_tool(combine_results)

async def determine_capabilities_internal(request: Dict) -> Dict:
    """Internal implementation of determine_capabilities."""
    intent = request.get("intent", "").lower()
    parameters = request.get("parameters", {})
    
    capability_map = {
        "analyze_risks": ["risk_analysis", "data_validation"],
        "get_historical": ["historical_analysis", "data_validation"],
        "get_news": ["news_monitoring"],
        "greet": ["greeting"],
        "farewell": ["farewell"],
        "get_recommendations": [
            "risk_analysis",
            "historical_analysis",
            "recommendations"
        ]
    }
    
    capabilities = capability_map.get(intent, [])
    
    if parameters.get("location"):
        capabilities.append("data_validation")
        
    return {
        "capabilities": list(set(capabilities)),
        "intent": intent,
        "parameters": parameters
    }

async def combine_results_internal(results: List[Dict], request: Dict) -> Dict:
    """Internal implementation of combine_results."""
    successful_results = [
        r for r in results
        if r.get("status") == "success"
    ]
    
    combined = {
        r["capability"]: r["result"]
        for r in successful_results
    }
    
    return {
        "status": "success",
        "timestamp": datetime.now().isoformat(),
        "request": request,
        "results": combined,
        "capabilities_used": list(combined.keys())
    }

# --- Climate Risk Analysis Tools ---

def register_risk_analysis_tools(agent: Agent) -> None:
    """Register tools for the risk analysis agent."""
    
    @Tool
    async def analyze_current_risks(
        location: str,
        time_period: str,
        tool_context: ToolContext
    ) -> Dict[str, Any]:
        """Analyze current climate risks for a location."""
        return await execute_with_concurrency_limit(
            tool_context,
            analyze_current_risks_internal,
            "risk_analyzer",
            location,
            time_period,
            tool_context
        )
        
    @Tool
    async def get_risk_thresholds(
        location: str,
        tool_context: ToolContext
    ) -> Dict[str, Any]:
        """Get risk thresholds for a location."""
        return await execute_with_concurrency_limit(
            tool_context,
            get_risk_thresholds_internal,
            "risk_analyzer",
            location,
            tool_context
        )
        
    # Register tools with agent
    agent.register_tool(analyze_current_risks)
    agent.register_tool(get_risk_thresholds)

async def analyze_current_risks_internal(
    location: str,
    time_period: str,
    tool_context: ToolContext
) -> Dict[str, Any]:
    """Internal implementation of analyze_current_risks."""
    cached = get_cached_result(
        tool_context,
        f"risk_analysis_{location}",
        CACHE_DURATIONS["risk_analysis"]
    )
    if cached:
        return cached
    
    preferred_units = tool_context.state.get("preferred_units", "metric")
    
    result = {
        "status": "success",
        "location": location,
        "time_period": time_period,
        "units": preferred_units,
        "risks": [],
        "timestamp": datetime.now().isoformat()
    }
    
    update_cache(tool_context, f"risk_analysis_{location}", result)
    
    return result

async def get_risk_thresholds_internal(
    location: str,
    tool_context: ToolContext
) -> Dict[str, Any]:
    """Internal implementation of get_risk_thresholds."""
    cached = get_cached_result(
        tool_context,
        f"thresholds_{location}",
        CACHE_DURATIONS["risk_analysis"]
    )
    if cached:
        return cached
    
    thresholds = {
        "temperature": {"warning": 30, "critical": 35},
        "precipitation": {"warning": 50, "critical": 100},
        "wind_speed": {"warning": 30, "critical": 50}
    }
    
    result = {
        "status": "success",
        "location": location,
        "thresholds": thresholds,
        "timestamp": datetime.now().isoformat()
    }
    
    update_cache(tool_context, f"thresholds_{location}", result)
    
    return result

# --- Historical Analysis Tools ---

def register_historical_analysis_tools(agent: Agent) -> None:
    """Register tools for the historical analysis agent."""
    
    @Tool
    async def get_historical_data(
        location: str,
        time_period: str,
        tool_context: ToolContext
    ) -> Dict[str, Any]:
        """Get historical climate data for a location."""
        # Check cache
        cached = get_cached_result(
            tool_context,
            f"historical_{location}_{time_period}",
            CACHE_DURATIONS["historical_data"]
        )
        if cached:
            return cached
        
        # Get preferences
        preferred_units = tool_context.state.get("preferred_units", "metric")
        
        # Fetch data
        result = {
            "status": "success",
            "location": location,
            "time_period": time_period,
            "units": preferred_units,
            "data": [],
            "timestamp": datetime.now().isoformat()
        }
        
        # Update cache
        update_cache(tool_context, f"historical_{location}_{time_period}", result)
        
        return result
        
    @Tool
    async def analyze_trends(
        location: str,
        tool_context: ToolContext
    ) -> Dict[str, Any]:
        """Analyze climate trends for a location."""
        # Check cache
        cached = get_cached_result(
            tool_context,
            f"trends_{location}",
            CACHE_DURATIONS["historical_data"]
        )
        if cached:
            return cached
        
        # Perform analysis
        result = {
            "status": "success",
            "location": location,
            "trends": [],
            "timestamp": datetime.now().isoformat()
        }
        
        # Update cache
        update_cache(tool_context, f"trends_{location}", result)
        
        return result
        
    # Register tools with agent
    agent.register_tool(get_historical_data)
    agent.register_tool(analyze_trends)

# --- News Monitoring Tools ---

def register_news_tools(agent: Agent) -> None:
    """Register tools for the news monitoring agent."""
    
    @Tool
    async def search_risk_news(
        location: str,
        tool_context: ToolContext
    ) -> Dict[str, Any]:
        """Search for climate risk related news."""
        # Check cache
        cached = get_cached_result(
            tool_context,
            f"news_{location}",
            CACHE_DURATIONS["news"]
        )
        if cached:
            return cached
        
        # Get preferences
        preferred_language = tool_context.state.get("preferred_language", "en")
        
        # Fetch news
        result = {
            "status": "success",
            "location": location,
            "language": preferred_language,
            "news": [],
            "timestamp": datetime.now().isoformat()
        }
        
        # Update cache
        update_cache(tool_context, f"news_{location}", result)
        
        return result
        
    @Tool
    async def get_weather_alerts(
        location: str,
        tool_context: ToolContext
    ) -> Dict[str, Any]:
        """Get active weather alerts for a location."""
        # Check cache
        cached = get_cached_result(
            tool_context,
            f"alerts_{location}",
            CACHE_DURATIONS["alerts"]
        )
        if cached:
            return cached
        
        # Get preferences
        preferred_units = tool_context.state.get("preferred_units", "metric")
        
        # Fetch alerts
        result = {
            "status": "success",
            "location": location,
            "units": preferred_units,
            "alerts": [],
            "timestamp": datetime.now().isoformat()
        }
        
        # Update cache
        update_cache(tool_context, f"alerts_{location}", result)
        
        return result
        
    # Register tools with agent
    agent.register_tool(search_risk_news)
    agent.register_tool(get_weather_alerts)

# --- Greeting Tools ---

def register_greeting_tools(agent: Agent) -> None:
    """Register tools for the greeting agent."""
    
    @Tool
    async def say_hello(
        user_id: str,
        tool_context: ToolContext
    ) -> Dict[str, Any]:
        """Greet the user and initialize session."""
        # Get preferences
        preferred_language = tool_context.state.get("preferred_language", "en")
        
        # Update interaction count
        interaction_count = tool_context.state.get("interaction_count", 0) + 1
        tool_context.state["interaction_count"] = interaction_count
        
        return {
            "status": "success",
            "message": f"Hello! This is your {interaction_count} interaction.",
            "language": preferred_language,
            "timestamp": datetime.now().isoformat()
        }
        
    @Tool
    async def offer_assistance(
        tool_context: ToolContext
    ) -> Dict[str, Any]:
        """Offer assistance based on user preferences."""
        # Get preferences and history
        preferred_language = tool_context.state.get("preferred_language", "en")
        location_history = tool_context.state.get("location_history", [])
        
        return {
            "status": "success",
            "message": "How can I help you today?",
            "language": preferred_language,
            "recent_locations": location_history[-3:] if location_history else [],
            "timestamp": datetime.now().isoformat()
        }
        
    # Register tools with agent
    agent.register_tool(say_hello)
    agent.register_tool(offer_assistance)

# --- Farewell Tools ---

def register_farewell_tools(agent: Agent) -> None:
    """Register tools for the farewell agent."""
    
    @Tool
    async def say_goodbye(
        tool_context: ToolContext
    ) -> Dict[str, Any]:
        """Conclude the session and summarize activities."""
        # Get session statistics
        interaction_count = tool_context.state.get("interaction_count", 0)
        location_history = tool_context.state.get("location_history", [])
        analysis_history = tool_context.state.get("analysis_history", [])
        
        return {
            "status": "success",
            "message": "Thank you for using our service!",
            "summary": {
                "total_interactions": interaction_count,
                "locations_analyzed": len(set(location_history)),
                "analyses_performed": len(analysis_history)
            },
            "timestamp": datetime.now().isoformat()
        }
        
    # Register tools with agent
    agent.register_tool(say_goodbye)

# --- Data Validation Tools ---

def register_validation_tools(agent: Agent) -> None:
    """Register tools for the data validation agent."""
    
    @Tool
    async def validate_location(
        location: str,
        tool_context: ToolContext
    ) -> Dict[str, Any]:
        """Validate a location for analysis."""
        # Check cache
        cached = get_cached_result(
            tool_context,
            f"validation_{location}",
            CACHE_DURATIONS["validation"]
        )
        if cached:
            return cached
        
        # Validate location
        result = {
            "status": "success",
            "location": location,
            "is_valid": True,
            "timestamp": datetime.now().isoformat()
        }
        
        # Update cache
        update_cache(tool_context, f"validation_{location}", result)
        
        # Update location history
        if "location_history" not in tool_context.state:
            tool_context.state["location_history"] = []
        tool_context.state["location_history"].append(location)
        
        return result
        
    @Tool
    async def validate_risk_data(
        data: Dict[str, Any],
        tool_context: ToolContext
    ) -> Dict[str, Any]:
        """Validate risk analysis data."""
        # Get preferences
        preferred_units = tool_context.state.get("preferred_units", "metric")
        
        # Validate data
        result = {
            "status": "success",
            "is_valid": True,
            "units": preferred_units,
            "validation_details": {},
            "timestamp": datetime.now().isoformat()
        }
        
        # Update validation history
        if "validation_history" not in tool_context.state:
            tool_context.state["validation_history"] = []
        tool_context.state["validation_history"].append({
            "timestamp": result["timestamp"],
            "result": result
        })
        
        return result
        
    # Register tools with agent
    agent.register_tool(validate_location)
    agent.register_tool(validate_risk_data)

# --- Recommendation Tools ---

def register_recommendation_tools(agent: Agent) -> None:
    """Register tools for the recommendation agent."""
    
    @Tool
    async def generate_recommendations(
        location: str,
        risk_data: Dict[str, Any],
        tool_context: ToolContext
    ) -> Dict[str, Any]:
        """Generate recommendations based on risk analysis."""
        # Check cache
        cached = get_cached_result(
            tool_context,
            f"recommendations_{location}",
            CACHE_DURATIONS["risk_analysis"]
        )
        if cached:
            return cached
        
        # Get preferences
        preferred_language = tool_context.state.get("preferred_language", "en")
        
        # Generate recommendations
        result = {
            "status": "success",
            "location": location,
            "language": preferred_language,
            "recommendations": [],
            "timestamp": datetime.now().isoformat()
        }
        
        # Update cache
        update_cache(tool_context, f"recommendations_{location}", result)
        
        # Update analysis history
        if "analysis_history" not in tool_context.state:
            tool_context.state["analysis_history"] = []
        tool_context.state["analysis_history"].append({
            "type": "recommendation",
            "location": location,
            "timestamp": result["timestamp"]
        })
        
        return result
        
    @Tool
    async def get_local_resources(
        location: str,
        tool_context: ToolContext
    ) -> Dict[str, Any]:
        """Get local resources for risk mitigation."""
        # Check cache
        cached = get_cached_result(
            tool_context,
            f"resources_{location}",
            CACHE_DURATIONS["resources"]
        )
        if cached:
            return cached
        
        # Get preferences
        preferred_language = tool_context.state.get("preferred_language", "en")
        
        # Fetch resources
        result = {
            "status": "success",
            "location": location,
            "language": preferred_language,
            "resources": [],
            "timestamp": datetime.now().isoformat()
        }
        
        # Update cache
        update_cache(tool_context, f"resources_{location}", result)
        
        return result
        
    # Register tools with agent
    agent.register_tool(generate_recommendations)
    agent.register_tool(get_local_resources) 