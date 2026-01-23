"""
S.O.I.L.E.R. Soil Diagnosis Skill

Deterministic rule-based soil diagnosis.
All thresholds and calculations are documented and verifiable.
"""

from typing import Optional

from core.skills.types import (
    SoilInput,
    DiagnosisResult,
    NutrientAnalysis,
    NutrientLevel,
    PHStatus,
    Issue,
    Recommendation,
    Severity,
)


# =============================================================================
# REFERENCE THRESHOLDS (documented and verifiable)
# Sources: Thai Department of Agriculture, FAO guidelines
# =============================================================================

# pH Thresholds
PH_THRESHOLDS = {
    "very_acidic": (0.0, 4.5),
    "acidic": (4.5, 5.5),
    "slightly_acidic": (5.5, 6.0),
    "optimal": (6.0, 7.0),
    "slightly_alkaline": (7.0, 7.5),
    "alkaline": (7.5, 8.5),
    "very_alkaline": (8.5, 14.0),
}

# Nutrient thresholds (mg/kg) - Thai standards
NUTRIENT_THRESHOLDS = {
    "nitrogen": {
        "very_low": (0, 10),
        "low": (10, 20),
        "medium": (20, 40),
        "high": (40, 60),
        "very_high": (60, float("inf")),
        "optimal": (25, 45),
    },
    "phosphorus": {
        "very_low": (0, 5),
        "low": (5, 15),
        "medium": (15, 30),
        "high": (30, 50),
        "very_high": (50, float("inf")),
        "optimal": (15, 35),
    },
    "potassium": {
        "very_low": (0, 30),
        "low": (30, 60),
        "medium": (60, 120),
        "high": (120, 200),
        "very_high": (200, float("inf")),
        "optimal": (80, 150),
    },
}

# Thai translations for nutrient levels
LEVEL_TH = {
    NutrientLevel.VERY_LOW: "ต่ำมาก",
    NutrientLevel.LOW: "ต่ำ",
    NutrientLevel.MEDIUM: "ปานกลาง",
    NutrientLevel.HIGH: "สูง",
    NutrientLevel.VERY_HIGH: "สูงมาก",
}

PH_STATUS_TH = {
    PHStatus.VERY_ACIDIC: "เป็นกรดจัดมาก",
    PHStatus.ACIDIC: "เป็นกรดจัด",
    PHStatus.SLIGHTLY_ACIDIC: "เป็นกรดเล็กน้อย",
    PHStatus.OPTIMAL: "เหมาะสม",
    PHStatus.SLIGHTLY_ALKALINE: "เป็นด่างเล็กน้อย",
    PHStatus.ALKALINE: "เป็นด่าง",
    PHStatus.VERY_ALKALINE: "เป็นด่างจัด",
}


def _classify_ph(ph: float) -> tuple[PHStatus, str, float]:
    """Classify pH and return status, Thai description, and score."""
    for status_name, (low, high) in PH_THRESHOLDS.items():
        if low <= ph < high:
            status = PHStatus(status_name)
            status_th = PH_STATUS_TH[status]

            # Score: optimal is 100, decreases as pH deviates
            if status == PHStatus.OPTIMAL:
                score = 100.0
            elif status in (PHStatus.SLIGHTLY_ACIDIC, PHStatus.SLIGHTLY_ALKALINE):
                score = 80.0
            elif status in (PHStatus.ACIDIC, PHStatus.ALKALINE):
                score = 50.0
            else:
                score = 30.0

            return status, status_th, score

    return PHStatus.OPTIMAL, PH_STATUS_TH[PHStatus.OPTIMAL], 100.0


def _classify_nutrient(
    nutrient: str, value: float
) -> tuple[NutrientLevel, str, tuple, Optional[float]]:
    """Classify nutrient level and calculate deficit."""
    thresholds = NUTRIENT_THRESHOLDS.get(nutrient, {})
    optimal = thresholds.get("optimal", (20, 40))

    # Find level
    level = NutrientLevel.MEDIUM
    for level_name, (low, high) in thresholds.items():
        if level_name == "optimal":
            continue
        if low <= value < high:
            level = NutrientLevel(level_name)
            break

    level_th = LEVEL_TH[level]

    # Calculate deficit (simplified: if below optimal midpoint)
    optimal_mid = (optimal[0] + optimal[1]) / 2
    deficit = None
    if value < optimal[0]:
        # Simplified conversion: assume 1 mg/kg soil = 0.1 kg/rai needed
        deficit = (optimal_mid - value) * 0.1

    return level, level_th, optimal, deficit


