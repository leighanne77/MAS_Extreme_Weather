# Nature-Based Solutions External Search - Implementation Mapping

Implementation complete
1. src/multi_agent_system/agents/recommendation_agent.py
Updated search_external_nature_based_solutions method with:
Decision support notes in docstring
Disclaimer in return value
Clear notes that results are examples for user review only
Updated agent card with two new capabilities:
search_external_nature_based_solutions (with decision support description)
get_comprehensive_nature_based_solutions (with decision support description)
2. src/multi_agent_system/agents/tools.py
Updated search_nature_based_solutions_external function with:
Decision support notes in docstring
"Extreme weather" terminology in search queries (not "climate")
Disclaimer labels in return data
Decision support metadata flags
Updated get_comprehensive_nature_based_solutions function with:
Decision support notes in docstring
Clear labels separating "curated examples" vs "location-specific" results
Decision support disclaimers in return data
Metadata flags indicating decision support
3. src/multi_agent_system/data/nature_based_solutions_source.py
Added search_external_solutions async method with:
Decision support notes
Geographic filtering support (hierarchical geography)
Bioregional profile considerations
Proper error handling
Updated fetch_data docstring with:
Note that returns JSON-only
Reference to search_external_solutions() for external search
Decision support notes
Updated get_solutions docstring with:
Note that returns JSON-only
Reference to external search methods
Decision support notes
4. docs/1-USER_STORIES_and_PRODUCT/AGENT/Agents_Req_for_Pythia.md
Added "Nature-Based Solutions Discovery" section with:
Decision support boundaries
Required workflow (JSON examples + external search)
Search strategies using "extreme weather" terminology
Tool usage guidelines
Data access constraints
Geographic filtering requirements
Compliance verified
Decision support boundaries: all results labeled as examples for user review
Terminology: uses "extreme weather" not "climate"
Architecture: uses existing A2A protocol (no new architectures)
Data access: only publicly available sources
No promises: all results are examples, not guarantees
Geographic filtering: supports hierarchical geography
All changes pass linting with no errors. The implementation is ready for use.

**Date Created**: December 15, 2025  
**Date Last Updated**: December 15, 2025  
**Purpose**: Map instructions from `NATURE_BASED_SOLUTIONS_EXTERNAL_SEARCH_SUGGESTIONS.md` to specific files in `src/`

**⚠️ IMPORTANT: This document contains SUGGESTIONS ONLY - No changes should be made without explicit user approval**

---

## Project Rules Compliance

This implementation plan complies with:
- **Cursor Rules**: `docs/00_cursor_rules.md` (Architecture Constraints, No File Changes Without Approval, No Real-Time Data Promises)
- **LLM Rules**: `docs/_RULES_Pythia_System_Rules/00_LLM_General_Rules_for_Pythia.md` (Decision Support Boundaries, Data Access Constraints, Terminology Constraints, Value Proposition Boundaries)

### Key Compliance Notes:

1. **Decision Support Tool**: All external search results are for **decision support only**, NOT automated decision-making. Users must review all recommendations.
2. **Terminology**: Use "extreme weather" terminology, NOT "climate" terminology throughout.
3. **No Promises**: External search results are **examples and references only**, not guarantees or promises of outcomes.
4. **Architecture Constraints**: Use existing A2A protocol and `base_agent.py` architecture - do not create new architectures.
5. **Data Access**: External search provides publicly available examples only - no proprietary data access.
6. **No Real-Time**: External search results are batch-processed, not real-time (aligns with 1-6 hour refresh intervals).
7. **Approval Required**: All file changes require explicit user approval before implementation.

---

## Summary

This document maps each suggestion from the external search suggestions file to the specific files where changes need to be implemented. All implementations must:
- Present results as **decision support examples** for user review
- Clearly label external search results as **reference examples only**
- Use **extreme weather** terminology (not "climate")
- Work within existing A2A protocol and agent architecture
- Require explicit approval before any file changes

---

## File-by-File Implementation Map

### 1. `src/multi_agent_system/agents/recommendation_agent.py`

**Status**: ✅ **PARTIALLY IMPLEMENTED** - Instructions already added, but agent card needs updates

#### Already Implemented:
- ✅ `NATURE_BASED_SOLUTIONS_INSTRUCTIONS` constant (lines 6-45) - Already present

#### Still Needed:

