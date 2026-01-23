"""
S.O.I.L.E.R. Fertilizer Planning Skill

Deterministic rule-based fertilizer recommendations.
All calculations are documented and verifiable.
"""

from typing import Optional

from core.skills.types import (
    FertilizerInput,
    FertilizerPlanResult,
    FertilizerOption,
)


# =============================================================================
# REFERENCE DATA (documented and verifiable)
# Sources: Thai Department of Agriculture, Thai Rice Department
# =============================================================================

# Crop nutrient requirements (kg/rai for target yield)
# Format: {crop: {N, P2O5, K2O per rai for standard yield}}
CROP_REQUIREMENTS = {
    "rice": {
        "name_th": "ข้าว",
        "n_kg_per_rai": 12,  # 12 kg N/rai for 500 kg/rai yield
        "p2o5_kg_per_rai": 6,
        "k2o_kg_per_rai": 6,
        "base_yield_kg_per_rai": 500,
    },
    "corn": {
        "name_th": "ข้าวโพด",
        "n_kg_per_rai": 15,
        "p2o5_kg_per_rai": 8,
        "k2o_kg_per_rai": 8,
        "base_yield_kg_per_rai": 800,
    },
    "cassava": {
        "name_th": "มันสำปะหลัง",
        "n_kg_per_rai": 8,
        "p2o5_kg_per_rai": 4,
        "k2o_kg_per_rai": 12,  # High K for tuber crops
        "base_yield_kg_per_rai": 3000,
    },
    "sugarcane": {
        "name_th": "อ้อย",
        "n_kg_per_rai": 16,
        "p2o5_kg_per_rai": 6,
        "k2o_kg_per_rai": 16,
        "base_yield_kg_per_rai": 10000,
    },
    "vegetable": {
        "name_th": "ผัก",
        "n_kg_per_rai": 10,
        "p2o5_kg_per_rai": 8,
        "k2o_kg_per_rai": 10,
        "base_yield_kg_per_rai": 2000,
    },
}

# Default for unknown crops
DEFAULT_CROP = {
    "name_th": "พืชทั่วไป",
    "n_kg_per_rai": 10,
    "p2o5_kg_per_rai": 6,
    "k2o_kg_per_rai": 8,
    "base_yield_kg_per_rai": 1000,
}

# Common fertilizer formulas available in Thailand
FERTILIZER_CATALOG = [
    {
        "name": "Urea",
        "name_th": "ยูเรีย",
        "formula": "46-0-0",
        "n": 46,
        "p": 0,
        "k": 0,
        "cost_per_kg": 22,  # THB/kg (approximate)
        "organic": False,
    },
    {
        "name": "16-20-0",
        "name_th": "สูตร 16-20-0",
        "formula": "16-20-0",
        "n": 16,
        "p": 20,
        "k": 0,
        "cost_per_kg": 20,
        "organic": False,
    },
    {
        "name": "15-15-15",
        "name_th": "สูตร 15-15-15",
        "formula": "15-15-15",
        "n": 15,
        "p": 15,
        "k": 15,
        "cost_per_kg": 22,
        "organic": False,
    },
    {
        "name": "MOP (0-0-60)",
        "name_th": "โพแทสเซียมคลอไรด์",
        "formula": "0-0-60",
        "n": 0,
        "p": 0,
        "k": 60,
        "cost_per_kg": 25,
        "organic": False,
    },
    {
        "name": "DAP (18-46-0)",
        "name_th": "ไดแอมโมเนียมฟอสเฟต",
        "formula": "18-46-0",
        "n": 18,
        "p": 46,
        "k": 0,
        "cost_per_kg": 28,
        "organic": False,
    },
    {
        "name": "Organic Compost",
        "name_th": "ปุ๋ยหมัก",
        "formula": "2-1-1",
        "n": 2,
        "p": 1,
        "k": 1,
        "cost_per_kg": 5,
        "organic": True,
    },
]


def _get_crop_requirements(crop: str) -> dict:
    """Get crop nutrient requirements, case-insensitive."""
    crop_lower = crop.lower().strip()
    return CROP_REQUIREMENTS.get(crop_lower, DEFAULT_CROP)


