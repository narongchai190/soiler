"""
S.O.I.L.E.R. Fertilizer Calculator
Utility functions for calculating fertilizer requirements and costs.
"""

from typing import Any, Dict, List, Tuple

from data.knowledge_base import CROP_REQUIREMENTS, FERTILIZERS


def calculate_nutrient_gap(
    current_npk: Dict[str, float],
    crop_name: str,
    field_size_rai: float = 1.0
) -> Dict[str, float]:
    """
    Calculate the nutrient gap between current soil levels and crop requirements.

    Args:
        current_npk: Current soil NPK levels in mg/kg
            {"nitrogen": float, "phosphorus": float, "potassium": float}
        crop_name: Name of the target crop
        field_size_rai: Field size in rai (1 rai = 1,600 m²)

    Returns:
        Dictionary with nutrient gaps in kg needed per rai:
            {"nitrogen_gap_kg": float, "p2o5_gap_kg": float, "k2o_gap_kg": float}
    """
    crop = CROP_REQUIREMENTS.get(crop_name)
    if not crop:
        raise ValueError(f"Unknown crop: {crop_name}")

    requirements = crop["nutrient_requirements_kg_per_rai"]

    # Convert soil levels (mg/kg) to relative fertility status
    # Using simplified conversion: mg/kg thresholds from knowledge base
    # Low < 30, Medium 30-60, High > 60 for N (approximate)

    n_current = current_npk.get("nitrogen", 0)
    p_current = current_npk.get("phosphorus", 0)
    k_current = current_npk.get("potassium", 0)

    # Calculate soil contribution factor (0.0 to 1.0) based on current levels
    # Higher soil levels = less fertilizer needed
    n_factor = min(1.0, max(0.0, 1.0 - (n_current / 80)))  # Reduce if N > 80 mg/kg
    p_factor = min(1.0, max(0.0, 1.0 - (p_current / 50)))  # Reduce if P > 50 mg/kg
    k_factor = min(1.0, max(0.0, 1.0 - (k_current / 200))) # Reduce if K > 200 mg/kg

    # Calculate gaps (what we need to add)
    n_gap = requirements["nitrogen"]["optimal"] * n_factor
    p_gap = requirements["phosphorus_p2o5"]["optimal"] * p_factor
    k_gap = requirements["potassium_k2o"]["optimal"] * k_factor

    return {
        "nitrogen_gap_kg": round(n_gap * field_size_rai, 2),
        "p2o5_gap_kg": round(p_gap * field_size_rai, 2),
        "k2o_gap_kg": round(k_gap * field_size_rai, 2),
        "field_size_rai": field_size_rai,
        "soil_n_factor": round(n_factor, 2),
        "soil_p_factor": round(p_factor, 2),
        "soil_k_factor": round(k_factor, 2),
    }


def calculate_fertilizer_amounts(
    nutrient_gaps: Dict[str, float],
    preferred_fertilizers: List[str] | None = None
) -> List[Dict[str, Any]]:
    """
    Calculate specific fertilizer amounts to meet nutrient gaps.

    Args:
        nutrient_gaps: Output from calculate_nutrient_gap()
        preferred_fertilizers: Optional list of preferred fertilizer names

    Returns:
        List of fertilizer recommendations with amounts
    """
    n_needed = nutrient_gaps["nitrogen_gap_kg"]
    p_needed = nutrient_gaps["p2o5_gap_kg"]
    k_needed = nutrient_gaps["k2o_gap_kg"]
    field_size = nutrient_gaps.get("field_size_rai", 1.0)

    recommendations = []

    # Strategy: Use compound fertilizer first, then single-nutrient to top up

    # Check if NPK 16-20-0 can cover base needs (good for rice)
    npk_16_20_0 = next((f for f in FERTILIZERS if f["formula"] == "16-20-0"), None)

    if npk_16_20_0 and p_needed > 0:
        # Calculate how much 16-20-0 to apply based on P requirement
        p_content = npk_16_20_0["npk_ratio"]["P"] / 100
        amount_for_p = p_needed / p_content if p_content > 0 else 0

        # Cap at reasonable application rate
        amount_for_p = min(amount_for_p, 50 * field_size)

        if amount_for_p > 0:
            n_from_compound = amount_for_p * (npk_16_20_0["npk_ratio"]["N"] / 100)
            p_from_compound = amount_for_p * p_content

            recommendations.append({
                "fertilizer": npk_16_20_0,
                "amount_kg": round(amount_for_p, 2),
                "amount_per_rai_kg": round(amount_for_p / field_size, 2),
                "nutrients_provided": {
                    "N": round(n_from_compound, 2),
                    "P2O5": round(p_from_compound, 2),
                    "K2O": 0
                },
                "application_stage": "basal",
                "timing": "Before transplanting or at planting"
            })

            n_needed -= n_from_compound
            p_needed -= p_from_compound

    # Top up Nitrogen with Urea (46-0-0)
    if n_needed > 0:
        urea = next((f for f in FERTILIZERS if f["formula"] == "46-0-0"), None)
        if urea:
            n_content = urea["npk_ratio"]["N"] / 100
            amount_urea = n_needed / n_content

            recommendations.append({
                "fertilizer": urea,
                "amount_kg": round(amount_urea, 2),
                "amount_per_rai_kg": round(amount_urea / field_size, 2),
                "nutrients_provided": {
                    "N": round(n_needed, 2),
                    "P2O5": 0,
                    "K2O": 0
                },
                "application_stage": "top-dress",
                "timing": "Split: 50% at tillering, 50% at panicle initiation"
            })

    # Add Potassium with MOP (0-0-60)
    if k_needed > 0:
        mop = next((f for f in FERTILIZERS if f["formula"] == "0-0-60"), None)
        if mop:
            k_content = mop["npk_ratio"]["K"] / 100
            amount_mop = k_needed / k_content

            recommendations.append({
                "fertilizer": mop,
                "amount_kg": round(amount_mop, 2),
                "amount_per_rai_kg": round(amount_mop / field_size, 2),
                "nutrients_provided": {
                    "N": 0,
                    "P2O5": 0,
                    "K2O": round(k_needed, 2)
                },
                "application_stage": "split",
                "timing": "50% basal, 50% at panicle initiation"
            })

    return recommendations


