from prediction_service import predict_patient


# ============================================================
# PATIENT 1 — LIKELY POTENTIALLY AVOIDABLE
# ============================================================

patient_1 = {

    # Past
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
    "barrier_no_insurance": "1",
    "barrier_after_hours_problem": "1",
    "transportation_barrier": "1",
    "alternative_care_access": "0",
    "has_primary_care_provider": "0"
}


# ============================================================
# PATIENT 2 — FEWER ACCESS BARRIERS
# ============================================================

patient_2 = {

    # Past
    "past_diagnosis_category_mode": "Respiratory",
    "triage_acuity": 4,
    "prior_ed_visits": 0,
    "ed_visits_last_30_days": 0,
    "ed_visits_last_90_days": 0,
    "days_since_last_ed_visit": 999,
    "care_management_contact_last_90_days": 2,
    "pcp_visits_last_12_months": 3,
    "days_since_last_pcp_visit": 30,

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
    "barrier_no_insurance": "0",
    "barrier_after_hours_problem": "0",
    "transportation_barrier": "0",
    "alternative_care_access": "1",
    "has_primary_care_provider": "1"
}


# ============================================================
# PATIENT 3 — HIGHER ACUITY
# ============================================================

patient_3 = {

    # Past
    "past_diagnosis_category_mode": "Cardiovascular",
    "triage_acuity": 1,
    "prior_ed_visits": 1,
    "ed_visits_last_30_days": 0,
    "ed_visits_last_90_days": 1,
    "days_since_last_ed_visit": 90,
    "care_management_contact_last_90_days": 1,
    "pcp_visits_last_12_months": 2,
    "days_since_last_pcp_visit": 45,

    # Current
    "age": 68,
    "gender": "Male",
    "region": "Urban",
    "condition": "Chest Pain",
    "diagnosis_category": "Cardiovascular",
    "severity": "Severe",

    "systolic_bp": 175,
    "diastolic_bp": 105,
    "heart_rate": 118,
    "temperature": 99.1,
    "respiratory_rate": 26,
    "oxygen_saturation": 91,

    "symptom_fever_chills": 0,
    "symptom_cold_cough": 0,
    "symptom_vomiting": 0,
    "symptom_duration_days": 1,

    # Barriers
    "barrier_no_insurance": "0",
    "barrier_after_hours_problem": "0",
    "transportation_barrier": "0",
    "alternative_care_access": "1",
    "has_primary_care_provider": "1"
}


# ============================================================
# TEST ALL PATIENTS
# ============================================================

patients = {
    "Patient 1 - Multiple Access Barriers": patient_1,
    "Patient 2 - Good Access": patient_2,
    "Patient 3 - High Acuity": patient_3
}


for name, patient in patients.items():

    print("\n" + "=" * 70)

    print(name)

    print("=" * 70)

    result = predict_patient(patient)

    print(
        f"Probability: "
        f"{result['potentially_avoidable_probability']}"
    )

    print(
        f"Prediction: "
        f"{result['prediction']}"
    )

    print(
        f"Classification: "
        f"{result['classification']}"
    )