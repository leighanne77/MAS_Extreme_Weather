# Suggestions: src/ Files to Help Agents Enforce 00_LLM Rules

**Date Created**: December 14, 2025  
**Status**: Suggestions Only (No Changes Made)  
**Based On**: `docs/_RULES_Pythia_System_Rules/00_LLM_General_Rules_for_Pythia.md`

## Overview

This document suggests what should be added to `src/` files to help agents automatically enforce the rules defined in `00_LLM_General_Rules_for_Pythia.md`. These suggestions focus on programmatic enforcement rather than relying solely on documentation.

## Current State Analysis

### **Existing Enforcement Mechanisms:**
- ✅ `RequestValidator` in `base_agent.py` - Basic request validation
- ✅ `DataGovernance` in `governance.py` - Policy-based data compliance
- ✅ `DataValidator` in `validators.py` - Schema-based validation
- ⚠️ **Missing**: Terminology filtering, constraint enforcement, response sanitization

### **Gaps Identified:**
- No terminology filtering (climate, carbon terms)
- No decision support boundary enforcement
- No data access constraint validation
- No response sanitization before sending to users
- No geographic data access validation
- No user persona validation

## Suggested Implementations

### **1. System Constraints Validator**

#### **File**: `src/multi_agent_system/utils/constraint_validator.py`

**Purpose**: Validate agent responses and actions against system constraints before sending to users.

