"""
S.O.I.L.E.R. Skills Type Definitions

Pydantic models for skill inputs and outputs.
All outputs are deterministic and verifiable.
"""

from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field


class NutrientLevel(str, Enum):
    """Nutrient level classification."""
    VERY_LOW = "very_low"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    VERY_HIGH = "very_high"


class PHStatus(str, Enum):
    """Soil pH status classification."""
    VERY_ACIDIC = "very_acidic"  # < 4.5
    ACIDIC = "acidic"            # 4.5 - 5.5
    SLIGHTLY_ACIDIC = "slightly_acidic"  # 5.5 - 6.0
    OPTIMAL = "optimal"          # 6.0 - 7.0
    SLIGHTLY_ALKALINE = "slightly_alkaline"  # 7.0 - 7.5
    ALKALINE = "alkaline"        # 7.5 - 8.5
    VERY_ALKALINE = "very_alkaline"  # > 8.5


class Severity(str, Enum):
    """Issue severity level."""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


class Issue(BaseModel):
    """Identified soil or nutrient issue."""
    code: str = Field(..., description="Issue code (e.g., 'PH_LOW')")
    description: str = Field(..., description="Human-readable description")
    description_th: str = Field(..., description="Thai description")
    severity: Severity = Field(..., description="Issue severity")
    affected_parameter: str = Field(..., description="Parameter affected (e.g., 'pH', 'nitrogen')")


class Recommendation(BaseModel):
    """Recommendation for soil improvement."""
    code: str = Field(..., description="Recommendation code")
    action: str = Field(..., description="Action to take")
    action_th: str = Field(..., description="Thai action description")
    priority: int = Field(..., ge=1, le=5, description="Priority 1-5 (1=highest)")
    rationale: str = Field(..., description="Why this recommendation")


class SoilInput(BaseModel):
    """Input for soil diagnosis skill."""
    ph: Optional[float] = Field(None, ge=0, le=14, description="Soil pH value")
    nitrogen: Optional[float] = Field(None, ge=0, description="Nitrogen content (mg/kg)")
    phosphorus: Optional[float] = Field(None, ge=0, description="Available phosphorus (mg/kg)")
    potassium: Optional[float] = Field(None, ge=0, description="Exchangeable potassium (mg/kg)")
    organic_matter: Optional[float] = Field(None, ge=0, le=100, description="Organic matter (%)")
    texture: Optional[str] = Field(None, description="Soil texture (clay/loam/sand)")
    ec: Optional[float] = Field(None, ge=0, description="Electrical conductivity (dS/m)")
    target_crop: Optional[str] = Field(None, description="Target crop for recommendations")


class NutrientAnalysis(BaseModel):
    """Analysis of a single nutrient."""
    value: Optional[float] = Field(None, description="Measured value")
    unit: str = Field("mg/kg", description="Unit of measurement")
    level: NutrientLevel = Field(..., description="Classified level")
    level_th: str = Field(..., description="Thai level description")
    optimal_range: tuple = Field(..., description="Optimal range (min, max)")
    deficit_kg_per_rai: Optional[float] = Field(None, description="Deficit in kg/rai if below optimal")


class DiagnosisResult(BaseModel):
    """Result of soil diagnosis skill."""
    # Input validation
    inputs_provided: List[str] = Field(default_factory=list, description="Which inputs were provided")
    missing_fields: List[str] = Field(default_factory=list, description="Critical missing inputs")

    # pH Analysis
    ph_status: Optional[PHStatus] = Field(None, description="pH classification")
    ph_status_th: Optional[str] = Field(None, description="Thai pH status")
    ph_score: Optional[float] = Field(None, ge=0, le=100, description="pH score out of 100")

    # Nutrient Analysis
    nitrogen_analysis: Optional[NutrientAnalysis] = Field(None)
    phosphorus_analysis: Optional[NutrientAnalysis] = Field(None)
    potassium_analysis: Optional[NutrientAnalysis] = Field(None)

    # Overall Assessment
    health_score: Optional[float] = Field(None, ge=0, le=100, description="Overall soil health score")
    issues: List[Issue] = Field(default_factory=list, description="Identified issues")
    recommendations: List[Recommendation] = Field(default_factory=list, description="Recommendations")

    # Grounding
    confidence: float = Field(1.0, ge=0, le=1, description="Confidence in diagnosis (1.0 if all inputs)")
    assumptions: List[str] = Field(default_factory=list, description="Assumptions made due to missing data")
    warnings: List[str] = Field(default_factory=list, description="Warnings about limitations")

    # Summary
    summary_th: str = Field("", description="Thai summary of diagnosis")


class FertilizerOption(BaseModel):
    """A fertilizer option in the plan."""
    name: str = Field(..., description="Fertilizer name")
    name_th: str = Field(..., description="Thai name")
    formula: str = Field(..., description="N-P-K formula (e.g., '16-20-0')")
    rate_kg_per_rai: float = Field(..., ge=0, description="Application rate kg/rai")
    cost_per_kg: float = Field(..., ge=0, description="Cost per kg in THB")
    total_cost: float = Field(..., ge=0, description="Total cost for field")
    application_timing: str = Field(..., description="When to apply")
    application_timing_th: str = Field(..., description="Thai timing description")


class FertilizerInput(BaseModel):
    """Input for fertilizer planning skill."""
    crop: str = Field(..., description="Target crop name")
    growth_stage: Optional[str] = Field(None, description="Current growth stage")
    field_size_rai: float = Field(1.0, gt=0, description="Field size in rai")
    target_yield_kg_per_rai: Optional[float] = Field(None, description="Target yield")
    budget_thb: Optional[float] = Field(None, ge=0, description="Budget constraint")

    # From soil diagnosis
    soil_ph: Optional[float] = Field(None, description="Soil pH")
    soil_n: Optional[float] = Field(None, description="Current soil N (mg/kg)")
    soil_p: Optional[float] = Field(None, description="Current soil P (mg/kg)")
    soil_k: Optional[float] = Field(None, description="Current soil K (mg/kg)")

    # Preferences
    prefer_organic: bool = Field(False, description="Prefer organic options")
    has_irrigation: bool = Field(True, description="Irrigation available")


class FertilizerPlanResult(BaseModel):
    """Result of fertilizer planning skill."""
    # Input validation
    inputs_provided: List[str] = Field(default_factory=list)
    missing_fields: List[str] = Field(default_factory=list)

    # Nutrient targets
    target_n_kg_per_rai: float = Field(..., description="Target N application kg/rai")
    target_p2o5_kg_per_rai: float = Field(..., description="Target P2O5 application kg/rai")
    target_k2o_kg_per_rai: float = Field(..., description="Target K2O application kg/rai")

    # Calculation breakdown
    calculation_method: str = Field(..., description="How targets were calculated")
    calculation_details: dict = Field(default_factory=dict, description="Detailed calculation")

    # Recommendations
    fertilizer_options: List[FertilizerOption] = Field(default_factory=list)
    recommended_option_index: int = Field(0, description="Index of recommended option")

    # Cost analysis
    total_cost_thb: float = Field(..., ge=0)
    cost_per_rai_thb: float = Field(..., ge=0)
    within_budget: bool = Field(True)

    # Grounding
    confidence: float = Field(1.0, ge=0, le=1)
    assumptions: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
    disclaimers: List[str] = Field(default_factory=list, description="Important caveats")

    # Summary
    summary_th: str = Field("", description="Thai summary")
