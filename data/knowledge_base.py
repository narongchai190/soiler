"""
S.O.I.L.E.R. Knowledge Base
Soil Optimization & Intelligent Land Expert Recommender

Contains reference data for soil series, crop requirements, and fertilizers
specific to Phrae Province, Thailand.

Data is loaded from master_data.json for easy maintenance and updates.
"""

import json
from pathlib import Path
from typing import Dict, List, Any, Optional


# =============================================================================
# DATA LOADING
# =============================================================================

def _load_master_data() -> Dict[str, Any]:
    """Load master data from JSON file."""
    data_dir = Path(__file__).parent
    json_path = data_dir / "master_data.json"

    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Warning: master_data.json not found at {json_path}")
        return _get_fallback_data()
    except json.JSONDecodeError as e:
        print(f"Warning: Error parsing master_data.json: {e}")
        return _get_fallback_data()


def _get_fallback_data() -> Dict[str, Any]:
    """Return minimal fallback data if JSON fails to load."""
    return {
        "soil_series": {},
        "crop_requirements": {},
        "fertilizers": [],
        "climate_data": {},
        "districts": {}
    }


# Load data on module import
_MASTER_DATA = _load_master_data()


# =============================================================================
# SOIL SERIES DATABASE
# =============================================================================

SOIL_SERIES: Dict[str, Dict[str, Any]] = _MASTER_DATA.get("soil_series", {})


# =============================================================================
# CROP REQUIREMENTS DATABASE
# =============================================================================

CROP_REQUIREMENTS: Dict[str, Dict[str, Any]] = _MASTER_DATA.get("crop_requirements", {})


# =============================================================================
# FERTILIZER DATABASE
# =============================================================================

FERTILIZERS: List[Dict[str, Any]] = _MASTER_DATA.get("fertilizers", [])


# =============================================================================
# CLIMATE DATA
# =============================================================================

CLIMATE_DATA: Dict[str, Any] = _MASTER_DATA.get("climate_data", {})


# =============================================================================
# DISTRICTS DATA
# =============================================================================

DISTRICTS: Dict[str, Any] = _MASTER_DATA.get("districts", {})


# =============================================================================
# METADATA
# =============================================================================

def get_data_version() -> str:
    """Get the version of the loaded data."""
    metadata = _MASTER_DATA.get("metadata", {})
    return metadata.get("version", "unknown")


def get_data_last_updated() -> str:
    """Get the last updated date of the data."""
    metadata = _MASTER_DATA.get("metadata", {})
    return metadata.get("last_updated", "unknown")


# =============================================================================
# HELPER FUNCTIONS - SOIL SERIES
# =============================================================================

def get_soil_series(series_name: str) -> Optional[Dict[str, Any]]:
    """
    Retrieve soil series data by name.

    Args:
        series_name: Name of the soil series (e.g., "Phrae", "Long", "Den Chai")

    Returns:
        Soil series data dictionary or None if not found
    """
    return SOIL_SERIES.get(series_name)


def get_all_soil_series_names() -> List[str]:
    """Return list of all available soil series names."""
    return list(SOIL_SERIES.keys())


def get_soil_series_by_location(location_name: str) -> Optional[Dict[str, Any]]:
    """
    Get soil series data based on location/district name.

    Args:
        location_name: Location or district name

    Returns:
        Matching soil series data or None
    """
    # Try direct match first
    for name, data in SOIL_SERIES.items():
        if name.lower() in location_name.lower():
            return {name: data}

        # Check location areas
        areas = data.get("location_areas", [])
        for area in areas:
            if area.lower() in location_name.lower():
                return {name: data}

    return None


# =============================================================================
# HELPER FUNCTIONS - CROPS
# =============================================================================

def get_crop_requirements(crop_name: str) -> Optional[Dict[str, Any]]:
    """
    Retrieve crop requirement data by name.

    Args:
        crop_name: Name of the crop (e.g., "Riceberry Rice", "Corn")

    Returns:
        Crop requirements dictionary or None if not found
    """
    return CROP_REQUIREMENTS.get(crop_name)


def get_all_crop_names() -> List[str]:
    """Return list of all available crop names."""
    return list(CROP_REQUIREMENTS.keys())


def get_crop_nutrient_requirements(crop_name: str) -> Optional[Dict[str, Any]]:
    """
    Get nutrient requirements for a specific crop.

    Args:
        crop_name: Name of the crop

    Returns:
        Nutrient requirements (N, P, K) in kg/rai
    """
    crop = CROP_REQUIREMENTS.get(crop_name)
    if crop:
        return crop.get("nutrient_requirements_kg_per_rai")
    return None


def get_crop_growth_stages(crop_name: str) -> Optional[Dict[str, Any]]:
    """
    Get growth stages for a specific crop.

    Args:
        crop_name: Name of the crop

    Returns:
        Growth stages dictionary
    """
    crop = CROP_REQUIREMENTS.get(crop_name)
    if crop:
        return crop.get("growth_stages")
    return None


# =============================================================================
# HELPER FUNCTIONS - FERTILIZERS
# =============================================================================

def get_fertilizers_by_type(fertilizer_type: str) -> List[Dict[str, Any]]:
    """
    Filter fertilizers by type.

    Args:
        fertilizer_type: Type of fertilizer (nitrogen, phosphorus, potassium, compound, organic)

    Returns:
        List of fertilizers matching the type
    """
    return [f for f in FERTILIZERS if f.get("type") == fertilizer_type]


