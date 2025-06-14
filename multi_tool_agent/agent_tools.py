"""
Agent Tools for Climate Risk Analysis

This module provides tools for specialized agents in the climate risk analysis system.
"""

import os
from typing import Dict, List, Optional, Any
from datetime import datetime
import asyncio
from google.adk.agents import Agent
from google.adk.tools import Tool, ToolContext

# Constants for caching
CACHE_DURATIONS = {
    "risk_analysis": 3600,    # 1 hour
    "historical_data": 86400, # 24 hours
    "news": 1800,            # 30 minutes
    "alerts": 300,           # 5 minutes
    "validation": 86400,     # 24 hours
    "resources": 86400       # 24 hours
}

def get_cached_result(
    tool_context: ToolContext,
    cache_key: str,
    cache_duration: int
) -> Optional[Dict[str, Any]]:
    """Get cached result if available and not expired."""
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
    """Update cache with new result."""
    tool_context.state[cache_key] = {
        "timestamp": datetime.now().isoformat(),
        "result": result
    }

# --- Root Orchestrator Tools ---

def register_orchestrator_tools(agent: Agent) -> None:
    """Register tools for the root orchestrator agent."""
    
    @Tool
    async def determine_capabilities(request: Dict) -> Dict:
        """Determine required capabilities for a user request.
        
        Args:
            request (Dict): User request with intent and parameters
            
        Returns:
            Dict: Required capabilities and their priorities
        """
        # Extract intent from request
        intent = request.get("intent", "").lower()
        parameters = request.get("parameters", {})
        
        # Map intents to capabilities
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
        
        # Get base capabilities
        capabilities = capability_map.get(intent, [])
        
        # Add context-specific capabilities
        if parameters.get("location"):
            capabilities.append("data_validation")
            
        return {
            "capabilities": list(set(capabilities)),  # Remove duplicates
            "intent": intent,
            "parameters": parameters
        }
        
    @Tool
    async def combine_results(results: List[Dict], request: Dict) -> Dict:
        """Combine results from multiple agents.
        
        Args:
            results (List[Dict]): Results from agents
            request (Dict): Original user request
            
        Returns:
            Dict: Combined response
        """
        # Filter successful results
        successful_results = [
            r for r in results
            if r.get("status") == "success"
        ]
        
        # Combine results by capability
        combined = {
            r["capability"]: r["result"]
            for r in successful_results
        }
        
        # Add metadata
        return {
            "status": "success",
            "timestamp": datetime.now().isoformat(),
            "request": request,
            "results": combined,
            "capabilities_used": list(combined.keys())
        }
        
    # Register tools with agent
    agent.register_tool(determine_capabilities)
    agent.register_tool(combine_results)

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
        # Check cache
        cached = get_cached_result(
            tool_context,
            f"risk_analysis_{location}",
            CACHE_DURATIONS["risk_analysis"]
        )
        if cached:
            return cached
        
        # Get preferences
        preferred_units = tool_context.state.get("preferred_units", "metric")
        
        # Perform analysis
        result = {
            "status": "success",
            "location": location,
            "time_period": time_period,
            "units": preferred_units,
            "risks": [],
            "timestamp": datetime.now().isoformat()
        }
        
        # Update cache
        update_cache(tool_context, f"risk_analysis_{location}", result)
        
        return result
        
    @Tool
    async def get_risk_thresholds(
        location: str,
        tool_context: ToolContext
    ) -> Dict[str, Any]:
        """Get risk thresholds for a location."""
        # Check cache
        cached = get_cached_result(
            tool_context,
            f"thresholds_{location}",
            CACHE_DURATIONS["risk_analysis"]
        )
        if cached:
            return cached
        
        # Get or set default thresholds
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
        
        # Update cache
        update_cache(tool_context, f"thresholds_{location}", result)
        
        return result
        
    # Register tools with agent
    agent.register_tool(analyze_current_risks)
    agent.register_tool(get_risk_thresholds)

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