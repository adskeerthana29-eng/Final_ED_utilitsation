# ============================================================
# UC07 — NAVIGATION RULES
# ============================================================
#
# ML prediction:
#   potentially_avoidable_probability
#
# Navigation barriers:
#   - No insurance
#   - After-hours problem
#   - Transportation barrier
#   - No PCP
#   - No alternative-care access
#
# Clinical safety:
#   - Triage acuity: 1–5
#   - Severity: Mild / Moderate / Severe
#   - Oxygen saturation
#   - Heart rate
#   - Systolic BP
#
# IMPORTANT:
# This system supports FUTURE CARE NAVIGATION.
# It must NOT tell a patient to avoid emergency care.
# ============================================================


# ============================================================
# 1. CLINICAL SAFETY CHECK
# ============================================================

def clinical_safety_check(patient):

    safety_reasons = []


    # ========================================================
    # TRIAGE ACUITY
    # ========================================================
    #
    # Your dataset uses:
    #
    # 1 = highest urgency
    # 5 = lowest urgency
    #
    # Therefore:
    # 1 and 2 -> safety review
    #
    # ========================================================

    triage_acuity = patient.get(
        "triage_acuity"
    )

    if triage_acuity is not None:

        try:

            triage_acuity = int(
                triage_acuity
            )

            if triage_acuity in [1, 2]:

                safety_reasons.append(
                    f"High-priority triage acuity "
                    f"({triage_acuity})"
                )

        except (
            ValueError,
            TypeError
        ):

            safety_reasons.append(
                "Unable to parse triage acuity — "
                "flagged for manual review"
            )


    # ========================================================
    # SEVERITY
    # ========================================================
    #
    # Dataset values:
    # Mild
    # Moderate
    # Severe
    #
    # Severe severity -> safety review
    # ========================================================

    severity = str(
        patient.get(
            "severity",
            ""
        )
    ).strip().lower()


    if severity == "severe":

        safety_reasons.append(
            "High severity"
        )


    # ========================================================
    # OXYGEN SATURATION
    # ========================================================

    oxygen = patient.get(
        "oxygen_saturation"
    )


    if oxygen is not None:

        try:

            oxygen = float(
                oxygen
            )

            if oxygen < 92:

                safety_reasons.append(
                    "Low oxygen saturation"
                )

        except (
            ValueError,
            TypeError
        ):

            pass


    # ========================================================
    # HEART RATE
    # ========================================================

    heart_rate = patient.get(
        "heart_rate"
    )


    if heart_rate is not None:

        try:

            heart_rate = float(
                heart_rate
            )

            if heart_rate > 120:

                safety_reasons.append(
                    "Elevated heart rate"
                )

        except (
            ValueError,
            TypeError
        ):

            pass


    # ========================================================
    # SYSTOLIC BLOOD PRESSURE
    # ========================================================

    systolic_bp = patient.get(
        "systolic_bp"
    )


    if systolic_bp is not None:

        try:

            systolic_bp = float(
                systolic_bp
            )

            if systolic_bp >= 180:

                safety_reasons.append(
                    "Very high systolic blood pressure"
                )

        except (
            ValueError,
            TypeError
        ):

            pass


    # ========================================================
    # FINAL SAFETY RESULT
    # ========================================================

    return {

        "safety_flag":
            len(safety_reasons) > 0,

        "reasons":
            safety_reasons
    }


# ============================================================
# 2. IDENTIFY NAVIGATION BARRIERS
# ============================================================

