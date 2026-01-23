"""
Unit tests for soil diagnosis skill.

Tests verify deterministic, rule-based behavior.
"""

from core.skills.types import (
    SoilInput,
    NutrientLevel,
    PHStatus,
    Severity,
)
from core.skills.soil import soil_diagnosis


class TestPHClassification:
    """Test pH classification logic."""

    def test_very_acidic_ph(self):
        """pH < 4.5 should be very acidic."""
        result = soil_diagnosis(SoilInput(ph=4.0))
        assert result.ph_status == PHStatus.VERY_ACIDIC
        assert result.ph_score == 30.0

    def test_acidic_ph(self):
        """pH 4.5-5.5 should be acidic."""
        result = soil_diagnosis(SoilInput(ph=5.0))
        assert result.ph_status == PHStatus.ACIDIC
        assert result.ph_score == 50.0

    def test_slightly_acidic_ph(self):
        """pH 5.5-6.0 should be slightly acidic."""
        result = soil_diagnosis(SoilInput(ph=5.7))
        assert result.ph_status == PHStatus.SLIGHTLY_ACIDIC
        assert result.ph_score == 80.0

    def test_optimal_ph(self):
        """pH 6.0-7.0 should be optimal."""
        result = soil_diagnosis(SoilInput(ph=6.5))
        assert result.ph_status == PHStatus.OPTIMAL
        assert result.ph_score == 100.0

    def test_slightly_alkaline_ph(self):
        """pH 7.0-7.5 should be slightly alkaline."""
        result = soil_diagnosis(SoilInput(ph=7.2))
        assert result.ph_status == PHStatus.SLIGHTLY_ALKALINE
        assert result.ph_score == 80.0

    def test_alkaline_ph(self):
        """pH 7.5-8.5 should be alkaline."""
        result = soil_diagnosis(SoilInput(ph=8.0))
        assert result.ph_status == PHStatus.ALKALINE
        assert result.ph_score == 50.0

    def test_very_alkaline_ph(self):
        """pH > 8.5 should be very alkaline."""
        result = soil_diagnosis(SoilInput(ph=9.0))
        assert result.ph_status == PHStatus.VERY_ALKALINE
        assert result.ph_score == 30.0


class TestNutrientClassification:
    """Test nutrient level classification."""

    def test_nitrogen_very_low(self):
        """N < 10 mg/kg should be very low."""
        result = soil_diagnosis(SoilInput(nitrogen=5))
        assert result.nitrogen_analysis is not None
        assert result.nitrogen_analysis.level == NutrientLevel.VERY_LOW
        assert result.nitrogen_analysis.deficit_kg_per_rai is not None

    def test_nitrogen_low(self):
        """N 10-20 mg/kg should be low."""
        result = soil_diagnosis(SoilInput(nitrogen=15))
        assert result.nitrogen_analysis.level == NutrientLevel.LOW

    def test_nitrogen_medium(self):
        """N 20-40 mg/kg should be medium."""
        result = soil_diagnosis(SoilInput(nitrogen=30))
        assert result.nitrogen_analysis.level == NutrientLevel.MEDIUM

    def test_nitrogen_high(self):
        """N 40-60 mg/kg should be high."""
        result = soil_diagnosis(SoilInput(nitrogen=50))
        assert result.nitrogen_analysis.level == NutrientLevel.HIGH

    def test_nitrogen_very_high(self):
        """N > 60 mg/kg should be very high."""
        result = soil_diagnosis(SoilInput(nitrogen=80))
        assert result.nitrogen_analysis.level == NutrientLevel.VERY_HIGH

    def test_phosphorus_levels(self):
        """Test phosphorus classification thresholds."""
        # Very low < 5
        result = soil_diagnosis(SoilInput(phosphorus=3))
        assert result.phosphorus_analysis.level == NutrientLevel.VERY_LOW

        # Medium 15-30
        result = soil_diagnosis(SoilInput(phosphorus=20))
        assert result.phosphorus_analysis.level == NutrientLevel.MEDIUM

    def test_potassium_levels(self):
        """Test potassium classification thresholds."""
        # Very low < 30
        result = soil_diagnosis(SoilInput(potassium=20))
        assert result.potassium_analysis.level == NutrientLevel.VERY_LOW

        # Medium 60-120
        result = soil_diagnosis(SoilInput(potassium=90))
        assert result.potassium_analysis.level == NutrientLevel.MEDIUM


