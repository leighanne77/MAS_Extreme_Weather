"""
Configuration Module

This module provides configuration management for the agent system.
"""

import json
import os
from typing import Any

from dotenv import load_dotenv
from pydantic import BaseModel, Field


class GoogleCloudConfig(BaseModel):
    """Google Cloud configuration settings."""
    project_id: str
    location: str = "us-central1"
    credentials_path: str | None = None
    dataset_id: str = "agentic_data"
    bucket_name: str = "agentic-data"
    pubsub_topic: str = "agentic-events"

class AgentConfig(BaseModel):
    """Agent configuration settings."""
    quality_agent: dict[str, Any] = Field(default_factory=dict)
    catalog_agent: dict[str, Any] = Field(default_factory=dict)
    lineage_agent: dict[str, Any] = Field(default_factory=dict)

class SystemConfig(BaseModel):
    """System-wide configuration settings."""
    google_cloud: GoogleCloudConfig
    agents: AgentConfig
    workflow_dir: str = "workflows"
    catalog_dir: str = "catalog"
    lineage_dir: str = "lineage"
    quality_dir: str = "quality_reports"
    log_level: str = "INFO"

class ConfigManager:
    """Manages system configuration."""

    def __init__(
        self,
        config_path: str | None = None,
        env_path: str | None = None
    ):
        """Initialize configuration manager.

        Args:
            config_path: Path to configuration file
            env_path: Path to environment file
        """
        # Load environment variables
        if env_path:
            load_dotenv(env_path)
        else:
            load_dotenv()

        # Load configuration
        self.config_path = config_path or "config.json"
        self.config = self._load_config()

    def _load_config(self) -> SystemConfig:
        """Load configuration from file or environment.

        Returns:
            System configuration
        """
        # Try to load from file
        if os.path.exists(self.config_path):
            with open(self.config_path) as f:
                config_data = json.load(f)
        else:
            # Create default configuration
            config_data = {
                "google_cloud": {
                    "project_id": os.getenv("GOOGLE_CLOUD_PROJECT", ""),
                    "location": os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1"),
                    "credentials_path": os.getenv("GOOGLE_APPLICATION_CREDENTIALS"),
                    "dataset_id": os.getenv("GOOGLE_CLOUD_DATASET", "agentic_data"),
                    "bucket_name": os.getenv("GOOGLE_CLOUD_BUCKET", "agentic-data"),
                    "pubsub_topic": os.getenv("GOOGLE_CLOUD_TOPIC", "agentic-events")
                },
                "agents": {
                    "quality_agent": {},
                    "catalog_agent": {},
                    "lineage_agent": {}
                },
                "workflow_dir": os.getenv("WORKFLOW_DIR", "workflows"),
                "catalog_dir": os.getenv("CATALOG_DIR", "catalog"),
                "lineage_dir": os.getenv("LINEAGE_DIR", "lineage"),
                "quality_dir": os.getenv("QUALITY_DIR", "quality_reports"),
                "log_level": os.getenv("LOG_LEVEL", "INFO")
            }

        return SystemConfig(**config_data)

    def save_config(self) -> None:
        """Save current configuration to file."""
        with open(self.config_path, 'w') as f:
            json.dump(self.config.dict(), f, indent=2)

    def get_google_cloud_config(self) -> GoogleCloudConfig:
        """Get Google Cloud configuration.

        Returns:
            Google Cloud configuration
        """
        return self.config.google_cloud

    def get_agent_config(self) -> AgentConfig:
        """Get agent configuration.

        Returns:
            Agent configuration
        """
        return self.config.agents

    def update_agent_config(
        self,
        agent_id: str,
        config: dict[str, Any]
    ) -> None:
        """Update agent configuration.

        Args:
            agent_id: Agent identifier
            config: New configuration
        """
        if agent_id in self.config.agents.dict():
            setattr(self.config.agents, agent_id, config)
            self.save_config()

    def get_system_config(self) -> SystemConfig:
        """Get system configuration.

        Returns:
            System configuration
        """
        return self.config