def _analyze_nutrient(nutrient: str, value: Optional[float]) -> Optional[NutrientAnalysis]:
    """Analyze a single nutrient."""
    if value is None:
        return None

    level, level_th, optimal, deficit = _classify_nutrient(nutrient, value)

    return NutrientAnalysis(
        value=value,
        unit="mg/kg",
        level=level,
        level_th=level_th,
        optimal_range=optimal,
        deficit_kg_per_rai=deficit,
    )


def _identify_issues(result: DiagnosisResult) -> list[Issue]:
    """Identify soil issues based on analysis."""
    issues = []

    # pH issues
    if result.ph_status in (PHStatus.VERY_ACIDIC, PHStatus.ACIDIC):
        issues.append(Issue(
            code="PH_LOW",
            description="Soil is too acidic",
            description_th="ดินเป็นกรดเกินไป อาจทำให้ธาตุอาหารถูกตรึง",
            severity=Severity.CRITICAL if result.ph_status == PHStatus.VERY_ACIDIC else Severity.WARNING,
            affected_parameter="pH",
        ))
    elif result.ph_status in (PHStatus.VERY_ALKALINE, PHStatus.ALKALINE):
        issues.append(Issue(
            code="PH_HIGH",
            description="Soil is too alkaline",
            description_th="ดินเป็นด่างเกินไป อาจทำให้ขาดธาตุเหล็กและสังกะสี",
            severity=Severity.CRITICAL if result.ph_status == PHStatus.VERY_ALKALINE else Severity.WARNING,
            affected_parameter="pH",
        ))

    # Nutrient issues
    for name, analysis in [
        ("nitrogen", result.nitrogen_analysis),
        ("phosphorus", result.phosphorus_analysis),
        ("potassium", result.potassium_analysis),
    ]:
        if analysis and analysis.level in (NutrientLevel.VERY_LOW, NutrientLevel.LOW):
            name_th = {"nitrogen": "ไนโตรเจน", "phosphorus": "ฟอสฟอรัส", "potassium": "โพแทสเซียม"}[name]
            issues.append(Issue(
                code=f"{name.upper()}_LOW",
                description=f"Low {name} level",
                description_th=f"ระดับ{name_th}ต่ำ ควรเพิ่มปุ๋ย",
                severity=Severity.CRITICAL if analysis.level == NutrientLevel.VERY_LOW else Severity.WARNING,
                affected_parameter=name,
            ))

    return issues


def _generate_recommendations(result: DiagnosisResult) -> list[Recommendation]:
    """Generate recommendations based on diagnosis."""
    recommendations = []
    priority = 1

    # pH correction
    if result.ph_status in (PHStatus.VERY_ACIDIC, PHStatus.ACIDIC):
        recommendations.append(Recommendation(
            code="LIME_APPLICATION",
            action="Apply agricultural lime (calcium carbite) to raise pH",
            action_th="ใส่ปูนขาว 100-300 กก./ไร่ เพื่อเพิ่ม pH",
            priority=priority,
            rationale="Acidic soil reduces nutrient availability",
        ))
        priority += 1
    elif result.ph_status in (PHStatus.VERY_ALKALINE, PHStatus.ALKALINE):
        recommendations.append(Recommendation(
            code="SULFUR_APPLICATION",
            action="Apply sulfur or acidifying fertilizers to lower pH",
            action_th="ใส่กำมะถันหรือปุ๋ยที่มีฤทธิ์เป็นกรด",
            priority=priority,
            rationale="Alkaline soil causes micronutrient deficiency",
        ))
        priority += 1

    # Nutrient recommendations
    if result.nitrogen_analysis and result.nitrogen_analysis.level in (NutrientLevel.VERY_LOW, NutrientLevel.LOW):
        recommendations.append(Recommendation(
            code="ADD_NITROGEN",
            action="Apply nitrogen fertilizer (urea 46-0-0 or ammonium sulfate)",
            action_th="ใส่ปุ๋ยไนโตรเจน เช่น ยูเรีย หรือแอมโมเนียมซัลเฟต",
            priority=priority,
            rationale="Nitrogen deficiency limits plant growth",
        ))
        priority += 1

    if result.phosphorus_analysis and result.phosphorus_analysis.level in (NutrientLevel.VERY_LOW, NutrientLevel.LOW):
        recommendations.append(Recommendation(
            code="ADD_PHOSPHORUS",
            action="Apply phosphorus fertilizer (TSP or DAP)",
            action_th="ใส่ปุ๋ยฟอสเฟต เช่น ทริปเปิลซุปเปอร์ฟอสเฟต",
            priority=priority,
            rationale="Phosphorus deficiency affects root development",
        ))
        priority += 1

    if result.potassium_analysis and result.potassium_analysis.level in (NutrientLevel.VERY_LOW, NutrientLevel.LOW):
        recommendations.append(Recommendation(
            code="ADD_POTASSIUM",
            action="Apply potassium fertilizer (MOP 0-0-60)",
            action_th="ใส่ปุ๋ยโพแทส เช่น MOP 0-0-60",
            priority=priority,
            rationale="Potassium deficiency reduces yield and quality",
        ))

    return recommendations