def _calculate_targets(
    input_data: FertilizerInput,
) -> tuple[float, float, float, dict]:
    """
    Calculate N-P-K targets based on crop requirements and soil status.

    Returns: (target_n, target_p2o5, target_k2o, calculation_details)
    """
    crop_req = _get_crop_requirements(input_data.crop)
    details = {"method": "crop_requirement_based"}

    # Base requirements
    base_n = crop_req["n_kg_per_rai"]
    base_p = crop_req["p2o5_kg_per_rai"]
    base_k = crop_req["k2o_kg_per_rai"]

    details["base_n"] = base_n
    details["base_p2o5"] = base_p
    details["base_k2o"] = base_k

    # Adjust for target yield if provided
    yield_factor = 1.0
    if input_data.target_yield_kg_per_rai:
        base_yield = crop_req["base_yield_kg_per_rai"]
        yield_factor = input_data.target_yield_kg_per_rai / base_yield
        # Cap yield factor to reasonable range
        yield_factor = max(0.5, min(2.0, yield_factor))
        details["yield_factor"] = yield_factor

    # Adjust for soil nutrient levels if provided
    # Simplified: reduce requirement if soil has adequate nutrients
    soil_n_factor = 1.0
    soil_p_factor = 1.0
    soil_k_factor = 1.0

    if input_data.soil_n is not None:
        # If soil N > 40 mg/kg, reduce N requirement by 30%
        if input_data.soil_n > 40:
            soil_n_factor = 0.7
        elif input_data.soil_n > 25:
            soil_n_factor = 0.85
        details["soil_n_adjustment"] = soil_n_factor

    if input_data.soil_p is not None:
        if input_data.soil_p > 30:
            soil_p_factor = 0.7
        elif input_data.soil_p > 15:
            soil_p_factor = 0.85
        details["soil_p_adjustment"] = soil_p_factor

    if input_data.soil_k is not None:
        if input_data.soil_k > 120:
            soil_k_factor = 0.7
        elif input_data.soil_k > 80:
            soil_k_factor = 0.85
        details["soil_k_adjustment"] = soil_k_factor

    # Calculate final targets
    target_n = base_n * yield_factor * soil_n_factor
    target_p = base_p * yield_factor * soil_p_factor
    target_k = base_k * yield_factor * soil_k_factor

    # Round to 1 decimal
    target_n = round(target_n, 1)
    target_p = round(target_p, 1)
    target_k = round(target_k, 1)

    return target_n, target_p, target_k, details


def _calculate_fertilizer_rate(
    fertilizer: dict,
    target_n: float,
    target_p: float,
    target_k: float,
    field_size: float,
) -> Optional[FertilizerOption]:
    """
    Calculate how much of a fertilizer to apply.

    For single-nutrient fertilizers, targets that nutrient.
    For compound fertilizers, balances to avoid over-application.
    """
    n_pct = fertilizer["n"] / 100
    p_pct = fertilizer["p"] / 100
    k_pct = fertilizer["k"] / 100

    # Determine limiting nutrient for this fertilizer
    rates_needed = []
    if n_pct > 0 and target_n > 0:
        rates_needed.append(target_n / n_pct)
    if p_pct > 0 and target_p > 0:
        rates_needed.append(target_p / p_pct)
    if k_pct > 0 and target_k > 0:
        rates_needed.append(target_k / k_pct)

    if not rates_needed:
        return None

    # Use minimum rate to avoid over-application
    rate_kg_per_rai = min(rates_needed)

    # Skip if rate is negligible
    if rate_kg_per_rai < 1:
        return None

    rate_kg_per_rai = round(rate_kg_per_rai, 1)
    total_kg = rate_kg_per_rai * field_size
    total_cost = total_kg * fertilizer["cost_per_kg"]

    return FertilizerOption(
        name=fertilizer["name"],
        name_th=fertilizer["name_th"],
        formula=fertilizer["formula"],
        rate_kg_per_rai=rate_kg_per_rai,
        cost_per_kg=fertilizer["cost_per_kg"],
        total_cost=round(total_cost, 2),
        application_timing="basal and top-dressing",
        application_timing_th="รองพื้นและแต่งหน้า",
    )


def _generate_fertilizer_options(
    target_n: float,
    target_p: float,
    target_k: float,
    field_size: float,
    prefer_organic: bool,
    budget: Optional[float],
) -> list[FertilizerOption]:
    """Generate fertilizer options based on targets."""
    options = []

    for fertilizer in FERTILIZER_CATALOG:
        # Skip non-organic if organic preferred
        if prefer_organic and not fertilizer["organic"]:
            continue

        option = _calculate_fertilizer_rate(
            fertilizer, target_n, target_p, target_k, field_size
        )
        if option:
            # Skip if over budget
            if budget and option.total_cost > budget:
                continue
            options.append(option)

    # Sort by cost
    options.sort(key=lambda x: x.total_cost)

    return options


