
# UC07 — COMPLETE NAVIGATION TEST

from navigation_service import (
    navigate_patient
)


# PATIENT 1
#
# Expected:
# High potentially-avoidable probability
# Multiple navigation barriers


patient_1 = {

    
    "past_diagnosis_category_mode":
        "Respiratory",

    "triage_acuity":
        4,

    "prior_ed_visits":
        3,

    "ed_visits_last_30_days":
        2,

    "ed_visits_last_90_days":
        4,

    "days_since_last_ed_visit":
        15,

    "care_management_contact_last_90_days":
        0,

    "pcp_visits_last_12_months":
        0,

    "days_since_last_pcp_visit":
        365,


    # --------------------------------------------------------
    # CURRENT
    # --------------------------------------------------------

    "age":
        45,

    "gender":
        "Female",

    "region":
        "Urban",

    "condition":
        "Cough",

    "diagnosis_category":
        "Respiratory",

    "severity":
        "Mild",


    # --------------------------------------------------------
    # VITALS
    # --------------------------------------------------------

    "systolic_bp":
        120,

    "diastolic_bp":
        80,

    "heart_rate":
        78,

    "temperature":
        98.4,

    "respiratory_rate":
        16,

    "oxygen_saturation":
        98,


    # --------------------------------------------------------
    # SYMPTOMS
    # --------------------------------------------------------

    "symptom_fever_chills":
        0,

    "symptom_cold_cough":
        1,

    "symptom_vomiting":
        0,

    "symptom_duration_days":
        3,


    # --------------------------------------------------------
    # BARRIERS
    # --------------------------------------------------------

    "barrier_no_insurance":
        1,

    "barrier_after_hours_problem":
        1,

    "transportation_barrier":
        1,

    "alternative_care_access":
        0,

    "has_primary_care_provider":
        0
}


# ============================================================
# PATIENT 2
#
# Expected:
# Low potentially-avoidable probability
# No navigation trigger
# ============================================================

patient_2 = {

    # --------------------------------------------------------
    # PAST
    # --------------------------------------------------------

    "past_diagnosis_category_mode":
        "Respiratory",

    "triage_acuity":
        4,

    "prior_ed_visits":
        0,

    "ed_visits_last_30_days":
        0,

    "ed_visits_last_90_days":
        0,

    "days_since_last_ed_visit":
        999,

    "care_management_contact_last_90_days":
        2,

    "pcp_visits_last_12_months":
        3,

    "days_since_last_pcp_visit":
        30,


    # --------------------------------------------------------
    # CURRENT
    # --------------------------------------------------------

    "age":
        45,

    "gender":
        "Female",

    "region":
        "Urban",

    "condition":
        "Cough",

    "diagnosis_category":
        "Respiratory",

    "severity":
        "Mild",


    # --------------------------------------------------------
    # VITALS
    # --------------------------------------------------------

    "systolic_bp":
        120,

    "diastolic_bp":
        80,

    "heart_rate":
        78,

    "temperature":
        98.4,

    "respiratory_rate":
        16,

    "oxygen_saturation":
        98,


    # --------------------------------------------------------
    # SYMPTOMS
    # --------------------------------------------------------

    "symptom_fever_chills":
        0,

    "symptom_cold_cough":
        1,

    "symptom_vomiting":
        0,

    "symptom_duration_days":
        3,


    # --------------------------------------------------------
    # BARRIERS
    # --------------------------------------------------------

    "barrier_no_insurance":
        0,

    "barrier_after_hours_problem":
        0,

    "transportation_barrier":
        0,

    "alternative_care_access":
        1,

    "has_primary_care_provider":
        1
}


# ============================================================
# PATIENT 3
#
# Expected:
# Clinical safety review
#
# High-priority triage + high severity +
# concerning vital signs.
# ============================================================

