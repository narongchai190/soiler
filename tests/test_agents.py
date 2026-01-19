"""
Smoke tests for S.O.I.L.E.R. agents.
Tests that each agent can be instantiated and processes basic input.
"""
import pytest


class TestAgentInstantiation:
    """Test that all agents can be instantiated."""

    def test_soil_series_agent_init(self):
        from agents.soil_series_agent import SoilSeriesAgent
        agent = SoilSeriesAgent(verbose=False)
        assert agent.agent_name == "SoilSeriesExpert"

    def test_soil_chemistry_agent_init(self):
        from agents.soil_chemistry_agent import SoilChemistryAgent
        agent = SoilChemistryAgent(verbose=False)
        assert agent.agent_name == "SoilChemistryExpert"

    def test_crop_biology_agent_init(self):
        from agents.crop_biology_agent import CropBiologyAgent
        agent = CropBiologyAgent(verbose=False)
        assert agent.agent_name == "CropBiologyExpert"

    def test_pest_disease_agent_init(self):
        from agents.pest_disease_agent import PestDiseaseAgent
        agent = PestDiseaseAgent(verbose=False)
        assert agent.agent_name == "PestDiseaseExpert"

    def test_climate_agent_init(self):
        from agents.climate_agent import ClimateAgent
        agent = ClimateAgent(verbose=False)
        assert agent.agent_name == "ClimateExpert"

    def test_fertilizer_formula_agent_init(self):
        from agents.fertilizer_formula_agent import FertilizerFormulaAgent
        agent = FertilizerFormulaAgent(verbose=False)
        assert agent.agent_name == "FertilizerExpert"

    def test_market_cost_agent_init(self):
        from agents.market_cost_agent import MarketCostAgent
        agent = MarketCostAgent(verbose=False)
        assert agent.agent_name == "MarketCostExpert"

    def test_report_agent_init(self):
        from agents.report_agent import ReportAgent
        agent = ReportAgent(verbose=False)
        assert agent.agent_name == "ChiefReporter"


class TestAgentProcessing:
    """Test that agents can process basic input."""

    def test_soil_series_agent_process(self):
        from agents.soil_series_agent import SoilSeriesAgent
        agent = SoilSeriesAgent(verbose=False)
        result = agent.process({
            "location": "Phrae",
            "texture": "clay loam",
            "lat": 18.1,
            "lon": 100.1
        })
        assert result.success is True
        assert "observation_th" in result.payload

    def test_soil_chemistry_agent_process(self):
        from agents.soil_chemistry_agent import SoilChemistryAgent
        agent = SoilChemistryAgent(verbose=False)
        result = agent.process({
            "ph": 6.5,
            "nitrogen": 25,
            "phosphorus": 15,
            "potassium": 120,
            "target_crop": "Corn"
        })
        assert result.success is True
        assert "observation_th" in result.payload

    def test_climate_agent_process(self):
        from agents.climate_agent import ClimateAgent
        agent = ClimateAgent(verbose=False)
        result = agent.process({
            "location": "Phrae",
            "target_crop": "Corn"
        })
        assert result.success is True
        assert "observation_th" in result.payload

    def test_fertilizer_formula_agent_process(self):
        from agents.fertilizer_formula_agent import FertilizerFormulaAgent
        agent = FertilizerFormulaAgent(verbose=False)
        result = agent.process({
            "target_crop": "Corn",
            "field_size_rai": 5,
            "nitrogen": 20,
            "phosphorus": 12,
            "potassium": 100,
            "budget_thb": 10000
        })
        assert result.success is True
        assert "observation_th" in result.payload
