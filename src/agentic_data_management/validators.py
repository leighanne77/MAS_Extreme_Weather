"""
Data Validator Module

This module provides functionality for validating data against schemas
and business rules.
"""

from typing import Any, Dict, List, Optional, Union
from datetime import datetime
import json
from pathlib import Path
import aiofiles

from pydantic import BaseModel, Field
from jsonschema import validate, ValidationError

class ValidationResult(BaseModel):
    """Represents the result of a data validation operation."""
    valid: bool
    errors: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)

class DataValidator:
    """Class for validating data against schemas and rules."""
    
    def __init__(self, rules_dir: str = "rules"):
        """Initialize the DataValidator.
        
        Args:
            rules_dir: Directory containing validation rules
        """
        self.rules_dir = Path(rules_dir)
        self.rules_dir.mkdir(parents=True, exist_ok=True)
    
    async def validate(
        self,
        data: Dict[str, Any],
        schema: Dict[str, Any],
        rules: Optional[List[str]] = None
    ) -> ValidationResult:
        """Validate data against schema and rules.
        
        Args:
            data: Data to validate
            schema: JSON Schema to validate against
            rules: Optional list of additional rule names to apply
            
        Returns:
            ValidationResult containing validation results
        """
        result = ValidationResult(valid=True)
        
        try:
            # Validate against schema
            validate(instance=data, schema=schema)
            
            # Apply additional rules if specified
            if rules:
                for rule_name in rules:
                    rule_result = await self._apply_rule(data, rule_name)
                    if not rule_result["valid"]:
                        result.valid = False
                        result.errors.extend(rule_result["errors"])
                    result.warnings.extend(rule_result["warnings"])
            
            return result
            
        except ValidationError as e:
            result.valid = False
            result.errors.append(str(e))
            return result
        except Exception as e:
            result.valid = False
            result.errors.append(f"Validation error: {str(e)}")
            return result
    
    async def _apply_rule(
        self,
        data: Dict[str, Any],
        rule_name: str
    ) -> Dict[str, Any]:
        """Apply a specific validation rule.
        
        Args:
            data: Data to validate
            rule_name: Name of the rule to apply
            
        Returns:
            Dict containing rule validation results
        """
        rule_path = self.rules_dir / f"{rule_name}.json"
        if not rule_path.exists():
            raise FileNotFoundError(f"Rule not found: {rule_name}")
        
        async with aiofiles.open(rule_path, 'r') as f:
            rule = json.loads(await f.read())
        
        result = {"valid": True, "errors": [], "warnings": []}
        
        # Apply rule logic here
        # This is a placeholder for actual rule implementation
        
        return result
    
    async def add_rule(
        self,
        rule_name: str,
        rule_definition: Dict[str, Any]
    ) -> None:
        """Add a new validation rule.
        
        Args:
            rule_name: Name of the rule
            rule_definition: Rule definition
        """
        rule_path = self.rules_dir / f"{rule_name}.json"
        async with aiofiles.open(rule_path, 'w') as f:
            await f.write(json.dumps(rule_definition, indent=2))
    
    async def get_rule(self, rule_name: str) -> Dict[str, Any]:
        """Get a validation rule definition.
        
        Args:
            rule_name: Name of the rule
            
        Returns:
            Rule definition
        """
        rule_path = self.rules_dir / f"{rule_name}.json"
        if not rule_path.exists():
            raise FileNotFoundError(f"Rule not found: {rule_name}")
        
        async with aiofiles.open(rule_path, 'r') as f:
            return json.loads(await f.read())
    
    async def list_rules(self) -> List[str]:
        """List all available validation rules.
        
        Returns:
            List of rule names
        """
        return [f.stem for f in self.rules_dir.glob("*.json")] 