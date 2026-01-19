"""
S.O.I.L.E.R. Agents Package - Version 2.0
ระบบ Multi-Agent สำหรับการเกษตรอัจฉริยะ

Available Agents (9-Agent Architecture):
1. SoilSeriesAgent (ผู้เชี่ยวชาญชุดดิน) - Soil series identification
2. SoilChemistryAgent (ผู้เชี่ยวชาญเคมีดิน) - pH and nutrient analysis
3. CropBiologyAgent (ผู้เชี่ยวชาญชีววิทยาพืช) - Crop planning
4. PestDiseaseAgent (ผู้เชี่ยวชาญโรคและแมลง) - Pest/disease management
5. ClimateAgent (ผู้เชี่ยวชาญภูมิอากาศ) - Weather and climate analysis
6. FertilizerFormulaAgent (ผู้เชี่ยวชาญสูตรปุ๋ย) - Fertilizer recommendations
7. MarketCostAgent (ผู้เชี่ยวชาญตลาดและต้นทุน) - Market and cost analysis
8. ReportAgent (ผู้สรุปรายงาน) - Executive report compilation

Legacy Agents (Backward Compatibility):
- SoilAgent, CropAgent, EnvironmentAgent, FertilizerAgent, MarketAgent
"""

from agents.base_agent import BaseAgent

# New 9-Agent Architecture
from agents.soil_series_agent import SoilSeriesAgent
from agents.soil_chemistry_agent import SoilChemistryAgent
from agents.crop_biology_agent import CropBiologyAgent
from agents.pest_disease_agent import PestDiseaseAgent
from agents.climate_agent import ClimateAgent
from agents.fertilizer_formula_agent import FertilizerFormulaAgent
from agents.market_cost_agent import MarketCostAgent
from agents.report_agent import ReportAgent

# Legacy agents (backward compatibility)
from agents.soil_agent import SoilAgent
from agents.crop_agent import CropAgent
from agents.env_agent import EnvironmentAgent
from agents.fertilizer_agent import FertilizerAgent
from agents.market_agent import MarketAgent

__all__ = [
    # Base
    "BaseAgent",

    # New 9-Agent Architecture
    "SoilSeriesAgent",
    "SoilChemistryAgent",
    "CropBiologyAgent",
    "PestDiseaseAgent",
    "ClimateAgent",
    "FertilizerFormulaAgent",
    "MarketCostAgent",
    "ReportAgent",

    # Legacy (backward compatibility)
    "SoilAgent",
    "CropAgent",
    "EnvironmentAgent",
    "FertilizerAgent",
    "MarketAgent",
]