def soil_diagnosis(input_data: SoilInput) -> DiagnosisResult:
    """
    Perform deterministic soil diagnosis.

    Args:
        input_data: Soil analysis input parameters

    Returns:
        DiagnosisResult with issues, recommendations, and confidence score

    Note:
        All calculations use documented thresholds from Thai Department of Agriculture.
        Confidence decreases when inputs are missing.
    """
    result = DiagnosisResult(
        target_n_kg_per_rai=0,
        target_p2o5_kg_per_rai=0,
        target_k2o_kg_per_rai=0,
        calculation_method="",
        total_cost_thb=0,
        cost_per_rai_thb=0,
    )

    # Track provided inputs
    provided = []
    missing = []

    # Analyze pH
    if input_data.ph is not None:
        provided.append("pH")
        status, status_th, score = _classify_ph(input_data.ph)
        result.ph_status = status
        result.ph_status_th = status_th
        result.ph_score = score
    else:
        missing.append("pH")
        result.assumptions.append("ไม่มีข้อมูล pH - สมมติว่าอยู่ในช่วงปกติ")

    # Analyze nutrients
    if input_data.nitrogen is not None:
        provided.append("nitrogen")
        result.nitrogen_analysis = _analyze_nutrient("nitrogen", input_data.nitrogen)
    else:
        missing.append("nitrogen")

    if input_data.phosphorus is not None:
        provided.append("phosphorus")
        result.phosphorus_analysis = _analyze_nutrient("phosphorus", input_data.phosphorus)
    else:
        missing.append("phosphorus")

    if input_data.potassium is not None:
        provided.append("potassium")
        result.potassium_analysis = _analyze_nutrient("potassium", input_data.potassium)
    else:
        missing.append("potassium")

    result.inputs_provided = provided
    result.missing_fields = missing

    # Calculate confidence based on inputs provided
    total_inputs = 4  # pH, N, P, K
    result.confidence = len(provided) / total_inputs

    # Calculate health score
    scores = []
    if result.ph_score is not None:
        scores.append(result.ph_score)

    for analysis in [result.nitrogen_analysis, result.phosphorus_analysis, result.potassium_analysis]:
        if analysis:
            level_scores = {
                NutrientLevel.VERY_LOW: 20,
                NutrientLevel.LOW: 40,
                NutrientLevel.MEDIUM: 70,
                NutrientLevel.HIGH: 90,
                NutrientLevel.VERY_HIGH: 80,  # Too high is also not ideal
            }
            scores.append(level_scores.get(analysis.level, 70))

    result.health_score = sum(scores) / len(scores) if scores else None

    # Identify issues and generate recommendations
    result.issues = _identify_issues(result)
    result.recommendations = _generate_recommendations(result)

    # Add warnings
    if result.confidence < 1.0:
        result.warnings.append(
            f"ความเชื่อมั่นในการวินิจฉัย {result.confidence*100:.0f}% เนื่องจากขาดข้อมูลบางส่วน"
        )

    # Build summary
    summary_parts = []
    if result.ph_status_th:
        summary_parts.append(f"pH: {result.ph_status_th}")
    if result.health_score:
        summary_parts.append(f"คะแนนสุขภาพดิน: {result.health_score:.0f}/100")
    if result.issues:
        summary_parts.append(f"พบปัญหา {len(result.issues)} รายการ")

    result.summary_th = " | ".join(summary_parts)

    return result
