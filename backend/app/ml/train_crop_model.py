import os
import json
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
import joblib

# Empirical ICAR / Agricultural University benchmark ranges for 22 crops in India
CROP_DATA_PARAMS = {
    "Rice": {"N": (60, 100), "P": (35, 60), "K": (35, 50), "temp": (20, 27), "humidity": (80, 95), "ph": (5.5, 7.2), "rain": (150, 300), "season": "Kharif", "guidance": "Requires flooded or moist soil conditions and warm humid climate."},
    "Maize": {"N": (60, 100), "P": (40, 60), "K": (15, 25), "temp": (18, 27), "humidity": (55, 75), "ph": (5.5, 7.5), "rain": (60, 110), "season": "Kharif / Rabi", "guidance": "Well-drained loamy soil, sensitive to waterlogging."},
    "Chickpea": {"N": (20, 60), "P": (55, 80), "K": (75, 85), "temp": (17, 22), "humidity": (14, 20), "ph": (6.0, 8.0), "rain": (60, 90), "season": "Rabi", "guidance": "Cool climate, light to deep black soils, drought-tolerant legume."},
    "Kidneybeans": {"N": (10, 40), "P": (55, 80), "K": (15, 25), "temp": (15, 24), "humidity": (20, 30), "ph": (5.5, 6.5), "rain": (60, 150), "season": "Kharif", "guidance": "Prefers rich, well-drained loamy soil with neutral pH."},
    "Pigeonpeas": {"N": (10, 40), "P": (55, 80), "K": (15, 25), "temp": (25, 35), "humidity": (45, 65), "ph": (5.0, 7.5), "rain": (90, 200), "season": "Kharif", "guidance": "Deep root system, deep black or well-drained loam."},
    "Mothbeans": {"N": (10, 40), "P": (35, 60), "K": (15, 25), "temp": (24, 32), "humidity": (40, 65), "ph": (5.5, 8.5), "rain": (30, 75), "season": "Kharif", "guidance": "Extremely drought-resistant, suited for arid and semi-arid regions."},
    "Mungbean": {"N": (10, 40), "P": (35, 60), "K": (15, 25), "temp": (27, 35), "humidity": (80, 90), "ph": (6.2, 7.5), "rain": (35, 60), "season": "Kharif / Summer", "guidance": "Warm climate, well-drained loam or alluvial soils."},
    "Blackgram": {"N": (20, 60), "P": (55, 80), "K": (15, 25), "temp": (25, 35), "humidity": (60, 70), "ph": (6.5, 7.8), "rain": (60, 75), "season": "Kharif / Rabi", "guidance": "Heavy soils like vertisols, requires moderate moisture."},
    "Lentil": {"N": (10, 40), "P": (55, 80), "K": (15, 25), "temp": (18, 25), "humidity": (60, 70), "ph": (5.5, 7.0), "rain": (35, 55), "season": "Rabi", "guidance": "Cool season legume, light loams and alluvial soils."},
    "Pomegranate": {"N": (15, 45), "P": (10, 30), "K": (35, 55), "temp": (18, 25), "humidity": (85, 95), "ph": (5.5, 7.5), "rain": (100, 115), "season": "Whole Year", "guidance": "Semi-arid climate, deep loamy soils, drip irrigation recommended."},
    "Banana": {"N": (90, 120), "P": (70, 95), "K": (45, 55), "temp": (25, 30), "humidity": (75, 85), "ph": (5.5, 6.5), "rain": (90, 120), "season": "Whole Year", "guidance": "High nutrient feeder, rich organic soils with adequate drainage."},
    "Mango": {"N": (10, 40), "P": (15, 40), "K": (25, 35), "temp": (27, 36), "humidity": (45, 55), "ph": (4.5, 7.0), "rain": (85, 105), "season": "Summer", "guidance": "Tropical climate, deep alluvial or loamy soils."},
    "Grapes": {"N": (10, 40), "P": (120, 145), "K": (195, 205), "temp": (8, 42), "humidity": (80, 85), "ph": (5.5, 7.0), "rain": (65, 75), "season": "Rabi / Summer", "guidance": "Well-drained sandy loam or clay loam with high potash."},
    "Watermelon": {"N": (80, 120), "P": (5, 30), "K": (45, 55), "temp": (24, 27), "humidity": (80, 90), "ph": (6.0, 7.0), "rain": (40, 60), "season": "Zaid / Summer", "guidance": "Warm dry climate, sandy loams with organic matter."},
    "Muskmelon": {"N": (80, 120), "P": (5, 30), "K": (45, 55), "temp": (27, 30), "humidity": (90, 95), "ph": (6.0, 6.8), "rain": (20, 30), "season": "Zaid / Summer", "guidance": "High sunshine, warm nights, well-drained sandy soil."},
    "Apple": {"N": (10, 40), "P": (120, 145), "K": (195, 205), "temp": (21, 24), "humidity": (90, 95), "ph": (5.5, 6.5), "rain": (100, 125), "season": "Temperate", "guidance": "Hill stations, rich well-aerated loamy soil."},
    "Orange": {"N": (10, 40), "P": (5, 30), "K": (5, 15), "temp": (10, 35), "humidity": (90, 95), "ph": (6.0, 8.0), "rain": (100, 120), "season": "Winter / Spring", "guidance": "Subtropical climate, light well-drained soils."},
    "Papaya": {"N": (30, 70), "P": (45, 70), "K": (45, 55), "temp": (23, 44), "humidity": (90, 95), "ph": (6.5, 7.0), "rain": (140, 250), "season": "Whole Year", "guidance": "Tropical climate, fertile well-drained soil, avoid water stagnation."},
    "Coconut": {"N": (15, 40), "P": (10, 30), "K": (25, 35), "temp": (25, 29), "humidity": (90, 98), "ph": (5.0, 8.0), "rain": (130, 230), "season": "Whole Year", "guidance": "Coastal and high humidity regions, deep sandy loam."},
    "Cotton": {"N": (100, 140), "P": (35, 60), "K": (15, 25), "temp": (22, 26), "humidity": (60, 85), "ph": (6.0, 8.0), "rain": (60, 100), "season": "Kharif", "guidance": "Black cotton soil (vertisols), warm climate, moderate moisture."},
    "Jute": {"N": (60, 100), "P": (35, 60), "K": (35, 45), "temp": (23, 26), "humidity": (70, 90), "ph": (6.0, 7.5), "rain": (150, 200), "season": "Kharif", "guidance": "Warm and wet climate, fertile alluvial plains."},
    "Coffee": {"N": (80, 120), "P": (15, 40), "K": (25, 35), "temp": (23, 28), "humidity": (50, 70), "ph": (6.0, 7.0), "rain": (115, 200), "season": "Plantation", "guidance": "Highlands with shade, well-drained humus-rich acidic soil."}
}

