"""
S.O.I.L.E.R. Fertilizer Recommendation Agent
Generates specific fertilizer recommendations based on soil analysis and crop needs.
"""

from datetime import datetime
from typing import Any, Dict, List
import uuid

from agents.base_agent import BaseAgent
from core.schemas import RecommendationPriority
from data.knowledge_base import CROP_REQUIREMENTS, FERTILIZERS
from utils.calculator import (
    calculate_fertilizer_amounts,
    calculate_nutrient_gap,
    calculate_total_cost,
)


class FertilizerAgent(BaseAgent):
    """
    Fertilizer Recommendation Agent - Generates optimized fertilizer plans.

    Responsibilities:
    - Calculate nutrient gaps based on soil analysis
    - Select appropriate fertilizers from knowledge base
    - Create application schedule by growth stage
    - Calculate costs and provide budget analysis
    - Suggest organic alternatives when available
    """

    def __init__(self, verbose: bool = True):
        super().__init__(agent_name="FertilizerAdvisor", verbose=verbose)

    def _execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute fertilizer recommendation.

        Args:
            input_data: Dictionary containing:
                - sample_id: str
                - target_crop: str
                - field_size_rai: float
                - soil_analysis: dict (from SoilAgent)
                - current_npk: dict with nitrogen, phosphorus, potassium
                - budget_thb: float (optional)
                - prefer_organic: bool (optional)

        Returns:
            Fertilizer recommendation dictionary
        """
        self.think("Analyzing soil data and crop requirements...")

        sample_id = input_data.get("sample_id", "UNKNOWN")
        target_crop = input_data.get("target_crop", "Riceberry Rice")
        field_size_rai = input_data.get("field_size_rai", 1.0)
        current_npk = input_data.get("current_npk", {})
        budget_thb = input_data.get("budget_thb")
        prefer_organic = input_data.get("prefer_organic", False)
        soil_analysis = input_data.get("soil_analysis", {})

        # Validate crop
        if target_crop not in CROP_REQUIREMENTS:
            self.log_error(f"Unknown crop: {target_crop}")
            raise ValueError(f"Unknown crop: {target_crop}. Available: {list(CROP_REQUIREMENTS.keys())}")

        crop_data = CROP_REQUIREMENTS[target_crop]
        self.log_action(f"Target crop: {target_crop} ({crop_data['growth_cycle_days']} day cycle)")

        # Step 1: Calculate nutrient gaps
        self.think("Calculating nutrient deficiencies...")
        nutrient_gaps = calculate_nutrient_gap(
            current_npk=current_npk,
            crop_name=target_crop,
            field_size_rai=field_size_rai
        )

        self.log_result(f"N gap: {nutrient_gaps['nitrogen_gap_kg']} kg")
        self.log_result(f"P₂O₅ gap: {nutrient_gaps['p2o5_gap_kg']} kg")
        self.log_result(f"K₂O gap: {nutrient_gaps['k2o_gap_kg']} kg")

        # Step 2: Calculate fertilizer amounts
        self.think("Selecting optimal fertilizer combinations...")
        fertilizer_recs = calculate_fertilizer_amounts(nutrient_gaps)

        for rec in fertilizer_recs:
            self.log_action(
                f"Selected: {rec['fertilizer']['name']} - "
                f"{rec['amount_per_rai_kg']} kg/rai at {rec['application_stage']}"
            )

        # Step 3: Calculate costs
        self.think("Calculating cost estimates...")
        cost_analysis = calculate_total_cost(fertilizer_recs)
        cost_per_rai = cost_analysis["total_cost_thb"] / field_size_rai if field_size_rai > 0 else 0

        self.log_result(f"Total cost: {cost_analysis['total_cost_thb']:.2f} THB")
        self.log_result(f"Cost per rai: {cost_per_rai:.2f} THB/rai")

        # Step 4: Build application schedule
        self.think("Creating application schedule...")
        applications = self._build_application_schedule(fertilizer_recs, target_crop)

        # Step 5: Check budget constraints
        budget_status = None
        if budget_thb:
            self.think(f"Checking against budget of {budget_thb} THB...")
            if cost_analysis["total_cost_thb"] > budget_thb:
                self.log_warning(f"Recommendation exceeds budget by {cost_analysis['total_cost_thb'] - budget_thb:.2f} THB")
                budget_status = "over_budget"
                # Could implement budget-constrained optimization here
            else:
                budget_status = "within_budget"
                self.log_result("Recommendation is within budget")

        # Step 6: Generate organic alternatives
        organic_alternatives = []
        if prefer_organic:
            self.think("Finding organic alternatives...")
            organic_alternatives = self._get_organic_alternatives(nutrient_gaps)
            for alt in organic_alternatives:
                self.log_action(f"Organic option: {alt}")

        # Step 7: Determine priority
        priority = self._determine_priority(nutrient_gaps, soil_analysis)
        self.log_result(f"Recommendation priority: {priority}")

        # Step 8: Generate warnings and environmental notes
        warnings = self._generate_warnings(fertilizer_recs, target_crop)
        environmental_notes = self._generate_environmental_notes(fertilizer_recs)

        # Build recommendation
        recommendation_id = f"REC-{datetime.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}"

        result = {
            "recommendation_id": recommendation_id,
            "sample_id": sample_id,
            "target_crop": target_crop,
            "field_size_rai": field_size_rai,
            "target_yield_kg_per_rai": crop_data["yield_potential_kg_per_rai"]["average"],

            # Nutrient requirements
            "nutrient_gaps": nutrient_gaps,
            "total_n_required_kg": nutrient_gaps["nitrogen_gap_kg"],
            "total_p2o5_required_kg": nutrient_gaps["p2o5_gap_kg"],
            "total_k2o_required_kg": nutrient_gaps["k2o_gap_kg"],

            # Fertilizer applications
            "applications": applications,

            # Cost analysis
            "cost_breakdown": cost_analysis["breakdown"],
            "total_estimated_cost_thb": cost_analysis["total_cost_thb"],
            "cost_per_rai_thb": round(cost_per_rai, 2),
            "budget_status": budget_status,

            # Priority and confidence
            "recommendation_priority": priority,
            "confidence_score": self._calculate_confidence(nutrient_gaps, fertilizer_recs),

            # Additional guidance
            "organic_alternatives": organic_alternatives if organic_alternatives else None,
            "environmental_notes": environmental_notes,
            "warnings": warnings,

            # Yield projection
            "expected_yield_improvement": self._estimate_yield_improvement(nutrient_gaps),
        }

        return result

    def _build_application_schedule(
        self,
        fertilizer_recs: List[Dict[str, Any]],
        target_crop: str
    ) -> List[Dict[str, Any]]:
        """Build detailed application schedule."""
        crop = CROP_REQUIREMENTS.get(target_crop, {})
        growth_stages = crop.get("growth_stages", {})

        applications = []
        for rec in fertilizer_recs:
            fert = rec["fertilizer"]

            # Determine timing based on fertilizer type and crop
            if rec["application_stage"] == "basal":
                timing = "1-2 days before transplanting" if "Rice" in target_crop else "At planting"
                days_after_planting = 0
            elif rec["application_stage"] == "top-dress":
                timing = rec["timing"]
                days_after_planting = 25  # Approximate
            else:
                timing = rec["timing"]
                days_after_planting = 0

            applications.append({
                "fertilizer_name": fert["name"],
                "formula": fert["formula"],
                "amount_kg_per_rai": rec["amount_per_rai_kg"],
                "total_amount_kg": rec["amount_kg"],
                "application_stage": rec["application_stage"],
                "application_method": fert.get("application_method", "broadcast"),
                "timing_description": timing,
                "days_after_planting": days_after_planting,
                "nutrients_provided": rec["nutrients_provided"],
                "notes": fert.get("notes", "")
            })

        # Sort by application timing
        applications.sort(key=lambda x: x["days_after_planting"])

        return applications

    def _get_organic_alternatives(self, nutrient_gaps: Dict[str, float]) -> List[str]:
        """Get organic fertilizer alternatives."""
        alternatives = []

        # Find organic fertilizers
        organic_ferts = [f for f in FERTILIZERS if f["type"] == "organic"]

        for fert in organic_ferts:
            npk = fert["npk_ratio"]
            if npk["N"] > 0 and nutrient_gaps["nitrogen_gap_kg"] > 0:
                # Calculate required amount
                n_content = npk["N"] / 100
                amount_needed = nutrient_gaps["nitrogen_gap_kg"] / n_content if n_content > 0 else 0
                alternatives.append(
                    f"{fert['name']}: ~{amount_needed:.0f} kg/rai "
                    f"(provides N-P-K slowly, improves soil structure)"
                )

        if not alternatives:
            alternatives.append("Compost at 500-1000 kg/rai as soil amendment")
            alternatives.append("Green manure cover crops in off-season")

        return alternatives

    def _determine_priority(
        self,
        nutrient_gaps: Dict[str, float],
        soil_analysis: Dict[str, Any]
    ) -> str:
        """Determine recommendation priority level."""
        # Check for critical deficiencies
        critical_issues = soil_analysis.get("critical_issues", [])

        if critical_issues:
            return RecommendationPriority.CRITICAL.value

        # High priority if large nutrient gaps
        total_gap = (
            nutrient_gaps["nitrogen_gap_kg"] +
            nutrient_gaps["p2o5_gap_kg"] +
            nutrient_gaps["k2o_gap_kg"]
        )

        if total_gap > 50:
            return RecommendationPriority.HIGH.value
        elif total_gap > 25:
            return RecommendationPriority.MEDIUM.value
        else:
            return RecommendationPriority.LOW.value

    def _calculate_confidence(
        self,
        nutrient_gaps: Dict[str, float],
        fertilizer_recs: List[Dict[str, Any]]
    ) -> float:
        """Calculate confidence score for the recommendation."""
        # Start with base confidence
        confidence = 0.85

        # Reduce if very large gaps (harder to optimize)
        total_gap = (
            nutrient_gaps["nitrogen_gap_kg"] +
            nutrient_gaps["p2o5_gap_kg"] +
            nutrient_gaps["k2o_gap_kg"]
        )
        if total_gap > 100:
            confidence -= 0.1
        elif total_gap > 50:
            confidence -= 0.05

        # Increase if using well-matched fertilizers
        if len(fertilizer_recs) <= 3:
            confidence += 0.05

        return min(0.95, max(0.5, confidence))

    def _generate_warnings(
        self,
        fertilizer_recs: List[Dict[str, Any]],
        target_crop: str
    ) -> List[str]:
        """Generate warnings for the recommendation."""
        warnings = []

        for rec in fertilizer_recs:
            fert = rec["fertilizer"]

            # Urea volatilization warning
            if fert["formula"] == "46-0-0":
                warnings.append(
                    "Urea: Apply in cool conditions or incorporate immediately "
                    "to prevent nitrogen loss through volatilization"
                )

            # High application rate warning
            if rec["amount_per_rai_kg"] > 50:
                warnings.append(
                    f"{fert['name']}: High application rate - consider splitting "
                    "into multiple applications"
                )

        # Crop-specific warnings
        if "Rice" in target_crop:
            warnings.append(
                "For flooded rice: Apply nitrogen fertilizer when field is drained "
                "or has shallow water to reduce losses"
            )

        return warnings

    def _generate_environmental_notes(
        self,
        fertilizer_recs: List[Dict[str, Any]]
    ) -> List[str]:
        """Generate environmental considerations."""
        notes = [
            "Avoid application before heavy rainfall to prevent runoff",
            "Maintain buffer zones near water bodies",
            "Store fertilizers in dry, covered areas away from water sources",
        ]

        # Check for high nitrogen application
        total_n = sum(
            rec["nutrients_provided"]["N"]
            for rec in fertilizer_recs
        )
        if total_n > 20:
            notes.append(
                "High nitrogen application: Split into multiple doses to "
                "improve efficiency and reduce environmental impact"
            )

        return notes

    def _estimate_yield_improvement(self, nutrient_gaps: Dict[str, float]) -> Dict[str, Any]:
        """Estimate potential yield improvement from fertilization."""
        # Simplified yield response model
        # Assumes linear response up to a point

        n_factor = nutrient_gaps.get("soil_n_factor", 0.5)
        p_factor = nutrient_gaps.get("soil_p_factor", 0.5)
        k_factor = nutrient_gaps.get("soil_k_factor", 0.5)

        # Average deficiency factor
        avg_deficiency = (n_factor + p_factor + k_factor) / 3

        # Estimate improvement (very simplified)
        if avg_deficiency > 0.7:
            improvement_pct = 30
            assessment = "significant improvement expected"
        elif avg_deficiency > 0.4:
            improvement_pct = 20
            assessment = "moderate improvement expected"
        else:
            improvement_pct = 10
            assessment = "maintenance level - soil already has good fertility"

        return {
            "estimated_improvement_percent": improvement_pct,
            "assessment": assessment,
            "note": "Actual results depend on weather, water management, and pest control"
        }
