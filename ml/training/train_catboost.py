# ============================================================
# UC07 — REGULARIZED CATBOOST TRAINING
#
# Input:
#     UC07_preprocessed.csv
#
# Target:
#     potentially_avoidable
#
# Dropped from ML INPUT:
#     patient_id
#     name
#     phone_number
#     potentially_avoidable_probability
#     potentially_avoidable
#
# Split:
#     70% Training
#     15% Validation
#     15% Testing
#
# Model:
#     Regularized CatBoostClassifier
# ============================================================


import pandas as pd
from pathlib import Path

from catboost import CatBoostClassifier

from sklearn.model_selection import train_test_split

from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    average_precision_score,
    classification_report,
    confusion_matrix
)


# ============================================================
# 1. PROJECT PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parents[2]

DATA_FILE = (
    BASE_DIR
    / "ml"
    / "data"
    / "processed"
    / "UC07_preprocessed.csv"
)

MODEL_FILE = (
    BASE_DIR
    / "ml"
    / "models"
    / "catboost_model.cbm"
)


# ============================================================
# 2. SETTINGS
# ============================================================

TARGET = "potentially_avoidable"

RANDOM_STATE = 42

THRESHOLD = 0.50


# ============================================================
# 3. LOAD DATA
# ============================================================

print("=" * 80)
print("UC07 — REGULARIZED CATBOOST TRAINING")
print("=" * 80)

print("\nLoading dataset:")
print(DATA_FILE)

df = pd.read_csv(DATA_FILE)

print(f"\nDataset shape: {df.shape}")


# ============================================================
# 4. CHECK REQUIRED COLUMNS
# ============================================================

if TARGET not in df.columns:

    raise ValueError(
        f"Target column '{TARGET}' not found."
    )


# ============================================================
# 5. TARGET
# ============================================================

# IMPORTANT:
# potentially_avoidable is the TARGET.
# It is NOT used as an input feature.

y = df[TARGET].astype(int)


print("\n" + "=" * 80)
print("TARGET DISTRIBUTION")
print("=" * 80)

print(y.value_counts())

print("\nTarget percentage:")

print(
    y.value_counts(normalize=True)
    .mul(100)
    .round(2)
)


# ============================================================
# 6. DROP IDENTIFIERS / LEAKAGE / TARGET FROM X
# ============================================================

DROP_COLUMNS = [

    # Patient identifiers
    "patient_id",
    "name",
    "phone_number",

    # Existing prediction — leakage
    "potentially_avoidable_probability",

    # Target — must not be an input feature
    "potentially_avoidable"
]


X = df.drop(
    columns=DROP_COLUMNS,
    errors="ignore"
).copy()


# ============================================================
# 7. VERIFY THAT DROPPED COLUMNS ARE NOT IN X
# ============================================================

remaining_dropped_columns = [
    column
    for column in DROP_COLUMNS
    if column in X.columns
]

if remaining_dropped_columns:

    raise ValueError(
        "These columns were not removed from X: "
        f"{remaining_dropped_columns}"
    )


print("\n" + "=" * 80)
print("FEATURE INFORMATION")
print("=" * 80)

print(
    f"Number of input features: {X.shape[1]}"
)

print("\nInput features:")

for column in X.columns:
    print(f"  ✓ {column}")


# ============================================================
# 8. CATEGORICAL FEATURES
# ============================================================

CATEGORICAL_FEATURES = [

    # -------------------------
    # Past / Historical
    # -------------------------

    "past_diagnosis_category_mode",

    "triage_acuity",


    # -------------------------
    # Current
    # -------------------------

    "gender",
    "region",
    "condition",
    "diagnosis_category",
    "severity",

    "symptom_fever_chills",
    "symptom_cold_cough",
    "symptom_vomiting",

    "barrier_no_insurance",
    "barrier_after_hours_problem",
    "transportation_barrier",

    "alternative_care_access",
    "has_primary_care_provider"
]


# ============================================================
# 9. NUMERICAL FEATURES
# ============================================================

NUMERICAL_FEATURES = [

    # -------------------------
    # Past / Historical
    # -------------------------

    "prior_ed_visits",
    "ed_visits_last_30_days",
    "ed_visits_last_90_days",
    "days_since_last_ed_visit",

    "care_management_contact_last_90_days",

    "pcp_visits_last_12_months",
    "days_since_last_pcp_visit",


    # -------------------------
    # Current
    # -------------------------

    "age",

    "systolic_bp",
    "diastolic_bp",
    "heart_rate",
    "temperature",
    "respiratory_rate",
    "oxygen_saturation",

    "symptom_duration_days"
]


