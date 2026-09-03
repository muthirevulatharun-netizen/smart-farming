import io
from fastapi.testclient import TestClient
from PIL import Image
import pytest

from backend.app.main import app
from backend.app.database.connection import SessionLocal
from backend.app.database.models import User

client = TestClient(app)

# ============================================================
# 1. System Health Check Test
# ============================================================
def test_health_check():
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "service" in data

# ============================================================
# 2. Authentication & Mobile OTP Tests (Section 7, 8, 9, 10, 34)
# ============================================================
def test_otp_send_and_verify_flow():
    test_phone = "+919876543210"

    # Send OTP
    send_resp = client.post("/api/auth/otp/send", json={"phone": test_phone})
    assert send_resp.status_code == 200
    send_data = send_resp.json()
    assert send_data["success"] is True
    assert send_data["dev_otp"] is not None
    otp_code = send_data["dev_otp"]

    # Verify with Wrong OTP
    wrong_resp = client.post("/api/auth/otp/verify", json={"phone": test_phone, "otp": "000000"})
    assert wrong_resp.status_code == 400
    err_text = wrong_resp.json().get("message") or wrong_resp.json().get("detail")
    assert "Incorrect OTP" in err_text

    # Verify with Correct OTP
    verify_resp = client.post("/api/auth/otp/verify", json={"phone": test_phone, "otp": otp_code, "name": "Ramesh Farmer"})
    assert verify_resp.status_code == 200
    verify_data = verify_resp.json()
    assert "access_token" in verify_data
    assert verify_data["user"]["phone"] == test_phone
    token = verify_data["access_token"]

    # Test Authenticated /api/auth/me Endpoint
    me_resp = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me_resp.status_code == 200
    assert me_resp.json()["phone"] == test_phone

def test_password_register_and_login():
    phone = "+919123456780"
    client.post("/api/auth/register", json={
        "phone": phone,
        "name": "Suresh Kumar",
        "email": "suresh@example.com",
        "password": "Password123"
    })

    # Login with phone
    login_resp = client.post("/api/auth/login", json={
        "identifier": phone,
        "password": "Password123"
    })
    assert login_resp.status_code == 200
    assert "access_token" in login_resp.json()

    # Login with wrong password
    bad_login = client.post("/api/auth/login", json={
        "identifier": phone,
        "password": "WrongPassword"
    })
    assert bad_login.status_code == 401

# ============================================================
# 3. Crop Recommendation ML Tests (Section 14, 34)
# ============================================================
def test_crop_recommendation_valid():
    payload = {
        "nitrogen": 90,
        "phosphorus": 42,
        "potassium": 43,
        "temperature": 25,
        "humidity": 80,
        "ph": 6.5,
        "rainfall": 200
    }
    resp = client.post("/api/crop/recommend", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["success"] is True
    assert "recommended_crop" in data
    assert data["confidence"] > 0
    assert "suitable_season" in data
    assert "guidance" in data

def test_crop_recommendation_invalid_input():
    payload = {
        "nitrogen": -10,  # invalid negative
        "phosphorus": 42,
        "potassium": 43,
        "temperature": 25,
        "humidity": 80,
        "ph": 6.5,
        "rainfall": 200
    }
    resp = client.post("/api/crop/recommend", json=payload)
    assert resp.status_code == 422  # validation error

# ============================================================
# 4. Crop Disease Computer Vision Tests (Section 15, 34)
# ============================================================
def test_disease_prediction_valid_image():
    # Create an in-memory test image
    img = Image.new("RGB", (224, 224), color=(34, 139, 34))
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format='JPEG')
    img_bytes = img_byte_arr.getvalue()

    files = {"file": ("tomato_leaf.jpg", img_bytes, "image/jpeg")}
    data = {"crop_hint": "Tomato"}
    resp = client.post("/api/disease/predict", files=files, data=data)
    assert resp.status_code == 200
    result = resp.json()
    assert result["success"] is True
    assert "disease" in result
    assert "confidence" in result
    assert len(result["symptoms"]) > 0
    assert len(result["treatment"]) > 0
    assert "disclaimer" in result

