"""
FRED API Integration for Pythia Multi-Agent System

This module provides access to Federal Reserve Economic Data (FRED) API,
including economic indicators, interest rates, inflation data, and regional
economic data essential for IRR calculations and economic risk assessments.

FRED API Documentation: https://fred.stlouisfed.org/docs/api/
API Key Registration: https://fredaccount.stlouisfed.org
"""

import logging
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, List, Dict, Any

try:
    from fredapi import Fred
except ImportError:
    Fred = None
    logging.warning("fredapi not installed. Install with: pip install fredapi>=0.5.0")

from .data_source import DataSource

logger = logging.getLogger(__name__)


class FREDDataSource(DataSource):
    """
    FRED (Federal Reserve Economic Data) Data Source.
    
    Provides access to:
    - Economic indicators (GDP, unemployment, inflation)
    - Interest rates (Federal funds rate, Treasury rates)
    - Regional economic data (state-level indicators)
    - Data for IRR calculations
    """
    
    def __init__(self, cache_dir: str = ".cache"):
        """
        Initialize FRED data source.
        
        Args:
            cache_dir: Directory for caching data
        """
        super().__init__()
        self.cache_dir = Path(cache_dir) / "fred"
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.cache_expiry = timedelta(hours=6)  # 6-hour cache for FRED data
        
        # Get API key from environment
        api_key = os.getenv("FRED_API_KEY")
        if not api_key:
            logger.warning("FRED_API_KEY not found in environment. FRED API calls will fail.")
            self.fred = None
        elif Fred is None:
            logger.warning("fredapi library not installed. Install with: pip install fredapi>=0.5.0")
            self.fred = None
        else:
            try:
                self.fred = Fred(api_key=api_key)
                logger.info("FRED API client initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize FRED API client: {e}")
                self.fred = None
    
    def _check_api_available(self) -> bool:
        """Check if FRED API is available."""
        if self.fred is None:
            logger.error("FRED API not available. Check FRED_API_KEY environment variable and fredapi installation.")
            return False
        return True
    
    def get_economic_indicators(
        self,
        series_ids: List[str],
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        frequency: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get economic indicators by series ID.
        
        Args:
            series_ids: List of FRED series IDs (e.g., ['GDP', 'UNRATE', 'CPIAUCSL'])
            start_date: Start date in YYYY-MM-DD format (optional)
            end_date: End date in YYYY-MM-DD format (optional)
            frequency: Data frequency ('d'=daily, 'w'=weekly, 'm'=monthly, 'q'=quarterly, 'a'=annual)
        
        Returns:
            Dict with status and data for each series
        """
        if not self._check_api_available():
            return {"status": "error", "error": "FRED API not available"}
        
        try:
            results = {}
            
            for series_id in series_ids:
                try:
                    # Get series data
                    data = self.fred.get_series(
                        series_id,
                        start=start_date,
                        end=end_date,
                        frequency=frequency
                    )
                    
                    # Get series info
                    info = self.fred.get_series_info(series_id)
                    
                    results[series_id] = {
                        "data": data.to_dict() if hasattr(data, 'to_dict') else data.to_list() if hasattr(data, 'to_list') else list(data),
                        "info": {
                            "title": info.get("title", ""),
                            "units": info.get("units", ""),
                            "frequency": info.get("frequency", ""),
                            "seasonal_adjustment": info.get("seasonal_adjustment", ""),
                            "last_updated": info.get("last_updated", "")
                        }
                    }
                except Exception as e:
                    logger.error(f"Error fetching series {series_id}: {e}")
                    results[series_id] = {
                        "status": "error",
                        "error": str(e)
                    }
            
            return {
                "status": "success",
                "series_count": len(series_ids),
                "data": results
            }
        except Exception as e:
            logger.error(f"Error fetching economic indicators: {e}")
            return self.handle_error(e)
    
    def get_regional_economic_data(
        self,
        state: str,
        indicators: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Get state-specific economic data.
        
        Args:
            state: Two-letter state code (e.g., 'AL' for Alabama, 'TX' for Texas)
            indicators: List of indicator types ['unemployment', 'gdp', 'income'] (optional, defaults to all)
        
        Returns:
            Dict with regional economic data
        """
        if not self._check_api_available():
            return {"status": "error", "error": "FRED API not available"}
        
        try:
            state_upper = state.upper()
            
            # Default indicators if not specified
            if indicators is None:
                indicators = ['unemployment', 'gdp']
            
            results = {}
            
            # State unemployment rate (format: [STATE]UR, e.g., ALUR for Alabama)
            if 'unemployment' in indicators:
                try:
                    unemployment_series = f"{state_upper}UR"
                    data = self.fred.get_series(unemployment_series)
                    info = self.fred.get_series_info(unemployment_series)
                    results['unemployment_rate'] = {
                        "series_id": unemployment_series,
                        "data": data.to_dict() if hasattr(data, 'to_dict') else list(data),
                        "title": info.get("title", ""),
                        "units": info.get("units", ""),
                        "latest_value": float(data.iloc[-1]) if len(data) > 0 else None,
                        "latest_date": str(data.index[-1]) if len(data) > 0 else None
                    }
                except Exception as e:
                    logger.warning(f"Could not fetch unemployment data for {state}: {e}")
                    results['unemployment_rate'] = {"status": "error", "error": str(e)}
            
            # State GDP (format: [STATE]NGSP, e.g., ALNGSP for Alabama)
            if 'gdp' in indicators:
                try:
                    gdp_series = f"{state_upper}NGSP"
                    data = self.fred.get_series(gdp_series)
                    info = self.fred.get_series_info(gdp_series)
                    results['gdp'] = {
                        "series_id": gdp_series,
                        "data": data.to_dict() if hasattr(data, 'to_dict') else list(data),
                        "title": info.get("title", ""),
                        "units": info.get("units", ""),
                        "latest_value": float(data.iloc[-1]) if len(data) > 0 else None,
                        "latest_date": str(data.index[-1]) if len(data) > 0 else None
                    }
                except Exception as e:
                    logger.warning(f"Could not fetch GDP data for {state}: {e}")
                    results['gdp'] = {"status": "error", "error": str(e)}
            
            # State personal income (format: [STATE]PCPI, e.g., ALPCPI for Alabama)
            if 'income' in indicators:
                try:
                    income_series = f"{state_upper}PCPI"
                    data = self.fred.get_series(income_series)
                    info = self.fred.get_series_info(income_series)
                    results['personal_income'] = {
                        "series_id": income_series,
                        "data": data.to_dict() if hasattr(data, 'to_dict') else list(data),
                        "title": info.get("title", ""),
                        "units": info.get("units", ""),
                        "latest_value": float(data.iloc[-1]) if len(data) > 0 else None,
                        "latest_date": str(data.index[-1]) if len(data) > 0 else None
                    }
                except Exception as e:
                    logger.warning(f"Could not fetch income data for {state}: {e}")
                    results['personal_income'] = {"status": "error", "error": str(e)}
            
            return {
                "status": "success",
                "state": state_upper,
                "indicators": indicators,
                "data": results
            }
        except Exception as e:
            logger.error(f"Error fetching regional economic data: {e}")
            return self.handle_error(e)
    
    def get_irr_calculation_data(self) -> Dict[str, Any]:
        """
        Get data needed for IRR (Internal Rate of Return) calculations.
        
        Returns:
            Dict with:
            - Risk-free rate (10-Year Treasury: DGS10)
            - Inflation rate (CPI: CPIAUCSL)
            - Federal funds rate (FEDFUNDS)
        """
        if not self._check_api_available():
            return {"status": "error", "error": "FRED API not available"}
        
        try:
            # Get latest values for key indicators
            series_ids = {
                "risk_free_rate": "DGS10",  # 10-Year Treasury Constant Maturity Rate
                "inflation_rate": "CPIAUCSL",  # Consumer Price Index for All Urban Consumers
                "federal_funds_rate": "FEDFUNDS"  # Federal Funds Effective Rate
            }
            
            results = {}
            
            for key, series_id in series_ids.items():
                try:
                    data = self.fred.get_series(series_id)
                    info = self.fred.get_series_info(series_id)
                    
                    # Get latest value
                    latest_value = float(data.iloc[-1]) if len(data) > 0 else None
                    latest_date = str(data.index[-1]) if len(data) > 0 else None
                    
                    results[key] = {
                        "series_id": series_id,
                        "title": info.get("title", ""),
                        "units": info.get("units", ""),
                        "latest_value": latest_value,
                        "latest_date": latest_date,
                        "frequency": info.get("frequency", "")
                    }
                except Exception as e:
                    logger.warning(f"Could not fetch {key} ({series_id}): {e}")
                    results[key] = {"status": "error", "error": str(e)}
            
            return {
                "status": "success",
                "data": results,
                "description": "Data for IRR calculations: risk-free rate, inflation rate, and federal funds rate"
            }
        except Exception as e:
            logger.error(f"Error fetching IRR calculation data: {e}")
            return self.handle_error(e)
    
    def search_series(
        self,
        query: str,
        limit: int = 20,
        order_by: str = "popularity"
    ) -> Dict[str, Any]:
        """
        Search for FRED series by keyword.
        
        Args:
            query: Search query (e.g., "unemployment", "GDP", "Alabama")
            limit: Maximum number of results (default: 20)
            order_by: Sort order ('popularity', 'search_rank', 'series_id', 'title', 'units', 'frequency')
        
        Returns:
            Dict with search results
        """
        if not self._check_api_available():
            return {"status": "error", "error": "FRED API not available"}
        
        try:
            # Use FRED API search
            search_results = self.fred.search(query, limit=limit, order_by=order_by)
            
            # Convert to list of dicts
            results = []
            for idx, row in search_results.iterrows():
                results.append({
                    "series_id": row.get("id", ""),
                    "title": row.get("title", ""),
                    "units": row.get("units", ""),
                    "frequency": row.get("frequency", ""),
                    "seasonal_adjustment": row.get("seasonal_adjustment", ""),
                    "popularity": row.get("popularity", 0)
                })
            
            return {
                "status": "success",
                "query": query,
                "count": len(results),
                "results": results
            }
        except Exception as e:
            logger.error(f"Error searching FRED series: {e}")
            return self.handle_error(e)
    
    def get_series_info(self, series_id: str) -> Dict[str, Any]:
        """
        Get metadata about a specific FRED series.
        
        Args:
            series_id: FRED series ID (e.g., 'GDP', 'UNRATE', 'DGS10')
        
        Returns:
            Dict with series metadata
        """
        if not self._check_api_available():
            return {"status": "error", "error": "FRED API not available"}
        
        try:
            info = self.fred.get_series_info(series_id)
            
            return {
                "status": "success",
                "series_id": series_id,
                "info": {
                    "title": info.get("title", ""),
                    "units": info.get("units", ""),
                    "frequency": info.get("frequency", ""),
                    "seasonal_adjustment": info.get("seasonal_adjustment", ""),
                    "last_updated": info.get("last_updated", ""),
                    "observation_start": info.get("observation_start", ""),
                    "observation_end": info.get("observation_end", ""),
                    "notes": info.get("notes", "")
                }
            }
        except Exception as e:
            logger.error(f"Error getting series info for {series_id}: {e}")
            return self.handle_error(e)
    
    async def fetch_data(self, **kwargs) -> Dict[str, Any]:
        """
        Fetch data from FRED API using the generic DataSource interface.
        
        Args:
            **kwargs: Can include:
                - action: "get_economic_indicators", "get_regional_economic_data", 
                         "get_irr_calculation_data", "search_series", "get_series_info"
                - Other parameters depend on the action
        
        Returns:
            Dict[str, Any]: Fetched data
        """
        self.fetch_count += 1
        self.last_fetch_time = datetime.now()
        
        action = kwargs.pop("action", "get_economic_indicators")
        
        try:
            if action == "get_economic_indicators":
                return self.get_economic_indicators(**kwargs)
            elif action == "get_regional_economic_data":
                return self.get_regional_economic_data(**kwargs)
            elif action == "get_irr_calculation_data":
                return self.get_irr_calculation_data()
            elif action == "search_series":
                return self.search_series(**kwargs)
            elif action == "get_series_info":
                return self.get_series_info(**kwargs)
            else:
                return {"status": "error", "error": f"Unknown action: {action}"}
        except Exception as e:
            return self.handle_error(e)
    
    def get_metadata(self) -> Dict[str, Any]:
        """Get metadata about this data source."""
        return {
            "name": "FRED API",
            "description": "Federal Reserve Economic Data API",
            "api_documentation": "https://fred.stlouisfed.org/docs/api/",
            "api_key_registration": "https://fredaccount.stlouisfed.org",
            "data_types": [
                "economic_indicators",
                "interest_rates",
                "inflation_data",
                "regional_economic_data",
                "irr_calculation_data"
            ],
            "requires_api_key": True,
            "api_key_env_var": "FRED_API_KEY"
        }