def calculate_total_cost(
    fertilizer_recommendations: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Calculate total cost for fertilizer recommendations.

    Args:
        fertilizer_recommendations: Output from calculate_fertilizer_amounts()

    Returns:
        Cost breakdown dictionary
    """
    cost_breakdown = []
    total_cost = 0.0

    for rec in fertilizer_recommendations:
        fert = rec["fertilizer"]
        amount = rec["amount_kg"]
        unit_price = fert["price_thb_per_kg"]
        item_cost = amount * unit_price

        cost_breakdown.append({
            "fertilizer_name": fert["name"],
            "formula": fert["formula"],
            "quantity_kg": amount,
            "unit_price_thb": unit_price,
            "total_cost_thb": round(item_cost, 2)
        })

        total_cost += item_cost

    return {
        "breakdown": cost_breakdown,
        "total_cost_thb": round(total_cost, 2),
        "currency": "THB"
    }


def calculate_lime_requirement(
    current_ph: float,
    target_ph: float,
    soil_texture: str,
    field_size_rai: float = 1.0
) -> Dict[str, Any]:
    """
    Calculate lime requirement to raise soil pH.

    Args:
        current_ph: Current soil pH
        target_ph: Desired soil pH
        soil_texture: Soil texture classification
        field_size_rai: Field size in rai

    Returns:
        Lime recommendation dictionary
    """
    if current_ph >= target_ph:
        return {
            "lime_needed": False,
            "amount_kg_per_rai": 0,
            "total_amount_kg": 0,
            "message": "Soil pH is adequate, no lime needed"
        }

    ph_difference = target_ph - current_ph

    # Buffer capacity based on texture (higher clay = more lime needed)
    texture_factors = {
        "sand": 0.8,
        "loamy sand": 1.0,
        "sandy loam": 1.2,
        "loam": 1.5,
        "silt loam": 1.6,
        "clay loam": 2.0,
        "silty clay loam": 2.2,
        "silty clay": 2.5,
        "clay": 3.0,
    }

    factor = texture_factors.get(soil_texture.lower(), 1.5)

    # Base rate: ~200 kg/rai agricultural lime per 0.5 pH unit for medium texture
    base_rate = 200  # kg per rai per 0.5 pH unit
    lime_per_rai = (ph_difference / 0.5) * base_rate * factor

    return {
        "lime_needed": True,
        "current_ph": current_ph,
        "target_ph": target_ph,
        "amount_kg_per_rai": round(lime_per_rai, 1),
        "total_amount_kg": round(lime_per_rai * field_size_rai, 1),
        "lime_type": "Agricultural limestone (iteiteite Cite ite ite)",
        "application_timing": "Apply 2-4 weeks before planting and incorporate",
        "message": f"Apply {round(lime_per_rai, 1)} kg/rai of agricultural lime"
    }


def assess_nutrient_level(
    nutrient: str,
    value: float,
    thresholds: Dict[str, float] | None = None
) -> Tuple[str, str]:
    """
    Assess nutrient level and return status.

    Args:
        nutrient: Nutrient name (nitrogen, phosphorus, potassium)
        value: Current level in mg/kg
        thresholds: Optional custom thresholds

    Returns:
        Tuple of (status, description)
    """
    default_thresholds = {
        "nitrogen": {"very_low": 15, "low": 30, "medium": 60, "high": 80},
        "phosphorus": {"very_low": 8, "low": 15, "medium": 30, "high": 50},
        "potassium": {"very_low": 40, "low": 80, "medium": 150, "high": 200},
    }

    thresh = thresholds or default_thresholds.get(nutrient.lower(), {
        "very_low": 10, "low": 25, "medium": 50, "high": 75
    })

    if value < thresh["very_low"]:
        return "very_low", "Critical deficiency - immediate attention needed"
    elif value < thresh["low"]:
        return "low", "Deficient - supplementation recommended"
    elif value < thresh["medium"]:
        return "medium", "Adequate - maintenance fertilization"
    elif value < thresh["high"]:
        return "high", "Sufficient - reduce fertilizer application"
    else:
        return "very_high", "Excess - no fertilizer needed, monitor for toxicity"
