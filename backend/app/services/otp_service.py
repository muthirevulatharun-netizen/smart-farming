import time
import random
import re
from typing import Tuple, Optional, Dict
import httpx
from backend.app.config import settings

# In-memory store for OTPs (in production, use Redis or DB)
# Structure: phone -> {"otp": "123456", "expires_at": float, "last_sent_at": float, "attempts": int}
_otp_store: Dict[str, dict] = {}

class OTPService:
    COOLDOWN_SECONDS = 60
    EXPIRY_SECONDS = 300  # 5 minutes
    MAX_ATTEMPTS = 3

    @staticmethod
    def normalize_phone(phone: str) -> str:
        """Normalize phone number to international format, defaulting to India +91 if needed."""
        cleaned = re.sub(r"[^\d+]", "", phone)
        if not cleaned.startswith("+"):
            if len(cleaned) == 10:
                cleaned = "+91" + cleaned
            elif cleaned.startswith("91") and len(cleaned) == 12:
                cleaned = "+" + cleaned
            else:
                cleaned = "+" + cleaned
        return cleaned

    @staticmethod
    def validate_phone(phone: str) -> bool:
        """Validate phone format."""
        pattern = r"^\+91[6-9]\d{9}$|^\+[1-9]\d{1,14}$"
        return bool(re.match(pattern, phone))

    @classmethod
    def send_otp(cls, raw_phone: str) -> Tuple[bool, str, Optional[str]]:
        """
        Send a 6-digit OTP to the specified phone number.
        Returns: (success, message, dev_otp)
        """
        phone = cls.normalize_phone(raw_phone)
        if not cls.validate_phone(phone):
            return False, "Invalid mobile number format. Please provide a valid 10-digit number.", None

        now = time.time()
        record = _otp_store.get(phone)

        # Check resend cooldown
        if record and (now - record.get("last_sent_at", 0) < cls.COOLDOWN_SECONDS):
            remaining = int(cls.COOLDOWN_SECONDS - (now - record["last_sent_at"]))
            return False, f"Please wait {remaining} seconds before requesting another OTP.", None

        # Generate 6-digit OTP
        otp = f"{random.randint(100000, 999999)}"

        if settings.OTP_PROVIDER.lower() == "twilio" and settings.TWILIO_ACCOUNT_SID and settings.TWILIO_AUTH_TOKEN:
            try:
                # Use Twilio Verify API
                url = f"https://verify.twilio.com/v2/Services/{settings.TWILIO_VERIFY_SERVICE_SID}/Verifications"
                auth = (settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
                data = {"To": phone, "Channel": "sms"}
                with httpx.Client(timeout=10) as client:
                    resp = client.post(url, auth=auth, data=data)
                    if resp.status_code in (200, 201):
                        _otp_store[phone] = {
                            "otp": None,  # Twilio stores and verifies it
                            "expires_at": now + cls.EXPIRY_SECONDS,
                            "last_sent_at": now,
                            "attempts": 0,
                            "provider": "twilio"
                        }
                        return True, f"OTP sent via SMS to {phone}.", None
                    else:
                        # Fallback if Twilio fails
                        pass
            except Exception as e:
                # Log and fallback to mock in non-prod
                if settings.ENVIRONMENT == "production":
                    return False, "SMS provider temporarily unavailable. Please try again.", None

        # Development / Mock Provider
        _otp_store[phone] = {
            "otp": otp,
            "expires_at": now + cls.EXPIRY_SECONDS,
            "last_sent_at": now,
            "attempts": 0,
            "provider": "mock"
        }

        dev_otp_value = otp if settings.ENVIRONMENT != "production" else None
        return True, f"OTP sent to {phone} successfully.", dev_otp_value

    @classmethod
    def verify_otp(cls, raw_phone: str, entered_otp: str) -> Tuple[bool, str]:
        """
        Verify the OTP entered by user.
        Returns: (success, message)
        """
        phone = cls.normalize_phone(raw_phone)
        record = _otp_store.get(phone)

        if not record:
            return False, "No OTP request found for this mobile number. Please request a new OTP."

        now = time.time()
        if now > record["expires_at"]:
            del _otp_store[phone]
            return False, "OTP has expired. Please request a new one."

        if record["attempts"] >= cls.MAX_ATTEMPTS:
            del _otp_store[phone]
            return False, "Maximum verification attempts exceeded. Please request a new OTP."

        record["attempts"] += 1

        # If Twilio Verify was used
        if record.get("provider") == "twilio":
            try:
                url = f"https://verify.twilio.com/v2/Services/{settings.TWILIO_VERIFY_SERVICE_SID}/VerificationCheck"
                auth = (settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
                data = {"To": phone, "Code": entered_otp}
                with httpx.Client(timeout=10) as client:
                    resp = client.post(url, auth=auth, data=data)
                    result = resp.json()
                    if result.get("status") == "approved":
                        del _otp_store[phone]
                        return True, "Verification successful."
                    else:
                        remaining = cls.MAX_ATTEMPTS - record["attempts"]
                        return False, f"Incorrect OTP. {remaining} attempt(s) remaining."
            except Exception:
                return False, "Verification service error. Please try again."

        # Mock / Local Verification
        if record["otp"] == entered_otp.strip():
            del _otp_store[phone]
            return True, "Verification successful."
        else:
            remaining = cls.MAX_ATTEMPTS - record["attempts"]
            return False, f"Incorrect OTP. {remaining} attempt(s) remaining."

otp_service = OTPService()
