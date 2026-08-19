# ============================================================
# UC07 — CATBOOST PROBABILITY CALIBRATION CHECK
#
# Checks:
# 1. Calibration curve
# 2. Brier score
# 3. Actual positive rate vs predicted probability
# 4. 0.90–1.00 probability group
#
# IMPORTANT:
# This script DOES NOT retrain the CatBoost model.
# It loads the already-trained .cbm model.
# ============================================================

import pandas as pd
import numpy as np

from pathlib import Path

from catboost import CatBoostClassifier

from sklearn.model_selection import train_test_split

from sklearn.metrics import (
    brier_score_loss,
    roc_auc_score
)

from sklearn.calibration import calibration_curve

import matplotlib.pyplot as plt


# ============================================================
# 1. PATHS
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
# 2. SETTINGS
# ============================================================

TARGET = "potentially_avoidable"

RANDOM_STATE = 42

TEST_SIZE = 0.15


# ============================================================
# 3. LOAD DATA
# ============================================================

print("=" * 70)
print("UC07 — PROBABILITY CALIBRATION CHECK")
print("=" * 70)

print("\nLoading dataset:")

print(DATA_FILE)

df = pd.read_csv(DATA_FILE)

print(
    f"\nDataset shape: {df.shape}"
)


# ============================================================
# 4. TARGET
# ============================================================

y = df[TARGET].astype(int)

X = df.drop(
    columns=[TARGET],
    errors="ignore"
).copy()


# ============================================================
# 5. CATEGORICAL FEATURES
# ============================================================

