# FinVest | User Service | crud.py
# Member 1: User & KYC Profile management — all database operations

from sqlalchemy.orm import Session
from models import User
from schemas import UserCreate, UserUpdate, VALID_KYC_TRANSITIONS
import uuid
from datetime import datetime, timezone


def create_user(db: Session, user_data: UserCreate) -> User:
    """Register a new user with auto-generated UUID and timestamps."""
    now = datetime.now(timezone.utc).isoformat()
    db_user = User(
        id=str(uuid.uuid4()),
        full_name=user_data.full_name,
        email=user_data.email,
        phone_number=user_data.phone_number,
        national_id=user_data.national_id,
        date_of_birth=user_data.date_of_birth,
        risk_category=user_data.risk_category.value,
        kyc_status="Pending",
        is_active=True,
        created_at=now,
        updated_at=now,
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def get_user_by_id(db: Session, user_id: str) -> User | None:
    """Fetch a single user by UUID."""
    return db.query(User).filter(User.id == user_id).first()


def get_user_by_email(db: Session, email: str) -> User | None:
    """Fetch a single user by email address."""
    return db.query(User).filter(User.email == email.lower()).first()


def list_users(db: Session, skip: int = 0, limit: int = 100) -> tuple[list[User], int]:
    """Return paginated list of active users and total count."""
    query = db.query(User).filter(User.is_active == True)
    total = query.count()
    users = query.offset(skip).limit(limit).all()
    return users, total


def update_user(db: Session, user_id: str, update_data: UserUpdate) -> User | None:
    """Update profile fields (excluding KYC status and email)."""
    db_user = get_user_by_id(db, user_id)
    if not db_user:
        return None

    update_dict = update_data.model_dump(exclude_unset=True)
    # Convert enum to string if present
    if "risk_category" in update_dict and update_dict["risk_category"] is not None:
        update_dict["risk_category"] = update_dict["risk_category"].value

    for field, value in update_dict.items():
        setattr(db_user, field, value)

    db_user.updated_at = datetime.now(timezone.utc).isoformat()
    db.commit()
    db.refresh(db_user)
    return db_user


def update_kyc_status(db: Session, user_id: str, new_status: str) -> tuple[User | None, str | None]:
    """
    Update the KYC status with transition validation.
    Returns (user, error_message). error_message is None on success.
    """
    db_user = get_user_by_id(db, user_id)
    if not db_user:
        return None, "User not found"

    current = db_user.kyc_status
    allowed = VALID_KYC_TRANSITIONS.get(current, [])
    if new_status not in allowed:
        return db_user, f"Invalid KYC transition: '{current}' → '{new_status}'. Allowed: {allowed}"

    db_user.kyc_status = new_status
    db_user.updated_at = datetime.now(timezone.utc).isoformat()
    db.commit()
    db.refresh(db_user)
    return db_user, None


def soft_delete_user(db: Session, user_id: str) -> User | None:
    """Soft-delete: deactivate user and scrub PII fields."""
    db_user = get_user_by_id(db, user_id)
    if not db_user:
        return None

    db_user.is_active = False
    db_user.national_id = None
    db_user.date_of_birth = None
    db_user.updated_at = datetime.now(timezone.utc).isoformat()
    db.commit()
    db.refresh(db_user)
    return db_user

def hard_delete_user(db: Session, user_id: str) -> bool:
    """Hard-delete a user from the database. Returns True if deleted, False if not found."""
    db_user = get_user_by_id(db, user_id)
    if not db_user:
        return False

    db.delete(db_user)
    db.commit()
    return True