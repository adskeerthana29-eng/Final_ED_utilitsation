# ============================================================
# UC07 — NAVIGATION SERVICE
# ============================================================
#
# Flow:
#
# Patient
#    ↓
# CatBoost prediction
#    ↓
# Navigation rules
#    ↓
# Final navigation result
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

for p in [str(BASE_DIR), str(ML_DIR), str(PREDICTION_DIR), str(NAVIGATION_DIR)]:
    if p not in sys.path:
        sys.path.insert(0, p)

try:
    from prediction_service import predict_patient
except ImportError:
    from ml.prediction.prediction_service import predict_patient

try:
    from navigation_rules import generate_navigation
except ImportError:
    from ml.navigation.navigation_rules import generate_navigation


# ============================================================
# 5. MAIN NAVIGATION FUNCTION
# ============================================================

def navigate_patient(patient):

    # --------------------------------------------------------
    # Step 1
    # Get CatBoost prediction
    # --------------------------------------------------------

    prediction_result = predict_patient(
        patient
    )


    # --------------------------------------------------------
    # Step 2
    # Apply navigation rules
    # --------------------------------------------------------

    navigation_result = generate_navigation(

        patient,

        prediction_result
    )


    # --------------------------------------------------------
    # Step 3
    # Return complete result
    # --------------------------------------------------------

    return navigation_result