**Suggested Implementation**:
```python
"""
System Constraints Validator

Validates agent responses and actions against rules defined in
docs/_RULES_Pythia_System_Rules/00_LLM_General_Rules_for_Pythia.md
"""

from typing import Any, Dict, List
from dataclasses import dataclass
from enum import Enum

class ConstraintViolationType(Enum):
    TERMINOLOGY = "terminology"
    DATA_ACCESS = "data_access"
    DECISION_SUPPORT = "decision_support"
    FINANCIAL_PROMISE = "financial_promise"
    ENVIRONMENTAL_CLAIM = "environmental_claim"
    INTEGRATION = "integration"
    USER_PERSONA = "user_persona"
    REAL_TIME_DATA = "real_time_data"

@dataclass
class ConstraintViolation:
    violation_type: ConstraintViolationType
    message: str
    severity: str  # "error", "warning"
    suggested_fix: str

class SystemConstraintValidator:
    """Validates agent responses against system constraints."""
    
    def __init__(self):
        # Load constraint rules from config
        self.terminology_rules = self._load_terminology_rules()
        self.data_access_rules = self._load_data_access_rules()
        self.decision_support_rules = self._load_decision_support_rules()
        # ... other rule sets
    
    def validate_response(self, response: str, context: Dict[str, Any]) -> List[ConstraintViolation]:
        """Validate agent response against all system constraints."""
        violations = []
        
        # Check terminology
        violations.extend(self._check_terminology(response))
        
        # Check data access promises
        violations.extend(self._check_data_access_promises(response))
        
        # Check decision support boundaries
        violations.extend(self._check_decision_support(response))
        
        # Check financial promises
        violations.extend(self._check_financial_promises(response))
        
        # Check environmental claims
        violations.extend(self._check_environmental_claims(response))
        
        # Check integration promises
        violations.extend(self._check_integration_promises(response))
        
        # Check real-time data promises
        violations.extend(self._check_realtime_promises(response))
        
        return violations
    
    def _check_terminology(self, text: str) -> List[ConstraintViolation]:
        """Check for prohibited terminology (climate, carbon terms)."""
        violations = []
        
        # Prohibited terms
        prohibited_terms = {
            "climate": "extreme weather-related",
            "climate change": "extreme weather patterns",
            "climate risk": "extreme weather risk",
            "climate resilience": "extreme weather resilience",
            "carbon credit": None,  # Should not be used at all
            "carbon market": None,
            "carbon trading": None,
            "carbon sequestration": "biodiversity benefits or ecosystem services",
            "carbon reduction": "environmental benefits",
        }
        
        text_lower = text.lower()
        for prohibited, replacement in prohibited_terms.items():
            if prohibited in text_lower:
                violations.append(ConstraintViolation(
                    violation_type=ConstraintViolationType.TERMINOLOGY,
                    message=f"Prohibited term '{prohibited}' found",
                    severity="error",
                    suggested_fix=f"Replace with '{replacement}'" if replacement else "Remove this term entirely"
                ))
        
        return violations
    
    def _check_data_access_promises(self, text: str) -> List[ConstraintViolation]:
        """Check for promises about proprietary data access."""
        violations = []
        
        prohibited_phrases = [
            "access your proprietary data",
            "connect to your internal systems",
            "integrate with your database",
            "real-time data access",
            "live data feed",
        ]
        
        text_lower = text.lower()
        for phrase in prohibited_phrases:
            if phrase in text_lower:
                violations.append(ConstraintViolation(
                    violation_type=ConstraintViolationType.DATA_ACCESS,
                    message=f"Prohibited data access promise: '{phrase}'",
                    severity="error",
                    suggested_fix="Remove promise of proprietary data access. Use external data sources only."
                ))
        
        return violations
    
    def _check_decision_support(self, text: str) -> List[ConstraintViolation]:
        """Check that decision support boundaries are respected."""
        violations = []
        
        # Must include decision support disclaimer
        required_phrases = [
            "decision support",
            "for your review",
            "not automated",
        ]
        
        # Prohibited phrases
        prohibited_phrases = [
            "automated decision",
            "automatic integration",
            "seamless integration",
            "direct integration",
        ]
        
        text_lower = text.lower()
        
        # Check for prohibited phrases
        for phrase in prohibited_phrases:
            if phrase in text_lower:
                violations.append(ConstraintViolation(
                    violation_type=ConstraintViolationType.DECISION_SUPPORT,
                    message=f"Prohibited phrase: '{phrase}'",
                    severity="error",
                    suggested_fix="Remove automation/integration promises. Emphasize decision support only."
                ))
        
        # Warn if decision support disclaimer is missing
        has_disclaimer = any(phrase in text_lower for phrase in required_phrases)
        if not has_disclaimer and any(keyword in text_lower for keyword in ["recommend", "suggest", "analysis"]):
            violations.append(ConstraintViolation(
                violation_type=ConstraintViolationType.DECISION_SUPPORT,
                message="Missing decision support disclaimer",
                severity="warning",
                suggested_fix="Add: 'This is a decision support tool, not a decision-making tool. Recommendations are for your review only and cannot be automated.'"
            ))
        
        return violations
    
    def _check_financial_promises(self, text: str) -> List[ConstraintViolation]:
        """Check for prohibited financial promises (ROI guarantees, specific percentages)."""
        violations = []
        
        import re
        
        # Check for specific percentage promises
        percentage_pattern = r'\b(\d+)%\s+(improvement|increase|return|ROI|guarantee)'
        matches = re.findall(percentage_pattern, text, re.IGNORECASE)
        if matches:
            for match in matches:
                violations.append(ConstraintViolation(
                    violation_type=ConstraintViolationType.FINANCIAL_PROMISE,
                    message=f"Specific percentage promise found: '{match[0]}% {match[1]}'",
                    severity="error",
                    suggested_fix="Replace with 'statistically significant and measurable improvements' or 'range of likely outcomes'"
                ))
        
        # Check for ROI guarantees
        guarantee_phrases = [
            "guaranteed roi",
            "roi guarantee",
            "guaranteed return",
            "promised return",
        ]
        
        text_lower = text.lower()
        for phrase in guarantee_phrases:
            if phrase in text_lower:
                violations.append(ConstraintViolation(
                    violation_type=ConstraintViolationType.FINANCIAL_PROMISE,
                    message=f"ROI guarantee found: '{phrase}'",
                    severity="error",
                    suggested_fix="Remove guarantee. Use 'range of likely outcomes' instead."
                ))
        
        return violations
    
    def _check_environmental_claims(self, text: str) -> List[ConstraintViolation]:
        """Check for unvalidated environmental claims."""
        violations = []
        
        # Phrases that require validation
        claim_phrases = [
            "will reduce carbon",
            "carbon reduction of",
            "certified environmental",
            "complies with environmental standard",
        ]
        
        text_lower = text.lower()
        for phrase in claim_phrases:
            if phrase in text_lower:
                violations.append(ConstraintViolation(
                    violation_type=ConstraintViolationType.ENVIRONMENTAL_CLAIM,
                    message=f"Unvalidated environmental claim: '{phrase}'",
                    severity="warning",
                    suggested_fix="Remove specific environmental impact claims. Use 'environmental benefits' or 'biodiversity benefits' instead."
                ))
        
        return violations
    
    def _check_integration_promises(self, text: str) -> List[ConstraintViolation]:
        """Check for prohibited integration promises."""
        violations = []
        
        prohibited_phrases = [
            "seamless integration",
            "direct integration",
            "automatic integration",
            "connect to your systems",
            "api access to your database",
        ]
        
        text_lower = text.lower()
        for phrase in prohibited_phrases:
            if phrase in text_lower:
                violations.append(ConstraintViolation(
                    violation_type=ConstraintViolationType.INTEGRATION,
                    message=f"Prohibited integration promise: '{phrase}'",
                    severity="error",
                    suggested_fix="Remove integration promise. State: 'Export-based integration only. Users can manually incorporate results into their systems.'"
                ))
        
        return violations
    
    def _check_realtime_promises(self, text: str) -> List[ConstraintViolation]:
        """Check for real-time data promises."""
        violations = []
        
        prohibited_phrases = [
            "real-time data",
            "live data",
            "instant updates",
            "real-time monitoring",
            "live feed",
        ]
        
        text_lower = text.lower()
        for phrase in prohibited_phrases:
            if phrase in text_lower:
                violations.append(ConstraintViolation(
                    violation_type=ConstraintViolationType.REAL_TIME_DATA,
                    message=f"Real-time data promise found: '{phrase}'",
                    severity="error",
                    suggested_fix="Replace with 'scheduled data updates (1-6 hour refresh intervals, not real-time)'"
                ))
        
        return violations
    
    def _load_terminology_rules(self) -> Dict[str, str]:
        """Load terminology replacement rules from config."""
        # TODO: Load from config file
        return {}
    
    def _load_data_access_rules(self) -> Dict[str, Any]:
        """Load data access constraint rules from config."""
        # TODO: Load from config file
        return {}
    
    def _load_decision_support_rules(self) -> Dict[str, Any]:
        """Load decision support boundary rules from config."""
        # TODO: Load from config file
        return {}
```

