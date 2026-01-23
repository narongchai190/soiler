"""
S.O.I.L.E.R. Skills Module

Deterministic tools for soil diagnosis and fertilizer planning.
These skills produce grounded, verifiable outputs without hallucination.
"""

from core.skills.types import (
    SoilInput,
    DiagnosisResult,
    FertilizerInput,
    FertilizerPlanResult,
    NutrientLevel,
    Issue,
    Recommendation,
)
from core.skills.soil import soil_diagnosis
from core.skills.fertilizer import fertilizer_plan
from core.skills.skill_agent import (
    SkillBasedSoilChemistryAgent,
    SkillBasedFertilizerAgent,
    get_skill_based_agents,
)

__all__ = [
    # Types
    "SoilInput",
    "DiagnosisResult",
    "FertilizerInput",
    "FertilizerPlanResult",
    "NutrientLevel",
    "Issue",
    "Recommendation",
    # Skills
    "soil_diagnosis",
    "fertilizer_plan",
    # Skill-based agents
    "SkillBasedSoilChemistryAgent",
    "SkillBasedFertilizerAgent",
    "get_skill_based_agents",
]
