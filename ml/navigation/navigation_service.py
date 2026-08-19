# ============================================================
# UC07 — NAVIGATION SERVICE
# ============================================================
#
# Flow:
#
# Patient / Feature Vector
#          ↓
#     CatBoost prediction
#          ↓
#   Safety screening
#          ↓
# Avoidability category
#          ↓
# Access-barrier analysis
#          ↓
# Navigation recommendation
#
# IMPORTANT:
# This service does NOT tell a patient to avoid emergency care.
# It provides decision support for the care manager.
# ============================================================

from pathlib import Path
import sys


# ============================================================
# 1. PROJECT PATH
# ============================================================

BASE_DIR = Path(__file__).resolve().parents[2]

ML_DIR = BASE_DIR / "ml"
PREDICTION_DIR = ML_DIR / "prediction"
NAVIGATION_DIR = ML_DIR / "navigation"

for p in [
    str(BASE_DIR),
    str(ML_DIR),
    str(PREDICTION_DIR),
    str(NAVIGATION_DIR),
]:
    if p not in sys.path:
        sys.path.insert(0, p)


# ============================================================
# 2. IMPORT NAVIGATION RULES
# ============================================================

try:

    from navigation_rules import (
        generate_navigation_recommendation
    )

except ImportError:

    from ml.navigation.navigation_rules import (
        generate_navigation_recommendation
    )


# ============================================================
# 3. EXTRACT MODEL PROBABILITY
# ============================================================

def _extract_probability(prediction_result):
    """
    Extract potentially-avoidable probability from the
    CatBoost prediction result.

    Actual prediction_service.py format:

    {
        "potentially_avoidable_probability": 0.7777,
        "prediction": 1,
        "classification": "Potentially Avoidable"
    }

    Returns
    -------
    float
        Probability between 0.0 and 1.0
    """

    # --------------------------------------------------------
    # Empty result
    # --------------------------------------------------------

    if prediction_result is None:

        raise ValueError(
            "CatBoost prediction result is empty."
        )


    # ========================================================
    # DICTIONARY RESULT
    # ========================================================

    if isinstance(prediction_result, dict):

        # ----------------------------------------------------
        # IMPORTANT:
        # This is the actual key returned by your
        # prediction_service.py
        # ----------------------------------------------------

        possible_keys = [

            "potentially_avoidable_probability",

            # Compatibility keys
            "probability",
            "avoidability_probability",
            "positive_probability",
            "prediction_probability",
            "probability_1",
            "class_1_probability",
            "risk_probability",
        ]


        # ----------------------------------------------------
        # Search for probability
        # ----------------------------------------------------

        for key in possible_keys:

            if key not in prediction_result:
                continue


            value = prediction_result[key]


            if value is None:
                continue


            try:

                probability = float(value)

            except (TypeError, ValueError):

                continue


            # ------------------------------------------------
            # If probability is supplied as percentage
            #
            # Example:
            # 77.77 → 0.7777
            # ------------------------------------------------

            if probability > 1:

                probability = (
                    probability / 100.0
                )


            # ------------------------------------------------
            # Validate
            # ------------------------------------------------

            if not 0.0 <= probability <= 1.0:

                raise ValueError(
                    "Invalid avoidability probability: "
                    f"{probability}"
                )


            return probability


        # ====================================================
        # NESTED PREDICTION RESULT
        # ====================================================

        for nested_key in [

            "prediction_result",
            "result",
            "model_result",

        ]:

            nested = prediction_result.get(
                nested_key
            )


            if isinstance(nested, dict):

                try:

                    return _extract_probability(
                        nested
                    )

                except ValueError:

                    pass


    # ========================================================
    # NUMERIC RESULT
    # ========================================================

    if isinstance(
        prediction_result,
        (int, float)
    ):

        probability = float(
            prediction_result
        )


        # Percentage → decimal

        if probability > 1:

            probability = (
                probability / 100.0
            )


        if not 0.0 <= probability <= 1.0:

            raise ValueError(
                "Invalid avoidability probability: "
                f"{probability}"
            )


        return probability


    # ========================================================
    # PROBABILITY NOT FOUND
    # ========================================================

    raise ValueError(
        "Could not find avoidability probability "
        f"in prediction result: {prediction_result}"
    )


