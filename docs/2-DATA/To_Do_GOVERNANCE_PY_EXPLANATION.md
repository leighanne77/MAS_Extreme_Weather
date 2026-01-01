# How `governance.py` Manages Data for Agents

**Date Created**: December 14, 2025  
**File**: `src/agentic_data_management/governance.py`

## Overview

The `governance.py` module provides a **data governance framework** that ensures all data used by agents complies with defined policies, rules, and regulations. It acts as a **quality gate** and **compliance checker** for data before agents can use it.

## Architecture

### **Core Components**

```
DataGovernance
├── Policy Management
│   ├── create_policy()      # Define new governance policies
│   ├── get_policy()         # Retrieve existing policies
│   ├── update_policy()      # Modify policies
│   ├── list_policies()      # List all policies
│   └── get_active_policies() # Get only active policies
│
├── Compliance Checking
│   ├── check_compliance()   # Main compliance validation
│   ├── _check_rule()        # Individual rule evaluation
│   └── _generate_summary()  # Compliance report generation
│
└── Data Models
    ├── Policy               # Policy definition structure
    ├── ComplianceCheck      # Individual check result
    └── ComplianceReport     # Complete compliance report
```

## How It Works

### **1. Policy Definition**

Policies are JSON files stored in a `policies/` directory. Each policy contains:

```python
Policy(
    name="data_quality_policy",
    description="Ensures data quality standards",
    rules=[
        {
            "name": "required_fields_check",
            "type": "validation",
            "fields": ["id", "timestamp", "source"]
        },
        {
            "name": "data_freshness_check",
            "type": "temporal",
            "max_age_hours": 6
        }
    ],
    created_by="system",
    is_active=True
)
```

**Example Policy Creation:**
```python
governance = DataGovernance(policies_dir="policies")

await governance.create_policy(
    name="nature_based_solutions_policy",
    description="Governance policy for nature-based solutions data",
    rules=[
        {
            "name": "required_fields",
            "type": "validation",
            "required": ["id", "name", "description", "risk_types"]
        },
        {
            "name": "risk_type_validation",
            "type": "enum_check",
            "field": "risk_types",
            "allowed_values": ["flooding", "extreme_heat", "drought", "storm_surge"]
        }
    ],
    created_by="data_team"
)
```

### **2. Data Compliance Checking**

When agents need to use data, the governance system checks it against all active policies:

```python
# Agent receives data from a source
data = {
    "id": "wetland_restoration",
    "name": "Wetland Restoration",
    "description": "Restoring wetlands...",
    "risk_types": ["flooding", "drought"]
}

# Check compliance before using
compliance_report = await governance.check_compliance(
    data=data,
    data_source="nature_based_solutions.json",
    policies=["nature_based_solutions_policy"]  # Optional: specific policies
)

# Result structure:
# ComplianceReport(
#     data_source="nature_based_solutions.json",
#     checks=[
#         ComplianceCheck(
#             policy_name="nature_based_solutions_policy",
#             check_name="required_fields",
#             status="pass",
#             details={"message": "All required fields present"}
#         ),
#         ComplianceCheck(
#             policy_name="nature_based_solutions_policy",
#             check_name="risk_type_validation",
#             status="pass",
#             details={"message": "Risk types are valid"}
#         )
#     ],
#     summary={
#         "total_checks": 2,
#         "passed_checks": 2,
#         "compliance_rate": 1.0
#     }
# )
```

### **3. Integration with DataManager**

The `DataGovernance` class is integrated into `DataManager`, which orchestrates all data operations:

```python
# From data_manager.py
class DataManager:
    def __init__(self):
        # ... other components ...
        self.governance = DataGovernance()  # Governance instance
        
    async def process_data(self, data_source, validation_rules, ...):
        # 1. Load data
        data = await self._load_data(data_source)
        
        # 2. Validate schema
        validation_result = await self.validator.validate(data, schema)
        
        # 3. Check governance compliance (NEW)
        compliance_report = await self.governance.check_compliance(
            data=data,
            data_source=data_source
        )
        
        if compliance_report.summary["compliance_rate"] < 1.0:
            # Handle non-compliance
            raise ComplianceError("Data does not meet governance policies")
        
        # 4. Transform data
        transformed_data = await self.transformer.transform(data, ...)
        
        # 5. Calculate quality metrics
        metrics = await self.quality_metrics.calculate(transformed_data)
        
        return {
            "data": transformed_data,
            "compliance": compliance_report,
            "metrics": metrics
        }
```

## How Agents Use It

### **Agent Workflow with Governance**

1. **Agent Requests Data**:
   ```python
   # Agent needs nature-based solutions data
   agent_request = {
       "data_type": "nature_based_solutions",
       "location": "Mobile Bay, Alabama",
       "risk_types": ["flooding", "storm_surge"]
   }
   ```

2. **DataManager Processes Request**:
   ```python
   # DataManager loads data and checks governance
   result = await data_manager.process_data(
       data_source="nature_based_solutions.json",
       validation_rules="nbs_schema.json",
       transformation_pipeline="standardize_nbs"
   )
   ```

3. **Governance Check Happens Automatically**:
   - All active policies are checked
   - Each rule in each policy is evaluated
   - Compliance report is generated

4. **Agent Receives Validated Data**:
   ```python
   # Agent receives:
   {
       "status": "success",
       "data": [...],  # Validated and compliant data
       "compliance": {
           "compliance_rate": 1.0,
           "checks_passed": 5,
           "total_checks": 5
       },
       "quality_metrics": {...}
   }
   ```

## Current Implementation Status

