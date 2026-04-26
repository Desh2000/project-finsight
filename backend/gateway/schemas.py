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


class OrderType(str, Enum):
    BUY = "Buy"
    SELL = "Sell"


class TransactionStatus(str, Enum):
    PENDING = "Pending"
    COMPLETED = "Completed"
    FAILED = "Failed"
    CANCELLED = "Cancelled"


# ── Valid status transitions ──
VALID_STATUS_TRANSITIONS = {
    "Pending": ["Completed", "Failed", "Cancelled"],
    "Completed": [],
    "Failed": [],
    "Cancelled": [],
}


class TransactionCreate(BaseModel):
    """Schema for placing a new buy/sell order."""
    user_id: str = Field(..., min_length=1)
    asset_id: str = Field(..., min_length=1)
    asset_ticker: str = Field(..., min_length=1)
    order_type: OrderType
    quantity: float = Field(..., gt=0, description="Number of units (can be fractional)")
    price_at_order: float = Field(..., gt=0, description="USD price at time of order")
    notes: Optional[str] = None

    @field_validator("asset_ticker")
    @classmethod
    def ticker_uppercase(cls, v: str) -> str:
        return v.upper()


class TransactionStatusUpdate(BaseModel):
    """Schema for updating the order status."""
    status: TransactionStatus


class TransactionResponse(BaseModel):
    """Schema for a single transaction."""
    id: str
    user_id: str
    asset_id: str
    asset_ticker: str
    order_type: str
    quantity: float
    price_at_order: float
    total_value_usd: float
    status: str
    notes: Optional[str] = None
    created_at: str
    updated_at: str

    model_config = {"from_attributes": True}


class TransactionListResponse(BaseModel):
    """Schema for transaction list."""
    transactions: list[TransactionResponse]
    total: int


class AssetSummary(BaseModel):
    """Per-asset summary in a user's portfolio."""
    ticker: str
    net_quantity: float
    total_spent_usd: float


class TransactionSummaryResponse(BaseModel):
    """Summary of a user's transaction history."""
    user_id: str
    total_invested_usd: float
    total_withdrawn_usd: float
    net_position_usd: float
    completed_orders: int
    pending_orders: int
    by_asset: list[AssetSummary]

class AssetType(str, Enum):
    CRYPTO = "Crypto"
    STOCK = "Stock"


class RiskRating(str, Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"


class AssetCreate(BaseModel):
    """Schema for adding a new asset to the platform."""
    ticker: str = Field(..., min_length=1, max_length=10)
    name: str = Field(..., min_length=1, max_length=200)
    asset_type: AssetType = AssetType.CRYPTO
    coingecko_id: Optional[str] = None
    description: Optional[str] = None
    risk_rating: RiskRating = RiskRating.HIGH

    @field_validator("ticker")
    @classmethod
    def ticker_uppercase(cls, v: str) -> str:
        if v != v.upper():
            raise ValueError("Ticker must be uppercase (e.g., 'BTC', 'ETH')")
        return v


class AssetUpdate(BaseModel):
    """Schema for updating asset metadata (all fields optional)."""
    name: Optional[str] = None
    description: Optional[str] = None
    risk_rating: Optional[RiskRating] = None
    coingecko_id: Optional[str] = None
    asset_type: Optional[AssetType] = None


class TradeableToggle(BaseModel):
    """Schema for toggling the tradeable status."""
    is_tradeable: bool


class AssetResponse(BaseModel):
    """Schema for a single asset (database fields only)."""
    id: str
    ticker: str
    name: str
    asset_type: str
    coingecko_id: Optional[str] = None
    description: Optional[str] = None
    risk_rating: str
    is_tradeable: bool
    created_at: str
    updated_at: str

    model_config = {"from_attributes": True}


class AssetEnrichedResponse(BaseModel):
    """Schema for an asset enriched with live market price data."""
    id: str
    ticker: str
    name: str
    asset_type: str
    risk_rating: str
    is_tradeable: bool
    live_price_usd: Optional[float] = None
    stale_data: bool = False
    last_updated: str

    model_config = {"from_attributes": True}


class AssetListResponse(BaseModel):
    """Schema for the enriched asset list endpoint."""
    assets: list[AssetEnrichedResponse]
    total: int


class CurrencyDisplay(str, Enum):
    USD = "USD"
    LKR = "LKR"


class GoalStatus(str, Enum):
    ACTIVE = "Active"
    COMPLETED = "Completed"
    ABANDONED = "Abandoned"


class GoalCreate(BaseModel):
    """Schema for creating a new savings goal."""
    user_id: str = Field(..., min_length=1)
    goal_name: str = Field(..., min_length=1, max_length=200)
    target_amount_usd: float = Field(..., gt=0)
    target_date: str = Field(..., description="ISO date in the future (YYYY-MM-DD)")
    currency_display: CurrencyDisplay = CurrencyDisplay.LKR

    @field_validator("target_date")
    @classmethod
    def validate_future_date(cls, v: str) -> str:
        from datetime import datetime, timezone
        try:
            target = datetime.fromisoformat(v)
        except ValueError:
            raise ValueError("target_date must be a valid ISO date (YYYY-MM-DD)")
        if target.date() <= datetime.now(timezone.utc).date():
            raise ValueError("target_date must be in the future")
        return v


class GoalUpdate(BaseModel):
    """Schema for updating a savings goal (all fields optional)."""
    goal_name: Optional[str] = None
    target_amount_usd: Optional[float] = Field(None, gt=0)
    target_date: Optional[str] = None
    currency_display: Optional[CurrencyDisplay] = None


class DepositRequest(BaseModel):
    """Schema for depositing money into a savings goal."""
    amount: float = Field(..., gt=0, description="Amount in USD to add to the goal")


class GoalResponse(BaseModel):
    """Schema for a single savings goal."""
    id: str
    user_id: str
    goal_name: str
    target_amount_usd: float
    current_amount_usd: float
    target_date: str
    currency_display: str
    status: str
    created_at: str
    updated_at: str

    model_config = {"from_attributes": True}


class GoalEnrichedResponse(BaseModel):
    """Schema for a goal enriched with LKR values and completion data."""
    id: str
    goal_name: str
    target_amount_usd: float
    current_amount_usd: float
    completion_percentage: float
    target_amount_lkr: float
    current_amount_lkr: float
    days_remaining: int
    status: str


class GoalListResponse(BaseModel):
    """Schema for the goals list."""
    goals: list[GoalResponse]
    total: int


class PortfolioResponse(BaseModel):
    """Schema for the portfolio analytics endpoint."""
    user_id: str
    total_goal_value_usd: float
    total_goal_value_lkr: float
    exchange_rate: float
    fallback_rate: bool
    rate_timestamp: str
    active_goals: int
    completed_goals: int
    abandoned_goals: int
    goals: list[GoalEnrichedResponse]


class GoalPredictionResponse(BaseModel):
    """Schema returned by the ML risk-prediction endpoint."""
    goal_id: str
    goal_name: str
    goal_status: str
    # ── ML outputs ──
    risk_label: str                  # "on_track" | "at_risk" | "critical"
    risk_probability: float          # confidence for the predicted label
    on_track_probability: float
    at_risk_probability: float
    critical_probability: float
    # ── Deposit recommendations ──
    required_daily_usd: float
    required_weekly_usd: float
    required_monthly_usd: float
    # ── Human-readable insight ──
    smart_insight: str
    days_remaining: int
    save_efficiency: float           # actual save pace / ideal save pace