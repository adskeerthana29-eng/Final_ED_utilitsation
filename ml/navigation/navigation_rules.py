"""
Navigation Rules for Avoidable ED Utilization

Purpose
-------
Convert the ML avoidability prediction + current clinical safety information
+ access barriers into a care-navigation recommendation.

IMPORTANT
---------
This module does NOT diagnose the patient and does NOT decide whether a
patient should or should not use emergency care.

The ML model identifies a pattern that MAY be associated with potentially
avoidable ED utilization.

The navigation layer:
    1. Performs a safety screen.
    2. Categorizes model confidence.
    3. Identifies access barriers.
    4. Suggests appropriate care-navigation options.
    5. Leaves the final decision to the care manager.

Emergency symptoms / concerning clinical findings always take priority
over the avoidability prediction.
"""

from typing import Any, Dict, List, Optional


# ---------------------------------------------------------------------------
# CONFIGURATION
# ---------------------------------------------------------------------------

# Model probability thresholds.
#
# These are PROJECT DESIGN thresholds, not clinically validated thresholds.
# They should be validated with appropriate clinical/business stakeholders
# before production use.
LOW_RISK_THRESHOLD = 0.40
HIGH_RISK_THRESHOLD = 0.60

# Safety thresholds.
#
# These are intentionally conservative project-level screening rules.
# They are NOT diagnostic criteria.
LOW_OXYGEN_SATURATION = 92
HIGH_HEART_RATE = 120
HIGH_SYSTOLIC_BP = 180

HIGH_ACUITY_LEVELS = {1, 2}
SEVERE_LEVELS = {"severe", "critical", "high"}


# ---------------------------------------------------------------------------
# HELPER FUNCTIONS
# ---------------------------------------------------------------------------

def _safe_float(value: Any) -> Optional[float]:
    """
    Safely convert a value to float.

    Returns None if the value is missing or invalid.
    """
    if value is None:
        return None

    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _safe_int(value: Any) -> Optional[int]:
    """
    Safely convert a value to integer.

    Returns None if the value is missing or invalid.
    """
    if value is None:
        return None

    try:
        return int(float(value))
    except (TypeError, ValueError):
        return None


def _normalise_text(value: Any) -> str:
    """
    Normalize text for comparisons.
    """
    if value is None:
        return ""

    return str(value).strip().lower()


def _is_true(value: Any) -> bool:
    """
    Convert common boolean representations into True/False.
    """
    if isinstance(value, bool):
        return value

    if value is None:
        return False

    if isinstance(value, (int, float)):
        return value == 1

    text = str(value).strip().lower()

    return text in {
        "true",
        "yes",
        "y",
        "1",
        "on",
        "checked",
    }


# ---------------------------------------------------------------------------
# SAFETY SCREEN
# ---------------------------------------------------------------------------

def check_clinical_safety(patient: Dict[str, Any]) -> Dict[str, Any]:
    """
    Perform a basic safety screen using current encounter information.

    IMPORTANT:
    This is a safety override layer, NOT a medical diagnosis.

    Returns
    -------
    dict
        {
            "safety_concern": bool,
            "reasons": [...],
            "severity": "high"/"moderate"/"none"
        }
    """

    reasons: List[str] = []

    # -------------------------------------------------------
    # Triage acuity
    # -------------------------------------------------------

    triage = _safe_int(patient.get("triage_acuity"))

    if triage is not None and triage in HIGH_ACUITY_LEVELS:
        reasons.append(
            f"Triage acuity is {triage}, indicating a high-priority "
            "presentation requiring clinical assessment."
        )

    # -------------------------------------------------------
    # Severity
    # -------------------------------------------------------

    severity = _normalise_text(patient.get("severity"))

    if severity in SEVERE_LEVELS:
        reasons.append(
            f"Current reported severity is '{patient.get('severity')}'."
        )

    # -------------------------------------------------------
    # Oxygen saturation
    # -------------------------------------------------------

    oxygen = _safe_float(patient.get("oxygen_saturation"))

    if oxygen is not None and oxygen < LOW_OXYGEN_SATURATION:
        reasons.append(
            f"Oxygen saturation is {oxygen:.0f}%, which requires "
            "clinical assessment."
        )

    # -------------------------------------------------------
    # Heart rate
    # -------------------------------------------------------

    heart_rate = _safe_float(patient.get("heart_rate"))

    if heart_rate is not None and heart_rate > HIGH_HEART_RATE:
        reasons.append(
            f"Heart rate is {heart_rate:.0f} bpm."
        )

    # -------------------------------------------------------
    # Systolic blood pressure
    # -------------------------------------------------------

    systolic_bp = _safe_float(patient.get("systolic_bp"))

    if systolic_bp is not None and systolic_bp >= HIGH_SYSTOLIC_BP:
        reasons.append(
            f"Systolic blood pressure is {systolic_bp:.0f} mmHg."
        )

    # -------------------------------------------------------
    # Determine safety level
    # -------------------------------------------------------

    if not reasons:
        safety_level = "none"

    elif len(reasons) >= 2:
        safety_level = "high"

    else:
        safety_level = "moderate"

    return {
        "safety_concern": bool(reasons),
        "reasons": reasons,
        "severity": safety_level,
    }


