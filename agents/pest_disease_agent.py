"""
S.O.I.L.E.R. Agent #4: Pest & Disease Expert
ผู้เชี่ยวชาญโรคและแมลง - Analyzes pest/disease risks and prevention.
"""

from typing import Any, Dict, List
from agents.base_agent import BaseAgent


class PestDiseaseAgent(BaseAgent):
    """
    ผู้เชี่ยวชาญโรคและแมลง (Pest & Disease Expert)

    หน้าที่:
    - ประเมินความเสี่ยงโรคและแมลงศัตรูพืช
    - แนะนำมาตรการป้องกัน
    - วางแผนการจัดการศัตรูพืชแบบผสมผสาน (IPM)
    """

    # Common pests and diseases database
    PEST_DATABASE = {
        "Riceberry Rice": {
            "pests": [
                {"name_th": "เพลี้ยกระโดดสีน้ำตาล", "name_en": "Brown planthopper", "risk": "high", "season": "rainy"},
                {"name_th": "หนอนกอข้าว", "name_en": "Rice stem borer", "risk": "medium", "season": "all"},
                {"name_th": "หนอนห่อใบข้าว", "name_en": "Leaf folder", "risk": "medium", "season": "rainy"},
            ],
            "diseases": [
                {"name_th": "โรคไหม้", "name_en": "Rice blast", "risk": "high", "condition": "humid"},
                {"name_th": "โรคขอบใบแห้ง", "name_en": "Bacterial leaf blight", "risk": "medium", "condition": "wet"},
                {"name_th": "โรคใบจุดสีน้ำตาล", "name_en": "Brown spot", "risk": "low", "condition": "nutrient_deficiency"},
            ]
        },
        "Corn": {
            "pests": [
                {"name_th": "หนอนกระทู้ข้าวโพดลายจุด", "name_en": "Fall armyworm", "risk": "high", "season": "all"},
                {"name_th": "เพลี้ยอ่อนข้าวโพด", "name_en": "Corn aphid", "risk": "medium", "season": "dry"},
                {"name_th": "ด้วงงวงข้าวโพด", "name_en": "Corn weevil", "risk": "medium", "season": "storage"},
            ],
            "diseases": [
                {"name_th": "โรคใบไหม้แผลใหญ่", "name_en": "Northern corn leaf blight", "risk": "high", "condition": "humid"},
                {"name_th": "โรคราน้ำค้าง", "name_en": "Downy mildew", "risk": "medium", "condition": "wet"},
                {"name_th": "โรคลำต้นเน่า", "name_en": "Stalk rot", "risk": "medium", "condition": "waterlogged"},
            ]
        }
    }

    def __init__(self, verbose: bool = True):
        super().__init__(
            agent_name="PestDiseaseExpert",
            agent_name_th="ผู้เชี่ยวชาญโรคและแมลง",
            verbose=verbose
        )

    def _execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """วิเคราะห์ความเสี่ยงโรคและแมลงศัตรูพืช"""
        self.think("กำลังประเมินความเสี่ยงโรคและแมลงศัตรูพืช...")

        target_crop = input_data.get("target_crop", "Corn")
        season = input_data.get("season", "rainy")
        humidity = input_data.get("humidity", 75)
        irrigation = input_data.get("irrigation_available", True)

        # Get pest/disease data for crop
        crop_data = self.PEST_DATABASE.get(target_crop, self.PEST_DATABASE.get("Corn"))

        # Analyze pest risks
        self.think("กำลังวิเคราะห์ความเสี่ยงจากแมลงศัตรูพืช...")
        pest_analysis = self._analyze_pests(crop_data.get("pests", []), season)

        # Analyze disease risks
        self.think("กำลังวิเคราะห์ความเสี่ยงจากโรคพืช...")
        disease_analysis = self._analyze_diseases(crop_data.get("diseases", []), humidity, irrigation)

        # Calculate overall risk
        high_risk_count = len([p for p in pest_analysis if p["risk_level"] == "high"])
        high_risk_count += len([d for d in disease_analysis if d["risk_level"] == "high"])

        if high_risk_count >= 3:
            overall_risk = "สูง"
            overall_risk_score = 75
        elif high_risk_count >= 1:
            overall_risk = "ปานกลาง"
            overall_risk_score = 50
        else:
            overall_risk = "ต่ำ"
            overall_risk_score = 25

        self.log_result(f"ความเสี่ยงโดยรวม: {overall_risk}")

        # Generate IPM recommendations
        self.think("กำลังสร้างแผนจัดการศัตรูพืชแบบผสมผสาน (IPM)...")
        ipm_plan = self._generate_ipm_plan(pest_analysis, disease_analysis)

        # Build observation in Thai
        top_pests = [p["name_th"] for p in pest_analysis if p["risk_level"] == "high"][:2]
        top_diseases = [d["name_th"] for d in disease_analysis if d["risk_level"] == "high"][:2]

        observation_th = (
            f"ผู้เชี่ยวชาญโรคและแมลง: ความเสี่ยงโดยรวม{overall_risk} "
            f"แมลงที่ต้องระวัง: {', '.join(top_pests) if top_pests else 'ไม่มีที่เสี่ยงสูง'} "
            f"โรคที่ต้องระวัง: {', '.join(top_diseases) if top_diseases else 'ไม่มีที่เสี่ยงสูง'} "
            f"แนะนำใช้วิธี IPM ผสมผสาน"
        )

        return {
            "crop": target_crop,
            "pest_analysis": pest_analysis,
            "disease_analysis": disease_analysis,
            "overall_risk": overall_risk,
            "overall_risk_score": overall_risk_score,
            "ipm_plan": ipm_plan,
            "prevention_calendar": self._create_prevention_calendar(pest_analysis, disease_analysis),
            "chemical_recommendations": self._get_chemical_recommendations(pest_analysis, disease_analysis),
            "organic_alternatives": self._get_organic_alternatives(),
            "observation_th": observation_th
        }

    def _analyze_pests(self, pests: List[Dict], season: str) -> List[Dict]:
        """Analyze pest risks for current conditions."""
        analysis = []
        for pest in pests:
            # Adjust risk based on season
            base_risk = pest.get("risk", "medium")
            pest_season = pest.get("season", "all")

            if pest_season == "all" or pest_season == season:
                risk_level = base_risk
            else:
                risk_level = "low" if base_risk != "high" else "medium"

            analysis.append({
                "name_th": pest["name_th"],
                "name_en": pest["name_en"],
                "risk_level": risk_level,
                "risk_level_th": self._translate_risk(risk_level),
                "prevention_th": self._get_pest_prevention(pest["name_en"]),
                "monitoring_th": "ตรวจแปลงทุก 3-5 วัน"
            })

        return analysis

    def _analyze_diseases(self, diseases: List[Dict], humidity: float, irrigation: bool) -> List[Dict]:
        """Analyze disease risks for current conditions."""
        analysis = []
        for disease in diseases:
            base_risk = disease.get("risk", "medium")
            condition = disease.get("condition", "")

            # Adjust risk based on conditions
            risk_level = base_risk
            if condition == "humid" and humidity > 80:
                risk_level = "high"
            elif condition == "wet" and irrigation:
                risk_level = "high" if base_risk == "medium" else base_risk

            analysis.append({
                "name_th": disease["name_th"],
                "name_en": disease["name_en"],
                "risk_level": risk_level,
                "risk_level_th": self._translate_risk(risk_level),
                "favorable_condition_th": self._translate_condition(condition),
                "prevention_th": self._get_disease_prevention(disease["name_en"])
            })

        return analysis

    def _translate_risk(self, risk: str) -> str:
        """Translate risk level to Thai."""
        return {"high": "สูง", "medium": "ปานกลาง", "low": "ต่ำ"}.get(risk, "ปานกลาง")

    def _translate_condition(self, condition: str) -> str:
        """Translate condition to Thai."""
        translations = {
            "humid": "อากาศชื้นสูง",
            "wet": "ฝนตกชุก/น้ำขัง",
            "dry": "อากาศแห้ง",
            "nutrient_deficiency": "ขาดธาตุอาหาร",
            "waterlogged": "น้ำท่วมขัง",
            "storage": "ช่วงเก็บรักษา"
        }
        return translations.get(condition, condition)

    def _get_pest_prevention(self, pest_name: str) -> str:
        """Get prevention measures for specific pest."""
        preventions = {
            "Brown planthopper": "ใช้พันธุ์ต้านทาน ไม่ใส่ปุ๋ยไนโตรเจนมากเกินไป",
            "Rice stem borer": "ทำลายตอซัง หว่านเมล็ดให้พร้อมกัน",
            "Leaf folder": "ไม่ใส่ปุ๋ยไนโตรเจนมากเกินไป ใช้แสงไฟล่อแมลง",
            "Fall armyworm": "ตรวจแปลงบ่อย ใช้สารชีวภัณฑ์ Bt",
            "Corn aphid": "ใช้แมลงศัตรูธรรมชาติ เช่น ด้วงเต่าลาย",
            "Corn weevil": "ตากเมล็ดให้แห้ง เก็บในที่แห้งสนิท"
        }
        return preventions.get(pest_name, "ตรวจแปลงสม่ำเสมอ ใช้ศัตรูธรรมชาติ")

    def _get_disease_prevention(self, disease_name: str) -> str:
        """Get prevention measures for specific disease."""
        preventions = {
            "Rice blast": "ใช้พันธุ์ต้านทาน ไม่ใส่ไนโตรเจนมากเกินไป",
            "Bacterial leaf blight": "ใช้พันธุ์ต้านทาน ระบายน้ำดี",
            "Brown spot": "ใส่ปุ๋ยให้สมดุล เพิ่มโพแทสเซียม",
            "Northern corn leaf blight": "ใช้พันธุ์ต้านทาน หมุนเวียนพืช",
            "Downy mildew": "ใช้เมล็ดพันธุ์ปลอดโรค คลุกเมล็ดด้วยสารป้องกัน",
            "Stalk rot": "ระบายน้ำดี ไม่ปลูกหนาแน่นเกินไป"
        }
        return preventions.get(disease_name, "ใช้พันธุ์ต้านทาน ปลูกให้ถูกระยะ")

    def _generate_ipm_plan(self, pests: List, diseases: List) -> Dict:
        """Generate Integrated Pest Management plan."""
        return {
            "cultural_practices_th": [
                "ใช้พันธุ์ต้านทานโรคและแมลง",
                "ปลูกให้ถูกระยะ ไม่หนาแน่นเกินไป",
                "กำจัดวัชพืชที่เป็นแหล่งอาศัยของศัตรูพืช",
                "หมุนเวียนพืช ไม่ปลูกพืชชนิดเดียวซ้ำ"
            ],
            "biological_control_th": [
                "ใช้แตนเบียนไข่ไตรโคแกรมมา",
                "ใช้เชื้อราบิวเวอเรียกำจัดแมลง",
                "ใช้เชื้อแบคทีเรีย Bt กำจัดหนอน",
                "อนุรักษ์แมลงศัตรูธรรมชาติ"
            ],
            "monitoring_th": [
                "ตรวจแปลงทุก 3-5 วัน",
                "ใช้กับดักแสงไฟล่อแมลง",
                "สังเกตอาการผิดปกติของพืช",
                "บันทึกข้อมูลทุกครั้ง"
            ],
            "chemical_last_resort_th": "ใช้สารเคมีเฉพาะเมื่อจำเป็น และเลือกสารที่ปลอดภัย"
        }

    def _create_prevention_calendar(self, pests: List, diseases: List) -> List[Dict]:
        """Create prevention calendar."""
        return [
            {"stage_th": "ก่อนปลูก", "activities_th": ["คลุกเมล็ดด้วยสารป้องกันเชื้อรา", "เตรียมกับดักแมลง"]},
            {"stage_th": "ระยะกล้า", "activities_th": ["ตรวจโรคในแปลงกล้า", "ป้องกันหนูและนก"]},
            {"stage_th": "ระยะเจริญเติบโต", "activities_th": ["ตรวจแมลงทุกสัปดาห์", "พ่นสารชีวภัณฑ์ป้องกัน"]},
            {"stage_th": "ระยะออกดอก", "activities_th": ["ระวังโรคที่มากับความชื้น", "ตรวจหนอนเจาะ"]},
            {"stage_th": "ระยะเก็บเกี่ยว", "activities_th": ["งดพ่นสารเคมี 14 วันก่อนเก็บเกี่ยว"]}
        ]

    def _get_chemical_recommendations(self, pests: List, diseases: List) -> List[Dict]:
        """Get chemical recommendations if needed."""
        return [
            {"type_th": "สารกำจัดแมลง", "name": "คลอร์ไพริฟอส", "note_th": "ใช้เฉพาะเมื่อระบาดรุนแรง"},
            {"type_th": "สารป้องกันเชื้อรา", "name": "แมนโคเซบ", "note_th": "พ่นป้องกันก่อนโรคระบาด"}
        ]

    def _get_organic_alternatives(self) -> List[Dict]:
        """Get organic pest control alternatives."""
        return [
            {"name_th": "น้ำหมักสมุนไพร", "target_th": "แมลงปากดูด", "how_th": "ผสมน้ำ 1:50 ฉีดพ่น"},
            {"name_th": "เชื้อ Bt", "target_th": "หนอนผีเสื้อ", "how_th": "ผสมน้ำตามฉลาก ฉีดพ่นตอนเย็น"},
            {"name_th": "เชื้อราบิวเวอเรีย", "target_th": "แมลงทั่วไป", "how_th": "ผสมน้ำ ฉีดพ่นในที่ร่ม"},
            {"name_th": "น้ำส้มควันไม้", "target_th": "ป้องกันแมลงหลายชนิด", "how_th": "ผสมน้ำ 1:100 ฉีดพ่น"}
        ]
