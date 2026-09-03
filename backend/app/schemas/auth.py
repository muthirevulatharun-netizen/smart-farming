from typing import Optional, Any
from pydantic import BaseModel, Field

class SendOTPRequest(BaseModel):
    phone: str = Field(..., description="Mobile number with country code, e.g., +919876543210")

class VerifyOTPRequest(BaseModel):
    phone: str = Field(..., description="Mobile number with country code")
    otp: str = Field(..., min_length=4, max_length=6, description="OTP code")
    name: Optional[str] = Field(None, description="Optional name for new registrations")

class ResendOTPRequest(BaseModel):
    phone: str = Field(...)

class RegisterRequest(BaseModel):
    phone: str
    name: str
    email: Optional[str] = None
    password: str = Field(..., min_length=6)
    preferred_language: Optional[str] = "en"

class LoginRequest(BaseModel):
    identifier: str = Field(..., description="Phone number or email")
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: dict

class OTPResponse(BaseModel):
    success: bool
    message: str
    dev_otp: Optional[str] = None
    resend_in_seconds: int = 60