# ---------------------------------------------------------------------------
# ACCESS BARRIERS
# ---------------------------------------------------------------------------

def identify_access_barriers(patient: Dict[str, Any]) -> List[Dict[str, str]]:
    """
    Identify barriers that may affect access to lower-acuity care.

    Returns a list of structured barrier records.
    """

    barriers: List[Dict[str, str]] = []

    # -------------------------------------------------------
    # No insurance
    # -------------------------------------------------------

    if _is_true(patient.get("barrier_no_insurance")):
        barriers.append(
            {
                "type": "insurance",
                "title": "Insurance / affordability barrier",
                "description": (
                    "The patient may have difficulty accessing care "
                    "because of insurance or affordability constraints."
                ),
                "action": (
                    "Consider connecting the patient with available "
                    "coverage, financial-assistance, or community-care "
                    "resources."
                ),
            }
        )

    # -------------------------------------------------------
    # After-hours access
    # -------------------------------------------------------

    if _is_true(patient.get("barrier_after_hours_problem")):
        barriers.append(
            {
                "type": "after_hours",
                "title": "After-hours access barrier",
                "description": (
                    "The patient reports difficulty accessing routine "
                    "care outside normal operating hours."
                ),
                "action": (
                    "If clinically appropriate, consider telehealth, "
                    "an after-hours primary-care service, or another "
                    "available non-emergency care option."
                ),
            }
        )

    # -------------------------------------------------------
    # Transportation
    # -------------------------------------------------------

    if _is_true(patient.get("barrier_transportation")):
        barriers.append(
            {
                "type": "transportation",
                "title": "Transportation barrier",
                "description": (
                    "Transportation may make an in-person alternative "
                    "care visit difficult."
                ),
                "action": (
                    "Consider telehealth or an accessible in-person "
                    "care option when clinically appropriate."
                ),
            }
        )

    # -------------------------------------------------------
    # No PCP
    # -------------------------------------------------------

    has_pcp = patient.get("has_pcp")

    if has_pcp is not None and not _is_true(has_pcp):
        barriers.append(
            {
                "type": "no_pcp",
                "title": "No established primary-care provider",
                "description": (
                    "The patient does not appear to have an established "
                    "primary-care provider."
                ),
                "action": (
                    "Consider helping the patient establish primary-care "
                    "follow-up for ongoing management."
                ),
            }
        )

    # -------------------------------------------------------
    # Limited alternative-care access
    # -------------------------------------------------------

    alternative_access = patient.get("alternative_care_access")

    if (
        alternative_access is not None
        and not _is_true(alternative_access)
    ):
        barriers.append(
            {
                "type": "limited_alternative_access",
                "title": "Limited alternative-care access",
                "description": (
                    "The patient may have limited access to lower-acuity "
                    "care alternatives."
                ),
                "action": (
                    "Care management may review available primary-care, "
                    "urgent-care, telehealth, or community-care options."
                ),
            }
        )

    return barriers


# ---------------------------------------------------------------------------
# MODEL RISK CATEGORY
# ---------------------------------------------------------------------------

def classify_avoidability_probability(
    probability: float,
) -> Dict[str, Any]:
    """
    Convert model probability into a navigation-oriented category.

    Categories:
        low
        borderline
        high

    NOTE:
    These thresholds are project-design thresholds and are not clinical
    decision thresholds.
    """

    probability = max(0.0, min(1.0, float(probability)))

    if probability < LOW_RISK_THRESHOLD:
        category = "low"
        label = "Low Potential Avoidability"

    elif probability < HIGH_RISK_THRESHOLD:
        category = "borderline"
        label = "Borderline Care-Navigation Assessment"

    else:
        category = "high"
        label = "Potentially Avoidable Pattern"

    return {
        "category": category,
        "label": label,
        "probability": probability,
    }


# ---------------------------------------------------------------------------
# NAVIGATION OPTIONS
# ---------------------------------------------------------------------------

