"""
S.O.I.L.E.R. Agent #6: Fertilizer Formula Expert
ผู้เชี่ยวชาญสูตรปุ๋ย - Calculates fertilizer requirements and application schedule.
"""

from typing import Any, Dict, List
from agents.base_agent import BaseAgent
from data.knowledge_base import FERTILIZERS, CROP_REQUIREMENTS


class FertilizerFormulaAgent(BaseAgent):
    """
    ผู้เชี่ยวชาญสูตรปุ๋ย (Fertilizer Formula Expert)

    หน้าที่:
    - คำนวณปริมาณธาตุอาหารที่ขาด
    - เลือกสูตรปุ๋ยที่เหมาะสม
    - วางแผนการใส่ปุ๋ย
    - คำนวณต้นทุนปุ๋ย
    """

    def __init__(self, verbose: bool = True):
        super().__init__(
            agent_name="FertilizerExpert",
            agent_name_th="ผู้เชี่ยวชาญสูตรปุ๋ย",
            verbose=verbose
        )

    def _execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """คำนวณและแนะนำสูตรปุ๋ย"""
        self.think("กำลังวิเคราะห์ความต้องการปุ๋ย...")

        target_crop = input_data.get("target_crop", "Corn")
        field_size_rai = input_data.get("field_size_rai", 1.0)
        soil_n = input_data.get("nitrogen", 20)
        soil_p = input_data.get("phosphorus", 15)
        soil_k = input_data.get("potassium", 100)
        budget = input_data.get("budget_thb", 15000)
        prefer_organic = input_data.get("prefer_organic", False)

        # Get crop nutrient requirements
        crop_data = CROP_REQUIREMENTS.get(target_crop, {})
        nutrient_req = crop_data.get("nutrient_requirements_kg_per_rai", {})
        growth_cycle = crop_data.get("growth_cycle_days", 120)

        self.log_action(f"พืชเป้าหมาย: {crop_data.get('name_th', target_crop)} ({growth_cycle} วัน)")

        # Calculate nutrient gaps
        self.think("กำลังคำนวณธาตุอาหารที่ขาด...")
        nutrient_gaps = self._calculate_nutrient_gaps(
            soil_n, soil_p, soil_k, nutrient_req, field_size_rai
        )

        self.log_result(f"ขาด N: {nutrient_gaps['N']['gap_kg']:.1f} กก.")
        self.log_result(f"ขาด P₂O₅: {nutrient_gaps['P']['gap_kg']:.1f} กก.")
        self.log_result(f"ขาด K₂O: {nutrient_gaps['K']['gap_kg']:.1f} กก.")

        # Select fertilizers
        self.think("กำลังเลือกสูตรปุ๋ยที่เหมาะสม...")
        selected_fertilizers = self._select_fertilizers(nutrient_gaps, prefer_organic)

        for fert in selected_fertilizers:
            self.log_action(f"เลือก: {fert['name_th']} - {fert['rate_kg_per_rai']:.1f} กก./ไร่")

        # Calculate costs
        self.think("กำลังคำนวณค่าใช้จ่าย...")
        cost_analysis = self._calculate_costs(selected_fertilizers, field_size_rai)
        self.log_result(f"ค่าปุ๋ยรวม: {cost_analysis['total_cost']:.2f} บาท")
        self.log_result(f"ค่าปุ๋ยต่อไร่: {cost_analysis['cost_per_rai']:.2f} บาท/ไร่")

        # Check budget
        within_budget = cost_analysis['total_cost'] <= budget
        if not within_budget:
            self.log_warning(f"เกินงบประมาณ {cost_analysis['total_cost'] - budget:.2f} บาท")

        # Create application schedule
        self.think("กำลังวางแผนการใส่ปุ๋ย...")
        schedule = self._create_application_schedule(selected_fertilizers, growth_cycle)

        # Get organic alternatives if requested
        organic_alts = self._get_organic_alternatives() if prefer_organic else []

        # Build observation in Thai
        budget_status = "อยู่ในงบประมาณ" if within_budget else f"เกินงบ {cost_analysis['total_cost'] - budget:,.0f} บาท"
        observation_th = (
            f"ผู้เชี่ยวชาญสูตรปุ๋ย: แนะนำปุ๋ย {len(selected_fertilizers)} รายการ "
            f"ค่าใช้จ่ายรวม {cost_analysis['total_cost']:,.0f} บาท "
            f"({cost_analysis['cost_per_rai']:,.0f} บาท/ไร่) "
            f"{budget_status} "
            f"แบ่งใส่ {len(schedule)} ครั้ง"
        )

        return {
            "crop_name": target_crop,
            "crop_name_th": crop_data.get("name_th", target_crop),
            "field_size_rai": field_size_rai,
            "nutrient_gaps": nutrient_gaps,
            "selected_fertilizers": selected_fertilizers,
            "application_schedule": schedule,
            "cost_analysis": cost_analysis,
            "budget_thb": budget,
            "within_budget": within_budget,
            "organic_alternatives": organic_alts,
            "recommendations_th": self._generate_recommendations(nutrient_gaps, within_budget),
            "observation_th": observation_th
        }

    def _calculate_nutrient_gaps(self, soil_n: float, soil_p: float, soil_k: float,
                                   crop_req: Dict, field_size: float) -> Dict:
        """Calculate nutrient gaps."""
        # Convert soil mg/kg to kg/rai (approximate)
        soil_n_kg = soil_n * 0.0016 * 1600 * 0.15  # 15cm depth
        soil_p_kg = soil_p * 0.0016 * 1600 * 0.15
        soil_k_kg = soil_k * 0.0016 * 1600 * 0.15

        # Crop requirements (optimal level)
        req_n = crop_req.get("nitrogen", {}).get("optimal", 12) * field_size
        req_p = crop_req.get("phosphorus_p2o5", {}).get("optimal", 6) * field_size
        req_k = crop_req.get("potassium_k2o", {}).get("optimal", 8) * field_size

        # Calculate gaps (need - available)
        gap_n = max(0, req_n - soil_n_kg * 0.3)  # 30% availability
        gap_p = max(0, req_p - soil_p_kg * 0.2)  # 20% availability
        gap_k = max(0, req_k - soil_k_kg * 0.5)  # 50% availability

        return {
            "N": {
                "soil_level_mg_kg": soil_n,
                "required_kg": req_n,
                "gap_kg": gap_n,
                "gap_per_rai": gap_n / field_size if field_size > 0 else 0,
                "status_th": "ต่ำ" if soil_n < 20 else ("ปานกลาง" if soil_n < 40 else "สูง")
            },
            "P": {
                "soil_level_mg_kg": soil_p,
                "required_kg": req_p,
                "gap_kg": gap_p,
                "gap_per_rai": gap_p / field_size if field_size > 0 else 0,
                "status_th": "ต่ำ" if soil_p < 15 else ("ปานกลาง" if soil_p < 30 else "สูง")
            },
            "K": {
                "soil_level_mg_kg": soil_k,
                "required_kg": req_k,
                "gap_kg": gap_k,
                "gap_per_rai": gap_k / field_size if field_size > 0 else 0,
                "status_th": "ต่ำ" if soil_k < 60 else ("ปานกลาง" if soil_k < 120 else "สูง")
            }
        }

    def _select_fertilizers(self, gaps: Dict, prefer_organic: bool) -> List[Dict]:
        """Select appropriate fertilizers based on nutrient gaps."""
        selected = []

        # Filter fertilizer types
        if prefer_organic:
            available = [f for f in FERTILIZERS if f.get("type") == "organic"]
        else:
            available = [f for f in FERTILIZERS if f.get("type") != "organic"]

        # Basal fertilizer (NPK compound)
        npk_compound = next((f for f in available if "16-20-0" in f.get("formula", "")), None)
        if not npk_compound:
            npk_compound = next((f for f in available if "15-15-15" in f.get("formula", "")), None)

        if npk_compound:
            rate = min(30, gaps["P"]["gap_per_rai"] / 0.20) if gaps["P"]["gap_per_rai"] > 0 else 20
            selected.append({
                "name": npk_compound["name"],
                "name_th": npk_compound.get("name_th", npk_compound["name"]),
                "formula": npk_compound["formula"],
                "type_th": "ปุ๋ยรองพื้น",
                "rate_kg_per_rai": round(rate, 1),
                "timing_th": "รองพื้นก่อนปลูก",
                "stage": "basal",
                "price_per_kg": npk_compound.get("price_thb_per_kg", 18)
            })

        # Top-dress nitrogen (Urea)
        urea = next((f for f in available if "46-0-0" in f.get("formula", "")), None)
        if urea and gaps["N"]["gap_per_rai"] > 5:
            rate = min(20, gaps["N"]["gap_per_rai"] / 0.46)
            selected.append({
                "name": urea["name"],
                "name_th": urea.get("name_th", "ยูเรีย"),
                "formula": urea["formula"],
                "type_th": "ปุ๋ยแต่งหน้า",
                "rate_kg_per_rai": round(rate, 1),
                "timing_th": "แต่งหน้าครั้งที่ 1 (20-30 วัน)",
                "stage": "top_dress_1",
                "price_per_kg": urea.get("price_thb_per_kg", 18.5)
            })

        # Potassium supplement
        mop = next((f for f in available if "0-0-60" in f.get("formula", "")), None)
        if mop and gaps["K"]["gap_per_rai"] > 3:
            rate = min(15, gaps["K"]["gap_per_rai"] / 0.60)
            selected.append({
                "name": mop["name"],
                "name_th": mop.get("name_th", "โพแทสเซียมคลอไรด์"),
                "formula": mop["formula"],
                "type_th": "ปุ๋ยเสริมโพแทสเซียม",
                "rate_kg_per_rai": round(rate, 1),
                "timing_th": "แบ่งใส่ 2 ครั้ง",
                "stage": "split",
                "price_per_kg": mop.get("price_thb_per_kg", 20)
            })

        return selected

    def _calculate_costs(self, fertilizers: List[Dict], field_size: float) -> Dict:
        """Calculate fertilizer costs."""
        total_cost = 0
        breakdown = []

        for fert in fertilizers:
            total_kg = fert["rate_kg_per_rai"] * field_size
            cost = total_kg * fert["price_per_kg"]
            total_cost += cost

            breakdown.append({
                "name_th": fert["name_th"],
                "total_kg": round(total_kg, 1),
                "price_per_kg": fert["price_per_kg"],
                "total_cost": round(cost, 2)
            })

        return {
            "total_cost": round(total_cost, 2),
            "cost_per_rai": round(total_cost / field_size, 2) if field_size > 0 else 0,
            "breakdown": breakdown
        }

    def _create_application_schedule(self, fertilizers: List[Dict], growth_days: int) -> List[Dict]:
        """Create fertilizer application schedule."""
        schedule = []

        stage_timing = {
            "basal": {"day": 0, "stage_th": "ก่อนปลูก/รองพื้น"},
            "top_dress_1": {"day": 25, "stage_th": "แต่งหน้าครั้งที่ 1"},
            "top_dress_2": {"day": 45, "stage_th": "แต่งหน้าครั้งที่ 2"},
            "split": {"day": 35, "stage_th": "ใส่เสริม"}
        }

        for fert in fertilizers:
            stage = fert.get("stage", "basal")
            timing = stage_timing.get(stage, stage_timing["basal"])

            schedule.append({
                "name_th": fert["name_th"],
                "formula": fert["formula"],
                "rate_kg_per_rai": fert["rate_kg_per_rai"],
                "timing_day": timing["day"],
                "stage_th": timing["stage_th"],
                "method_th": "หว่าน" if stage == "basal" else "โรยข้างแถว",
                "note_th": fert.get("timing_th", "")
            })

        # Sort by timing
        schedule.sort(key=lambda x: x["timing_day"])
        return schedule

    def _get_organic_alternatives(self) -> List[Dict]:
        """Get organic fertilizer alternatives."""
        organic = [f for f in FERTILIZERS if f.get("type") == "organic"]
        return [
            {
                "name_th": f.get("name_th", f["name"]),
                "formula": f["formula"],
                "rate_th": "200-500 กก./ไร่",
                "benefit_th": f.get("notes_th", "ปรับปรุงโครงสร้างดิน")
            }
            for f in organic[:3]
        ]

    def _generate_recommendations(self, gaps: Dict, within_budget: bool) -> List[str]:
        """Generate fertilizer recommendations in Thai."""
        recs = []

        if gaps["N"]["status_th"] == "ต่ำ":
            recs.append("ดินขาดไนโตรเจน ควรใส่ปุ๋ยยูเรียหรือแอมโมเนียมซัลเฟต")
        if gaps["P"]["status_th"] == "ต่ำ":
            recs.append("ดินขาดฟอสฟอรัส ควรใส่ปุ๋ยรองพื้นที่มีฟอสฟอรัสสูง")
        if gaps["K"]["status_th"] == "ต่ำ":
            recs.append("ดินขาดโพแทสเซียม ควรใส่ปุ๋ยโพแทสเซียมคลอไรด์")

        if not within_budget:
            recs.append("ค่าปุ๋ยเกินงบ พิจารณาใช้ปุ๋ยอินทรีย์ทดแทนบางส่วน")

        recs.append("แบ่งใส่ปุ๋ยหลายครั้งดีกว่าใส่ครั้งเดียว")
        recs.append("ใส่ปุ๋ยหลังฝนตกหรือรดน้ำ")

        return recs
