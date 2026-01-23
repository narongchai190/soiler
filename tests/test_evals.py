"""
S.O.I.L.E.R. Evaluation Suite

30 deterministic test cases for skills and RAG.
These are the core evaluation cases for CI/CD.

Structure:
- 10 soil diagnosis cases
- 10 fertilizer planning cases
- 10 RAG retrieval cases
"""

import pytest
from core.skills.types import SoilInput, FertilizerInput, NutrientLevel, PHStatus, Severity
from core.skills.soil import soil_diagnosis
from core.skills.fertilizer import fertilizer_plan
from core.rag.retriever import RAGRetriever, load_corpus, search_corpus


# =============================================================================
# SOIL DIAGNOSIS EVALS (10 cases)
# =============================================================================

class TestSoilDiagnosisEvals:
    """10 evaluation cases for soil diagnosis skill."""

    # Case 1: Optimal soil - all parameters in good range
    def test_eval_01_optimal_soil(self):
        """EVAL-SOIL-01: Optimal soil should have no issues."""
        result = soil_diagnosis(SoilInput(
            ph=6.5,
            nitrogen=35,
            phosphorus=25,
            potassium=100,
        ))
        assert result.health_score >= 70
        assert len(result.issues) == 0
        assert result.confidence == 1.0

    # Case 2: Very acidic soil
    def test_eval_02_very_acidic_soil(self):
        """EVAL-SOIL-02: Very acidic soil should have critical pH issue."""
        result = soil_diagnosis(SoilInput(ph=4.0))
        assert result.ph_status == PHStatus.VERY_ACIDIC
        assert any(i.severity == Severity.CRITICAL for i in result.issues)
        assert any(r.code == "LIME_APPLICATION" for r in result.recommendations)

    # Case 3: Very alkaline soil
    def test_eval_03_very_alkaline_soil(self):
        """EVAL-SOIL-03: Very alkaline soil should have pH issue."""
        result = soil_diagnosis(SoilInput(ph=9.0))
        assert result.ph_status == PHStatus.VERY_ALKALINE
        assert any(i.code == "PH_HIGH" for i in result.issues)
        assert any(r.code == "SULFUR_APPLICATION" for r in result.recommendations)

    # Case 4: All nutrients deficient
    def test_eval_04_all_nutrients_deficient(self):
        """EVAL-SOIL-04: All low nutrients should generate all recommendations."""
        result = soil_diagnosis(SoilInput(
            nitrogen=5,
            phosphorus=3,
            potassium=20,
        ))
        rec_codes = [r.code for r in result.recommendations]
        assert "ADD_NITROGEN" in rec_codes
        assert "ADD_PHOSPHORUS" in rec_codes
        assert "ADD_POTASSIUM" in rec_codes

    # Case 5: High nutrients - no recommendations needed
    def test_eval_05_high_nutrients(self):
        """EVAL-SOIL-05: High nutrients should not recommend more fertilizer."""
        result = soil_diagnosis(SoilInput(
            ph=6.5,
            nitrogen=70,
            phosphorus=60,
            potassium=220,
        ))
        assert result.nitrogen_analysis.level == NutrientLevel.VERY_HIGH
        # Should not recommend adding more
        assert not any(r.code == "ADD_NITROGEN" for r in result.recommendations)

    # Case 6: pH boundary - exactly 6.0
    def test_eval_06_ph_boundary_optimal(self):
        """EVAL-SOIL-06: pH 6.0 should be classified as optimal."""
        result = soil_diagnosis(SoilInput(ph=6.0))
        assert result.ph_status == PHStatus.OPTIMAL
        assert result.ph_score == 100.0

    # Case 7: Nitrogen boundary - exactly 20 (medium threshold)
    def test_eval_07_nitrogen_boundary(self):
        """EVAL-SOIL-07: Nitrogen at 20 should be medium level."""
        result = soil_diagnosis(SoilInput(nitrogen=20))
        assert result.nitrogen_analysis.level == NutrientLevel.MEDIUM

    # Case 8: Missing all inputs - lowest confidence
    def test_eval_08_no_inputs(self):
        """EVAL-SOIL-08: No inputs should have 0% confidence."""
        result = soil_diagnosis(SoilInput())
        assert result.confidence == 0.0
        assert len(result.missing_fields) == 4

    # Case 9: Partial inputs - reduced confidence
    def test_eval_09_partial_inputs(self):
        """EVAL-SOIL-09: Partial inputs should reduce confidence."""
        result = soil_diagnosis(SoilInput(ph=6.5, nitrogen=30))
        assert result.confidence == 0.5  # 2 of 4 inputs
        assert len(result.inputs_provided) == 2

    # Case 10: Thai output validation
    def test_eval_10_thai_output(self):
        """EVAL-SOIL-10: Thai descriptions should be present and correct."""
        result = soil_diagnosis(SoilInput(
            ph=5.0,
            nitrogen=15,
        ))
        # pH Thai should contain Thai text
        assert result.ph_status_th is not None
        assert "กรด" in result.ph_status_th  # Contains "acid" in Thai

        # Nutrient Thai should contain Thai text
        assert result.nitrogen_analysis.level_th is not None
        assert "ต่ำ" in result.nitrogen_analysis.level_th  # Contains "low" in Thai


