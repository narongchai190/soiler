"""
S.O.I.L.E.R. Pydantic Schemas
Soil Optimization & Intelligent Land Expert Recommender

Type-safe data models for communication between agents.
"""

from datetime import datetime
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field, field_validator


# =============================================================================
# ENUMS
# =============================================================================

class SoilTexture(str, Enum):
    """Soil texture classifications."""
    SAND = "sand"
    LOAMY_SAND = "loamy sand"
    SANDY_LOAM = "sandy loam"
    LOAM = "loam"
    SILT_LOAM = "silt loam"
    SILT = "silt"
    SANDY_CLAY_LOAM = "sandy clay loam"
    CLAY_LOAM = "clay loam"
    SILTY_CLAY_LOAM = "silty clay loam"
    SANDY_CLAY = "sandy clay"
    SILTY_CLAY = "silty clay"
    CLAY = "clay"


class DrainageClass(str, Enum):
    """Soil drainage classifications."""
    VERY_POOR = "very poor"
    POOR = "poor"
    SLOW = "slow"
    MODERATE = "moderate"
    WELL_DRAINED = "well-drained"
    EXCESSIVE = "excessive"


class FertilityLevel(str, Enum):
    """Nutrient fertility level classifications."""
    VERY_LOW = "very low"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    VERY_HIGH = "very high"


