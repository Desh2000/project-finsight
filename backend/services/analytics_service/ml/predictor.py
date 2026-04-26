# FinVest | Analytics Service | ml/predictor.py
# Goal Completion Risk Engine — Model loading & inference
#
# This module is imported once at service startup. The pipeline (scaler +
# RandomForest) is loaded into module-level memory so every HTTP request
# gets sub-millisecond inference without disk I/O.

import os
import math
import joblib
import numpy as np
from datetime import datetime, timezone

MODEL_PATH = os.path.join(os.path.dirname(__file__), "goal_risk_model.pkl")
FEATURE_NAMES = [
    "pct_time_elapsed",
    "pct_amount_saved",
    "save_efficiency",
    "days_remaining",
    "days_total",
    "log_target_usd",
    "completion_pct",
]

# ── Lazy-load: populated on first call to predict() ──
_pipeline = None


def _load_pipeline():
    global _pipeline
    if _pipeline is None:
        if not os.path.exists(MODEL_PATH):
            raise FileNotFoundError(
                f"[ML] Model not found at {MODEL_PATH}. "
                "Ensure ensure_model_ready() was called on service startup."
            )
        _pipeline = joblib.load(MODEL_PATH)
        print(f"[ML] Pipeline loaded from {MODEL_PATH}")
    return _pipeline


# ───────────────────────────────────────────────────────────
# Feature engineering — must mirror trainer.py exactly
# ───────────────────────────────────────────────────────────

def _extract_features(
    created_at: str,
    target_date: str,
    current_amount_usd: float,
    target_amount_usd: float,
) -> tuple[np.ndarray, dict]:
    """
    Compute the 7-feature vector from a SavingsGoal record.
    Returns (X, feature_dict) where X is shape (1, 7).
    """
    now = datetime.now(timezone.utc)

    # Parse created_at (ISO string stored by the service)
    try:
        created = datetime.fromisoformat(created_at)
        if created.tzinfo is None:
            created = created.replace(tzinfo=timezone.utc)
    except Exception:
        created = now

    # Parse target_date (YYYY-MM-DD stored as string)
    try:
        target_dt = datetime.fromisoformat(target_date).replace(tzinfo=timezone.utc)
    except Exception:
        target_dt = now

    days_total = max((target_dt - created).days, 1)
    days_elapsed = max((now - created).days, 0)
    days_remaining = max((target_dt - now).days, 0)

    pct_time_elapsed = min(days_elapsed / days_total, 1.0)
    pct_amount_saved = current_amount_usd / max(target_amount_usd, 1e-6)
    save_efficiency = pct_amount_saved / max(pct_time_elapsed, 1e-6)
    log_target_usd = math.log1p(max(target_amount_usd, 0))
    completion_pct = min(pct_amount_saved * 100, 150.0)

    features = {
        "pct_time_elapsed": pct_time_elapsed,
        "pct_amount_saved": pct_amount_saved,
        "save_efficiency": save_efficiency,
        "days_remaining": float(days_remaining),
        "days_total": float(days_total),
        "log_target_usd": log_target_usd,
        "completion_pct": completion_pct,
    }

    X = np.array([[
        pct_time_elapsed,
        pct_amount_saved,
        save_efficiency,
        float(days_remaining),
        float(days_total),
        log_target_usd,
        completion_pct,
    ]])
    return X, features, days_remaining


# ───────────────────────────────────────────────────────────
# Smart insight message generator
# ───────────────────────────────────────────────────────────

def _generate_insight(
    risk_label: str,
    pct_amount_saved: float,
    pct_time_elapsed: float,
    save_efficiency: float,
    days_remaining: int,
    required_daily_usd: float,
) -> str:
    """Generate a human-readable, actionable insight string."""
    gap_pct = round((1.0 - pct_amount_saved) * 100, 1)
    elapsed_pct = round(pct_time_elapsed * 100, 1)
    saved_pct = round(pct_amount_saved * 100, 1)

    if risk_label == "on_track":
        if save_efficiency >= 1.2:
            return (
                f"🚀 Excellent pace! You've saved {saved_pct}% with {elapsed_pct}% of time used. "
                f"Keep up ${ required_daily_usd:.2f}/day and you'll finish early!"
            )
        return (
            f"✅ On track! You've saved {saved_pct}% of your target. "
            f"Maintain ${required_daily_usd:.2f}/day to hit your goal."
        )
    elif risk_label == "at_risk":
        return (
            f"⚠️ Slightly behind. You've saved {saved_pct}% but {elapsed_pct}% of time has passed. "
            f"Increase deposits to ${required_daily_usd:.2f}/day to catch up in {days_remaining} days."
        )
    else:  # critical
        if days_remaining <= 7:
            return (
                f"🚨 Deadline in {days_remaining} day(s)! You still need {gap_pct}% more. "
                f"An urgent deposit of ${required_daily_usd:.2f}/day is required."
            )
        return (
            f"🔴 Critical risk! Only {saved_pct}% saved but {elapsed_pct}% of time has elapsed. "
            f"You need ${required_daily_usd:.2f}/day to still reach your goal."
        )


