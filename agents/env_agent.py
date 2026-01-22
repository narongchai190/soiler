"""
S.O.I.L.E.R. Environment Agent
Analyzes weather patterns, climate suitability, and environmental factors.

Enhanced with real-time weather forecast capability (OpenWeatherMap ready).
"""

from datetime import datetime, timedelta
from typing import Any, Dict, List
import random
import os

from agents.base_agent import BaseAgent


# OpenWeatherMap API Configuration (for future use)
OPENWEATHERMAP_API_KEY = os.environ.get("OPENWEATHERMAP_API_KEY", None)
OPENWEATHERMAP_BASE_URL = "https://api.openweathermap.org/data/2.5"


class EnvironmentAgent(BaseAgent):
    """
    Environment Agent - Assesses environmental conditions and climate suitability.

    Responsibilities:
    - Analyze weather patterns for the location
    - Assess climate suitability for target crop
    - Identify environmental risks (drought, flood, etc.)
    - Provide seasonal planting recommendations
    - Calculate growing degree days and thermal suitability
    """

    # Climate data for Phrae Province (Northern Thailand)
    # Monthly averages (simulated historical data)
    PHRAE_CLIMATE = {
        1: {"temp_min": 14, "temp_max": 31, "rainfall_mm": 5, "humidity": 65, "season": "cool_dry"},
        2: {"temp_min": 16, "temp_max": 34, "rainfall_mm": 8, "humidity": 60, "season": "hot_dry"},
        3: {"temp_min": 20, "temp_max": 36, "rainfall_mm": 25, "humidity": 55, "season": "hot_dry"},
        4: {"temp_min": 23, "temp_max": 37, "rainfall_mm": 65, "humidity": 60, "season": "hot_dry"},
        5: {"temp_min": 24, "temp_max": 35, "rainfall_mm": 180, "humidity": 75, "season": "rainy"},
        6: {"temp_min": 24, "temp_max": 33, "rainfall_mm": 150, "humidity": 80, "season": "rainy"},
        7: {"temp_min": 24, "temp_max": 32, "rainfall_mm": 200, "humidity": 85, "season": "rainy"},
        8: {"temp_min": 24, "temp_max": 32, "rainfall_mm": 250, "humidity": 85, "season": "rainy"},
        9: {"temp_min": 23, "temp_max": 32, "rainfall_mm": 220, "humidity": 85, "season": "rainy"},
        10: {"temp_min": 22, "temp_max": 32, "rainfall_mm": 100, "humidity": 78, "season": "rainy"},
        11: {"temp_min": 18, "temp_max": 31, "rainfall_mm": 30, "humidity": 70, "season": "cool_dry"},
        12: {"temp_min": 15, "temp_max": 30, "rainfall_mm": 10, "humidity": 68, "season": "cool_dry"},
    }

    # Crop climate requirements
    CROP_CLIMATE_NEEDS = {
        "Riceberry Rice": {
            "temp_min": 20,
            "temp_max": 35,
            "optimal_temp": 28,
            "min_rainfall_mm": 1000,
            "growing_season": "rainy",
            "flood_tolerant": True,
            "drought_tolerant": False,
        },
        "Corn": {
            "temp_min": 18,
            "temp_max": 35,
            "optimal_temp": 25,
            "min_rainfall_mm": 400,
            "growing_season": "late_rainy",
            "flood_tolerant": False,
            "drought_tolerant": True,
        },
    }

    def __init__(self, verbose: bool = True):
        super().__init__(agent_name="EnvironmentExpert", verbose=verbose)

    def _execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute environmental analysis.

        Args:
            input_data: Dictionary containing:
                - location: str
                - target_crop: str
                - planting_date: str (optional, ISO format)
                - crop_analysis: dict (from CropAgent)

        Returns:
            Environmental analysis and recommendations
        """
        self.think("Analyzing environmental conditions...")

        location = input_data.get("location", "Phrae Province")
        target_crop = input_data.get("target_crop", "Riceberry Rice")
        planting_date_str = input_data.get("planting_date")
        crop_analysis = input_data.get("crop_analysis", {})

        # Parse planting date
        if planting_date_str:
            planting_date = datetime.fromisoformat(planting_date_str)
        else:
            planting_date = datetime.now() + timedelta(days=14)

        growth_cycle = crop_analysis.get("growth_cycle_days", 120)

        # Step 1: Get climate data for location
        self.think(f"Retrieving climate data for {location}...")
        climate_data = self._get_climate_data(location, planting_date, growth_cycle)
        self.log_result(f"Growing season rainfall: {climate_data['total_rainfall_mm']:.0f} mm")

        # Step 2: Assess climate suitability
        self.think(f"Assessing climate suitability for {target_crop}...")
        suitability = self._assess_climate_suitability(
            target_crop, climate_data, planting_date
        )
        self.log_result(f"Climate suitability: {suitability['rating']}")

        # Step 3: Identify weather risks
        self.think("Identifying weather-related risks...")
        weather_risks = self._identify_weather_risks(
            target_crop, climate_data, planting_date
        )
        for risk in weather_risks:
            if risk["severity"] == "high":
                self.log_warning(f"High risk: {risk['risk']}")
            else:
                self.log_action(f"Risk noted: {risk['risk']}")

        # Step 4: Calculate growing degree days
        self.think("Calculating thermal accumulation...")
        gdd_analysis = self._calculate_growing_degree_days(
            climate_data, target_crop
        )
        self.log_result(f"Expected GDD: {gdd_analysis['total_gdd']:.0f}")

        # Step 5: Optimal planting window
        self.think("Determining optimal planting window...")
        planting_window = self._determine_planting_window(
            target_crop, location
        )
        self.log_result(f"Optimal planting: {planting_window['optimal_months']}")

        # Step 6: Generate weather-based recommendations
        self.think("Generating environment-based recommendations...")
        env_recommendations = self._generate_recommendations(
            target_crop, climate_data, weather_risks, planting_date
        )

        # Step 7: Seasonal forecast
        self.think("Generating seasonal outlook...")
        seasonal_forecast = self._generate_seasonal_forecast(planting_date)

        # Build result
        result = {
            "location": location,
            "analysis_date": datetime.now().isoformat(),
            "target_crop": target_crop,

            # Planting timing
            "planting_date": planting_date.isoformat(),
            "harvest_date": (planting_date + timedelta(days=growth_cycle)).isoformat(),
            "growth_period_days": growth_cycle,

            # Climate data
            "climate_data": climate_data,

            # Suitability assessment
            "climate_suitability": suitability,

            # Weather risks
            "weather_risks": weather_risks,
            "risk_summary": {
                "high_risks": len([r for r in weather_risks if r["severity"] == "high"]),
                "medium_risks": len([r for r in weather_risks if r["severity"] == "medium"]),
                "low_risks": len([r for r in weather_risks if r["severity"] == "low"])
            },

            # Thermal analysis
            "growing_degree_days": gdd_analysis,

            # Planting window
            "planting_window": planting_window,

            # Seasonal forecast
            "seasonal_forecast": seasonal_forecast,

            # Recommendations
            "recommendations": env_recommendations,

            # Observation for next agent
            "observation": self._generate_observation(
                suitability, weather_risks, planting_window
            )
        }

        return result

    def _get_climate_data(
        self,
        location: str,
        planting_date: datetime,
        growth_cycle: int
    ) -> Dict[str, Any]:
        """Get climate data for the growing period."""
        start_month = planting_date.month

        # Collect monthly data for growing period
        monthly_data = []
        total_rainfall = 0
        temp_mins = []
        temp_maxs = []

        current_month = start_month
        months_covered = 0
        max_months = (growth_cycle // 30) + 2

        while months_covered < max_months:
            month_data = self.PHRAE_CLIMATE.get(current_month, self.PHRAE_CLIMATE[1])
            monthly_data.append({
                "month": current_month,
                "month_name": datetime(2024, current_month, 1).strftime("%B"),
                **month_data
            })
            total_rainfall += month_data["rainfall_mm"]
            temp_mins.append(month_data["temp_min"])
            temp_maxs.append(month_data["temp_max"])

            current_month = (current_month % 12) + 1
            months_covered += 1

        avg_temp_min = sum(temp_mins) / len(temp_mins)
        avg_temp_max = sum(temp_maxs) / len(temp_maxs)

        return {
            "location": location,
            "region": "Northern Thailand",
            "climate_zone": "Tropical savanna (Aw)",
            "monthly_data": monthly_data,
            "total_rainfall_mm": total_rainfall,
            "avg_temp_min_c": round(avg_temp_min, 1),
            "avg_temp_max_c": round(avg_temp_max, 1),
            "avg_temp_c": round((avg_temp_min + avg_temp_max) / 2, 1),
            "growing_season": self._determine_season(start_month)
        }

    def _determine_season(self, month: int) -> str:
        """Determine the season for a given month."""
        if month in [11, 12, 1, 2]:
            return "cool_dry"
        elif month in [3, 4]:
            return "hot_dry"
        else:
            return "rainy"

    def _assess_climate_suitability(
        self,
        target_crop: str,
        climate_data: Dict[str, Any],
        planting_date: datetime
    ) -> Dict[str, Any]:
        """Assess climate suitability for the target crop."""
        crop_needs = self.CROP_CLIMATE_NEEDS.get(target_crop, {
            "temp_min": 20, "temp_max": 35, "optimal_temp": 28,
            "min_rainfall_mm": 500, "growing_season": "rainy"
        })

        score = 0
        max_score = 100
        factors = []

        # Temperature suitability (40 points)
        avg_temp = climate_data["avg_temp_c"]
        if crop_needs["temp_min"] <= avg_temp <= crop_needs["temp_max"]:
            temp_score = 40
            factors.append({"factor": "Temperature", "status": "suitable", "score": 40})
        else:
            temp_diff = min(
                abs(avg_temp - crop_needs["temp_min"]),
                abs(avg_temp - crop_needs["temp_max"])
            )
            temp_score = max(0, 40 - (temp_diff * 5))
            factors.append({"factor": "Temperature", "status": "marginal", "score": temp_score})
        score += temp_score

        # Rainfall suitability (35 points)
        total_rain = climate_data["total_rainfall_mm"]
        min_rain = crop_needs["min_rainfall_mm"]

        if total_rain >= min_rain:
            rain_score = 35
            factors.append({"factor": "Rainfall", "status": "adequate", "score": 35})
        elif total_rain >= min_rain * 0.7:
            rain_score = 25
            factors.append({"factor": "Rainfall", "status": "marginal - irrigation recommended", "score": 25})
        else:
            rain_score = 10
            factors.append({"factor": "Rainfall", "status": "insufficient - irrigation required", "score": 10})
        score += rain_score

        # Season suitability (25 points)
        current_season = climate_data["growing_season"]
        preferred_season = crop_needs["growing_season"]

        if current_season == preferred_season or preferred_season in current_season:
            season_score = 25
            factors.append({"factor": "Season", "status": "optimal", "score": 25})
        elif current_season == "rainy":
            season_score = 20
            factors.append({"factor": "Season", "status": "acceptable", "score": 20})
        else:
            season_score = 10
            factors.append({"factor": "Season", "status": "suboptimal", "score": 10})
        score += season_score

        # Rating
        if score >= 85:
            rating = "excellent"
        elif score >= 70:
            rating = "good"
        elif score >= 55:
            rating = "moderate"
        elif score >= 40:
            rating = "marginal"
        else:
            rating = "poor"

        return {
            "score": score,
            "max_score": max_score,
            "rating": rating,
            "factors": factors,
            "interpretation": f"Climate conditions are {rating} for {target_crop} cultivation"
        }

    def _identify_weather_risks(
        self,
        target_crop: str,
        climate_data: Dict[str, Any],
        planting_date: datetime
    ) -> List[Dict[str, Any]]:
        """Identify weather-related risks."""
        risks = []
        crop_needs = self.CROP_CLIMATE_NEEDS.get(target_crop, {})

        # Drought risk
        total_rain = climate_data["total_rainfall_mm"]
        min_rain = crop_needs.get("min_rainfall_mm", 500)

        if total_rain < min_rain * 0.5:
            risks.append({
                "risk": "Severe drought risk",
                "severity": "high",
                "probability": "high",
                "impact": "Major yield loss possible",
                "mitigation": [
                    "Ensure irrigation access",
                    "Consider drought-tolerant varieties",
                    "Mulching to conserve moisture"
                ]
            })
        elif total_rain < min_rain:
            risks.append({
                "risk": "Moderate drought risk",
                "severity": "medium",
                "probability": "medium",
                "impact": "Yield reduction possible",
                "mitigation": [
                    "Supplemental irrigation during dry spells",
                    "Monitor soil moisture regularly"
                ]
            })

        # Flood risk (for rainy season)
        monthly_data = climate_data.get("monthly_data", [])
        high_rain_months = [m for m in monthly_data if m.get("rainfall_mm", 0) > 200]

        if high_rain_months and not crop_needs.get("flood_tolerant", False):
            risks.append({
                "risk": "Flood/waterlogging risk",
                "severity": "high" if len(high_rain_months) > 2 else "medium",
                "probability": "medium",
                "impact": "Root damage and yield loss in non-tolerant crops",
                "mitigation": [
                    "Ensure proper field drainage",
                    "Raise beds for susceptible crops",
                    "Monitor weather forecasts"
                ]
            })

        # Heat stress
        avg_max = climate_data["avg_temp_max_c"]
        if avg_max > crop_needs.get("temp_max", 35):
            risks.append({
                "risk": "Heat stress risk",
                "severity": "medium",
                "probability": "high",
                "impact": "Reduced pollination and grain filling",
                "mitigation": [
                    "Adequate irrigation to cool crops",
                    "Consider shade nets for sensitive stages",
                    "Adjust planting date if possible"
                ]
            })

        # Cold damage (for cool season)
        avg_min = climate_data["avg_temp_min_c"]
        if avg_min < crop_needs.get("temp_min", 15):
            risks.append({
                "risk": "Cold damage risk",
                "severity": "medium",
                "probability": "low",
                "impact": "Stunted growth in cool months",
                "mitigation": [
                    "Avoid planting in coldest months",
                    "Use row covers if temperatures drop"
                ]
            })

        # Storm/wind risk
        risks.append({
            "risk": "Storm damage",
            "severity": "low",
            "probability": "low",
            "impact": "Lodging and physical damage",
            "mitigation": [
                "Avoid excessive nitrogen (causes weak stems)",
                "Consider lodging-resistant varieties"
            ]
        })

        return risks

    def _calculate_growing_degree_days(
        self,
        climate_data: Dict[str, Any],
        target_crop: str
    ) -> Dict[str, Any]:
        """Calculate growing degree days for the crop."""
        # Base temperature varies by crop
        base_temps = {
            "Riceberry Rice": 10,
            "Corn": 10,
        }
        base_temp = base_temps.get(target_crop, 10)

        # Calculate GDD from monthly data
        monthly_data = climate_data.get("monthly_data", [])
        total_gdd = 0

        for month in monthly_data:
            avg_temp = (month["temp_min"] + month["temp_max"]) / 2
            daily_gdd = max(0, avg_temp - base_temp)
            monthly_gdd = daily_gdd * 30  # Approximate days per month
            total_gdd += monthly_gdd

        # Typical GDD requirements
        gdd_requirements = {
            "Riceberry Rice": 2500,
            "Corn": 2700,
        }
        required_gdd = gdd_requirements.get(target_crop, 2500)

        adequacy = (total_gdd / required_gdd) * 100 if required_gdd > 0 else 0

        return {
            "base_temperature_c": base_temp,
            "total_gdd": round(total_gdd, 0),
            "required_gdd": required_gdd,
            "gdd_adequacy_percent": round(adequacy, 1),
            "interpretation": "Adequate thermal units" if adequacy >= 100 else "May need extended growing period"
        }

    def _determine_planting_window(
        self,
        target_crop: str,
        location: str
    ) -> Dict[str, Any]:
        """Determine optimal planting window."""
        # Planting windows for Phrae Province
        windows = {
            "Riceberry Rice": {
                "optimal_months": "May - July",
                "acceptable_months": "April - August",
                "harvest_months": "September - November",
                "notes": "Plant at start of rainy season for best results"
            },
            "Corn": {
                "optimal_months": "June - July",
                "acceptable_months": "May - August",
                "harvest_months": "September - November",
                "notes": "Late rainy season planting avoids waterlogging"
            }
        }

        window = windows.get(target_crop, {
            "optimal_months": "May - July",
            "acceptable_months": "April - August",
            "harvest_months": "October - December",
            "notes": "Adjust based on specific crop requirements"
        })

        current_month = datetime.now().month
        optimal_start = 5  # May
        optimal_end = 7  # July

        if optimal_start <= current_month <= optimal_end:
            timing_status = "Currently in optimal planting window"
        elif current_month < optimal_start:
            days_until = (datetime(datetime.now().year, optimal_start, 1) - datetime.now()).days
            timing_status = f"Optimal window starts in ~{days_until} days"
        else:
            timing_status = "Past optimal window - consider adjusting plans"

        return {
            **window,
            "timing_status": timing_status,
            "current_month": datetime.now().strftime("%B")
        }

    def _generate_seasonal_forecast(
        self,
        planting_date: datetime
    ) -> Dict[str, Any]:
        """Generate seasonal weather forecast."""
        # Simplified forecast (in production, would use actual forecast data)
        month = planting_date.month

        if month in [5, 6, 7, 8, 9]:
            outlook = "Normal to above-normal rainfall expected"
            confidence = "moderate"
            recommendation = "Good conditions for rice; ensure drainage for other crops"
        elif month in [11, 12, 1, 2]:
            outlook = "Dry conditions expected with cool nights"
            confidence = "high"
            recommendation = "Irrigation essential; protect from cold if temperatures drop"
        else:
            outlook = "Transitional period with variable conditions"
            confidence = "low"
            recommendation = "Monitor forecasts closely; be prepared for both wet and dry spells"

        return {
            "forecast_period": f"{planting_date.strftime('%B %Y')} - {(planting_date + timedelta(days=120)).strftime('%B %Y')}",
            "outlook": outlook,
            "confidence": confidence,
            "recommendation": recommendation,
            "data_source": "Historical climate patterns (simulated)",
            "update_frequency": "Check official forecasts monthly"
        }

    def _generate_recommendations(
        self,
        target_crop: str,
        climate_data: Dict[str, Any],
        weather_risks: List[Dict[str, Any]],
        planting_date: datetime
    ) -> List[Dict[str, Any]]:
        """Generate environment-based recommendations."""
        recommendations = []

        # Planting timing
        season = climate_data["growing_season"]
        if season == "rainy":
            recommendations.append({
                "category": "Planting",
                "recommendation": "Good timing - rainy season provides natural irrigation",
                "priority": "info"
            })
        else:
            recommendations.append({
                "category": "Planting",
                "recommendation": "Dry season planting - ensure irrigation is available",
                "priority": "high"
            })

        # Based on risks
        high_risks = [r for r in weather_risks if r["severity"] == "high"]
        for risk in high_risks:
            recommendations.append({
                "category": "Risk mitigation",
                "recommendation": f"Address {risk['risk']}: {risk['mitigation'][0]}",
                "priority": "high"
            })

        # Water management
        total_rain = climate_data["total_rainfall_mm"]
        if total_rain > 1000:
            recommendations.append({
                "category": "Water management",
                "recommendation": "High rainfall expected - ensure field drainage is adequate",
                "priority": "medium"
            })
        elif total_rain < 500:
            recommendations.append({
                "category": "Water management",
                "recommendation": "Low rainfall - plan irrigation schedule now",
                "priority": "high"
            })

        # General
        recommendations.append({
            "category": "Monitoring",
            "recommendation": "Check weather forecasts weekly and adjust management accordingly",
            "priority": "medium"
        })

        return recommendations

    def _generate_observation(
        self,
        suitability: Dict[str, Any],
        weather_risks: List[Dict[str, Any]],
        planting_window: Dict[str, Any]
    ) -> str:
        """Generate observation summary for next agent."""
        high_risks = len([r for r in weather_risks if r["severity"] == "high"])

        return (
            f"EnvironmentExpert Assessment: Climate suitability is {suitability['rating']} "
            f"(score: {suitability['score']}/100). "
            f"Identified {high_risks} high-severity weather risk(s). "
            f"Optimal planting: {planting_window['optimal_months']}. "
            f"{planting_window['timing_status']}."
        )

    # =========================================================================
    # REAL-TIME WEATHER FORECAST (OpenWeatherMap Ready)
    # =========================================================================

    def get_weather_forecast(
        self,
        lat: float,
        lon: float,
        days: int = 5
    ) -> Dict[str, Any]:
        """
        Get weather forecast for a specific location.

        Currently uses mock data, but structured for OpenWeatherMap API integration.

        Args:
            lat: Latitude coordinate
            lon: Longitude coordinate
            days: Number of forecast days (1-7)

        Returns:
            Dictionary containing:
            - humidity_percent (ความชื้นสัมพัทธ์)
            - rain_probability_percent (โอกาสเกิดฝน)
            - avg_temperature_c (อุณหภูมิเฉลี่ย)
            - daily_forecast: List of daily forecasts
            - source: Data source indicator
        """
        self.think(f"Fetching weather forecast for coordinates ({lat}, {lon})...")

        # Check if API key is available for real data
        if OPENWEATHERMAP_API_KEY:
            return self._fetch_real_forecast(lat, lon, days)
        else:
            self.log_action("Using simulated weather data (API key not configured)")
            return self._generate_mock_forecast(lat, lon, days)

    def _fetch_real_forecast(
        self,
        lat: float,
        lon: float,
        days: int
    ) -> Dict[str, Any]:
        """
        Fetch real forecast from OpenWeatherMap API.

        Note: Requires valid API key and requests library.
        """
        # This is the structure for future API integration
        # Uncomment and use when API key is configured

        # import requests
        # url = f"{OPENWEATHERMAP_BASE_URL}/forecast"
        # params = {
        #     "lat": lat,
        #     "lon": lon,
        #     "appid": OPENWEATHERMAP_API_KEY,
        #     "units": "metric",
        #     "cnt": days * 8  # 3-hour intervals
        # }
        # response = requests.get(url, params=params)
        # if response.status_code == 200:
        #     data = response.json()
        #     return self._parse_openweathermap_response(data)

        # Fallback to mock data
        return self._generate_mock_forecast(lat, lon, days)

    def _generate_mock_forecast(
        self,
        lat: float,
        lon: float,
        days: int
    ) -> Dict[str, Any]:
        """
        Generate realistic mock weather forecast based on Phrae climate patterns.

        Uses historical averages with randomized variations.
        """
        current_date = datetime.now()
        current_month = current_date.month

        # Get base climate data for current month
        base_climate = self.PHRAE_CLIMATE.get(current_month, self.PHRAE_CLIMATE[1])

        # Generate daily forecasts
        daily_forecasts = []
        temp_sum = 0
        humidity_sum = 0
        rain_days = 0

        for i in range(min(days, 7)):
            forecast_date = current_date + timedelta(days=i)
            forecast_month = forecast_date.month
            month_climate = self.PHRAE_CLIMATE.get(forecast_month, base_climate)

            # Add realistic variation
            temp_min = month_climate["temp_min"] + random.uniform(-2, 2)
            temp_max = month_climate["temp_max"] + random.uniform(-2, 3)
            avg_temp = (temp_min + temp_max) / 2

            humidity = month_climate["humidity"] + random.uniform(-10, 10)
            humidity = max(40, min(95, humidity))  # Clamp to realistic range

            # Rain probability based on season
            base_rain_mm = month_climate["rainfall_mm"]
            if base_rain_mm > 100:  # Rainy season
                rain_probability = random.uniform(50, 85)
            elif base_rain_mm > 30:  # Transitional
                rain_probability = random.uniform(25, 50)
            else:  # Dry season
                rain_probability = random.uniform(5, 20)

            if rain_probability > 50:
                rain_days += 1

            # Weather condition
            if rain_probability > 70:
                condition = "ฝนตก"
                condition_en = "Rainy"
                icon = "🌧️"
            elif rain_probability > 40:
                condition = "มีเมฆมาก"
                condition_en = "Cloudy"
                icon = "⛅"
            elif rain_probability > 20:
                condition = "เมฆบางส่วน"
                condition_en = "Partly Cloudy"
                icon = "🌤️"
            else:
                condition = "แดดจัด"
                condition_en = "Sunny"
                icon = "☀️"

            daily_forecasts.append({
                "date": forecast_date.strftime("%Y-%m-%d"),
                "day_name": forecast_date.strftime("%A"),
                "day_name_th": self._get_thai_day_name(forecast_date.weekday()),
                "temp_min_c": round(temp_min, 1),
                "temp_max_c": round(temp_max, 1),
                "avg_temp_c": round(avg_temp, 1),
                "humidity_percent": round(humidity, 0),
                "rain_probability_percent": round(rain_probability, 0),
                "condition": condition,
                "condition_en": condition_en,
                "icon": icon,
                "wind_speed_kmh": round(random.uniform(5, 20), 1),
                "wind_direction": random.choice(["N", "NE", "E", "SE", "S", "SW", "W", "NW"])
            })

            temp_sum += avg_temp
            humidity_sum += humidity

        # Calculate averages
        avg_temp = temp_sum / len(daily_forecasts) if daily_forecasts else 0
        avg_humidity = humidity_sum / len(daily_forecasts) if daily_forecasts else 0
        rain_probability = (rain_days / len(daily_forecasts)) * 100 if daily_forecasts else 0

        # Weather summary in Thai
        if rain_probability > 60:
            summary_th = "คาดว่าจะมีฝนตกเป็นส่วนใหญ่ในช่วงนี้ เตรียมรับมือกับสภาพอากาศชื้น"
        elif rain_probability > 30:
            summary_th = "อากาศแปรปรวน มีโอกาสฝนตกบางวัน ควรติดตามพยากรณ์อย่างใกล้ชิด"
        else:
            summary_th = "สภาพอากาศแห้ง แดดจัด ควรเตรียมน้ำให้เพียงพอสำหรับพืช"

        return {
            # Summary values (ค่าสรุป)
            "humidity_percent": round(avg_humidity, 1),
            "humidity_percent_th": f"ความชื้นสัมพัทธ์เฉลี่ย {round(avg_humidity, 0)}%",

            "rain_probability_percent": round(rain_probability, 1),
            "rain_probability_th": f"โอกาสเกิดฝน {round(rain_probability, 0)}%",

            "avg_temperature_c": round(avg_temp, 1),
            "avg_temperature_th": f"อุณหภูมิเฉลี่ย {round(avg_temp, 1)}°C",

            # Additional metrics
            "temp_range": {
                "min": min([d["temp_min_c"] for d in daily_forecasts]),
                "max": max([d["temp_max_c"] for d in daily_forecasts])
            },

            # Daily forecast
            "daily_forecast": daily_forecasts,
            "forecast_days": len(daily_forecasts),

            # Summary
            "summary_th": summary_th,
            "summary_en": self._get_english_summary(rain_probability),

            # Metadata
            "location": {"lat": lat, "lon": lon},
            "generated_at": datetime.now().isoformat(),
            "source": "simulated",
            "source_th": "ข้อมูลจำลอง (ไม่ได้เชื่อมต่อ API)",
            "api_ready": OPENWEATHERMAP_API_KEY is not None
        }

    def _get_thai_day_name(self, weekday: int) -> str:
        """Get Thai day name from weekday number (0=Monday)."""
        thai_days = [
            "วันจันทร์",
            "วันอังคาร",
            "วันพุธ",
            "วันพฤหัสบดี",
            "วันศุกร์",
            "วันเสาร์",
            "วันอาทิตย์"
        ]
        return thai_days[weekday] if 0 <= weekday < 7 else "ไม่ทราบ"

    def _get_english_summary(self, rain_probability: float) -> str:
        """Get English weather summary."""
        if rain_probability > 60:
            return "Expect mostly rainy conditions. Prepare for wet weather."
        elif rain_probability > 30:
            return "Variable weather with some rain possible. Monitor forecasts closely."
        else:
            return "Dry and sunny conditions. Ensure adequate water supply for crops."

    def get_current_weather(self, lat: float, lon: float) -> Dict[str, Any]:
        """
        Get current weather conditions (simplified version).

        Args:
            lat: Latitude
            lon: Longitude

        Returns:
            Current weather data
        """
        current_month = datetime.now().month
        base_climate = self.PHRAE_CLIMATE.get(current_month, self.PHRAE_CLIMATE[1])

        # Generate current conditions with variation
        temp = (base_climate["temp_min"] + base_climate["temp_max"]) / 2
        temp += random.uniform(-3, 3)

        humidity = base_climate["humidity"] + random.uniform(-10, 10)
        humidity = max(40, min(95, humidity))

        return {
            "temperature_c": round(temp, 1),
            "temperature_th": f"{round(temp, 1)}°C",
            "humidity_percent": round(humidity, 0),
            "humidity_th": f"ความชื้น {round(humidity, 0)}%",
            "feels_like_c": round(temp + random.uniform(-2, 2), 1),
            "condition": base_climate["season"],
            "timestamp": datetime.now().isoformat(),
            "location": {"lat": lat, "lon": lon}
        }
