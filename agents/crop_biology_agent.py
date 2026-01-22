"""
S.O.I.L.E.R. Agent #3: Crop Biology Expert
ผู้เชี่ยวชาญชีววิทยาพืช - Analyzes crop requirements and growth planning.
"""

from datetime import datetime, timedelta
from typing import Any, Dict, List
from agents.base_agent import BaseAgent
from data.knowledge_base import CROP_REQUIREMENTS


class CropBiologyAgent(BaseAgent):
    """
    ผู้เชี่ยวชาญชีววิทยาพืช (Crop Biology Expert)

    หน้าที่:
    - วิเคราะห์ความต้องการของพืช
    - วางแผนระยะการเจริญเติบโต
    - คำนวณความต้องการน้ำและปุ๋ย
    - ประเมินเป้าหมายผลผลิต
    """

    def __init__(self, verbose: bool = True):
        super().__init__(
            agent_name="CropBiologyExpert",
            agent_name_th="ผู้เชี่ยวชาญชีววิทยาพืช",
            verbose=verbose
        )

    def _execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """วิเคราะห์ความต้องการและการเจริญเติบโตของพืช"""
        self.think("กำลังวิเคราะห์ความต้องการของพืช...")

        target_crop = input_data.get("target_crop", "Corn")
        field_size_rai = input_data.get("field_size_rai", 1.0)
        soil_health_score = input_data.get("soil_health_score", 70)
        planting_date_str = input_data.get("planting_date")

        # Get crop data
        crop_data = CROP_REQUIREMENTS.get(target_crop, {})
        crop_name_th = crop_data.get("name_th", target_crop)

        self.log_result(f"พืชเป้าหมาย: {crop_name_th}")

        # Parse planting date
        if planting_date_str:
            planting_date = datetime.fromisoformat(planting_date_str)
        else:
            planting_date = datetime.now() + timedelta(days=14)
            self.think("ไม่ได้ระบุวันปลูก สมมติว่าจะปลูกใน 2 สัปดาห์")

        # Growth cycle
        growth_cycle = crop_data.get("growth_cycle_days", 120)
        harvest_date = planting_date + timedelta(days=growth_cycle)
        self.log_result(f"ระยะเวลาปลูก: {growth_cycle} วัน")

        # Build growth calendar
        self.think("กำลังวางแผนระยะการเจริญเติบโต...")
        growth_calendar = self._build_growth_calendar(crop_data, planting_date)

        # Calculate water requirements
        self.think("กำลังคำนวณความต้องการน้ำ...")
        water_req = self._calculate_water_requirements(crop_data, field_size_rai)
        self.log_result(f"ความต้องการน้ำรวม: {water_req['total_mm']} มม.")

        # Calculate yield targets
        self.think("กำลังประเมินเป้าหมายผลผลิต...")
        yield_targets = self._calculate_yield_targets(crop_data, soil_health_score, field_size_rai)
        self.log_result(f"ผลผลิตเป้าหมาย: {yield_targets['target_kg_per_rai']:.0f} กก./ไร่")

        # Nutrient requirements
        nutrient_req = self._get_nutrient_requirements(crop_data, field_size_rai)

        # Critical periods
        critical_periods = self._identify_critical_periods(crop_data, planting_date)

        # Build observation in Thai
        observation_th = (
            f"ผู้เชี่ยวชาญชีววิทยาพืช: {crop_name_th} ใช้เวลาปลูก {growth_cycle} วัน "
            f"ต้องการน้ำ {water_req['total_mm']} มม. "
            f"ผลผลิตเป้าหมาย {yield_targets['target_kg_per_rai']:.0f} กก./ไร่ "
            f"(รวม {yield_targets['total_kg']:.0f} กก. จาก {field_size_rai} ไร่) "
            f"ช่วงวิกฤต: {', '.join([p['name_th'] for p in critical_periods[:2]])}"
        )

        return {
            "crop_name": target_crop,
            "crop_name_th": crop_name_th,
            "growth_cycle_days": growth_cycle,
            "planting_date": planting_date.isoformat(),
            "harvest_date": harvest_date.isoformat(),
            "growth_calendar": growth_calendar,
            "water_requirements": water_req,
            "yield_targets": yield_targets,
            "nutrient_requirements": nutrient_req,
            "critical_periods": critical_periods,
            "soil_requirements": crop_data.get("soil_requirements", {}),
            "special_notes_th": crop_data.get("special_notes_th", []),
            "observation_th": observation_th
        }

    def _build_growth_calendar(self, crop_data: Dict, planting_date: datetime) -> List[Dict]:
        """Build growth stage calendar."""
        calendar = []
        current_date = planting_date
        stages = crop_data.get("growth_stages", {})

        stage_names_th = {
            "seedling": "ระยะกล้า",
            "vegetative": "ระยะเจริญเติบโต",
            "reproductive": "ระยะออกดอก/ออกรวง",
            "ripening": "ระยะสุกแก่",
            "emergence": "ระยะงอก",
            "maturity": "ระยะเก็บเกี่ยว"
        }

        for stage_name, stage_data in stages.items():
            days = stage_data.get("days", 30)
            end_date = current_date + timedelta(days=days)

            calendar.append({
                "stage": stage_name,
                "stage_th": stage_names_th.get(stage_name, stage_name),
                "description_th": stage_data.get("description_th", stage_data.get("description", "")),
                "start_date": current_date.strftime("%Y-%m-%d"),
                "end_date": end_date.strftime("%Y-%m-%d"),
                "duration_days": days,
                "key_activities_th": self._get_stage_activities(stage_name)
            })

            current_date = end_date

        return calendar

    def _get_stage_activities(self, stage: str) -> List[str]:
        """Get key activities for each growth stage in Thai."""
        activities = {
            "seedling": ["เตรียมแปลงเพาะ", "ดูแลความชื้น", "ป้องกันโรคในระยะกล้า"],
            "emergence": ["รดน้ำสม่ำเสมอ", "ป้องกันนกและแมลง"],
            "vegetative": ["ใส่ปุ๋ยเร่งการเจริญเติบโต", "กำจัดวัชพืช", "ตรวจโรคและแมลง"],
            "reproductive": ["ใส่ปุ๋ยเสริมการออกดอก", "ดูแลน้ำให้เพียงพอ", "ป้องกันโรค"],
            "ripening": ["ลดการให้น้ำ", "เตรียมเก็บเกี่ยว"],
            "maturity": ["เก็บเกี่ยวเมื่อสุกแก่", "ตากและเก็บรักษา"]
        }
        return activities.get(stage, ["ดูแลทั่วไป"])

    def _calculate_water_requirements(self, crop_data: Dict, field_size: float) -> Dict:
        """Calculate water requirements."""
        water_mm = crop_data.get("water_requirement_mm", 500)
        water_per_rai_liters = water_mm * 1600  # 1 rai = 1600 sqm, 1mm = 1 liter/sqm

        return {
            "total_mm": water_mm,
            "per_rai_liters": water_per_rai_liters,
            "total_liters": water_per_rai_liters * field_size,
            "daily_avg_mm": water_mm / crop_data.get("growth_cycle_days", 120),
            "irrigation_needed": water_mm > 600,
            "recommendation_th": "ต้องการระบบชลประทาน" if water_mm > 800 else "ฝนธรรมชาติอาจเพียงพอในฤดูฝน"
        }

    def _calculate_yield_targets(self, crop_data: Dict, soil_score: float, field_size: float) -> Dict:
        """Calculate yield targets based on soil conditions."""
        yield_potential = crop_data.get("yield_potential_kg_per_rai", {"low": 400, "average": 600, "high": 800})

        # Adjust based on soil health
        if soil_score >= 80:
            target = yield_potential.get("high", 800)
            level = "สูง"
        elif soil_score >= 60:
            target = yield_potential.get("average", 600)
            level = "ปานกลาง"
        else:
            target = yield_potential.get("low", 400)
            level = "ต่ำ"

        return {
            "target_kg_per_rai": target,
            "total_kg": target * field_size,
            "level": level,
            "potential_range": yield_potential,
            "field_size_rai": field_size
        }

    def _get_nutrient_requirements(self, crop_data: Dict, field_size: float) -> Dict:
        """Get nutrient requirements in kg/rai."""
        nutrient_req = crop_data.get("nutrient_requirements_kg_per_rai", {})

        return {
            "nitrogen": {
                "per_rai": nutrient_req.get("nitrogen", {}).get("optimal", 12),
                "total": nutrient_req.get("nitrogen", {}).get("optimal", 12) * field_size,
                "unit": "กก."
            },
            "phosphorus": {
                "per_rai": nutrient_req.get("phosphorus_p2o5", {}).get("optimal", 6),
                "total": nutrient_req.get("phosphorus_p2o5", {}).get("optimal", 6) * field_size,
                "unit": "กก. P₂O₅"
            },
            "potassium": {
                "per_rai": nutrient_req.get("potassium_k2o", {}).get("optimal", 8),
                "total": nutrient_req.get("potassium_k2o", {}).get("optimal", 8) * field_size,
                "unit": "กก. K₂O"
            }
        }

    def _identify_critical_periods(self, crop_data: Dict, planting_date: datetime) -> List[Dict]:
        """Identify critical growth periods."""
        periods = []

        if "rice" in crop_data.get("scientific_name", "").lower():
            periods = [
                {"name_th": "ระยะแตกกอ", "timing_th": "20-40 วันหลังปลูก", "priority": "สูง"},
                {"name_th": "ระยะออกรวง", "timing_th": "60-80 วันหลังปลูก", "priority": "วิกฤต"},
                {"name_th": "ระยะเมล็ดสุก", "timing_th": "90-110 วันหลังปลูก", "priority": "สูง"}
            ]
        else:  # Corn and others
            periods = [
                {"name_th": "ระยะงอก", "timing_th": "7-14 วันหลังปลูก", "priority": "สูง"},
                {"name_th": "ระยะออกดอก", "timing_th": "45-60 วันหลังปลูก", "priority": "วิกฤต"},
                {"name_th": "ระยะติดเมล็ด", "timing_th": "60-80 วันหลังปลูก", "priority": "สูง"}
            ]

        return periods
