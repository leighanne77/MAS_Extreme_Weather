"""
ERDDAP MCP Native Data Provider
Implements a native MCP-compliant ERDDAP data provider for agent use.
"""

import os
import json
import logging
from typing import List, Dict, Any, Optional
from pathlib import Path
from datetime import datetime, timedelta
from .data_source import DataSource
from erddapy import ERDDAP
import pandas as pd

logger = logging.getLogger(__name__)

class ERDDAPDataProvider(DataSource):
    """
    Native MCP provider for ERDDAP servers.
    """
    def __init__(self, registry_path: Optional[str] = None):
        super().__init__()
        self.registry_path = registry_path or os.path.join(
            os.path.dirname(__file__), 'erddap_servers.json')
        self.servers = self._load_servers()
        self.cache: Dict[str, Any] = {}
        self.cache_expiry = timedelta(hours=6)

    def _load_servers(self) -> List[Dict[str, Any]]:
        try:
            with open(self.registry_path, 'r') as f:
                servers = json.load(f)
            logger.info(f"Loaded {len(servers)} ERDDAP servers from registry.")
            return servers
        except Exception as e:
            logger.error(f"Failed to load ERDDAP servers: {e}")
            return []

    def list_servers(self, public_only: bool = True) -> List[Dict[str, Any]]:
        return [s for s in self.servers if (not public_only or s.get('public', True))]

    def search_datasets(self, query: str, server_url: str) -> List[Dict[str, Any]]:
        e = ERDDAP(server=server_url)
        search_url = e.get_search_url(response="csv", search_for=query)
        df = pd.read_csv(search_url)
        results = []
        for _, row in df.iterrows():
            results.append({
                'dataset_id': row.get('Dataset ID', ''),
                'title': row.get('Title', ''),
                'institution': row.get('Institution', ''),
                'summary': row.get('Summary', ''),
            })
        return results

    def get_dataset_info(self, dataset_id: str, server_url: str, protocol: str = "tabledap") -> Dict[str, Any]:
        e = ERDDAP(server=server_url, protocol=protocol)
        e.dataset_id = dataset_id
        info_url = e.get_info_url(response="csv")
        df = pd.read_csv(info_url)
        global_attrs = df[df['Variable Name'] == 'NC_GLOBAL']
        variables = df[df['Row Type'] == 'variable']['Variable Name'].unique().tolist()
        return {
            'title': global_attrs[global_attrs['Attribute Name'] == 'title']['Value'].values[0] if not global_attrs[global_attrs['Attribute Name'] == 'title'].empty else '',
            'summary': global_attrs[global_attrs['Attribute Name'] == 'summary']['Value'].values[0] if not global_attrs[global_attrs['Attribute Name'] == 'summary'].empty else '',
            'variables': variables
        }

    def get_data(self, dataset_id: str, server_url: str, variables: List[str], constraints: Dict[str, Any], protocol: str = "tabledap") -> pd.DataFrame:
        e = ERDDAP(server=server_url, protocol=protocol)
        e.dataset_id = dataset_id
        e.response = "csv"
        if variables:
            e.variables = variables
        if constraints:
            e.constraints = constraints
        if protocol == "griddap":
            e.griddap_initialize()
        df = e.to_pandas()
        return df

    async def fetch_data(self, **kwargs) -> dict:
        # Example: fetch_data(dataset_id=..., server_url=..., variables=..., constraints=...)
        try:
            df = self.get_data(
                dataset_id=kwargs['dataset_id'],
                server_url=kwargs['server_url'],
                variables=kwargs.get('variables', []),
                constraints=kwargs.get('constraints', {}),
                protocol=kwargs.get('protocol', 'tabledap')
            )
            self.last_fetch_time = datetime.now()
            self.fetch_count += 1
            return {'status': 'ok', 'data': df.to_dict(orient='records')}
        except Exception as e:
            return self.handle_error(e)


# Singleton instance for convenience
_erddap_provider_instance: Optional[ERDDAPDataProvider] = None


def get_erddap_provider(registry_path: Optional[str] = None) -> ERDDAPDataProvider:
    """
    Get a singleton instance of the ERDDAPDataProvider.
    
    Args:
        registry_path: Optional path to the ERDDAP servers registry JSON file.
                      If not provided, uses the default registry path.
    
    Returns:
        ERDDAPDataProvider: Singleton instance of the ERDDAP data provider.
    
    Example:
        >>> provider = get_erddap_provider()
        >>> servers = provider.list_servers()
    """
    global _erddap_provider_instance
    if _erddap_provider_instance is None:
        _erddap_provider_instance = ERDDAPDataProvider(registry_path=registry_path)
    return _erddap_provider_instance

