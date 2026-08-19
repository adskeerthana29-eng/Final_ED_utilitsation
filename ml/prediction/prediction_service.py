# ============================================================
# UC07 — PREDICTION SERVICE
# ============================================================

import pandas as pd
from pathlib import Path

from catboost import CatBoostClassifier


# ============================================================
# 1. MODEL PATH
# ============================================================

BASE_DIR = Path(__file__).resolve().parents[2]

MODEL_FILE = (
    BASE_DIR
    / "ml"
    / "models"
    / "catboost_model.cbm"
)


# ============================================================
# 2. LOAD MODEL ONCE
# ============================================================

model = CatBoostClassifier()

model.load_model(MODEL_FILE)


# ============================================================
# 3. FEATURE ORDER
# ============================================================

FEATURES = [

    # -------------------------
    # PAST / HISTORICAL
    # -------------------------

    "past_diagnosis_category_mode",
    "prior_ed_visits",
    "ed_visits_last_30_days",
    "ed_visits_last_90_days",
    "days_since_last_ed_visit",
    "triage_acuity",
    "care_management_contact_last_90_days",
    "pcp_visits_last_12_months",
    "days_since_last_pcp_visit",

    # -------------------------
    # CURRENT
    # -------------------------

    "age",
    "gender",
    "region",
    "condition",
    "diagnosis_category",
    "severity",

    "systolic_bp",
    "diastolic_bp",
    "heart_rate",
    "temperature",
    "respiratory_rate",
    "oxygen_saturation",

    "symptom_fever_chills",
    "symptom_cold_cough",
    "symptom_vomiting",
    "symptom_duration_days",

    "barrier_no_insurance",
    "barrier_after_hours_problem",
    "transportation_barrier",

    "alternative_care_access",
    "has_primary_care_provider"
]


# ============================================================
# 4. CATEGORICAL FEATURES
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


# ============================================================
# 5. PREDICT FUNCTION
# ============================================================

def predict_patient(patient):

    # --------------------------------------------------------
    # Check missing features
    # --------------------------------------------------------

    missing_features = [
        feature
        for feature in FEATURES
        if feature not in patient
    ]

    if missing_features:

        raise ValueError(
            "Missing patient features:\n"
            + "\n".join(missing_features)
        )


    # --------------------------------------------------------
    # Validate triage_acuity (must be integer 1-5)
    # --------------------------------------------------------

    try:

        acuity_value = int(
            patient["triage_acuity"]
        )

    except (ValueError, TypeError):

        raise ValueError(
            "triage_acuity must be an integer 1-5, got: "
            f"{patient['triage_acuity']!r}"
        )

    if acuity_value not in [1, 2, 3, 4, 5]:

        raise ValueError(
            "triage_acuity must be between 1 and 5, got: "
            f"{acuity_value}"
        )


    # --------------------------------------------------------
    # Validate binary fields (must be 0 or 1)
    # --------------------------------------------------------

    BINARY_FIELDS = [
        "symptom_fever_chills",
        "symptom_cold_cough",
        "symptom_vomiting",
        "barrier_no_insurance",
        "barrier_after_hours_problem",
        "transportation_barrier",
        "alternative_care_access",
        "has_primary_care_provider"
    ]

    for field in BINARY_FIELDS:

        if str(patient[field]).strip() not in ["0", "1"]:

            raise ValueError(
                f"{field} must be 0 or 1, got: "
                f"{patient[field]!r}"
            )


    # --------------------------------------------------------
    # Create DataFrame
    # --------------------------------------------------------

    X = pd.DataFrame(
        [patient],
        columns=FEATURES
    )


    # --------------------------------------------------------
    # Convert categorical values to strings
    # --------------------------------------------------------

    for column in CATEGORICAL_FEATURES:

        X[column] = (
            X[column]
            .fillna("Unknown")
            .astype(str)
        )


    # --------------------------------------------------------
    # Prediction probability
    # --------------------------------------------------------

    probability = float(
        model.predict_proba(X)[0][1]
    )


    # --------------------------------------------------------
    # Prediction
    # --------------------------------------------------------

    prediction = int(
        probability >= 0.50
    )


    # --------------------------------------------------------
    # Result
    # --------------------------------------------------------

    return {

        "potentially_avoidable_probability":
            round(probability, 4),

        "prediction":
            prediction,

        "classification":
            (
                "Potentially Avoidable"
                if prediction == 1
                else "Non-Avoidable"
            )
    }