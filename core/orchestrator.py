"""
S.O.I.L.E.R. Orchestrator - Version 2.0
ระบบประสานงาน Multi-Agent สำหรับการเกษตรอัจฉริยะ

The main "Commander" that coordinates all 8 specialized agents in the analysis pipeline.
All agent observations are in Thai language.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional
import uuid

# New 9-Agent Architecture (8 agents + orchestrator)
from agents.soil_series_agent import SoilSeriesAgent
from agents.soil_chemistry_agent import SoilChemistryAgent
from agents.crop_biology_agent import CropBiologyAgent
from agents.pest_disease_agent import PestDiseaseAgent
from agents.climate_agent import ClimateAgent
from agents.fertilizer_formula_agent import FertilizerFormulaAgent
from agents.market_cost_agent import MarketCostAgent
from agents.report_agent import ReportAgent


class SoilerOrchestrator:
    """
    S.O.I.L.E.R. Orchestrator (Commander) - ผู้ประสานงาน

    Coordinates the 8-agent workflow pipeline:
    ┌────────────────────────────────────────────────────────────────────────────────────┐
    │ INPUT → [ชุดดิน] → [เคมีดิน] → [ชีววิทยาพืช] → [โรคแมลง] →                           │
    │         [ภูมิอากาศ] → [สูตรปุ๋ย] → [ตลาด] → [รายงาน] → OUTPUT                        │
    └────────────────────────────────────────────────────────────────────────────────────┘

    Each agent passes its Thai "Observation" (ข้อสังเกต) to the next agent in the chain,
    enabling context-aware decision making throughout the pipeline.

    Usage:
        orchestrator = SoilerOrchestrator()
        result = orchestrator.analyze(
            location="อำเภอเด่นชัย",
            crop="Riceberry Rice",
            ph=6.2,
            nitrogen=35,
            phosphorus=20,
            potassium=120,
            field_size_rai=5.0
        )
    """

    AGENT_SEQUENCE_TH = [
        ("SoilSeriesExpert", "ผู้เชี่ยวชาญชุดดิน"),
        ("SoilChemistryExpert", "ผู้เชี่ยวชาญเคมีดิน"),
        ("CropBiologyExpert", "ผู้เชี่ยวชาญชีววิทยาพืช"),
        ("PestDiseaseExpert", "ผู้เชี่ยวชาญโรคและแมลง"),
        ("ClimateExpert", "ผู้เชี่ยวชาญภูมิอากาศ"),
        ("FertilizerExpert", "ผู้เชี่ยวชาญสูตรปุ๋ย"),
        ("MarketCostExpert", "ผู้เชี่ยวชาญตลาดและต้นทุน"),
        ("ChiefReporter", "ผู้สรุปรายงาน"),
    ]

    def __init__(self, verbose: bool = True):
        """
        Initialize the S.O.I.L.E.R. orchestrator with all 8 agents.

        Args:
            verbose: Whether to show agent thinking logs
        """
        self.verbose = verbose

        # Initialize all 8 agents
        self.soil_series_agent = SoilSeriesAgent(verbose=verbose)
        self.soil_chemistry_agent = SoilChemistryAgent(verbose=verbose)
        self.crop_biology_agent = CropBiologyAgent(verbose=verbose)
        self.pest_disease_agent = PestDiseaseAgent(verbose=verbose)
        self.climate_agent = ClimateAgent(verbose=verbose)
        self.fertilizer_agent = FertilizerFormulaAgent(verbose=verbose)
        self.market_agent = MarketCostAgent(verbose=verbose)
        self.report_agent = ReportAgent(verbose=verbose)

        self._session_id: Optional[str] = None
        self._analysis_history: list = []
        self._agent_observations: List[Dict[str, str]] = []

    def _print_header(self, text: str) -> None:
        """Print a formatted header."""
        if self.verbose:
            width = 70
            print("\n" + "═" * width)
            print(f"🌱 S.O.I.L.E.R. | {text}")
            print("═" * width)

    def _print_section(self, step: int, total: int, title: str, title_th: str) -> None:
        """Print a section divider with step counter."""
        if self.verbose:
            print(f"\n{'─' * 50}")
            print(f"📋 ขั้นตอน {step}/{total}: {title_th}")
            print(f"   ({title})")
            print("─" * 50)

    def _print_pipeline(self, current_step: int) -> None:
        """Print visual pipeline status."""
        if not self.verbose:
            return

        stages_th = ["ชุดดิน", "เคมีดิน", "ชีววิทยา", "โรคแมลง", "ภูมิอากาศ", "ปุ๋ย", "ตลาด", "รายงาน"]
        pipeline = ""
        for i, stage in enumerate(stages_th):
            if i < current_step:
                pipeline += f"[✓ {stage}] → "
            elif i == current_step:
                pipeline += f"[▶ {stage}] → "
            else:
                pipeline += f"[○ {stage}] → "
        print(f"\n🔄 สถานะ: {pipeline[:-3]}")

    def _generate_session_id(self) -> str:
        """Generate unique session ID."""
        return f"SESSION-{datetime.now().strftime('%Y%m%d%H%M%S')}-{uuid.uuid4().hex[:6].upper()}"

    def _collect_observation(self, agent_name: str, agent_name_th: str, observation_th: str) -> None:
        """Collect Thai observation from an agent."""
        self._agent_observations.append({
            "agent": agent_name,
            "agent_th": agent_name_th,
            "observation_th": observation_th,
            "timestamp": datetime.now().isoformat()
        })

    def analyze(
        self,
        location: str,
        crop: str,
        ph: float,
        nitrogen: float,
        phosphorus: float,
        potassium: float,
        field_size_rai: float = 1.0,
        texture: str = "loam",
        lat: float = 18.0,
        lon: float = 99.8,
        planting_date: Optional[str] = None,
        budget_thb: Optional[float] = None,
        prefer_organic: bool = False,
        irrigation_available: bool = True
    ) -> Dict[str, Any]:
        """
        Run complete 8-agent analysis pipeline with Thai observations.

        Args:
            location: Field location (e.g., "อำเภอเด่นชัย, แพร่")
            crop: Target crop name (e.g., "Riceberry Rice", "Corn")
            ph: Soil pH value (0-14)
            nitrogen: Nitrogen content in mg/kg
            phosphorus: Available phosphorus in mg/kg
            potassium: Exchangeable potassium in mg/kg
            field_size_rai: Field size in rai (1 rai = 1,600 m²)
            texture: Soil texture (e.g., "clay loam", "sandy loam")
            lat: Latitude coordinate
            lon: Longitude coordinate
            planting_date: Optional planting date (ISO format)
            budget_thb: Optional budget constraint in Thai Baht
            prefer_organic: Whether to prioritize organic options
            irrigation_available: Whether irrigation is available

        Returns:
            Complete S.O.I.L.E.R. Executive Report with Thai observations
        """
        # Initialize session
        self._session_id = self._generate_session_id()
        self._agent_observations = []
        sample_id = f"SOIL-{datetime.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:4].upper()}"

        self._print_header("เริ่มวิเคราะห์ Multi-Agent Pipeline")
        if self.verbose:
            print(f"🔑 Session ID: {self._session_id}")
            print(f"🧪 Sample ID: {sample_id}")
            print(f"📍 ตำแหน่ง: {location}")
            print(f"🌾 พืชเป้าหมาย: {crop}")
            print(f"📐 ขนาดพื้นที่: {field_size_rai} ไร่ ({field_size_rai * 0.16:.2f} เฮกตาร์)")
            print(f"\n🤖 ทีม Agent: {' → '.join([a[1] for a in self.AGENT_SEQUENCE_TH])}")

        total_steps = 8

        # ═══════════════════════════════════════════════════════════════
        # STEP 1: Soil Series Identification
        # ═══════════════════════════════════════════════════════════════
        self._print_pipeline(0)
        self._print_section(1, total_steps, "Soil Series Expert", "ผู้เชี่ยวชาญชุดดิน")

        soil_series_input = {
            "request_id": f"{self._session_id}-SERIES",
            "sample_id": sample_id,
            "location": location,
            "lat": lat,
            "lon": lon,
            "texture": texture,
            "target_crop": crop
        }

        soil_series_response = self.soil_series_agent.process(soil_series_input)

        if not soil_series_response.success:
            return self._build_error_response("การระบุชุดดินล้มเหลว", soil_series_response.error_message)

        soil_series_analysis = soil_series_response.payload
        self._collect_observation(
            "SoilSeriesExpert", "ผู้เชี่ยวชาญชุดดิน",
            soil_series_analysis.get("observation_th", "")
        )

        # ═══════════════════════════════════════════════════════════════
        # STEP 2: Soil Chemistry Analysis
        # ═══════════════════════════════════════════════════════════════
        self._print_pipeline(1)
        self._print_section(2, total_steps, "Soil Chemistry Expert", "ผู้เชี่ยวชาญเคมีดิน")

        soil_chemistry_input = {
            "request_id": f"{self._session_id}-CHEM",
            "ph": ph,
            "nitrogen": nitrogen,
            "phosphorus": phosphorus,
            "potassium": potassium,
            "target_crop": crop,
            "previous_observation_th": soil_series_analysis.get("observation_th", "")
        }

        soil_chemistry_response = self.soil_chemistry_agent.process(soil_chemistry_input)

        if not soil_chemistry_response.success:
            return self._build_error_response("การวิเคราะห์เคมีดินล้มเหลว", soil_chemistry_response.error_message)

        soil_chemistry_analysis = soil_chemistry_response.payload
        self._collect_observation(
            "SoilChemistryExpert", "ผู้เชี่ยวชาญเคมีดิน",
            soil_chemistry_analysis.get("observation_th", "")
        )

        # ═══════════════════════════════════════════════════════════════
        # STEP 3: Crop Biology Analysis
        # ═══════════════════════════════════════════════════════════════
        self._print_pipeline(2)
        self._print_section(3, total_steps, "Crop Biology Expert", "ผู้เชี่ยวชาญชีววิทยาพืช")

        crop_biology_input = {
            "request_id": f"{self._session_id}-CROP",
            "target_crop": crop,
            "field_size_rai": field_size_rai,
            "soil_health_score": soil_chemistry_analysis.get("health_score", 70),
            "planting_date": planting_date,
            "irrigation_available": irrigation_available,
            "previous_observation_th": soil_chemistry_analysis.get("observation_th", "")
        }

        crop_biology_response = self.crop_biology_agent.process(crop_biology_input)

        if not crop_biology_response.success:
            return self._build_error_response("การวิเคราะห์ชีววิทยาพืชล้มเหลว", crop_biology_response.error_message)

        crop_biology_analysis = crop_biology_response.payload
        self._collect_observation(
            "CropBiologyExpert", "ผู้เชี่ยวชาญชีววิทยาพืช",
            crop_biology_analysis.get("observation_th", "")
        )

        # ═══════════════════════════════════════════════════════════════
        # STEP 4: Pest & Disease Analysis
        # ═══════════════════════════════════════════════════════════════
        self._print_pipeline(3)
        self._print_section(4, total_steps, "Pest & Disease Expert", "ผู้เชี่ยวชาญโรคและแมลง")

        pest_disease_input = {
            "request_id": f"{self._session_id}-PEST",
            "target_crop": crop,
            "season": "rainy",  # Can be determined from planting date
            "humidity": 75,
            "irrigation_available": irrigation_available,
            "previous_observation_th": crop_biology_analysis.get("observation_th", "")
        }

        pest_disease_response = self.pest_disease_agent.process(pest_disease_input)

        if not pest_disease_response.success:
            return self._build_error_response("การวิเคราะห์โรคและแมลงล้มเหลว", pest_disease_response.error_message)

        pest_disease_analysis = pest_disease_response.payload
        self._collect_observation(
            "PestDiseaseExpert", "ผู้เชี่ยวชาญโรคและแมลง",
            pest_disease_analysis.get("observation_th", "")
        )

        # ═══════════════════════════════════════════════════════════════
        # STEP 5: Climate Analysis
        # ═══════════════════════════════════════════════════════════════
        self._print_pipeline(4)
        self._print_section(5, total_steps, "Climate Expert", "ผู้เชี่ยวชาญภูมิอากาศ")

        climate_input = {
            "request_id": f"{self._session_id}-CLIMATE",
            "location": location,
            "lat": lat,
            "lon": lon,
            "target_crop": crop,
            "planting_date": planting_date,
            "growth_cycle_days": crop_biology_analysis.get("growth_cycle_days", 120),
            "previous_observation_th": pest_disease_analysis.get("observation_th", "")
        }

        climate_response = self.climate_agent.process(climate_input)

        if not climate_response.success:
            return self._build_error_response("การวิเคราะห์ภูมิอากาศล้มเหลว", climate_response.error_message)

        climate_analysis = climate_response.payload
        self._collect_observation(
            "ClimateExpert", "ผู้เชี่ยวชาญภูมิอากาศ",
            climate_analysis.get("observation_th", "")
        )

        # ═══════════════════════════════════════════════════════════════
        # STEP 6: Fertilizer Formula
        # ═══════════════════════════════════════════════════════════════
        self._print_pipeline(5)
        self._print_section(6, total_steps, "Fertilizer Expert", "ผู้เชี่ยวชาญสูตรปุ๋ย")

        fertilizer_input = {
            "request_id": f"{self._session_id}-FERT",
            "target_crop": crop,
            "field_size_rai": field_size_rai,
            "nitrogen": nitrogen,
            "phosphorus": phosphorus,
            "potassium": potassium,
            "budget_thb": budget_thb or 15000,
            "prefer_organic": prefer_organic,
            "previous_observation_th": climate_analysis.get("observation_th", "")
        }

        fertilizer_response = self.fertilizer_agent.process(fertilizer_input)

        if not fertilizer_response.success:
            return self._build_error_response("การคำนวณสูตรปุ๋ยล้มเหลว", fertilizer_response.error_message)

        fertilizer_analysis = fertilizer_response.payload
        self._collect_observation(
            "FertilizerExpert", "ผู้เชี่ยวชาญสูตรปุ๋ย",
            fertilizer_analysis.get("observation_th", "")
        )

        # ═══════════════════════════════════════════════════════════════
        # STEP 7: Market & Cost Analysis
        # ═══════════════════════════════════════════════════════════════
        self._print_pipeline(6)
        self._print_section(7, total_steps, "Market & Cost Expert", "ผู้เชี่ยวชาญตลาดและต้นทุน")

        market_input = {
            "request_id": f"{self._session_id}-MARKET",
            "target_crop": crop,
            "field_size_rai": field_size_rai,
            "yield_kg_per_rai": crop_biology_analysis.get("yield_targets", {}).get("target_kg_per_rai", 600),
            "fertilizer_cost_thb": fertilizer_analysis.get("cost_analysis", {}).get("total_cost", 0),
            "prefer_organic": prefer_organic,
            "previous_observation_th": fertilizer_analysis.get("observation_th", "")
        }

        market_response = self.market_agent.process(market_input)

        if not market_response.success:
            return self._build_error_response("การวิเคราะห์ตลาดล้มเหลว", market_response.error_message)

        market_analysis = market_response.payload
        self._collect_observation(
            "MarketCostExpert", "ผู้เชี่ยวชาญตลาดและต้นทุน",
            market_analysis.get("observation_th", "")
        )

        # ═══════════════════════════════════════════════════════════════
        # STEP 8: Final Report Compilation
        # ═══════════════════════════════════════════════════════════════
        self._print_pipeline(7)
        self._print_section(8, total_steps, "Report Agent", "ผู้สรุปรายงาน")

        report_input = {
            "request_id": f"{self._session_id}-REPORT",
            "session_id": self._session_id,
            "sample_id": sample_id,
            "location": location,
            "target_crop": crop,
            "field_size_rai": field_size_rai,
            # All agent analyses
            "soil_series_analysis": soil_series_analysis,
            "soil_chemistry_analysis": soil_chemistry_analysis,
            "crop_biology_analysis": crop_biology_analysis,
            "pest_disease_analysis": pest_disease_analysis,
            "climate_analysis": climate_analysis,
            "fertilizer_analysis": fertilizer_analysis,
            "market_analysis": market_analysis,
            "all_observations": self._agent_observations,
            "previous_observation_th": market_analysis.get("observation_th", "")
        }

        report_response = self.report_agent.process(report_input)

        if not report_response.success:
            return self._build_error_response("การสร้างรายงานล้มเหลว", report_response.error_message)

        final_report = report_response.payload

        # Add orchestrator metadata
        final_report["orchestrator_metadata"] = {
            "pipeline_completed": True,
            "agents_executed": len(self.AGENT_SEQUENCE_TH),
            "observations_collected": len(self._agent_observations),
            "session_id": self._session_id,
            "version": "2.0"
        }

        # Add all individual analyses for detailed access
        final_report["detailed_analyses"] = {
            "soil_series": soil_series_analysis,
            "soil_chemistry": soil_chemistry_analysis,
            "crop_biology": crop_biology_analysis,
            "pest_disease": pest_disease_analysis,
            "climate": climate_analysis,
            "fertilizer": fertilizer_analysis,
            "market": market_analysis
        }

        # Store in history
        self._analysis_history.append(final_report)

        # Print final summary
        self._print_final_summary(final_report)

        return final_report

    def _print_final_summary(self, report: Dict[str, Any]) -> None:
        """Print the final executive summary in Thai."""
        if not self.verbose:
            return

        summary = report.get("executive_summary", {})
        dashboard = report.get("dashboard", {})

        print("\n" + "═" * 70)
        print("🌱 S.O.I.L.E.R. สรุปผลการวิเคราะห์")
        print("═" * 70)

        # Overall assessment
        assessment = summary.get("overall_status_th", "ไม่ทราบ")
        score = summary.get("overall_score", 0)
        print(f"\n📊 สถานะโดยรวม: {assessment} (คะแนน: {score:.1f}/100)")

        # Key metrics
        print(f"\n🏥 สุขภาพดิน: {dashboard.get('soil_health', {}).get('score', 0)}/100")
        print(f"🌾 ผลผลิตเป้าหมาย: {dashboard.get('yield_target', {}).get('value', 0):,.0f} กก./ไร่")
        print(f"💰 ต้นทุนรวม: {dashboard.get('investment', {}).get('total_cost', 0):,.0f} บาท")
        print(f"📈 ROI คาดการณ์: {dashboard.get('returns', {}).get('roi_percent', 0):.1f}%")
        print(f"💵 กำไรคาดการณ์: {dashboard.get('returns', {}).get('profit', 0):,.0f} บาท")

        # Bottom line
        print("\n📝 สรุป:")
        print(f"   {summary.get('bottom_line_th', 'การวิเคราะห์เสร็จสมบูรณ์')}")

        # Agent observations chain (Thai)
        print("\n🔗 ข้อสังเกตจากทีม Agent:")
        for i, obs in enumerate(self._agent_observations, 1):
            agent_th = obs.get("agent_th", "Unknown")
            observation = obs.get("observation_th", "")[:70]
            print(f"   {i}. [{agent_th}]: {observation}...")

        print("\n" + "═" * 70)
        print("✅ รายงานเสร็จสมบูรณ์")
        print("═" * 70 + "\n")

    def _build_error_response(self, title: str, message: str) -> Dict[str, Any]:
        """Build error response in Thai."""
        return {
            "success": False,
            "error_th": title,
            "message": message,
            "session_id": self._session_id,
            "timestamp": datetime.now().isoformat(),
            "observations_collected": self._agent_observations
        }

    def get_history(self) -> list:
        """Get analysis history for this orchestrator instance."""
        return self._analysis_history

    def get_observations(self) -> List[Dict[str, str]]:
        """Get all agent observations (Thai) from the last analysis."""
        return self._agent_observations

    def quick_analyze(
        self,
        ph: float,
        n: float,
        p: float,
        k: float,
        crop: str = "Riceberry Rice",
        field_size_rai: float = 1.0
    ) -> Dict[str, Any]:
        """
        Quick analysis with minimal parameters.

        Args:
            ph: Soil pH
            n: Nitrogen (mg/kg)
            p: Phosphorus (mg/kg)
            k: Potassium (mg/kg)
            crop: Target crop
            field_size_rai: Field size in rai

        Returns:
            Complete S.O.I.L.E.R. Executive Report
        """
        return self.analyze(
            location="จังหวัดแพร่",
            crop=crop,
            ph=ph,
            nitrogen=n,
            phosphorus=p,
            potassium=k,
            field_size_rai=field_size_rai
        )


# =============================================================================
# Convenience function for direct usage
# =============================================================================

def run_analysis(
    location: str,
    crop: str,
    ph: float,
    nitrogen: float,
    phosphorus: float,
    potassium: float,
    field_size_rai: float = 1.0,
    lat: float = 18.0,
    lon: float = 99.8,
    planting_date: Optional[str] = None,
    budget_thb: Optional[float] = None,
    prefer_organic: bool = False,
    verbose: bool = True
) -> Dict[str, Any]:
    """
    Convenience function to run S.O.I.L.E.R. analysis.

    Example:
        from core.orchestrator import run_analysis

        result = run_analysis(
            location="อำเภอเด่นชัย, แพร่",
            crop="Riceberry Rice",
            ph=6.0,
            nitrogen=35,
            phosphorus=18,
            potassium=100,
            field_size_rai=3.0
        )
    """
    orchestrator = SoilerOrchestrator(verbose=verbose)
    return orchestrator.analyze(
        location=location,
        crop=crop,
        ph=ph,
        nitrogen=nitrogen,
        phosphorus=phosphorus,
        potassium=potassium,
        field_size_rai=field_size_rai,
        lat=lat,
        lon=lon,
        planting_date=planting_date,
        budget_thb=budget_thb,
        prefer_organic=prefer_organic
    )


if __name__ == "__main__":
    # Demo run
    print("🌱 S.O.I.L.E.R. - ระบบแนะนำการเกษตรอัจฉริยะ")
    print("Multi-Agent AI System Demo v2.0\n")

    result = run_analysis(
        location="อำเภอเด่นชัย, จังหวัดแพร่",
        crop="Riceberry Rice",
        ph=5.8,
        nitrogen=28,
        phosphorus=15,
        potassium=95,
        field_size_rai=5.0,
        budget_thb=5000
    )

    # Print report ID
    print(f"\n📄 Report ID: {result.get('report_metadata', {}).get('report_id', 'N/A')}")
