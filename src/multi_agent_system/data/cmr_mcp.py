"""
CMR MCP Server Integration for Pythia Multi-Agent System

This module integrates NASA's Common Metadata Repository (CMR) via the earthaccess library
to provide satellite and Earth science data access for climate risk analysis.
"""

import os
import logging
from typing import Optional, List, Dict, Any
import earthaccess
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class CMRDataProvider:
    """
    CMR Data Provider for accessing NASA Earth science data
    """
    
    def __init__(self, edl_token: Optional[str] = None):
        """
        Initialize CMR data provider with EDL token
        
        Args:
            edl_token: Earthdata Login token for authentication
        """
        self.edl_token = edl_token or os.getenv('NASA_EARTHDATA_TOKEN')
        self._authenticated = False
        
        if self.edl_token:
            self._authenticate()
    
    def _authenticate(self):
        """Authenticate with NASA Earthdata using EDL token"""
        try:
            # Configure earthaccess with EDL token
            earthaccess.login(strategy="token", token=self.edl_token)
            self._authenticated = True
            logger.info("Successfully authenticated with NASA Earthdata")
        except Exception as e:
            logger.error(f"Failed to authenticate with NASA Earthdata: {e}")
            self._authenticated = False
    
    def search_datasets(self, 
                       keywords: Optional[List[str]] = None,
                       start_date: Optional[str] = None,
                       end_date: Optional[str] = None,
                       daac: Optional[str] = None,
                       limit: int = 10) -> List[Dict[str, Any]]:
        """
        Search for datasets in NASA's CMR
        
        Args:
            keywords: List of keywords to search for
            start_date: Start date for temporal search (YYYY-MM-DD or YYYY)
            end_date: End date for temporal search (YYYY-MM-DD or YYYY)
            daac: Specific DAAC to search (e.g., 'PODAAC', 'NSIDC')
            limit: Maximum number of results to return
            
        Returns:
            List of dataset metadata dictionaries
        """
        if not self._authenticated:
            logger.warning("Not authenticated with NASA Earthdata")
            return []
        
        try:
            # Build search arguments
            search_args = {}
            
            if keywords:
                search_args['keyword'] = ' '.join(keywords)
            
            if daac:
                search_args['daac'] = daac
            
            if start_date or end_date:
                search_args['temporal'] = (start_date, end_date)
            
            # Search for datasets
            collections = earthaccess.search_datasets(count=limit, **search_args)
            
            # Format results
            results = []
            for collection in collections:
                try:
                    result = {
                        'concept_id': collection.concept_id(),
                        'short_name': collection.summary().get('short-name', 'Unknown'),
                        'title': collection.summary().get('title', 'Unknown'),
                        'abstract': collection.abstract(),
                        'version': collection.summary().get('version', 'Unknown'),
                        'daac': collection.summary().get('daac', 'Unknown'),
                        'temporal_range': collection.summary().get('temporal-range', 'Unknown'),
                        'spatial_coverage': collection.summary().get('spatial-coverage', 'Unknown')
                    }
                    results.append(result)
                except Exception as e:
                    logger.warning(f"Error formatting collection {collection.concept_id()}: {e}")
                    continue
            
            logger.info(f"Found {len(results)} datasets matching search criteria")
            return results
            
        except Exception as e:
            logger.error(f"Error searching CMR datasets: {e}")
            return []
    
    def get_dataset_granules(self, 
                           concept_id: str,
                           start_date: Optional[str] = None,
                           end_date: Optional[str] = None,
                           limit: int = 50) -> List[Dict[str, Any]]:
        """
        Get granules (individual files) for a specific dataset
        
        Args:
            concept_id: CMR concept ID of the dataset
            start_date: Start date for temporal search
            end_date: End date for temporal search
            limit: Maximum number of granules to return
            
        Returns:
            List of granule metadata dictionaries
        """
        if not self._authenticated:
            logger.warning("Not authenticated with NASA Earthdata")
            return []
        
        try:
            # Build search arguments
            search_args = {'concept_id': concept_id}
            
            if start_date or end_date:
                search_args['temporal'] = (start_date, end_date)
            
            # Search for granules
            granules = earthaccess.search_data(count=limit, **search_args)
            
            # Format results
            results = []
            for granule in granules:
                try:
                    result = {
                        'concept_id': granule.concept_id(),
                        'title': granule.summary().get('title', 'Unknown'),
                        'size': granule.summary().get('size', 'Unknown'),
                        'date_created': granule.summary().get('date-created', 'Unknown'),
                        'temporal_range': granule.summary().get('temporal-range', 'Unknown'),
                        'spatial_coverage': granule.summary().get('spatial-coverage', 'Unknown'),
                        'download_urls': granule.download_urls() if hasattr(granule, 'download_urls') else []
                    }
                    results.append(result)
                except Exception as e:
                    logger.warning(f"Error formatting granule {granule.concept_id()}: {e}")
                    continue
            
            logger.info(f"Found {len(results)} granules for dataset {concept_id}")
            return results
            
        except Exception as e:
            logger.error(f"Error getting granules for dataset {concept_id}: {e}")
            return []
    
    def get_climate_datasets(self, region: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get climate-related datasets for risk analysis
        
        Args:
            region: Optional region filter (e.g., 'Gulf Coast', 'Caribbean')
            
        Returns:
            List of climate dataset metadata
        """
        climate_keywords = [
            'climate', 'temperature', 'precipitation', 'sea level',
            'ocean temperature', 'atmospheric', 'weather', 'extreme weather',
            'hurricane', 'tropical cyclone', 'flood', 'drought'
        ]
        
        # Add region-specific keywords
        if region:
            if 'gulf' in region.lower() or 'alabama' in region.lower():
                climate_keywords.extend(['Gulf of Mexico', 'Mobile Bay', 'coastal'])
            elif 'caribbean' in region.lower():
                climate_keywords.extend(['Caribbean Sea', 'tropical', 'island'])
            elif 'kansas' in region.lower():
                climate_keywords.extend(['agriculture', 'farmland', 'plains'])
        
        return self.search_datasets(keywords=climate_keywords, limit=20)
    
    def get_oceanographic_datasets(self, region: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get oceanographic datasets for coastal risk analysis
        
        Args:
            region: Optional region filter
            
        Returns:
            List of oceanographic dataset metadata
        """
        ocean_keywords = [
            'ocean temperature', 'sea surface temperature', 'salinity',
            'ocean currents', 'sea level', 'wave height', 'ocean color',
            'chlorophyll', 'ocean acidification'
        ]
        
        return self.search_datasets(keywords=ocean_keywords, limit=15)
    
    def get_atmospheric_datasets(self, region: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get atmospheric datasets for weather risk analysis
        
        Args:
            region: Optional region filter
            
        Returns:
            List of atmospheric dataset metadata
        """
        atmospheric_keywords = [
            'atmospheric', 'weather', 'precipitation', 'temperature',
            'humidity', 'wind', 'pressure', 'atmospheric composition',
            'aerosols', 'clouds'
        ]
        
        return self.search_datasets(keywords=atmospheric_keywords, limit=15)

# Global CMR provider instance
_cmr_provider: Optional[CMRDataProvider] = None

def get_cmr_provider() -> CMRDataProvider:
    """Get or create global CMR provider instance"""
    global _cmr_provider
    if _cmr_provider is None:
        _cmr_provider = CMRDataProvider()
    return _cmr_provider

def initialize_cmr_provider(edl_token: str) -> CMRDataProvider:
    """Initialize CMR provider with EDL token"""
    global _cmr_provider
    _cmr_provider = CMRDataProvider(edl_token)
    return _cmr_provider 