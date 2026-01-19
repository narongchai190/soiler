"""
S.O.I.L.E.R. Agent #2: Soil Chemistry Expert
ผู้เชี่ยวชาญเคมีดิน - Analyzes soil chemical properties (pH, N, P, K).
"""

from typing import Any, Dict, List
from agents.base_agent import BaseAgent


class SoilChemistryAgent(BaseAgent):
    """
    ผู้เชี่ยวชาญเคมีดิน (Soil Chemistry Expert)

    หน้าที่:
    - วิเคราะห์ค่า pH และสถานะความเป็นกรด-ด่าง
    - ประเมินระดับธาตุอาหาร N, P, K
    - คำนวณคะแนนสุขภาพดิน
    - ระบุปัญหาทางเคมีดิน
    """

    # Reference values for nutrient assessment (mg/kg)
    NUTRIENT_THRESHOLDS = {
        "nitrogen": {"low": 20, "medium": 40, "high": 60},
        "phosphorus": {"low": 15, "medium": 30, "high": 45},
        "potassium": {"low": 60, "medium": 120, "high": 180}
    }

    def __init__(self, verbose: bool = True):
        super().__init__(
            agent_name="SoilChemistryExpert",
            agent_name_th="ผู้เชี่ยวชาญเคมีดิน",
            verbose=verbose
        )

    def _execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """วิเคราะห์คุณสมบัติทางเคมีของดิน"""
        self.think("กำลังวิเคราะห์คุณสมบัติทางเคมีของดิน...")

        ph = input_data.get("ph", 6.5)
        nitrogen = input_data.get("nitrogen", 20)
        phosphorus = input_data.get("phosphorus", 15)
        potassium = input_data.get("potassium", 100)
        target_crop = input_data.get("target_crop", "")

        # Analyze pH
        self.think("กำลังวิเคราะห์ค่า pH...")
        ph_analysis = self._analyze_ph(ph, target_crop)
        self.log_result(f"สถานะ pH: {ph_analysis['status_th']}")

        # Analyze nutrients
        self.think("กำลังประเมินระดับธาตุอาหาร N-P-K...")
        nutrient_analysis = self._analyze_nutrients(nitrogen, phosphorus, potassium)

        for nutrient, data in nutrient_analysis.items():
            self.log_result(f"{data['name_th']}: {data['status_th']} ({data['value']} มก./กก.)")

        # Calculate soil health score
        self.think("กำลังคำนวณคะแนนสุขภาพดิน...")
        health_score = self._calculate_health_score(ph_analysis, nutrient_analysis)
        self.log_result(f"คะแนนสุขภาพดิน: {health_score:.1f}/100")

        # Identify issues
        issues = self._identify_issues(ph_analysis, nutrient_analysis)

        # Build observation in Thai
        nutrient_summary = []
        for n, data in nutrient_analysis.items():
            nutrient_summary.append(f"{data['symbol']}={data['status_th']}")

        observation_th = (
            f"ผู้เชี่ยวชาญเคมีดิน: pH {ph} ({ph_analysis['status_th']}) "
            f"ธาตุอาหาร {', '.join(nutrient_summary)} "
            f"คะแนนสุขภาพดิน {health_score:.0f}/100 "
            f"{'พบปัญหา: ' + ', '.join(issues[:2]) if issues else 'ไม่พบปัญหาวิกฤต'}"
        )

        return {
            "ph_value": ph,
            "ph_analysis": ph_analysis,
            "nutrient_analysis": nutrient_analysis,
            "health_score": health_score,
            "issues": issues,
            "recommendations_th": self._generate_recommendations(ph_analysis, nutrient_analysis),
            "observation_th": observation_th
        }

    def _analyze_ph(self, ph: float, crop: str = "") -> Dict[str, Any]:
        """Analyze pH value and its implications."""
        if ph < 4.5:
            status = "very_acidic"
            status_th = "เป็นกรดจัดมาก"
            suitability = "ไม่เหมาะสม"
            score = 30
        elif ph < 5.5:
            status = "acidic"
            status_th = "เป็นกรดจัด"
            suitability = "ต้องปรับปรุง"
            score = 50
        elif ph < 6.0:
            status = "slightly_acidic"
            status_th = "เป็นกรดเล็กน้อย"
            suitability = "พอใช้ได้"
            score = 70
        elif ph < 7.0:
            status = "neutral"
            status_th = "เป็นกลาง"
            suitability = "เหมาะสมดี"
            score = 90
        elif ph < 7.5:
            status = "slightly_alkaline"
            status_th = "เป็นด่างเล็กน้อย"
            suitability = "พอใช้ได้"
            score = 75
        elif ph < 8.5:
            status = "alkaline"
            status_th = "เป็นด่าง"
            suitability = "ต้องปรับปรุง"
            score = 50
        else:
            status = "very_alkaline"
            status_th = "เป็นด่างจัดมาก"
            suitability = "ไม่เหมาะสม"
            score = 30

        return {
            "value": ph,
            "status": status,
            "status_th": status_th,
            "suitability": suitability,
            "score": score,
            "recommendation_th": self._get_ph_recommendation(status)
        }

    def _get_ph_recommendation(self, status: str) -> str:
        """Get pH adjustment recommendation in Thai."""
        recommendations = {
            "very_acidic": "ควรใส่ปูนขาวหรือโดโลไมท์ 200-400 กก./ไร่",
            "acidic": "ควรใส่ปูนขาวหรือโดโลไมท์ 100-200 กก./ไร่",
            "slightly_acidic": "อาจใส่ปูนขาว 50-100 กก./ไร่ ถ้าจำเป็น",
            "neutral": "ค่า pH เหมาะสม ไม่ต้องปรับ",
            "slightly_alkaline": "หลีกเลี่ยงการใส่ปูน ใช้ปุ๋ยที่มีฤทธิ์เป็นกรด",
            "alkaline": "ควรใส่กำมะถันหรือปุ๋ยที่มีฤทธิ์เป็นกรด",
            "very_alkaline": "ต้องปรับปรุงดินอย่างเร่งด่วน ใช้กำมะถัน"
        }
        return recommendations.get(status, "")

    def _analyze_nutrients(self, n: float, p: float, k: float) -> Dict[str, Dict]:
        """Analyze N, P, K levels."""
        return {
            "nitrogen": self._assess_nutrient("nitrogen", n, "N", "ไนโตรเจน"),
            "phosphorus": self._assess_nutrient("phosphorus", p, "P", "ฟอสฟอรัส"),
            "potassium": self._assess_nutrient("potassium", k, "K", "โพแทสเซียม")
        }

    def _assess_nutrient(self, nutrient: str, value: float, symbol: str, name_th: str) -> Dict:
        """Assess a single nutrient level."""
        thresholds = self.NUTRIENT_THRESHOLDS.get(nutrient, {"low": 20, "medium": 40, "high": 60})

        if value < thresholds["low"]:
            status = "low"
            status_th = "ต่ำ"
            score = 40
        elif value < thresholds["medium"]:
            status = "medium"
            status_th = "ปานกลาง"
            score = 70
        else:
            status = "high"
            status_th = "สูง"
            score = 95

        return {
            "symbol": symbol,
            "name_th": name_th,
            "value": value,
            "unit": "มก./กก.",
            "status": status,
            "status_th": status_th,
            "score": score,
            "thresholds": thresholds
        }

    def _calculate_health_score(self, ph_analysis: Dict, nutrient_analysis: Dict) -> float:
        """Calculate overall soil health score."""
        # pH contributes 30%
        ph_score = ph_analysis["score"] * 0.30

        # Nutrients contribute 70% (N=30%, P=20%, K=20%)
        n_score = nutrient_analysis["nitrogen"]["score"] * 0.30
        p_score = nutrient_analysis["phosphorus"]["score"] * 0.20
        k_score = nutrient_analysis["potassium"]["score"] * 0.20

        return ph_score + n_score + p_score + k_score

    def _identify_issues(self, ph_analysis: Dict, nutrient_analysis: Dict) -> List[str]:
        """Identify critical soil chemistry issues."""
        issues = []

        if ph_analysis["status"] in ["very_acidic", "acidic"]:
            issues.append("ดินเป็นกรดจัด ต้องใส่ปูน")
        elif ph_analysis["status"] in ["alkaline", "very_alkaline"]:
            issues.append("ดินเป็นด่างจัด")

        for nutrient, data in nutrient_analysis.items():
            if data["status"] == "low":
                issues.append(f"{data['name_th']}ต่ำ ต้องเพิ่ม")

        return issues

    def _generate_recommendations(self, ph_analysis: Dict, nutrient_analysis: Dict) -> List[str]:
        """Generate recommendations in Thai."""
        recs = []

        if ph_analysis["recommendation_th"]:
            recs.append(ph_analysis["recommendation_th"])

        for nutrient, data in nutrient_analysis.items():
            if data["status"] == "low":
                if nutrient == "nitrogen":
                    recs.append(f"เพิ่ม{data['name_th']}โดยใส่ปุ๋ยยูเรียหรือแอมโมเนียมซัลเฟต")
                elif nutrient == "phosphorus":
                    recs.append(f"เพิ่ม{data['name_th']}โดยใส่ปุ๋ยซุปเปอร์ฟอสเฟต")
                elif nutrient == "potassium":
                    recs.append(f"เพิ่ม{data['name_th']}โดยใส่ปุ๋ยโพแทสเซียมคลอไรด์")

        return recs