def build_navigation_options(
    patient: Dict[str, Any],
    barriers: List[Dict[str, str]],
) -> List[Dict[str, str]]:
    """
    Build possible navigation options based on identified barriers.

    This function does not select a medical treatment.
    It provides care-access options for care-manager review.
    """

    options: List[Dict[str, str]] = []

    barrier_types = {
        barrier["type"]
        for barrier in barriers
    }

    # -------------------------------------------------------
    # Telehealth
    # -------------------------------------------------------

    if (
        "after_hours" in barrier_types
        or "transportation" in barrier_types
    ):
        options.append(
            {
                "pathway": "Telehealth",
                "reason": (
                    "May improve access when transportation or "
                    "after-hours availability is a barrier."
                ),
            }
        )

    # -------------------------------------------------------
    # Primary care
    # -------------------------------------------------------

    if "no_pcp" in barrier_types:
        options.append(
            {
                "pathway": "Primary Care",
                "reason": (
                    "Consider establishing or arranging primary-care "
                    "follow-up for ongoing management."
                ),
            }
        )

    elif "after_hours" not in barrier_types:
        options.append(
            {
                "pathway": "Primary Care",
                "reason": (
                    "Primary-care follow-up may be appropriate when "
                    "the current condition is clinically stable."
                ),
            }
        )

    # -------------------------------------------------------
    # Urgent care
    # -------------------------------------------------------

    options.append(
        {
            "pathway": "Urgent Care",
            "reason": (
                "May be considered for clinically appropriate "
                "same-day or short-term evaluation when emergency "
                "care is not required."
            ),
        }
    )

    # -------------------------------------------------------
    # Care management
    # -------------------------------------------------------

    options.append(
        {
            "pathway": "Care Management Follow-up",
            "reason": (
                "Review symptoms, barriers, available services, "
                "and appropriate follow-up options."
            ),
        }
    )

    # -------------------------------------------------------
    # Remove duplicate pathways
    # -------------------------------------------------------

    unique_options = []
    seen = set()

    for option in options:
        pathway = option["pathway"]

        if pathway not in seen:
            unique_options.append(option)
            seen.add(pathway)

    return unique_options


# ---------------------------------------------------------------------------
# MAIN NAVIGATION DECISION
# ---------------------------------------------------------------------------

