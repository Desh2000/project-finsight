# FinVest | Analytics Service | schemas.py
# Member 4: Savings Goal & Portfolio Analytics — Pydantic v2 validation schemas

from pydantic import BaseModel, Field, field_validator
from typing import Optional
from enum import Enum


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
