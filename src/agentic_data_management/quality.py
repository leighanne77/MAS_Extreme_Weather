"""
Quality Metrics Module

This module provides functionality for measuring and tracking data quality metrics.
"""

from typing import Any, Dict, List, Optional, Union
from datetime import datetime
import json
from pathlib import Path
import aiofiles
import pandas as pd
import numpy as np
from pydantic import BaseModel, Field

class QualityMetric(BaseModel):
    """Represents a single data quality metric."""
    name: str
    value: float
    description: str
    timestamp: datetime = Field(default_factory=datetime.now)
    metadata: Dict[str, Any] = Field(default_factory=dict)

class QualityReport(BaseModel):
    """Represents a complete data quality report."""
    data_source: str
    metrics: List[QualityMetric]
    created_at: datetime = Field(default_factory=datetime.now)
    summary: Dict[str, Any] = Field(default_factory=dict)

class QualityMetrics:
    """Class for measuring and tracking data quality metrics."""
    
    def __init__(self, reports_dir: str = "quality_reports"):
        """Initialize the QualityMetrics.
        
        Args:
            reports_dir: Directory containing quality reports
        """
        self.reports_dir = Path(reports_dir)
        self.reports_dir.mkdir(parents=True, exist_ok=True)
    
    async def calculate_metrics(
        self,
        data: Union[Dict[str, Any], pd.DataFrame],
        data_source: str,
        metrics: Optional[List[str]] = None
    ) -> QualityReport:
        """Calculate quality metrics for a dataset.
        
        Args:
            data: Data to analyze
            data_source: Source identifier for the data
            metrics: Optional list of specific metrics to calculate
            
        Returns:
            QualityReport containing calculated metrics
        """
        if metrics is None:
            metrics = self._get_default_metrics()
        
        calculated_metrics = []
        for metric_name in metrics:
            metric_value = await self._calculate_metric(data, metric_name)
            metric = QualityMetric(
                name=metric_name,
                value=metric_value,
                description=self._get_metric_description(metric_name)
            )
            calculated_metrics.append(metric)
        
        report = QualityReport(
            data_source=data_source,
            metrics=calculated_metrics,
            summary=self._generate_summary(calculated_metrics)
        )
        
        # Save report
        report_path = self.reports_dir / f"{data_source}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        async with aiofiles.open(report_path, 'w') as f:
            await f.write(report.json(indent=2))
        
        return report
    
    async def _calculate_metric(
        self,
        data: Union[Dict[str, Any], pd.DataFrame],
        metric_name: str
    ) -> float:
        """Calculate a specific quality metric.
        
        Args:
            data: Data to analyze
            metric_name: Name of the metric to calculate
            
        Returns:
            Calculated metric value
        """
        if isinstance(data, pd.DataFrame):
            if metric_name == "completeness":
                return 1 - data.isnull().sum().sum() / (data.shape[0] * data.shape[1])
            elif metric_name == "uniqueness":
                return len(data.drop_duplicates()) / len(data)
            elif metric_name == "consistency":
                # Placeholder for consistency calculation
                return 1.0
            else:
                raise ValueError(f"Unknown metric: {metric_name}")
        else:
            # Handle dictionary data
            if metric_name == "completeness":
                return 1.0  # Placeholder
            elif metric_name == "uniqueness":
                return 1.0  # Placeholder
            elif metric_name == "consistency":
                return 1.0  # Placeholder
            else:
                raise ValueError(f"Unknown metric: {metric_name}")
    
    def _get_default_metrics(self) -> List[str]:
        """Get the list of default metrics to calculate.
        
        Returns:
            List of metric names
        """
        return ["completeness", "uniqueness", "consistency"]
    
    def _get_metric_description(self, metric_name: str) -> str:
        """Get the description for a metric.
        
        Args:
            metric_name: Name of the metric
            
        Returns:
            Metric description
        """
        descriptions = {
            "completeness": "Measures the proportion of non-null values in the dataset",
            "uniqueness": "Measures the proportion of unique values in the dataset",
            "consistency": "Measures the consistency of data formats and values"
        }
        return descriptions.get(metric_name, "No description available")
    
    def _generate_summary(self, metrics: List[QualityMetric]) -> Dict[str, Any]:
        """Generate a summary of quality metrics.
        
        Args:
            metrics: List of calculated metrics
            
        Returns:
            Summary dictionary
        """
        return {
            "average_quality": sum(m.value for m in metrics) / len(metrics),
            "metric_count": len(metrics),
            "timestamp": datetime.now().isoformat()
        }
    
    async def get_report(self, data_source: str, timestamp: Optional[str] = None) -> QualityReport:
        """Get a quality report for a data source.
        
        Args:
            data_source: Source identifier
            timestamp: Optional specific timestamp to get
            
        Returns:
            QualityReport
        """
        if timestamp:
            report_path = self.reports_dir / f"{data_source}_{timestamp}.json"
        else:
            # Get most recent report
            reports = list(self.reports_dir.glob(f"{data_source}_*.json"))
            if not reports:
                raise FileNotFoundError(f"No reports found for {data_source}")
            report_path = max(reports, key=lambda p: p.stat().st_mtime)
        
        async with aiofiles.open(report_path, 'r') as f:
            report_data = json.loads(await f.read())
            return QualityReport(**report_data)
    
    async def list_reports(self, data_source: Optional[str] = None) -> List[str]:
        """List available quality reports.
        
        Args:
            data_source: Optional source identifier to filter by
            
        Returns:
            List of report filenames
        """
        if data_source:
            pattern = f"{data_source}_*.json"
        else:
            pattern = "*.json"
        
        return [f.name for f in self.reports_dir.glob(pattern)] 