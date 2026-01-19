"""
S.O.I.L.E.R. Agent #5: Climate & Environment Expert
ผู้เชี่ยวชาญภูมิอากาศ - Analyzes weather patterns and climate suitability.
"""

import random
from datetime import datetime, timedelta
from typing import Any, Dict, List
from agents.base_agent import BaseAgent


class ClimateAgent(BaseAgent):
    """
    ผู้เชี่ยวชาญภูมิอากาศ (Climate & Environment Expert)

    หน้าที่:
    - วิเคราะห์สภาพอากาศและฤดูกาล
    - ประเมินความเหมาะสมของภูมิอากาศ
    - ระบุความเสี่ยงจากสภาพอากาศ
    - แนะนำช่วงเวลาปลูกที่เหมาะสม
    """

    # Climate data for Phrae Province
    PHRAE_CLIMATE = {
        1: {"temp_min": 14, "temp_max": 31, "rainfall_mm": 5, "humidity": 65, "season": "แล้งหนาว"},
        2: {"temp_min": 16, "temp_max": 34, "rainfall_mm": 8, "humidity": 60, "season": "แล้งร้อน"},
        3: {"temp_min": 20, "temp_max": 36, "rainfall_mm": 25, "humidity": 55, "season": "แล้งร้อน"},
        4: {"temp_min": 23, "temp_max": 37, "rainfall_mm": 65, "humidity": 60, "season": "แล้งร้อน"},
        5: {"temp_min": 24, "temp_max": 35, "rainfall_mm": 180, "humidity": 75, "season": "ฝน"},
        6: {"temp_min": 24, "temp_max": 33, "rainfall_mm": 150, "humidity": 80, "season": "ฝน"},
        7: {"temp_min": 24, "temp_max": 32, "rainfall_mm": 200, "humidity": 85, "season": "ฝน"},
        8: {"temp_min": 24, "temp_max": 32, "rainfall_mm": 250, "humidity": 85, "season": "ฝน"},
        9: {"temp_min": 23, "temp_max": 32, "rainfall_mm": 220, "humidity": 85, "season": "ฝน"},
        10: {"temp_min": 22, "temp_max": 32, "rainfall_mm": 100, "humidity": 78, "season": "ฝน"},
        11: {"temp_min": 18, "temp_max": 31, "rainfall_mm": 30, "humidity": 70, "season": "แล้งหนาว"},
        12: {"temp_min": 15, "temp_max": 30, "rainfall_mm": 10, "humidity": 68, "season": "แล้งหนาว"},
    }

    def __init__(self, verbose: bool = True):
        super().__init__(
            agent_name="ClimateExpert",
            agent_name_th="ผู้เชี่ยวชาญภูมิอากาศ",
            verbose=verbose
        )

    def _execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """วิเคราะห์สภาพภูมิอากาศและความเหมาะสม"""
        self.think("กำลังวิเคราะห์สภาพภูมิอากาศ...")

        location = input_data.get("location", "แพร่")
        target_crop = input_data.get("target_crop", "Corn")
        lat = input_data.get("lat", 18.0)
        lon = input_data.get("lon", 99.8)
        planting_date_str = input_data.get("planting_date")
        growth_cycle = input_data.get("growth_cycle_days", 120)

        # Parse planting date
        if planting_date_str:
            planting_date = datetime.fromisoformat(planting_date_str)
        else:
            planting_date = datetime.now() + timedelta(days=14)

        # Get growing season climate
        self.think(f"กำลังดึงข้อมูลภูมิอากาศสำหรับ {location}...")
        climate_data = self._get_growing_season_climate(planting_date, growth_cycle)
        self.log_result(f"ปริมาณฝนตลอดฤดู: {climate_data['total_rainfall_mm']:.0f} มม.")

        # Assess climate suitability
        self.think(f"กำลังประเมินความเหมาะสมสำหรับ {target_crop}...")
        suitability = self._assess_suitability(target_crop, climate_data)
        self.log_result(f"ความเหมาะสมภูมิอากาศ: {suitability['rating_th']}")

        # Identify weather risks
        self.think("กำลังประเมินความเสี่ยงจากสภาพอากาศ...")
        risks = self._identify_risks(target_crop, climate_data)

        # Get optimal planting window
        self.think("กำลังหาช่วงเวลาปลูกที่ดีที่สุด...")
        planting_window = self._get_optimal_planting_window(target_crop)
        self.log_result(f"ช่วงปลูกที่ดี: {planting_window['optimal_th']}")

        # Weather forecast
        forecast = self._get_weather_forecast(lat, lon)

        # Build observation in Thai
        risk_summary = ", ".join([r["risk_th"] for r in risks if r["severity"] == "high"][:2])
        observation_th = (
            f"ผู้เชี่ยวชาญภูมิอากาศ: ความเหมาะสม{suitability['rating_th']} "
            f"(คะแนน {suitability['score']}/100) "
            f"ฝนตลอดฤดู {climate_data['total_rainfall_mm']:.0f} มม. "
            f"อุณหภูมิเฉลี่ย {climate_data['avg_temp']:.1f}°C "
            f"ความเสี่ยง: {risk_summary if risk_summary else 'ไม่มีความเสี่ยงสูง'} "
            f"ช่วงปลูกที่ดี: {planting_window['optimal_th']}"
        )

        return {
            "location": location,
            "climate_data": climate_data,
            "suitability": suitability,
            "weather_risks": risks,
            "planting_window": planting_window,
            "forecast": forecast,
            "growing_degree_days": self._calculate_gdd(climate_data, target_crop),
            "recommendations_th": self._generate_recommendations(suitability, risks),
            "observation_th": observation_th
        }

    def _get_growing_season_climate(self, planting_date: datetime, growth_days: int) -> Dict:
        """Get climate data for the growing season."""
        start_month = planting_date.month
        months_needed = (growth_days // 30) + 2

        monthly_data = []
        total_rainfall = 0
        temps = []
        humidities = []

        for i in range(months_needed):
            month = ((start_month - 1 + i) % 12) + 1
            data = self.PHRAE_CLIMATE.get(month, self.PHRAE_CLIMATE[1])
            monthly_data.append({
                "month": month,
                "month_th": self._get_thai_month(month),
                **data
            })
            total_rainfall += data["rainfall_mm"]
            temps.append((data["temp_min"] + data["temp_max"]) / 2)
            humidities.append(data["humidity"])

        current_season = self.PHRAE_CLIMATE.get(planting_date.month, {}).get("season", "ไม่ทราบ")

        return {
            "monthly_data": monthly_data,
            "total_rainfall_mm": total_rainfall,
            "avg_temp": sum(temps) / len(temps),
            "avg_humidity": sum(humidities) / len(humidities),
            "min_temp": min([d["temp_min"] for d in monthly_data]),
            "max_temp": max([d["temp_max"] for d in monthly_data]),
            "current_season_th": current_season
        }

    def _get_thai_month(self, month: int) -> str:
        """Get Thai month name."""
        months = ["", "มกราคม", "กุมภาพันธ์", "มีนาคม", "เมษายน", "พฤษภาคม", "มิถุนายน",
                  "กรกฎาคม", "สิงหาคม", "กันยายน", "ตุลาคม", "พฤศจิกายน", "ธันวาคม"]
        return months[month] if 1 <= month <= 12 else ""

    def _assess_suitability(self, crop: str, climate_data: Dict) -> Dict:
        """Assess climate suitability for crop."""
        crop_needs = {
            "Riceberry Rice": {"min_rain": 1000, "temp_range": (20, 35), "flood_ok": True},
            "Corn": {"min_rain": 400, "temp_range": (18, 35), "flood_ok": False}
        }
        needs = crop_needs.get(crop, crop_needs["Corn"])

        score = 0
        factors = []

        # Rainfall assessment (40 points)
        rainfall = climate_data["total_rainfall_mm"]
        if rainfall >= needs["min_rain"]:
            rain_score = 40
            rain_status = "เพียงพอ"
        elif rainfall >= needs["min_rain"] * 0.7:
            rain_score = 25
            rain_status = "พอใช้ได้"
        else:
            rain_score = 10
            rain_status = "ไม่เพียงพอ"
        score += rain_score
        factors.append({"factor_th": "ปริมาณฝน", "status_th": rain_status, "score": rain_score})

        # Temperature assessment (35 points)
        avg_temp = climate_data["avg_temp"]
        if needs["temp_range"][0] <= avg_temp <= needs["temp_range"][1]:
            temp_score = 35
            temp_status = "เหมาะสม"
        else:
            temp_score = 15
            temp_status = "ไม่เหมาะสม"
        score += temp_score
        factors.append({"factor_th": "อุณหภูมิ", "status_th": temp_status, "score": temp_score})

        # Season assessment (25 points)
        season = climate_data["current_season_th"]
        if "ฝน" in season:
            season_score = 25
            season_status = "ฤดูฝน - เหมาะสม"
        else:
            season_score = 15
            season_status = "ฤดูแล้ง - ต้องมีน้ำ"
        score += season_score
        factors.append({"factor_th": "ฤดูกาล", "status_th": season_status, "score": season_score})

        # Rating
        if score >= 85:
            rating_th = "ดีเยี่ยม"
        elif score >= 70:
            rating_th = "ดี"
        elif score >= 55:
            rating_th = "ปานกลาง"
        else:
            rating_th = "ต้องระวัง"

        return {
            "score": score,
            "rating_th": rating_th,
            "factors": factors
        }

    def _identify_risks(self, crop: str, climate_data: Dict) -> List[Dict]:
        """Identify weather-related risks."""
        risks = []

        # Drought risk
        if climate_data["total_rainfall_mm"] < 500:
            risks.append({
                "risk_th": "ภัยแล้ง",
                "severity": "high",
                "severity_th": "สูง",
                "mitigation_th": "เตรียมระบบน้ำสำรอง วางแผนให้น้ำเสริม"
            })
        elif climate_data["total_rainfall_mm"] < 800:
            risks.append({
                "risk_th": "ฝนน้อย",
                "severity": "medium",
                "severity_th": "ปานกลาง",
                "mitigation_th": "เตรียมน้ำสำรอง"
            })

        # Flood risk
        high_rain_months = [m for m in climate_data["monthly_data"] if m["rainfall_mm"] > 200]
        if high_rain_months and crop != "Riceberry Rice":
            risks.append({
                "risk_th": "น้ำท่วม/น้ำขัง",
                "severity": "high" if len(high_rain_months) > 2 else "medium",
                "severity_th": "สูง" if len(high_rain_months) > 2 else "ปานกลาง",
                "mitigation_th": "ทำร่องระบายน้ำ ยกแปลงให้สูง"
            })

        # Heat stress
        if climate_data["max_temp"] > 38:
            risks.append({
                "risk_th": "อากาศร้อนจัด",
                "severity": "medium",
                "severity_th": "ปานกลาง",
                "mitigation_th": "ให้น้ำช่วยลดอุณหภูมิ หลีกเลี่ยงการทำงานช่วงเที่ยง"
            })

        # Storm risk
        risks.append({
            "risk_th": "พายุ/ลมแรง",
            "severity": "low",
            "severity_th": "ต่ำ",
            "mitigation_th": "เลือกพันธุ์ที่ลำต้นแข็งแรง"
        })

        return risks

    def _get_optimal_planting_window(self, crop: str) -> Dict:
        """Get optimal planting window for crop."""
        windows = {
            "Riceberry Rice": {
                "optimal_th": "พฤษภาคม - กรกฎาคม",
                "acceptable_th": "เมษายน - สิงหาคม",
                "note_th": "ปลูกต้นฤดูฝนได้ผลดีที่สุด"
            },
            "Corn": {
                "optimal_th": "มิถุนายน - กรกฎาคม",
                "acceptable_th": "พฤษภาคม - สิงหาคม",
                "note_th": "ปลูกหลังฝนตกสม่ำเสมอแล้ว"
            }
        }
        return windows.get(crop, windows["Corn"])

    def _calculate_gdd(self, climate_data: Dict, crop: str) -> Dict:
        """Calculate growing degree days."""
        base_temp = 10  # Base temperature for most crops
        total_gdd = 0

        for month in climate_data["monthly_data"]:
            avg_temp = (month["temp_min"] + month["temp_max"]) / 2
            daily_gdd = max(0, avg_temp - base_temp)
            total_gdd += daily_gdd * 30

        required = {"Riceberry Rice": 2500, "Corn": 2700}.get(crop, 2500)

        return {
            "total_gdd": total_gdd,
            "required_gdd": required,
            "adequate": total_gdd >= required,
            "status_th": "เพียงพอ" if total_gdd >= required else "อาจไม่เพียงพอ"
        }

    def _get_weather_forecast(self, lat: float, lon: float) -> Dict:
        """Get weather forecast (simulated)."""
        current_month = datetime.now().month
        base = self.PHRAE_CLIMATE.get(current_month, self.PHRAE_CLIMATE[1])

        return {
            "humidity_percent": base["humidity"] + random.randint(-5, 5),
            "rain_probability_percent": 60 if base["rainfall_mm"] > 100 else 20,
            "avg_temperature_c": (base["temp_min"] + base["temp_max"]) / 2,
            "summary_th": f"ฤดู{base['season']} อุณหภูมิ {base['temp_min']}-{base['temp_max']}°C",
            "source_th": "ข้อมูลจำลองจากค่าเฉลี่ยรายเดือน"
        }

    def _generate_recommendations(self, suitability: Dict, risks: List) -> List[str]:
        """Generate climate-based recommendations in Thai."""
        recs = []

        if suitability["score"] < 70:
            recs.append("ควรเตรียมระบบชลประทานให้พร้อม")

        for risk in risks:
            if risk["severity"] == "high":
                recs.append(f"เตรียมรับมือ{risk['risk_th']}: {risk['mitigation_th']}")

        recs.append("ติดตามพยากรณ์อากาศเป็นประจำทุกสัปดาห์")

        return recs
