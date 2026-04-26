# FinVest | User Service | schemas.py
# Member 1: User & KYC Profile management — Pydantic v2 validation schemas

from pydantic import BaseModel, Field, field_validator
from typing import Optional
from enum import Enum
import re


class RiskCategory(str, Enum):
    """Allowed risk categories for investor profiles."""
    CONSERVATIVE = "Conservative"
    MODERATE = "Moderate"
    AGGRESSIVE = "Aggressive"


class KYCStatus(str, Enum):
    """Allowed KYC verification statuses."""
    PENDING = "Pending"
    UNDER_REVIEW = "Under Review"
    VERIFIED = "Verified"
    REJECTED = "Rejected"


# ── Investment thresholds per risk category (in USD) ──
RISK_THRESHOLDS = {
    "Conservative": 1000.0,
    "Moderate": 10000.0,
    "Aggressive": float("inf"),
}

# ── Allowed KYC status transitions ──
VALID_KYC_TRANSITIONS = {
    "Pending": ["Under Review"],
    "Under Review": ["Verified", "Rejected"],
    "Verified": [],
    "Rejected": [],
}


class UserCreate(BaseModel):
    """Schema for creating / registering a new user."""
    full_name: str = Field(..., min_length=1, max_length=200)
    email: str = Field(..., max_length=254)
    phone_number: Optional[str] = None
    national_id: Optional[str] = None
    date_of_birth: Optional[str] = None
    risk_category: RiskCategory = RiskCategory.MODERATE

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: str) -> str:
        pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
        if not re.match(pattern, v):
            raise ValueError("Invalid email format")
        return v.lower()

    @field_validator("phone_number")
    @classmethod
    def validate_phone(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            digits = re.sub(r"[^\d]", "", v)
            if len(digits) < 10 or len(digits) > 15:
                raise ValueError("Phone number must be 10–15 digits")
        return v

    @field_validator("national_id")
    @classmethod
    def validate_national_id(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            if not re.match(r"^[a-zA-Z0-9]{9,12}$", v):
                raise ValueError("National ID must be 9–12 alphanumeric characters")
        return v

    @field_validator("date_of_birth")
    @classmethod
    def validate_dob(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
          from datetime import date

        try:
            dob = date.fromisoformat(v)  # use date
        except ValueError:
            raise ValueError("date_of_birth must be a valid ISO date (YYYY-MM-DD)")

        if dob >= date.today():
            raise ValueError("date_of_birth must be in the past")

        return v


class UserUpdate(BaseModel):
    """Schema for updating an existing user profile (all fields optional)."""
    full_name: Optional[str] = None
    phone_number: Optional[str] = None
    national_id: Optional[str] = None
    date_of_birth: Optional[str] = None
    risk_category: Optional[RiskCategory] = None

    @field_validator("phone_number")
    @classmethod
    def validate_phone(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            digits = re.sub(r"[^\d]", "", v)
            if len(digits) < 10 or len(digits) > 15:
                raise ValueError("Phone number must be 10–15 digits")
        return v

    @field_validator("national_id")
    @classmethod
    def validate_national_id(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            if not re.match(r"^[a-zA-Z0-9]{9,12}$", v):
                raise ValueError("National ID must be 9–12 alphanumeric characters")
        return v


class KYCUpdate(BaseModel):
    """Schema for updating only the KYC status of a user."""
    kyc_status: KYCStatus


class UserResponse(BaseModel):
    """Schema returned for a single user."""
    id: str
    full_name: str
    email: str
    phone_number: Optional[str] = None
    national_id: Optional[str] = None
    date_of_birth: Optional[str] = None
    risk_category: str
    kyc_status: str
    is_active: bool
    created_at: str
    updated_at: str

    model_config = {"from_attributes": True}


class UserListResponse(BaseModel):
    """Schema for paginated user list."""
    users: list[UserResponse]
    total: int
