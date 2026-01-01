"""
Example usage of the native ERDDAP MCP provider tools for agents.
"""
import asyncio
from src.multi_agent_system.agents import tools

async def main():
    # List available ERDDAP servers
    servers = await tools.erddap_list_servers_tool()
    print("Available ERDDAP servers:", servers)

    # Pick the first public server for demonstration
    if servers["status"] == "success" and servers["data"]:
        server_url = servers["data"][0]["url"]
        # Search for datasets containing 'SST' (sea surface temperature)
        search = await tools.erddap_search_datasets_tool("SST", server_url)
        print("Search results for 'SST':", search)

        # If datasets found, get info and fetch data
        if search["status"] == "success" and search["data"]:
            dataset_id = search["data"][0]["dataset_id"]
            info = await tools.erddap_get_dataset_info_tool(dataset_id, server_url)
            print(f"Info for dataset {dataset_id}:", info)

            # Fetch a small sample of data (first variable, no constraints)
            if info["status"] == "success" and info["data"]["variables"]:
                variable = info["data"]["variables"][0]
                data = await tools.erddap_fetch_data_tool(dataset_id, server_url, [variable], {})
                print(f"Sample data for {dataset_id} ({variable}):", data)

if __name__ == "__main__":
    asyncio.run(main())
