from typing import Dict, Any, List, Optional

class FertilizerService:
    # Standard ICAR soil fertility index (in mg/kg or ppm)
    # Low / Medium (Optimal) / High
    THRESHOLDS = {
        "N": {"low": 50.0, "high": 90.0, "unit": "mg/kg", "name": "Nitrogen"},
        "P": {"low": 25.0, "high": 55.0, "unit": "mg/kg", "name": "Phosphorus"},
        "K": {"low": 40.0, "high": 80.0, "unit": "mg/kg", "name": "Potassium"}
    }

    @classmethod
    def calculate_recommendations(
        cls,
        crop: str,
        nitrogen: float,
        phosphorus: float,
        potassium: float,
        ph: Optional[float] = 6.5,
        soil_type: Optional[str] = "loam",
        growth_stage: Optional[str] = "vegetative"
    ) -> Dict[str, Any]:
        crop_name = crop.capitalize()

        # Evaluate N, P, K levels
        analyses = []
        low_nutrients = []
        high_nutrients = []

        # Nitrogen
        n_status = "Optimal"
        if nitrogen < cls.THRESHOLDS["N"]["low"]:
            n_status = "Low"
            low_nutrients.append("Nitrogen")
        elif nitrogen > cls.THRESHOLDS["N"]["high"]:
            n_status = "High"
            high_nutrients.append("Nitrogen")
        analyses.append({
            "nutrient": "Nitrogen (N)",
            "current_value": nitrogen,
            "status": n_status,
            "target_range": f"{cls.THRESHOLDS['N']['low']} - {cls.THRESHOLDS['N']['high']} mg/kg"
        })

        # Phosphorus
        p_status = "Optimal"
        if phosphorus < cls.THRESHOLDS["P"]["low"]:
            p_status = "Low"
            low_nutrients.append("Phosphorus")
        elif phosphorus > cls.THRESHOLDS["P"]["high"]:
            p_status = "High"
            high_nutrients.append("Phosphorus")
        analyses.append({
            "nutrient": "Phosphorus (P)",
            "current_value": phosphorus,
            "status": p_status,
            "target_range": f"{cls.THRESHOLDS['P']['low']} - {cls.THRESHOLDS['P']['high']} mg/kg"
        })

        # Potassium
        k_status = "Optimal"
        if potassium < cls.THRESHOLDS["K"]["low"]:
            k_status = "Low"
            low_nutrients.append("Potassium")
        elif potassium > cls.THRESHOLDS["K"]["high"]:
            k_status = "High"
            high_nutrients.append("Potassium")
        analyses.append({
            "nutrient": "Potassium (K)",
            "current_value": potassium,
            "status": k_status,
            "target_range": f"{cls.THRESHOLDS['K']['low']} - {cls.THRESHOLDS['K']['high']} mg/kg"
        })

        organic_recs: List[str] = []
        chemical_recs: List[str] = []

        if "Nitrogen" in low_nutrients:
            organic_recs.append("Incorporate well-rotted Farm Yard Manure (FYM @ 5-8 tonnes/acre) or vermicompost @ 2 tonnes/acre during field prep.")
            organic_recs.append("Intercrop or green-manure with legumes (Sunnhemp / Dhaincha) to naturally fix atmospheric nitrogen.")
            chemical_recs.append(f"Top-dress Urea @ 25-30 kg/acre in 2 split doses during active vegetative growth of {crop_name}.")
        elif "Nitrogen" in high_nutrients:
            chemical_recs.append("Withhold chemical nitrogen fertilizers to prevent excessive vegetative succulent growth that attracts sucking pests.")

        if "Phosphorus" in low_nutrients:
            organic_recs.append("Apply Rock Phosphate along with Phosphate Solubilizing Bacteria (PSB) biofertilizer @ 2 kg/acre to boost root uptake.")
            chemical_recs.append("Apply Single Super Phosphate (SSP) @ 50 kg/acre or DAP @ 25 kg/acre as basal dose near the root zone.")

        if "Potassium" in low_nutrients:
            organic_recs.append("Apply wood ash or bio-potash (Frateuria aurantia) to replenish exchangeable potassium organically.")
            chemical_recs.append("Apply Muriate of Potash (MOP / 0-0-60) @ 20 kg/acre at flowering and fruit initiation to improve fruit size and disease resistance.")

        if not low_nutrients:
            organic_recs.append("Soil fertility is well-balanced. Maintain organic matter with Jeevamrutham or Panchagavya drenching every 15 days.")
            chemical_recs.append("Apply light maintenance dose of 19:19:19 water-soluble foliar spray @ 5g/L during pre-flowering.")

        # pH adjustments
        ph_val = ph or 6.5
        if ph_val < 6.0:
            organic_recs.append(f"Soil is slightly acidic (pH {ph_val}). Apply agricultural lime @ 200 kg/acre before ploughing.")
        elif ph_val > 7.8:
            organic_recs.append(f"Soil is alkaline/calcareous (pH {ph_val}). Incorporate agricultural gypsum @ 250 kg/acre and sulphur to lower pH.")

        timing = "Apply basal doses during final land preparation. Split nitrogen top-dressing between 25-30 days after sowing and flowering."

        precautions = [
            "Never mix Single Super Phosphate (SSP) directly with Urea before storage.",
            "Wear gloves and protective mask when broadcasting chemical fertilizers.",
            "Always apply fertilizers when soil has adequate moisture; avoid application on parched dry soil."
        ]

        guidance = (
            f"Soil analysis for {crop_name} indicates "
            + (f"deficiencies in {', '.join(low_nutrients)}." if low_nutrients else "balanced macronutrient status.")
        )

        return {
            "success": True,
            "crop": crop_name,
            "nutrient_analysis": analyses,
            "general_guidance": guidance,
            "organic_recommendations": organic_recs,
            "chemical_recommendations": chemical_recs,
            "application_timing": timing,
            "precautions": precautions
        }

fertilizer_service = FertilizerService()