# =============================================================================
# FERTILIZER PLANNING EVALS (10 cases)
# =============================================================================

class TestFertilizerPlanEvals:
    """10 evaluation cases for fertilizer planning skill."""

    # Case 11: Rice standard requirements
    def test_eval_11_rice_standard(self):
        """EVAL-FERT-11: Rice should have standard 12-6-6 requirements."""
        result = fertilizer_plan(FertilizerInput(crop="rice"))
        assert result.target_n_kg_per_rai == 12.0
        assert result.target_p2o5_kg_per_rai == 6.0
        assert result.target_k2o_kg_per_rai == 6.0

    # Case 12: Cassava high potassium
    def test_eval_12_cassava_high_k(self):
        """EVAL-FERT-12: Cassava should have high K requirement."""
        result = fertilizer_plan(FertilizerInput(crop="cassava"))
        assert result.target_k2o_kg_per_rai > result.target_n_kg_per_rai

    # Case 13: High yield target increases nutrients
    def test_eval_13_high_yield_adjustment(self):
        """EVAL-FERT-13: High yield target should increase nutrients."""
        base = fertilizer_plan(FertilizerInput(crop="rice"))
        high_yield = fertilizer_plan(FertilizerInput(
            crop="rice",
            target_yield_kg_per_rai=800,  # 60% higher than base 500
        ))
        assert high_yield.target_n_kg_per_rai > base.target_n_kg_per_rai

    # Case 14: High soil N reduces fertilizer N
    def test_eval_14_soil_adjustment(self):
        """EVAL-FERT-14: High soil N should reduce N recommendation."""
        base = fertilizer_plan(FertilizerInput(crop="rice"))
        high_soil_n = fertilizer_plan(FertilizerInput(
            crop="rice",
            soil_n=50,
        ))
        assert high_soil_n.target_n_kg_per_rai < base.target_n_kg_per_rai

    # Case 15: Budget constraint
    def test_eval_15_budget_constraint(self):
        """EVAL-FERT-15: Low budget should limit options or flag within_budget."""
        result = fertilizer_plan(FertilizerInput(
            crop="rice",
            field_size_rai=100,
            budget_thb=500,  # Very low budget
        ))
        # Should either have no options or flag not within budget
        if result.fertilizer_options:
            # Check if flagged as not within budget
            assert not result.within_budget or result.total_cost_thb <= 500

    # Case 16: Organic preference
    def test_eval_16_organic_preference(self):
        """EVAL-FERT-16: Organic preference should filter options."""
        result = fertilizer_plan(FertilizerInput(
            crop="rice",
            prefer_organic=True,
        ))
        # Should only return organic options
        for opt in result.fertilizer_options:
            # Organic compost has formula 2-1-1
            assert "Organic" in opt.name or opt.formula == "2-1-1"

    # Case 17: Cost calculation correct
    def test_eval_17_cost_calculation(self):
        """EVAL-FERT-17: Cost should scale with field size."""
        small = fertilizer_plan(FertilizerInput(crop="rice", field_size_rai=1))
        large = fertilizer_plan(FertilizerInput(crop="rice", field_size_rai=5))

        if small.fertilizer_options and large.fertilizer_options:
            # Large field should have ~5x the cost
            ratio = large.total_cost_thb / small.total_cost_thb
            assert 4 < ratio < 6  # Allow some variance

    # Case 18: Full inputs high confidence
    def test_eval_18_full_confidence(self):
        """EVAL-FERT-18: Full inputs should give 100% confidence."""
        result = fertilizer_plan(FertilizerInput(
            crop="rice",
            target_yield_kg_per_rai=500,
            soil_n=30,
            soil_p=20,
            soil_k=80,
        ))
        assert result.confidence == 1.0

    # Case 19: Disclaimers always present
    def test_eval_19_disclaimers(self):
        """EVAL-FERT-19: Disclaimers should always be present."""
        result = fertilizer_plan(FertilizerInput(crop="rice"))
        assert len(result.disclaimers) > 0
        # Should mention expert consultation
        disclaimer_text = " ".join(result.disclaimers)
        assert "ผู้เชี่ยวชาญ" in disclaimer_text or "เบื้องต้น" in disclaimer_text

    # Case 20: Unknown crop uses defaults
    def test_eval_20_unknown_crop(self):
        """EVAL-FERT-20: Unknown crop should use default requirements."""
        result = fertilizer_plan(FertilizerInput(crop="unknown_exotic_plant"))
        # Should still calculate (uses default values)
        assert result.target_n_kg_per_rai > 0
        assert result.target_p2o5_kg_per_rai > 0
        assert result.target_k2o_kg_per_rai > 0


