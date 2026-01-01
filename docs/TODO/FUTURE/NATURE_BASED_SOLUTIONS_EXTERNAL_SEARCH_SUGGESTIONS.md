# Suggestions: Enabling Agents to Find Nature-Based Solutions Beyond JSON File

**Date Created**: December 14, 2025  
**Status**: Suggestions Only (No Changes Made)

## Current State Analysis

### **Current Implementation Limitations**

1. **`nature_based_solutions_source.py`**:
   - Only loads solutions from `nature_based_solutions.json`
   - No external search capabilities
   - No web search integration
   - No API calls to external databases

2. **`get_nature_based_solutions_with_biodiversity_tool`** (tools.py):
   - Only calls `loader.get_solutions_by_risk_type()` which pulls from JSON
   - No location-specific search
   - No external data source integration

3. **`get_nbs_solutions`** (tools.py):
   - Contains hardcoded example solutions
   - Not connected to real data sources
   - No location parameter usage for external search

4. **Agent System Instructions**:
   - No explicit instructions to search beyond JSON
   - No guidance on using JSON as examples/reference
   - No workflow for external discovery

## Suggested Changes

### **1. Agent System Prompts/Instructions**

#### **1.1 Add to RecommendationAgent System Prompt**

**Location**: `src/multi_agent_system/agents/recommendation_agent.py` or agent initialization

**Suggested Addition**:
```python
NATURE_BASED_SOLUTIONS_INSTRUCTIONS = """
CRITICAL: Nature-Based Solutions Discovery Workflow

1. START WITH JSON AS EXAMPLES:
   - Load solutions from nature_based_solutions.json as reference examples
   - Use these to understand solution structure, risk types, and implementation patterns
   - DO NOT limit yourself to only these solutions

2. SEARCH FOR LOCATION-SPECIFIC SOLUTIONS:
   - For ANY location worldwide, search for additional nature-based solutions
   - Use web search tools to find solutions specific to the user's location
   - Search for: "[location] nature-based solutions [risk_type]"
   - Search for: "[location] green infrastructure [risk_type]"
   - Search for: "[location] ecosystem-based adaptation"
   - Search for: "[location] nature-based climate adaptation"

3. SEARCH FOR RISK-SPECIFIC SOLUTIONS:
   - For each identified risk type, search for solutions beyond JSON
   - Example: "mangrove restoration [location]" for coastal erosion
   - Example: "urban heat island mitigation [location]" for extreme heat
   - Example: "floodplain restoration [location]" for flooding

4. SEARCH FOR CULTURALLY/ECOLOGICALLY APPROPRIATE SOLUTIONS:
   - Find solutions that work for the specific bioregion
   - Consider local ecosystem compatibility
   - Search for indigenous/traditional knowledge where appropriate
   - Example: "traditional flood management [location]"

5. COMBINE RESULTS:
   - Present JSON examples as "Reference Examples" or "Common Solutions"
   - Present external search results as "Location-Specific Solutions"
   - Clearly distinguish between curated examples and discovered solutions
   - Prioritize location-specific solutions when available

6. VALIDATE AND STRUCTURE:
   - Ensure discovered solutions follow the same structure as JSON examples
   - Include: name, description, risk_types, suitable_locations, benefits, implementation_steps
   - Add source attribution for external solutions
   - Note confidence level for external sources
"""
```

#### **1.2 Add to Agent Tool Descriptions**

**Location**: `src/multi_agent_system/agents/tools.py`

**Suggested Update to `get_nbs_solutions` docstring**:
```python
def get_nbs_solutions(
    location: str,
    risk_types: list[str],
    solution_scale: str = "property"
) -> dict[str, Any]:
    """
    Get nature-based solutions for extreme weather resilience.
    
    IMPORTANT: This function returns curated examples from JSON file.
    Agents MUST also search externally for location-specific solutions.
    
    Workflow:
    1. Get examples from JSON (this function)
    2. Search externally for location-specific solutions (use web search tools)
    3. Combine and present both
    
    Args:
        location (str): The location to find solutions for (e.g., "Mumbai, India", "Lagos, Nigeria")
        risk_types (List[str]): Risk types to address (e.g., ["flooding", "extreme_heat"])
        solution_scale (str): Scale of solutions ("property", "community", "regional")

    Returns:
        Dict[str, Any]: Nature-based solutions with cost/benefit data (EXAMPLES ONLY)
    """
```

### **2. Add Web Search Tool for Nature-Based Solutions**

#### **2.1 New Tool: `search_nature_based_solutions_external`**

**Location**: `src/multi_agent_system/agents/tools.py`

