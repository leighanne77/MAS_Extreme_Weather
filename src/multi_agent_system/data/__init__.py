"""
Data handling and integration modules.
"""

from .data_source import DataSource
from .data_sources import DataSource, DataSourceManager
from .nature_based_solutions_source import NatureBasedSolutionsSource
from .weather_data import NOAAWeatherData, get_weather_data

__all__ = [
    'NOAAWeatherData',
    'get_weather_data',
    'DataSource',
    'DataSourceManager',
    'NatureBasedSolutionsSource'
]
