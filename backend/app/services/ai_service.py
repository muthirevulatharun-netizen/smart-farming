import os
import json
from typing import Dict, Any, Optional
import httpx
from backend.app.config import settings

AGRICULTURAL_SYSTEM_PROMPT = """You are 'Smart Farming AI', an expert digital agronomist dedicated to assisting Indian farmers.
Your goal is to provide precise, practical, and sustainable agricultural advice in the farmer's preferred language (English, Telugu తెలుగు, or Hindi).

GUIDELINES:
1. Always ground your responses in real agricultural science and Indian farming practices (ICAR, KVK, State Agricultural Universities).
2. Incorporate the farmer's contextual data when available (current crop, soil type, location, weather conditions, recent rainfall, disease history).
3. If asked about irrigation (e.g. 'Should I water today?'), analyze the ambient temperature, humidity, soil type, and rain forecast before answering.
4. When answering in Telugu, use authentic Telugu terminology (e.g. వరి for Rice, పత్తి for Cotton, ఎరువులు for Fertilizers, తెగులు for Disease, నీటిపారుదల for Irrigation).
5. Always maintain safety precautions for chemical usage and mention that AI advice is for informational guidance.
"""

class AIService:
    @classmethod
    def generate_chat_response(
        cls,
        message: str,
        crop: Optional[str] = None,
        language: str = "en",
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Generate context-rich agricultural AI response in English or Telugu."""
        lang_code = (language or "en").lower()
        is_telugu = "te" in lang_code or any('\u0C00' <= char <= '\u0C7F' for char in message)

        # Context synthesis
        context_str = ""
        if context:
            context_str = f"""
FARMER CONTEXT:
- Farmer Name: {context.get('farmer_name', 'Farmer')}
- Active Crop: {crop or context.get('primary_crop', 'General')}
- Soil Type: {context.get('soil_type', 'Loam')}
- Location: {context.get('location', 'Andhra Pradesh, India')}
- Current Weather: Temp {context.get('temperature', 32)}°C, Humidity {context.get('humidity', 60)}%, Rain Probability {context.get('rain_probability', 10)}%
- Recent Disease Scans: {context.get('recent_disease', 'None')}
"""

        # Try Google Gemini API if key is available
        api_key = settings.GEMINI_API_KEY or os.environ.get("GEMINI_API_KEY")
        if api_key:
            try:
                endpoint = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
                prompt_content = f"{AGRICULTURAL_SYSTEM_PROMPT}\n\n{context_str}\n\nFarmer Query: {message}\n\nPreferred Language: {'Telugu' if is_telugu else 'English'}\nAnswer:"

                payload = {
                    "contents": [{"parts": [{"text": prompt_content}]}],
                    "generationConfig": {"temperature": 0.4, "maxOutputTokens": 800}
                }

                with httpx.Client(timeout=12) as client:
                    resp = client.post(endpoint, json=payload)
                    if resp.status_code == 200:
                        data = resp.json()
                        candidates = data.get("candidates", [])
                        if candidates:
                            answer_text = candidates[0].get("content", {}).get("parts", [{}])[0].get("text", "")
                            if answer_text.strip():
                                return {
                                    "success": True,
                                    "answer": answer_text.strip(),
                                    "language": "te" if is_telugu else "en",
                                    "context_used": context
                                }
            except Exception as e:
                # Fall through to context-aware agronomic knowledge engine
                pass

        # Context-Aware Agricultural Knowledge Engine Fallback
        answer = cls._fallback_knowledge_engine(message, crop, is_telugu, context)
        return {
            "success": True,
            "answer": answer,
            "language": "te" if is_telugu else "en",
            "context_used": context
        }

    @classmethod
    def _fallback_knowledge_engine(
        cls,
        message: str,
        crop: Optional[str],
        is_telugu: bool,
        context: Optional[Dict[str, Any]]
    ) -> str:
        msg_lower = message.lower()
        active_crop = crop or (context.get("primary_crop") if context else "Tomato")

        # Query 1: Water / Irrigation
        if any(w in msg_lower for w in ["water", "irrigation", "irrigate", "తడి", "నీరు", "నీటి"]):
            rain_prob = context.get("rain_probability", 20) if context else 20
            temp = context.get("temperature", 32) if context else 32
            if rain_prob > 50:
                if is_telugu:
                    return f"మీ ప్రాంతంలో వర్షం పడే అవకాశం {int(rain_prob)}% ఉంది. కాబట్టి ఈరోజు {active_crop} పంటకు నీరు పెట్టడం వాయిదా వేయడం మంచిది. దీనివల్ల నీరు ఆదా అవుతుంది మరియు వేరు కుళ్లు తెగులు రాకుండా ఉంటుంది."
                return f"There is a high chance of rainfall ({int(rain_prob)}%) in your area today. We recommend postponing irrigation for your {active_crop} crop to prevent waterlogging and save resources."
            else:
                if is_telugu:
                    return f"ప్రస్తుత ఉష్ణోగ్రత {temp}°C గా ఉంది. నేలలో తేమ తక్కువగా ఉంటే, ఆవిరి కాకుండా ఉండటానికి ఉదయం (6:00 AM - 8:30 AM) లేదా సాయంత్రం వేళల్లో {active_crop} పంటకు బిందు సేద్యం (Drip Irrigation) ద్వారా తేలికపాటి తడి ఇవ్వండి."
                return f"Current temperature is {temp}°C with dry conditions. Provide moderate irrigation to your {active_crop} crop during cooler hours (early morning 6:00 - 8:30 AM or evening) to minimize moisture evaporation."

        # Query 2: Yellow Leaves / Disease
        if any(w in msg_lower for w in ["yellow", "spots", "leaves", "disease", "ఆకులు", "పసుపు", "మచ్చలు", "తెగులు"]):
            if is_telugu:
                return (
                    f"{active_crop} పంటలో ఆకులు పసుపు రంగులోకి మారడానికి లేదా మచ్చలు రావడానికి ముఖ్య కారణాలు:\n\n"
                    "1. నత్రజని (Nitrogen) లోపం - దిగువ ఆకులు ముందుగా పసుపుగా మారతాయి.\n"
                    "2. అధిక తేమ లేదా నీటి నిల్వ (Overwatering/Poor drainage).\n"
                    "3. శిలీంధ్ర తెగుళ్లు (Early Blight / Leaf spot) లేదా రసం పీల్చే పురుగులు.\n\n"
                    "సిఫార్సు: మరింత ఖచ్చితమైన విశ్లేషణ కోసం మన 'Crop Scanner' లో ఆకు ఫోటోను అప్‌లోడ్ చేయండి. ప్రస్తుతానికి నీటి నిల్వను తగ్గించి, 19:19:19 ఎరువును 5 గ్రాములు లీటరు నీటికి కలిపి పిచికారీ చేయవచ్చు."
                )
            return (
                f"Yellowing leaves or spots in your {active_crop} crop are typically caused by:\n\n"
                "1. **Nutrient Deficiency:** Nitrogen deficit usually shows yellowing starting from bottom leaves; Iron/Zinc deficit shows in top young leaves.\n"
                "2. **Overwatering / Poor Drainage:** Roots suffocating in waterlogged soil.\n"
                "3. **Fungal or Sucking Pest Damage:** Fungal spots (Early Blight) or whitefly sap depletion.\n\n"
                "**Action:** Please upload a clear photo of the leaf using our **Crop Scanner** for instant computer vision diagnosis. In the meantime, avoid overhead watering."
            )

        # Query 3: Fertilizer / Nutrient
        if any(w in msg_lower for w in ["fertilizer", "manure", "urea", "npk", "ఎరువు", "యూరియా", "పోషకాలు"]):
            if is_telugu:
                return (
                    f"{active_crop} పంటకు సమతుల్య పోషక యాజమాన్యం:\n\n"
                    "1. సేంద్రీయ పద్ధతి: ఎకరానికి 5-8 టన్నుల చివికిన పశువుల ఎరువు లేదా 2 టన్నుల వర్మీకంపోస్ట్ వేయండి.\n"
                    "2. రసాయన ఎరువులు: నేల స్వభావాన్ని బట్టి నత్రజని, భాస్వరం, పొటాష్ (NPK) ను సమతుల్యంగా వేయాలి. పూత దశకు ముందు 19:19:19 నీటిలో కరిగే ఎరువును (5 గ్రా/లీ) పిచికారీ చేయండి.\n"
                    "3. జీవన ఎరువులు: అజోస్పైరిల్లమ్ మరియు PSB వాడటం వల్ల పోషక గ్రహణ శక్తి పెరుగుతుంది."
                )
            return (
                f"Fertilizer recommendations for your {active_crop} crop:\n\n"
                "1. **Basal Application:** Apply well-rotted Farm Yard Manure (FYM @ 5-8 tonnes/acre) or vermicompost along with biofertilizers (PSB/Azospirillum).\n"
                "2. **NPK Regime:** Apply Phosphatic fertilizers (SSP/DAP) as basal dose. Split Nitrogen (Urea) into 2-3 top dressings to prevent leaching.\n"
                "3. **Micronutrients:** Spray water-soluble 19:19:19 (@ 5g/L) during active vegetative and pre-flowering stage."
            )

        # Query 4: Which crop to grow / Crop planning
        if any(w in msg_lower for w in ["which crop", "what crop", "recommend", "ఏ పంట", "సాగు"]):
            if is_telugu:
                return (
                    "మీ ప్రాంత నేల రకం మరియు వాతావరణాన్ని బట్టి ఖరీఫ్ / రబీ సీజన్ కు తగిన పంటలు:\n\n"
                    "1. లోమీ / ఎర్ర నేలలు: టమోటా, మిరప, పత్తి, వేరుశనగ అత్యధిక దిగుబడినిస్తాయి.\n"
                    "2. నల్లరేగడి నేలలు: పత్తి, శనగ, మొక్కజొన్న అనుకూలమైనవి.\n"
                    "3. తక్కువ నీటి సదుపాయం ఉన్నచోట: పెసలు, మినుములు, చిరుధాన్యాలు (మిల్లెట్స్) సాగు చేయండి.\n\n"
                    "మీ మట్టి N-P-K విలువలను మా 'Crop Recommendation' టూల్ లో ఎంటర్ చేసి ఖచ్చితమైన AI నివేదికను పొందండి!"
                )
            return (
                "Based on seasonal agricultural patterns in India:\n\n"
                "1. **Loamy & Alluvial Soils:** Tomato, Chilli, Cotton, and Groundnut provide high market value.\n"
                "2. **Black Vertisols:** Cotton, Maize, and Chickpea thrive with high moisture retention.\n"
                "3. **Water-Limited Regions:** Legumes (Mungbean, Blackgram) or Millets (Jowar, Bajra).\n\n"
                "For exact data-driven suggestions, enter your soil test values (N, P, K, pH) into our **Crop Recommendation** feature!"
            )

        # General response
        if is_telugu:
            return (
                f"నమస్కారం! నేను మీ స్మార్ట్ వ్యవసాయ సహాయకుడిని. మీ {active_crop} పంట ఆరోగ్యం, నీటిపారుదల, ఎరువులు, చీడపీడల నివారణ మరియు వాతావరణం గురించి ఏవైనా సందేహాలు ఉంటే అడగండి. మీకు సహాయం చేయడానికి సిద్ధంగా ఉన్నాను."
            )
        return (
            f"Hello! I am your Smart Farming AI Assistant. I can assist you with your {active_crop} crop, soil nutrition, disease diagnosis, weather alerts, and irrigation planning. How can I help your farm today?"
        )

ai_service = AIService()