def generate_navigation_recommendation(
    patient: Dict[str, Any],
    avoidability_probability: float,
    prediction: Optional[int] = None,
) -> Dict[str, Any]:
    """
    Generate the complete care-navigation recommendation.

    Parameters
    ----------
    patient:
        Current encounter + relevant EHR information.

    avoidability_probability:
        CatBoost probability for potentially avoidable ED utilization.

    prediction:
        Optional binary model prediction.

    Returns
    -------
    dict
        Structured navigation result suitable for UI/API.
    """

    # -------------------------------------------------------
    # 1. Safety comes FIRST
    # -------------------------------------------------------

    safety = check_clinical_safety(patient)

    # -------------------------------------------------------
    # Safety override
    # -------------------------------------------------------

    if safety["safety_concern"]:

        return {
            "status": "safety_review",
            "status_label": "Clinical Safety Review Required",

            "avoidability_probability": round(
                float(avoidability_probability) * 100,
                1,
            ),

            "recommendation": (
                "Current clinical information contains findings "
                "that require clinical assessment. The avoidability "
                "prediction should not be used to discourage or "
                "delay emergency evaluation."
            ),

            "recommended_pathway": (
                "Clinical evaluation / appropriate escalation"
            ),

            "care_manager_action": (
                "Follow the appropriate clinical escalation process "
                "based on the patient's current presentation."
            ),

            "safety_override": True,

            "safety_reasons": safety["reasons"],

            "barriers": identify_access_barriers(patient),

            "navigation_options": [],

            "disclaimer": (
                "This system is a decision-support tool. It does not "
                "diagnose the patient or determine whether emergency "
                "care is required."
            ),
        }

    # -------------------------------------------------------
    # 2. Classify model probability
    # -------------------------------------------------------

    risk = classify_avoidability_probability(
        avoidability_probability
    )

    # -------------------------------------------------------
    # 3. Identify access barriers
    # -------------------------------------------------------

    barriers = identify_access_barriers(patient)

    # -------------------------------------------------------
    # 4. LOW probability
    # -------------------------------------------------------

    if risk["category"] == "low":

        return {
            "status": "low_avoidability",
            "status_label": "No Lower-Acuity Navigation Indicated",

            "avoidability_probability": round(
                risk["probability"] * 100,
                1,
            ),

            "recommendation": (
                "The model does not identify a strong pattern of "
                "potentially avoidable ED utilization for this "
                "encounter."
            ),

            "recommended_pathway": (
                "No ED-substitution intervention indicated"
            ),

            "care_manager_action": (
                "No immediate lower-acuity navigation intervention "
                "is indicated based on this assessment. Continue "
                "appropriate follow-up according to the patient's "
                "clinical plan."
            ),

            "safety_override": False,

            "safety_reasons": [],

            "barriers": barriers,

            "navigation_options": [],

            "disclaimer": (
                "The model prediction does not determine whether "
                "emergency care is necessary."
            ),
        }

    # -------------------------------------------------------
    # 5. BORDERLINE probability
    # -------------------------------------------------------

    if risk["category"] == "borderline":

        options = build_navigation_options(
            patient,
            barriers,
        )

        return {
            "status": "borderline",
            "status_label": "Borderline Care-Navigation Assessment",

            "avoidability_probability": round(
                risk["probability"] * 100,
                1,
            ),

            "recommendation": (
                "The model does not have sufficient confidence to "
                "classify this encounter as clearly potentially "
                "avoidable."
            ),

            "recommended_pathway": (
                "Care Manager Review"
            ),

            "care_manager_action": (
                "Review the patient's current symptoms, clinical "
                "status, access barriers, and available care options "
                "before selecting a navigation pathway."
            ),

            "safety_override": False,

            "safety_reasons": [],

            "barriers": barriers,

            "navigation_options": options,

            "automatic_substitution": False,

            "disclaimer": (
                "No automatic lower-acuity substitution is recommended. "
                "Any care-navigation decision should be made by the "
                "appropriate care professional based on the patient's "
                "current clinical context."
            ),
        }

    # -------------------------------------------------------
    # 6. HIGH probability
    # -------------------------------------------------------

    options = build_navigation_options(
        patient,
        barriers,
    )

    # -------------------------------------------------------
    # No barriers
    # -------------------------------------------------------

    if not barriers:

        care_manager_action = (
            "Review the patient's current symptoms and clinical "
            "context. If clinically appropriate, consider primary "
            "care, urgent care, telehealth, or care-management "
            "follow-up as an alternative pathway."
        )

    else:

        care_manager_action = (
            "Review the identified access barriers and select an "
            "appropriate care pathway. Potential options are shown "
            "for care-manager consideration."
        )

    return {
        "status": "potentially_avoidable",
        "status_label": "Potentially Avoidable Pattern",

        "avoidability_probability": round(
            risk["probability"] * 100,
            1,
        ),

        "recommendation": (
            "The model identified a pattern consistent with "
            "potentially avoidable ED utilization. The patient "
            "should still be assessed for clinical safety before "
            "considering an alternative care pathway."
        ),

        "recommended_pathway": (
            "Care-navigation assessment"
        ),

        "care_manager_action": care_manager_action,

        "safety_override": False,

        "safety_reasons": [],

        "barriers": barriers,

        "navigation_options": options,

        "automatic_substitution": False,

        "disclaimer": (
            "This recommendation does not mean the patient should "
            "avoid emergency care. If emergency symptoms are present "
            "or the patient's condition worsens, appropriate emergency "
            "evaluation should not be delayed."
        ),
    }


# ---------------------------------------------------------------------------
# BACKWARD-COMPATIBLE FUNCTION
# ---------------------------------------------------------------------------

def get_navigation_recommendation(
    patient: Dict[str, Any],
    prediction: int,
    probability: Optional[float] = None,
) -> Dict[str, Any]:
    """
    Backward-compatible wrapper.

    This allows existing code to continue calling the navigation
    module with:

        get_navigation_recommendation(
            patient,
            prediction,
            probability
        )

    If probability is not supplied, prediction is used as a fallback.

    NOTE:
    The probability should ideally always be passed from CatBoost.
    """

    if probability is None:

        probability = (
            1.0
            if int(prediction) == 1
            else 0.0
        )

    return generate_navigation_recommendation(
        patient=patient,
        avoidability_probability=probability,
        prediction=prediction,
    )


# ---------------------------------------------------------------------------
# OPTIONAL ALIAS
# ---------------------------------------------------------------------------

def navigation_rules(
    patient: Dict[str, Any],
    prediction: int,
    probability: Optional[float] = None,
) -> Dict[str, Any]:
    """
    Alias for compatibility with code that imports navigation_rules().
    """

    return get_navigation_recommendation(
        patient=patient,
        prediction=prediction,
        probability=probability,
    )