"""
Aggregation Agent for managing data aggregation and summarization.
Handles data aggregation rules, summary generation, and aggregation metrics.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
import asyncio
from .base_agent import BaseAgent

class AggregationAgent(BaseAgent):
    """Agent responsible for managing data aggregation and summarization."""
    
    def __init__(self):
        super().__init__(
            name="aggregation_agent",
            description="Manages data aggregation and summarization",
            capabilities={
                "streaming": True,
                "pushNotifications": True,
                "stateTransitionHistory": True
            }
        )
        self.aggregation_rules = {}
        self.summary_templates = {}
        self.aggregation_metrics = {}
        
    async def define_aggregation_rule(self, rule_id: str, rule: Dict[str, Any]) -> Dict[str, Any]:
        """Define a new aggregation rule."""
        try:
            self.aggregation_rules[rule_id] = {
                "rule": rule,
                "defined_at": datetime.utcnow().isoformat()
            }
            
            return {
                "status": "success",
                "message": f"Aggregation rule defined: {rule_id}"
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }
    
    async def define_summary_template(self, template_id: str, template: Dict[str, Any]) -> Dict[str, Any]:
        """Define a new summary template."""
        try:
            self.summary_templates[template_id] = {
                "template": template,
                "defined_at": datetime.utcnow().isoformat()
            }
            
            return {
                "status": "success",
                "message": f"Summary template defined: {template_id}"
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }
    
    async def aggregate_data(self, data_ids: List[str], rule_id: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Aggregate data using a rule."""
        try:
            if rule_id not in self.aggregation_rules:
                return {
                    "status": "error",
                    "error": f"Aggregation rule {rule_id} not found"
                }
            
            rule = self.aggregation_rules[rule_id]
            aggregation_result = await self._execute_aggregation(data_ids, rule, context)
            
            return {
                "status": "success",
                "aggregation_result": aggregation_result
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }
    
    async def generate_summary(self, data_id: str, template_id: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a summary using a template."""
        try:
            if template_id not in self.summary_templates:
                return {
                    "status": "error",
                    "error": f"Summary template {template_id} not found"
                }
            
            template = self.summary_templates[template_id]
            summary_result = await self._execute_summary_generation(data_id, template, context)
            
            return {
                "status": "success",
                "summary_result": summary_result
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }
    
    async def track_aggregation_metric(self, metric_id: str, metric_data: Dict[str, Any]) -> Dict[str, Any]:
        """Track an aggregation metric."""
        try:
            self.aggregation_metrics[metric_id] = {
                "data": metric_data,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            return {
                "status": "success",
                "message": f"Aggregation metric tracked: {metric_id}"
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }
    
    async def get_aggregation_rule(self, rule_id: str) -> Dict[str, Any]:
        """Get aggregation rule."""
        try:
            if rule_id not in self.aggregation_rules:
                return {
                    "status": "error",
                    "error": f"No aggregation rule found for {rule_id}"
                }
            
            return {
                "status": "success",
                "rule": self.aggregation_rules[rule_id]
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }
    
    async def get_summary_template(self, template_id: str) -> Dict[str, Any]:
        """Get summary template."""
        try:
            if template_id not in self.summary_templates:
                return {
                    "status": "error",
                    "error": f"No summary template found for {template_id}"
                }
            
            return {
                "status": "success",
                "template": self.summary_templates[template_id]
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }
    
    async def get_aggregation_metrics(self, metric_id: Optional[str] = None) -> Dict[str, Any]:
        """Get aggregation metrics with optional ID filter."""
        try:
            metrics = self.aggregation_metrics
            if metric_id:
                metrics = {
                    mid: metric for mid, metric in self.aggregation_metrics.items()
                    if mid == metric_id
                }
            
            return {
                "status": "success",
                "metrics": metrics
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }
    
    async def _execute_aggregation(self, data_ids: List[str], rule: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute aggregation using a rule."""
        # Implementation would depend on specific aggregation requirements
        return {
            "aggregated": True,
            "details": {
                "rule_id": rule.get("id"),
                "data_ids": data_ids,
                "aggregation_time": datetime.utcnow().isoformat(),
                "context": context
            }
        }
    
    async def _execute_summary_generation(self, data_id: str, template: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute summary generation using a template."""
        # Implementation would depend on specific summary requirements
        return {
            "summarized": True,
            "details": {
                "template_id": template.get("id"),
                "data_id": data_id,
                "summary_time": datetime.utcnow().isoformat(),
                "context": context
            }
        } 