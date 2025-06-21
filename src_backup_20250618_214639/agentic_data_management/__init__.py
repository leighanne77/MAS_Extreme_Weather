"""
Agentic Data Management System

A robust data management system designed to work with multi-agent systems,
providing intelligent data handling, validation, and transformation capabilities.
"""

from .data_manager import DataManager
from .validators import DataValidator
from .transformers import DataTransformer
from .schemas import SchemaManager
from .quality import QualityMetrics
from .governance import DataGovernance

__version__ = "0.1.0"
__all__ = [
    "DataManager",
    "DataValidator",
    "DataTransformer",
    "SchemaManager",
    "QualityMetrics",
    "DataGovernance",
] 