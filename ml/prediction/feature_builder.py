import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

PREDICTION_DIR = Path(__file__).resolve().parent
if str(PREDICTION_DIR) not in sys.path:
    sys.path.insert(0, str(PREDICTION_DIR))

try:
    from prediction_service import FEATURES
except ImportError:
    from ml.prediction.prediction_service import FEATURES


def build_prediction_features(patient, encounter_data):
    """
    Merge historical patient data with current encounter data
    and return ONLY the features required by the trained CatBoost model.
    """

    # ---------------------------------------------------------
    # 1. Start with historical patient information
    # ---------------------------------------------------------
    combined = dict(patient)

    # ---------------------------------------------------------
    # 2. Current encounter values override historical values
    # ---------------------------------------------------------
    combined.update(encounter_data)

    # ---------------------------------------------------------
    # 3. Extract ONLY the 30 CatBoost features
    # ---------------------------------------------------------
    model_input = {
        feature: combined.get(feature)
        for feature in FEATURES
    }

    # ---------------------------------------------------------
    # 4. Check for missing ML features
    # ---------------------------------------------------------
    missing_features = [
        feature
        for feature, value in model_input.items()
        if value is None
    ]

    if missing_features:
        raise ValueError(
            "Missing features required by CatBoost model:\n"
            + "\n".join(missing_features)
        )

    # ---------------------------------------------------------
    # 5. Return exactly the model input
    # ---------------------------------------------------------
    return model_input