def generate_dataset(samples_per_crop=120):
    """Generate realistic agricultural dataset based on ICAR agronomic distributions."""
    rows = []
    np.random.seed(42)

    for crop, params in CROP_DATA_PARAMS.items():
        for _ in range(samples_per_crop):
            n = np.clip(np.random.normal(np.mean(params["N"]), (params["N"][1] - params["N"][0]) / 4), 0, 200)
            p = np.clip(np.random.normal(np.mean(params["P"]), (params["P"][1] - params["P"][0]) / 4), 0, 180)
            k = np.clip(np.random.normal(np.mean(params["K"]), (params["K"][1] - params["K"][0]) / 4), 0, 220)
            temp = np.clip(np.random.normal(np.mean(params["temp"]), (params["temp"][1] - params["temp"][0]) / 4), 5, 45)
            hum = np.clip(np.random.normal(np.mean(params["humidity"]), (params["humidity"][1] - params["humidity"][0]) / 4), 10, 100)
            ph = np.clip(np.random.normal(np.mean(params["ph"]), (params["ph"][1] - params["ph"][0]) / 4), 3.5, 9.5)
            rain = np.clip(np.random.normal(np.mean(params["rain"]), (params["rain"][1] - params["rain"][0]) / 4), 15, 400)

            rows.append({
                "N": round(float(n), 2),
                "P": round(float(p), 2),
                "K": round(float(k), 2),
                "temperature": round(float(temp), 2),
                "humidity": round(float(hum), 2),
                "ph": round(float(ph), 2),
                "rainfall": round(float(rain), 2),
                "label": crop
            })

    return pd.DataFrame(rows)

def train_and_save():
    os.makedirs("models", exist_ok=True)
    os.makedirs("datasets", exist_ok=True)

    df = generate_dataset()
    df.to_csv("datasets/crop_recommendation.csv", index=False)
    print(f"Generated dataset with {len(df)} records across {df['label'].nunique()} crops.")

    X = df[["N", "P", "K", "temperature", "humidity", "ph", "rainfall"]]
    y = df["label"]

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

    model = RandomForestClassifier(n_estimators=100, max_depth=16, random_state=42)
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    print(f"Random Forest Crop Recommendation Model Test Accuracy: {acc * 100:.2f}%")

    # Save model and metadata
    joblib.dump(model, "models/crop_recommendation.joblib")

    meta = {crop: {"season": data["season"], "guidance": data["guidance"]} for crop, data in CROP_DATA_PARAMS.items()}
    with open("models/crop_metadata.json", "w") as f:
        json.dump(meta, f, indent=2)

    print("Model and metadata saved to models/crop_recommendation.joblib and models/crop_metadata.json")
    return acc

if __name__ == "__main__":
    train_and_save()
