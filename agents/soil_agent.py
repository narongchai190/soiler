"""
S.O.I.L.E.R. Soil Analysis Agent
Analyzes soil data and matches against known soil series.
"""

from typing import Any, Dict, List, Tuple

from agents.base_agent import BaseAgent
from data.knowledge_base import CROP_REQUIREMENTS, SOIL_SERIES
from utils.calculator import assess_nutrient_level, calculate_lime_requirement


class SoilAgent(BaseAgent):
    """
    Soil Analysis Agent - Identifies soil type and assesses soil health.

    Responsibilities:
    - Match user soil data against known soil series
    - Assess pH status and suitability for target crop
    - Evaluate nutrient levels (N-P-K)
    - Calculate overall soil health score
    - Identify critical issues and limitations
    """

    def __init__(self, verbose: bool = True):
        super().__init__(agent_name="SoilAnalyst", verbose=verbose)

    def _execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute soil analysis.

        Args:
            input_data: Dictionary containing:
                - sample_id: str
                - ph: float
                - nitrogen: float (mg/kg)
                - phosphorus: float (mg/kg)
                - potassium: float (mg/kg)
                - texture: str (optional)
                - location: str (optional)
                - target_crop: str (optional)

        Returns:
            Analysis results dictionary
        """
        self.think("Receiving soil sample data for analysis...")

        sample_id = input_data.get("sample_id", "UNKNOWN")
        ph = input_data.get("ph", 6.5)
        nitrogen = input_data.get("nitrogen", 0)
        phosphorus = input_data.get("phosphorus", 0)
        potassium = input_data.get("potassium", 0)
        texture = input_data.get("texture", "loam")
        location = input_data.get("location", "Unknown")
        target_crop = input_data.get("target_crop")

        # Step 1: Identify soil series
        self.think("Matching soil profile against known soil series...")
        series_match, confidence = self._match_soil_series(
            ph=ph,
            nitrogen=nitrogen,
            phosphorus=phosphorus,
            potassium=potassium,
            texture=texture,
            location=location
        )
        self.log_action(f"Best match: {series_match} (confidence: {confidence:.0%})")

        # Step 2: Analyze pH
        self.think("Analyzing pH status...")
        ph_analysis = self._analyze_ph(ph, target_crop)
        self.log_result(f"pH Status: {ph_analysis['status']}")

        # Step 3: Assess nutrient levels
        self.think("Evaluating nutrient levels (N-P-K)...")
        nutrient_status = self._assess_nutrients(nitrogen, phosphorus, potassium)
        for ns in nutrient_status:
            self.log_result(f"{ns['nutrient']}: {ns['status']} ({ns['current_level']} mg/kg)")

        # Step 4: Calculate soil health score
        self.think("Calculating overall soil health score...")
        health_score, health_indicators = self._calculate_health_score(
            ph=ph,
            nitrogen=nitrogen,
            phosphorus=phosphorus,
            potassium=potassium,
            texture=texture
        )
        self.log_result(f"Soil Health Score: {health_score}/100")

        # Step 5: Assess crop suitability
        crop_suitability = None
        if target_crop:
            self.think(f"Assessing suitability for {target_crop}...")
            crop_suitability = self._assess_crop_suitability(
                ph=ph,
                nitrogen=nitrogen,
                phosphorus=phosphorus,
                potassium=potassium,
                texture=texture,
                target_crop=target_crop
            )
            self.log_result(f"Crop Suitability: {crop_suitability['score']}/100")

        # Step 6: Identify critical issues
        self.think("Identifying critical issues and recommendations...")
        critical_issues, recommendations = self._identify_issues(
            ph=ph,
            ph_analysis=ph_analysis,
            nutrient_status=nutrient_status,
            target_crop=target_crop
        )

        if critical_issues:
            for issue in critical_issues:
                self.log_warning(issue)
        else:
            self.log_result("No critical issues found")

        # Build result
        result = {
            "sample_id": sample_id,
            "location": location,
            "identified_soil_series": series_match,
            "series_match_confidence": confidence,
            "ph_value": ph,
            "ph_status": ph_analysis["status"],
            "ph_suitability": ph_analysis["suitability"],
            "lime_recommendation": ph_analysis.get("lime_recommendation"),
            "nutrient_status": nutrient_status,
            "soil_health_score": health_score,
            "health_indicators": health_indicators,
            "target_crop": target_crop,
            "crop_suitability": crop_suitability,
            "critical_issues": critical_issues,
            "recommendations": recommendations,
        }

        return result

    def _match_soil_series(
        self,
        ph: float,
        nitrogen: float,
        phosphorus: float,
        potassium: float,
        texture: str,
        location: str
    ) -> Tuple[str, float]:
        """
        Match soil profile against known soil series using similarity scoring.

        Returns:
            Tuple of (best_match_name, confidence_score)
        """
        best_match = None
        best_score = 0.0

        for series_name, series_data in SOIL_SERIES.items():
            score = 0.0
            max_score = 0.0

            # pH matching (weight: 30%)
            ph_range = series_data["typical_properties"]["ph_range"]
            max_score += 30
            if ph_range["min"] <= ph <= ph_range["max"]:
                # Perfect if within range
                score += 30
            else:
                # Partial score based on distance
                distance = min(
                    abs(ph - ph_range["min"]),
                    abs(ph - ph_range["max"])
                )
                score += max(0, 30 - (distance * 15))

            # Texture matching (weight: 25%)
            max_score += 25
            series_texture = series_data["texture"].lower()
            input_texture = texture.lower()
            if series_texture == input_texture:
                score += 25
            elif any(word in series_texture for word in input_texture.split()):
                score += 15

            # Location matching (weight: 20%)
            max_score += 20
            location_lower = location.lower()
            for area in series_data.get("location_areas", []):
                if any(word in location_lower for word in area.lower().split()):
                    score += 20
                    break

            # NPK profile matching (weight: 25%)
            max_score += 25
            npk_props = series_data["typical_properties"]

            # Nitrogen
            n_range = npk_props["nitrogen_mg_kg"]
            if n_range["low"] <= nitrogen <= n_range["high"]:
                score += 8.33

            # Phosphorus
            p_range = npk_props["phosphorus_mg_kg"]
            if p_range["low"] <= phosphorus <= p_range["high"]:
                score += 8.33

            # Potassium
            k_range = npk_props["potassium_mg_kg"]
            if k_range["low"] <= potassium <= k_range["high"]:
                score += 8.34

            # Calculate confidence
            confidence = score / max_score if max_score > 0 else 0

            if confidence > best_score:
                best_score = confidence
                best_match = series_name

        return best_match or "Unknown", best_score

    def _analyze_ph(self, ph: float, target_crop: str | None = None) -> Dict[str, Any]:
        """Analyze pH status and suitability."""
        # Determine pH status
        if ph < 5.5:
            status = "strongly acidic"
        elif ph < 6.0:
            status = "moderately acidic"
        elif ph < 6.5:
            status = "slightly acidic"
        elif ph < 7.0:
            status = "neutral"
        elif ph < 7.5:
            status = "slightly alkaline"
        elif ph < 8.0:
            status = "moderately alkaline"
        else:
            status = "strongly alkaline"

        # Assess suitability for target crop
        suitability = "unknown - no target crop specified"
        lime_recommendation = None

        if target_crop and target_crop in CROP_REQUIREMENTS:
            crop = CROP_REQUIREMENTS[target_crop]
            ph_req = crop["soil_requirements"]["ph_range"]

            if ph_req["min"] <= ph <= ph_req["max"]:
                if abs(ph - ph_req["optimal"]) < 0.3:
                    suitability = f"optimal for {target_crop}"
                else:
                    suitability = f"suitable for {target_crop}"
            elif ph < ph_req["min"]:
                suitability = f"too acidic for {target_crop} - lime recommended"
                lime_recommendation = calculate_lime_requirement(
                    current_ph=ph,
                    target_ph=ph_req["optimal"],
                    soil_texture="loam"  # Default, should be passed
                )
            else:
                suitability = f"too alkaline for {target_crop} - sulfur may be needed"

        return {
            "status": status,
            "suitability": suitability,
            "lime_recommendation": lime_recommendation
        }

    def _assess_nutrients(
        self,
        nitrogen: float,
        phosphorus: float,
        potassium: float
    ) -> List[Dict[str, Any]]:
        """Assess N-P-K nutrient levels."""
        results = []

        # Nitrogen
        n_status, n_desc = assess_nutrient_level("nitrogen", nitrogen)
        results.append({
            "nutrient": "Nitrogen (N)",
            "current_level": nitrogen,
            "unit": "mg/kg",
            "status": n_status,
            "description": n_desc,
            "deficiency_percent": max(0, (30 - nitrogen) / 30 * 100) if nitrogen < 30 else None,
            "excess_percent": max(0, (nitrogen - 80) / 80 * 100) if nitrogen > 80 else None,
        })

        # Phosphorus
        p_status, p_desc = assess_nutrient_level("phosphorus", phosphorus)
        results.append({
            "nutrient": "Phosphorus (P)",
            "current_level": phosphorus,
            "unit": "mg/kg",
            "status": p_status,
            "description": p_desc,
            "deficiency_percent": max(0, (15 - phosphorus) / 15 * 100) if phosphorus < 15 else None,
            "excess_percent": max(0, (phosphorus - 50) / 50 * 100) if phosphorus > 50 else None,
        })

        # Potassium
        k_status, k_desc = assess_nutrient_level("potassium", potassium)
        results.append({
            "nutrient": "Potassium (K)",
            "current_level": potassium,
            "unit": "mg/kg",
            "status": k_status,
            "description": k_desc,
            "deficiency_percent": max(0, (80 - potassium) / 80 * 100) if potassium < 80 else None,
            "excess_percent": max(0, (potassium - 200) / 200 * 100) if potassium > 200 else None,
        })

        return results

    def _calculate_health_score(
        self,
        ph: float,
        nitrogen: float,
        phosphorus: float,
        potassium: float,
        texture: str
    ) -> Tuple[float, List[Dict[str, Any]]]:
        """Calculate overall soil health score (0-100)."""
        indicators = []
        total_score = 0

        # pH Score (25 points) - optimal around 6.0-6.5
        ph_optimal = 6.25
        ph_deviation = abs(ph - ph_optimal)
        ph_score = max(0, 25 - (ph_deviation * 10))
        ph_rating = "good" if ph_score > 18 else ("fair" if ph_score > 10 else "poor")
        indicators.append({
            "indicator": "pH Balance",
            "value": ph,
            "rating": ph_rating,
            "description": f"pH of {ph} is {'optimal' if ph_score > 20 else 'acceptable' if ph_score > 10 else 'needs adjustment'}"
        })
        total_score += ph_score

        # Nitrogen Score (25 points)
        n_optimal = 45
        n_score = max(0, 25 - abs(nitrogen - n_optimal) * 0.5)
        n_rating = "good" if n_score > 18 else ("fair" if n_score > 10 else "poor")
        indicators.append({
            "indicator": "Nitrogen Status",
            "value": nitrogen,
            "rating": n_rating,
            "description": f"N at {nitrogen} mg/kg is {'adequate' if n_score > 15 else 'needs supplementation'}"
        })
        total_score += n_score

        # Phosphorus Score (25 points)
        p_optimal = 25
        p_score = max(0, 25 - abs(phosphorus - p_optimal) * 0.8)
        p_rating = "good" if p_score > 18 else ("fair" if p_score > 10 else "poor")
        indicators.append({
            "indicator": "Phosphorus Status",
            "value": phosphorus,
            "rating": p_rating,
            "description": f"P at {phosphorus} mg/kg is {'adequate' if p_score > 15 else 'needs supplementation'}"
        })
        total_score += p_score

        # Potassium Score (25 points)
        k_optimal = 140
        k_score = max(0, 25 - abs(potassium - k_optimal) * 0.15)
        k_rating = "good" if k_score > 18 else ("fair" if k_score > 10 else "poor")
        indicators.append({
            "indicator": "Potassium Status",
            "value": potassium,
            "rating": k_rating,
            "description": f"K at {potassium} mg/kg is {'adequate' if k_score > 15 else 'needs supplementation'}"
        })
        total_score += k_score

        return round(total_score, 1), indicators

    def _assess_crop_suitability(
        self,
        ph: float,
        nitrogen: float,
        phosphorus: float,
        potassium: float,
        texture: str,
        target_crop: str
    ) -> Dict[str, Any]:
        """Assess suitability for specific crop."""
        if target_crop not in CROP_REQUIREMENTS:
            return {"score": 0, "assessment": "Unknown crop"}

        crop = CROP_REQUIREMENTS[target_crop]
        soil_req = crop["soil_requirements"]
        score = 0

        # pH suitability (40 points)
        ph_range = soil_req["ph_range"]
        if ph_range["min"] <= ph <= ph_range["max"]:
            if abs(ph - ph_range["optimal"]) < 0.3:
                score += 40
            else:
                score += 30
        elif abs(ph - ph_range["min"]) < 0.5 or abs(ph - ph_range["max"]) < 0.5:
            score += 15

        # Texture suitability (30 points)
        if texture.lower() in [t.lower() for t in soil_req["texture_preference"]]:
            score += 30
        else:
            score += 10

        # Drainage consideration (30 points)
        score += 20  # Default moderate score

        assessment = "excellent" if score >= 80 else ("good" if score >= 60 else ("fair" if score >= 40 else "poor"))

        return {
            "score": score,
            "assessment": assessment,
            "limiting_factors": self._get_limiting_factors(ph, texture, target_crop)
        }

    def _get_limiting_factors(self, ph: float, texture: str, target_crop: str) -> List[str]:
        """Identify limiting factors for crop production."""
        factors = []
        crop = CROP_REQUIREMENTS.get(target_crop, {})
        soil_req = crop.get("soil_requirements", {})

        ph_range = soil_req.get("ph_range", {})
        if ph_range:
            if ph < ph_range.get("min", 0):
                factors.append(f"pH too low (current: {ph}, minimum: {ph_range['min']})")
            elif ph > ph_range.get("max", 14):
                factors.append(f"pH too high (current: {ph}, maximum: {ph_range['max']})")

        texture_prefs = soil_req.get("texture_preference", [])
        if texture_prefs and texture.lower() not in [t.lower() for t in texture_prefs]:
            factors.append(f"Soil texture ({texture}) not ideal for {target_crop}")

        return factors

    def _identify_issues(
        self,
        ph: float,
        ph_analysis: Dict[str, Any],
        nutrient_status: List[Dict[str, Any]],
        target_crop: str | None
    ) -> Tuple[List[str], List[str]]:
        """Identify critical issues and generate recommendations."""
        critical_issues = []
        recommendations = []

        # pH issues
        if ph < 5.0:
            critical_issues.append("Severely acidic soil - lime application critical")
            recommendations.append("Apply agricultural lime immediately, retest in 3 months")
        elif ph < 5.5:
            recommendations.append("Consider lime application to raise pH")

        if ph > 8.0:
            critical_issues.append("Highly alkaline soil - may cause nutrient lockout")
            recommendations.append("Apply elemental sulfur or acidifying fertilizers")

        # Nutrient issues
        for ns in nutrient_status:
            if ns["status"] == "very_low":
                critical_issues.append(f"{ns['nutrient']} critically deficient")
                recommendations.append(f"Priority fertilization for {ns['nutrient']} required")
            elif ns["status"] == "low":
                recommendations.append(f"Supplement {ns['nutrient']} before planting")

        # Crop-specific recommendations
        if target_crop:
            recommendations.append(f"Follow split application schedule for {target_crop}")

        return critical_issues, recommendations