class TestIssueIdentification:
    """Test issue detection logic."""

    def test_acidic_soil_issue(self):
        """Acidic soil should generate PH_LOW issue."""
        result = soil_diagnosis(SoilInput(ph=5.0))
        assert len(result.issues) > 0
        ph_issue = next((i for i in result.issues if i.code == "PH_LOW"), None)
        assert ph_issue is not None
        assert ph_issue.severity == Severity.WARNING

    def test_very_acidic_critical_issue(self):
        """Very acidic soil should generate CRITICAL issue."""
        result = soil_diagnosis(SoilInput(ph=4.0))
        ph_issue = next((i for i in result.issues if i.code == "PH_LOW"), None)
        assert ph_issue is not None
        assert ph_issue.severity == Severity.CRITICAL

    def test_alkaline_soil_issue(self):
        """Alkaline soil should generate PH_HIGH issue."""
        result = soil_diagnosis(SoilInput(ph=8.0))
        ph_issue = next((i for i in result.issues if i.code == "PH_HIGH"), None)
        assert ph_issue is not None
        assert ph_issue.severity == Severity.WARNING

    def test_low_nitrogen_issue(self):
        """Low nitrogen should generate NITROGEN_LOW issue."""
        result = soil_diagnosis(SoilInput(nitrogen=15))
        n_issue = next((i for i in result.issues if i.code == "NITROGEN_LOW"), None)
        assert n_issue is not None
        assert n_issue.affected_parameter == "nitrogen"

    def test_optimal_soil_no_issues(self):
        """Optimal soil should have no issues."""
        result = soil_diagnosis(SoilInput(
            ph=6.5,
            nitrogen=35,
            phosphorus=25,
            potassium=100,
        ))
        assert len(result.issues) == 0


class TestRecommendations:
    """Test recommendation generation."""

    def test_lime_recommendation_for_acidic(self):
        """Acidic soil should recommend lime application."""
        result = soil_diagnosis(SoilInput(ph=5.0))
        lime_rec = next(
            (r for r in result.recommendations if r.code == "LIME_APPLICATION"),
            None
        )
        assert lime_rec is not None
        assert lime_rec.priority == 1

    def test_sulfur_recommendation_for_alkaline(self):
        """Alkaline soil should recommend sulfur application."""
        result = soil_diagnosis(SoilInput(ph=8.0))
        sulfur_rec = next(
            (r for r in result.recommendations if r.code == "SULFUR_APPLICATION"),
            None
        )
        assert sulfur_rec is not None

    def test_nitrogen_recommendation(self):
        """Low nitrogen should recommend nitrogen fertilizer."""
        result = soil_diagnosis(SoilInput(nitrogen=10))
        n_rec = next(
            (r for r in result.recommendations if r.code == "ADD_NITROGEN"),
            None
        )
        assert n_rec is not None

    def test_recommendations_have_priority_order(self):
        """Multiple recommendations should have sequential priorities."""
        result = soil_diagnosis(SoilInput(
            ph=5.0,
            nitrogen=10,
            phosphorus=5,
            potassium=20,
        ))
        # Should have lime first, then nutrients
        priorities = [r.priority for r in result.recommendations]
        assert priorities == sorted(priorities)


