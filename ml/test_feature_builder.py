from prediction.feature_builder import build_prediction_features


patient = {
    "patient_id": "P-FE8F2ED3",

    # Historical
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
    "diagnosis_category": "Respiratory",
}


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

    # Current severity
    "severity": "Moderate",

    # Current triage
    "triage_acuity": 3,
}


features = build_prediction_features(
    patient,
    encounter_data
)


print("=" * 60)
print("FEATURE BUILDER TEST")
print("=" * 60)

print("FEATURE COUNT:", len(features))

print("\nFEATURES:")
for key, value in features.items():
    print(f"{key:40} = {value}")


print("\nNULL FEATURES:")

missing = [
    key
    for key, value in features.items()
    if value is None
]

print(missing)

print("\nTEST RESULT:")

if len(features) != 30:
    print("[FAIL] Expected 30 features")

elif missing:
    print("[FAIL] Missing feature values:")
    print(missing)

else:
    print("[PASS] All 30 model features are available")