def get_fertilizer_by_name(name: str) -> Optional[Dict[str, Any]]:
    """
    Get fertilizer data by name.

    Args:
        name: Name of the fertilizer

    Returns:
        Fertilizer data or None if not found
    """
    for f in FERTILIZERS:
        if f.get("name") == name or f.get("id") == name:
            return f
    return None


def get_fertilizer_by_formula(formula: str) -> Optional[Dict[str, Any]]:
    """
    Get fertilizer data by formula.

    Args:
        formula: NPK formula (e.g., "46-0-0", "15-15-15")

    Returns:
        Fertilizer data or None if not found
    """
    for f in FERTILIZERS:
        if f.get("formula") == formula:
            return f
    return None


def get_all_fertilizer_names() -> List[str]:
    """Return list of all fertilizer names."""
    return [f.get("name", "") for f in FERTILIZERS]


def get_organic_fertilizers() -> List[Dict[str, Any]]:
    """Get all organic fertilizers."""
    return get_fertilizers_by_type("organic")


def get_chemical_fertilizers() -> List[Dict[str, Any]]:
    """Get all non-organic fertilizers."""
    return [f for f in FERTILIZERS if f.get("type") != "organic"]


# =============================================================================
# HELPER FUNCTIONS - CLIMATE
# =============================================================================

def get_climate_data(location: str = "phrae_province") -> Optional[Dict[str, Any]]:
    """
    Get climate data for a location.

    Args:
        location: Location identifier

    Returns:
        Climate data dictionary
    """
    return CLIMATE_DATA.get(location)


def get_monthly_climate(month: int, location: str = "phrae_province") -> Optional[Dict[str, Any]]:
    """
    Get climate data for a specific month.

    Args:
        month: Month number (1-12)
        location: Location identifier

    Returns:
        Monthly climate data
    """
    climate = CLIMATE_DATA.get(location, {})
    monthly = climate.get("monthly_averages", {})
    return monthly.get(str(month))


# =============================================================================
# HELPER FUNCTIONS - DISTRICTS
# =============================================================================

def get_district_info(district_key: str) -> Optional[Dict[str, Any]]:
    """
    Get district information.

    Args:
        district_key: District identifier (e.g., "phrae_district")

    Returns:
        District data dictionary
    """
    return DISTRICTS.get(district_key)


def get_all_districts() -> Dict[str, Any]:
    """Get all district data."""
    return DISTRICTS


def get_district_coordinates(district_key: str) -> Optional[Dict[str, float]]:
    """
    Get coordinates for a district.

    Args:
        district_key: District identifier

    Returns:
        Dictionary with lat and lng
    """
    district = DISTRICTS.get(district_key)
    if district:
        return district.get("coordinates")
    return None


# =============================================================================
# DATA RELOAD FUNCTION
# =============================================================================

def reload_data():
    """
    Reload data from master_data.json.
    Useful when the JSON file has been updated.
    """
    global _MASTER_DATA, SOIL_SERIES, CROP_REQUIREMENTS, FERTILIZERS, CLIMATE_DATA, DISTRICTS

    _MASTER_DATA = _load_master_data()
    SOIL_SERIES = _MASTER_DATA.get("soil_series", {})
    CROP_REQUIREMENTS = _MASTER_DATA.get("crop_requirements", {})
    FERTILIZERS = _MASTER_DATA.get("fertilizers", [])
    CLIMATE_DATA = _MASTER_DATA.get("climate_data", {})
    DISTRICTS = _MASTER_DATA.get("districts", {})

    return True


# =============================================================================
# DATA VALIDATION
# =============================================================================

def validate_data() -> Dict[str, Any]:
    """
    Validate that all required data is loaded correctly.

    Returns:
        Dictionary with validation results
    """
    results = {
        "valid": True,
        "errors": [],
        "warnings": [],
        "summary": {}
    }

    # Check soil series
    if not SOIL_SERIES:
        results["errors"].append("No soil series data loaded")
        results["valid"] = False
    else:
        results["summary"]["soil_series_count"] = len(SOIL_SERIES)

    # Check crop requirements
    if not CROP_REQUIREMENTS:
        results["errors"].append("No crop requirements data loaded")
        results["valid"] = False
    else:
        results["summary"]["crop_count"] = len(CROP_REQUIREMENTS)

    # Check fertilizers
    if not FERTILIZERS:
        results["errors"].append("No fertilizer data loaded")
        results["valid"] = False
    else:
        results["summary"]["fertilizer_count"] = len(FERTILIZERS)

    # Check for required fields in soil series
    for name, data in SOIL_SERIES.items():
        if "typical_properties" not in data:
            results["warnings"].append(f"Soil series '{name}' missing typical_properties")

    # Check for required fields in crops
    for name, data in CROP_REQUIREMENTS.items():
        if "nutrient_requirements_kg_per_rai" not in data:
            results["warnings"].append(f"Crop '{name}' missing nutrient requirements")

    return results


# Auto-validate on import
_validation = validate_data()
if not _validation["valid"]:
    print(f"Knowledge Base Warning: {_validation['errors']}")
