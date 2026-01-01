# ERDDAP MCP Server - Getting Started Guide

**Date Created**: December 14, 2025  
**Repository**: [https://github.com/robertdcurrier/erddap2mcp](https://github.com/robertdcurrier/erddap2mcp)

---

## Overview

This guide walks you through setting up the ERDDAP MCP Server for oceanographic and environmental data access. The ERDDAP MCP Server provides access to 63+ pre-configured ERDDAP servers worldwide.

---

## Prerequisites

✅ **Already Done**:
- `erddapy>=0.10.0` is already in `requirements.txt`
- `mcp[cli]>=1.6.0` is already in `requirements.txt`

---

## Step-by-Step Setup

### **Step 1: Install Dependencies**

First, make sure all dependencies are installed:

```bash
# Install from requirements.txt (includes erddapy and mcp)
pip install -r requirements.txt

# Or install individually
pip install erddapy>=0.10.0
pip install mcp[cli]>=1.6.0
```

### **Step 2: Clone the ERDDAP MCP Server Repository**

```bash
# Navigate to your project directory
cd /Users/midnighthome/Builds/004_MAS_Climate

# Clone the repository into dependencies directory
mkdir -p dependencies
cd dependencies
git clone https://github.com/robertdcurrier/erddap2mcp.git
cd ..

# This creates a directory: dependencies/erddap2mcp/
```

### **Step 3: Review the Repository Structure**

The repository contains:
- `erddapy_mcp_server.py` - Main MCP server file (local stdio mode)
- `erddap_remote_mcp_oauth.py` - Remote HTTP server version
- `erddaps.json` - 63+ pre-configured ERDDAP servers
- `requirements.txt` - Dependencies for the MCP server
- `README.md` - Documentation

### **Step 4: Install Repository Dependencies**

```bash
# Navigate to the cloned repository
cd dependencies/erddap2mcp

# Install the repository's dependencies
pip install -r requirements.txt
```

### **Step 5: Test the MCP Server (Optional)**

Test that the server works:

```bash
# Test the server directly
python erddapy_mcp_server.py

# Or test with a command
echo '{"jsonrpc": "2.0", "method": "tools/list", "id": 1}' | python erddapy_mcp_server.py
```

### **Step 6: Create Wrapper in Your Project**

Create a wrapper file in your project to integrate the ERDDAP MCP server:

**File**: `src/multi_agent_system/data/erddap_mcp.py`

```python
"""
ERDDAP MCP Server Integration

Wraps the erddap2mcp community repository to provide ERDDAP data access.
"""

import logging
import os
import subprocess
from pathlib import Path
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)

class ERDDAPMCPProvider:
    """
    ERDDAP MCP Server Provider
    
    Wraps the erddap2mcp repository to provide access to 63+ ERDDAP servers.
    No API key required - uses public ERDDAP servers.
    """
    
    def __init__(self, erddap_server_path: Optional[str] = None):
        """
        Initialize ERDDAP MCP provider.
        
        Args:
            erddap_server_path: Path to erddapy_mcp_server.py
                                Default: looks for erddap2mcp/ in project root
        """
        # Find the erddap2mcp repository
        project_root = Path(__file__).parent.parent.parent.parent.parent
        default_path = project_root / "dependencies" / "erddap2mcp" / "erddapy_mcp_server.py"
        
        if erddap_server_path:
            self.server_path = Path(erddap_server_path)
        elif default_path.exists():
            self.server_path = default_path
        else:
            # Try relative to current directory
            self.server_path = Path("dependencies/erddap2mcp/erddapy_mcp_server.py")
        
        if not self.server_path.exists():
            logger.warning(
                f"ERDDAP MCP server not found at {self.server_path}. "
                "Please clone the repository: git clone https://github.com/robertdcurrier/erddap2mcp.git"
            )
    
    def get_available_servers(self) -> Dict[str, Any]:
        """
        Get list of available ERDDAP servers.
        
        Returns:
            Dict with available ERDDAP servers from erddaps.json
        """
        # The erddaps.json file is in the dependencies/erddap2mcp directory
        erddaps_file = self.server_path.parent / "erddaps.json"
        
        if not erddaps_file.exists():
            return {
                "status": "error",
                "error": "erddaps.json not found"
            }
        
        try:
            import json
            with open(erddaps_file, 'r') as f:
                servers = json.load(f)
            return {
                "status": "success",
                "servers": servers,
                "count": len(servers) if isinstance(servers, list) else 0
            }
        except Exception as e:
            logger.error(f"Failed to load ERDDAP servers: {e}")
            return {
                "status": "error",
                "error": str(e)
            }
    
    def search_datasets(
        self,
        server_url: Optional[str] = None,
        search_text: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Search for datasets on an ERDDAP server.
        
        Args:
            server_url: ERDDAP server URL (defaults to NOAA CoastWatch)
            search_text: Search query
        
        Returns:
            Dataset search results
        """
        # This would call the MCP server tool
        # Implementation depends on how you integrate with the MCP server
        # For now, this is a placeholder
        return {
            "status": "success",
            "message": "Use MCP server tools directly for dataset search"
        }
```

### **Step 7: Register in Data Source Registry**

Add to `src/multi_agent_system/data_management.py` or `src/multi_agent_system/data/enhanced_data_sources.py`:

```python
# In EnhancedDataManager._initialize_sources() or similar
from .erddap_mcp import ERDDAPMCPProvider

# Add ERDDAP MCP provider
self.sources["erddap"] = ERDDAPMCPProvider()
```

### **Step 8: Configure ERDDAP Server URL (Optional)**

The repository includes `erddaps.json` with 63+ pre-configured servers. You can:

1. **Use default server** (NOAA CoastWatch): No configuration needed
2. **Specify a different server**: Pass `server_url` parameter when calling methods
3. **Add custom servers**: Edit `erddaps.json` in the `dependencies/erddap2mcp/` directory

---

## Available ERDDAP Servers

The `erddaps.json` file includes servers such as:

- **NOAA CoastWatch**: `https://coastwatch.pfeg.noaa.gov/erddap`
- **IOOS ERDDAP**: `https://erddap.ioos.us/erddap`
- **GCOOS ERDDAP**: `https://gcoos5.geos.tamu.edu/erddap` (Gulf of Mexico)
- **Marine Institute Ireland**: `https://erddap.marine.ie/erddap`
- **Ocean Networks Canada**: `https://data.oceannetworks.ca/erddap`
- **EMODnet Physics**: `https://erddap.emodnet-physics.eu/erddap`

And 57+ more servers worldwide.

---

## Integration Options

### **Option A: Local stdio Server (Recommended for Development)**

Use the local `erddapy_mcp_server.py` directly:

```python
# In your agent configuration or data source
import subprocess

# Start the MCP server as a subprocess
mcp_process = subprocess.Popen(
    ["python", "dependencies/erddap2mcp/erddapy_mcp_server.py"],
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE
)
```

### **Option B: Remote HTTP Server (For Production)**

Use the remote server version:

```bash
# Deploy the remote server (see repository README for details)
cd erddap2mcp
python erddap_remote_mcp_oauth.py
```

Then connect via HTTP endpoint.

### **Option C: Direct Integration (Simplest)**

Create a wrapper that uses `erddapy` library directly (bypassing MCP protocol):i 

```python
from erddapy import ERDDAP

# Direct ERDDAP access without MCP
e = ERDDAP(
    server="https://coastwatch.pfeg.noaa.gov/erddap",
    protocol="tabledap"
)

# Search for datasets
datasets = e.get_search_url(search_for="temperature", response="csv")
```

---

## Quick Start Commands

```bash
# 1. Install dependencies (if not already done)
pip install -r requirements.txt

# 2. Clone the repository into dependencies directory
mkdir -p dependencies
cd dependencies
git clone https://github.com/robertdcurrier/erddap2mcp.git
cd ..

# 3. Install repository dependencies
cd dependencies/erddap2mcp
pip install -r requirements.txt
cd ../..

# 4. Test the server
cd dependencies/erddap2mcp
python erddapy_mcp_server.py
# Press Ctrl+C to stop
cd ../..

# 5. Create wrapper file
# Create src/multi_agent_system/data/erddap_mcp.py (see Step 6 above)
```

---

## Troubleshooting

### **Issue: "Module not found: erddapy"**
**Solution**: 
```bash
pip install erddapy>=0.10.0
```

### **Issue: "Module not found: mcp"**
**Solution**:
```bash
pip install mcp[cli]>=1.6.0
```

### **Issue: "erddap2mcp directory not found"**
**Solution**: Make sure you cloned the repository in the dependencies directory:
```bash
cd /Users/midnighthome/Builds/004_MAS_Climate
mkdir -p dependencies
cd dependencies
git clone https://github.com/robertdcurrier/erddap2mcp.git
cd ..
```

### **Issue: "erddaps.json not found"**
**Solution**: The file should be in `dependencies/erddap2mcp/erddaps.json`. If missing, check the repository.

---

## Next Steps

1. ✅ Clone the repository
2. ✅ Install dependencies
3. ✅ Test the server
4. ✅ Create wrapper file (`src/multi_agent_system/data/erddap_mcp.py`)
5. ✅ Register in data source registry (`enhanced_data_sources.py`)
6. ✅ Add agent tools for ERDDAP data access (`tools.py`)
7. ⬜ Test integration with your agents

---

## References

- **Repository**: [https://github.com/robertdcurrier/erddap2mcp](https://github.com/robertdcurrier/erddap2mcp)
- **ERDDAP Documentation**: [https://coastwatch.pfeg.noaa.gov/erddap/index.html](https://coastwatch.pfeg.noaa.gov/erddap/index.html)
- **erddapy Library**: [https://github.com/ioos/erddapy](https://github.com/ioos/erddapy)
- **MCP Protocol**: [https://modelcontextprotocol.io/](https://modelcontextprotocol.io/)

---

## Change Log

### **December 14, 2025**
- **Initial Creation**: Step-by-step getting started guide for ERDDAP MCP Server
- **Repository**: Confirmed correct repository URL (robertdcurrier/erddap2mcp)
- **Dependencies**: Noted that erddapy and mcp are already in requirements.txt
- **Integration Options**: Provided three options (local stdio, remote HTTP, direct integration)
- **Implementation Complete**: 
  - ✅ Created `ERDDAPDataProvider` wrapper class in `src/multi_agent_system/data/erddap_mcp.py`
  - ✅ Registered in `EnhancedDataManager` as `sources["erddap"]`
  - ✅ Added 4 agent tools: `get_erddap_servers_tool`, `search_erddap_datasets_tool`, `get_erddap_dataset_info_tool`, `get_erddap_data_tool`
  - ✅ Exported in `src/multi_agent_system/data/__init__.py`