**Integration Point**: Add to `BaseAgent._execute_request()` method to validate responses before returning.

---

### **2. Terminology Filter Configuration**

#### **File**: `src/multi_agent_system/config/terminology_rules.json`

**Purpose**: Centralized configuration for prohibited and replacement terminology.

**Suggested Structure**:
```json
{
  "prohibited_terms": {
    "climate": {
      "replacement": "extreme weather-related",
      "severity": "error",
      "contexts": ["risk", "resilience", "adaptation", "change"]
    },
    "carbon credit": {
      "replacement": null,
      "severity": "error",
      "message": "Do not reference carbon credits. Use 'biodiversity benefits' or 'ecosystem services' instead."
    },
    "carbon market": {
      "replacement": null,
      "severity": "error",
      "message": "Do not reference carbon markets."
    },
    "carbon trading": {
      "replacement": null,
      "severity": "error",
      "message": "Do not reference carbon trading."
    },
    "carbon sequestration": {
      "replacement": "biodiversity benefits or ecosystem services",
      "severity": "error"
    },
    "real-time": {
      "replacement": "scheduled updates (1-6 hour refresh intervals, not real-time)",
      "severity": "error"
    },
    "live data": {
      "replacement": "scheduled data updates",
      "severity": "error"
    }
  },
  "required_phrases": {
    "decision_support_disclaimer": {
      "phrases": ["decision support", "for your review", "not automated"],
      "required_when": ["recommend", "suggest", "analysis"],
      "severity": "warning"
    }
  },
  "allowed_terms": [
    "extreme weather",
    "extreme weather-related risk",
    "extreme weather resilience",
    "biodiversity",
    "ecosystem services",
    "environmental benefits"
  ]
}
```

---

### **3. System Constraints Configuration**

#### **File**: `src/multi_agent_system/config/system_constraints.json`

**Purpose**: Centralized configuration for all system constraints.

**Suggested Structure**:
```json
{
  "data_access": {
    "cannot_access": [
      "user-specific proprietary data",
      "internal business models",
      "confidential financial information",
      "individual performance metrics",
      "internal risk models",
      "QOF performance data",
      "individual investment performance data"
    ],
    "can_provide": [
      "publicly available extreme weather risk data",
      "government-published environmental and infrastructure data",
      "scientific and research datasets",
      "compliance and regulatory information",
      "geographic-specific risk assessments",
      "infrastructure resilience metrics",
      "nature-based solutions data filtered by location"
    ],
    "refresh_intervals": {
      "min_hours": 1,
      "max_hours": 6,
      "message": "scheduled data updates (1-6 hour refresh intervals, not real-time)"
    }
  },
  "user_personas": {
    "allowed": [
      "Private Equity Investor",
      "Government Funders"
    ],
    "prohibited": [
      "private insurance",
      "public insurance"
    ]
  },
  "decision_support": {
    "disclaimer": "This is a decision support tool, NOT a decision making tool. Recommendations are for your review only and cannot be automated.",
    "prohibited_capabilities": [
      "automated decision-making",
      "automatic integration",
      "seamless integration",
      "direct system connections"
    ],
    "allowed_capabilities": [
      "export-based integration",
      "manual incorporation of results"
    ]
  },
  "financial_promises": {
    "prohibited": [
      "specific ROI guarantees",
      "specific percentage improvements",
      "guaranteed returns"
    ],
    "allowed": [
      "range of likely outcomes",
      "statistically significant and measurable improvements"
    ]
  },
  "integration": {
    "prohibited": [
      "seamless integration",
      "direct integration",
      "automatic integration",
      "API access to user databases",
      "connect to internal systems"
    ],
    "allowed": [
      "export results",
      "manual incorporation",
      "external data feeds"
    ]
  }
}
```

