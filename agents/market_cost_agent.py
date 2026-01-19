"""
S.O.I.L.E.R. Agent #7: Market & Cost Expert
ผู้เชี่ยวชาญตลาดและต้นทุน - Analyzes market prices, costs, and profitability.
"""

from typing import Any, Dict, List
from agents.base_agent import BaseAgent
from data.knowledge_base import CROP_REQUIREMENTS


class MarketCostAgent(BaseAgent):
    """
    ผู้เชี่ยวชาญตลาดและต้นทุน (Market & Cost Expert)

    หน้าที่:
    - วิเคราะห์ราคาตลาดและแนวโน้ม
    - คำนวณต้นทุนการผลิต
    - ประเมินผลตอบแทนการลงทุน (ROI)
    - แนะนำช่องทางการตลาด
    """

    # Market price data (THB per kg)
    MARKET_PRICES = {
        "Riceberry Rice": {
            "farm_gate": 25,
            "wholesale": 35,
            "retail": 55,
            "organic_premium": 1.3,
            "trend_th": "ราคาทรงตัว มีแนวโน้มดีขึ้น"
        },
        "Corn": {
            "farm_gate": 8.5,
            "wholesale": 10,
            "retail": 15,
            "organic_premium": 1.2,
            "trend_th": "ราคาผันผวนตามตลาดโลก"
        }
    }

    # Production cost templates (THB per rai)
    COST_TEMPLATES = {
        "Riceberry Rice": {
            "land_prep": 800,
            "seeds": 400,
            "fertilizer": 1500,
            "pesticide": 300,
            "water": 500,
            "labor": 2000,
            "harvest": 800,
            "transport": 300
        },
        "Corn": {
            "land_prep": 600,
            "seeds": 350,
            "fertilizer": 1200,
            "pesticide": 400,
            "water": 200,
            "labor": 1000,
            "harvest": 500,
            "transport": 250
        }
    }

    def __init__(self, verbose: bool = True):
        super().__init__(
            agent_name="MarketCostExpert",
            agent_name_th="ผู้เชี่ยวชาญตลาดและต้นทุน",
            verbose=verbose
        )

    def _execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """วิเคราะห์ตลาดและต้นทุนการผลิต"""
        self.think("กำลังวิเคราะห์ข้อมูลตลาดและต้นทุน...")

        target_crop = input_data.get("target_crop", "Corn")
        field_size_rai = input_data.get("field_size_rai", 1.0)
        yield_kg_per_rai = input_data.get("yield_kg_per_rai", 600)
        fertilizer_cost = input_data.get("fertilizer_cost_thb", 0)
        is_organic = input_data.get("prefer_organic", False)

        # Get crop data
        crop_data = CROP_REQUIREMENTS.get(target_crop, {})
        crop_name_th = crop_data.get("name_th", target_crop)

        self.log_action(f"วิเคราะห์ตลาดสำหรับ: {crop_name_th}")

        # Analyze market prices
        self.think("กำลังวิเคราะห์ราคาตลาด...")
        market_analysis = self._analyze_market(target_crop, is_organic)
        self.log_result(f"ราคาหน้าฟาร์ม: {market_analysis['farm_gate_price']:.2f} บาท/กก.")

        # Calculate production costs
        self.think("กำลังคำนวณต้นทุนการผลิต...")
        cost_analysis = self._calculate_costs(target_crop, field_size_rai, fertilizer_cost)
        self.log_result(f"ต้นทุนรวม: {cost_analysis['total_cost']:,.0f} บาท")
        self.log_result(f"ต้นทุนต่อไร่: {cost_analysis['cost_per_rai']:,.0f} บาท/ไร่")

        # Calculate revenue and profit
        self.think("กำลังคำนวณรายได้และกำไร...")
        profit_analysis = self._calculate_profit(
            market_analysis, cost_analysis, yield_kg_per_rai, field_size_rai
        )
        self.log_result(f"รายได้คาดการณ์: {profit_analysis['total_revenue']:,.0f} บาท")
        self.log_result(f"กำไรสุทธิ: {profit_analysis['net_profit']:,.0f} บาท")

        # Calculate ROI
        roi = profit_analysis['roi_percent']
        self.log_result(f"ROI: {roi:.1f}%")

        # Market channels
        self.think("กำลังวิเคราะห์ช่องทางการตลาด...")
        channels = self._get_market_channels(target_crop, is_organic)

        # Risk assessment
        risks = self._assess_market_risks(target_crop, profit_analysis)

        # Build observation in Thai
        profit_status = "กำไร" if profit_analysis['net_profit'] > 0 else "ขาดทุน"
        observation_th = (
            f"ผู้เชี่ยวชาญตลาดและต้นทุน: {crop_name_th} ราคาหน้าฟาร์ม {market_analysis['farm_gate_price']:.0f} บาท/กก. "
            f"ต้นทุน {cost_analysis['cost_per_rai']:,.0f} บาท/ไร่ "
            f"รายได้คาดการณ์ {profit_analysis['total_revenue']:,.0f} บาท "
            f"{profit_status} {abs(profit_analysis['net_profit']):,.0f} บาท "
            f"ROI {roi:.1f}% "
            f"แนวโน้ม: {market_analysis['trend_th']}"
        )

        return {
            "crop_name": target_crop,
            "crop_name_th": crop_name_th,
            "field_size_rai": field_size_rai,
            "market_analysis": market_analysis,
            "cost_analysis": cost_analysis,
            "profit_analysis": profit_analysis,
            "market_channels": channels,
            "market_risks": risks,
            "recommendations_th": self._generate_recommendations(profit_analysis, market_analysis),
            "observation_th": observation_th
        }

    def _analyze_market(self, crop: str, is_organic: bool) -> Dict:
        """Analyze market prices for the crop."""
        prices = self.MARKET_PRICES.get(crop, self.MARKET_PRICES.get("Corn"))

        farm_gate = prices["farm_gate"]
        wholesale = prices["wholesale"]
        retail = prices["retail"]

        # Apply organic premium
        if is_organic:
            premium = prices.get("organic_premium", 1.2)
            farm_gate *= premium
            wholesale *= premium
            retail *= premium

        return {
            "farm_gate_price": farm_gate,
            "wholesale_price": wholesale,
            "retail_price": retail,
            "is_organic": is_organic,
            "organic_premium_percent": (prices.get("organic_premium", 1.0) - 1) * 100,
            "trend_th": prices.get("trend_th", "ราคาทรงตัว"),
            "price_range_th": f"{farm_gate:.0f}-{retail:.0f} บาท/กก."
        }

    def _calculate_costs(self, crop: str, field_size: float, fertilizer_cost: float) -> Dict:
        """Calculate production costs."""
        template = self.COST_TEMPLATES.get(crop, self.COST_TEMPLATES.get("Corn"))

        breakdown = []
        total_per_rai = 0

        cost_names_th = {
            "land_prep": "เตรียมดิน",
            "seeds": "เมล็ดพันธุ์",
            "fertilizer": "ปุ๋ย",
            "pesticide": "สารเคมี/ชีวภัณฑ์",
            "water": "น้ำ/ชลประทาน",
            "labor": "แรงงาน",
            "harvest": "เก็บเกี่ยว",
            "transport": "ขนส่ง"
        }

        for item, cost in template.items():
            # Use actual fertilizer cost if provided
            if item == "fertilizer" and fertilizer_cost > 0:
                cost_per_rai = fertilizer_cost / field_size if field_size > 0 else fertilizer_cost
            else:
                cost_per_rai = cost

            total_per_rai += cost_per_rai
            breakdown.append({
                "item": item,
                "item_th": cost_names_th.get(item, item),
                "cost_per_rai": cost_per_rai,
                "total_cost": cost_per_rai * field_size
            })

        return {
            "breakdown": breakdown,
            "cost_per_rai": total_per_rai,
            "total_cost": total_per_rai * field_size,
            "field_size_rai": field_size
        }

    def _calculate_profit(self, market: Dict, costs: Dict, yield_per_rai: float, field_size: float) -> Dict:
        """Calculate revenue, profit, and ROI."""
        total_yield = yield_per_rai * field_size

        # Revenue at different price points
        revenue_farm_gate = total_yield * market["farm_gate_price"]
        revenue_wholesale = total_yield * market["wholesale_price"]
        revenue_retail = total_yield * market["retail_price"]

        # Use farm gate as primary
        total_revenue = revenue_farm_gate
        total_cost = costs["total_cost"]
        net_profit = total_revenue - total_cost

        # ROI calculation
        roi = (net_profit / total_cost * 100) if total_cost > 0 else 0

        # Break-even analysis
        break_even_yield = total_cost / market["farm_gate_price"] if market["farm_gate_price"] > 0 else 0
        break_even_per_rai = break_even_yield / field_size if field_size > 0 else 0

        return {
            "total_yield_kg": total_yield,
            "yield_per_rai": yield_per_rai,
            "total_revenue": total_revenue,
            "revenue_farm_gate": revenue_farm_gate,
            "revenue_wholesale": revenue_wholesale,
            "revenue_retail": revenue_retail,
            "total_cost": total_cost,
            "net_profit": net_profit,
            "profit_per_rai": net_profit / field_size if field_size > 0 else 0,
            "roi_percent": roi,
            "break_even_yield_kg": break_even_yield,
            "break_even_per_rai": break_even_per_rai,
            "is_profitable": net_profit > 0
        }

    def _get_market_channels(self, crop: str, is_organic: bool) -> List[Dict]:
        """Get recommended market channels."""
        channels = [
            {
                "channel_th": "พ่อค้าคนกลาง/โรงสี",
                "price_level_th": "ราคาต่ำสุด",
                "pros_th": "สะดวก รับซื้อปริมาณมาก",
                "cons_th": "ราคาต่ำ",
                "recommended": True
            },
            {
                "channel_th": "สหกรณ์การเกษตร",
                "price_level_th": "ราคาปานกลาง",
                "pros_th": "ราคายุติธรรม มีสวัสดิการ",
                "cons_th": "ต้องเป็นสมาชิก",
                "recommended": True
            },
            {
                "channel_th": "ตลาดเกษตรกร/ตลาดนัด",
                "price_level_th": "ราคาสูง",
                "pros_th": "ราคาดี ขายตรงผู้บริโภค",
                "cons_th": "ต้องขนส่งเอง ปริมาณจำกัด",
                "recommended": False
            }
        ]

        if is_organic:
            channels.append({
                "channel_th": "ตลาดออร์แกนิก/ออนไลน์",
                "price_level_th": "ราคาสูงมาก",
                "pros_th": "ราคาพรีเมียม ตลาดโต",
                "cons_th": "ต้องมีใบรับรอง",
                "recommended": True
            })

        return channels

    def _assess_market_risks(self, crop: str, profit: Dict) -> List[Dict]:
        """Assess market-related risks."""
        risks = []

        # Price volatility
        risks.append({
            "risk_th": "ความผันผวนของราคา",
            "severity_th": "ปานกลาง",
            "mitigation_th": "ทำสัญญาซื้อขายล่วงหน้า หรือขายผ่านสหกรณ์"
        })

        # Low profit margin
        if profit["roi_percent"] < 20:
            risks.append({
                "risk_th": "กำไรต่ำ",
                "severity_th": "สูง",
                "mitigation_th": "ลดต้นทุน เพิ่มผลผลิต หาตลาดราคาดี"
            })

        # Market access
        risks.append({
            "risk_th": "การเข้าถึงตลาด",
            "severity_th": "ต่ำ",
            "mitigation_th": "รวมกลุ่มเกษตรกร ใช้ช่องทางออนไลน์"
        })

        return risks

    def _generate_recommendations(self, profit: Dict, market: Dict) -> List[str]:
        """Generate market recommendations in Thai."""
        recs = []

        if profit["is_profitable"]:
            if profit["roi_percent"] >= 50:
                recs.append("ผลตอบแทนดีมาก พิจารณาขยายพื้นที่ปลูก")
            elif profit["roi_percent"] >= 20:
                recs.append("ผลตอบแทนอยู่ในเกณฑ์ดี รักษาคุณภาพผลผลิต")
            else:
                recs.append("ผลตอบแทนต่ำ ควรหาทางลดต้นทุนหรือเพิ่มราคาขาย")
        else:
            recs.append("คาดว่าจะขาดทุน ควรทบทวนแผนการผลิต")

        recs.append("เปรียบเทียบราคาหลายตลาดก่อนขาย")
        recs.append("พิจารณาแปรรูปเพิ่มมูลค่าถ้าเป็นไปได้")

        if market.get("is_organic"):
            recs.append("ใช้ประโยชน์จากราคาพรีเมียมสินค้าอินทรีย์")

        return recs
