# FinVest | User Service | models.py
# Member 1: User & KYC Profile management — SQLAlchemy ORM models

from sqlalchemy import Column, String, Boolean
from database import Base
import uuid
from datetime import datetime, timezone


class User(Base):
    """SQLAlchemy model representing a user / investor account."""
    __tablename__ = "users"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    full_name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    phone_number = Column(String, nullable=True)
    national_id = Column(String, nullable=True)
    date_of_birth = Column(String, nullable=True)
    risk_category = Column(String, default="Moderate")  # Conservative, Moderate, Aggressive
    kyc_status = Column(String, default="Pending")  # Pending, Under Review, Verified, Rejected
    is_active = Column(Boolean, default=True)
    created_at = Column(String, default=lambda: datetime.now(timezone.utc).isoformat())
    updated_at = Column(String, default=lambda: datetime.now(timezone.utc).isoformat(),
                        onupdate=lambda: datetime.now(timezone.utc).isoformat())