---

### **4. Response Sanitizer**

#### **File**: `src/multi_agent_system/utils/response_sanitizer.py`

**Purpose**: Sanitize agent responses before sending to users to ensure compliance.

**Suggested Implementation**:
```python
"""
Response Sanitizer

Sanitizes agent responses to ensure compliance with system constraints.
"""

from typing import Any, Dict
from .constraint_validator import SystemConstraintValidator, ConstraintViolation

class ResponseSanitizer:
    """Sanitizes agent responses for compliance."""
    
    def __init__(self):
        self.validator = SystemConstraintValidator()
    
    def sanitize_response(
        self, 
        response: str | Dict[str, Any],
        context: Dict[str, Any] | None = None
    ) -> Dict[str, Any]:
        """
        Sanitize agent response.
        
        Args:
            response: Agent response (string or dict)
            context: Additional context (user type, location, etc.)
        
        Returns:
            Dict with sanitized response and validation results
        """
        # Convert dict response to string for validation
        if isinstance(response, dict):
            response_text = self._extract_text_from_dict(response)
        else:
            response_text = response
        
        # Validate against constraints
        violations = self.validator.validate_response(
            response_text, 
            context or {}
        )
        
        # Apply fixes for violations
        sanitized_text = response_text
        fixes_applied = []
        
        for violation in violations:
            if violation.severity == "error":
                # Apply automatic fixes for errors
                sanitized_text = self._apply_fix(sanitized_text, violation)
                fixes_applied.append(violation.message)
        
        # Add decision support disclaimer if missing
        sanitized_text = self._ensure_decision_support_disclaimer(sanitized_text)
        
        # Reconstruct response dict if original was dict
        if isinstance(response, dict):
            sanitized_response = response.copy()
            sanitized_response["response_text"] = sanitized_text
        else:
            sanitized_response = {"response_text": sanitized_text}
        
        return {
            "sanitized_response": sanitized_response,
            "violations": [v.__dict__ for v in violations],
            "fixes_applied": fixes_applied,
            "compliance_status": "compliant" if not violations else "violations_found"
        }
    
    def _extract_text_from_dict(self, response_dict: Dict[str, Any]) -> str:
        """Extract text content from response dict."""
        # Extract from common fields
        text_fields = ["message", "response", "text", "content", "result"]
        for field in text_fields:
            if field in response_dict:
                return str(response_dict[field])
        # Fallback: convert entire dict to string
        return str(response_dict)
    
    def _apply_fix(self, text: str, violation: ConstraintViolation) -> str:
        """Apply suggested fix to text."""
        # TODO: Implement automatic text replacement based on violation type
        # This would use the terminology rules and constraint configs
        return text
    
    def _ensure_decision_support_disclaimer(self, text: str) -> str:
        """Ensure decision support disclaimer is present."""
        disclaimer = "This is a decision support tool, NOT a decision making tool. Recommendations are for your review only and cannot be automated."
        
        if "decision support" not in text.lower():
            # Add disclaimer at the beginning or end
            text = f"{text}\n\n{disclaimer}"
        
        return text
```

**Integration Point**: Add to `BaseAgent._execute_request()` before returning response to user.

---

### **5. Data Access Validator**

#### **File**: `src/multi_agent_system/utils/data_access_validator.py`

**Purpose**: Validate that agents only access allowed data sources and don't promise proprietary data access.

