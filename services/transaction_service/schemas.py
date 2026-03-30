# FinVest | Transaction Service | schemas.py
# Member 3: Transaction & Order management — Pydantic v2 validation schemas

from pydantic import BaseModel, Field, field_validator
from typing import Optional
from enum import Enum


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
