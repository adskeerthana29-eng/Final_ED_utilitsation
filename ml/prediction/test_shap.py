import sys
from pathlib import Path

# ============================================================
# PROJECT ROOT
# ============================================================

BASE_DIR = Path(__file__).resolve().parents[2]

# Allow imports from ml/prediction
PREDICTION_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(PREDICTION_DIR))

# Allow imports from project root
sys.path.insert(0, str(BASE_DIR))


# ============================================================
# IMPORTS
# ============================================================

import joblib
import pandas as pd

from feature_builder import build_prediction_features
from prediction_service import FEATURES


# ============================================================
# LOAD SHAP EXPLAINER
# ============================================================

explainer_path = (
    BASE_DIR
    / "carenavigator"
    / "models"
    / "explainer.joblib"
)

print("=" * 60)
print("SHAP TEST")
print("=" * 60)

print("Explainer path:")
print(explainer_path)

explainer = joblib.load(explainer_path)

print("\nExplainer loaded successfully")
print("Explainer type:", type(explainer))


# ============================================================
# TEST PATIENT
# ============================================================

patient = {

    "patient_id": "P-FE8F2ED3",

    # Historical features
    "gender": "Female",
    "region": "South",

    "past_diagnosis_category_mode":
        "Respiratory",

    "triage_acuity": 3,

    "prior_ed_visits": 3,

    "ed_visits_last_30_days": 2,

    "ed_visits_last_90_days": 4,

    "days_since_last_ed_visit": 15,

    "alternative_care_access": 1,

    "care_management_contact_last_90_days": 1,

    "has_primary_care_provider": 1,

    "pcp_visits_last_12_months": 2,

    "days_since_last_pcp_visit": 30,

    # Patient information
    "age": 70,

    "condition": "Asthma",

    "diagnosis_category":
        "Respiratory"
}


# ============================================================
# CURRENT ENCOUNTER
# ============================================================

encounter_data = {

    # Current vitals
    "systolic_bp": 140,

    "diastolic_bp": 85,

    "heart_rate": 82,

    "temperature": 38.1,

    "respiratory_rate": 19,

    "oxygen_saturation": 96,

    # Current symptoms
    "symptom_fever_chills": 1,

    "symptom_cold_cough": 1,

    "symptom_vomiting": 0,

    "symptom_duration_days": 3,

    # Current barriers
    "barrier_no_insurance": 0,

    "barrier_after_hours_problem": 1,

    "transportation_barrier": 0,

    # Current clinical severity
    "severity": "Moderate",

    # Current triage
    "triage_acuity": 3
}


# ============================================================
# BUILD MODEL FEATURES
# ============================================================

features = build_prediction_features(
    patient,
    encounter_data
)


# ============================================================
# CHECK FEATURES
# ============================================================

print("\n" + "=" * 60)
print("FEATURE CHECK")
print("=" * 60)

print("FEATURE COUNT:", len(features))

null_features = [
    key
    for key, value in features.items()
    if value is None
]

print("NULL FEATURES:", null_features)


if len(features) != 30:

    raise ValueError(
        f"Expected 30 features, got {len(features)}"
    )


if null_features:

    raise ValueError(
        f"Missing feature values: {null_features}"
    )


print("\nAll 30 features are available.")


# ============================================================
# PRINT FEATURES
# ============================================================

print("\n" + "=" * 60)
print("MODEL FEATURES")
print("=" * 60)

for feature, value in features.items():

    print(
        f"{feature:<45} = {value}"
    )


# ============================================================
# CREATE DATAFRAME
# ============================================================

X = pd.DataFrame(
    [features],
    columns=FEATURES
)


print("\nDataFrame shape:", X.shape)


# ============================================================
# SHAP CALCULATION
# ============================================================

print("\n" + "=" * 60)
print("CALCULATING SHAP VALUES")
print("=" * 60)

shap_values = explainer.shap_values(X)


print("SHAP result type:", type(shap_values))


# ============================================================
# HANDLE SHAP OUTPUT
# ============================================================

if isinstance(shap_values, list):

    # Binary classification
    #
    # Class 0 = Non-Avoidable
    # Class 1 = Potentially Avoidable

    values = shap_values[1][0]

else:

    values = shap_values[0]


# ============================================================
# CHECK SHAP LENGTH
# ============================================================

print("SHAP feature count:", len(values))

if len(values) != len(FEATURES):

    raise ValueError(
        "SHAP values and model features have different lengths."
    )


# ============================================================
# CREATE EXPLANATION TABLE
# ============================================================

importance = pd.DataFrame({

    "feature": FEATURES,

    "shap_value": values
})


importance["absolute_shap"] = (
    importance["shap_value"].abs()
)


importance = importance.sort_values(
    "absolute_shap",
    ascending=False
)


# ============================================================
# TOP FEATURES
# ============================================================

print("\n" + "=" * 60)
print("TOP 10 SHAP FEATURES")
print("=" * 60)

print(
    importance[
        [
            "feature",
            "shap_value"
        ]
    ]
    .head(10)
    .to_string(index=False)
)


# ============================================================
# POSITIVE / NEGATIVE CONTRIBUTORS
# ============================================================

positive = (
    importance[
        importance["shap_value"] > 0
    ]
    .head(5)
)


negative = (
    importance[
        importance["shap_value"] < 0
    ]
    .sort_values(
        "shap_value",
        ascending=True
    )
    .head(5)
)


print("\n" + "=" * 60)
print("TOP POSITIVE CONTRIBUTORS")
print("=" * 60)

if len(positive) > 0:

    print(
        positive[
            ["feature", "shap_value"]
        ].to_string(index=False)
    )

else:

    print("No positive contributors.")


print("\n" + "=" * 60)
print("TOP NEGATIVE CONTRIBUTORS")
print("=" * 60)

if len(negative) > 0:

    print(
        negative[
            ["feature", "shap_value"]
        ].to_string(index=False)
    )

else:

    print("No negative contributors.")


# ============================================================
# COMPLETE
# ============================================================

print("\n" + "=" * 60)
print("SHAP TEST COMPLETE")
print("=" * 60)