**Suggested Implementation**:
```python
"""
Data Access Validator

Validates data access requests against system constraints.
"""

from typing import Any, Dict, List
from dataclasses import dataclass

@dataclass
class DataAccessRequest:
    data_source: str
    data_type: str
    user_type: str
    location: str | None = None

class DataAccessValidator:
    """Validates data access requests."""
    
    def __init__(self):
        self.allowed_sources = self._load_allowed_sources()
        self.prohibited_sources = self._load_prohibited_sources()
        self.user_type_restrictions = self._load_user_type_restrictions()
    
    def validate_access_request(
        self, 
        request: DataAccessRequest
    ) -> Dict[str, Any]:
        """
        Validate data access request.
        
        Returns:
            Dict with validation result and allowed/prohibited status
        """
        errors = []
        warnings = []
        
        # Check if source is prohibited
        if request.data_source in self.prohibited_sources:
            errors.append(f"Data source '{request.data_source}' is prohibited")
        
        # Check user type restrictions
        user_restrictions = self.user_type_restrictions.get(request.user_type, {})
        if request.data_type in user_restrictions.get("cannot_access", []):
            errors.append(
                f"User type '{request.user_type}' cannot access '{request.data_type}'"
            )
        
        # Check if source is allowed
        is_allowed = request.data_source in self.allowed_sources
        
        return {
            "allowed": is_allowed and not errors,
            "errors": errors,
            "warnings": warnings,
            "message": "Access granted" if is_allowed and not errors else "Access denied"
        }
    
    def get_allowed_data_sources(self, user_type: str) -> List[str]:
        """Get list of allowed data sources for user type."""
        user_restrictions = self.user_type_restrictions.get(user_type, {})
        allowed = self.allowed_sources.copy()
        
        # Filter based on user type restrictions
        cannot_access = user_restrictions.get("cannot_access", [])
        allowed = [s for s in allowed if s not in cannot_access]
        
        return allowed
    
    def _load_allowed_sources(self) -> List[str]:
        """Load allowed data sources from config."""
        # TODO: Load from system_constraints.json
        return [
            "NOAA SWDI",
            "NOAA National Hurricane Center",
            "USGS",
            "EPA",
            "FEMA",
            "ERDDAP MCP Server",
            "CMR MCP Server",
            "Data.gov MCP Server",
            # ... other allowed sources
        ]
    
    def _load_prohibited_sources(self) -> List[str]:
        """Load prohibited data sources."""
        return [
            "user proprietary data",
            "internal business models",
            "confidential financial information",
            "individual performance metrics",
        ]
    
    def _load_user_type_restrictions(self) -> Dict[str, Dict[str, List[str]]]:
        """Load user type-specific restrictions."""
        # TODO: Load from system_constraints.json
        return {
            "Private Equity Investor": {
                "cannot_access": [
                    "QOF performance data",
                    "individual investment performance data",
                    "internal risk models"
                ],
                "can_access": [
                    "opportunity zone compliance data",
                    "hurricane risk assessments",
                    "manufacturing infrastructure resilience metrics"
                ]
            },
            "Government Funders": {
                "cannot_access": [
                    "local government coordination data"
                ],
                "can_access": [
                    "agricultural productivity data",
                    "extreme weather impact assessments",
                    "rural development program effectiveness metrics"
                ]
            }
        }
```

**Integration Point**: Add to data source access methods in `enhanced_data_sources.py` and data loading methods.

---

### **6. Geographic Data Filter**

#### **File**: `src/multi_agent_system/utils/geographic_data_filter.py`

**Purpose**: Filter and validate geographic data access based on location and bioregion.

