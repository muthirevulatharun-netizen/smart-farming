import os
import json
from typing import Dict, Any, List
import joblib
import numpy as np

class CropRecommendationEngine:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(CropRecommendationEngine, cls).__new__(cls)
            cls._instance._load_model()
        return cls._instance

    def _load_model(self):
        # Look for model file in standard locations
        model_paths = [
            "models/crop_recommendation.joblib",
            "../models/crop_recommendation.joblib",
            os.path.join(os.path.dirname(__file__), "../../../models/crop_recommendation.joblib")
        ]
        self.model = None
        for path in model_paths:
            if os.path.exists(path):
                self.model = joblib.load(path)
                break

        meta_paths = [
            "models/crop_metadata.json",
            "../models/crop_metadata.json",
            os.path.join(os.path.dirname(__file__), "../../../models/crop_metadata.json")
        ]
        self.metadata = {}
        for path in meta_paths:
            if os.path.exists(path):
                with open(path, "r") as f:
                    self.metadata = json.load(f)
                break

    def predict(
        self,
        nitrogen: float,
        phosphorus: float,
        potassium: float,
        temperature: float,
        humidity: float,
        ph: float,
        rainfall: float
    ) -> Dict[str, Any]:
        """Predict top recommended crops with confidence percentages."""
        if self.model is None:
            # Lazy train if model hasn't been generated yet
            from backend.app.ml.train_crop_model import train_and_save
            train_and_save()
            self._load_model()

        import pandas as pd
        input_data = pd.DataFrame([[nitrogen, phosphorus, potassium, temperature, humidity, ph, rainfall]],
                                  columns=["N", "P", "K", "temperature", "humidity", "ph", "rainfall"])
        probabilities = self.model.predict_proba(input_data)[0]
        classes = self.model.classes_

        # Sort by highest probability
        sorted_indices = np.argsort(probabilities)[::-1]
        top_index = sorted_indices[0]
        top_crop = classes[top_index]
        top_confidence = float(probabilities[top_index])

        # Top 3 alternative crops
        alternatives: List[Dict[str, Any]] = []
        for idx in sorted_indices[1:4]:
            if probabilities[idx] > 0.05:
                alternatives.append({
                    "crop": classes[idx],
                    "confidence": round(float(probabilities[idx]) * 100, 1)
                })

        meta = self.metadata.get(top_crop, {
            "season": "Kharif / Rabi",
            "guidance": "Follow standard agricultural practices for balanced nutrient management."
        })

        return {
            "recommended_crop": top_crop,
            "confidence": round(top_confidence * 100, 1),
            "suitable_season": meta.get("season", "Kharif"),
            "guidance": meta.get("guidance", "Optimal agronomic conditions detected."),
            "alternatives": alternatives
        }

crop_engine = CropRecommendationEngine()
