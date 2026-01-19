"""
S.O.I.L.E.R. Market Analyst Agent
Tracks fertilizer prices, calculates ROI, and provides economic analysis.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from agents.base_agent import BaseAgent
from data.knowledge_base import FERTILIZERS, CROP_REQUIREMENTS


class MarketAgent(BaseAgent):
    """
    Market Analyst Agent - Provides economic analysis and ROI calculations.

    Responsibilities:
    - Track current fertilizer prices
    - Calculate return on investment (ROI)
    - Analyze cost-benefit of recommendations
    - Provide budget optimization suggestions
    - Compare organic vs conventional economics
    """

    # Market data (simulated - in production, would connect to real data sources)
    CROP_PRICES_THB_PER_KG = {
        "Riceberry Rice": 45.0,  # Premium rice variety
        "Corn": 8.5,  # Field corn
        "Jasmine Rice": 18.0,
        "Cassava": 2.5,
    }

    # Price volatility factors
    PRICE_VOLATILITY = {
        "Riceberry Rice": 0.15,  # 15% price variation
        "Corn": 0.20,
        "Jasmine Rice": 0.10,
        "Cassava": 0.25,
    }

    def __init__(self, verbose: bool = True):
        super().__init__(agent_name="MarketAnalyst", verbose=verbose)

    def _execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute market analysis and ROI calculation.

        Args:
            input_data: Dictionary containing:
                - target_crop: str
                - field_size_rai: float
                - fertilizer_plan: dict (from FertilizerAgent)
                - crop_analysis: dict (from CropAgent)
                - budget_thb: float (optional)

        Returns:
            Market analysis and ROI calculations
        """
        self.think("Analyzing market conditions and calculating ROI...")

        target_crop = input_data.get("target_crop", "Riceberry Rice")
        field_size_rai = input_data.get("field_size_rai", 1.0)
        fertilizer_plan = input_data.get("fertilizer_plan", {})
        crop_analysis = input_data.get("crop_analysis", {})
        budget_thb = input_data.get("budget_thb")

        # Step 1: Get current fertilizer prices
        self.think("Fetching current fertilizer prices...")
        price_analysis = self._analyze_fertilizer_prices(fertilizer_plan)
        self.log_result(f"Total input cost: {price_analysis['total_cost_thb']:,.2f} THB")

        # Step 2: Estimate crop revenue
        self.think("Calculating expected crop revenue...")
        revenue_analysis = self._calculate_revenue(
            target_crop, crop_analysis, field_size_rai
        )
        self.log_result(f"Expected revenue: {revenue_analysis['expected_revenue_thb']:,.2f} THB")

        # Step 3: Calculate ROI
        self.think("Computing return on investment...")
        roi_analysis = self._calculate_roi(
            price_analysis, revenue_analysis, field_size_rai
        )
        self.log_result(f"ROI: {roi_analysis['roi_percent']:.1f}%")

        # Step 4: Break-even analysis
        self.think("Performing break-even analysis...")
        breakeven = self._calculate_breakeven(
            price_analysis, target_crop, field_size_rai
        )
        self.log_result(f"Break-even yield: {breakeven['breakeven_yield_kg_per_rai']:.1f} kg/rai")

        # Step 5: Budget analysis
        budget_status = None
        if budget_thb:
            self.think(f"Checking against budget of {budget_thb:,.2f} THB...")
            budget_status = self._analyze_budget(price_analysis, budget_thb)
            if budget_status["within_budget"]:
                self.log_result("Recommendation is within budget")
            else:
                self.log_warning(f"Over budget by {budget_status['overage_thb']:,.2f} THB")

        # Step 6: Cost optimization suggestions
        self.think("Generating cost optimization suggestions...")
        optimizations = self._generate_optimizations(
            fertilizer_plan, price_analysis, budget_thb
        )

        # Step 7: Risk analysis
        self.think("Assessing market and production risks...")
        risk_analysis = self._analyze_risks(target_crop, roi_analysis)

        # Step 8: Compare with organic alternatives
        self.think("Comparing conventional vs organic economics...")
        organic_comparison = self._compare_organic_economics(
            fertilizer_plan, target_crop, field_size_rai
        )

        # Build result
        result = {
            "analysis_date": datetime.now().isoformat(),
            "target_crop": target_crop,
            "field_size_rai": field_size_rai,

            # Price Analysis
            "fertilizer_costs": price_analysis,

            # Revenue Projections
            "revenue_projections": revenue_analysis,

            # ROI Analysis
            "roi_analysis": roi_analysis,

            # Break-even
            "breakeven_analysis": breakeven,

            # Budget
            "budget_analysis": budget_status,

            # Optimizations
            "cost_optimizations": optimizations,

            # Risk Assessment
            "risk_analysis": risk_analysis,

            # Organic Comparison
            "organic_comparison": organic_comparison,

            # Summary metrics
            "summary_metrics": {
                "total_investment_thb": price_analysis["total_cost_thb"],
                "expected_revenue_thb": revenue_analysis["expected_revenue_thb"],
                "expected_profit_thb": roi_analysis["expected_profit_thb"],
                "roi_percent": roi_analysis["roi_percent"],
                "cost_per_rai_thb": price_analysis["cost_per_rai_thb"],
                "profit_per_rai_thb": roi_analysis["profit_per_rai_thb"]
            },

            # Observation for next agent
            "observation": self._generate_observation(
                roi_analysis, breakeven, risk_analysis
            )
        }

        return result

    def _analyze_fertilizer_prices(
        self,
        fertilizer_plan: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Analyze fertilizer prices and total costs."""
        applications = fertilizer_plan.get("applications", [])
        cost_breakdown = fertilizer_plan.get("cost_breakdown", [])

        total_cost = fertilizer_plan.get("total_estimated_cost_thb", 0)
        cost_per_rai = fertilizer_plan.get("cost_per_rai_thb", 0)

        # Get current prices from knowledge base
        current_prices = []
        for fert in FERTILIZERS:
            current_prices.append({
                "name": fert["name"],
                "formula": fert["formula"],
                "price_per_kg": fert["price_thb_per_kg"],
                "price_per_50kg": fert["price_thb_per_50kg_bag"]
            })

        # Price trend (simulated)
        price_trend = "stable"  # Could be: rising, falling, stable, volatile

        return {
            "applications": applications,
            "cost_breakdown": cost_breakdown,
            "total_cost_thb": total_cost,
            "cost_per_rai_thb": cost_per_rai,
            "current_prices": current_prices,
            "price_trend": price_trend,
            "price_index": 1.0,  # 1.0 = baseline, >1 = above average
            "best_purchase_timing": "Buy before planting season for best prices"
        }

    def _calculate_revenue(
        self,
        target_crop: str,
        crop_analysis: Dict[str, Any],
        field_size_rai: float
    ) -> Dict[str, Any]:
        """Calculate expected revenue from crop sales."""
        # Get yield targets
        yield_targets = crop_analysis.get("yield_targets", {})
        target_yield = yield_targets.get("target_kg_per_rai", 450)
        yield_range = yield_targets.get("yield_range", {
            "low": target_yield * 0.7,
            "expected": target_yield,
            "high": target_yield * 1.2
        })

        # Get crop price
        crop_price = self.CROP_PRICES_THB_PER_KG.get(target_crop, 15.0)
        volatility = self.PRICE_VOLATILITY.get(target_crop, 0.15)

        # Calculate revenue scenarios
        expected_yield_total = target_yield * field_size_rai
        expected_revenue = expected_yield_total * crop_price

        low_revenue = yield_range["low"] * field_size_rai * crop_price * (1 - volatility)
        high_revenue = yield_range["high"] * field_size_rai * crop_price * (1 + volatility)

        return {
            "crop_price_thb_per_kg": crop_price,
            "price_volatility": volatility,
            "expected_yield_kg_per_rai": target_yield,
            "total_expected_yield_kg": expected_yield_total,
            "revenue_scenarios": {
                "pessimistic": round(low_revenue, 2),
                "expected": round(expected_revenue, 2),
                "optimistic": round(high_revenue, 2)
            },
            "expected_revenue_thb": round(expected_revenue, 2),
            "revenue_per_rai_thb": round(expected_revenue / field_size_rai, 2)
        }

    def _calculate_roi(
        self,
        price_analysis: Dict[str, Any],
        revenue_analysis: Dict[str, Any],
        field_size_rai: float
    ) -> Dict[str, Any]:
        """Calculate return on investment."""
        total_cost = price_analysis["total_cost_thb"]
        expected_revenue = revenue_analysis["expected_revenue_thb"]

        # Add other costs (estimated)
        other_costs = {
            "seed_cost": 500 * field_size_rai,
            "labor_cost": 2000 * field_size_rai,
            "pesticide_cost": 300 * field_size_rai,
            "machinery_cost": 800 * field_size_rai,
            "miscellaneous": 400 * field_size_rai
        }
        total_other_costs = sum(other_costs.values())

        total_investment = total_cost + total_other_costs
        expected_profit = expected_revenue - total_investment

        # ROI calculation
        roi_percent = (expected_profit / total_investment) * 100 if total_investment > 0 else 0

        # Profit per rai
        profit_per_rai = expected_profit / field_size_rai if field_size_rai > 0 else 0

        return {
            "fertilizer_cost_thb": total_cost,
            "other_costs_thb": total_other_costs,
            "other_costs_breakdown": other_costs,
            "total_investment_thb": round(total_investment, 2),
            "expected_revenue_thb": round(expected_revenue, 2),
            "expected_profit_thb": round(expected_profit, 2),
            "roi_percent": round(roi_percent, 1),
            "profit_per_rai_thb": round(profit_per_rai, 2),
            "investment_per_rai_thb": round(total_investment / field_size_rai, 2),
            "profitability_rating": self._rate_profitability(roi_percent)
        }

    def _rate_profitability(self, roi_percent: float) -> str:
        """Rate the profitability of the investment."""
        if roi_percent >= 100:
            return "excellent"
        elif roi_percent >= 50:
            return "good"
        elif roi_percent >= 25:
            return "moderate"
        elif roi_percent >= 0:
            return "marginal"
        else:
            return "loss"

    def _calculate_breakeven(
        self,
        price_analysis: Dict[str, Any],
        target_crop: str,
        field_size_rai: float
    ) -> Dict[str, Any]:
        """Calculate break-even point."""
        total_cost = price_analysis["total_cost_thb"]
        crop_price = self.CROP_PRICES_THB_PER_KG.get(target_crop, 15.0)

        # Break-even yield (fertilizer cost only)
        breakeven_yield_fert = total_cost / crop_price if crop_price > 0 else 0
        breakeven_yield_per_rai = breakeven_yield_fert / field_size_rai if field_size_rai > 0 else 0

        # Typical yields from knowledge base
        crop_data = CROP_REQUIREMENTS.get(target_crop, {})
        typical_yield = crop_data.get("yield_potential_kg_per_rai", {}).get("average", 450)

        # Margin of safety
        margin_of_safety = ((typical_yield - breakeven_yield_per_rai) / typical_yield) * 100 if typical_yield > 0 else 0

        return {
            "breakeven_yield_kg": round(breakeven_yield_fert, 1),
            "breakeven_yield_kg_per_rai": round(breakeven_yield_per_rai, 1),
            "typical_yield_kg_per_rai": typical_yield,
            "margin_of_safety_percent": round(margin_of_safety, 1),
            "breakeven_achievable": breakeven_yield_per_rai < typical_yield,
            "interpretation": self._interpret_breakeven(margin_of_safety)
        }

    def _interpret_breakeven(self, margin_of_safety: float) -> str:
        """Interpret the break-even analysis."""
        if margin_of_safety >= 50:
            return "Highly favorable - large margin for yield variability"
        elif margin_of_safety >= 30:
            return "Favorable - good buffer against yield losses"
        elif margin_of_safety >= 15:
            return "Acceptable - moderate risk if yields are low"
        elif margin_of_safety >= 0:
            return "Marginal - little room for yield losses"
        else:
            return "Unfavorable - expected yield below break-even point"

    def _analyze_budget(
        self,
        price_analysis: Dict[str, Any],
        budget_thb: float
    ) -> Dict[str, Any]:
        """Analyze against budget constraints."""
        total_cost = price_analysis["total_cost_thb"]
        within_budget = total_cost <= budget_thb
        variance = budget_thb - total_cost

        return {
            "budget_thb": budget_thb,
            "actual_cost_thb": total_cost,
            "within_budget": within_budget,
            "variance_thb": round(variance, 2),
            "overage_thb": round(-variance, 2) if variance < 0 else 0,
            "budget_utilization_percent": round((total_cost / budget_thb) * 100, 1) if budget_thb > 0 else 0,
            "recommendation": "Proceed as planned" if within_budget else "Consider cost optimizations below"
        }

    def _generate_optimizations(
        self,
        fertilizer_plan: Dict[str, Any],
        price_analysis: Dict[str, Any],
        budget_thb: Optional[float]
    ) -> List[Dict[str, Any]]:
        """Generate cost optimization suggestions."""
        optimizations = []

        total_cost = price_analysis["total_cost_thb"]

        # Bulk purchase discount
        optimizations.append({
            "strategy": "Bulk purchasing",
            "description": "Buy fertilizers in bulk (50kg bags) for 5-10% savings",
            "potential_savings_percent": 7.5,
            "potential_savings_thb": round(total_cost * 0.075, 2)
        })

        # Off-season purchasing
        optimizations.append({
            "strategy": "Off-season purchasing",
            "description": "Purchase fertilizers 1-2 months before planting season",
            "potential_savings_percent": 10,
            "potential_savings_thb": round(total_cost * 0.10, 2)
        })

        # Group purchasing
        optimizations.append({
            "strategy": "Cooperative purchasing",
            "description": "Join farmer groups for collective bargaining",
            "potential_savings_percent": 12,
            "potential_savings_thb": round(total_cost * 0.12, 2)
        })

        # Organic alternatives
        optimizations.append({
            "strategy": "Partial organic substitution",
            "description": "Replace 30% of chemical fertilizers with organic options",
            "potential_savings_percent": 15,
            "potential_savings_thb": round(total_cost * 0.15, 2),
            "note": "May require larger quantities; improves long-term soil health"
        })

        # Government subsidies
        optimizations.append({
            "strategy": "Government subsidies",
            "description": "Check eligibility for agricultural input subsidies",
            "potential_savings_percent": 20,
            "potential_savings_thb": round(total_cost * 0.20, 2),
            "note": "Subject to program availability and eligibility"
        })

        return optimizations

    def _analyze_risks(
        self,
        target_crop: str,
        roi_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Analyze market and production risks."""
        roi = roi_analysis["roi_percent"]
        volatility = self.PRICE_VOLATILITY.get(target_crop, 0.15)

        risks = []

        # Price risk
        if volatility > 0.2:
            risks.append({
                "risk": "High price volatility",
                "severity": "high",
                "mitigation": "Consider forward contracts or cooperative marketing"
            })
        elif volatility > 0.1:
            risks.append({
                "risk": "Moderate price volatility",
                "severity": "medium",
                "mitigation": "Monitor market prices; diversify sales channels"
            })

        # ROI risk
        if roi < 25:
            risks.append({
                "risk": "Low profit margin",
                "severity": "high",
                "mitigation": "Optimize costs; improve yields through better management"
            })

        # Weather/production risk
        risks.append({
            "risk": "Weather-related yield loss",
            "severity": "medium",
            "mitigation": "Crop insurance; irrigation; resilient varieties"
        })

        # Input cost risk
        risks.append({
            "risk": "Fertilizer price increases",
            "severity": "medium",
            "mitigation": "Buy early; consider organic alternatives; bulk purchase"
        })

        # Overall risk rating
        high_risks = len([r for r in risks if r["severity"] == "high"])
        if high_risks >= 2:
            overall_risk = "high"
        elif high_risks == 1:
            overall_risk = "moderate"
        else:
            overall_risk = "low"

        return {
            "overall_risk_level": overall_risk,
            "identified_risks": risks,
            "risk_adjusted_roi": round(roi * (1 - volatility), 1),
            "recommendation": "Proceed with caution" if overall_risk == "high" else "Acceptable risk level"
        }

    def _compare_organic_economics(
        self,
        fertilizer_plan: Dict[str, Any],
        target_crop: str,
        field_size_rai: float
    ) -> Dict[str, Any]:
        """Compare organic vs conventional economics."""
        conventional_cost = fertilizer_plan.get("total_estimated_cost_thb", 0)

        # Organic cost estimation (typically lower input cost but higher labor)
        organic_input_cost = conventional_cost * 0.6  # 40% less on inputs
        organic_labor_cost = 1500 * field_size_rai  # Higher labor for organic
        organic_total = organic_input_cost + organic_labor_cost

        # Organic premium (Riceberry already premium, add another 20% for organic)
        organic_price_premium = 1.2

        crop_price = self.CROP_PRICES_THB_PER_KG.get(target_crop, 15.0)
        organic_price = crop_price * organic_price_premium

        return {
            "conventional": {
                "input_cost_thb": conventional_cost,
                "crop_price_thb_per_kg": crop_price
            },
            "organic": {
                "input_cost_thb": round(organic_input_cost, 2),
                "additional_labor_cost_thb": organic_labor_cost,
                "total_cost_thb": round(organic_total, 2),
                "crop_price_thb_per_kg": organic_price,
                "price_premium_percent": 20
            },
            "comparison": {
                "cost_difference_thb": round(organic_total - conventional_cost, 2),
                "break_even_premium_needed": round(((organic_total / conventional_cost) - 1) * 100, 1),
                "recommendation": "Organic viable if premium market access available"
            },
            "transition_notes": [
                "Organic certification requires 2-3 year transition period",
                "Build organic matter through cover crops and compost",
                "Establish buyer relationships before transitioning"
            ]
        }

    def _generate_observation(
        self,
        roi_analysis: Dict[str, Any],
        breakeven: Dict[str, Any],
        risk_analysis: Dict[str, Any]
    ) -> str:
        """Generate observation summary for next agent."""
        return (
            f"MarketAnalyst Assessment: ROI of {roi_analysis['roi_percent']:.1f}% "
            f"({roi_analysis['profitability_rating']}). "
            f"Break-even at {breakeven['breakeven_yield_kg_per_rai']:.0f} kg/rai "
            f"with {breakeven['margin_of_safety_percent']:.0f}% safety margin. "
            f"Overall risk level: {risk_analysis['overall_risk_level']}. "
            f"Expected profit: {roi_analysis['expected_profit_thb']:,.0f} THB."
        )