patient_3 = {

    # --------------------------------------------------------
    # PAST
    # --------------------------------------------------------

    "past_diagnosis_category_mode":
        "Cardiovascular",

    "triage_acuity":
        1,

    "prior_ed_visits":
        1,

    "ed_visits_last_30_days":
        0,

    "ed_visits_last_90_days":
        1,

    "days_since_last_ed_visit":
        90,

    "care_management_contact_last_90_days":
        1,

    "pcp_visits_last_12_months":
        2,

    "days_since_last_pcp_visit":
        45,


    # --------------------------------------------------------
    # CURRENT
    # --------------------------------------------------------

    "age":
        68,

    "gender":
        "Male",

    "region":
        "Urban",

    "condition":
        "Chest Pain",

    "diagnosis_category":
        "Cardiovascular",

    "severity":
        "Severe",


    # --------------------------------------------------------
    # VITALS
    # --------------------------------------------------------

    "systolic_bp":
        185,

    "diastolic_bp":
        105,

    "heart_rate":
        125,

    "temperature":
        99.1,

    "respiratory_rate":
        26,

    "oxygen_saturation":
        91,


    # --------------------------------------------------------
    # SYMPTOMS
    # --------------------------------------------------------

    "symptom_fever_chills":
        0,

    "symptom_cold_cough":
        0,

    "symptom_vomiting":
        0,

    "symptom_duration_days":
        1,


    # --------------------------------------------------------
    # BARRIERS
    # --------------------------------------------------------

    "barrier_no_insurance":
        0,

    "barrier_after_hours_problem":
        0,

    "transportation_barrier":
        0,

    "alternative_care_access":
        1,

    "has_primary_care_provider":
        1
}


# ============================================================
# PRINT FUNCTION
# ============================================================

def print_result(
    patient_name,
    result
):

    print("\n")
    print("=" * 70)

    print(
        patient_name
    )

    print("=" * 70)

    print(
        f"Probability: "
        f"{result['probability']:.4f}"
    )

    print(
        f"Prediction: "
        f"{result['prediction']}"
    )

    print(
        f"Classification: "
        f"{result['classification']}"
    )

    print(
        f"Navigation Status: "
        f"{result['navigation_status']}"
    )

    print(
        f"Safety Flag: "
        f"{result['safety_flag']}"
    )


    # --------------------------------------------------------
    # SAFETY REASONS
    # --------------------------------------------------------

    if result["safety_reasons"]:

        print("\nSafety Reasons:")

        for reason in result[
            "safety_reasons"
        ]:

            print(
                f"  • {reason}"
            )


    # --------------------------------------------------------
    # BARRIERS
    # --------------------------------------------------------

    if result["barriers"]:

        print("\nNavigation Barriers:")

        for barrier in result[
            "barriers"
        ]:

            print(
                f"  • {barrier}"
            )


    # --------------------------------------------------------
    # REASONS
    # --------------------------------------------------------

    if result["reasons"]:

        print("\nReasons:")

        for reason in result[
            "reasons"
        ]:

            print(
                f"  • {reason}"
            )


    # --------------------------------------------------------
    # ACTIONS
    # --------------------------------------------------------

    if result[
        "navigation_actions"
    ]:

        print(
            "\nNavigation Actions:"
        )

        for action in result[
            "navigation_actions"
        ]:

            print(
                f"  • {action}"
            )


# ============================================================
# RUN PATIENT 1
# ============================================================

result_1 = navigate_patient(
    patient_1
)

print_result(
    "PATIENT 1 — MULTIPLE ACCESS BARRIERS",
    result_1
)


# ============================================================
# RUN PATIENT 2
# ============================================================

result_2 = navigate_patient(
    patient_2
)

print_result(
    "PATIENT 2 — GOOD ACCESS",
    result_2
)


# ============================================================
# RUN PATIENT 3
# ============================================================

result_3 = navigate_patient(
    patient_3
)

print_result(
    "PATIENT 3 — HIGH CLINICAL PRIORITY",
    result_3
)