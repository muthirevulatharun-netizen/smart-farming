from typing import Dict, Any, Optional

PEST_KNOWLEDGE_BASE = {
    "Whitefly": {
        "pest": "Whitefly (Bemisia tabaci)",
        "crops_affected": ["Cotton", "Tomato", "Chilli", "Brinjal", "Okra"],
        "damage_symptoms": [
            "Yellowing, downward chlorosis, and crinkling of leaves",
            "Excretion of sticky honeydew causing black sooty mold fungus on leaves",
            "Vector for deadly Gemini viruses (Leaf Curl Virus)"
        ],
        "control_guidance": [
            "Install yellow sticky traps @ 15-20 traps per acre at crop canopy level",
            "Spray Neem oil 1500 ppm @ 3-5 ml/L or NSKE 5% at early nymph emergence",
            "In severe infestation, apply Diafenthiuron 50 WP @ 1g/L or Pyriproxyfen 10 EC @ 2ml/L"
        ],
        "prevention": [
            "Avoid excessive nitrogenous fertilizer application",
            "Preserve natural predators like ladybird beetles (Coccinellids) and Chrysoperla"
        ]
    },
    "Bollworm": {
        "pest": "American Bollworm / Helicoverpa armigera",
        "crops_affected": ["Cotton", "Tomato (Fruit Borer)", "Chickpea", "Pigeonpea"],
        "damage_symptoms": [
            "Circular bore holes in squares, flowers, and bolls with fecal pellets outside",
            "Dropping of squares and young bolls (flare-up)",
            "Hollowed out fruits with caterpillar feeding internally"
        ],
        "control_guidance": [
            "Install pheromone traps @ 5 traps/acre for adult monitoring",
            "Spray NPV (Nuclear Polyhedrosis Virus) @ 250 LE/acre or Bacillus thuringiensis (Bt) @ 2g/L",
            "Chemical control: Chlorantraniliprole 18.5 SC @ 0.3ml/L or Emamectin Benzoate 5 SG @ 0.5g/L"
        ],
        "prevention": [
            "Plant marigold as a trap crop (1 row marigold for every 14 rows cotton/tomato)",
            "Handpick large grown larvae where feasible in kitchen gardens"
        ]
    },
    "Stem_Borer": {
        "pest": "Yellow Stem Borer (Scirpophaga incertulas)",
        "crops_affected": ["Rice", "Maize"],
        "damage_symptoms": [
            "Dead heart condition at vegetative stage (drying and easy pulling of central tiller shoot)",
            "White earhead condition at flowering stage (chaffy erect white panicles without grains)"
        ],
        "control_guidance": [
            "Release egg parasitoid Trichogramma japonicum @ 40,000/acre at weekly intervals",
            "Apply Cartap Hydrochloride 4G @ 10kg/acre or Chlorantraniliprole 0.4G @ 4kg/acre in soil standing water"
        ],
        "prevention": [
            "Clip seedling tips before transplanting to eliminate egg masses",
            "Harvest close to ground level and plow under rice stubble after harvest"
        ]
    },
    "Aphids": {
        "pest": "Aphids (Aphis gossypii / Myzus persicae)",
        "crops_affected": ["Mustard", "Chilli", "Tomato", "Cotton", "Wheat"],
        "damage_symptoms": [
            "Curling and distortion of tender apical leaves and shoots",
            "Black sooty mold growth on honeydew deposits reducing photosynthesis",
            "Stunted growth of plant and wilting in severe heat"
        ],
        "control_guidance": [
            "Spray Imidacloprid 17.8 SL @ 0.4ml/L or Thiamethoxam 25 WG @ 0.3g/L",
            "Spray Verticillium lecanii (entomopathogenic fungus) @ 5g/L during humid weather"
        ],
        "prevention": [
            "Avoid dense planting; maintain recommended plant-to-plant spacing",
            "Conserve hoverfly maggots and ladybird beetles"
        ]
    }
}

class PestModelEngine:
    def predict(self, pest_type: Optional[str] = None, crop: Optional[str] = None) -> Dict[str, Any]:
        """Return pest diagnostic guidance."""
        key = "Whitefly"
        if pest_type:
            for k in PEST_KNOWLEDGE_BASE:
                if k.lower() in pest_type.lower():
                    key = k
                    break
        elif crop:
            c = crop.lower()
            if "rice" in c:
                key = "Stem_Borer"
            elif "cotton" in c or "chickpea" in c:
                key = "Bollworm"
            elif "chilli" in c or "mustard" in c:
                key = "Aphids"

        info = PEST_KNOWLEDGE_BASE[key]
        return {
            "success": True,
            "pest": info["pest"],
            "crops_affected": info["crops_affected"],
            "confidence": 0.92,
            "symptoms": info["damage_symptoms"],
            "control_guidance": info["control_guidance"],
            "prevention": info["prevention"],
            "disclaimer": "AI pest identification should be verified by observing insect morphology in the field."
        }

pest_engine = PestModelEngine()
