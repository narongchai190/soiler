"""
S.O.I.L.E.R. Agent #1: Soil Series Expert
ผู้เชี่ยวชาญชุดดิน - Identifies soil series based on location and properties.
"""

from typing import Any, Dict, List
from agents.base_agent import BaseAgent
from data.knowledge_base import SOIL_SERIES


class SoilSeriesAgent(BaseAgent):
    """
    ผู้เชี่ยวชาญชุดดิน (Soil Series Expert)

    หน้าที่:
    - ระบุชุดดินจากตำแหน่งและลักษณะดิน
    - วิเคราะห์ลักษณะทางกายภาพ
    - ประเมินความเหมาะสมเบื้องต้น
    """

    def __init__(self, verbose: bool = True):
        super().__init__(
            agent_name="SoilSeriesExpert",
            agent_name_th="ผู้เชี่ยวชาญชุดดิน",
            verbose=verbose
        )

    def _execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """วิเคราะห์และระบุชุดดิน"""
        self.think("กำลังวิเคราะห์ข้อมูลเพื่อระบุชุดดิน...")

        location = input_data.get("location", "")
        texture = input_data.get("texture", "")
        ph = input_data.get("ph", 6.5)

        # Match soil series
        self.think("กำลังเปรียบเทียบกับฐานข้อมูลชุดดิน...")
        matched_series, confidence = self._match_soil_series(location, texture, ph)

        series_data = SOIL_SERIES.get(matched_series, {})

        self.log_result(f"ชุดดินที่ระบุ: {matched_series} (ความมั่นใจ {confidence*100:.0f}%)")

        # Get soil characteristics
        characteristics = self._get_characteristics(series_data)

        # Build observation in Thai
        observation_th = (
            f"ผู้เชี่ยวชาญชุดดิน: ระบุว่าเป็นชุดดิน{matched_series} "
            f"(ความมั่นใจ {confidence*100:.0f}%) "
            f"เนื้อดินเป็น{series_data.get('texture_th', series_data.get('texture', 'ไม่ทราบ'))} "
            f"การระบายน้ำ{self._translate_drainage(series_data.get('drainage', ''))} "
            f"เหมาะกับพืช: {', '.join(series_data.get('suitable_crops', [])[:3])}"
        )

        return {
            "identified_series": matched_series,
            "series_code": series_data.get("series_code", ""),
            "confidence": confidence,
            "description": series_data.get("description", ""),
            "description_th": series_data.get("description_th", ""),
            "texture": series_data.get("texture", ""),
            "texture_th": series_data.get("texture_th", ""),
            "texture_composition": series_data.get("texture_composition", {}),
            "drainage": series_data.get("drainage", ""),
            "water_holding_capacity": series_data.get("water_holding_capacity", ""),
            "cec": series_data.get("cec_meq_100g", 0),
            "suitable_crops": series_data.get("suitable_crops", []),
            "limitations": series_data.get("limitations", []),
            "characteristics": characteristics,
            "typical_properties": series_data.get("typical_properties", {}),
            "observation_th": observation_th
        }

    def _match_soil_series(self, location: str, texture: str, ph: float) -> tuple:
        """Match input to known soil series."""
        best_match = "Long"
        best_score = 0.0

        for series_name, series_data in SOIL_SERIES.items():
            score = 0.0

            # Location matching
            if series_name.lower() in location.lower():
                score += 0.5
            for area in series_data.get("location_areas", []):
                if area.lower() in location.lower():
                    score += 0.3

            # Texture matching
            if texture.lower() == series_data.get("texture", "").lower():
                score += 0.3

            # pH range matching
            ph_range = series_data.get("typical_properties", {}).get("ph_range", {})
            if ph_range:
                if ph_range.get("min", 0) <= ph <= ph_range.get("max", 14):
                    score += 0.2

            if score > best_score:
                best_score = score
                best_match = series_name

        confidence = min(0.97, best_score + 0.4) if best_score > 0 else 0.6
        return best_match, confidence

    def _get_characteristics(self, series_data: Dict) -> List[Dict]:
        """Get soil characteristics in Thai."""
        characteristics = []

        if series_data.get("texture"):
            characteristics.append({
                "property": "เนื้อดิน",
                "value": series_data.get("texture_th", series_data.get("texture")),
                "rating": "ปกติ"
            })

        if series_data.get("drainage"):
            characteristics.append({
                "property": "การระบายน้ำ",
                "value": self._translate_drainage(series_data.get("drainage")),
                "rating": "ปกติ"
            })

        if series_data.get("water_holding_capacity"):
            characteristics.append({
                "property": "ความสามารถอุ้มน้ำ",
                "value": self._translate_whc(series_data.get("water_holding_capacity")),
                "rating": "ดี"
            })

        return characteristics

    def _translate_drainage(self, drainage: str) -> str:
        """Translate drainage to Thai."""
        translations = {
            "well-drained": "ดี",
            "moderate": "ปานกลาง",
            "slow": "ช้า",
            "poor": "ไม่ดี"
        }
        return translations.get(drainage.lower(), drainage)

    def _translate_whc(self, whc: str) -> str:
        """Translate water holding capacity to Thai."""
        translations = {
            "high": "สูง",
            "very high": "สูงมาก",
            "moderate": "ปานกลาง",
            "low": "ต่ำ"
        }
        return translations.get(whc.lower(), whc)
