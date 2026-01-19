"""
S.O.I.L.E.R. Data Package
Knowledge base, reference data, and database management.
"""

from data.knowledge_base import (
    SOIL_SERIES,
    CROP_REQUIREMENTS,
    FERTILIZERS,
    CLIMATE_DATA,
    DISTRICTS,
    get_soil_series,
    get_crop_requirements,
    get_fertilizers_by_type,
    get_all_soil_series_names,
    get_all_crop_names,
    get_data_version,
    get_data_last_updated,
    reload_data,
)

from data.database_manager import (
    DatabaseManager,
    get_database,
    save_analysis,
    get_recent_history,
    get_analysis_by_id,
)

__all__ = [
    # Knowledge Base Data
    "SOIL_SERIES",
    "CROP_REQUIREMENTS",
    "FERTILIZERS",
    "CLIMATE_DATA",
    "DISTRICTS",
    # Knowledge Base Functions
    "get_soil_series",
    "get_crop_requirements",
    "get_fertilizers_by_type",
    "get_all_soil_series_names",
    "get_all_crop_names",
    "get_data_version",
    "get_data_last_updated",
    "reload_data",
    # Database Manager
    "DatabaseManager",
    "get_database",
    "save_analysis",
    "get_recent_history",
    "get_analysis_by_id",
]
