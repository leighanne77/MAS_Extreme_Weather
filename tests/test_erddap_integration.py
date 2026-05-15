"""
Integration tests for ERDDAP data tools.

Tests the native ERDDAP MCP provider tools for fetching oceanographic data.
These tests connect to live ERDDAP servers.
"""

import pytest
from src.multi_agent_system.agents import tools


class TestERDDAPIntegration:
    """Integration tests for ERDDAP tools."""

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_list_erddap_servers(self):
        """Test listing available ERDDAP servers."""
        servers = await tools.erddap_list_servers_tool()
        
        assert "status" in servers
        if servers["status"] == "success":
            assert "data" in servers
            assert isinstance(servers["data"], list)

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_search_datasets(self):
        """Test searching for datasets on ERDDAP servers."""
        # First get available servers
        servers = await tools.erddap_list_servers_tool()
        
        if servers["status"] == "success" and servers["data"]:
            server_url = servers["data"][0]["url"]
            # Search for datasets containing 'SST' (sea surface temperature)
            search = await tools.erddap_search_datasets_tool("SST", server_url)
            
            assert "status" in search
            # Search may return empty results, which is valid

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_get_dataset_info(self):
        """Test getting dataset information from ERDDAP."""
        servers = await tools.erddap_list_servers_tool()
        
        if servers["status"] == "success" and servers["data"]:
            server_url = servers["data"][0]["url"]
            search = await tools.erddap_search_datasets_tool("SST", server_url)
            
            if search["status"] == "success" and search["data"]:
                dataset_id = search["data"][0]["dataset_id"]
                info = await tools.erddap_get_dataset_info_tool(dataset_id, server_url)
                
                assert "status" in info
                if info["status"] == "success":
                    assert "data" in info


# Allow running directly for manual testing
if __name__ == "__main__":
    import asyncio

    async def main():
        servers = await tools.erddap_list_servers_tool()
        print("Available ERDDAP servers:", servers)

        if servers["status"] == "success" and servers["data"]:
            server_url = servers["data"][0]["url"]
            search = await tools.erddap_search_datasets_tool("SST", server_url)
            print("Search results for 'SST':", search)

    asyncio.run(main())