**Suggested Implementation**:
```python
"""
Geographic Data Filter

Filters data sources and solutions based on geographic location and bioregion.
"""

from typing import Any, Dict, List, Optional
from dataclasses import dataclass

@dataclass
class GeographicContext:
    location: str
    country: str | None = None
    region: str | None = None
    state_province: str | None = None
    city: str | None = None
    bioregion: str | None = None
    location_type: str | None = None  # coastal, riverine, urban, rural, agricultural

class GeographicDataFilter:
    """Filters data sources and solutions by geography."""
    
    def __init__(self):
        self.risk_profiles = self._load_risk_profiles()
        self.data_source_mapping = self._load_data_source_mapping()
        self.solution_mapping = self._load_solution_mapping()
    
    def get_appropriate_data_sources(
        self, 
        context: GeographicContext
    ) -> List[str]:
        """
        Get appropriate data sources for geographic location.
        
        Returns:
            List of recommended data source names
        """
        sources = []
        
        # Identify primary risks for location
        primary_risks = self._identify_primary_risks(context)
        
        # Select data sources based on location type and risks
        if context.location_type == "coastal":
            sources.extend([
                "NOAA coastal data",
                "NOAA storm surge models",
                "NOAA sea level data",
                "ERDDAP MCP Server"
            ])
        elif context.location_type == "inland":
            sources.extend([
                "NOAA precipitation data",
                "NOAA temperature extremes",
                "NOAA drought indices"
            ])
        elif context.location_type == "agricultural":
            sources.extend([
                "USDA crop-specific weather data",
                "USDA soil moisture data",
                "USDA growing season data"
            ])
        elif context.location_type == "urban":
            sources.extend([
                "NOAA heat island data",
                "EPA stormwater management data",
                "FEMA infrastructure resilience metrics"
            ])
        
        # Add bioregion-specific sources if available
        if context.bioregion:
            bioregion_sources = self.risk_profiles.get(
                context.bioregion, {}
            ).get("data_sources", [])
            sources.extend(bioregion_sources)
        
        return list(set(sources))  # Remove duplicates
    
    def filter_nature_based_solutions(
        self,
        solutions: List[Dict[str, Any]],
        context: GeographicContext
    ) -> List[Dict[str, Any]]:
        """
        Filter nature-based solutions by location type.
        
        Args:
            solutions: List of solution dictionaries
            context: Geographic context
        
        Returns:
            Filtered list of solutions appropriate for location
        """
        filtered = []
        
        for solution in solutions:
            suitable_locations = solution.get("suitable_locations", [])
            
            # Check if solution is suitable for location type
            if context.location_type:
                if context.location_type in suitable_locations:
                    filtered.append(solution)
            else:
                # If no location type specified, include all
                filtered.append(solution)
        
        # Sort by relevance to location
        filtered = self._sort_by_relevance(filtered, context)
        
        return filtered
    
    def _identify_primary_risks(
        self, 
        context: GeographicContext
    ) -> List[str]:
        """Identify primary extreme weather risks for location."""
        risks = []
        
        if context.location_type == "coastal":
            risks.extend(["hurricanes", "storm_surge", "coastal_flooding"])
        elif context.location_type == "riverine":
            risks.extend(["flooding", "river_flooding"])
        elif context.location_type == "agricultural":
            risks.extend(["drought", "extreme_heat", "monsoon"])
        elif context.location_type == "urban":
            risks.extend(["extreme_heat", "stormwater", "urban_flooding"])
        
        # Add bioregion-specific risks
        if context.bioregion:
            bioregion_risks = self.risk_profiles.get(
                context.bioregion, {}
            ).get("primary_risks", [])
            risks.extend(bioregion_risks)
        
        return list(set(risks))
    
    def _sort_by_relevance(
        self,
        solutions: List[Dict[str, Any]],
        context: GeographicContext
    ) -> List[Dict[str, Any]]:
        """Sort solutions by relevance to geographic context."""
        # TODO: Implement relevance scoring
        return solutions
    
    def _load_risk_profiles(self) -> Dict[str, Dict[str, Any]]:
        """Load bioregional risk profiles."""
        # TODO: Load from regional_risk_profiles.json
        return {}
    
    def _load_data_source_mapping(self) -> Dict[str, List[str]]:
        """Load mapping of location types to data sources."""
        return {
            "coastal": ["NOAA coastal", "ERDDAP"],
            "riverine": ["NOAA precipitation", "USGS"],
            "agricultural": ["USDA", "NOAA agricultural"],
            "urban": ["NOAA heat island", "EPA stormwater"]
        }
    
    def _load_solution_mapping(self) -> Dict[str, List[str]]:
        """Load mapping of location types to solution types."""
        return {
            "coastal": ["living_shoreline", "wetland_restoration", "barrier_island"],
            "riverine": ["floodplain_restoration", "riparian_buffer"],
            "urban": ["green_infrastructure", "urban_forest", "stormwater_management"],
            "rural": ["agricultural_adaptation", "soil_conservation", "water_management"]
        }
```

**Integration Point**: Add to `nature_based_solutions_source.py` and data source selection logic.

---

### **7. User Persona Validator**

#### **File**: `src/multi_agent_system/utils/user_persona_validator.py`

**Purpose**: Validate that agents only work with allowed user personas and don't suggest features for prohibited personas.

