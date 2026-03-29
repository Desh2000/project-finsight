# FinVest | Analytics Service | router.py
# Member 4: Savings Goal & Portfolio Analytics — FastAPI route definitions

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from database import get_db
from schemas import (
    GoalCreate, GoalUpdate, DepositRequest,
    GoalResponse, GoalListResponse, PortfolioResponse,
)
import crud
from external import get_usd_to_lkr

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.post(
    "/goals/",
    response_model=GoalResponse,
    status_code=201,
    summary="Create a savings goal",
    description="Create a new savings goal. target_date must be in the future.",
)
def create_goal(goal_data: GoalCreate, db: Session = Depends(get_db)):
    return crud.create_goal(db, goal_data)


@router.get(
    "/goals/",
    response_model=GoalListResponse,
    summary="List savings goals",
    description="List all savings goals with optional filters for user_id and status.",
)
def list_goals(
    user_id: str | None = Query(None),
    status: str | None = Query(None),
    db: Session = Depends(get_db),
):
    goals = crud.list_goals(db, user_id=user_id, status=status)
    return {"goals": goals, "total": len(goals)}


@router.get(
    "/goals/{goal_id}",
    summary="Get a savings goal",
    description="Fetch a single savings goal with completion percentage and LKR values.",
)
def get_goal(goal_id: str, db: Session = Depends(get_db)):
    db_goal = crud.get_goal_by_id(db, goal_id)
    if not db_goal:
        raise HTTPException(status_code=404, detail="Goal not found")
    rate, _, _ = get_usd_to_lkr()
    return crud.get_enriched_goal(db_goal, rate)


@router.put(
    "/goals/{goal_id}",
    response_model=GoalResponse,
    summary="Update a savings goal",
    description="Update goal target_amount, target_date, or currency_display.",
)
def update_goal(goal_id: str, update_data: GoalUpdate, db: Session = Depends(get_db)):
    db_goal = crud.update_goal(db, goal_id, update_data)
    if not db_goal:
        raise HTTPException(status_code=404, detail="Goal not found")
    return db_goal


@router.patch(
    "/goals/{goal_id}/deposit",
    response_model=GoalResponse,
    summary="Deposit into a savings goal",
    description="Add money to current_amount_usd. Auto-completes the goal if target is reached.",
)
def deposit(goal_id: str, deposit_data: DepositRequest, db: Session = Depends(get_db)):
    db_goal, error = crud.deposit_to_goal(db, goal_id, deposit_data.amount)
    if error and db_goal is None:
        raise HTTPException(status_code=404, detail=error)
    if error:
        raise HTTPException(status_code=400, detail=error)
    return db_goal


@router.delete(
    "/goals/{goal_id}",
    status_code=204,
    summary="Abandon a savings goal",
    description="Set the goal status to 'Abandoned'.",
)
def delete_goal(goal_id: str, db: Session = Depends(get_db)):
    db_goal = crud.abandon_goal(db, goal_id)
    if not db_goal:
        raise HTTPException(status_code=404, detail="Goal not found")
    return None


@router.get(
    "/portfolio/{user_id}",
    response_model=PortfolioResponse,
    summary="Portfolio analytics",
    description=(
        "Analytical centrepiece: computes total goal values in USD and LKR, "
        "active/completed/abandoned counts, and enriched goal details."
    ),
)
def get_portfolio(user_id: str, db: Session = Depends(get_db)):
    return crud.get_portfolio(db, user_id)
