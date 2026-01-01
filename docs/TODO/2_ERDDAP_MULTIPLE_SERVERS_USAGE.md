# ERDDAP Multiple Servers Usage Guide

**Date Created**: December 14, 2025  
**Purpose**: Guide for using multiple ERDDAP servers including CoastWatch and GCOOS

---

## Overview

 The design of your MCP tool interface (e.g., get_erddap_data_tool, search_erddap_datasets_tool), allows agents use to interact with ERDDAP servers via the MCP layer.

Agents can switch between servers by passing the appropriate server_name to the tool functions, and can discover available servers programmatically using the provided helper tools. This is simple, flexible, and fully agent-friendly.

## STeps to implement

## Step 2: Design the Data Provider Class
File: erddap_mcp.py
Class: ERDDAPDataProvider (inherits from your MCP DataSource base, if available)
Responsibilities:
Load server registry from erddaps.json
List available servers and their metadata
Search datasets on a given server (by name, region, etc.)
Retrieve data from a selected dataset/server
Handle server selection by server_name, short_name, or URL
Implement caching and error handling
Cursor Rule Alignment:
Do not invent new architectures; use the existing MCP/agent structure.
Only reference real, existing servers and files.

## Step 3: Implement Server Registry Loader
Load and parse erddaps.json at initialization.
Provide methods to list all servers, filter by region/type, and get server details by name.
Cursor Rule Alignment:
Verify all server URLs and document sources.
Do not reference servers that do not exist in the registry.

## Step 4: Implement Dataset Search
For a given server, implement a method to search datasets (e.g., by keyword, bounding box, time range).
Use the ERDDAP REST API endpoints (e.g., /search/index.json) under the hood, but abstract this behind the MCP interface.
Cursor Rule Alignment:
Only expose datasets that are actually available on the server.
If unsure about a dataset, flag for verification.

## Step 5: Implement Data Retrieval
For a given server and dataset, implement a method to retrieve data (CSV, JSON, or NetCDF as needed).
Support variable selection, constraints (e.g., time, region), and output format.
Return data in a standardized MCP format for agent consumption.

## Step 6: MCP Tool Integration
Expose MCP tool functions:
get_erddap_servers_tool()
search_erddap_datasets_tool(search_text, server_name, ...)
get_erddap_data_tool(dataset_id, server_name, variables, constraints, ...)
Ensure these tools are discoverable and usable by agents.
Cursor Rule Alignment:
Present tool options and recommendations before making changes.
Do not add or remove tool interfaces without explicit approval.

## Step 7: Error Handling and Fallbacks
Handle server downtime, timeouts, and missing datasets gracefully.
Allow agents to try alternative servers if the primary is unavailable.
Cursor Rule Alignment:
Communicate clearly when data is unavailable or needs verification.
Do not make up fallback data or sources.

## Step 8: Caching and Performance
Implement caching for server lists, dataset metadata, and (optionally) data queries to reduce load and improve speed.
Respect cache expiry intervals (e.g., 1–6 hours, not real-time).
Cursor Rule Alignment:
Document cache intervals and do not promise real-time updates.

## Step 9: Documentation and Usage Examples
Update MCP_Integrations_December_2025.md and 2_ERDDAP_MULTIPLE_SERVERS_USAGE.md with:
How to use the new MCP tools
Example agent queries
Best practices for server selection
Cursor Rule Alignment:
Always update the change log and date in docs.
Suggest doc changes before making them, if not explicitly approved.

## Step 10: Testing
Unit tests for each method (server listing, search, data retrieval)
Integration tests with at least two real ERDDAP servers
Agent workflow tests (end-to-end)
Cursor Rule Alignment:
Only test with real, available servers and datasets.
Do not create fictional test data or scenarios.

The ERDDAP integration supports **63+ pre-configured servers** from `dependencies/erddap2mcp/erddaps.json`. You can easily switch between servers using either:
- **Server name** (e.g., "coastwatch", "gcoos") - **Recommended**
- **Server short_name** (e.g., "CSWC", "GCOOS") - **Recommended**
- **Full server URL** (e.g., "https://coastwatch.pfeg.noaa.gov/erddap/")

---

---

## Change Log

### **December 14, 2025**
- **Initial Creation**: Guide for using multiple ERDDAP servers
- **Enhanced Support**: Added `server_name` parameter to all methods
- **Helper Methods**: Added `get_server_by_name()` and `get_server_url()` methods
- **Examples**: Provided examples for CoastWatch and GCOOS usage

