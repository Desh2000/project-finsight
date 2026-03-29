# FinVest | Analytics Service | crud.py
# Member 4: Savings Goal & Portfolio Analytics — all database operations

from sqlalchemy.orm import Session
from models import SavingsGoal
from schemas import GoalCreate, GoalUpdate
from external import get_usd_to_lkr
import uuid
from datetime import datetime, timezone


def create_goal(db: Session, goal_data: GoalCreate) -> SavingsGoal:
    """Create a new savings goal."""
    now = datetime.now(timezone.utc).isoformat()
    db_goal = SavingsGoal(
        id=str(uuid.uuid4()),
        user_id=goal_data.user_id,
        goal_name=goal_data.goal_name,
        target_amount_usd=goal_data.target_amount_usd,
        current_amount_usd=0.0,
        target_date=goal_data.target_date,
        currency_display=goal_data.currency_display.value,
        status="Active",
        created_at=now,
        updated_at=now,
    )
    db.add(db_goal)
    db.commit()
    db.refresh(db_goal)
    return db_goal


def get_goal_by_id(db: Session, goal_id: str) -> SavingsGoal | None:
    return db.query(SavingsGoal).filter(SavingsGoal.id == goal_id).first()


def list_goals(db: Session, user_id: str | None = None, status: str | None = None) -> list[SavingsGoal]:
    query = db.query(SavingsGoal)
    if user_id:
        query = query.filter(SavingsGoal.user_id == user_id)
    if status:
        query = query.filter(SavingsGoal.status == status)
    return query.all()


def update_goal(db: Session, goal_id: str, update_data: GoalUpdate) -> SavingsGoal | None:
    db_goal = get_goal_by_id(db, goal_id)
    if not db_goal:
        return None

    update_dict = update_data.model_dump(exclude_unset=True)
    if "currency_display" in update_dict and update_dict["currency_display"] is not None:
        update_dict["currency_display"] = update_dict["currency_display"].value

    for field, value in update_dict.items():
        setattr(db_goal, field, value)

    db_goal.updated_at = datetime.now(timezone.utc).isoformat()
    db.commit()
    db.refresh(db_goal)
    return db_goal


def deposit_to_goal(db: Session, goal_id: str, amount: float) -> tuple[SavingsGoal | None, str | None]:
    """Add to current_amount_usd. Auto-complete goal if target is reached."""
    db_goal = get_goal_by_id(db, goal_id)
    if not db_goal:
        return None, "Goal not found"

    if db_goal.status != "Active":
        return db_goal, f"Cannot deposit: goal status is '{db_goal.status}'"

    db_goal.current_amount_usd = round(db_goal.current_amount_usd + amount, 2)

    # Auto-complete if target reached
    if db_goal.current_amount_usd >= db_goal.target_amount_usd:
        db_goal.status = "Completed"

    db_goal.updated_at = datetime.now(timezone.utc).isoformat()
    db.commit()
    db.refresh(db_goal)
    return db_goal, None


def abandon_goal(db: Session, goal_id: str) -> SavingsGoal | None:
    db_goal = get_goal_by_id(db, goal_id)
    if not db_goal:
        return None
    db_goal.status = "Abandoned"
    db_goal.updated_at = datetime.now(timezone.utc).isoformat()
    db.commit()
    db.refresh(db_goal)
    return db_goal


def get_enriched_goal(goal, exchange_rate: float) -> dict:
    """Enrich a goal with LKR values and completion data."""
    completion_pct = (
        round((goal.current_amount_usd / goal.target_amount_usd) * 100, 1)
        if goal.target_amount_usd > 0 else 0.0
    )

    # Calculate days remaining
    try:
        target_date = datetime.fromisoformat(goal.target_date).date()
        today = datetime.now(timezone.utc).date()
        days_remaining = max(0, (target_date - today).days)
    except Exception:
        days_remaining = 0

    return {
        "id": goal.id,
        "goal_name": goal.goal_name,
        "target_amount_usd": goal.target_amount_usd,
        "current_amount_usd": goal.current_amount_usd,
        "completion_percentage": completion_pct,
        "target_amount_lkr": round(goal.target_amount_usd * exchange_rate, 2),
        "current_amount_lkr": round(goal.current_amount_usd * exchange_rate, 2),
        "days_remaining": days_remaining,
        "status": goal.status,
    }


def get_portfolio(db: Session, user_id: str) -> dict:
    """Compute the full portfolio analytics for a user."""
    all_goals = db.query(SavingsGoal).filter(SavingsGoal.user_id == user_id).all()

    rate, is_fallback, rate_timestamp = get_usd_to_lkr()

    active_goals = [g for g in all_goals if g.status == "Active"]
    completed_goals = [g for g in all_goals if g.status == "Completed"]
    abandoned_goals = [g for g in all_goals if g.status == "Abandoned"]

    total_value_usd = sum(g.current_amount_usd for g in active_goals)

    enriched = [get_enriched_goal(g, rate) for g in all_goals]

    return {
        "user_id": user_id,
        "total_goal_value_usd": round(total_value_usd, 2),
        "total_goal_value_lkr": round(total_value_usd * rate, 2),
        "exchange_rate": rate,
        "fallback_rate": is_fallback,
        "rate_timestamp": rate_timestamp,
        "active_goals": len(active_goals),
        "completed_goals": len(completed_goals),
        "abandoned_goals": len(abandoned_goals),
        "goals": enriched,
    }