def identify_navigation_barriers(patient):

    barriers = []


    # ========================================================
    # NO INSURANCE
    # ========================================================

    if str(
        patient.get(
            "barrier_no_insurance",
            0
        )
    ).strip() == "1":

        barriers.append({

            "barrier":
                "No insurance",

            "reason":
                "The patient reports an insurance barrier.",

            "navigation":
                "Review available insurance coverage "
                "and financial assistance resources."
        })


    # ========================================================
    # AFTER-HOURS PROBLEM
    # ========================================================

    if str(
        patient.get(
            "barrier_after_hours_problem",
            0
        )
    ).strip() == "1":

        barriers.append({

            "barrier":
                "After-hours access problem",

            "reason":
                "The patient reports difficulty "
                "accessing care after normal hours.",

            "navigation":
                "TELEHEALTH"
        })


    # ========================================================
    # TRANSPORTATION BARRIER
    # ========================================================

    if str(
        patient.get(
            "transportation_barrier",
            0
        )
    ).strip() == "1":

        barriers.append({

            "barrier":
                "Transportation barrier",

            "reason":
                "Transportation may limit access "
                "to other care settings.",

            "navigation":
                "TELEHEALTH "
                "assistance and accessible care options."
        })


    # ========================================================
    # NO PRIMARY CARE PROVIDER
    # ========================================================

    if str(
        patient.get(
            "has_primary_care_provider",
            0
        )
    ).strip() == "0":

        barriers.append({

            "barrier":
                "No primary care provider",

            "reason":
                "The patient does not currently "
                "have an established primary care provider.",

            "navigation":
                "Support connection with an appropriate "
                "primary care provider."
        })


    # ========================================================
    # NO ALTERNATIVE CARE ACCESS
    # ========================================================

    if str(
        patient.get(
            "alternative_care_access",
            0
        )
    ).strip() == "0":

        barriers.append({

            "barrier":
                "Limited alternative-care access",

            "reason":
                "The patient reports no available "
                "alternative care access.",

            "navigation":
                "Help identify appropriate primary care, "
                "urgent care, or telehealth options "
                "when clinically appropriate."
        })


    return barriers


# ============================================================
# 3. MAIN NAVIGATION FUNCTION
# ============================================================

def generate_navigation(
    patient,
    prediction_result
):

    # ========================================================
    # GET MODEL RESULT
    # ========================================================

    probability = float(
        prediction_result[
            "potentially_avoidable_probability"
        ]
    )


    prediction = int(
        prediction_result[
            "prediction"
        ]
    )


    classification = (
        prediction_result[
            "classification"
        ]
    )


    # ========================================================
    # STEP 1 — CLINICAL SAFETY CHECK
    # ========================================================

    safety_result = clinical_safety_check(
        patient
    )


    # ========================================================
    # STEP 2 — SAFETY OVERRIDE
    # ========================================================
    #
    # Safety comes before navigation.
    #
    # If the patient has high-priority triage,
    # high severity, or concerning vitals,
    # do NOT generate avoidability navigation.
    #
    # ========================================================

    if safety_result[
        "safety_flag"
    ]:

        return {

            "probability":
                probability,

            "prediction":
                prediction,

            "classification":
                classification,

            "navigation_status":
                "Clinical safety review",

            "safety_flag":
                True,

            "safety_reasons":
                safety_result[
                    "reasons"
                ],

            "barriers":
                [],

            "reasons":
                safety_result[
                    "reasons"
                ],

            "navigation_actions": [

                "Do not use the avoidability "
                "prediction to discourage emergency care.",

                "Follow appropriate clinical "
                "evaluation and escalation procedures."
            ]
        }


    # ========================================================
    # STEP 3 — MODEL PREDICTS NON-AVOIDABLE
    # ========================================================

    if prediction == 0:

        return {

            "probability":
                probability,

            "prediction":
                prediction,

            "classification":
                "Non-Avoidable",

            "navigation_status":
                "No potentially-avoidable navigation trigger",

            "safety_flag":
                False,

            "safety_reasons":
                [],

            "barriers":
                [],

            "reasons":
                [],

            "navigation_actions":
                []
        }


    # ========================================================
    # STEP 4 — MODEL PREDICTS POTENTIALLY AVOIDABLE
    # ========================================================

    barriers = identify_navigation_barriers(
        patient
    )


    # ========================================================
    # STEP 5 — EXTRACT REASONS
    # ========================================================

    reasons = [

        item["reason"]

        for item in barriers
    ]


    # ========================================================
    # STEP 6 — EXTRACT NAVIGATION ACTIONS
    # ========================================================

    navigation_actions = [

        item["navigation"]

        for item in barriers
    ]


    # ========================================================
    # STEP 7 — FINAL NAVIGATION RESULT
    # ========================================================

    return {

        "probability":
            probability,

        "prediction":
            prediction,

        "classification":
            "Potentially Avoidable",

        "navigation_status":
            "Navigation review recommended",

        "safety_flag":
            False,

        "safety_reasons":
            [],

        "barriers": [

            item["barrier"]

            for item in barriers
        ],

        "reasons":
            reasons,

        "navigation_actions":
            navigation_actions
    }