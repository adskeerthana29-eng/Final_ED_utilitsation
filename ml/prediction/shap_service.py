import shap
from pathlib import Path
from catboost import CatBoostClassifier
import pandas as pd


# ============================================================
# PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parents[2]

MODEL_PATH = (
    BASE_DIR
    / "ml"
    / "models"
    / "catboost_model.cbm"
)


# ============================================================
# LOAD CATBOOST MODEL
# ============================================================

model = CatBoostClassifier()

model.load_model(MODEL_PATH)


# ============================================================
# CREATE SHAP EXPLAINER
# ============================================================

explainer = shap.TreeExplainer(model)


# ============================================================
# GET SHAP REASONS
# ============================================================

def get_shap_values(features):
    """
    Calculate SHAP values for one patient.

    `features` must contain the same 30 raw
    features used by the CatBoost model.
    """

    feature_names = model.feature_names_

    X = pd.DataFrame(
        [features],
        columns=feature_names
    )

    shap_values = explainer.shap_values(X)

    return X, shap_values


# ============================================================
# TOP SHAP FEATURES
# ============================================================

def get_top_shap_features(features, top_n=10):

    X, shap_values = get_shap_values(features)

    # CatBoost binary classification
    if isinstance(shap_values, list):
        values = shap_values[1][0]
    else:
        values = shap_values[0]

    result = pd.DataFrame({
        "feature": X.columns,
        "shap_value": values
    })

    result["absolute_shap"] = (
        result["shap_value"].abs()
    )

    result = result.sort_values(
        "absolute_shap",
        ascending=False
    )

    return result.head(top_n)