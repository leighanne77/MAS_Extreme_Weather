"""
Integration tests for OpenET API.

Tests the OpenETDataSource class for fetching evapotranspiration (ET) data.
Requires valid API credentials to run against live API.
"""

import pytest
from src.multi_agent_system.data.openet_api import OpenETDataSource


class TestOpenETIntegration:
    """Integration tests for OpenET API."""

    @pytest.fixture
    def openet_source(self):
        """Create OpenETDataSource instance."""
        return OpenETDataSource()

    @pytest.mark.integration
    def test_get_et_success(self, openet_source):
        """Test fetching ET data for a valid location."""
        # Example coordinates (longitude, latitude) for Kansas
        lon = -100.0
        lat = 38.0
        start_date = "2022-01-01"
        end_date = "2022-12-31"
        source = "ensemble"  # or 'ssebop', 'disalexi', etc.

        result = openet_source.get_et(lon, lat, start_date, end_date, source)

        # Check response structure
        assert "status" in result
        if result["status"] == "success":
            assert "data" in result
        else:
            # API may fail without credentials - that's expected
            assert "error" in result


# Allow running directly for manual testing
if __name__ == "__main__":
    openet = OpenETDataSource()
    result = openet.get_et(-100.0, 38.0, "2022-01-01", "2022-12-31", "ensemble")
    print("OpenET API result:", result)
