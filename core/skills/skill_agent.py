"""
S.O.I.L.E.R. Skill-based Agent Wrappers

These agents wrap deterministic skills to integrate with the orchestrator pipeline.
All math is done by the skills; agents only format output.
"""

from datetime import datetime
from typing import Any, Dict
from dataclasses import dataclass

from core.skills.types import SoilInput, FertilizerInput
from core.skills.soil import soil_diagnosis
from core.skills.fertilizer import fertilizer_plan


@dataclass
class AgentResponse:
    """Standardized agent response format."""
    success: bool
    payload: Dict[str, Any]
    error_message: str = ""


class SkillBasedSoilChemistryAgent:
    """
    Skill-based soil chemistry agent.

    Uses deterministic soil_diagnosis() skill for all calculations.
    No LLM hallucination - all values are verifiable.
    """

    def __init__(self, verbose: bool = True):
        self.verbose = verbose
        self.agent_name = "SoilChemistryExpert"
        self.agent_name_th = "ผู้เชี่ยวชาญเคมีดิน (Skill-based)"

    def process(self, input_data: Dict[str, Any]) -> AgentResponse:
        """
        Process soil chemistry analysis using deterministic skill.

        Args:
            input_data: Dict with ph, nitrogen, phosphorus, potassium, etc.

        Returns:
            AgentResponse with diagnosis results
        """
        try:
            # Build skill input
            skill_input = SoilInput(
                ph=input_data.get("ph"),
                nitrogen=input_data.get("nitrogen"),
                phosphorus=input_data.get("phosphorus"),
                potassium=input_data.get("potassium"),
                organic_matter=input_data.get("organic_matter"),
                texture=input_data.get("texture"),
                ec=input_data.get("ec"),
                target_crop=input_data.get("target_crop"),
            )

            # Run deterministic skill
            result = soil_diagnosis(skill_input)

            # Build observation in Thai
            observation_parts = []
            if result.ph_status_th:
                observation_parts.append(f"ค่า pH: {result.ph_status_th}")
            if result.health_score:
                observation_parts.append(f"คะแนนสุขภาพดิน: {result.health_score:.0f}/100")
            if result.issues:
                observation_parts.append(f"พบปัญหา: {len(result.issues)} รายการ")
            if result.confidence < 1.0:
                observation_parts.append(f"ความเชื่อมั่น: {result.confidence*100:.0f}%")

            observation_th = " | ".join(observation_parts) if observation_parts else result.summary_th

            # Build payload in orchestrator-expected format
            payload = {
                "request_id": input_data.get("request_id", ""),
                "timestamp": datetime.now().isoformat(),
                "agent": self.agent_name,
                "agent_th": self.agent_name_th,

                # Core analysis results
                "health_score": result.health_score or 70,
                "ph_analysis": {
                    "value": input_data.get("ph"),
                    "status": result.ph_status.value if result.ph_status else "unknown",
                    "status_th": result.ph_status_th,
                    "score": result.ph_score,
                },
                "nutrient_analysis": {
                    "nitrogen": self._format_nutrient(result.nitrogen_analysis, "nitrogen", input_data.get("nitrogen")),
                    "phosphorus": self._format_nutrient(result.phosphorus_analysis, "phosphorus", input_data.get("phosphorus")),
                    "potassium": self._format_nutrient(result.potassium_analysis, "potassium", input_data.get("potassium")),
                },
                "issues": [
                    {
                        "code": issue.code,
                        "description": issue.description,
                        "description_th": issue.description_th,
                        "severity": issue.severity.value,
                        "affected_parameter": issue.affected_parameter,
                    }
                    for issue in result.issues
                ],
                "recommendations": [
                    {
                        "code": rec.code,
                        "action": rec.action,
                        "action_th": rec.action_th,
                        "priority": rec.priority,
                        "rationale": rec.rationale,
                    }
                    for rec in result.recommendations
                ],

                # Grounding metadata
                "grounded": True,
                "confidence": result.confidence,
                "inputs_provided": result.inputs_provided,
                "missing_fields": result.missing_fields,
                "assumptions": result.assumptions,
                "warnings": result.warnings,
                "disclaimers": [
                    "การวินิจฉัยนี้ใช้ค่ามาตรฐานจากกรมวิชาการเกษตร",
                    "ควรปรึกษาผู้เชี่ยวชาญก่อนดำเนินการจริง",
                ],

                # Thai observation for pipeline
                "observation_th": observation_th,
                "summary_th": result.summary_th,
            }

            return AgentResponse(success=True, payload=payload)

        except Exception as e:
            return AgentResponse(
                success=False,
                payload={},
                error_message=f"Soil diagnosis skill error: {str(e)}"
            )

    def _format_nutrient(self, analysis, name: str, value: float) -> Dict[str, Any]:
        """Format nutrient analysis for payload."""
        if analysis is None:
            return {"value": value, "status": "unknown", "status_th": "ไม่มีข้อมูล"}

        return {
            "value": analysis.value,
            "unit": analysis.unit,
            "level": analysis.level.value,
            "level_th": analysis.level_th,
            "optimal_range": list(analysis.optimal_range),
            "deficit_kg_per_rai": analysis.deficit_kg_per_rai,
        }


