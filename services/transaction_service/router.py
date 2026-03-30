# FinVest | Transaction Service | router.py
# Member 3: Transaction & Order management — FastAPI route definitions

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from database import get_db
from schemas import (
    TransactionCreate, TransactionStatusUpdate,
    TransactionResponse, TransactionListResponse, TransactionSummaryResponse,
)
import crud

router = APIRouter(prefix="/api/transactions", tags=["Transactions"])


@router.post(
    "/",
    response_model=TransactionResponse,
    status_code=201,
    summary="Place a new order",
    description="Create a new Buy/Sell order. Status is auto-set to Pending and total_value_usd is computed.",
)
def create_transaction(txn_data: TransactionCreate, db: Session = Depends(get_db)):
    db_txn, error = crud.create_transaction(db, txn_data)
    if error:
        raise HTTPException(status_code=400, detail=error)
    return db_txn


@router.get(
    "/",
    response_model=TransactionListResponse,
    summary="List all transactions",
    description="Returns all transactions with optional filters for user_id, asset_ticker, status, order_type.",
)
def list_transactions(
    user_id: str | None = Query(None),
    asset_ticker: str | None = Query(None),
    status: str | None = Query(None),
    order_type: str | None = Query(None),
    db: Session = Depends(get_db),
):
    txns = crud.list_transactions(db, user_id=user_id, asset_ticker=asset_ticker, status=status, order_type=order_type)
    return {"transactions": txns, "total": len(txns)}


@router.get(
    "/summary/{user_id}",
    response_model=TransactionSummaryResponse,
    summary="User transaction summary",
    description="Returns an aggregated summary of all transactions for a specific user.",
)
def get_user_summary(user_id: str, db: Session = Depends(get_db)):
    return crud.get_user_summary(db, user_id)


@router.get(
    "/user/{user_id}",
    response_model=TransactionListResponse,
    summary="User transaction history",
    description="All transactions for a specific user, sorted by created_at descending.",
)
def get_user_transactions(user_id: str, db: Session = Depends(get_db)):
    txns = crud.get_user_transactions(db, user_id)
    return {"transactions": txns, "total": len(txns)}


@router.get(
    "/{txn_id}",
    response_model=TransactionResponse,
    summary="Get transaction receipt",
    description="Fetch a single transaction by UUID.",
)
def get_transaction(txn_id: str, db: Session = Depends(get_db)):
    db_txn = crud.get_transaction_by_id(db, txn_id)
    if not db_txn:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return db_txn


@router.patch(
    "/{txn_id}/status",
    response_model=TransactionResponse,
    summary="Update order status",
    description="Update the status of a transaction. Validates lifecycle rules (e.g., Completed/Cancelled cannot be updated).",
)
def update_status(txn_id: str, status_data: TransactionStatusUpdate, db: Session = Depends(get_db)):
    db_txn, error = crud.update_transaction_status(db, txn_id, status_data.status.value)
    if error and db_txn is None:
        raise HTTPException(status_code=404, detail=error)
    if error:
        raise HTTPException(status_code=400, detail=error)
    return db_txn


@router.delete(
    "/{txn_id}",
    response_model=TransactionResponse,
    summary="Cancel a pending order",
    description="Cancel a Pending order (sets status to Cancelled). Returns 409 if the order is not Pending.",
)
def cancel_transaction(txn_id: str, db: Session = Depends(get_db)):
    db_txn, error = crud.cancel_transaction(db, txn_id)
    if error and db_txn is None:
        raise HTTPException(status_code=404, detail=error)
    if error:
        raise HTTPException(status_code=409, detail=error)
    return db_txn