**1.1 Add External Search Tool to Agent Tools List**
- **Location**: In `__init__` method or tool registration
- **Action**: Add `search_external_nature_based_solutions` to tools list
- **Architecture**: Must use existing A2A protocol - see `src/multi_agent_system/a2a/` and `base_agent.py`
- **Reference**: Suggestions section 2.2, lines 189-225
- **⚠️ Approval Required**: User must approve before adding to tools list

**1.2 Implement `search_external_nature_based_solutions` Method**
- **Location**: Add as new method in RecommendationAgent class
- **Action**: Implement async method that calls `search_nature_based_solutions_external` from tools
- **Decision Support Note**: Method must clearly indicate results are examples for user review only
- **Reference**: Suggestions section 2.2, lines 202-225
- **⚠️ Approval Required**: User must approve implementation approach

**1.3 Update Agent Card Documentation**
- **Location**: Update `agent_card` dictionary (around line 55)
- **Action**: Add two new skills to `capabilities.skills`:
  - `search_external_nature_based_solutions` - Must note "decision support examples only"
  - `get_comprehensive_nature_based_solutions` - Must note "decision support examples only"
- **Reference**: Suggestions section 7.1, lines 544-570
- **⚠️ Approval Required**: User must approve agent card updates

---

### 2. `src/multi_agent_system/agents/tools.py`

**Status**: ⚠️ **PARTIALLY IMPLEMENTED** - Some functions exist but need completion

#### Already Implemented:
- ✅ `get_nbs_solutions` function (line 165) - Has updated docstring warning it's examples only
- ✅ `search_nature_based_solutions_external` function (line 240) - Exists but is placeholder

#### Still Needed:

**2.1 Complete `search_nature_based_solutions_external` Implementation**
- **Location**: Function at line 240
- **Action**: Replace TODO comments with actual web search integration
- **Decision Support**: Must clearly label results as "reference examples for user review"
- **Terminology**: Use "extreme weather" not "climate" in search queries and responses
- **Data Access**: Only search publicly available sources - no proprietary data
- **Options**:
  - Google Search API integration (section 5.1, lines 390-425)
  - SerpAPI integration (section 5.2, lines 427-461)
  - LLM-native web search (section 5.3, lines 468-494)
- **Reference**: Suggestions section 2.1, lines 122-182
- **⚠️ Approval Required**: User must approve web search API choice and implementation

**2.2 Add `get_comprehensive_nature_based_solutions` Function**
- **Location**: Add new function after `search_nature_based_solutions_external`
- **Action**: Implement comprehensive function that combines JSON examples + external search
- **Decision Support**: Must clearly separate "curated examples" vs "external reference examples"
- **Terminology**: Use "extreme weather" terminology throughout
- **Reference**: Suggestions section 4.1, lines 305-382
- **⚠️ Approval Required**: User must approve function design and return structure

**2.3 Add Web Search API Helper Functions (Optional)**
- **Location**: Add after main NBS functions
- **Action**: Implement one or more of:
  - `search_google_for_nbs_solutions` (section 5.1)
  - `search_serpapi_for_nbs_solutions` (section 5.2)
  - `search_llm_web_for_nbs_solutions` (section 5.3)
- **Geographic Filtering**: Must support geographic filtering per `00_LLM_General_Rules_for_Pythia.md` guidelines
- **Reference**: Suggestions section 5, lines 384-494
- **⚠️ Approval Required**: User must approve API choice and integration approach

---

### 3. `src/multi_agent_system/data/nature_based_solutions_source.py`

**Status**: ❌ **NOT IMPLEMENTED** - Needs new method

#### Still Needed:

**3.1 Add `search_external_solutions` Method**
- **Location**: Add new async method to `NatureBasedSolutionsSource` class
- **Action**: Implement method that searches external sources for location-specific solutions
- **Geographic Filtering**: Must support hierarchical geography (country → region → state → city) per project rules
- **Bioregional Profiles**: Consider bioregional risk profiles when available
- **Decision Support**: Results must be labeled as reference examples only
- **Reference**: Suggestions section 3.1, lines 234-267
- **⚠️ Approval Required**: User must approve method design

**3.2 Update `get_solutions` Method Documentation**
- **Location**: Update docstring for `get_solutions` method (or `fetch_data` method)
- **Action**: Add note that method returns JSON-only, and agents should also call `search_external_solutions()`
- **Decision Support Note**: Add note that all results are examples for user review
- **Reference**: Suggestions section 3.2, lines 273-297
- **⚠️ Approval Required**: User must approve docstring updates

---

### 4. Documentation Files

**Status**: ❌ **NOT IMPLEMENTED**

#### Still Needed:

