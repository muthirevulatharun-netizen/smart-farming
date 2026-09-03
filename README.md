# Smart Farming AI Assistant (స్మార్ట్ వ్యవసాయ సహాయకుడు)

An intelligent full-stack, AI and Machine Learning-powered digital farming assistant designed for Indian agriculture. Built with **FastAPI**, **SQLAlchemy**, **PostgreSQL / SQLite**, **Scikit-Learn**, **Computer Vision**, and **Google Gemini API / Open-Meteo**, supporting **English** and **Telugu (తెలుగు)**.

---

## 🌾 System Architecture

```text
                         SMART FARMING AI ASSISTANT
                                  |
              +-------------------+-------------------+
              |                                       |
          FRONTEND                                BACKEND
     Preserved Stitch UI                          FastAPI
              |                                       |
              |                         +-------------+-------------+
              |                         |             |             |
              |                     PostgreSQL     AI Services    ML Models
              |                         |             |             |
              |                         |        AI Chatbot      Crop ML (99.4%)
              |                         |        Weather API     Disease CV
              |                         |        Voice STT/TTS   Pest IPM
              |                         |
              +-------------------------+
                         REST APIs
```

---

## 🚀 Key Features

1. **Zero-Redesign Frontend Preservation**: Retains 100% of the original Stitch visual designs, Tailwind Emerald/Forest color schemes, Manrope/Hanken Grotesk typography, and responsive cards.
2. **Mobile Number OTP Authentication**: Real 6-digit OTP verification flow with country code validation (+91 for India), 60s cooldown, 5-minute expiry, and brute-force protection.
3. **ML Crop Recommendation**: Scikit-Learn Random Forest Classifier trained across 22 major Indian crops with **99.43% accuracy** on soil test inputs (N, P, K, pH, Rainfall, Temp, Humidity).
4. **Computer Vision Disease Detection**: Leaf image upload and camera viewfinder with AI diagnostic symptoms, ICAR treatment chemicals (e.g. Copper Oxychloride, Mancozeb), organic remedies, and prevention.
5. **Integrated Pest Management (IPM)**: Pest identification for Whiteflies, Bollworms, Stem Borers, and Aphids with pheromone trap dosages and biological control (NPV/Bt).
6. **Real-Time Weather & Alerts**: Hyper-local forecasts from Open-Meteo API with agricultural advisories that adjust irrigation recommendations.
7. **Smart Irrigation & NPK Fertilizer Engines**: Soil moisture calculation that postpones watering when rain probability exceeds 60%, plus balanced N-P-K deficiency analysis.
8. **Farming Calendar**: Auto-generated 130-day crop timeline from land prep, seed treatment, vegetative top-dressing, to harvest.
9. **Multilingual Voice & AI Chatbot**: Context-aware agronomist answering queries in English and authentic Telugu (వరి, పత్తి, తెగుళ్లు, ఎరువులు) with Web Speech Recognition and Audio TTS.

---

## 🛠️ Technology Stack

| Layer | Technologies |
|---|---|
| **Frontend** | HTML5, Tailwind CSS, Material Symbols, Web Speech API (STT/TTS), Vanilla JS Centralized API Client |
| **Backend** | Python 3.11+, FastAPI, Uvicorn, Pydantic v2, Python-Multipart |
| **Database** | PostgreSQL (Production) / SQLite (Zero-dependency local dev), SQLAlchemy 2.0 ORM |
| **Authentication** | Mobile SMS OTP (Twilio Verify & Mock Provider), JWT (HS256), Bcrypt |
| **Machine Learning** | Scikit-Learn (Random Forest), Pandas, NumPy, Joblib |
| **Computer Vision** | Pillow (PIL), Feature Histogram & Necrosis Signature Analysis |
| **External APIs** | Open-Meteo (Real Weather), Google Gemini AI API, Twilio Verify |

---

## 📁 Folder Structure

```text
Smart Farming/
├── backend/
│   ├── app/
│   │   ├── main.py                  # Master FastAPI App
│   │   ├── config.py                # Pydantic Settings
│   │   ├── database/
│   │   │   ├── connection.py        # SQLAlchemy Engine & Sessions
│   │   │   └── models.py            # 8 Database Entities
│   │   ├── schemas/                 # Pydantic Input/Output Schemas
│   │   ├── routers/                 # 12 Modular API Routers
│   │   │   ├── auth.py              # OTP, Login, Register, Me
│   │   │   ├── users.py             # Profile Management
│   │   │   ├── crops.py             # ML Crop Recommendation & Catalog
│   │   │   ├── disease.py           # Image Disease Detection
│   │   │   ├── pest.py              # Pest Identification
│   │   │   ├── weather.py           # Real Weather & Forecast
│   │   │   ├── fertilizer.py        # Fertilizer Recommendations
│   │   │   ├── irrigation.py        # Smart Irrigation
│   │   │   ├── calendar.py          # Crop Farming Calendar
│   │   │   ├── dashboard.py         # Aggregated Metrics
│   │   │   └── admin.py             # System Metrics
│   │   ├── services/                # Business Logic & Integrations
│   │   ├── ml/                      # ML Models & Training Scripts
│   │   └── auth/                    # JWT & Password Security
│   ├── tests/
│   │   └── test_all.py              # 15 Automated Pytest Suites
│   ├── requirements.txt
│   ├── .env.example
│   └── .env
├── frontend/
│   ├── index.html                   # Landing Page
│   ├── auth.html                    # Mobile OTP & Password Login
│   ├── setup.html                   # 3-Step Farm Setup Wizard
│   ├── dashboard.html               # Farmer Bento Grid Dashboard
│   ├── scanner.html                 # Leaf Scanner & Disease Detection
│   ├── assistant.html               # Multilingual AI Voice Assistant
│   ├── soil-irrigation.html         # Soil NPK & Smart Water Page
│   ├── weather-market.html          # Weather Forecast & Mandi Prices
│   └── js/
│       └── api.js                   # Centralized API Client
├── models/
│   ├── crop_recommendation.joblib   # Trained ML Model (99.43% acc)
│   └── crop_metadata.json
├── datasets/
│   └── crop_recommendation.csv
├── Dockerfile
├── docker-compose.yml
├── .gitignore
└── README.md
```