# ============================================================
# 4. EXTRACT BINARY PREDICTION
# ============================================================

def _extract_prediction(prediction_result):
    """
    Extract binary CatBoost prediction.

    Expected:

        prediction = 0
        or
        prediction = 1
    """

    if not isinstance(
        prediction_result,
        dict
    ):

        return None


    for key in [

        "prediction",
        "predicted_class",
        "class",
        "label",

    ]:

        if key not in prediction_result:
            continue


        value = prediction_result[key]


        if value is None:
            continue


        try:

            return int(value)

        except (
            TypeError,
            ValueError
        ):

            pass


    return None


# ============================================================
# 5. MAIN NAVIGATION FUNCTION
# ============================================================

def navigate_patient(
    patient,
    prediction_result=None,
):
    """
    Generate a care-navigation recommendation.

    Parameters
    ----------
    patient:
        Feature dictionary / encounter information already
        prepared for the prediction pipeline.

    prediction_result:
        Optional CatBoost result.

        If encounter.py already calculated the prediction,
        pass it here so CatBoost is NOT executed twice.

    Returns
    -------
    dict
        Structured navigation recommendation.
    """


    # ========================================================
    # STEP 1 — GET CATBOOST PREDICTION
    # ========================================================

    if prediction_result is None:

        try:

            from prediction_service import (
                predict_patient
            )

        except ImportError:

            from ml.prediction.prediction_service import (
                predict_patient
            )


        prediction_result = predict_patient(
            patient
        )


    # ========================================================
    # STEP 2 — EXTRACT PROBABILITY
    # ========================================================

    probability = _extract_probability(
        prediction_result
    )


    # ========================================================
    # STEP 3 — EXTRACT BINARY PREDICTION
    # ========================================================

    prediction = _extract_prediction(
        prediction_result
    )


    # ========================================================
    # STEP 4 — GENERATE NAVIGATION
    # ========================================================

    navigation_result = (
        generate_navigation_recommendation(

            patient=patient,

            avoidability_probability=probability,

            prediction=prediction,
        )
    )


    # ========================================================
    # STEP 5 — SAFETY CHECK
    # ========================================================

    if navigation_result is None:

        navigation_result = {}


    if not isinstance(
        navigation_result,
        dict
    ):

        navigation_result = {

            "recommendation":
                str(navigation_result)

        }


    # ========================================================
    # STEP 6 — ADD MODEL INFORMATION
    # ========================================================

    navigation_result[
        "model_prediction"
    ] = prediction


    navigation_result[
        "model_probability"
    ] = probability


    navigation_result[
        "model_probability_percent"
    ] = round(
        probability * 100,
        2
    )


    # ========================================================
    # STEP 7 — RETURN FINAL RESULT
    # ========================================================

    return navigation_result


# ============================================================
# 6. BACKWARD COMPATIBILITY
# ============================================================

def generate_navigation(
    patient,
    prediction_result=None,
):
    """
    Backward-compatible wrapper.

    Existing project code can continue using:

        generate_navigation(...)

    """

    return navigate_patient(

        patient=patient,

        prediction_result=prediction_result,

    )


# ============================================================
# 7. TEST
# ============================================================

if __name__ == "__main__":

    print(
        "UC07 Navigation Service loaded successfully."
    )

    # Test the exact format currently returned
    # by your CatBoost prediction service.

    test_prediction = {

        "potentially_avoidable_probability": 0.7777,

        "prediction": 1,

        "classification":
            "Potentially Avoidable",

    }


    probability = _extract_probability(
        test_prediction
    )


    prediction = _extract_prediction(
        test_prediction
    )


    print(
        "Test probability:",
        probability
    )

    print(
        "Test percentage:",
        round(
            probability * 100,
            2
        ),
        "%"
    )

    print(
        "Test prediction:",
        prediction
    )