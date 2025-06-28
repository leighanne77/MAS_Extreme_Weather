"""
Agentic Data Management System

A robust data management system designed to work with multi-agent systems,
providing intelligent data handling, validation, and transformation capabilities.
"""

from .data_manager import DataManager
from .governance import DataGovernance
from .quality import QualityMetrics
from .schemas import SchemaManager
from .transformers import DataTransformer
from .validators import DataValidator

__version__ = "0.1.0"
__all__ = [
    "DataManager",
    "DataValidator",
    "DataTransformer",
    "SchemaManager",
    "QualityMetrics",
    "DataGovernance",
]
