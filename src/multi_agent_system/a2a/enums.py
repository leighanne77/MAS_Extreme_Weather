"""
A2A Protocol Enums - Re-export Layer

All A2A enums are now defined in src/enums.py (canonical location).
This module re-exports them for backward compatibility with existing imports.

Usage:
    # Preferred (canonical):
    from enums import MessageType, Priority, StatusCode, PartType
    
    # Still supported (backward compatible):
    from multi_agent_system.a2a.enums import MessageType, Priority, StatusCode, PartType
"""

# Re-export all A2A enums from canonical location
from enums import (
    MessageType,
    Priority,
    StatusCode,
    PartType,
    STATUS_DESCRIPTIONS,
    get_status_description,
)

# Explicit __all__ for clean re-exports
__all__ = [
    "MessageType",
    "Priority",
    "StatusCode",
    "PartType",
    "STATUS_DESCRIPTIONS",
    "get_status_description",
]