**Suggested Implementation**:
```python
async def search_nature_based_solutions_external(
    location: str,
    risk_types: list[str],
    solution_scale: str = "property"
) -> dict[str, Any]:
    """
    Search for nature-based solutions beyond the JSON file.
    
    This tool searches external sources (web, APIs) to find location-specific
    nature-based solutions that may not be in the curated JSON file.
    
    Args:
        location (str): Location to search for (e.g., "Mumbai, India")
        risk_types (List[str]): Risk types to address
        solution_scale (str): Scale of solutions
        
    Returns:
        Dict[str, Any]: External nature-based solutions with source attribution
    """
    try:
        # TODO: Integrate with web search API (e.g., Google Search API, SerpAPI)
        # TODO: Search for location-specific solutions
        # TODO: Parse and structure results
        # TODO: Add source attribution
        
        # Example search queries:
        search_queries = [
            f"{location} nature-based solutions {risk_type}"
            for risk_type in risk_types
        ]
        search_queries.extend([
            f"{location} green infrastructure {risk_type}"
            for risk_type in risk_types
        ])
        search_queries.append(f"{location} ecosystem-based adaptation")
        
        # Placeholder for web search integration
        external_solutions = []
        
        return {
            "status": "success",
            "data": {
                "location": location,
                "solutions": external_solutions,
                "source": "external_search",
                "search_queries": search_queries,
                "total_solutions": len(external_solutions)
            },
            "metadata": {
                "timestamp": datetime.now().isoformat(),
                "confidence": 0.8  # Lower confidence for external sources
            }
        }
    except Exception as e:
        logger.error(f"Error searching external NBS solutions: {str(e)}")
        return {
            "status": "error",
            "error": str(e)
        }
```

#### **2.2 Add to RecommendationAgent Tools**

**Location**: `src/multi_agent_system/agents/recommendation_agent.py`

**Suggested Addition**:
```python
def __init__(self):
    super().__init__("recommendation_agent")
    self.tools = [
        self.generate_risk_recommendations,
        self.find_local_resources,
        self.prioritize_recommendations,
        self.get_biodiversity_enhanced_solutions,
        self.calculate_ecosystem_service_value,
        # ADD THIS:
        self.search_external_nature_based_solutions  # New tool
    ]

async def search_external_nature_based_solutions(
    self,
    location: str,
    risk_types: list[str],
    solution_scale: str = "property"
) -> dict[str, Any]:
    """Search for location-specific nature-based solutions beyond JSON file."""
    try:
        from .tools import search_nature_based_solutions_external
        result = await search_nature_based_solutions_external(
            location, risk_types, solution_scale
        )
        return {
            "status": "success",
            "result": result,
            "confidence": 0.8
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "confidence": 0.0
        }
```

### **3. Update Nature-Based Solutions Source to Support External Search**

#### **3.1 Add External Search Method**

**Location**: `src/multi_agent_system/data/nature_based_solutions_source.py`

**Suggested Addition**:
```python
async def search_external_solutions(
    self,
    location: str,
    risk_types: list[str],
    geography: str = None
) -> dict[str, Any]:
    """
    Search for nature-based solutions beyond the JSON file.
    
    This method should be called AFTER loading examples from JSON.
    It searches external sources for location-specific solutions.
    
    Args:
        location: Location to search for
        risk_types: Risk types to address
        geography: Optional geography/bioregion identifier
        
    Returns:
        Dict containing external solutions with source attribution
    """
    # TODO: Implement web search integration
    # TODO: Search for location-specific solutions
    # TODO: Parse and structure results
    # TODO: Validate against JSON structure
    
    return {
        "status": "success",
        "data": [],
        "source": "external_search",
        "location": location,
        "risk_types": risk_types
    }
```

#### **3.2 Update `get_solutions` Method Documentation**

**Location**: `src/multi_agent_system/data/nature_based_solutions_source.py`

**Suggested Update**:
```python
async def get_solutions(self,
                      risk_type: str | None = None,
                      location_type: str | None = None,
                      scale: str | None = None,
                      implementation_level: str | None = None) -> dict[str, Any]:
    """
    Get nature-based solutions with multiple filter options.
    
    NOTE: This method returns solutions from the curated JSON file only.
    For location-specific solutions, agents should also call:
    - search_external_solutions() for external search
    - Or use web search tools directly
    
    Args:
        risk_type (Optional[str]): Type of risk (e.g., "flooding", "extreme_heat")
        location_type (Optional[str]): Type of location (e.g., "urban", "rural", "coastal")
        scale (Optional[str]): Scale of implementation (e.g., "local", "city", "regional")
        implementation_level (Optional[str]): Implementation level

    Returns:
        Dict[str, Any]: Nature-based solutions data (CURATED EXAMPLES ONLY)
    """
```

### **4. Update Agent Workflow for Combined Results**

#### **4.1 New Combined Tool: `get_comprehensive_nature_based_solutions`**

**Location**: `src/multi_agent_system/agents/tools.py`

