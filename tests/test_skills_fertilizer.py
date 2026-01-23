"""
Unit tests for fertilizer planning skill.

Tests verify deterministic, rule-based behavior.
"""

import pytest
from core.skills.types import FertilizerInput
from core.skills.fertilizer import fertilizer_plan


class TestCropRequirements:
    """Test crop-specific nutrient requirements."""

    def test_rice_requirements(self):
        """Rice should have standard N-P-K requirements."""
        result = fertilizer_plan(FertilizerInput(crop="rice"))
        assert result.target_n_kg_per_rai > 0
        assert result.target_p2o5_kg_per_rai > 0
        assert result.target_k2o_kg_per_rai > 0
        # Rice standard: 12-6-6
        assert result.target_n_kg_per_rai == 12.0
        assert result.target_p2o5_kg_per_rai == 6.0

    def test_cassava_high_potassium(self):
        """Cassava should have high potassium requirement."""
        result = fertilizer_plan(FertilizerInput(crop="cassava"))
        # Cassava needs more K than N
        assert result.target_k2o_kg_per_rai > result.target_n_kg_per_rai

    def test_unknown_crop_uses_default(self):
        """Unknown crop should use default requirements."""
        result = fertilizer_plan(FertilizerInput(crop="unknown_crop"))
        assert result.target_n_kg_per_rai > 0
        # Should have assumptions about using default
        assert len(result.assumptions) > 0 or len(result.warnings) > 0

    def test_case_insensitive_crop(self):
        """Crop name should be case-insensitive."""
        result1 = fertilizer_plan(FertilizerInput(crop="Rice"))
        result2 = fertilizer_plan(FertilizerInput(crop="RICE"))
        result3 = fertilizer_plan(FertilizerInput(crop="rice"))
        assert result1.target_n_kg_per_rai == result2.target_n_kg_per_rai
        assert result2.target_n_kg_per_rai == result3.target_n_kg_per_rai


class TestYieldAdjustment:
    """Test target yield adjustments."""

    def test_higher_yield_increases_requirements(self):
        """Higher target yield should increase nutrient requirements."""
        base_result = fertilizer_plan(FertilizerInput(crop="rice"))
        high_yield_result = fertilizer_plan(FertilizerInput(
            crop="rice",
            target_yield_kg_per_rai=800,  # Higher than base 500
        ))
        assert high_yield_result.target_n_kg_per_rai > base_result.target_n_kg_per_rai

    def test_lower_yield_decreases_requirements(self):
        """Lower target yield should decrease nutrient requirements."""
        base_result = fertilizer_plan(FertilizerInput(crop="rice"))
        low_yield_result = fertilizer_plan(FertilizerInput(
            crop="rice",
            target_yield_kg_per_rai=300,  # Lower than base 500
        ))
        assert low_yield_result.target_n_kg_per_rai < base_result.target_n_kg_per_rai

    def test_yield_factor_capped(self):
        """Yield adjustment factor should be capped."""
        # Extremely high yield shouldn't cause unreasonable recommendations
        result = fertilizer_plan(FertilizerInput(
            crop="rice",
            target_yield_kg_per_rai=5000,  # 10x normal
        ))
        # Factor should be capped at 2.0
        assert result.target_n_kg_per_rai <= 12.0 * 2.0


class TestSoilAdjustment:
    """Test soil nutrient adjustments."""

    def test_high_soil_n_reduces_requirement(self):
        """High soil N should reduce N fertilizer recommendation."""
        base_result = fertilizer_plan(FertilizerInput(crop="rice"))
        high_n_result = fertilizer_plan(FertilizerInput(
            crop="rice",
            soil_n=50,  # High soil N
        ))
        assert high_n_result.target_n_kg_per_rai < base_result.target_n_kg_per_rai

    def test_high_soil_p_reduces_requirement(self):
        """High soil P should reduce P fertilizer recommendation."""
        base_result = fertilizer_plan(FertilizerInput(crop="rice"))
        high_p_result = fertilizer_plan(FertilizerInput(
            crop="rice",
            soil_p=40,  # High soil P
        ))
        assert high_p_result.target_p2o5_kg_per_rai < base_result.target_p2o5_kg_per_rai

    def test_high_soil_k_reduces_requirement(self):
        """High soil K should reduce K fertilizer recommendation."""
        base_result = fertilizer_plan(FertilizerInput(crop="rice"))
        high_k_result = fertilizer_plan(FertilizerInput(
            crop="rice",
            soil_k=150,  # High soil K
        ))
        assert high_k_result.target_k2o_kg_per_rai < base_result.target_k2o_kg_per_rai