# ============================================================
# 10. VERIFY FEATURE GROUPS
# ============================================================

all_declared_features = (
    CATEGORICAL_FEATURES
    +
    NUMERICAL_FEATURES
)

missing_features = [
    column
    for column in all_declared_features
    if column not in X.columns
]

if missing_features:

    raise ValueError(
        "Missing expected features:\n"
        + "\n".join(missing_features)
    )


# Check that every X column has been classified

unclassified_features = [
    column
    for column in X.columns
    if column not in all_declared_features
]

if unclassified_features:

    raise ValueError(
        "Unclassified input features:\n"
        + "\n".join(unclassified_features)
    )


# ============================================================
# 11. PREPARE CATEGORICAL FEATURES
# ============================================================

for column in CATEGORICAL_FEATURES:

    X[column] = (
        X[column]
        .fillna("Unknown")
        .astype(str)
    )


# CatBoost requires the column indices
# for categorical features.

categorical_indices = [
    X.columns.get_loc(column)
    for column in CATEGORICAL_FEATURES
]


# ============================================================
# 12. CHECK NUMERICAL FEATURES
# ============================================================

print("\n" + "=" * 80)
print("NUMERICAL MISSING VALUES")
print("=" * 80)

numerical_missing = (
    X[NUMERICAL_FEATURES]
    .isna()
    .sum()
)

print(
    numerical_missing[
        numerical_missing > 0
    ]
)


# The preprocessing step should already have handled
# missing numerical values.

if numerical_missing.sum() > 0:

    raise ValueError(
        "Missing numerical values remain. "
        "Run the preprocessing script first."
    )


# ============================================================
# 13. TRAIN / VALIDATION / TEST SPLIT
#
# 70% Training
# 15% Validation
# 15% Test
# ============================================================


# First:
# 85% Train + Validation
# 15% Test

X_train_val, X_test, y_train_val, y_test = (
    train_test_split(

        X,
        y,

        test_size=0.15,

        random_state=RANDOM_STATE,

        stratify=y
    )
)


# From the remaining 85%:
#
# 70% overall = Training
# 15% overall = Validation

validation_ratio = 0.15 / 0.85


X_train, X_validation, y_train, y_validation = (
    train_test_split(

        X_train_val,
        y_train_val,

        test_size=validation_ratio,

        random_state=RANDOM_STATE,

        stratify=y_train_val
    )
)


# ============================================================
# 14. PRINT SPLIT INFORMATION
# ============================================================

print("\n" + "=" * 80)
print("DATA SPLIT")
print("=" * 80)

print(
    f"Total      : {len(X)}"
)

print(
    f"Training   : {len(X_train)} "
    f"({len(X_train) / len(X) * 100:.1f}%)"
)

print(
    f"Validation : {len(X_validation)} "
    f"({len(X_validation) / len(X) * 100:.1f}%)"
)

print(
    f"Testing    : {len(X_test)} "
    f"({len(X_test) / len(X) * 100:.1f}%)"
)


# ============================================================
# 15. CLASS DISTRIBUTION AFTER SPLIT
# ============================================================

print("\nTraining target distribution:")

print(
    y_train.value_counts()
)

print("\nValidation target distribution:")

print(
    y_validation.value_counts()
)

print("\nTesting target distribution:")

print(
    y_test.value_counts()
)


# ============================================================
# 16. REGULARIZED CATBOOST
# ============================================================

model = CatBoostClassifier(

    # Maximum number of trees
    iterations=1000,

    # Smaller learning rate
    learning_rate=0.03,

    # Shallower trees
    depth=4,

    # Regularization
    l2_leaf_reg=12,

    # Randomness to reduce overfitting
    random_strength=1.5,

    # Bagging
    bagging_temperature=1.0,

    # Feature binning
    border_count=64,

    # Classification objective
    loss_function="Logloss",

    # Validation metric
    eval_metric="AUC",

    # Reproducibility
    random_seed=RANDOM_STATE,

    # Stop if validation performance stops improving
    early_stopping_rounds=100,

    verbose=100
)


# ============================================================
# 17. TRAIN MODEL
# ============================================================

print("\n" + "=" * 80)
print("TRAINING REGULARIZED CATBOOST")
print("=" * 80)