**Suggested Implementation**:
```python
async def get_comprehensive_nature_based_solutions(
    location: str,
    risk_types: list[str],
    solution_scale: str = "property",
    include_external: bool = True
) -> dict[str, Any]:
    """
    Get comprehensive nature-based solutions combining JSON examples and external search.
    
    This is the PRIMARY tool agents should use. It:
    1. Loads curated examples from JSON
    2. Searches externally for location-specific solutions
    3. Combines and structures results
    4. Clearly labels source of each solution
    
    Args:
        location: Location to find solutions for
        risk_types: Risk types to address
        solution_scale: Scale of solutions
        include_external: Whether to search external sources (default: True)
        
    Returns:
        Dict containing both curated examples and external solutions
    """
    try:
        from ..data.data_loader import get_data_loader
        loader = get_data_loader()
        
        # 1. Get curated examples from JSON
        curated_solutions = []
        for risk_type in risk_types:
            risk_solutions = loader.get_solutions_by_risk_type(risk_type)
            curated_solutions.extend(risk_solutions)
        
        # 2. Search externally if requested
        external_solutions = []
        if include_external:
            external_result = await search_nature_based_solutions_external(
                location, risk_types, solution_scale
            )
            if external_result.get("status") == "success":
                external_solutions = external_result.get("data", {}).get("solutions", [])
        
        # 3. Combine and structure
        return {
            "status": "success",
            "data": {
                "curated_examples": {
                    "solutions": curated_solutions,
                    "count": len(curated_solutions),
                    "source": "nature_based_solutions.json",
                    "note": "These are curated examples and reference solutions"
                },
                "location_specific": {
                    "solutions": external_solutions,
                    "count": len(external_solutions),
                    "source": "external_search",
                    "note": "Location-specific solutions discovered through external search"
                },
                "total_solutions": len(curated_solutions) + len(external_solutions),
                "location": location,
                "risk_types": risk_types
            },
            "metadata": {
                "timestamp": datetime.now().isoformat(),
                "curated_confidence": 0.95,
                "external_confidence": 0.8
            }
        }
    except Exception as e:
        logger.error(f"Error getting comprehensive NBS solutions: {str(e)}")
        return {
            "status": "error",
            "error": str(e)
        }
```

### **5. Web Search API Integration Options**

#### **5.1 Google Search API (Recommended)**

**Integration Point**: `src/multi_agent_system/agents/tools.py`

**Suggested Implementation**:
```python
# Add to requirements.txt:
# google-api-python-client>=2.0.0

async def search_google_for_nbs_solutions(
    location: str,
    risk_types: list[str]
) -> list[dict[str, Any]]:
    """
    Search Google for nature-based solutions.
    
    Requires: Google Custom Search API key and Search Engine ID
    """
    try:
        from googleapiclient.discovery import build
        
        # Build search queries
        queries = [
            f"{location} nature-based solutions {risk}"
            for risk in risk_types
        ]
        queries.extend([
            f"{location} green infrastructure {risk}"
            for risk in risk_types
        ])
        
        # TODO: Implement Google Custom Search API calls
        # TODO: Parse results
        # TODO: Extract solution information
        
        return []
    except Exception as e:
        logger.error(f"Google search error: {str(e)}")
        return []
```

#### **5.3 LLM-Based Web Search (Using Agent's Native Capabilities)**

**Alternative Approach**: If agents have web search capabilities through their LLM provider:

**Suggested Implementation**:
```python
async def search_llm_web_for_nbs_solutions(
    location: str,
    risk_types: list[str],
    agent: BaseAgent
) -> list[dict[str, Any]]:
    """
    Use agent's native web search capabilities to find solutions.
    
    This leverages the agent's built-in web search if available.
    """
    try:
        # Construct search prompt
        search_prompt = f"""
        Search for nature-based solutions for {location} addressing {', '.join(risk_types)}.
        Find specific examples, case studies, and implementation guides.
        Return structured data with: name, description, risk_types, benefits, implementation_steps.
        """
        
        # Use agent's web search capability
        # TODO: Implement based on agent's web search tool
        
        return []
    except Exception as e:
        logger.error(f"LLM web search error: {str(e)}")
        return []
```

### **6. External API Integration Options**

#### **6.1 IUCN Global Standard for Nature-Based Solutions**

**Potential API**: IUCN NBS Database (if available)

**Suggested Integration**:
```python
async def search_iucn_nbs_database(
    location: str,
    risk_types: list[str]
) -> list[dict[str, Any]]:
    """
    Search IUCN Global Standard for Nature-Based Solutions database.
    
    Note: Requires verification of API availability
    """
    # TODO: Verify if IUCN has public API
    # TODO: Implement if available
    return []
```

#### **6.2 UNEP Nature-Based Solutions Database**