class TestFertilizerOptions:
    """Test fertilizer option generation."""

    def test_options_generated(self):
        """Fertilizer options should be generated."""
        result = fertilizer_plan(FertilizerInput(crop="rice"))
        assert len(result.fertilizer_options) > 0

    def test_options_sorted_by_cost(self):
        """Options should be sorted by cost (lowest first)."""
        result = fertilizer_plan(FertilizerInput(crop="rice", field_size_rai=5))
        if len(result.fertilizer_options) > 1:
            costs = [opt.total_cost for opt in result.fertilizer_options]
            assert costs == sorted(costs)

    def test_recommended_option_index_valid(self):
        """Recommended option index should be valid."""
        result = fertilizer_plan(FertilizerInput(crop="rice"))
        if result.fertilizer_options:
            assert 0 <= result.recommended_option_index < len(result.fertilizer_options)

    def test_organic_preference(self):
        """Organic preference should filter options."""
        result = fertilizer_plan(FertilizerInput(
            crop="rice",
            prefer_organic=True,
        ))
        # All options should be organic
        for opt in result.fertilizer_options:
            # Organic compost formula is 2-1-1
            assert "Organic" in opt.name or opt.formula == "2-1-1"


class TestBudgetConstraint:
    """Test budget constraint handling."""

    def test_within_budget_flag(self):
        """Within budget flag should be set correctly."""
        result = fertilizer_plan(FertilizerInput(
            crop="rice",
            field_size_rai=1,
            budget_thb=1000,
        ))
        if result.fertilizer_options:
            assert result.within_budget == (result.total_cost_thb <= 1000)

    def test_low_budget_limits_options(self):
        """Low budget should limit available options."""
        low_budget_result = fertilizer_plan(FertilizerInput(
            crop="rice",
            field_size_rai=10,
            budget_thb=100,  # Very low budget
        ))
        high_budget_result = fertilizer_plan(FertilizerInput(
            crop="rice",
            field_size_rai=10,
            budget_thb=10000,  # High budget
        ))
        assert len(low_budget_result.fertilizer_options) <= len(high_budget_result.fertilizer_options)


class TestFieldSize:
    """Test field size calculations."""

    def test_larger_field_higher_total_cost(self):
        """Larger field should have higher total cost."""
        small_field = fertilizer_plan(FertilizerInput(crop="rice", field_size_rai=1))
        large_field = fertilizer_plan(FertilizerInput(crop="rice", field_size_rai=10))

        if small_field.fertilizer_options and large_field.fertilizer_options:
            # Compare same fertilizer type if possible
            small_cost = small_field.total_cost_thb
            large_cost = large_field.total_cost_thb
            assert large_cost > small_cost

    def test_cost_per_rai_consistent(self):
        """Cost per rai should be similar regardless of field size."""
        small_field = fertilizer_plan(FertilizerInput(crop="rice", field_size_rai=1))
        large_field = fertilizer_plan(FertilizerInput(crop="rice", field_size_rai=10))

        if small_field.fertilizer_options and large_field.fertilizer_options:
            # Cost per rai should be within 10% (rounding differences)
            diff = abs(small_field.cost_per_rai_thb - large_field.cost_per_rai_thb)
            assert diff < small_field.cost_per_rai_thb * 0.1


class TestConfidenceCalculation:
    """Test confidence score calculation."""

    def test_full_inputs_high_confidence(self):
        """All inputs should give high confidence."""
        result = fertilizer_plan(FertilizerInput(
            crop="rice",
            target_yield_kg_per_rai=500,
            soil_n=30,
            soil_p=20,
            soil_k=80,
        ))
        assert result.confidence == 1.0

    def test_missing_inputs_lower_confidence(self):
        """Missing inputs should lower confidence."""
        result = fertilizer_plan(FertilizerInput(crop="rice"))
        assert result.confidence < 1.0

    def test_inputs_tracked(self):
        """Provided and missing inputs should be tracked."""
        result = fertilizer_plan(FertilizerInput(
            crop="rice",
            soil_n=30,
        ))
        assert "crop" in result.inputs_provided
        assert "soil_n" in result.inputs_provided
        assert "soil_p" in result.missing_fields
        assert "soil_k" in result.missing_fields