### **✅ Implemented**
- Policy creation and management (CRUD operations)
- Policy storage (JSON files in `policies/` directory)
- Compliance checking framework
- Compliance report generation
- Integration with `DataManager`
- Active/inactive policy filtering

### **⚠️ Placeholder/Needs Implementation**
- **`_check_rule()` method** (line 170-191): Currently returns a placeholder "pass" status
  - **Needs**: Actual rule evaluation logic based on rule types
  - **Should support**:
    - Field validation rules
    - Enum/whitelist checks
    - Temporal checks (data freshness)
    - Range/constraint checks
    - Custom validation functions

## Rule Types That Should Be Supported

### **1. Field Validation Rules**
```python
{
    "name": "required_fields",
    "type": "required_fields",
    "fields": ["id", "name", "description"]
}
```

### **2. Enum/Whitelist Rules**
```python
{
    "name": "risk_type_validation",
    "type": "enum",
    "field": "risk_types",
    "allowed_values": ["flooding", "extreme_heat", "drought"]
}
```

### **3. Temporal Rules**
```python
{
    "name": "data_freshness",
    "type": "temporal",
    "field": "last_updated",
    "max_age_hours": 6
}
```

### **4. Range/Constraint Rules**
```python
{
    "name": "cost_range_validation",
    "type": "range",
    "field": "cost_range.min",
    "min": 0,
    "max": 1000000
}
```

### **5. Custom Validation Rules**
```python
{
    "name": "custom_validation",
    "type": "custom",
    "validator_function": "validate_nbs_structure",
    "parameters": {...}
}
```

## Integration Points

### **1. With DataManager**
- **Location**: `src/agentic_data_management/data_manager.py:63`
- **Usage**: Automatically checks compliance during data processing

### **2. With ComplianceAgent**
- **Location**: `src/agentic_data_management/agents/compliance_agent.py`
- **Relationship**: `ComplianceAgent` can use `DataGovernance` to enforce policies
- **Note**: Currently separate implementations; could be unified

### **3. With ValidationAgent**
- **Location**: `src/multi_agent_system/agents/validation_agent.py`
- **Relationship**: Validation happens before governance checks
- **Flow**: Schema validation → Governance compliance → Agent use

## Example Usage for Nature-Based Solutions

### **Creating a Policy for NBS Data**
```python
governance = DataGovernance(policies_dir="policies/nbs")

await governance.create_policy(
    name="nbs_data_quality",
    description="Quality standards for nature-based solutions data",
    rules=[
        {
            "name": "required_structure",
            "type": "required_fields",
            "fields": ["id", "name", "description", "risk_types", "suitable_locations"]
        },
        {
            "name": "risk_type_whitelist",
            "type": "enum",
            "field": "risk_types",
            "allowed_values": [
                "flooding", "drought", "extreme_heat", "storm_surge",
                "coastal_erosion", "water_quality", "air_quality"
            ]
        },
        {
            "name": "location_type_validation",
            "type": "enum",
            "field": "suitable_locations",
            "allowed_values": [
                "coastal", "riverine", "urban", "rural", "suburban"
            ]
        },
        {
            "name": "case_studies_structure",
            "type": "optional_structure",
            "field": "case_studies",
            "if_present": {
                "required_fields": ["name", "location", "description"]
            }
        }
    ],
    created_by="data_governance_team"
)
```

### **Checking NBS Data Compliance**
```python
# When agent loads NBS data
nbs_data = await load_nature_based_solutions()

# Check compliance
report = await governance.check_compliance(
    data=nbs_data,
    data_source="nature_based_solutions.json",
    policies=["nbs_data_quality"]
)

# Agent decision based on compliance
if report.summary["compliance_rate"] == 1.0:
    # All checks passed - safe to use
    agent.use_data(nbs_data)
else:
    # Some checks failed - log and handle
    agent.log_compliance_issues(report)
    agent.request_data_correction(report)
```

## Benefits for Agents

1. **Data Quality Assurance**: Ensures agents only receive validated, compliant data
2. **Policy Enforcement**: Centralized policy management and enforcement
3. **Compliance Tracking**: Full audit trail of compliance checks
4. **Error Prevention**: Catches data issues before agents process them
5. **Consistency**: All agents use the same governance standards

## Next Steps for Implementation

1. **Implement `_check_rule()` Logic**:
   - Add rule type handlers (required_fields, enum, temporal, range, custom)
   - Add rule evaluation engine
   - Add detailed error reporting

2. **Add Policy Templates**:
   - Pre-defined policies for common data types
   - Policy templates for nature-based solutions, weather data, economic data, etc.

3. **Enhance Compliance Reporting**:
   - Add severity levels (error, warning, info)
   - Add remediation suggestions
   - Add compliance history tracking

4. **Integration with Agent Tools**:
   - Add governance checks to agent data access tools
   - Add compliance status to agent responses
   - Add governance dashboard/reporting

## Related Files

- `src/agentic_data_management/data_manager.py` - Main data processing orchestrator
- `src/agentic_data_management/agents/compliance_agent.py` - Compliance-specific agent
- `src/agentic_data_management/validators.py` - Data validation (schema-based)
- `src/agentic_data_management/quality.py` - Data quality metrics

## Summary

The `governance.py` module provides a **policy-driven data governance framework** that:

- ✅ **Defines policies** as JSON files with rules
- ✅ **Checks data compliance** before agents use it
- ✅ **Generates compliance reports** with detailed results
- ✅ **Integrates automatically** with DataManager
- ⚠️ **Needs implementation** of actual rule checking logic

This ensures that all data used by agents meets quality, structure, and compliance standards defined in governance policies.