def test_disease_prediction_unsupported_file():
    files = {"file": ("script.exe", b"executable bytes", "application/octet-stream")}
    resp = client.post("/api/disease/predict", files=files)
    assert resp.status_code == 400
    assert "Unsupported file type" in resp.json()["message"]

# ============================================================
# 5. Pest Identification Tests (Section 16)
# ============================================================
def test_pest_prediction():
    resp = client.post("/api/pest/predict", data={"pest_hint": "Whitefly"})
    assert resp.status_code == 200
    data = resp.json()
    assert "Whitefly" in data["pest"]
    assert len(data["control_guidance"]) > 0

# ============================================================
# 6. AI Chatbot Tests - English & Telugu (Section 12, 13, 24, 34)
# ============================================================
def test_chatbot_english_query():
    resp = client.post("/api/chat", json={
        "message": "Why are my tomato leaves turning yellow?",
        "crop": "Tomato",
        "language": "en"
    })
    assert resp.status_code == 200
    data = resp.json()
    assert data["success"] is True
    assert len(data["answer"]) > 20

def test_chatbot_telugu_query():
    # Query in Telugu: "నా వరి పంటకు ఏ ఎరువు ఉపయోగించాలి?" (Which fertilizer for rice?)
    resp = client.post("/api/chat", json={
        "message": "నా వరి పంటకు ఏ ఎరువు ఉపయోగించాలి?",
        "crop": "Rice",
        "language": "te"
    })
    assert resp.status_code == 200
    data = resp.json()
    assert data["success"] is True
    assert data["language"] == "te"
    assert len(data["answer"]) > 10

# ============================================================
# 7. Real Weather API Tests (Section 17, 34)
# ============================================================
def test_weather_current_and_forecast():
    resp = client.get("/api/weather/current?lat=13.2172&lon=79.1003")
    assert resp.status_code == 200
    data = resp.json()
    assert data["success"] is True
    assert "temperature" in data
    assert "humidity" in data
    assert "ai_advisory" in data

    forecast_resp = client.get("/api/weather/forecast?lat=13.2172&lon=79.1003")
    assert forecast_resp.status_code == 200
    forecast_data = forecast_resp.json()
    assert len(forecast_data["forecast"]) >= 3

# ============================================================
# 8. Fertilizer & Irrigation Recommendation Tests (Section 19, 20, 34)
# ============================================================
def test_fertilizer_recommendation():
    resp = client.post("/api/fertilizer/recommend", json={
        "crop": "Tomato",
        "soil_type": "loam",
        "nitrogen": 40,  # low
        "phosphorus": 20, # low
        "potassium": 75, # optimal
        "ph": 6.4
    })
    assert resp.status_code == 200
    data = resp.json()
    assert data["success"] is True
    assert len(data["nutrient_analysis"]) == 3
    assert len(data["organic_recommendations"]) > 0

def test_irrigation_recommendation():
    resp = client.post("/api/irrigation/recommend", json={
        "crop": "Tomato",
        "soil_type": "loam",
        "moisture_level": 25.0, # low moisture
        "temperature": 32.0,
        "humidity": 45.0,
        "forecast_rain_prob": 10.0
    })
    assert resp.status_code == 200
    data = resp.json()
    assert data["success"] is True
    assert data["irrigation_required"] is True
    assert data["estimated_water_liters_per_acre"] > 0

def test_irrigation_suppression_on_rain():
    # If 80% chance of rain, irrigation should not be recommended
    resp = client.post("/api/irrigation/recommend", json={
        "crop": "Tomato",
        "soil_type": "loam",
        "moisture_level": 25.0,
        "forecast_rain_prob": 80.0
    })
    assert resp.status_code == 200
    data = resp.json()
    assert data["irrigation_required"] is False

# ============================================================
# 9. Dashboard Aggregator Test (Section 22, 25)
# ============================================================
def test_dashboard_aggregator():
    resp = client.get("/api/dashboard")
    assert resp.status_code == 200
    data = resp.json()
    assert data["success"] is True
    assert "farmer" in data
    assert "weather" in data
    assert "farm_health" in data
    assert "crops_health" in data
