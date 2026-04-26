# FinVest | User Service | router.py
# Member 1: User & KYC Profile management — FastAPI route definitions

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from database import get_db
from schemas import (
    UserCreate, UserUpdate, KYCUpdate,
    UserResponse, UserListResponse,
)
import crud

router = APIRouter(prefix="/api/users", tags=["Users"])


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=201,
    summary="Register a new user",
    description="Create a new investor account with auto-generated UUID and Pending KYC status.",
)
def register_user(user_data: UserCreate, db: Session = Depends(get_db)):
    # Check for duplicate email
    existing = crud.get_user_by_email(db, user_data.email)
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    return crud.create_user(db, user_data)


@router.get(
    "/",
    response_model=UserListResponse,
    summary="List all active users",
    description="Returns a paginated list of all active (non-deleted) users.",
)
def list_users(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=500, description="Maximum records to return"),
    db: Session = Depends(get_db),
):
    users, total = crud.list_users(db, skip=skip, limit=limit)
    return {"users": users, "total": total}


@router.get(
    "/{user_id}",
    response_model=UserResponse,
    summary="Get user profile",
    description="Fetch a single user's full profile by UUID. Returns 404 if not found.",
)
def get_user(user_id: str, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_id(db, user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user


@router.put(
    "/{user_id}",
    response_model=UserResponse,
    summary="Update user profile",
    description="Update profile fields such as full_name, phone_number, risk_category, etc.",
)
def update_user(user_id: str, update_data: UserUpdate, db: Session = Depends(get_db)):
    db_user = crud.update_user(db, user_id, update_data)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user


@router.patch(
    "/{user_id}/kyc",
    response_model=UserResponse,
    summary="Update KYC status",
    description=(
        "Update ONLY the KYC verification status. "
        "Valid transitions: Pending→Under Review→Verified or Rejected."
    ),
)
def update_kyc(user_id: str, kyc_data: KYCUpdate, db: Session = Depends(get_db)):
    db_user, error = crud.update_kyc_status(db, user_id, kyc_data.kyc_status.value)
    if error and db_user is None:
        raise HTTPException(status_code=404, detail=error)
    if error:
        raise HTTPException(status_code=400, detail=error)
    return db_user


@router.delete(
    "/{user_id}",
    status_code=200,
    summary="Soft-delete a user",
    description="Deactivate the user account and scrub PII (national_id, date_of_birth).",
)
def delete_user(user_id: str, db: Session = Depends(get_db)):
    db_user = crud.soft_delete_user(db, user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    return {"message": f"User has been deactivated."}

@router.delete(
    "/{user_id}/remove",
    status_code=200,
    summary="Hard-delete a user",
    description="Permanently delete the user account from the database.",
)
def hard_delete_user(user_id: str, db: Session = Depends(get_db)):
    success = crud.hard_delete_user(db, user_id)
    if not success:
        raise HTTPException(status_code=404, detail="User not found")
    return {"message": "User has been permanently deleted."}