# FinVest | Analytics Service | router.py
# Member 4: Savings Goal & Portfolio Analytics — FastAPI route definitions

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from database import get_db
from schemas import (
    GoalCreate, GoalUpdate, DepositRequest,
    GoalResponse, GoalListResponse, PortfolioResponse,
    GoalPredictionResponse,
)
import crud
from external import get_usd_to_lkr
from ml import predictor as ml_predictor

router = APIRouter(prefix="/api/analytics", tags=["Analytics"])


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


@router.get(
    "/goals/{goal_id}/predict",
    response_model=GoalPredictionResponse,
    summary="ML risk prediction for a savings goal",
    description=(
        "Runs the Goal Completion Risk Engine: a RandomForest classifier trained on "
        "20,000 synthetic savings scenarios. Returns a risk label (on_track / at_risk / critical), "
        "class probabilities, required daily/weekly/monthly deposits, and a smart investor insight."
    ),
    tags=["ML Predictions"],
)
def predict_goal_risk(goal_id: str, db: Session = Depends(get_db)):
    """Predict completion risk for a single savings goal using the trained ML model."""
    db_goal = crud.get_goal_by_id(db, goal_id)
    if not db_goal:
        raise HTTPException(status_code=404, detail="Goal not found")

    try:
        prediction = ml_predictor.predict(
            created_at=db_goal.created_at,
            target_date=db_goal.target_date,
            current_amount_usd=db_goal.current_amount_usd,
            target_amount_usd=db_goal.target_amount_usd,
            goal_status=db_goal.status,
        )
    except FileNotFoundError as exc:
        raise HTTPException(status_code=503, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"ML prediction failed: {exc}")

    return GoalPredictionResponse(
        goal_id=db_goal.id,
        goal_name=db_goal.goal_name,
        goal_status=db_goal.status,
        **prediction,
    )

@router.delete(
    "/goals/{goal_id}/permanent",
    status_code=200,
    summary="Permanently delete a savings goal",
    description="Completely removes the goal from the database (irreversible).",
)
def permanent_delete_goal(goal_id: str, db: Session = Depends(get_db)):
    db_goal = crud.delete_goal_permanently(db, goal_id)
    
    if not db_goal:
        raise HTTPException(status_code=404, detail="Goal not found")
    
    return {"message": f"Goal '{goal_id}' has been permanently deleted."}