**Potential API**: UNEP NBS Database (if available)

**Suggested Integration**:
```python
async def search_unep_nbs_database(
    location: str,
    risk_types: list[str]
) -> list[dict[str, Any]]:
    """
    Search UNEP Nature-Based Solutions database.
    
    Note: Requires verification of API availability
    """
    # TODO: Verify if UNEP has public API
    # TODO: Implement if available
    return []
```

### **7. Update Agent Card Documentation**

#### **7.1 Update RecommendationAgent Card**

**Location**: `src/multi_agent_system/agents/recommendation_agent.py`

**Suggested Addition to `agent_card`**:
```python
"capabilities": {
    "skills": [
        # ... existing skills ...
        {
            "name": "search_external_nature_based_solutions",
            "description": "Searches external sources (web, APIs) for location-specific nature-based solutions beyond the curated JSON file. Always use this in combination with get_nbs_solutions to provide comprehensive recommendations.",
            "parameters": {
                "location": {"type": "string", "required": True},
                "risk_types": {"type": "array", "items": {"type": "string"}},
                "solution_scale": {"type": "string", "enum": ["property", "community", "regional"]}
            }
        },
        {
            "name": "get_comprehensive_nature_based_solutions",
            "description": "Primary tool for getting nature-based solutions. Combines curated examples from JSON with location-specific solutions from external search. Always use this for comprehensive recommendations.",
            "parameters": {
                "location": {"type": "string", "required": True},
                "risk_types": {"type": "array", "items": {"type": "string"}},
                "solution_scale": {"type": "string", "enum": ["property", "community", "regional"]},
                "include_external": {"type": "boolean", "default": True}
            }
        }
    ]
}
```

### **8. Documentation Updates**

#### **8.1 Update Agent Guidelines**

**Location**: `docs/1-USER_STORIES_and_PRODUCT/AGENT/Agents_Req_for_Pythia.md`

**Suggested Addition**:
```markdown
### Nature-Based Solutions Discovery

**CRITICAL**: Agents must NOT limit themselves to the curated JSON file.

**Required Workflow**:
1. Load examples from `nature_based_solutions.json` as reference
2. Search externally for location-specific solutions
3. Combine and present both with clear source attribution
4. Prioritize location-specific solutions when available

**Search Strategies**:
- Use web search for "[location] nature-based solutions [risk_type]"
- Search for "[location] green infrastructure [risk_type]"
- Search for "[location] ecosystem-based adaptation"
- Consider bioregion-specific solutions
- Include culturally/ecologically appropriate solutions

**Tool Usage**:
- `get_nbs_solutions()`: Returns curated examples only
- `search_external_nature_based_solutions()`: Searches external sources
- `get_comprehensive_nature_based_solutions()`: Combines both (RECOMMENDED)
```

## Implementation Priority

### **Phase 1: Critical (Immediate)**
1. ✅ Add system prompts/instructions to agents
2. ✅ Update tool docstrings to clarify JSON is examples only
3. ✅ Add `get_comprehensive_nature_based_solutions` tool

### **Phase 2: High Priority**
4. ✅ Integrate web search API (Google Search API or SerpAPI)
5. ✅ Implement `search_external_nature_based_solutions` tool
6. ✅ Update RecommendationAgent to include new tools

### **Phase 3: Medium Priority**
7. ✅ Add external search method to `NatureBasedSolutionsSource`
8. ✅ Update agent card documentation
9. ✅ Add source attribution to all external solutions

### **Phase 4: Future Enhancements**
10. ✅ Verify and integrate IUCN/UNEP NBS databases (if available)
11. ✅ Add LLM-native web search capabilities
12. ✅ Implement solution validation and quality scoring

## Testing Strategy

### **Test Cases**
1. **Location-Specific Search**: Test with locations not in JSON (e.g., "Mumbai, India", "Lagos, Nigeria")
2. **Risk Type Coverage**: Test with risk types not well-covered in JSON
3. **Combined Results**: Verify both curated and external solutions are returned
4. **Source Attribution**: Verify all solutions have clear source labels
5. **Error Handling**: Test behavior when external search fails

## Notes

- **No changes have been made** - these are suggestions only
- **Web search API keys** will be required (Google Search API, SerpAPI, etc.)
- **Rate limiting** should be implemented for external API calls
- **Caching** should be considered for external search results
- **Cost considerations** for web search API usage
- **Compliance** with web search API terms of service

## Related Files

- `src/multi_agent_system/agents/recommendation_agent.py`
- `src/multi_agent_system/agents/tools.py`
- `src/multi_agent_system/data/nature_based_solutions_source.py`
- `src/multi_agent_system/data/nature_based_solutions.json`
- `docs/1-USER_STORIES_and_PRODUCT/AGENT/Agents_Req_for_Pythia.md`


