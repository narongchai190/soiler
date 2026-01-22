"""
S.O.I.L.E.R. Crop Expert Agent
Analyzes crop growth stages, water requirements, and yield optimization.
"""

from datetime import datetime, timedelta
from typing import Any, Dict, List

from agents.base_agent import BaseAgent
from data.knowledge_base import CROP_REQUIREMENTS


class CropAgent(BaseAgent):
    """
    Crop Expert Agent - Provides crop-specific guidance and yield optimization.

    Responsibilities:
    - Analyze crop growth stages and timing
    - Calculate water requirements
    - Set realistic yield targets based on conditions
    - Provide growth stage-specific recommendations
    - Identify critical periods for crop management
    """

    def __init__(self, verbose: bool = True):
        super().__init__(agent_name="CropExpert", verbose=verbose)

    def _execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute crop analysis.

        Args:
            input_data: Dictionary containing:
                - target_crop: str
                - planting_date: str (optional, ISO format)
                - soil_analysis: dict (from SoilAgent)
                - field_size_rai: float
                - irrigation_available: bool (optional)

        Returns:
            Crop analysis and recommendations
        """
        self.think("Analyzing crop requirements and growth parameters...")

        target_crop = input_data.get("target_crop", "Riceberry Rice")
        planting_date_str = input_data.get("planting_date")
        soil_analysis = input_data.get("soil_analysis", {})
        field_size_rai = input_data.get("field_size_rai", 1.0)
        irrigation_available = input_data.get("irrigation_available", True)

        # Validate crop
        if target_crop not in CROP_REQUIREMENTS:
            self.log_error(f"Unknown crop: {target_crop}")
            raise ValueError(f"Unknown crop: {target_crop}")

        crop_data = CROP_REQUIREMENTS[target_crop]
        self.log_action(f"Loading requirements for {target_crop}")

        # Parse planting date
        if planting_date_str:
            planting_date = datetime.fromisoformat(planting_date_str)
        else:
            planting_date = datetime.now() + timedelta(days=14)  # Assume 2 weeks from now
            self.think("No planting date provided, assuming 2 weeks from now")

        # Step 1: Analyze growth stages
        self.think("Mapping growth stages and critical periods...")
        growth_calendar = self._build_growth_calendar(crop_data, planting_date)
        self.log_result(f"Growth cycle: {crop_data['growth_cycle_days']} days")

        # Step 2: Calculate water requirements
        self.think("Calculating water requirements...")
        water_analysis = self._analyze_water_requirements(
            crop_data, field_size_rai, irrigation_available
        )
        self.log_result(f"Total water need: {water_analysis['total_water_mm']} mm")

        # Step 3: Determine yield targets
        self.think("Setting yield targets based on soil conditions...")
        yield_targets = self._calculate_yield_targets(
            crop_data, soil_analysis, irrigation_available
        )
        self.log_result(f"Target yield: {yield_targets['target_kg_per_rai']} kg/rai")

        # Step 4: Generate growth stage recommendations
        self.think("Generating stage-specific management recommendations...")
        stage_recommendations = self._generate_stage_recommendations(
            crop_data, target_crop, soil_analysis
        )

        # Step 5: Identify critical management periods
        self.think("Identifying critical management windows...")
        critical_periods = self._identify_critical_periods(crop_data, planting_date)

        # Step 6: Calculate input requirements
        self.think("Estimating total input requirements...")
        input_requirements = self._calculate_input_requirements(
            crop_data, field_size_rai, yield_targets
        )

        # Build result
        result = {
            "crop_name": target_crop,
            "scientific_name": crop_data.get("scientific_name"),
            "crop_code": crop_data.get("crop_code"),

            # Timing
            "planting_date": planting_date.isoformat(),
            "expected_harvest_date": (planting_date + timedelta(days=crop_data["growth_cycle_days"])).isoformat(),
            "growth_cycle_days": crop_data["growth_cycle_days"],

            # Growth calendar
            "growth_calendar": growth_calendar,
            "critical_periods": critical_periods,

            # Water management
            "water_requirements": water_analysis,

            # Yield
            "yield_targets": yield_targets,
            "total_expected_yield_kg": yield_targets["target_kg_per_rai"] * field_size_rai,

            # Recommendations
            "stage_recommendations": stage_recommendations,
            "input_requirements": input_requirements,

            # Special notes from knowledge base
            "special_notes": crop_data.get("special_notes", []),

            # Observation for next agent
            "observation": self._generate_observation(
                target_crop, yield_targets, water_analysis, critical_periods
            )
        }

        return result

    def _build_growth_calendar(
        self,
        crop_data: Dict[str, Any],
        planting_date: datetime
    ) -> List[Dict[str, Any]]:
        """Build detailed growth stage calendar."""
        calendar = []
        current_date = planting_date
        cumulative_days = 0

        for stage_name, stage_info in crop_data.get("growth_stages", {}).items():
            stage_days = stage_info["days"]
            start_date = current_date
            end_date = current_date + timedelta(days=stage_days)

            calendar.append({
                "stage": stage_name,
                "description": stage_info["description"],
                "duration_days": stage_days,
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
                "day_start": cumulative_days,
                "day_end": cumulative_days + stage_days,
                "key_activities": self._get_stage_activities(stage_name, crop_data)
            })

            current_date = end_date
            cumulative_days += stage_days

        return calendar

    def _get_stage_activities(self, stage_name: str, crop_data: Dict[str, Any]) -> List[str]:
        """Get key activities for each growth stage."""
        activities = {
            "seedling": [
                "Prepare nursery bed or seedling trays",
                "Maintain adequate moisture",
                "Monitor for seedling diseases",
                "Apply starter fertilizer if needed"
            ],
            "emergence": [
                "Ensure adequate soil moisture for germination",
                "Monitor for pest damage to emerging seedlings",
                "Check plant population and consider replanting gaps"
            ],
            "vegetative": [
                "Apply first nitrogen top-dress",
                "Monitor water levels (flooded for rice)",
                "Scout for pests and diseases",
                "Control weeds before canopy closure"
            ],
            "reproductive": [
                "Apply second nitrogen split",
                "Maintain optimal water supply",
                "Monitor for flowering-stage pests",
                "Apply potassium for grain filling"
            ],
            "ripening": [
                "Reduce water (drain field for rice)",
                "Monitor grain moisture content",
                "Prepare harvesting equipment",
                "Plan post-harvest handling"
            ],
            "maturity": [
                "Check grain moisture for harvest readiness",
                "Harvest at optimal moisture (14-18%)",
                "Dry grains properly to prevent spoilage"
            ]
        }

        return activities.get(stage_name, ["Monitor crop development", "Scout for issues"])

    def _analyze_water_requirements(
        self,
        crop_data: Dict[str, Any],
        field_size_rai: float,
        irrigation_available: bool
    ) -> Dict[str, Any]:
        """Analyze water requirements for the crop."""
        total_water_mm = crop_data.get("water_requirement_mm", 500)

        # Convert to cubic meters (1mm over 1 rai = 1.6 m³)
        total_water_m3_per_rai = total_water_mm * 1.6
        total_water_m3 = total_water_m3_per_rai * field_size_rai

        # Determine irrigation strategy
        if "Rice" in crop_data.get("scientific_name", ""):
            irrigation_type = "flooded/paddy"
            water_regime = "Maintain 5-10cm standing water during vegetative stage"
        else:
            irrigation_type = "supplemental"
            water_regime = "Irrigate when soil moisture drops below 50% field capacity"

        return {
            "total_water_mm": total_water_mm,
            "total_water_m3_per_rai": round(total_water_m3_per_rai, 1),
            "total_water_m3": round(total_water_m3, 1),
            "irrigation_type": irrigation_type,
            "water_regime": water_regime,
            "irrigation_available": irrigation_available,
            "water_stress_risk": "low" if irrigation_available else "high",
            "critical_water_stages": self._get_critical_water_stages(crop_data),
            "recommendations": [
                f"Total water requirement: {total_water_mm} mm over growing season",
                "Monitor soil moisture regularly",
                "Prioritize irrigation during reproductive stage"
            ]
        }

    def _get_critical_water_stages(self, crop_data: Dict[str, Any]) -> List[str]:
        """Identify stages where water is most critical."""
        crop_name = crop_data.get("crop_code", "")

        if crop_name == "RB":  # Riceberry Rice
            return ["vegetative (flooding required)", "reproductive (grain filling)"]
        elif crop_name == "CN":  # Corn
            return ["vegetative (rapid growth)", "reproductive (tasseling/silking)"]
        else:
            return ["reproductive stage"]

    def _calculate_yield_targets(
        self,
        crop_data: Dict[str, Any],
        soil_analysis: Dict[str, Any],
        irrigation_available: bool
    ) -> Dict[str, Any]:
        """Calculate realistic yield targets based on conditions."""
        yield_potential = crop_data.get("yield_potential_kg_per_rai", {})

        base_low = yield_potential.get("low", 300)
        base_avg = yield_potential.get("average", 450)
        base_high = yield_potential.get("high", 600)

        # Adjust based on soil health
        soil_health = soil_analysis.get("soil_health_score", 70)

        if soil_health >= 80:
            adjustment = 1.1  # 10% bonus for excellent soil
            target_level = "high"
        elif soil_health >= 60:
            adjustment = 1.0  # Average
            target_level = "average"
        elif soil_health >= 40:
            adjustment = 0.85  # 15% reduction
            target_level = "below_average"
        else:
            adjustment = 0.7  # 30% reduction for poor soil
            target_level = "low"

        # Further adjust for irrigation
        if not irrigation_available:
            adjustment *= 0.8  # 20% reduction without irrigation

        target_yield = base_avg * adjustment

        return {
            "target_kg_per_rai": round(target_yield, 0),
            "yield_range": {
                "low": round(base_low * adjustment, 0),
                "expected": round(target_yield, 0),
                "high": round(base_high * adjustment, 0)
            },
            "target_level": target_level,
            "adjustment_factor": adjustment,
            "limiting_factors": self._identify_yield_limiters(
                soil_analysis, irrigation_available
            ),
            "improvement_potential": self._calculate_improvement_potential(
                soil_analysis, adjustment
            )
        }

    def _identify_yield_limiters(
        self,
        soil_analysis: Dict[str, Any],
        irrigation_available: bool
    ) -> List[str]:
        """Identify factors limiting yield potential."""
        limiters = []

        # Check soil health
        soil_health = soil_analysis.get("soil_health_score", 70)
        if soil_health < 60:
            limiters.append(f"Soil health below optimal ({soil_health}/100)")

        # Check critical issues
        critical_issues = soil_analysis.get("critical_issues", [])
        for issue in critical_issues:
            limiters.append(f"Soil issue: {issue}")

        # Check crop suitability
        suitability = soil_analysis.get("crop_suitability", {})
        if suitability.get("score", 100) < 70:
            limiters.append("Soil-crop compatibility below ideal")

        # Irrigation
        if not irrigation_available:
            limiters.append("No irrigation - dependent on rainfall")

        return limiters if limiters else ["No major limiting factors identified"]

    def _calculate_improvement_potential(
        self,
        soil_analysis: Dict[str, Any],
        current_adjustment: float
    ) -> Dict[str, Any]:
        """Calculate potential yield improvement with interventions."""
        max_adjustment = 1.1  # Maximum with perfect conditions
        current = current_adjustment
        gap = max_adjustment - current

        improvement_pct = (gap / current) * 100 if current > 0 else 0

        return {
            "current_yield_factor": round(current, 2),
            "maximum_yield_factor": max_adjustment,
            "improvement_potential_percent": round(improvement_pct, 1),
            "key_improvements": [
                "Address soil nutrient deficiencies",
                "Optimize pH if needed",
                "Ensure adequate water supply",
                "Implement integrated pest management"
            ]
        }

    def _generate_stage_recommendations(
        self,
        crop_data: Dict[str, Any],
        crop_name: str,
        soil_analysis: Dict[str, Any]
    ) -> Dict[str, List[str]]:
        """Generate recommendations for each growth stage."""
        recommendations = {}

        # Pre-planting
        recommendations["pre_planting"] = [
            "Complete soil preparation 1-2 weeks before planting",
            "Apply basal fertilizers and incorporate",
            "Ensure adequate soil moisture for planting"
        ]

        if soil_analysis.get("lime_recommendation"):
            recommendations["pre_planting"].insert(0, "Apply lime to correct pH (allow 2-4 weeks)")

        # By growth stage
        for stage_name in crop_data.get("growth_stages", {}).keys():
            recommendations[stage_name] = self._get_stage_activities(stage_name, crop_data)

        # Post-harvest
        recommendations["post_harvest"] = [
            "Dry harvested produce to safe moisture levels",
            "Consider incorporating crop residues to improve soil",
            "Plan for next season's crop rotation"
        ]

        return recommendations

    def _identify_critical_periods(
        self,
        crop_data: Dict[str, Any],
        planting_date: datetime
    ) -> List[Dict[str, Any]]:
        """Identify critical management windows."""
        periods = []

        stages = crop_data.get("growth_stages", {})

        # First fertilizer application window
        if "vegetative" in stages:
            veg_start = sum(s["days"] for name, s in stages.items()
                          if list(stages.keys()).index(name) < list(stages.keys()).index("vegetative"))
            periods.append({
                "period": "First top-dress nitrogen",
                "timing": f"Day {veg_start + 15} - {veg_start + 25}",
                "date_range": {
                    "start": (planting_date + timedelta(days=veg_start + 15)).isoformat(),
                    "end": (planting_date + timedelta(days=veg_start + 25)).isoformat()
                },
                "priority": "high",
                "action": "Apply 50% of nitrogen top-dress"
            })

        # Reproductive stage - critical for yield
        if "reproductive" in stages:
            rep_start = sum(s["days"] for name, s in stages.items()
                          if list(stages.keys()).index(name) < list(stages.keys()).index("reproductive"))
            periods.append({
                "period": "Reproductive stage water management",
                "timing": f"Day {rep_start} - {rep_start + stages['reproductive']['days']}",
                "date_range": {
                    "start": (planting_date + timedelta(days=rep_start)).isoformat(),
                    "end": (planting_date + timedelta(days=rep_start + stages['reproductive']['days'])).isoformat()
                },
                "priority": "critical",
                "action": "Ensure adequate water - most critical period for yield"
            })

        # Second fertilizer application
        if "reproductive" in stages:
            periods.append({
                "period": "Second fertilizer application",
                "timing": f"Day {rep_start} - {rep_start + 10}",
                "date_range": {
                    "start": (planting_date + timedelta(days=rep_start)).isoformat(),
                    "end": (planting_date + timedelta(days=rep_start + 10)).isoformat()
                },
                "priority": "high",
                "action": "Apply remaining nitrogen and potassium"
            })

        # Harvest window
        total_days = crop_data["growth_cycle_days"]
        periods.append({
            "period": "Optimal harvest window",
            "timing": f"Day {total_days - 5} - {total_days + 7}",
            "date_range": {
                "start": (planting_date + timedelta(days=total_days - 5)).isoformat(),
                "end": (planting_date + timedelta(days=total_days + 7)).isoformat()
            },
            "priority": "high",
            "action": "Harvest at optimal grain moisture (14-20%)"
        })

        return periods

    def _calculate_input_requirements(
        self,
        crop_data: Dict[str, Any],
        field_size_rai: float,
        yield_targets: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Calculate total input requirements for the field."""
        target_yield = yield_targets["target_kg_per_rai"]

        # Seed requirement (approximate)
        if crop_data.get("crop_code") == "RB":
            seed_rate = 15  # kg/rai for rice
        else:
            seed_rate = 3  # kg/rai for corn

        return {
            "seed_kg_per_rai": seed_rate,
            "total_seed_kg": seed_rate * field_size_rai,
            "target_yield_kg": target_yield * field_size_rai,
            "harvest_index": 0.45,  # Approximate
            "labor_days_per_rai": 8,  # Approximate total labor
            "total_labor_days": 8 * field_size_rai
        }

    def _generate_observation(
        self,
        crop_name: str,
        yield_targets: Dict[str, Any],
        water_analysis: Dict[str, Any],
        critical_periods: List[Dict[str, Any]]
    ) -> str:
        """Generate observation summary for next agent."""
        critical_count = len([p for p in critical_periods if p["priority"] == "critical"])

        return (
            f"CropExpert Analysis: {crop_name} with target yield of "
            f"{yield_targets['target_kg_per_rai']} kg/rai. "
            f"Water requirement: {water_analysis['total_water_mm']} mm. "
            f"Identified {critical_count} critical management period(s). "
            f"Yield limiting factors: {', '.join(yield_targets.get('limiting_factors', ['none']))[:100]}."
        )
