# FinVest | Transaction Service | models.py
# Member 3: Transaction & Order management — SQLAlchemy ORM models

from sqlalchemy import Column, String, Float
from database import Base
import uuid
from datetime import datetime, timezone


class Transaction(Base):
    """SQLAlchemy model representing a buy/sell order."""
    __tablename__ = "transactions"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, nullable=False)
    asset_id = Column(String, nullable=False)
    asset_ticker = Column(String, nullable=False)  # Denormalized for display
    order_type = Column(String, nullable=False)  # Buy, Sell
    quantity = Column(Float, nullable=False)
    price_at_order = Column(Float, nullable=False)
    total_value_usd = Column(Float, nullable=False)  # quantity * price_at_order
    status = Column(String, default="Pending")  # Pending, Completed, Failed, Cancelled
    notes = Column(String, nullable=True)
    created_at = Column(String, default=lambda: datetime.now(timezone.utc).isoformat())
    updated_at = Column(String, default=lambda: datetime.now(timezone.utc).isoformat(),
                        onupdate=lambda: datetime.now(timezone.utc).isoformat())