model.fit(

    X_train,

    y_train,

    # CatBoost categorical feature indices
    cat_features=categorical_indices,

    # IMPORTANT:
    # Validation set is used for early stopping.
    #
    # Test set is NOT used here.
    eval_set=(
        X_validation,
        y_validation
    )
)


# ============================================================
# 18. PREDICTION FUNCTION
# ============================================================

def get_predictions(X_data):

    probability = (
        model
        .predict_proba(X_data)[:, 1]
    )

    prediction = (
        probability >= THRESHOLD
    ).astype(int)

    return prediction, probability


# ============================================================
# 19. GENERATE PREDICTIONS
# ============================================================

train_prediction, train_probability = (
    get_predictions(X_train)
)

validation_prediction, validation_probability = (
    get_predictions(X_validation)
)

test_prediction, test_probability = (
    get_predictions(X_test)
)


# ============================================================
# 20. METRICS FUNCTION
# ============================================================

def calculate_metrics(
    y_true,
    prediction,
    probability
):

    return {

        "Accuracy":
            accuracy_score(
                y_true,
                prediction
            ),

        "Precision":
            precision_score(
                y_true,
                prediction,
                zero_division=0
            ),

        "Recall":
            recall_score(
                y_true,
                prediction,
                zero_division=0
            ),

        "F1":
            f1_score(
                y_true,
                prediction,
                zero_division=0
            ),

        "ROC-AUC":
            roc_auc_score(
                y_true,
                probability
            ),

        "PR-AUC":
            average_precision_score(
                y_true,
                probability
            )
    }


# ============================================================
# 21. CALCULATE METRICS
# ============================================================

train_metrics = calculate_metrics(

    y_train,

    train_prediction,

    train_probability
)


validation_metrics = calculate_metrics(

    y_validation,

    validation_prediction,

    validation_probability
)


test_metrics = calculate_metrics(

    y_test,

    test_prediction,

    test_probability
)


# ============================================================
# 22. PERFORMANCE COMPARISON
# ============================================================

comparison = pd.DataFrame({

    "Metric":
        list(train_metrics.keys()),

    "Training":
        list(train_metrics.values()),

    "Validation":
        list(validation_metrics.values()),

    "Testing":
        list(test_metrics.values())
})


comparison["Train-Test Gap"] = (
    comparison["Training"]
    -
    comparison["Testing"]
)


comparison["Gap_%"] = (
    comparison["Train-Test Gap"]
    * 100
)


# ============================================================
# 23. PRINT PERFORMANCE
# ============================================================

print("\n" + "=" * 80)
print("TRAINING vs VALIDATION vs TESTING")
print("=" * 80)

print(
    comparison.to_string(

        index=False,

        formatters={

            "Training":
                "{:.4f}".format,

            "Validation":
                "{:.4f}".format,

            "Testing":
                "{:.4f}".format,

            "Train-Test Gap":
                "{:.4f}".format,

            "Gap_%":
                "{:.2f}%".format
        }
    )
)


# ============================================================
# 24. FINAL TEST CLASSIFICATION REPORT
# ============================================================

print("\n" + "=" * 80)
print("FINAL TEST CLASSIFICATION REPORT")
print("=" * 80)

print(
    classification_report(

        y_test,

        test_prediction,

        target_names=[
            "Non-Avoidable",
            "Potentially Avoidable"
        ],

        digits=4
    )
)


# ============================================================
# 25. FINAL TEST CONFUSION MATRIX
# ============================================================

print("\n" + "=" * 80)
print("FINAL TEST CONFUSION MATRIX")
print("=" * 80)

print(
    confusion_matrix(

        y_test,

        test_prediction
    )
)


# ============================================================
# 26. BEST ITERATION
# ============================================================

print("\n" + "=" * 80)
print("MODEL INFORMATION")
print("=" * 80)

print(
    "Best iteration:",
    model.get_best_iteration()
)

print(
    "\nBest validation score:"
)

print(
    model.get_best_score()
)


# ============================================================
# 27. SAVE MODEL
# ============================================================

MODEL_FILE.parent.mkdir(
    parents=True,
    exist_ok=True
)

model.save_model(
    MODEL_FILE
)


# ============================================================
# 28. FINAL RESULT
# ============================================================

print("\n" + "=" * 80)
print("MODEL SAVED SUCCESSFULLY")
print("=" * 80)

print(
    f"\nModel location:\n"
    f"{MODEL_FILE}"
)

print(
    "\nInput features used:",
    X.shape[1]
)

print(
    "Target:",
    TARGET
)

print("\nTraining completed successfully.")