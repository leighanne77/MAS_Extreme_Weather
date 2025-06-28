"""
Base data source module.
"""

import logging
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any

logger = logging.getLogger(__name__)

class DataSource(ABC):
    """Base class for all data sources.

    This class defines the interface that all data sources must implement.
    It includes methods for fetching data, handling errors, and collecting metrics.
    """

    def __init__(self):
        """Initialize the data source."""
        self.last_fetch_time: datetime | None = None
        self.fetch_count: int = 0
        self.error_count: int = 0

    @abstractmethod
    async def fetch_data(self, **kwargs) -> dict[str, Any]:
        """Fetch data from the source.

        Args:
            **kwargs: Additional arguments for fetching data

        Returns:
            Dict[str, Any]: Fetched data

        Raises:
            Exception: If data fetching fails
        """
        pass

    def handle_error(self, error: Exception) -> dict[str, Any]:
        """Handle an error that occurred during data fetching.

        Args:
            error (Exception): The error that occurred

        Returns:
            Dict[str, Any]: Error response
        """
        self.error_count += 1
        logger.error(f"Error fetching data: {str(error)}")
        return {
            "status": "error",
            "error": str(error)
        }

    def get_metrics(self) -> dict[str, Any]:
        """Get metrics for this data source.

        Returns:
            Dict[str, Any]: Metrics including fetch count, error count, and last fetch time
        """
        return {
            "fetch_count": self.fetch_count,
            "error_count": self.error_count,
            "last_fetch_time": self.last_fetch_time.isoformat() if self.last_fetch_time else None
        }
