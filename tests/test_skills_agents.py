"""
Unit tests for skill-based agents.

Tests verify that skill agents integrate properly with the orchestrator pipeline.
"""

from core.skills.skill_agent import (
    SkillBasedSoilChemistryAgent,
    SkillBasedFertilizerAgent,
    get_skill_based_agents,
)


class TestSkillBasedSoilChemistryAgent:
    """Test soil chemistry skill agent."""

    def test_process_returns_success(self):
        """Agent should return successful response."""
        agent = SkillBasedSoilChemistryAgent(verbose=False)
        response = agent.process({
            "ph": 6.5,
            "nitrogen": 30,
            "phosphorus": 20,
            "potassium": 100,
        })
        assert response.success is True
        assert response.payload is not None

    def test_payload_has_required_fields(self):
        """Payload should have all required fields for orchestrator."""
        agent = SkillBasedSoilChemistryAgent(verbose=False)
        response = agent.process({
            "ph": 6.5,
            "nitrogen": 30,
        })

        payload = response.payload
        assert "health_score" in payload
        assert "ph_analysis" in payload
        assert "nutrient_analysis" in payload
        assert "issues" in payload
        assert "recommendations" in payload
        assert "observation_th" in payload

    def test_payload_has_grounding_metadata(self):
        """Payload should have grounding metadata."""
        agent = SkillBasedSoilChemistryAgent(verbose=False)
        response = agent.process({"ph": 6.5})

        payload = response.payload
        assert payload["grounded"] is True
        assert "confidence" in payload
        assert "inputs_provided" in payload
        assert "missing_fields" in payload
        assert "assumptions" in payload
        assert "warnings" in payload
        assert "disclaimers" in payload

    def test_observation_in_thai(self):
        """Observation should be in Thai."""
        agent = SkillBasedSoilChemistryAgent(verbose=False)
        response = agent.process({"ph": 6.5})

        observation = response.payload["observation_th"]
        assert len(observation) > 0
        # Should contain Thai text
        assert "pH" in observation or "คะแนน" in observation

    def test_issues_formatted_correctly(self):
        """Issues should be formatted for orchestrator."""
        agent = SkillBasedSoilChemistryAgent(verbose=False)
        response = agent.process({
            "ph": 4.5,  # Acidic - will generate issue
            "nitrogen": 5,  # Very low - will generate issue
        })

        issues = response.payload["issues"]
        assert len(issues) > 0
        for issue in issues:
            assert "code" in issue
            assert "description" in issue
            assert "description_th" in issue
            assert "severity" in issue

    def test_recommendations_formatted_correctly(self):
        """Recommendations should be formatted for orchestrator."""
        agent = SkillBasedSoilChemistryAgent(verbose=False)
        response = agent.process({
            "ph": 5.0,  # Acidic - will generate lime recommendation
        })

        recs = response.payload["recommendations"]
        assert len(recs) > 0
        for rec in recs:
            assert "code" in rec
            assert "action" in rec
            assert "action_th" in rec
            assert "priority" in rec

    def test_handles_missing_inputs(self):
        """Agent should handle missing inputs gracefully."""
        agent = SkillBasedSoilChemistryAgent(verbose=False)
        response = agent.process({})  # Empty input

        assert response.success is True
        assert response.payload["confidence"] == 0.0
        assert len(response.payload["missing_fields"]) > 0