class RecommendationPriority(str, Enum):
    """Priority levels for recommendations."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


# =============================================================================
# INPUT SCHEMAS
# =============================================================================

class NPKLevels(BaseModel):
    """Nitrogen, Phosphorus, and Potassium levels in soil."""
    nitrogen_mg_kg: float = Field(..., ge=0, description="Nitrogen content in mg/kg")
    phosphorus_mg_kg: float = Field(..., ge=0, description="Available phosphorus in mg/kg")
    potassium_mg_kg: float = Field(..., ge=0, description="Exchangeable potassium in mg/kg")


class SoilData(BaseModel):
    """
    Input model for soil analysis data.
    Used by agents to receive and validate soil test results.
    """
    sample_id: str = Field(..., min_length=1, description="Unique identifier for the soil sample")
    location: str = Field(..., description="Location or field identifier")
    collection_date: datetime = Field(default_factory=datetime.now, description="Date of sample collection")

    # Core soil properties
    ph: float = Field(..., ge=0, le=14, description="Soil pH value")
    organic_matter_percent: float = Field(..., ge=0, le=100, description="Organic matter percentage")

    # Nutrient levels
    npk: NPKLevels = Field(..., description="N-P-K nutrient levels")

    # Physical properties
    texture: SoilTexture = Field(..., description="Soil texture classification")
    sand_percent: Optional[float] = Field(None, ge=0, le=100, description="Sand content percentage")
    silt_percent: Optional[float] = Field(None, ge=0, le=100, description="Silt content percentage")
    clay_percent: Optional[float] = Field(None, ge=0, le=100, description="Clay content percentage")
    drainage: Optional[DrainageClass] = Field(None, description="Drainage class")

    # Optional properties
    cec_meq_100g: Optional[float] = Field(None, ge=0, description="Cation Exchange Capacity")
    soil_series: Optional[str] = Field(None, description="Identified soil series name")

    # Metadata
    notes: Optional[str] = Field(None, description="Additional notes about the sample")

    @field_validator('sand_percent', 'silt_percent', 'clay_percent')
    @classmethod
    def validate_texture_composition(cls, v):
        """Validate texture percentages are within bounds."""
        if v is not None and (v < 0 or v > 100):
            raise ValueError('Texture percentage must be between 0 and 100')
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "sample_id": "PH-2024-001",
                "location": "Den Chai District, Plot A",
                "ph": 6.2,
                "organic_matter_percent": 2.5,
                "npk": {
                    "nitrogen_mg_kg": 45,
                    "phosphorus_mg_kg": 28,
                    "potassium_mg_kg": 150
                },
                "texture": "clay loam",
                "drainage": "moderate",
                "soil_series": "Den Chai"
            }
        }


# =============================================================================
# ANALYSIS RESULT SCHEMAS
# =============================================================================

class NutrientStatus(BaseModel):
    """Status assessment for a single nutrient."""
    nutrient: str = Field(..., description="Name of the nutrient")
    current_level: float = Field(..., description="Current level in soil")
    unit: str = Field(default="mg/kg", description="Unit of measurement")
    status: FertilityLevel = Field(..., description="Fertility classification")
    deficiency_percent: Optional[float] = Field(None, description="Percentage deficiency from optimal")
    excess_percent: Optional[float] = Field(None, description="Percentage excess from optimal")


class SoilHealthIndicator(BaseModel):
    """Individual soil health metric."""
    indicator: str = Field(..., description="Name of the indicator")
    value: float = Field(..., description="Measured or calculated value")
    rating: str = Field(..., description="Qualitative rating (poor/fair/good/excellent)")
    description: str = Field(..., description="Explanation of the indicator status")


class AnalysisResult(BaseModel):
    """
    Output model for soil analysis results.
    Produced by the Soil Analysis Agent for consumption by other agents.
    """
    sample_id: str = Field(..., description="Reference to original soil sample")
    analysis_timestamp: datetime = Field(default_factory=datetime.now, description="When analysis was performed")

    # Soil identification
    identified_soil_series: Optional[str] = Field(None, description="Matched soil series from knowledge base")
    series_match_confidence: Optional[float] = Field(None, ge=0, le=1, description="Confidence of series identification")

    # pH Analysis
    ph_status: str = Field(..., description="pH classification (acidic/neutral/alkaline)")
    ph_suitability: str = Field(..., description="Suitability assessment for target crop")
    lime_recommendation_kg_per_rai: Optional[float] = Field(None, ge=0, description="Lime needed if pH too low")
    sulfur_recommendation_kg_per_rai: Optional[float] = Field(None, ge=0, description="Sulfur needed if pH too high")

    # Nutrient Analysis
    nutrient_status: List[NutrientStatus] = Field(..., description="Status of each analyzed nutrient")

    # Overall Assessment
    soil_health_score: float = Field(..., ge=0, le=100, description="Overall soil health score (0-100)")
    health_indicators: List[SoilHealthIndicator] = Field(default=[], description="Detailed health indicators")

    # Crop suitability
    target_crop: Optional[str] = Field(None, description="Target crop for analysis")
    crop_suitability_score: Optional[float] = Field(None, ge=0, le=100, description="Suitability for target crop")

    # Key findings
    critical_issues: List[str] = Field(default=[], description="Critical issues requiring immediate attention")
    recommendations_summary: List[str] = Field(default=[], description="Summary of key recommendations")

    class Config:
        json_schema_extra = {
            "example": {
                "sample_id": "PH-2024-001",
                "identified_soil_series": "Den Chai",
                "series_match_confidence": 0.85,
                "ph_status": "slightly acidic",
                "ph_suitability": "suitable for rice cultivation",
                "nutrient_status": [
                    {
                        "nutrient": "Nitrogen",
                        "current_level": 45,
                        "unit": "mg/kg",
                        "status": "medium",
                        "deficiency_percent": 10
                    }
                ],
                "soil_health_score": 72.5,
                "target_crop": "Riceberry Rice",
                "crop_suitability_score": 85.0,
                "critical_issues": [],
                "recommendations_summary": ["Apply nitrogen fertilizer at tillering stage"]
            }
        }


# =============================================================================
# FERTILIZER RECOMMENDATION SCHEMAS
# =============================================================================

class FertilizerApplication(BaseModel):
    """Details for a single fertilizer application."""
    fertilizer_name: str = Field(..., description="Name of the fertilizer product")
    formula: str = Field(..., description="N-P-K formula (e.g., '46-0-0')")
    amount_kg_per_rai: float = Field(..., ge=0, description="Application rate in kg per rai")
    application_stage: str = Field(..., description="Growth stage for application")
    application_method: str = Field(..., description="How to apply the fertilizer")
    timing_description: str = Field(..., description="When to apply relative to planting")
    notes: Optional[str] = Field(None, description="Additional application notes")


class CostEstimate(BaseModel):
    """Cost breakdown for fertilizer recommendation."""
    fertilizer_name: str = Field(..., description="Fertilizer product name")
    quantity_kg: float = Field(..., ge=0, description="Total quantity needed")
    unit_price_thb: float = Field(..., ge=0, description="Price per kg in THB")
    total_cost_thb: float = Field(..., ge=0, description="Total cost in THB")


class FertilizerRecommendation(BaseModel):
    """
    Complete fertilizer recommendation for a field.
    Produced by the Fertilizer Recommendation Agent.
    """
    recommendation_id: str = Field(..., description="Unique recommendation identifier")
    sample_id: str = Field(..., description="Reference to soil sample")
    created_at: datetime = Field(default_factory=datetime.now, description="Recommendation creation time")

    # Context
    target_crop: str = Field(..., description="Crop for which recommendation is made")
    field_size_rai: float = Field(..., gt=0, description="Field size in rai")
    target_yield_kg_per_rai: Optional[float] = Field(None, description="Expected yield target")

    # Nutrient requirements
    total_n_required_kg: float = Field(..., ge=0, description="Total nitrogen required")
    total_p2o5_required_kg: float = Field(..., ge=0, description="Total P2O5 required")
    total_k2o_required_kg: float = Field(..., ge=0, description="Total K2O required")

    # Application schedule
    applications: List[FertilizerApplication] = Field(..., description="Scheduled fertilizer applications")

    # Cost analysis
    cost_breakdown: List[CostEstimate] = Field(default=[], description="Cost breakdown by fertilizer")
    total_estimated_cost_thb: float = Field(..., ge=0, description="Total estimated cost in THB")
    cost_per_rai_thb: float = Field(..., ge=0, description="Cost per rai in THB")

    # Priority and confidence
    recommendation_priority: RecommendationPriority = Field(..., description="Priority level of recommendation")
    confidence_score: float = Field(..., ge=0, le=1, description="Confidence in the recommendation")

    # Additional guidance
    organic_alternatives: Optional[List[str]] = Field(None, description="Organic fertilizer alternatives")
    environmental_notes: Optional[List[str]] = Field(None, description="Environmental considerations")
    warnings: List[str] = Field(default=[], description="Warnings or cautions")

    class Config:
        json_schema_extra = {
            "example": {
                "recommendation_id": "REC-2024-001",
                "sample_id": "PH-2024-001",
                "target_crop": "Riceberry Rice",
                "field_size_rai": 5.0,
                "target_yield_kg_per_rai": 450,
                "total_n_required_kg": 60,
                "total_p2o5_required_kg": 30,
                "total_k2o_required_kg": 40,
                "applications": [
                    {
                        "fertilizer_name": "NPK 16-20-0",
                        "formula": "16-20-0",
                        "amount_kg_per_rai": 25,
                        "application_stage": "basal",
                        "application_method": "broadcast and incorporate",
                        "timing_description": "Before transplanting"
                    }
                ],
                "total_estimated_cost_thb": 2500,
                "cost_per_rai_thb": 500,
                "recommendation_priority": "high",
                "confidence_score": 0.88
            }
        }


# =============================================================================
# INTER-AGENT MESSAGE SCHEMAS
# =============================================================================

class AgentRequest(BaseModel):
    """Base model for requests between agents."""
    request_id: str = Field(..., description="Unique request identifier")
    source_agent: str = Field(..., description="Agent making the request")
    target_agent: str = Field(..., description="Agent to handle the request")
    timestamp: datetime = Field(default_factory=datetime.now)
    payload: dict = Field(default={}, description="Request-specific data")


class AgentResponse(BaseModel):
    """Base model for responses between agents."""
    request_id: str = Field(..., description="Reference to original request")
    responding_agent: str = Field(..., description="Agent providing the response")
    timestamp: datetime = Field(default_factory=datetime.now)
    success: bool = Field(..., description="Whether the request was successful")
    error_message: Optional[str] = Field(None, description="Error details if unsuccessful")
    payload: dict = Field(default={}, description="Response-specific data")
