# FinVest | Transaction Service | crud.py
# Member 3: Transaction & Order management — all database operations

from sqlalchemy.orm import Session
from sqlalchemy import func
from models import Transaction
from schemas import TransactionCreate, VALID_STATUS_TRANSITIONS
import uuid
from datetime import datetime, timezone


def create_transaction(db: Session, txn_data: TransactionCreate) -> tuple[Transaction | None, str | None]:
    """
    Place a new order. Auto-computes total_value_usd.
    For Sell orders, verifies the user has sufficient holdings.
    Returns (transaction, error_message).
    """
    # For Sell orders, check that user has sufficient completed buy quantity
    if txn_data.order_type.value == "Sell":
        net_qty = _get_net_quantity(db, txn_data.user_id, txn_data.asset_ticker)
        if net_qty < txn_data.quantity:
            return None, (
                f"Insufficient holdings: you own {net_qty:.6f} {txn_data.asset_ticker} "
                f"but tried to sell {txn_data.quantity:.6f}"
            )

    now = datetime.now(timezone.utc).isoformat()
    total_value = round(txn_data.quantity * txn_data.price_at_order, 2)

    db_txn = Transaction(
        id=str(uuid.uuid4()),
        user_id=txn_data.user_id,
        asset_id=txn_data.asset_id,
        asset_ticker=txn_data.asset_ticker.upper(),
        order_type=txn_data.order_type.value,
        quantity=txn_data.quantity,
        price_at_order=txn_data.price_at_order,
        total_value_usd=total_value,
        status="Pending",
        notes=txn_data.notes,
        created_at=now,
        updated_at=now,
    )
    db.add(db_txn)
    db.commit()
    db.refresh(db_txn)
    return db_txn, None


def _get_net_quantity(db: Session, user_id: str, asset_ticker: str) -> float:
    """Calculate net quantity a user holds for a given asset (completed orders only)."""
    buy_qty = db.query(func.coalesce(func.sum(Transaction.quantity), 0.0)).filter(
        Transaction.user_id == user_id,
        Transaction.asset_ticker == asset_ticker.upper(),
        Transaction.order_type == "Buy",
        Transaction.status == "Completed",
    ).scalar()
    sell_qty = db.query(func.coalesce(func.sum(Transaction.quantity), 0.0)).filter(
        Transaction.user_id == user_id,
        Transaction.asset_ticker == asset_ticker.upper(),
        Transaction.order_type == "Sell",
        Transaction.status == "Completed",
    ).scalar()
    return float(buy_qty) - float(sell_qty)


def get_transaction_by_id(db: Session, txn_id: str) -> Transaction | None:
    return db.query(Transaction).filter(Transaction.id == txn_id).first()


def list_transactions(
    db: Session,
    user_id: str | None = None,
    asset_ticker: str | None = None,
    status: str | None = None,
    order_type: str | None = None,
) -> list[Transaction]:
    query = db.query(Transaction)
    if user_id:
        query = query.filter(Transaction.user_id == user_id)
    if asset_ticker:
        query = query.filter(Transaction.asset_ticker == asset_ticker.upper())
    if status:
        query = query.filter(Transaction.status == status)
    if order_type:
        query = query.filter(Transaction.order_type == order_type)
    return query.order_by(Transaction.created_at.desc()).all()


def get_user_transactions(db: Session, user_id: str) -> list[Transaction]:
    return (
        db.query(Transaction)
        .filter(Transaction.user_id == user_id)
        .order_by(Transaction.created_at.desc())
        .all()
    )


def update_transaction_status(db: Session, txn_id: str, new_status: str) -> tuple[Transaction | None, str | None]:
    """Update order status with lifecycle validation."""
    db_txn = get_transaction_by_id(db, txn_id)
    if not db_txn:
        return None, "Transaction not found"

    current = db_txn.status
    allowed = VALID_STATUS_TRANSITIONS.get(current, [])
    if new_status not in allowed:
        return db_txn, f"Invalid status transition: '{current}' → '{new_status}'. Allowed: {allowed}"

    db_txn.status = new_status
    db_txn.updated_at = datetime.now(timezone.utc).isoformat()
    db.commit()
    db.refresh(db_txn)
    return db_txn, None


def cancel_transaction(db: Session, txn_id: str) -> tuple[Transaction | None, str | None]:
    """Cancel a Pending order."""
    db_txn = get_transaction_by_id(db, txn_id)
    if not db_txn:
        return None, "Transaction not found"
    if db_txn.status != "Pending":
        return db_txn, f"Cannot cancel: order status is '{db_txn.status}', only 'Pending' orders can be cancelled"

    db_txn.status = "Cancelled"
    db_txn.updated_at = datetime.now(timezone.utc).isoformat()
    db.commit()
    db.refresh(db_txn)
    return db_txn, None


def get_user_summary(db: Session, user_id: str) -> dict:
    """Compute the full transaction summary for a user."""
    txns = db.query(Transaction).filter(Transaction.user_id == user_id).all()

    total_invested = 0.0
    total_withdrawn = 0.0
    completed = 0
    pending = 0
    asset_map: dict[str, dict] = {}

    for txn in txns:
        if txn.status == "Completed":
            completed += 1
            if txn.order_type == "Buy":
                total_invested += txn.total_value_usd
            else:
                total_withdrawn += txn.total_value_usd

            # Track per-asset
            if txn.asset_ticker not in asset_map:
                asset_map[txn.asset_ticker] = {"net_quantity": 0.0, "total_spent_usd": 0.0}
            if txn.order_type == "Buy":
                asset_map[txn.asset_ticker]["net_quantity"] += txn.quantity
                asset_map[txn.asset_ticker]["total_spent_usd"] += txn.total_value_usd
            else:
                asset_map[txn.asset_ticker]["net_quantity"] -= txn.quantity

        elif txn.status == "Pending":
            pending += 1

    by_asset = [
        {"ticker": ticker, "net_quantity": round(v["net_quantity"], 6), "total_spent_usd": round(v["total_spent_usd"], 2)}
        for ticker, v in asset_map.items()
    ]

    return {
        "user_id": user_id,
        "total_invested_usd": round(total_invested, 2),
        "total_withdrawn_usd": round(total_withdrawn, 2),
        "net_position_usd": round(total_invested - total_withdrawn, 2),
        "completed_orders": completed,
        "pending_orders": pending,
        "by_asset": by_asset,
    }

def delete_transaction(db: Session, txn_id: str) -> tuple[bool, str | None]:
    """Permanently delete a transaction record by ID."""
    db_txn = get_transaction_by_id(db, txn_id)
    if not db_txn:
        return False, "Transaction not found"
    
    db.delete(db_txn)
    db.commit()
    return True, None
