# FinVest | Asset Service | schemas.py
# Member 2: Platform Asset & Market Data — Pydantic v2 validation schemas

from pydantic import BaseModel, Field, field_validator
from typing import Optional
from enum import Enum


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