class TestConfidenceCalculation:
    """Test confidence score calculation."""

    def test_full_inputs_full_confidence(self):
        """All inputs provided should give 100% confidence."""
        result = soil_diagnosis(SoilInput(
            ph=6.5,
            nitrogen=30,
            phosphorus=20,
            potassium=80,
        ))
        assert result.confidence == 1.0
        assert len(result.warnings) == 0

    def test_partial_inputs_reduced_confidence(self):
        """Missing inputs should reduce confidence."""
        result = soil_diagnosis(SoilInput(ph=6.5))
        assert result.confidence == 0.25  # 1 of 4 inputs
        assert len(result.warnings) > 0

    def test_no_inputs_lowest_confidence(self):
        """No inputs should give 0% confidence."""
        result = soil_diagnosis(SoilInput())
        assert result.confidence == 0.0

    def test_missing_fields_tracked(self):
        """Missing fields should be tracked."""
        result = soil_diagnosis(SoilInput(ph=6.5, nitrogen=30))
        assert "phosphorus" in result.missing_fields
        assert "potassium" in result.missing_fields
        assert "pH" in result.inputs_provided
        assert "nitrogen" in result.inputs_provided


class TestHealthScore:
    """Test overall health score calculation."""

    def test_optimal_soil_high_score(self):
        """Optimal soil should have high health score."""
        result = soil_diagnosis(SoilInput(
            ph=6.5,
            nitrogen=50,  # HIGH level for better score
            phosphorus=35,  # HIGH level for better score
            potassium=150,  # HIGH level for better score
        ))
        assert result.health_score is not None
        assert result.health_score >= 80

    def test_poor_soil_low_score(self):
        """Poor soil should have low health score."""
        result = soil_diagnosis(SoilInput(
            ph=4.0,
            nitrogen=5,
            phosphorus=3,
            potassium=20,
        ))
        assert result.health_score is not None
        assert result.health_score < 50


class TestThaiLocalization:
    """Test Thai language output."""

    def test_ph_status_has_thai(self):
        """pH status should have Thai description."""
        result = soil_diagnosis(SoilInput(ph=6.5))
        assert result.ph_status_th is not None
        assert "เหมาะสม" in result.ph_status_th

    def test_nutrient_level_has_thai(self):
        """Nutrient levels should have Thai description."""
        result = soil_diagnosis(SoilInput(nitrogen=30))
        assert result.nitrogen_analysis.level_th is not None
        assert "ปานกลาง" in result.nitrogen_analysis.level_th

    def test_summary_is_thai(self):
        """Summary should be in Thai."""
        result = soil_diagnosis(SoilInput(ph=6.5))
        assert "pH" in result.summary_th
        assert "คะแนน" in result.summary_th


class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_boundary_ph_values(self):
        """Test pH at exact boundary values."""
        # Exactly 6.0 should be optimal
        result = soil_diagnosis(SoilInput(ph=6.0))
        assert result.ph_status == PHStatus.OPTIMAL

        # Exactly 7.0 should be slightly alkaline
        result = soil_diagnosis(SoilInput(ph=7.0))
        assert result.ph_status == PHStatus.SLIGHTLY_ALKALINE

    def test_zero_nutrient_values(self):
        """Zero nutrient values should work."""
        result = soil_diagnosis(SoilInput(nitrogen=0, phosphorus=0, potassium=0))
        assert result.nitrogen_analysis.level == NutrientLevel.VERY_LOW
        assert result.phosphorus_analysis.level == NutrientLevel.VERY_LOW
        assert result.potassium_analysis.level == NutrientLevel.VERY_LOW

    def test_very_high_nutrient_values(self):
        """Very high nutrient values should be classified correctly."""
        result = soil_diagnosis(SoilInput(
            nitrogen=100,
            phosphorus=80,
            potassium=300,
        ))
        assert result.nitrogen_analysis.level == NutrientLevel.VERY_HIGH
        assert result.phosphorus_analysis.level == NutrientLevel.VERY_HIGH
        assert result.potassium_analysis.level == NutrientLevel.VERY_HIGH