**4.1 Update Agent Guidelines**
- **Location**: `docs/1-USER_STORIES_and_PRODUCT/AGENT/Agents_Req_for_Pythia.md`
- **Action**: Add "Nature-Based Solutions Discovery" section
- **Decision Support**: Must emphasize decision support boundaries
- **Terminology**: Use "extreme weather" terminology
- **Reference**: Suggestions section 8.1, lines 574-601
- **⚠️ Approval Required**: User must approve documentation additions

---

## Implementation Priority by File

### **Priority 1: Critical (Immediate) - Requires Approval**
1. ✅ `recommendation_agent.py` - Instructions already added
2. ⚠️ `tools.py` - Complete `get_comprehensive_nature_based_solutions` function
3. ⚠️ `recommendation_agent.py` - Add tool to agent card and implement method

### **Priority 2: High Priority - Requires Approval**
4. ⚠️ `tools.py` - Complete `search_nature_based_solutions_external` with web search API
5. ❌ `nature_based_solutions_source.py` - Add `search_external_solutions` method
6. ❌ Documentation - Update agent guidelines

### **Priority 3: Medium Priority - Requires Approval**
7. ⚠️ `tools.py` - Add web search API helper functions (Google/SerpAPI)
8. ⚠️ `recommendation_agent.py` - Update agent card with new capabilities

### **Priority 4: Future Enhancements - Requires Approval**
9. ❌ External API integrations (IUCN, UNEP) - If APIs become available and verified
10. ❌ Solution validation and quality scoring

---

## Detailed Implementation Checklist

### File: `src/multi_agent_system/agents/recommendation_agent.py`

- [ ] **Add `search_external_nature_based_solutions` to tools list**
  - Find `__init__` method or tool registration
  - Add: `self.search_external_nature_based_solutions`
  - **⚠️ Verify**: Uses existing A2A protocol (no new architecture)
  - **⚠️ Approval Required**: User must approve
  
- [ ] **Implement `search_external_nature_based_solutions` method**
  ```python
  async def search_external_nature_based_solutions(
      self,
      location: str,
      risk_types: list[str],
      solution_scale: str = "property"
  ) -> dict[str, Any]:
      """
      Search for location-specific nature-based solutions beyond JSON file.
      
      NOTE: Results are decision support examples for user review only.
      Users must review all recommendations - this is NOT automated decision-making.
      """
      # Implementation from suggestions section 2.2
  ```
  - **⚠️ Approval Required**: User must approve implementation

- [ ] **Update agent_card capabilities**
  - Add `search_external_nature_based_solutions` skill
  - Add `get_comprehensive_nature_based_solutions` skill
  - **Must include**: "Decision support examples only" in descriptions
  - Use format from suggestions section 7.1
  - **⚠️ Approval Required**: User must approve agent card updates

### File: `src/multi_agent_system/agents/tools.py`

- [ ] **Complete `search_nature_based_solutions_external` function**
  - Replace TODO comments (lines 260-263)
  - Implement web search integration
  - **Decision Support**: Add clear labels that results are examples for user review
  - **Terminology**: Use "extreme weather" not "climate" in queries
  - Add source attribution
  - Parse and structure results
  - **⚠️ Approval Required**: User must approve API choice and implementation

- [ ] **Add `get_comprehensive_nature_based_solutions` function**
  - Implement function from suggestions section 4.1
  - Combine JSON examples + external search
  - **Decision Support**: Clearly label "curated examples" vs "external reference examples"
  - Return structured results with source labels
  - **⚠️ Approval Required**: User must approve function design

- [ ] **Add web search API helper (optional)**
  - Choose: Google Search API, SerpAPI, or LLM-native
  - **Geographic Filtering**: Support hierarchical geography per project rules
  - Implement helper function
  - Add to requirements.txt if needed
  - **⚠️ Approval Required**: User must approve API choice

### File: `src/multi_agent_system/data/nature_based_solutions_source.py`

- [ ] **Add `search_external_solutions` method**
  ```python
  async def search_external_solutions(
      self,
      location: str,
      risk_types: list[str],
      geography: str = None
  ) -> dict[str, Any]:
      """
      Search for nature-based solutions beyond the JSON file.
      
      NOTE: Results are decision support examples for user review only.
      This method searches external sources for location-specific examples.
      """
      # Implementation from suggestions section 3.1
  ```
  - **Geographic Filtering**: Support hierarchical geography (country → region → state → city)
  - **Bioregional Profiles**: Consider bioregional risk profiles
  - **⚠️ Approval Required**: User must approve method design

