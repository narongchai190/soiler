"""
Integration test for S.O.I.L.E.R. pipeline.
Tests that the full orchestrator pipeline runs successfully.
"""


class TestPipeline:
    """Test the full analysis pipeline."""

    def test_orchestrator_initialization(self):
        """Test that orchestrator can be initialized."""
        from core.orchestrator import SoilerOrchestrator
        orchestrator = SoilerOrchestrator(verbose=False)
        assert orchestrator is not None

    def test_full_pipeline_execution(self):
        """Test that full pipeline executes without errors."""
        from core.orchestrator import SoilerOrchestrator

        orchestrator = SoilerOrchestrator(verbose=False)

        result = orchestrator.analyze(
            location="Long District, Phrae Province",
            crop="Corn",
            ph=6.2,
            nitrogen=20,
            phosphorus=12,
            potassium=110,
            field_size_rai=15,
            budget_thb=15000
        )

        # Check result structure
        assert result is not None
        assert isinstance(result, dict)

        # Check essential keys exist (session_id is in report_metadata)
        assert "report_metadata" in result
        assert "session_id" in result["report_metadata"]

    def test_pipeline_returns_complete_report(self):
        """Test that pipeline returns complete report for valid input."""
        from core.orchestrator import SoilerOrchestrator

        orchestrator = SoilerOrchestrator(verbose=False)

        result = orchestrator.analyze(
            location="Den Chai, Phrae",
            crop="Corn",
            ph=6.5,
            nitrogen=30,
            phosphorus=20,
            potassium=150,
            field_size_rai=10,
            budget_thb=20000
        )

        # Check report structure contains expected sections
        assert "executive_summary" in result
        assert "dashboard" in result
        assert "project_info" in result


class TestSchemas:
    """Test Pydantic schemas."""

    def test_soil_texture_enum(self):
        """Test soil texture enum values."""
        from core.schemas import SoilTexture
        assert SoilTexture.CLAY == "clay"
        assert SoilTexture.LOAM == "loam"

    def test_fertility_level_enum(self):
        """Test fertility level enum values."""
        from core.schemas import FertilityLevel
        assert FertilityLevel.LOW == "low"
        assert FertilityLevel.HIGH == "high"
