# FinVest | Analytics Service | models.py
# Member 4: Savings Goal & Portfolio Analytics — SQLAlchemy ORM models

from sqlalchemy import Column, String, Float
from database import Base
import uuid
from datetime import datetime, timezone


class SavingsGoal(Base):
    """SQLAlchemy model representing a user's savings / investment goal."""
    __tablename__ = "savings_goals"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, nullable=False)
    goal_name = Column(String, nullable=False)
    target_amount_usd = Column(Float, nullable=False)
    current_amount_usd = Column(Float, default=0.0)
    target_date = Column(String, nullable=False)  # ISO date
    currency_display = Column(String, default="LKR")  # USD or LKR
    status = Column(String, default="Active")  # Active, Completed, Abandoned
    created_at = Column(String, default=lambda: datetime.now(timezone.utc).isoformat())
    updated_at = Column(String, default=lambda: datetime.now(timezone.utc).isoformat(),
                        onupdate=lambda: datetime.now(timezone.utc).isoformat())