---

## ⚙️ Prerequisites

* Python 3.10 or higher
* Pip
* (Optional) Docker & Docker Compose
* (Optional) PostgreSQL

---

## 📦 Installation & Setup

### 1. Clone & Navigate
```bash
cd "c:/Users/muthi/OneDrive/JAVA PROGRAMING/Documents/Desktop/Smart Farming"
```

### 2. Install Dependencies
```bash
pip install -r backend/requirements.txt
```

### 3. Configure Environment Variables
Copy `.env.example` to `backend/.env`:
```env
ENVIRONMENT=development
PORT=8000
HOST=0.0.0.0
FRONTEND_URL=*
DATABASE_URL=sqlite:///./smart_farming.db
JWT_SECRET=super_secure_jwt_secret_key_2026
JWT_ALGORITHM=HS256
OTP_PROVIDER=mock
AI_PROVIDER=gemini
GEMINI_API_KEY=your_gemini_api_key_here
WEATHER_PROVIDER=openmeteo
```

### 4. Train/Verify ML Crop Model
```bash
python -m backend.app.ml.train_crop_model
```
*Output: Random Forest Crop Recommendation Model Test Accuracy: 99.43%*

---

## 🧪 Running Automated Tests

Run the comprehensive pytest test suite covering all authentication, OTP, ML, CV, Chatbot, Weather, and Irrigation modules:

```bash
python -m pytest backend/tests/test_all.py -v
```

All 15 test suites pass:
```text
backend/tests/test_all.py::test_health_check PASSED
backend/tests/test_all.py::test_otp_send_and_verify_flow PASSED
backend/tests/test_all.py::test_password_register_and_login PASSED
backend/tests/test_all.py::test_crop_recommendation_valid PASSED
backend/tests/test_all.py::test_crop_recommendation_invalid_input PASSED
backend/tests/test_all.py::test_disease_prediction_valid_image PASSED
backend/tests/test_all.py::test_disease_prediction_unsupported_file PASSED
backend/tests/test_all.py::test_pest_prediction PASSED
backend/tests/test_all.py::test_chatbot_english_query PASSED
backend/tests/test_all.py::test_chatbot_telugu_query PASSED
backend/tests/test_all.py::test_weather_current_and_forecast PASSED
backend/tests/test_all.py::test_fertilizer_recommendation PASSED
backend/tests/test_all.py::test_irrigation_recommendation PASSED
backend/tests/test_all.py::test_irrigation_suppression_on_rain PASSED
backend/tests/test_all.py::test_dashboard_aggregator PASSED
======================= 15 passed in 7.40s =======================
```

---

## 💻 Running the Application

### Start the FastAPI Backend Server
```bash
python -m uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload
```

* Backend API: `http://localhost:8000`
* Interactive Swagger Docs: `http://localhost:8000/docs`
* ReDoc Documentation: `http://localhost:8000/redoc`
* Frontend App: Access directly via browser by opening `frontend/index.html` or through `http://localhost:8000/frontend/index.html`

---

## 🐳 Docker Deployment

### Run with PostgreSQL and Backend in One Command:
```bash
docker-compose up --build -d
```

Check logs:
```bash
docker-compose logs -f backend
```

---

## 🚜 Complete Farmer Workflow Walkthrough

1. **Landing Page**: Open `frontend/index.html`.
2. **Mobile OTP Login**: Navigate to `frontend/auth.html`, enter your mobile number (e.g., `+919876543210`), click **Send OTP**, enter the 6-digit code, and log in securely.
3. **Farm Setup**: In `frontend/setup.html`, configure farm size, soil type, auto-detect GPS location, and select your primary crop.
4. **Dashboard**: View live weather, overall farm health (84/100), crop conditions (Tomato, Chilli, Rice), and quick actions.
5. **Crop Recommendation**: Click **Recommend Crop**, input your soil test values (N: 90, P: 42, K: 43, pH: 6.5, Rain: 200), and get instant Random Forest predictions with confidence scores.
6. **Disease Scanner**: In `frontend/scanner.html`, upload a leaf photo or use your camera to diagnose Early Blight with symptoms, treatments, and prevention guidelines.
7. **AI Voice Assistant**: In `frontend/assistant.html`, ask questions in English or Telugu ("నా వరి పంటకు ఏ ఎరువు ఉపయోగించాలి?"), use microphone voice input, and listen to spoken audio answers.
8. **Soil & Irrigation**: Check real-time water deficit calculations and NPK fertilizer guidelines.
