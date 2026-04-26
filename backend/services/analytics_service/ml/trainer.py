# FinVest | Analytics Service | ml/trainer.py
# Goal Completion Risk Engine — Synthetic data generation & RandomForest training
#
# WHY SYNTHETIC DATA?
# The analytics_service has no historical deposit-event log — only point-in-time
# goal snapshots. We generate realistic training examples using domain-derived
# financial rules (mirroring how a human wealth advisor would classify a goal),
# then learn a generalised decision boundary with RandomForestClassifier so the
# model can handle novel goals it has never seen.

import os
import numpy as np
import joblib
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report

MODEL_PATH = os.path.join(os.path.dirname(__file__), "goal_risk_model.pkl")
N_SAMPLES = 20_000
RANDOM_STATE = 42
FEATURE_NAMES = [
    "pct_time_elapsed",
    "pct_amount_saved",
    "save_efficiency",
    "days_remaining",
    "days_total",
    "log_target_usd",
    "completion_pct",
]


# ───────────────────────────────────────────────────────────
# 1.  Synthetic data generation
# ───────────────────────────────────────────────────────────

def _generate_synthetic_data(n: int, rng: np.random.Generator) -> tuple[np.ndarray, np.ndarray]:
    """
    Generate N synthetic savings-goal observations with domain-realistic distributions.

    Feature engineering mirrors what the predictor computes at inference time,
    ensuring train/serve consistency.
    """
    # --- Goal timeline (in days) ---
    days_total = rng.integers(30, 1096, size=n).astype(float)          # 1 month – 3 years
    pct_time_elapsed = rng.uniform(0.01, 1.0, size=n)                   # how far through timeline
    days_elapsed = pct_time_elapsed * days_total
    days_remaining = np.maximum(days_total - days_elapsed, 0.0)

    # --- Savings progress ---
    # Good savers cluster around or above the "on-pace" amount;
    # at-risk savers lag behind; critical savers are way behind.
    # We simulate this with a mixture to get realistic class balance.
    pct_amount_saved = np.empty(n)
    labels_raw = rng.choice(["on_track", "at_risk", "critical"],
                             size=n, p=[0.40, 0.35, 0.25])

    for i in range(n):
        te = pct_time_elapsed[i]           # time fraction used
        if labels_raw[i] == "on_track":
            # saved ≥ 90 % of what they should have by now, possibly more
            target_saved = te * rng.uniform(0.90, 1.40)
        elif labels_raw[i] == "at_risk":
            # saved 50–90 % of expected pace
            target_saved = te * rng.uniform(0.50, 0.90)
        else:  # critical
            # saved < 50 % of expected pace
            target_saved = te * rng.uniform(0.01, 0.50)
        # Clamp to [0, 1.5] — can be slightly over 1 if goal almost complete
        pct_amount_saved[i] = np.clip(target_saved + rng.normal(0, 0.03), 0.0, 1.5)

    # --- Derived features ---
    save_efficiency = pct_amount_saved / np.maximum(pct_time_elapsed, 1e-6)
    log_target_usd = np.log1p(rng.uniform(100, 50_000, size=n))         # goal size (log scale)
    completion_pct = np.clip(pct_amount_saved * 100, 0, 150)

    # --- Analytical re-labelling (tighten domain logic) ---
    # Override labels to enforce hard domain rules that supersede the mixture:
    labels = labels_raw.copy()
    for i in range(n):
        eff = save_efficiency[i]
        dr = days_remaining[i]
        pct_saved = pct_amount_saved[i]

        # Already essentially done — always on_track
        if pct_saved >= 0.95:
            labels[i] = "on_track"
        # Deadline imminent and large gap — always critical
        elif dr <= 7 and pct_saved < 0.80:
            labels[i] = "critical"
        # Clearly ahead of schedule
        elif eff >= 1.00:
            labels[i] = "on_track"
        # Running behind but not disastrously so
        elif 0.55 <= eff < 1.00:
            labels[i] = "at_risk"
        # Severely behind
        else:
            labels[i] = "critical"

    X = np.column_stack([
        pct_time_elapsed,
        pct_amount_saved,
        save_efficiency,
        days_remaining,
        days_total,
        log_target_usd,
        completion_pct,
    ])
    return X, np.array(labels)


# ───────────────────────────────────────────────────────────
# 2.  Training pipeline
# ───────────────────────────────────────────────────────────

def train_and_save() -> None:
    """
    Train the RandomForest pipeline on synthetic data and persist to disk.
    Called once at service startup if MODEL_PATH does not exist.
    """
    print("[ML] Training Goal Completion Risk model …")
    rng = np.random.default_rng(RANDOM_STATE)
    X, y = _generate_synthetic_data(N_SAMPLES, rng)

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.15, random_state=RANDOM_STATE, stratify=y
    )

    pipeline = Pipeline([
        ("scaler", StandardScaler()),
        ("clf", RandomForestClassifier(
            n_estimators=120,
            max_depth=12,
            min_samples_leaf=4,
            class_weight="balanced",
            random_state=RANDOM_STATE,
            n_jobs=-1,
        )),
    ])
    pipeline.fit(X_train, y_train)

    # Evaluation (printed to service logs, not returned to users)
    y_pred = pipeline.predict(X_test)
    print("[ML] Classification Report:")
    print(classification_report(y_test, y_pred))

    joblib.dump(pipeline, MODEL_PATH)
    print(f"[ML] Model saved → {MODEL_PATH}")


def ensure_model_ready() -> None:
    """Entry point called from main.py on service startup."""
    if not os.path.exists(MODEL_PATH):
        train_and_save()
    else:
        print(f"[ML] Model already exists at {MODEL_PATH} — skipping training.")