def fertilizer_plan(input_data: FertilizerInput) -> FertilizerPlanResult:
    """
    Generate deterministic fertilizer recommendations.

    Args:
        input_data: Fertilizer planning input parameters

    Returns:
        FertilizerPlanResult with targets, options, and costs

    Note:
        All calculations use documented formulas.
        Confidence decreases when inputs are missing.
    """
    result = FertilizerPlanResult(
        target_n_kg_per_rai=0,
        target_p2o5_kg_per_rai=0,
        target_k2o_kg_per_rai=0,
        calculation_method="",
        total_cost_thb=0,
        cost_per_rai_thb=0,
    )

    # Track provided inputs
    provided = ["crop"]  # Always provided (required field)
    missing = []

    if input_data.field_size_rai:
        provided.append("field_size_rai")

    if input_data.target_yield_kg_per_rai:
        provided.append("target_yield")
    else:
        missing.append("target_yield")

    if input_data.soil_n is not None:
        provided.append("soil_n")
    else:
        missing.append("soil_n")

    if input_data.soil_p is not None:
        provided.append("soil_p")
    else:
        missing.append("soil_p")

    if input_data.soil_k is not None:
        provided.append("soil_k")
    else:
        missing.append("soil_k")

    result.inputs_provided = provided
    result.missing_fields = missing

    # Calculate N-P-K targets
    target_n, target_p, target_k, calc_details = _calculate_targets(input_data)

    result.target_n_kg_per_rai = target_n
    result.target_p2o5_kg_per_rai = target_p
    result.target_k2o_kg_per_rai = target_k
    result.calculation_method = "crop_requirement_adjusted_for_soil"
    result.calculation_details = calc_details

    # Generate fertilizer options
    options = _generate_fertilizer_options(
        target_n,
        target_p,
        target_k,
        input_data.field_size_rai,
        input_data.prefer_organic,
        input_data.budget_thb,
    )

    result.fertilizer_options = options

    # Select recommended option (first one, lowest cost)
    if options:
        result.recommended_option_index = 0
        recommended = options[0]
        result.total_cost_thb = recommended.total_cost
        result.cost_per_rai_thb = round(
            recommended.total_cost / input_data.field_size_rai, 2
        )

        if input_data.budget_thb:
            result.within_budget = result.total_cost_thb <= input_data.budget_thb

    # Calculate confidence
    # Full inputs: crop, soil_n, soil_p, soil_k, target_yield = 5 items
    confidence_items = 5
    actual_items = len([x for x in [
        True,  # crop always provided
        input_data.soil_n is not None,
        input_data.soil_p is not None,
        input_data.soil_k is not None,
        input_data.target_yield_kg_per_rai is not None,
    ] if x])
    result.confidence = actual_items / confidence_items

    # Add assumptions for missing data
    if input_data.target_yield_kg_per_rai is None:
        crop_req = _get_crop_requirements(input_data.crop)
        result.assumptions.append(
            f"สมมติเป้าหมายผลผลิตมาตรฐาน {crop_req['base_yield_kg_per_rai']} กก./ไร่"
        )

    if not any([input_data.soil_n, input_data.soil_p, input_data.soil_k]):
        result.assumptions.append("ไม่มีข้อมูลดิน - ใช้ค่าแนะนำมาตรฐานสำหรับพืช")

    # Add warnings
    if result.confidence < 1.0:
        result.warnings.append(
            f"ความเชื่อมั่น {result.confidence*100:.0f}% เนื่องจากขาดข้อมูลบางส่วน"
        )

    if not options:
        result.warnings.append("ไม่พบตัวเลือกปุ๋ยที่เหมาะสมในงบประมาณ")

    # Add disclaimers
    result.disclaimers = [
        "คำแนะนำนี้เป็นแนวทางเบื้องต้น ควรปรึกษาผู้เชี่ยวชาญก่อนใช้งานจริง",
        "ราคาปุ๋ยเป็นค่าประมาณ อาจแตกต่างตามพื้นที่และช่วงเวลา",
    ]

    # Build summary
    crop_req = _get_crop_requirements(input_data.crop)
    summary_parts = [
        f"แผนปุ๋ยสำหรับ{crop_req['name_th']}",
        f"เป้าหมาย N-P-K: {target_n}-{target_p}-{target_k} กก./ไร่",
    ]
    if options:
        summary_parts.append(f"แนะนำ: {options[0].name_th}")
        summary_parts.append(f"ค่าใช้จ่าย: {result.total_cost_thb:.0f} บาท")

    result.summary_th = " | ".join(summary_parts)

    return result