**Suggested Implementation**:
```python
"""
User Persona Validator

Validates user persona requests and ensures compliance with allowed personas.
"""

from typing import Any, Dict, List

class UserPersonaValidator:
    """Validates user persona requests."""
    
    def __init__(self):
        self.allowed_personas = [
            "Private Equity Investor",
            "Government Funders"
        ]
        self.prohibited_personas = [
            "private insurance",
            "public insurance",
            "Loan Officer",
            "Chief Risk Officer",
            "Chief Sustainability Officer",
            "Data Science Officer",
            "Crop Insurance Officer",
            "Credit Officer"
        ]
        self.persona_capabilities = self._load_persona_capabilities()
    
    def validate_persona(self, persona: str) -> Dict[str, Any]:
        """
        Validate user persona.
        
        Returns:
            Dict with validation result
        """
        persona_lower = persona.lower()
        
        # Check if prohibited
        for prohibited in self.prohibited_personas:
            if prohibited.lower() in persona_lower:
                return {
                    "valid": False,
                    "error": f"User persona '{persona}' is prohibited",
                    "allowed_personas": self.allowed_personas
                }
        
        # Check if allowed
        is_allowed = any(
            allowed.lower() in persona_lower 
            for allowed in self.allowed_personas
        )
        
        if not is_allowed:
            return {
                "valid": False,
                "error": f"User persona '{persona}' is not in allowed list",
                "allowed_personas": self.allowed_personas
            }
        
        return {
            "valid": True,
            "persona": persona,
            "capabilities": self.persona_capabilities.get(persona, {})
        }
    
    def get_allowed_capabilities(self, persona: str) -> Dict[str, Any]:
        """Get allowed capabilities for persona."""
        return self.persona_capabilities.get(persona, {})
    
    def _load_persona_capabilities(self) -> Dict[str, Dict[str, Any]]:
        """Load persona-specific capabilities."""
        # TODO: Load from system_constraints.json
        return {
            "Private Equity Investor": {
                "can_access": [
                    "opportunity zone compliance data",
                    "hurricane risk assessments",
                    "manufacturing infrastructure resilience metrics"
                ],
                "cannot_access": [
                    "QOF performance data",
                    "individual investment performance data",
                    "internal risk models"
                ]
            },
            "Government Funders": {
                "can_access": [
                    "agricultural productivity data",
                    "extreme weather impact assessments",
                    "rural development program effectiveness metrics"
                ],
                "cannot_access": [
                    "local government coordination data"
                ]
            }
        }
```

**Integration Point**: Add to agent initialization and request validation.

---

### **8. Integration with BaseAgent**

#### **File**: `src/multi_agent_system/agents/base_agent.py`

**Suggested Modifications** (additions only, no deletions):

**1. Add constraint validation to `_execute_request()` method**:
```python
# In BaseAgent._execute_request() method, after generating response:

from ..utils.constraint_validator import SystemConstraintValidator
from ..utils.response_sanitizer import ResponseSanitizer

# After generating response but before returning:
constraint_validator = SystemConstraintValidator()
response_sanitizer = ResponseSanitizer()

# Validate and sanitize response
sanitized = response_sanitizer.sanitize_response(
    result,
    context={
        "user_type": self.security_context.user_id,  # or from request
        "agent_name": self.name
    }
)

# Log violations if any
if sanitized["violations"]:
    self.logger.warning(f"Constraint violations found: {sanitized['violations']}")

# Return sanitized response
return sanitized["sanitized_response"]
```

**2. Add data access validation to data loading methods**:
```python
# In any data loading method:

from ..utils.data_access_validator import DataAccessValidator, DataAccessRequest

data_validator = DataAccessValidator()
access_request = DataAccessRequest(
    data_source=source_name,
    data_type=data_type,
    user_type=user_type
)

validation = data_validator.validate_access_request(access_request)
if not validation["allowed"]:
    raise ValueError(f"Data access denied: {validation['errors']}")
```

---

### **9. Configuration File Updates**

#### **File**: `src/multi_agent_system/config.py`

**Suggested Additions**:
```python
# Add to existing config.py

# System Constraints Configuration
SYSTEM_CONSTRAINTS_CONFIG = {
    "terminology_rules_path": "config/terminology_rules.json",
    "system_constraints_path": "config/system_constraints.json",
    "enable_constraint_validation": True,
    "enable_response_sanitization": True,
    "strict_mode": True  # If True, block responses with violations
}

# Data Access Configuration
DATA_ACCESS_CONFIG = {
    "refresh_interval_min_hours": 1,
    "refresh_interval_max_hours": 6,
    "refresh_interval_message": "scheduled data updates (1-6 hour refresh intervals, not real-time)",
    "prohibited_data_sources": [
        "user proprietary data",
        "internal business models",
        "confidential financial information"
    ]
}

# Decision Support Configuration
DECISION_SUPPORT_CONFIG = {
    "required_disclaimer": "This is a decision support tool, NOT a decision making tool. Recommendations are for your review only and cannot be automated.",
    "prohibited_capabilities": [
        "automated decision-making",
        "automatic integration",
        "seamless integration"
    ]
}
```

