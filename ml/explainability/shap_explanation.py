# ============================================================
# UC07 — SHAP EXPLAINABILITY
# ============================================================

import pandas as pd
from pathlib import Path
from catboost import CatBoostClassifier, Pool


# ============================================================
# 1. PROJECT PATH
# ============================================================

BASE_DIR = Path(__file__).resolve().parents[2]


# ============================================================
# 2. MODEL
# ============================================================

MODEL_FILE = (
    BASE_DIR
    / "ml"
    / "models"
    / "catboost_model.cbm"
)

model = CatBoostClassifier()
model.load_model(MODEL_FILE)


# ============================================================
# 3. FEATURES
# ============================================================

FEATURES = [
    "past_diagnosis_category_mode",
    "prior_ed_visits",
    "ed_visits_last_30_days",
    "ed_visits_last_90_days",
    "days_since_last_ed_visit",
    "triage_acuity",
    "care_management_contact_last_90_days",
    "pcp_visits_last_12_months",
    "days_since_last_pcp_visit",

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
# 5. EXPLAIN PATIENT
# ============================================================

def explain_patient(patient, top_n=5):

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
    # Create DataFrame
    # --------------------------------------------------------

    X = pd.DataFrame(
        [patient],
        columns=FEATURES
    )


    # --------------------------------------------------------
    # Handle categorical features
    # --------------------------------------------------------

    for column in CATEGORICAL_FEATURES:

        X[column] = (
            X[column]
            .fillna("Unknown")
            .astype(str)
        )


    # --------------------------------------------------------
    # CatBoost Pool
    # --------------------------------------------------------

    pool = Pool(
        data=X,
        cat_features=CATEGORICAL_FEATURES
    )


    # --------------------------------------------------------
    # SHAP values
    # --------------------------------------------------------

    shap_values = model.get_feature_importance(
        data=pool,
        type="ShapValues"
    )


    # --------------------------------------------------------
    # Feature SHAP values
    # --------------------------------------------------------

    feature_shap_values = shap_values[0][:-1]


    # --------------------------------------------------------
    # Build explanation table
    # --------------------------------------------------------

    explanation = pd.DataFrame({
        "feature": FEATURES,
        "feature_value": X.iloc[0].values,
        "shap_value": feature_shap_values
    })


    # --------------------------------------------------------
    # Importance
    # --------------------------------------------------------

    explanation["importance"] = (
        explanation["shap_value"].abs()
    )


    # --------------------------------------------------------
    # Sort
    # --------------------------------------------------------

    explanation = explanation.sort_values(
        "importance",
        ascending=False
    )


    # --------------------------------------------------------
    # Top SHAP features
    # --------------------------------------------------------

    top_features = explanation.head(top_n)


    # ========================================================
    # Convert SHAP values into readable reasons
    # ========================================================

    reasons = []

    for _, row in top_features.iterrows():

        shap_value = float(row["shap_value"])

        direction = (
            "increases"
            if shap_value > 0
            else "decreases"
        )

        reasons.append({

            "feature": str(row["feature"]),

            "value": row["feature_value"],

            "shap_value": round(
                shap_value,
                4
            ),

            "direction": direction,

            "impact": round(
                abs(shap_value),
                4
            )
        })


    # ========================================================
    # Return structured result
    # ========================================================

    return {
        "top_features": reasons
    }


# ============================================================
# 6. TEST
# ============================================================

if __name__ == "__main__":

    test_patient = {

        "past_diagnosis_category_mode": "Cardiovascular",
        "prior_ed_visits": 2,
        "ed_visits_last_30_days": 1,
        "ed_visits_last_90_days": 3,
        "days_since_last_ed_visit": 20,
        "triage_acuity": 3,
        "care_management_contact_last_90_days": 1,
        "pcp_visits_last_12_months": 2,
        "days_since_last_pcp_visit": 30,

        "age": 45,
        "gender": "Female",
        "region": "South",
        "condition": "Type 2 Diabetes",
        "diagnosis_category": "Endocrine",
        "severity": "Moderate",

        "systolic_bp": 130,
        "diastolic_bp": 80,
        "heart_rate": 78,
        "temperature": 98.6,
        "respiratory_rate": 18,
        "oxygen_saturation": 98,

        "symptom_fever_chills": 0,
        "symptom_cold_cough": 0,
        "symptom_vomiting": 0,
        "symptom_duration_days": 2,

        "barrier_no_insurance": 0,
        "barrier_after_hours_problem": 0,
        "transportation_barrier": 0,

        "alternative_care_access": 1,
        "has_primary_care_provider": 1
    }


    result = explain_patient(
        test_patient,
        top_n=5
    )


    print("\nSHAP Explanation")
    print("================")

    for reason in result["top_features"]:

        print(
            f"{reason['feature']} | "
            f"Value: {reason['value']} | "
            f"SHAP: {reason['shap_value']} | "
            f"Direction: {reason['direction']}"
        )