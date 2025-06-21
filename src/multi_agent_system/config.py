"""
Configuration settings for the multi-agent system.
"""

import os
from typing import Dict, Any, List

# A2A Protocol Configuration
A2A_CONFIG = {
    "message_timeout": 300,  # 5 minutes
    "max_message_size": 10 * 1024 * 1024,  # 10MB
    "max_retries": 3,
    "heartbeat_interval": 30,  # 30 seconds
    "discovery_timeout": 60,  # 60 seconds
    "enable_routing": True,
    "enable_multipart": True,
    "content_handlers": {
        "text": True,
        "data": True,
        "file": True,
        "image": True,
        "audio": True,
        "video": True,
        "binary": True
    }
}

# Agent Configuration
AGENT_CONFIG = {
    "max_concurrent_tasks": 5,
    "task_timeout": 300,
    "enable_heartbeat": True,
    "enable_discovery": True,
    "log_level": "INFO"
}

# ... existing code ... 