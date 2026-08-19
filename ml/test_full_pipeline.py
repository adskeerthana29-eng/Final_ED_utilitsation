# ============================================================
# UC07 — FULL PIPELINE TEST
#
# Runs ONE patient through the entire system:
#
#   1. CatBoost prediction
#   2. Navigation rules (safety + barriers)
#   3. SHAP explanation (why the model predicted this)
#
# This ties together what test_patients.py, test_navigation.py,
# and shap_explanation.py each test separately.
# ============================================================

import sys
from pathlib import Path


# ============================================================
# 1. MAKE ALL SUBMODULES IMPORTABLE
# ============================================================

BASE_DIR = Path(__file__).resolve().parent

sys.path.insert(0, str(BASE_DIR / "prediction"))
sys.path.insert(0, str(BASE_DIR / "navigation"))
sys.path.insert(0, str(BASE_DIR / "explainability"))


from prediction_service import predict_patient
from navigation_service import navigate_patient
from shap_explanation import explain_patient


# ============================================================
# 2. TEST PATIENT
#
# Change these values to test different scenarios.
# Must match the training schema:
#   triage_acuity        -> int 1-5   (1 = most urgent)
#   symptom_* fields      -> int 0/1
#   barrier_*/access/pcp  -> int or "0"/"1"
#   severity              -> "Mild" / "Moderate" / "Severe"
# ============================================================

patient = {

    # Past / historical
    "past_diagnosis_category_mode": "Respiratory",
    "triage_acuity": 4,
    "prior_ed_visits": 3,
    "ed_visits_last_30_days": 2,
    "ed_visits_last_90_days": 4,
    "days_since_last_ed_visit": 15,
    "care_management_contact_last_90_days": 0,
    "pcp_visits_last_12_months": 0,
    "days_since_last_pcp_visit": 365,

    # Current
    "age": 45,
    "gender": "Female",
    "region": "Urban",
    "condition": "Cough",
    "diagnosis_category": "Respiratory",
    "severity": "Mild",

    "systolic_bp": 120,
    "diastolic_bp": 80,
    "heart_rate": 78,
    "temperature": 98.4,
    "respiratory_rate": 16,
    "oxygen_saturation": 98,

    "symptom_fever_chills": 0,
    "symptom_cold_cough": 1,
    "symptom_vomiting": 0,
    "symptom_duration_days": 3,

    # Barriers
    "barrier_no_insurance": 1,
    "barrier_after_hours_problem": 1,
    "transportation_barrier": 1,
    "alternative_care_access": 0,
    "has_primary_care_provider": 0
}


# ============================================================
# 3. RUN PREDICTION
# ============================================================

print("=" * 70)
print("STEP 1 — PREDICTION")
print("=" * 70)

prediction_result = predict_patient(patient)

print(f"Probability   : {prediction_result['potentially_avoidable_probability']}")
print(f"Prediction    : {prediction_result['prediction']}")
print(f"Classification: {prediction_result['classification']}")


# ============================================================
# 4. RUN NAVIGATION
# ============================================================

print("\n" + "=" * 70)
print("STEP 2 — NAVIGATION")
print("=" * 70)

navigation_result = navigate_patient(patient)

print(f"Navigation Status: {navigation_result['navigation_status']}")
print(f"Safety Flag      : {navigation_result['safety_flag']}")

if navigation_result["safety_reasons"]:
    print("\nSafety Reasons:")
    for reason in navigation_result["safety_reasons"]:
        print(f"  • {reason}")

if navigation_result["barriers"]:
    print("\nNavigation Barriers:")
    for barrier in navigation_result["barriers"]:
        print(f"  • {barrier}")

if navigation_result["navigation_actions"]:
    print("\nNavigation Actions:")
    for action in navigation_result["navigation_actions"]:
        print(f"  • {action}")


# ============================================================
# 5. RUN SHAP EXPLANATION
# ============================================================

print("\n" + "=" * 70)
print("STEP 3 — SHAP EXPLANATION (why the model predicted this)")
print("=" * 70)

shap_result = explain_patient(patient, top_n=5)

for reason in shap_result["top_features"]:
    print(
        f"{reason['feature']:<35} | "
        f"Value: {str(reason['value']):<12} | "
        f"SHAP: {reason['shap_value']:>8} | "
        f"{reason['direction']} avoidability"
    )


# ============================================================
# 6. FINAL SUMMARY
# ============================================================

print("\n" + "=" * 70)
print("SUMMARY")
print("=" * 70)

print(
    f"\nThis patient is classified as "
    f"'{prediction_result['classification']}' "
    f"(probability {prediction_result['potentially_avoidable_probability']})."
)

print(
    f"Navigation outcome: {navigation_result['navigation_status']}."
)

print(
    f"Top SHAP driver: "
    f"{shap_result['top_features'][0]['feature']} "
    f"({shap_result['top_features'][0]['direction']} avoidability, "
    f"impact {shap_result['top_features'][0]['impact']})."
)