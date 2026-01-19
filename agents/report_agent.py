"""
S.O.I.L.E.R. Agent #8: Report Agent (ผู้สรุปรายงาน)
Formats and compiles the final executive report from all 8 agent outputs.
"""

from datetime import datetime
from typing import Any, Dict, List

from agents.base_agent import BaseAgent


class ReportAgent(BaseAgent):
    """
    ผู้สรุปรายงาน (Report Agent)

    หน้าที่:
    - รวบรวมข้อมูลจากทุก Agent
    - สร้างสรุปผู้บริหาร
    - จัดทำแผนปฏิบัติการ
    - สรุปความเสี่ยงและคำแนะนำ
    """

    def __init__(self, verbose: bool = True):
        super().__init__(
            agent_name="ChiefReporter",
            agent_name_th="ผู้สรุปรายงาน",
            verbose=verbose
        )

    def _execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """รวบรวมและสรุปรายงาน"""
        self.think("กำลังรวบรวมข้อมูลจากทุก Agent...")

        # Extract all inputs
        session_id = input_data.get("session_id", "N/A")
        sample_id = input_data.get("sample_id", "N/A")
        location = input_data.get("location", "ไม่ระบุ")
        target_crop = input_data.get("target_crop", "ข้าวโพด")
        field_size_rai = input_data.get("field_size_rai", 1.0)

        # Agent results
        soil_series = input_data.get("soil_series_analysis", {})
        soil_chemistry = input_data.get("soil_chemistry_analysis", {})
        crop_biology = input_data.get("crop_biology_analysis", {})
        pest_disease = input_data.get("pest_disease_analysis", {})
        climate = input_data.get("climate_analysis", {})
        fertilizer = input_data.get("fertilizer_analysis", {})
        market = input_data.get("market_analysis", {})

        # Step 1: Collect all Thai observations
        self.think("กำลังรวบรวมข้อสังเกตจากทุก Agent...")
        observations = self._collect_observations(input_data)
        self.log_result(f"รวบรวมข้อสังเกต {len(observations)} รายการ")

        # Step 2: Generate executive summary
        self.think("กำลังสร้างสรุปผู้บริหาร...")
        executive_summary = self._generate_executive_summary_th(
            soil_series, soil_chemistry, crop_biology,
            pest_disease, climate, fertilizer, market,
            target_crop, field_size_rai
        )

        # Step 3: Compile key metrics dashboard
        self.think("กำลังรวบรวมตัวชี้วัดสำคัญ...")
        dashboard = self._compile_dashboard_th(
            soil_chemistry, crop_biology, market, field_size_rai
        )

        # Step 4: Generate action plan
        self.think("กำลังสร้างแผนปฏิบัติการ...")
        action_plan = self._generate_action_plan_th(
            soil_series, soil_chemistry, crop_biology,
            pest_disease, climate, fertilizer, market
        )
        self.log_result(f"สร้างแผนปฏิบัติการ {len(action_plan)} รายการ")

        # Step 5: Compile risk matrix
        self.think("กำลังรวบรวมความเสี่ยง...")
        risk_matrix = self._compile_risk_matrix_th(
            soil_chemistry, pest_disease, climate, market
        )

        # Step 6: Create fertilizer schedule
        fertilizer_schedule = self._format_fertilizer_schedule_th(fertilizer)

        # Step 7: Financial summary
        financial_summary = self._create_financial_summary_th(market, field_size_rai)

        # Step 8: Crop calendar
        crop_calendar = self._create_crop_calendar_th(crop_biology, climate)

        # Step 9: Final recommendations
        recommendations = self._compile_recommendations_th(
            soil_series, soil_chemistry, crop_biology,
            pest_disease, climate, fertilizer, market
        )

        # Build Thai observation
        observation_th = (
            f"ผู้สรุปรายงาน: รายงานสมบูรณ์ "
            f"สถานะโดยรวม{executive_summary['overall_status_th']} "
            f"(คะแนน {executive_summary['overall_score']:.0f}/100) "
            f"แผนปฏิบัติการ {len(action_plan)} รายการ "
            f"ความเสี่ยงสูง {risk_matrix['summary']['high_severity']} รายการ"
        )

        # Build the complete report
        report = {
            # Header
            "report_metadata": {
                "title": "รายงานการวิเคราะห์ S.O.I.L.E.R.",
                "subtitle": "ระบบแนะนำการเกษตรอัจฉริยะ",
                "report_id": f"SOILER-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
                "session_id": session_id,
                "sample_id": sample_id,
                "generated_at": datetime.now().isoformat(),
                "generated_by": "S.O.I.L.E.R. Multi-Agent AI System v2.0"
            },

            # Project Info
            "project_info": {
                "location": location,
                "location_th": f"ตำแหน่ง: {location}",
                "target_crop": target_crop,
                "target_crop_th": crop_biology.get("crop_name_th", target_crop),
                "field_size_rai": field_size_rai,
                "field_size_th": f"{field_size_rai} ไร่",
                "analysis_date": datetime.now().strftime("%Y-%m-%d"),
                "analysis_date_th": self._format_thai_date(datetime.now())
            },

            # Executive Summary
            "executive_summary": executive_summary,

            # Key Metrics Dashboard
            "dashboard": dashboard,

            # Agent Observations Chain (Thai)
            "agent_observations": observations,

            # Detailed Sections
            "sections": {
                "soil_series": self._format_soil_series_section_th(soil_series),
                "soil_chemistry": self._format_soil_chemistry_section_th(soil_chemistry),
                "crop_planning": self._format_crop_section_th(crop_biology),
                "pest_disease": self._format_pest_section_th(pest_disease),
                "climate": self._format_climate_section_th(climate),
                "fertilizer": fertilizer_schedule,
                "financial": financial_summary,
                "risks": risk_matrix
            },

            # Action Plan
            "action_plan": action_plan,

            # Crop Calendar
            "crop_calendar": crop_calendar,

            # Final Recommendations
            "recommendations": recommendations,

            # Appendix
            "appendix": {
                "methodology_th": "วิเคราะห์โดยระบบ AI หลาย Agent ของ S.O.I.L.E.R.",
                "data_sources_th": [
                    "ข้อมูลดินจากผู้ใช้",
                    "ฐานข้อมูลชุดดินจังหวัดแพร่",
                    "ฐานข้อมูลความต้องการพืช",
                    "ข้อมูลภูมิอากาศย้อนหลัง",
                    "ราคาปุ๋ยและผลผลิตปัจจุบัน"
                ],
                "disclaimer_th": (
                    "รายงานนี้สร้างโดยระบบ AI ควรใช้เป็นแนวทาง "
                    "ปรึกษาเจ้าหน้าที่ส่งเสริมการเกษตรเพื่อคำแนะนำเฉพาะพื้นที่ "
                    "ผลลัพธ์จริงอาจแตกต่างตามสภาพอากาศและการจัดการ"
                ),
                "agents_involved_th": [
                    "ผู้เชี่ยวชาญชุดดิน",
                    "ผู้เชี่ยวชาญเคมีดิน",
                    "ผู้เชี่ยวชาญชีววิทยาพืช",
                    "ผู้เชี่ยวชาญโรคและแมลง",
                    "ผู้เชี่ยวชาญภูมิอากาศ",
                    "ผู้เชี่ยวชาญสูตรปุ๋ย",
                    "ผู้เชี่ยวชาญตลาดและต้นทุน",
                    "ผู้สรุปรายงาน"
                ]
            },

            "observation_th": observation_th
        }

        self.log_result("รายงานเสร็จสมบูรณ์")

        return report

    def _format_thai_date(self, dt: datetime) -> str:
        """Format date in Thai."""
        thai_months = [
            "", "มกราคม", "กุมภาพันธ์", "มีนาคม", "เมษายน",
            "พฤษภาคม", "มิถุนายน", "กรกฎาคม", "สิงหาคม",
            "กันยายน", "ตุลาคม", "พฤศจิกายน", "ธันวาคม"
        ]
        thai_year = dt.year + 543
        return f"{dt.day} {thai_months[dt.month]} {thai_year}"

    def _collect_observations(self, input_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Collect Thai observations from all agents."""
        observations = []

        agent_keys = [
            ("soil_series_analysis", "ผู้เชี่ยวชาญชุดดิน"),
            ("soil_chemistry_analysis", "ผู้เชี่ยวชาญเคมีดิน"),
            ("crop_biology_analysis", "ผู้เชี่ยวชาญชีววิทยาพืช"),
            ("pest_disease_analysis", "ผู้เชี่ยวชาญโรคและแมลง"),
            ("climate_analysis", "ผู้เชี่ยวชาญภูมิอากาศ"),
            ("fertilizer_analysis", "ผู้เชี่ยวชาญสูตรปุ๋ย"),
            ("market_analysis", "ผู้เชี่ยวชาญตลาดและต้นทุน"),
        ]

        for key, agent_name in agent_keys:
            data = input_data.get(key, {})
            obs = data.get("observation_th", "")
            if obs:
                observations.append({
                    "agent_th": agent_name,
                    "observation_th": obs
                })

        return observations

    def _generate_executive_summary_th(
        self,
        soil_series: Dict, soil_chemistry: Dict, crop_biology: Dict,
        pest_disease: Dict, climate: Dict, fertilizer: Dict, market: Dict,
        target_crop: str, field_size: float
    ) -> Dict[str, Any]:
        """Generate executive summary in Thai."""
        # Collect scores
        soil_score = soil_chemistry.get("health_score", 60)
        climate_score = climate.get("suitability", {}).get("score", 70)
        roi = market.get("profit_analysis", {}).get("roi_percent", 30)
        pest_risk = pest_disease.get("overall_risk_score", 50)

        # Calculate overall score
        overall_score = (
            soil_score * 0.25 +
            climate_score * 0.25 +
            min(max(roi, 0), 100) * 0.25 +
            (100 - pest_risk) * 0.25
        )

        # Status in Thai
        if overall_score >= 75:
            status_th = "ดีเยี่ยม"
            status_color = "green"
        elif overall_score >= 55:
            status_th = "ดี"
            status_color = "green"
        elif overall_score >= 40:
            status_th = "ปานกลาง"
            status_color = "yellow"
        else:
            status_th = "ต้องระวัง"
            status_color = "red"

        # Key highlights in Thai
        highlights = []

        if soil_score >= 70:
            highlights.append(f"✓ สุขภาพดินดี ({soil_score:.0f}/100)")
        else:
            highlights.append(f"△ ดินต้องปรับปรุง ({soil_score:.0f}/100)")

        if climate_score >= 70:
            highlights.append(f"✓ ภูมิอากาศเหมาะสม")
        else:
            highlights.append(f"△ มีความท้าทายด้านภูมิอากาศ")

        if roi >= 50:
            highlights.append(f"✓ ROI ดีมาก ({roi:.0f}%)")
        elif roi >= 0:
            highlights.append(f"○ ROI ปานกลาง ({roi:.0f}%)")
        else:
            highlights.append(f"✗ ROI ติดลบ ({roi:.0f}%)")

        # Bottom line in Thai
        yield_target = crop_biology.get("yield_targets", {}).get("target_kg_per_rai", 500)
        total_yield = yield_target * field_size
        profit = market.get("profit_analysis", {}).get("net_profit", 0)

        bottom_line = (
            f"พื้นที่ {field_size} ไร่ ปลูก{market.get('crop_name_th', target_crop)} "
            f"คาดว่าจะได้ผลผลิต {total_yield:,.0f} กก. "
            f"{'กำไร' if profit >= 0 else 'ขาดทุน'} {abs(profit):,.0f} บาท"
        )

        return {
            "overall_status_th": status_th,
            "overall_score": overall_score,
            "status_color": status_color,
            "target_crop_th": crop_biology.get("crop_name_th", target_crop),
            "field_size_rai": field_size,
            "highlights_th": highlights,
            "bottom_line_th": bottom_line,
            "confidence_th": "สูง" if overall_score >= 60 else "ปานกลาง"
        }

    def _compile_dashboard_th(
        self,
        soil_chemistry: Dict, crop_biology: Dict, market: Dict, field_size: float
    ) -> Dict[str, Any]:
        """Compile dashboard metrics in Thai."""
        return {
            "soil_health": {
                "score": soil_chemistry.get("health_score", 0),
                "max": 100,
                "status_th": self._score_to_status_th(soil_chemistry.get("health_score", 0))
            },
            "yield_target": {
                "value": crop_biology.get("yield_targets", {}).get("target_kg_per_rai", 0),
                "unit_th": "กก./ไร่",
                "total": crop_biology.get("yield_targets", {}).get("total_kg", 0),
                "total_unit_th": "กก."
            },
            "investment": {
                "total_cost": market.get("cost_analysis", {}).get("total_cost", 0),
                "cost_per_rai": market.get("cost_analysis", {}).get("cost_per_rai", 0),
                "unit_th": "บาท"
            },
            "returns": {
                "revenue": market.get("profit_analysis", {}).get("total_revenue", 0),
                "profit": market.get("profit_analysis", {}).get("net_profit", 0),
                "roi_percent": market.get("profit_analysis", {}).get("roi_percent", 0)
            }
        }

    def _score_to_status_th(self, score: float) -> str:
        """Convert score to Thai status."""
        if score >= 80:
            return "ดีเยี่ยม"
        elif score >= 60:
            return "ดี"
        elif score >= 40:
            return "พอใช้"
        else:
            return "ต้องปรับปรุง"

    def _generate_action_plan_th(
        self,
        soil_series: Dict, soil_chemistry: Dict, crop_biology: Dict,
        pest_disease: Dict, climate: Dict, fertilizer: Dict, market: Dict
    ) -> List[Dict[str, Any]]:
        """Generate prioritized action plan in Thai."""
        actions = []
        priority = 1

        # Critical soil issues
        for issue in soil_chemistry.get("issues", []):
            actions.append({
                "priority": priority,
                "urgency_th": "วิกฤต",
                "action_th": f"แก้ไขปัญหาดิน: {issue}",
                "category_th": "การจัดการดิน",
                "timeline_th": "ก่อนปลูก"
            })
            priority += 1

        # Weather risks
        for risk in climate.get("weather_risks", []):
            if risk.get("severity") == "high":
                actions.append({
                    "priority": priority,
                    "urgency_th": "สูง",
                    "action_th": f"เตรียมรับมือ{risk.get('risk_th', '')}",
                    "category_th": "การบริหารความเสี่ยง",
                    "timeline_th": "ทันที",
                    "mitigation_th": risk.get("mitigation_th", "")
                })
                priority += 1

        # Fertilizer applications
        for app in fertilizer.get("application_schedule", [])[:3]:
            actions.append({
                "priority": priority,
                "urgency_th": "สูง",
                "action_th": f"ใส่ปุ๋ย{app.get('name_th', '')} {app.get('rate_kg_per_rai', 0):.1f} กก./ไร่",
                "category_th": "การใส่ปุ๋ย",
                "timeline_th": app.get("stage_th", "ตามกำหนด")
            })
            priority += 1

        # Pest/disease prevention
        for pest in pest_disease.get("pest_analysis", [])[:2]:
            if pest.get("risk_level") == "high":
                actions.append({
                    "priority": priority,
                    "urgency_th": "สูง",
                    "action_th": f"ป้องกัน{pest.get('name_th', '')}",
                    "category_th": "การป้องกันศัตรูพืช",
                    "timeline_th": "ตลอดฤดู",
                    "method_th": pest.get("prevention_th", "")
                })
                priority += 1

        return actions

    def _compile_risk_matrix_th(
        self,
        soil_chemistry: Dict, pest_disease: Dict, climate: Dict, market: Dict
    ) -> Dict[str, Any]:
        """Compile risk matrix in Thai."""
        all_risks = []

        # Soil risks
        for issue in soil_chemistry.get("issues", []):
            all_risks.append({
                "risk_th": issue,
                "category_th": "ดิน",
                "severity_th": "สูง"
            })

        # Pest/disease risks
        for pest in pest_disease.get("pest_analysis", []):
            if pest.get("risk_level") in ["high", "medium"]:
                all_risks.append({
                    "risk_th": pest.get("name_th", ""),
                    "category_th": "ศัตรูพืช",
                    "severity_th": pest.get("risk_level_th", "ปานกลาง")
                })

        # Climate risks
        for risk in climate.get("weather_risks", []):
            all_risks.append({
                "risk_th": risk.get("risk_th", ""),
                "category_th": "ภูมิอากาศ",
                "severity_th": risk.get("severity_th", "ปานกลาง"),
                "mitigation_th": risk.get("mitigation_th", "")
            })

        # Market risks
        for risk in market.get("market_risks", []):
            all_risks.append({
                "risk_th": risk.get("risk_th", ""),
                "category_th": "ตลาด",
                "severity_th": risk.get("severity_th", "ปานกลาง")
            })

        # Summary
        high_count = len([r for r in all_risks if r.get("severity_th") == "สูง"])
        medium_count = len([r for r in all_risks if r.get("severity_th") == "ปานกลาง"])
        low_count = len([r for r in all_risks if r.get("severity_th") == "ต่ำ"])

        return {
            "risks": all_risks,
            "summary": {
                "total_risks": len(all_risks),
                "high_severity": high_count,
                "medium_severity": medium_count,
                "low_severity": low_count
            },
            "overall_rating_th": "สูง" if high_count >= 2 else ("ปานกลาง" if high_count >= 1 else "ต่ำ")
        }

    def _format_fertilizer_schedule_th(self, fertilizer: Dict) -> Dict[str, Any]:
        """Format fertilizer schedule in Thai."""
        schedule = fertilizer.get("application_schedule", [])
        return {
            "schedule": schedule,
            "total_applications": len(schedule),
            "total_cost_thb": fertilizer.get("cost_analysis", {}).get("total_cost", 0),
            "cost_per_rai_thb": fertilizer.get("cost_analysis", {}).get("cost_per_rai", 0),
            "within_budget": fertilizer.get("within_budget", True),
            "recommendations_th": fertilizer.get("recommendations_th", [])
        }

    def _create_financial_summary_th(self, market: Dict, field_size: float) -> Dict[str, Any]:
        """Create financial summary in Thai."""
        cost = market.get("cost_analysis", {})
        profit = market.get("profit_analysis", {})

        return {
            "investment_th": {
                "total_cost": cost.get("total_cost", 0),
                "cost_per_rai": cost.get("cost_per_rai", 0),
                "breakdown": cost.get("breakdown", [])
            },
            "revenue_th": {
                "total_revenue": profit.get("total_revenue", 0),
                "price_per_kg": market.get("market_analysis", {}).get("farm_gate_price", 0)
            },
            "profit_th": {
                "net_profit": profit.get("net_profit", 0),
                "profit_per_rai": profit.get("profit_per_rai", 0),
                "roi_percent": profit.get("roi_percent", 0),
                "is_profitable": profit.get("is_profitable", False)
            },
            "breakeven_th": {
                "yield_required": profit.get("break_even_per_rai", 0),
                "unit_th": "กก./ไร่"
            }
        }

    def _create_crop_calendar_th(self, crop_biology: Dict, climate: Dict) -> List[Dict[str, Any]]:
        """Create crop calendar in Thai."""
        return crop_biology.get("growth_calendar", [])

    def _format_soil_series_section_th(self, soil_series: Dict) -> Dict[str, Any]:
        """Format soil series section in Thai."""
        return {
            "series_name_th": soil_series.get("series_name_th", "ไม่ทราบ"),
            "series_name": soil_series.get("series_name", "Unknown"),
            "match_score": soil_series.get("match_score", 0),
            "characteristics_th": soil_series.get("characteristics_th", {}),
            "limitations_th": soil_series.get("limitations_th", []),
            "management_th": soil_series.get("management_recommendations_th", [])
        }

    def _format_soil_chemistry_section_th(self, soil_chemistry: Dict) -> Dict[str, Any]:
        """Format soil chemistry section in Thai."""
        return {
            "ph_analysis": soil_chemistry.get("ph_analysis", {}),
            "nutrient_analysis": soil_chemistry.get("nutrient_analysis", {}),
            "health_score": soil_chemistry.get("health_score", 0),
            "issues": soil_chemistry.get("issues", []),
            "recommendations_th": soil_chemistry.get("recommendations_th", [])
        }

    def _format_crop_section_th(self, crop_biology: Dict) -> Dict[str, Any]:
        """Format crop section in Thai."""
        return {
            "crop_name_th": crop_biology.get("crop_name_th", ""),
            "growth_cycle_days": crop_biology.get("growth_cycle_days", 0),
            "planting_date": crop_biology.get("planting_date", ""),
            "harvest_date": crop_biology.get("harvest_date", ""),
            "yield_targets": crop_biology.get("yield_targets", {}),
            "water_requirements": crop_biology.get("water_requirements", {}),
            "critical_periods": crop_biology.get("critical_periods", [])
        }

    def _format_pest_section_th(self, pest_disease: Dict) -> Dict[str, Any]:
        """Format pest/disease section in Thai."""
        return {
            "overall_risk": pest_disease.get("overall_risk", ""),
            "pest_analysis": pest_disease.get("pest_analysis", []),
            "disease_analysis": pest_disease.get("disease_analysis", []),
            "ipm_plan": pest_disease.get("ipm_plan", {}),
            "organic_alternatives": pest_disease.get("organic_alternatives", [])
        }

    def _format_climate_section_th(self, climate: Dict) -> Dict[str, Any]:
        """Format climate section in Thai."""
        return {
            "suitability": climate.get("suitability", {}),
            "weather_risks": climate.get("weather_risks", []),
            "planting_window": climate.get("planting_window", {}),
            "recommendations_th": climate.get("recommendations_th", [])
        }

    def _compile_recommendations_th(
        self,
        soil_series: Dict, soil_chemistry: Dict, crop_biology: Dict,
        pest_disease: Dict, climate: Dict, fertilizer: Dict, market: Dict
    ) -> Dict[str, List[str]]:
        """Compile all recommendations in Thai."""
        recommendations = {
            "immediate_th": [],
            "pre_planting_th": [],
            "during_growth_th": [],
            "financial_th": [],
            "long_term_th": []
        }

        # Immediate
        for issue in soil_chemistry.get("issues", []):
            recommendations["immediate_th"].append(f"แก้ไข: {issue}")

        # Pre-planting
        recommendations["pre_planting_th"].extend(
            soil_chemistry.get("recommendations_th", [])[:3]
        )
        recommendations["pre_planting_th"].extend(
            soil_series.get("management_recommendations_th", [])[:2]
        )

        # During growth
        recommendations["during_growth_th"].extend(
            fertilizer.get("recommendations_th", [])[:3]
        )
        recommendations["during_growth_th"].extend(
            climate.get("recommendations_th", [])[:2]
        )

        # Financial
        recommendations["financial_th"].extend(
            market.get("recommendations_th", [])[:3]
        )

        # Long-term
        recommendations["long_term_th"] = [
            "เพิ่มอินทรียวัตถุในดินโดยใช้ปุ๋ยหมักหรือปุ๋ยพืชสด",
            "หมุนเวียนพืชเพื่อตัดวงจรศัตรูพืช",
            "ตรวจดินทุกปีเพื่อติดตามการเปลี่ยนแปลง",
            "พิจารณาทำเกษตรอินทรีย์เพื่อเพิ่มมูลค่า"
        ]

        return recommendations
