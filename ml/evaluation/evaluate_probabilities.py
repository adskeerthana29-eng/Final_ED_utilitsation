import pandas as pd
from pathlib import Path

from catboost import CatBoostClassifier

from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    roc_auc_score,
    accuracy_score,
    brier_score_loss
)


# ============================================================
# PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parents[2]

DATA_FILE = (
    BASE_DIR
    / "ml"
    / "data"
    / "processed"
    / "UC07_preprocessed.csv"
)

MODEL_FILE = (
    BASE_DIR
    / "ml"
    / "models"
    / "catboost_model.cbm"
)


# ============================================================
# LOAD DATA
# ============================================================

df = pd.read_csv(DATA_FILE)

TARGET = "potentially_avoidable"

y = df[TARGET].astype(int)

X = df.drop(
    columns=[TARGET]
).copy()


# ============================================================
# CATEGORICAL FEATURES
# ============================================================

CATEGORICAL_FEATURES = [
    "past_diagnosis_category_mode",
    "triage_acuity",
    "gender",
    "region",
    "condition",
    "diagnosis_category",
    "severity",
    "symptom_fever_chills",
    "symptom_cold_cough",
    "symptom_vomiting",
    "barrier_no_insurance",
    "barrier_after_hours_problem",
    "transportation_barrier",
    "alternative_care_access",
    "has_primary_care_provider"
]


for column in CATEGORICAL_FEATURES:

    X[column] = (
        X[column]
        .fillna("Unknown")
        .astype(str)
    )


# ============================================================
# SAME TEST SPLIT
# ============================================================

X_train_val, X_test, y_train_val, y_test = train_test_split(
    X,
    y,
    test_size=0.15,
    random_state=42,
    stratify=y
)


# ============================================================
# LOAD SAVED MODEL
# ============================================================

model = CatBoostClassifier()

model.load_model(MODEL_FILE)


# ============================================================
# TEST PROBABILITIES
# ============================================================

probabilities = (
    model.predict_proba(X_test)[:, 1]
)


predictions = (
    probabilities >= 0.50
).astype(int)


# ============================================================
# BASIC METRICS
# ============================================================

print("=" * 70)
print("UC07 — PROBABILITY CHECK")
print("=" * 70)

print(
    f"\nTest Accuracy : "
    f"{accuracy_score(y_test, predictions):.4f}"
)

print(
    f"Test ROC-AUC  : "
    f"{roc_auc_score(y_test, probabilities):.4f}"
)

print(
    f"Brier Score   : "
    f"{brier_score_loss(y_test, probabilities):.4f}"
)


# ============================================================
# PROBABILITY DISTRIBUTION
# ============================================================

print("\n" + "=" * 70)
print("PROBABILITY DISTRIBUTION")
print("=" * 70)

print(
    pd.Series(probabilities).describe()
)


# ============================================================
# PROBABILITY RANGES
# ============================================================

bins = [
    0.0,
    0.1,
    0.2,
    0.3,
    0.4,
    0.5,
    0.6,
    0.7,
    0.8,
    0.9,
    1.0
]

labels = [
    "0.0-0.1",
    "0.1-0.2",
    "0.2-0.3",
    "0.3-0.4",
    "0.4-0.5",
    "0.5-0.6",
    "0.6-0.7",
    "0.7-0.8",
    "0.8-0.9",
    "0.9-1.0"
]

ranges = pd.cut(
    probabilities,
    bins=bins,
    labels=labels,
    include_lowest=True
)

print("\nProbability ranges:")

print(
    ranges.value_counts()
    .sort_index()
)


# ============================================================
# EXTREME CONFIDENCE
# ============================================================

very_high = (
    probabilities >= 0.90
).sum()

very_low = (
    probabilities <= 0.10
).sum()

print("\n" + "=" * 70)
print("EXTREME PROBABILITIES")
print("=" * 70)

print(
    f"Probability >= 0.90 : "
    f"{very_high} / {len(probabilities)}"
)

print(
    f"Probability <= 0.10 : "
    f"{very_low} / {len(probabilities)}"
)