class SkillBasedFertilizerAgent:
    """
    Skill-based fertilizer planning agent.

    Uses deterministic fertilizer_plan() skill for all calculations.
    No LLM hallucination - all values are verifiable.
    """

    def __init__(self, verbose: bool = True):
        self.verbose = verbose
        self.agent_name = "FertilizerExpert"
        self.agent_name_th = "ผู้เชี่ยวชาญสูตรปุ๋ย (Skill-based)"

    def process(self, input_data: Dict[str, Any]) -> AgentResponse:
        """
        Process fertilizer planning using deterministic skill.

        Args:
            input_data: Dict with crop, field_size, soil values, etc.

        Returns:
            AgentResponse with fertilizer plan results
        """
        try:
            # Build skill input
            skill_input = FertilizerInput(
                crop=input_data.get("target_crop", "rice"),
                growth_stage=input_data.get("growth_stage"),
                field_size_rai=input_data.get("field_size_rai", 1.0),
                target_yield_kg_per_rai=input_data.get("target_yield"),
                budget_thb=input_data.get("budget_thb"),
                soil_ph=input_data.get("ph"),
                soil_n=input_data.get("nitrogen"),
                soil_p=input_data.get("phosphorus"),
                soil_k=input_data.get("potassium"),
                prefer_organic=input_data.get("prefer_organic", False),
                has_irrigation=input_data.get("irrigation_available", True),
            )

            # Run deterministic skill
            result = fertilizer_plan(skill_input)

            # Build observation in Thai
            observation_parts = [
                f"เป้าหมาย N-P-K: {result.target_n_kg_per_rai}-{result.target_p2o5_kg_per_rai}-{result.target_k2o_kg_per_rai} กก./ไร่",
            ]
            if result.fertilizer_options:
                rec = result.fertilizer_options[result.recommended_option_index]
                observation_parts.append(f"แนะนำ: {rec.name_th}")
                observation_parts.append(f"ค่าใช้จ่าย: {result.total_cost_thb:.0f} บาท")
            if result.confidence < 1.0:
                observation_parts.append(f"ความเชื่อมั่น: {result.confidence*100:.0f}%")

            observation_th = " | ".join(observation_parts)

            # Build payload in orchestrator-expected format
            payload = {
                "request_id": input_data.get("request_id", ""),
                "timestamp": datetime.now().isoformat(),
                "agent": self.agent_name,
                "agent_th": self.agent_name_th,

                # Nutrient targets
                "nutrient_targets": {
                    "n_kg_per_rai": result.target_n_kg_per_rai,
                    "p2o5_kg_per_rai": result.target_p2o5_kg_per_rai,
                    "k2o_kg_per_rai": result.target_k2o_kg_per_rai,
                },
                "calculation_method": result.calculation_method,
                "calculation_details": result.calculation_details,

                # Fertilizer options
                "fertilizer_options": [
                    {
                        "name": opt.name,
                        "name_th": opt.name_th,
                        "formula": opt.formula,
                        "rate_kg_per_rai": opt.rate_kg_per_rai,
                        "cost_per_kg": opt.cost_per_kg,
                        "total_cost": opt.total_cost,
                        "application_timing": opt.application_timing,
                        "application_timing_th": opt.application_timing_th,
                    }
                    for opt in result.fertilizer_options
                ],
                "recommended_option_index": result.recommended_option_index,

                # Cost analysis
                "cost_analysis": {
                    "total_cost": result.total_cost_thb,
                    "cost_per_rai": result.cost_per_rai_thb,
                    "within_budget": result.within_budget,
                },

                # Grounding metadata
                "grounded": True,
                "confidence": result.confidence,
                "inputs_provided": result.inputs_provided,
                "missing_fields": result.missing_fields,
                "assumptions": result.assumptions,
                "warnings": result.warnings,
                "disclaimers": result.disclaimers,

                # Thai observation for pipeline
                "observation_th": observation_th,
                "summary_th": result.summary_th,
            }

            return AgentResponse(success=True, payload=payload)

        except Exception as e:
            return AgentResponse(
                success=False,
                payload={},
                error_message=f"Fertilizer planning skill error: {str(e)}"
            )


def get_skill_based_agents(verbose: bool = True) -> Dict[str, Any]:
    """
    Get all skill-based agents.

    Returns:
        Dict mapping agent names to agent instances
    """
    return {
        "soil_chemistry": SkillBasedSoilChemistryAgent(verbose=verbose),
        "fertilizer": SkillBasedFertilizerAgent(verbose=verbose),
    }