CATEGORICAL_FEATURES = [

    # -------------------------
    # Past / Historical
    # -------------------------

    "past_diagnosis_category_mode",
    "triage_acuity",

    # -------------------------
    # Current
    # -------------------------

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


# ============================================================
# 6. PREPARE CATEGORICAL FEATURES
# ============================================================

for column in CATEGORICAL_FEATURES:

    X[column] = (
        X[column]
        .fillna("Unknown")
        .astype(str)
    )


# ============================================================
# 7. RECREATE SAME TEST SPLIT
# ============================================================

X_train_val, X_test, y_train_val, y_test = (

    train_test_split(

        X,
        y,

        test_size=TEST_SIZE,

        random_state=RANDOM_STATE,

        stratify=y
    )
)


# ============================================================
# 8. LOAD SAVED MODEL
# ============================================================

print("\n" + "=" * 70)
print("LOADING SAVED MODEL")
print("=" * 70)

print(
    f"\nModel:\n{MODEL_FILE}"
)

model = CatBoostClassifier()

model.load_model(
    MODEL_FILE
)

print("\nModel loaded successfully.")


# ============================================================
# 9. TEST SET PROBABILITIES
# ============================================================

test_probability = (

    model
    .predict_proba(X_test)[:, 1]
)


# ============================================================
# 10. BASIC METRICS
# ============================================================

brier_score = brier_score_loss(
    y_test,
    test_probability
)

roc_auc = roc_auc_score(
    y_test,
    test_probability
)


print("\n" + "=" * 70)
print("CALIBRATION METRICS")
print("=" * 70)

print(
    f"\nROC-AUC    : {roc_auc:.4f}"
)

print(
    f"Brier Score: {brier_score:.4f}"
)


# ============================================================
# 11. CALIBRATION CURVE
# ============================================================

fraction_positive, mean_predicted = (

    calibration_curve(

        y_test,

        test_probability,

        n_bins=10,

        strategy="uniform"
    )
)


# ============================================================
# 12. CALIBRATION TABLE
# ============================================================

calibration_table = pd.DataFrame({

    "Mean Predicted Probability":
        mean_predicted,

    "Actual Positive Rate":
        fraction_positive

})

calibration_table["Difference"] = (

    calibration_table["Actual Positive Rate"]
    -
    calibration_table["Mean Predicted Probability"]

)


print("\n" + "=" * 70)
print("CALIBRATION TABLE")
print("=" * 70)

print(

    calibration_table.to_string(

        index=False,

        formatters={

            "Mean Predicted Probability":
                "{:.4f}".format,

            "Actual Positive Rate":
                "{:.4f}".format,

            "Difference":
                "{:.4f}".format
        }
    )
)


# ============================================================
# 13. 0.90–1.00 PROBABILITY GROUP
# ============================================================

high_probability_mask = (

    test_probability >= 0.90
)


high_probability_count = (
    high_probability_mask.sum()
)


high_probability_actual_rate = (

    y_test[high_probability_mask]
    .mean()
)


high_probability_mean_prediction = (

    test_probability[high_probability_mask]
    .mean()
)


print("\n" + "=" * 70)
print("0.90–1.00 PROBABILITY GROUP")
print("=" * 70)

print(
    f"\nNumber of patients:"
    f" {high_probability_count}"
)

print(
    f"Mean predicted probability:"
    f" {high_probability_mean_prediction:.4f}"
)

print(
    f"Actual positive rate:"
    f" {high_probability_actual_rate:.4f}"
)

print(
    f"Actual positive rate (%):"
    f" {high_probability_actual_rate * 100:.2f}%"
)

print(
    f"Prediction difference:"
    f" {high_probability_actual_rate - high_probability_mean_prediction:.4f}"
)


# ============================================================
# 14. INTERPRET HIGH PROBABILITY GROUP
# ============================================================

print("\n" + "=" * 70)
print("HIGH-PROBABILITY INTERPRETATION")
print("=" * 70)

difference = (
    high_probability_actual_rate
    -
    high_probability_mean_prediction
)


if abs(difference) <= 0.05:

    print(
        "\nGOOD:"
        "\nThe 0.90–1.00 probability group is"
        "\nreasonably close to its predicted probability."
    )

elif abs(difference) <= 0.10:

    print(
        "\nMODERATE:"
        "\nThere is some calibration difference"
        "\nbetween predicted probability and actual"
        "\noutcome frequency."
    )

else:

    print(
        "\nPOOR CALIBRATION:"
        "\nThe 0.90–1.00 group differs substantially"
        "\nfrom its predicted probability."
    )


# ============================================================
# 15. CALIBRATION CURVE PLOT
# ============================================================

plt.figure(
    figsize=(8, 6)
)

plt.plot(

    mean_predicted,

    fraction_positive,

    marker="o",

    label="CatBoost"
)


# Perfect calibration line

plt.plot(

    [0, 1],

    [0, 1],

    linestyle="--",

    label="Perfect Calibration"
)


plt.xlabel(
    "Mean Predicted Probability"
)

plt.ylabel(
    "Actual Positive Rate"
)

plt.title(
    "UC07 — CatBoost Calibration Curve"
)

plt.legend()

plt.grid(
    True,
    alpha=0.3
)

plt.tight_layout()


# ============================================================
# 16. SAVE CALIBRATION PLOT
# ============================================================

PLOT_FILE = (

    BASE_DIR
    / "ml"
    / "evaluation"
    / "calibration_curve.png"
)


plt.savefig(
    PLOT_FILE,
    dpi=150
)

plt.show()


# ============================================================
# 17. FINAL SUMMARY
# ============================================================

print("\n" + "=" * 70)
print("CALIBRATION CHECK COMPLETED")
print("=" * 70)

print(
    f"\nROC-AUC:"
    f" {roc_auc:.4f}"
)

print(
    f"Brier Score:"
    f" {brier_score:.4f}"
)

print(
    f"0.90–1.00 group:"
    f" {high_probability_count} patients"
)

print(
    f"Actual positive rate:"
    f" {high_probability_actual_rate:.4f}"
)

print(
    f"\nCalibration plot saved to:"
    f"\n{PLOT_FILE}"
)