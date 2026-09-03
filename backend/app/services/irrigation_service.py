from typing import Dict, Any, Optional
from backend.app.services.weather_service import weather_service

class IrrigationService:
    # Soil field capacity and wilting point baselines
    SOIL_MOISTURE_THRESHOLDS = {
        "sandy": {"critical": 25.0, "optimal": 45.0, "factor": 1.2},
        "loam": {"critical": 35.0, "optimal": 60.0, "factor": 1.0},
        "clay": {"critical": 45.0, "optimal": 70.0, "factor": 0.8},
        "silt": {"critical": 35.0, "optimal": 65.0, "factor": 0.9}
    }

    CROP_WATER_FACTORS = {
        "Rice": 2.5,
        "Banana": 1.8,
        "Sugarcane": 1.7,
        "Tomato": 1.2,
        "Cotton": 1.1,
        "Chilli": 1.0,
        "Maize": 1.0,
        "Chickpea": 0.6,
        "Lentil": 0.5
    }

    @classmethod
    def calculate_recommendation(
        cls,
        crop: Optional[str] = "Tomato",
        soil_type: Optional[str] = "loam",
        moisture_level: Optional[float] = None,
        temperature: Optional[float] = None,
        humidity: Optional[float] = None,
        recent_rainfall: Optional[float] = 0.0,
        forecast_rain_prob: Optional[float] = None,
        growth_stage: Optional[str] = "vegetative"
    ) -> Dict[str, Any]:
        s_type = (soil_type or "loam").lower()
        thresholds = cls.SOIL_MOISTURE_THRESHOLDS.get(s_type, cls.SOIL_MOISTURE_THRESHOLDS["loam"])

        # Fetch live weather if parameters omitted
        if temperature is None or humidity is None or forecast_rain_prob is None:
            w_data = weather_service.get_weather()
            current_w = w_data.get("current", {})
            temperature = current_w.get("temperature", 30.0)
            humidity = current_w.get("humidity", 55.0)
            forecast_rain_prob = current_w.get("rain_probability", 15.0)

        # Baseline moisture estimation if sensor value is absent
        if moisture_level is None:
            est_moisture = 45.0 - (temperature * 0.4) + (humidity * 0.2) + ((recent_rainfall or 0.0) * 0.5)
            moisture_level = round(float(min(95.0, max(15.0, est_moisture))), 1)

        crop_name = (crop or "Tomato").capitalize()
        crop_factor = cls.CROP_WATER_FACTORS.get(crop_name, 1.0)

        # Decision logic
        rain_prob = forecast_rain_prob or 0.0
        is_dry = moisture_level < thresholds["critical"]
        heavy_rain_expected = rain_prob >= 60.0

        if heavy_rain_expected:
            irrigation_required = False
            rec_time = "Postponed"
            liters = 0.0
            reason = f"High probability of rainfall ({int(rain_prob)}%) expected within 24 hours. Avoid unnecessary irrigation today to save water and prevent root hypoxia."
        elif is_dry:
            irrigation_required = True
            rec_time = "Early morning (6:00 AM - 8:30 AM) or Late evening"
            liters = round(12000.0 * crop_factor * thresholds["factor"], 0)
            reason = f"Soil moisture ({moisture_level}%) is below optimal threshold ({thresholds['critical']}%) for {s_type} soil. Provide thorough irrigation during cooler hours to minimize evaporation."
        elif moisture_level < thresholds["optimal"]:
            # Moderate
            if temperature > 34:
                irrigation_required = True
                rec_time = "Early morning"
                liters = round(6000.0 * crop_factor * thresholds["factor"], 0)
                reason = f"Moisture is moderate ({moisture_level}%), but ambient temperature is high ({temperature}°C). Light maintenance irrigation recommended to prevent canopy wilting."
            else:
                irrigation_required = False
                rec_time = "Not required today"
                liters = 0.0
                reason = f"Soil moisture is adequate ({moisture_level}%). Re-evaluate moisture levels tomorrow."
        else:
            irrigation_required = False
            rec_time = "Not required"
            liters = 0.0
            reason = f"Soil moisture ({moisture_level}%) is at or above optimal field capacity. No additional watering required."

        return {
            "success": True,
            "irrigation_required": irrigation_required,
            "recommended_time": rec_time,
            "estimated_water_liters_per_acre": liters,
            "moisture_percentage": moisture_level,
            "reason": reason,
            "is_estimate": True
        }

irrigation_service = IrrigationService()
