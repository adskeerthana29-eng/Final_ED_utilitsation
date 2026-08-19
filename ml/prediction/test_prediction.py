from feature_builder import build_prediction_features
from prediction_service import predict_patient

patient = {
    "patient_id": "P-FE8F2ED3",
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

    "age": 70,
    "condition": "Asthma",
    "diagnosis_category": "Respiratory",
}


encounter_data = {
    "systolic_bp": 140,
    "diastolic_bp": 85,
    "heart_rate": 82,
    "temperature": 38.1,
    "respiratory_rate": 19,
    "oxygen_saturation": 96,

    "symptom_fever_chills": 1,
    "symptom_cold_cough": 1,
    "symptom_vomiting": 0,
    "symptom_duration_days": 3,

    "barrier_no_insurance": 0,
    "barrier_after_hours_problem": 1,
    "transportation_barrier": 0,

    "severity": "Moderate",
    "triage_acuity": 3,
}


# --------------------------------------------------
# STEP 1 — BUILD MODEL INPUT
# --------------------------------------------------

features = build_prediction_features(
    patient,
    encounter_data
)

print("=" * 60)
print("CATBOOST PREDICTION TEST")
print("=" * 60)

print("FEATURE COUNT:", len(features))

missing = [
    key for key, value in features.items()
    if value is None
]

print("NULL FEATURES:", missing)


# --------------------------------------------------
# STEP 2 — SEND ONLY MODEL FEATURES TO CATBOOST
# --------------------------------------------------

result = predict_patient(features)


# --------------------------------------------------
# STEP 3 — DISPLAY RESULT
# --------------------------------------------------

print("\nMODEL RESULT")
print("-" * 60)

print(
    "Potentially Avoidable Probability:",
    result["potentially_avoidable_probability"]
)

print(
    "Prediction:",
    result["prediction"]
)

print(
    "Classification:",
    result["classification"]
)