# =============================================================================
# RAG RETRIEVAL EVALS (10 cases)
# =============================================================================

class TestRAGRetrievalEvals:
    """10 evaluation cases for RAG retrieval."""

    @pytest.fixture(autouse=True)
    def setup_retriever(self):
        """Load corpus before tests."""
        load_corpus()

    # Case 21: pH query finds pH document
    def test_eval_21_ph_retrieval(self):
        """EVAL-RAG-21: pH query should find pH standards document."""
        result = search_corpus("soil pH acidic alkaline")
        assert len(result.results) > 0
        # Should find pH document
        titles = [r.document_title.lower() for r in result.results]
        assert any("ph" in t for t in titles)

    # Case 22: NPK query finds nutrient document
    def test_eval_22_npk_retrieval(self):
        """EVAL-RAG-22: NPK query should find nutrient thresholds document."""
        result = search_corpus("nitrogen phosphorus potassium NPK thresholds")
        assert len(result.results) > 0
        # Should have relevant content
        context = result.get_context()
        assert "mg/kg" in context or "nitrogen" in context.lower()

    # Case 23: Rice fertilizer query
    def test_eval_23_rice_retrieval(self):
        """EVAL-RAG-23: Rice fertilizer query should find rice document."""
        result = search_corpus("rice fertilizer urea application")
        assert len(result.results) > 0
        titles = [r.document_title.lower() for r in result.results]
        assert any("rice" in t for t in titles)

    # Case 24: Thai language query
    def test_eval_24_thai_query(self):
        """EVAL-RAG-24: Thai query should return results."""
        result = search_corpus("ไนโตรเจน ฟอสฟอรัส โพแทสเซียม")
        # Should still find documents (keywords exist in Thai docs)
        assert len(result.results) > 0

    # Case 25: Organic fertilizer query
    def test_eval_25_organic_retrieval(self):
        """EVAL-RAG-25: Organic query should find organic document."""
        result = search_corpus("organic compost manure fertilizer")
        assert len(result.results) > 0
        titles = [r.document_title.lower() for r in result.results]
        assert any("organic" in t for t in titles)

    # Case 26: Citation format correct
    def test_eval_26_citation_format(self):
        """EVAL-RAG-26: Citations should have proper format."""
        result = search_corpus("soil texture clay loam")
        citations = result.get_citations()
        for c in citations:
            # Should have [DOC-ID] format
            assert "[" in c and "]" in c
            assert "-" in c  # Should have source separator

    # Case 27: Context extraction
    def test_eval_27_context_extraction(self):
        """EVAL-RAG-27: Context should be relevant excerpt."""
        result = search_corpus("cassava potassium tuber")
        context = result.get_context()
        # Should contain relevant text
        assert len(context) > 0
        assert "DOC" in context  # Should have document ID prefix

    # Case 28: Top-k limit respected
    def test_eval_28_top_k_limit(self):
        """EVAL-RAG-28: Top-k limit should be respected."""
        result = search_corpus("fertilizer", top_k=2)
        assert len(result.results) <= 2

    # Case 29: Empty query handling
    def test_eval_29_empty_query(self):
        """EVAL-RAG-29: Empty query should not crash."""
        result = search_corpus("")
        assert result is not None
        assert result.query == ""

    # Case 30: Document ID retrieval
    def test_eval_30_document_list(self):
        """EVAL-RAG-30: Should list all corpus documents."""
        retriever = RAGRetriever()
        retriever.load()
        docs = retriever.list_documents()

        # Should have multiple documents
        assert len(docs) >= 5  # We created at least 7 documents

        # Each should have required fields
        for doc in docs:
            assert "id" in doc
            assert "title" in doc
            assert "source" in doc


# =============================================================================
# SUMMARY TABLE GENERATION
# =============================================================================

def test_generate_eval_summary():
    """Generate summary of all eval cases."""
    summary = {
        "soil_diagnosis": 10,
        "fertilizer_plan": 10,
        "rag_retrieval": 10,
        "total": 30,
    }

    # This test always passes - it's for documentation
    assert summary["total"] == 30
    print("\n" + "=" * 60)
    print("S.O.I.L.E.R. EVALUATION SUMMARY")
    print("=" * 60)
    print(f"Soil Diagnosis Cases: {summary['soil_diagnosis']}")
    print(f"Fertilizer Plan Cases: {summary['fertilizer_plan']}")
    print(f"RAG Retrieval Cases: {summary['rag_retrieval']}")
    print(f"Total Cases: {summary['total']}")
    print("=" * 60)