# ───────────────────────────────────────────────────────────
# Public prediction API
# ───────────────────────────────────────────────────────────

def predict(
    created_at: str,
    target_date: str,
    current_amount_usd: float,
    target_amount_usd: float,
    goal_status: str,
) -> dict:
    """
    Run a full risk prediction for a savings goal.

    Args:
        created_at: ISO datetime string (goal creation time)
        target_date: ISO date string (YYYY-MM-DD)
        current_amount_usd: amount deposited so far
        target_amount_usd: the user's savings target
        goal_status: "Active" | "Completed" | "Abandoned"

    Returns:
        dict with risk label, probabilities, required deposits, insight
    """
    # Short-circuit: completed goals are always "on_track"
    if goal_status == "Completed":
        return {
            "risk_label": "on_track",
            "risk_probability": 1.0,
            "on_track_probability": 1.0,
            "at_risk_probability": 0.0,
            "critical_probability": 0.0,
            "required_daily_usd": 0.0,
            "required_weekly_usd": 0.0,
            "required_monthly_usd": 0.0,
            "smart_insight": "🎉 Goal completed! Congratulations on reaching your target.",
            "days_remaining": 0,
            "save_efficiency": 1.0,
        }

    # Short-circuit: abandoned goals
    if goal_status == "Abandoned":
        return {
            "risk_label": "critical",
            "risk_probability": 1.0,
            "on_track_probability": 0.0,
            "at_risk_probability": 0.0,
            "critical_probability": 1.0,
            "required_daily_usd": 0.0,
            "required_weekly_usd": 0.0,
            "required_monthly_usd": 0.0,
            "smart_insight": "❌ This goal has been abandoned.",
            "days_remaining": 0,
            "save_efficiency": 0.0,
        }

    pipeline = _load_pipeline()
    X, features, days_remaining = _extract_features(
        created_at, target_date, current_amount_usd, target_amount_usd
    )

    # Model inference
    risk_label: str = pipeline.predict(X)[0]
    proba: np.ndarray = pipeline.predict_proba(X)[0]
    classes: list = list(pipeline.classes_)

    def _p(label: str) -> float:
        idx = classes.index(label) if label in classes else -1
        return float(proba[idx]) if idx >= 0 else 0.0

    on_track_p = _p("on_track")
    at_risk_p = _p("at_risk")
    critical_p = _p("critical")

    label_proba_map = {"on_track": on_track_p, "at_risk": at_risk_p, "critical": critical_p}
    risk_probability = label_proba_map.get(risk_label, 0.0)

    # Required deposit calculations
    amount_remaining = max(target_amount_usd - current_amount_usd, 0.0)
    safe_days = max(days_remaining, 1)
    required_daily_usd = round(amount_remaining / safe_days, 2)
    required_weekly_usd = round(required_daily_usd * 7, 2)
    required_monthly_usd = round(required_daily_usd * 30, 2)

    smart_insight = _generate_insight(
        risk_label=risk_label,
        pct_amount_saved=features["pct_amount_saved"],
        pct_time_elapsed=features["pct_time_elapsed"],
        save_efficiency=features["save_efficiency"],
        days_remaining=days_remaining,
        required_daily_usd=required_daily_usd,
    )

    return {
        "risk_label": risk_label,
        "risk_probability": round(risk_probability, 4),
        "on_track_probability": round(on_track_p, 4),
        "at_risk_probability": round(at_risk_p, 4),
        "critical_probability": round(critical_p, 4),
        "required_daily_usd": required_daily_usd,
        "required_weekly_usd": required_weekly_usd,
        "required_monthly_usd": required_monthly_usd,
        "smart_insight": smart_insight,
        "days_remaining": days_remaining,
        "save_efficiency": round(features["save_efficiency"], 4),
    }