class TestSkillBasedFertilizerAgent:
    """Test fertilizer planning skill agent."""

    def test_process_returns_success(self):
        """Agent should return successful response."""
        agent = SkillBasedFertilizerAgent(verbose=False)
        response = agent.process({
            "target_crop": "rice",
            "field_size_rai": 5,
        })
        assert response.success is True
        assert response.payload is not None

    def test_payload_has_required_fields(self):
        """Payload should have all required fields for orchestrator."""
        agent = SkillBasedFertilizerAgent(verbose=False)
        response = agent.process({
            "target_crop": "rice",
        })

        payload = response.payload
        assert "nutrient_targets" in payload
        assert "fertilizer_options" in payload
        assert "cost_analysis" in payload
        assert "observation_th" in payload

    def test_nutrient_targets_present(self):
        """Nutrient targets should be calculated."""
        agent = SkillBasedFertilizerAgent(verbose=False)
        response = agent.process({
            "target_crop": "rice",
        })

        targets = response.payload["nutrient_targets"]
        assert "n_kg_per_rai" in targets
        assert "p2o5_kg_per_rai" in targets
        assert "k2o_kg_per_rai" in targets
        assert targets["n_kg_per_rai"] > 0

    def test_fertilizer_options_formatted(self):
        """Fertilizer options should be formatted for orchestrator."""
        agent = SkillBasedFertilizerAgent(verbose=False)
        response = agent.process({
            "target_crop": "rice",
            "field_size_rai": 1,
        })

        options = response.payload["fertilizer_options"]
        assert len(options) > 0
        for opt in options:
            assert "name" in opt
            assert "name_th" in opt
            assert "formula" in opt
            assert "rate_kg_per_rai" in opt
            assert "total_cost" in opt

    def test_cost_analysis_present(self):
        """Cost analysis should be included."""
        agent = SkillBasedFertilizerAgent(verbose=False)
        response = agent.process({
            "target_crop": "rice",
            "field_size_rai": 5,
            "budget_thb": 5000,
        })

        cost = response.payload["cost_analysis"]
        assert "total_cost" in cost
        assert "cost_per_rai" in cost
        assert "within_budget" in cost

    def test_payload_has_grounding_metadata(self):
        """Payload should have grounding metadata."""
        agent = SkillBasedFertilizerAgent(verbose=False)
        response = agent.process({"target_crop": "rice"})

        payload = response.payload
        assert payload["grounded"] is True
        assert "confidence" in payload
        assert "disclaimers" in payload
        assert len(payload["disclaimers"]) > 0

    def test_observation_in_thai(self):
        """Observation should be in Thai."""
        agent = SkillBasedFertilizerAgent(verbose=False)
        response = agent.process({"target_crop": "rice"})

        observation = response.payload["observation_th"]
        assert len(observation) > 0
        assert "กก./ไร่" in observation or "บาท" in observation

    def test_soil_inputs_adjust_targets(self):
        """Soil nutrient inputs should adjust fertilizer targets."""
        agent = SkillBasedFertilizerAgent(verbose=False)

        # Without soil data
        response1 = agent.process({"target_crop": "rice"})
        n1 = response1.payload["nutrient_targets"]["n_kg_per_rai"]

        # With high soil N
        response2 = agent.process({
            "target_crop": "rice",
            "nitrogen": 50,  # High soil N
        })
        n2 = response2.payload["nutrient_targets"]["n_kg_per_rai"]

        # High soil N should reduce fertilizer N requirement
        assert n2 < n1


class TestGetSkillBasedAgents:
    """Test agent factory function."""

    def test_returns_all_agents(self):
        """Should return all skill-based agents."""
        agents = get_skill_based_agents(verbose=False)
        assert "soil_chemistry" in agents
        assert "fertilizer" in agents

    def test_agents_are_correct_types(self):
        """Agents should be correct types."""
        agents = get_skill_based_agents(verbose=False)
        assert isinstance(agents["soil_chemistry"], SkillBasedSoilChemistryAgent)
        assert isinstance(agents["fertilizer"], SkillBasedFertilizerAgent)


class TestAgentPipelineCompatibility:
    """Test that agents work in pipeline scenarios."""

    def test_can_chain_soil_to_fertilizer(self):
        """Soil agent output can inform fertilizer agent."""
        soil_agent = SkillBasedSoilChemistryAgent(verbose=False)
        fert_agent = SkillBasedFertilizerAgent(verbose=False)

        # Run soil analysis
        soil_response = soil_agent.process({
            "ph": 6.0,
            "nitrogen": 25,
            "phosphorus": 15,
            "potassium": 80,
        })

        # Use soil results for fertilizer planning
        fert_response = fert_agent.process({
            "target_crop": "rice",
            "field_size_rai": 5,
            "nitrogen": 25,
            "phosphorus": 15,
            "potassium": 80,
            "previous_observation_th": soil_response.payload["observation_th"],
        })

        assert soil_response.success is True
        assert fert_response.success is True
        assert fert_response.payload["grounded"] is True

    def test_observation_chain_preserved(self):
        """Observations should be usable in chain."""
        soil_agent = SkillBasedSoilChemistryAgent(verbose=False)
        fert_agent = SkillBasedFertilizerAgent(verbose=False)

        soil_response = soil_agent.process({"ph": 6.5})
        soil_obs = soil_response.payload["observation_th"]

        fert_response = fert_agent.process({
            "target_crop": "rice",
            "previous_observation_th": soil_obs,
        })
        fert_obs = fert_response.payload["observation_th"]

        # Both observations should be non-empty
        assert len(soil_obs) > 0
        assert len(fert_obs) > 0
