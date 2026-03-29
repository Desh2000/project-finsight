# FinVest | Asset Service | models.py
# Member 2: Platform Asset & Market Data — SQLAlchemy ORM models

from sqlalchemy import Column, String, Boolean
from database import Base
import uuid
from datetime import datetime, timezone


class Asset(Base):
    """SQLAlchemy model representing an investable asset on the platform."""
    __tablename__ = "assets"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    ticker = Column(String, unique=True, nullable=False)
    name = Column(String, nullable=False)
    asset_type = Column(String, default="Crypto")  # Crypto, Stock
    coingecko_id = Column(String, nullable=True)
    description = Column(String, nullable=True)
    risk_rating = Column(String, default="High")  # Low, Medium, High
    is_tradeable = Column(Boolean, default=True)
    created_at = Column(String, default=lambda: datetime.now(timezone.utc).isoformat())
    updated_at = Column(String, default=lambda: datetime.now(timezone.utc).isoformat(),
                        onupdate=lambda: datetime.now(timezone.utc).isoformat())