class TestCalculationDetails:
    """Test calculation transparency."""

    def test_calculation_method_documented(self):
        """Calculation method should be documented."""
        result = fertilizer_plan(FertilizerInput(crop="rice"))
        assert result.calculation_method != ""
        assert len(result.calculation_method) > 0

    def test_calculation_details_provided(self):
        """Calculation details should be provided."""
        result = fertilizer_plan(FertilizerInput(
            crop="rice",
            target_yield_kg_per_rai=600,
            soil_n=50,
        ))
        assert "base_n" in result.calculation_details
        assert "yield_factor" in result.calculation_details
        assert "soil_n_adjustment" in result.calculation_details


class TestThaiLocalization:
    """Test Thai language output."""

    def test_summary_is_thai(self):
        """Summary should be in Thai."""
        result = fertilizer_plan(FertilizerInput(crop="rice"))
        assert "แผนปุ๋ย" in result.summary_th
        assert "กก./ไร่" in result.summary_th

    def test_fertilizer_names_have_thai(self):
        """Fertilizer options should have Thai names."""
        result = fertilizer_plan(FertilizerInput(crop="rice"))
        for opt in result.fertilizer_options:
            assert opt.name_th is not None
            assert len(opt.name_th) > 0

    def test_timing_has_thai(self):
        """Application timing should have Thai description."""
        result = fertilizer_plan(FertilizerInput(crop="rice"))
        for opt in result.fertilizer_options:
            assert opt.application_timing_th is not None


class TestDisclaimers:
    """Test disclaimer generation."""

    def test_disclaimers_always_present(self):
        """Disclaimers should always be included."""
        result = fertilizer_plan(FertilizerInput(crop="rice"))
        assert len(result.disclaimers) > 0

    def test_disclaimers_mention_expert(self):
        """Disclaimers should mention consulting experts."""
        result = fertilizer_plan(FertilizerInput(crop="rice"))
        disclaimer_text = " ".join(result.disclaimers)
        assert "ผู้เชี่ยวชาญ" in disclaimer_text or "เบื้องต้น" in disclaimer_text


class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_zero_field_size_handled(self):
        """Zero field size should be rejected by Pydantic."""
        with pytest.raises(ValueError):
            FertilizerInput(crop="rice", field_size_rai=0)

    def test_empty_crop_handled(self):
        """Empty crop should use default requirements."""
        result = fertilizer_plan(FertilizerInput(crop=""))
        # Should still produce a result with defaults
        assert result.target_n_kg_per_rai > 0

    def test_zero_soil_values(self):
        """Zero soil values should not cause errors."""
        result = fertilizer_plan(FertilizerInput(
            crop="rice",
            soil_n=0,
            soil_p=0,
            soil_k=0,
        ))
        # Should still calculate without soil adjustment
        assert result.target_n_kg_per_rai > 0

    def test_no_options_warning(self):
        """Should warn when no options available."""
        result = fertilizer_plan(FertilizerInput(
            crop="rice",
            field_size_rai=100,
            budget_thb=1,  # Impossibly low budget
        ))
        if not result.fertilizer_options:
            assert any("ไม่พบ" in w for w in result.warnings)


class TestIntegrationWithSoilDiagnosis:
    """Test integration with soil diagnosis results."""

    def test_accepts_soil_diagnosis_values(self):
        """Should accept values from soil diagnosis."""
        # Simulating values that would come from soil diagnosis
        result = fertilizer_plan(FertilizerInput(
            crop="rice",
            soil_ph=5.5,  # From diagnosis
            soil_n=15,    # From diagnosis
            soil_p=10,    # From diagnosis
            soil_k=50,    # From diagnosis
        ))
        assert result.target_n_kg_per_rai > 0
        assert result.confidence > 0.5