- [ ] **Update `fetch_data` or `get_solutions` docstring**
  - Add note that returns JSON-only
  - Reference `search_external_solutions()` for external search
  - **Decision Support**: Add note that all results are examples for user review
  - **⚠️ Approval Required**: User must approve docstring updates

### File: `docs/1-USER_STORIES_and_PRODUCT/AGENT/Agents_Req_for_Pythia.md`

- [ ] **Add "Nature-Based Solutions Discovery" section**
  - Copy content from suggestions section 8.1
  - Include workflow, search strategies, tool usage
  - **Decision Support**: Emphasize decision support boundaries
  - **Terminology**: Use "extreme weather" terminology
  - **⚠️ Approval Required**: User must approve documentation additions

---

## Dependencies & Requirements

### New Dependencies (if using web search APIs):

**For Google Search API:**
```python
# requirements.txt
google-api-python-client>=2.0.0
```

**For SerpAPI:**
```python
# requirements.txt
serpapi>=0.1.5
```

### Configuration Needed:

- Google Custom Search API key and Search Engine ID (if using Google)
- SerpAPI key (if using SerpAPI)
- Or configure LLM-native web search capabilities
- **⚠️ Note**: All API keys require user approval and secure storage

---

## Testing Strategy

### Test Cases to Implement:

1. **Location-Specific Search**
   - Test with locations not in JSON (e.g., "Mumbai, India", "Lagos, Nigeria")
   - Verify external search returns results
   - **Verify**: Results labeled as "reference examples for user review"

2. **Combined Results**
   - Verify both curated and external solutions returned
   - Check source attribution is clear
   - **Verify**: Decision support labels are present

3. **Error Handling**
   - Test behavior when external search fails
   - Verify graceful degradation to JSON-only results
   - **Verify**: Error messages don't promise unavailable features

4. **Tool Integration**
   - Test `get_comprehensive_nature_based_solutions` end-to-end
   - Verify agent can call new tools
   - **Verify**: Uses existing A2A protocol (no new architecture)

5. **Terminology Compliance**
   - Verify all responses use "extreme weather" not "climate"
   - Verify no financial promises or guarantees
   - Verify decision support boundaries are clear

---

## Project Rules Compliance Checklist

Before implementing any changes, verify:

- [ ] **Architecture Constraints**: Uses existing A2A protocol and `base_agent.py` - no new architectures
- [ ] **Decision Support**: All results clearly labeled as examples for user review only
- [ ] **Terminology**: Uses "extreme weather" not "climate" throughout
- [ ] **No Promises**: No financial promises, guarantees, or outcome percentages
- [ ] **Data Access**: Only publicly available data - no proprietary data access
- [ ] **No Real-Time**: Results are batch-processed, not real-time
- [ ] **Value Proposition**: Stays within defined user personas (Private Equity Investor, Government Funders)
- [ ] **Geographic Filtering**: Supports hierarchical geography and bioregional profiles
- [ ] **Approval Required**: User has explicitly approved all file changes
- [ ] **Documentation**: Change log updated with date and brief description

---

## Notes

- **Current State**: Instructions are already in `recommendation_agent.py`
- **Next Steps**: Focus on completing `get_comprehensive_nature_based_solutions` in `tools.py` (with approval)
- **Web Search**: Choose one API (Google, SerpAPI, or LLM-native) based on availability and cost (with approval)
- **Backwards Compatibility**: All changes should maintain existing functionality
- **Decision Support**: All implementations must emphasize this is decision support, not automated decision-making
- **Approval Workflow**: Present suggestions first, wait for explicit approval, then implement

---

## Related Files Reference

- **Source suggestions**: `docs/TODO/NATURE_BASED_SOLUTIONS_EXTERNAL_SEARCH_SUGGESTIONS.md`
- **Project rules**: `docs/00_cursor_rules.md` and `docs/_RULES_Pythia_System_Rules/00_LLM_General_Rules_for_Pythia.md`
- **Agent implementation**: `src/multi_agent_system/agents/recommendation_agent.py`
- **Tools implementation**: `src/multi_agent_system/agents/tools.py`
- **Data source**: `src/multi_agent_system/data/nature_based_solutions_source.py`
- **Agent guidelines**: `docs/1-USER_STORIES_and_PRODUCT/AGENT/Agents_Req_for_Pythia.md`
- **Architecture reference**: `src/multi_agent_system/agents/base_agent.py` and `src/multi_agent_system/a2a/`
