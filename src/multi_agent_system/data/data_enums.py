"""
Data Enums - Data-specific enums for the data module.

This module defines enums specific to data sources and re-exports
common enums from the canonical location (src/enums.py).

Canonical enums (re-exported from src/enums.py):
- DataLoadStatus, DataProvenance (as ProvenanceType), DataErrorType (as ErrorType)
- DataFormat, DataAccessLevel (as AccessLevel), ArtifactType

Data-specific enums (defined here):
- DataSourceType - includes JSON, API, ENHANCED for source format types
"""
from enum import Enum

# Re-export canonical enums for backward compatibility
from enums import (
    DataLoadStatus,
    DataProvenance as ProvenanceType,  # Alias for backward compat
    DataErrorType as ErrorType,  # Alias for backward compat
    DataUpdateFrequency as UpdateFrequency,  # Alias for backward compat
    DataFormat,
    DataAccessLevel as AccessLevel,  # Alias for backward compat
    ArtifactType,
)


class DataSourceType(Enum):
    """
    Data source types for the DataSourceManager.
    
    This enum includes both source format types (JSON, API, ENHANCED)
    and domain types (AGRICULTURE, WATER, etc.) for flexibility.
    """
    # Source format types (primary use)
    JSON = "json"
    API = "api"
    ENHANCED = "enhanced"
    # Domain types (legacy, kept for backward compatibility)
    AGRICULTURE = "agriculture"
    WATER = "water"
    ECONOMIC = "economic"
    ENVIRONMENTAL = "environmental"
    OTHER = "other"


# Explicit exports
__all__ = [
    # Re-exported from enums.py
    "DataLoadStatus",
    "ProvenanceType",
    "ErrorType",
    "UpdateFrequency",
    "DataFormat",
    "AccessLevel",
    "ArtifactType",
    # Defined here
    "DataSourceType",
]
