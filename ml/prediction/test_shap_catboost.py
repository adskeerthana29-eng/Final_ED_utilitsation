import sys
from pathlib import Path

# ============================================================
# PROJECT PATH
# ============================================================

# test_shap_catboost.py
#   -> ml
#      -> prediction
#
# parents[0] = ml/prediction
# parents[1] = ml
# parents[2] = project root

BASE_DIR = Path(__file__).resolve().parents[2]

ML_DIR = BASE_DIR / "ml"

# Make Python find the prediction package
sys.path.insert(0, str(BASE_DIR))
sys.path.insert(0, str(ML_DIR))


# ============================================================
# IMPORTS
# ============================================================

from prediction.feature_builder import build_prediction_features
from prediction.shap_service import get_top_shap_features


# ============================================================
# TEST PATIENT
# ============================================================

patient = {

    "patient_id": "P-FE8F2ED3",

    # Historical information
    "gender": "Female",
    "region": "South",
    "past_diagnosis_category_mode": "Respiratory",

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

    # Patient information required by model
    "age": 70,

    "condition": "Asthma",

    "diagnosis_category": "Respiratory"
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

    # Current clinical information
    "severity": "Moderate",

    "triage_acuity": 3
}


# ============================================================
# BUILD MODEL FEATURES
# ============================================================

print("=" * 60)
print("CATBOOST SHAP TEST")
print("=" * 60)

print("\nBUILDING FEATURES...")


features = build_prediction_features(
    patient,
    encounter_data
)


# ============================================================
# FEATURE COUNT
# ============================================================

print("\nFEATURE COUNT:", len(features))


# ============================================================
# NULL CHECK
# ============================================================

null_features = [
    key
    for key, value in features.items()
    if value is None
]


print("NULL FEATURES:", null_features)


if null_features:

    print(
        "\n[FAIL] SHAP TEST FAILED"
    )

    print(
        "Missing features:"
    )

    for feature in null_features:
        print(" -", feature)

    sys.exit(1)


print(
    "\n[OK] All 30 features are available."
)


# ============================================================
# PRINT FEATURES
# ============================================================

print("\nMODEL FEATURES")
print("-" * 60)

for feature, value in features.items():

    print(
        f"{feature:<45} = {value}"
    )


# ============================================================
# SHAP CALCULATION
# ============================================================

print("\n" + "=" * 60)
print("CALCULATING SHAP")
print("=" * 60)


try:

    top_features = get_top_shap_features(
        features,
        top_n=10
    )

except Exception as e:

    print("\n[FAIL] SHAP CALCULATION FAILED")

    print("Error:", e)

    print(
        "\nCheck that shap_service.py "
        "is loading ml/models/catboost_model.cbm"
    )

    sys.exit(1)


# ============================================================
# DISPLAY SHAP RESULTS
# ============================================================

print("\nTOP SHAP FEATURES")
print("-" * 60)


print(
    top_features[
        [
            "feature",
            "shap_value",
            "absolute_shap"
        ]
    ].to_string(index=False)
)


# ============================================================
# POSITIVE / NEGATIVE CONTRIBUTIONS
# ============================================================

print("\n" + "=" * 60)
print("SHAP INTERPRETATION")
print("=" * 60)


positive = top_features[
    top_features["shap_value"] > 0
]

negative = top_features[
    top_features["shap_value"] < 0
]


print("\nFEATURES INCREASING AVOIDABILITY")
print("-" * 60)

if len(positive) == 0:

    print("None among top features.")

else:

    for _, row in positive.iterrows():

        print(
            f"{row['feature']}: "
            f"{row['shap_value']:.6f}"
        )


print("\nFEATURES DECREASING AVOIDABILITY")
print("-" * 60)

if len(negative) == 0:

    print("None among top features.")

else:

    for _, row in negative.iterrows():

        print(
            f"{row['feature']}: "
            f"{row['shap_value']:.6f}"
        )


# ============================================================
# COMPLETE
# ============================================================

print("\n" + "=" * 60)
print("[OK] SHAP TEST COMPLETE")
print("=" * 60)