---

### **10. Agent System Prompts Enhancement**

#### **File**: `src/multi_agent_system/agents/system_prompts.py` (NEW FILE)

**Purpose**: Centralized system prompts that include constraint reminders.

**Suggested Implementation**:
```python
"""
System Prompts for Agents

Centralized system prompts that include constraint reminders.
"""

SYSTEM_PROMPT_BASE = """
You are an agent in the Pythia extreme weather risk analysis system.

CRITICAL CONSTRAINTS - You MUST follow these rules:

1. TERMINOLOGY:
   - NEVER use "climate" - use "extreme weather" or "extreme weather-related risk"
   - NEVER reference carbon markets, carbon credits, or carbon trading
   - Use: "biodiversity benefits", "ecosystem services", "environmental benefits"

2. DECISION SUPPORT:
   - This is a DECISION SUPPORT tool, NOT a decision-making tool
   - ALWAYS include: "This is a decision support tool. Recommendations are for your review only and cannot be automated."
   - NEVER promise automated decision-making or automatic integration

3. DATA ACCESS:
   - NEVER promise real-time data - use "scheduled data updates (1-6 hour refresh intervals, not real-time)"
   - NEVER promise access to user's proprietary data
   - ONLY use external, publicly available data sources

4. FINANCIAL PROMISES:
   - NEVER promise specific ROI percentages or guarantees
   - Use: "range of likely outcomes" or "statistically significant and measurable improvements"

5. INTEGRATION:
   - NEVER promise seamless or direct integration
   - State: "Export-based integration only. Users can manually incorporate results."

6. USER PERSONAS:
   - ONLY work with: Private Equity Investor, Government Funders
   - NEVER suggest features for private/public insurance personas

Before sending any response to a user, validate it against these constraints.
"""

def get_agent_system_prompt(agent_name: str, additional_context: str = "") -> str:
    """Get system prompt for specific agent."""
    return f"{SYSTEM_PROMPT_BASE}\n\n{additional_context}"
```

**Integration Point**: Use in agent initialization to set LLM system prompts.

---

## Implementation Priority

### **Phase 1: Critical (Immediate)**
1. ✅ **SystemConstraintValidator** - Core validation logic
2. ✅ **ResponseSanitizer** - Automatic response cleaning
3. ✅ **terminology_rules.json** - Terminology configuration
4. ✅ **system_constraints.json** - Constraint configuration

### **Phase 2: High Priority**
5. ✅ **DataAccessValidator** - Data source validation
6. ✅ **UserPersonaValidator** - Persona validation
7. ✅ **BaseAgent integration** - Add validation to agent responses

### **Phase 3: Medium Priority**
8. ✅ **GeographicDataFilter** - Location-based filtering
9. ✅ **system_prompts.py** - Centralized prompts
10. ✅ **config.py updates** - Configuration additions

## Testing Strategy

### **Test Cases**
1. **Terminology Filtering**: Test that "climate" is caught and replaced
2. **Decision Support**: Test that disclaimer is added when missing
3. **Data Access**: Test that proprietary data promises are blocked
4. **Financial Promises**: Test that specific percentages are caught
5. **Real-Time Promises**: Test that real-time data promises are blocked
6. **User Persona**: Test that prohibited personas are rejected
7. **Geographic Filtering**: Test that solutions are filtered by location type

## Benefits

1. **Automatic Enforcement**: Rules are enforced programmatically, not just documented
2. **Consistency**: All agents use the same validation logic
3. **Early Detection**: Violations caught before responses reach users
4. **Maintainability**: Rules centralized in config files, easy to update
5. **Audit Trail**: All violations logged for review
6. **User Safety**: Prevents accidental constraint violations

## Related Files

- `docs/_RULES_Pythia_System_Rules/00_LLM_General_Rules_for_Pythia.md` - Source of rules
- `docs/00_cursor_rules.md` - Cursor-specific rules
- `src/multi_agent_system/agents/base_agent.py` - Integration point
- `src/agentic_data_management/governance.py` - Existing governance framework
- `src/multi_agent_system/data/nature_based_solutions_source.py` - Data source that needs filtering

## Notes

- **No changes have been made** - these are suggestions only
- **Config files** should be JSON for easy editing
- **Validation** should be non-blocking (warnings) unless in strict mode
- **Logging** should capture all violations for audit purposes
- **Performance** should be considered - validation should be fast

