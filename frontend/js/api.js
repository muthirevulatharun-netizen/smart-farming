/**
 * Smart Farming AI Assistant - Centralized API Client
 * Manages authentication tokens, base URLs, error handling, and all backend API calls.
 */

// API base URL resolution order:
// 1. window.__API_URL__ (set in HTML or injected by host)
// 2. VITE_API_URL / NEXT_PUBLIC_API_URL (if replaced at build time)
// 3. Production Render backend (default)
// 4. Fallback to localhost for local dev
const API_BASE_URL = window.__API_URL__ || window.__VITE_API_URL__ || window.__NEXT_PUBLIC_API_URL__ || "https://smart-farming-710v.onrender.com";

const ApiClient = {
    getToken() {
        return localStorage.getItem("smart_farming_token");
    },

    setSession(token, user) {
        localStorage.setItem("smart_farming_token", token);
        if (user) {
            localStorage.setItem("smart_farming_user", JSON.stringify(user));
        }
    },

    getUser() {
        const user = localStorage.getItem("smart_farming_user");
        try {
            return user ? JSON.parse(user) : null;
        } catch (e) {
            return null;
        }
    },

    clearSession() {
        localStorage.removeItem("smart_farming_token");
        localStorage.removeItem("smart_farming_user");
    },

    async request(endpoint, options = {}) {
        const headers = options.headers || {};
        const token = this.getToken();
        if (token) {
            headers["Authorization"] = `Bearer ${token}`;
        }

        if (!(options.body instanceof FormData) && !headers["Content-Type"]) {
            headers["Content-Type"] = "application/json";
        }

        const config = {
            ...options,
            headers
        };

        try {
            const url = endpoint.startsWith("http") ? endpoint : `${API_BASE_URL}${endpoint}`;
            const response = await fetch(url, config);
            const data = await response.json().catch(() => ({}));

            if (!response.ok) {
                const message = data.detail || data.message || "An error occurred while processing the request.";
                throw new Error(message);
            }

            return data;
        } catch (error) {
            console.error(`API Error [${endpoint}]:`, error);
            throw error;
        }
    },

    // 1. Authentication
    auth: {
        async sendOTP(phone) {
            return ApiClient.request("/api/auth/otp/send", {
                method: "POST",
                body: JSON.stringify({ phone })
            });
        },

        async verifyOTP(phone, otp, name = null) {
            const res = await ApiClient.request("/api/auth/otp/verify", {
                method: "POST",
                body: JSON.stringify({ phone, otp, name })
            });
            if (res.access_token) {
                ApiClient.setSession(res.access_token, res.user);
            }
            return res;
        },

        async resendOTP(phone) {
            return ApiClient.request("/api/auth/otp/resend", {
                method: "POST",
                body: JSON.stringify({ phone })
            });
        },

        async login(identifier, password) {
            const res = await ApiClient.request("/api/auth/login", {
                method: "POST",
                body: JSON.stringify({ identifier, password })
            });
            if (res.access_token) {
                ApiClient.setSession(res.access_token, res.user);
            }
            return res;
        },

        async register(data) {
            const res = await ApiClient.request("/api/auth/register", {
                method: "POST",
                body: JSON.stringify(data)
            });
            if (res.access_token) {
                ApiClient.setSession(res.access_token, res.user);
            }
            return res;
        },

        async logout() {
            try {
                await ApiClient.request("/api/auth/logout", { method: "POST" });
            } catch (e) {}
            ApiClient.clearSession();
            window.location.href = "auth.html";
        },

        async getMe() {
            return ApiClient.request("/api/auth/me");
        }
    },

    // 2. Dashboard
    dashboard: {
        async getSummary() {
            return ApiClient.request("/api/dashboard");
        }
    },

    // 3. Crop Recommendation & Info
    crops: {
        async recommend(data) {
            return ApiClient.request("/api/crop/recommend", {
                method: "POST",
                body: JSON.stringify(data)
            });
        },

        async getAll() {
            return ApiClient.request("/api/crop/all");
        },

        async getById(id) {
            return ApiClient.request(`/api/crop/${id}`);
        }
    },

    // 4. Disease Detection
    disease: {
        async predict(file, cropHint = null) {
            const formData = new FormData();
            formData.append("file", file);
            if (cropHint) {
                formData.append("crop_hint", cropHint);
            }
            return ApiClient.request("/api/disease/predict", {
                method: "POST",
                body: formData
            });
        }
    },

    // 5. Pest Identification
    pest: {
        async predict(pestHint = null, cropHint = null, file = null) {
            const formData = new FormData();
            if (pestHint) formData.append("pest_hint", pestHint);
            if (cropHint) formData.append("crop_hint", cropHint);
            if (file) formData.append("file", file);
            return ApiClient.request("/api/pest/predict", {
                method: "POST",
                body: formData
            });
        }
    },

    // 6. AI Chatbot
    chat: {
        async send(message, crop = null, language = "en", context = null) {
            return ApiClient.request("/api/chat", {
                method: "POST",
                body: JSON.stringify({ message, crop, language, context })
            });
        },

        async getHistory() {
            return ApiClient.request("/api/chat/history");
        }
    },

    // 7. Weather
    weather: {
        async getCurrent(lat = null, lon = null, location = null) {
            let q = [];
            if (lat !== null) q.push(`lat=${lat}`);
            if (lon !== null) q.push(`lon=${lon}`);
            if (location) q.push(`location=${encodeURIComponent(location)}`);
            const qs = q.length ? `?${q.join("&")}` : "";
            return ApiClient.request(`/api/weather/current${qs}`);
        },

        async getForecast(lat = null, lon = null, location = null) {
            let q = [];
            if (lat !== null) q.push(`lat=${lat}`);
            if (lon !== null) q.push(`lon=${lon}`);
            if (location) q.push(`location=${encodeURIComponent(location)}`);
            const qs = q.length ? `?${q.join("&")}` : "";
            return ApiClient.request(`/api/weather/forecast${qs}`);
        }
    },

    // 8. Fertilizer
    fertilizer: {
        async recommend(data) {
            return ApiClient.request("/api/fertilizer/recommend", {
                method: "POST",
                body: JSON.stringify(data)
            });
        }
    },

    // 9. Smart Irrigation
    irrigation: {
        async recommend(data) {
            return ApiClient.request("/api/irrigation/recommend", {
                method: "POST",
                body: JSON.stringify(data)
            });
        }
    },

    // 10. Farming Calendar
    calendar: {
        async get() {
            return ApiClient.request("/api/calendar");
        },

        async create(data) {
            return ApiClient.request("/api/calendar/create", {
                method: "POST",
                body: JSON.stringify(data)
            });
        }
    },

    // 11. Profile
    profile: {
        async get() {
            return ApiClient.request("/api/profile");
        },

        async update(data) {
            return ApiClient.request("/api/profile", {
                method: "PUT",
                body: JSON.stringify(data)
            });
        }
    }
};

window.ApiClient = ApiClient;
