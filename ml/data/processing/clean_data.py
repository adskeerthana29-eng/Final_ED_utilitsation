# ============================================================
# UC07 — DATA PREPROCESSING
# Past + Current Patient Features
# ============================================================

import pandas as pd
import numpy as np
from pathlib import Path


# ============================================================
# 1. PATHS
# ============================================================

from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[3]

INPUT_FILE = (
    BASE_DIR
    / "ml"
    / "data"
    / "raw"
    / "UC07_synthetic_dataset_v7.csv"
)

OUTPUT_FILE = (
    BASE_DIR
    / "ml"
    / "data"
    / "processed"
    / "UC07_preprocessed.csv"
)

# ============================================================
# 2. LOAD DATA
# ============================================================

print("=" * 70)
print("UC07 — DATA PREPROCESSING")
print("=" * 70)

df = pd.read_csv(INPUT_FILE)

print(f"Original shape: {df.shape}")


# ============================================================
# 3. REMOVE DUPLICATE ROWS
# ============================================================

duplicate_count = df.duplicated().sum()

print(f"\nDuplicate rows: {duplicate_count}")

if duplicate_count > 0:
    df = df.drop_duplicates().reset_index(drop=True)

print(f"Shape after duplicate removal: {df.shape}")


# ============================================================
# 4. DEFINE TARGET
# ============================================================

TARGET = "potentially_avoidable"

y = df[TARGET].astype(int)

print("\nTarget distribution:")
print(y.value_counts())

print("\nTarget percentage:")
print(
    y.value_counts(normalize=True)
    .mul(100)
    .round(2)
)


# ============================================================
# 5. REMOVE IDENTIFIERS / LEAKAGE
# ============================================================

REMOVE_COLUMNS = [
    "patient_id",
    "name",
    "phone_number",

    # This is already an existing prediction.
    # It MUST NOT be used as a model feature.
    "potentially_avoidable_probability",

    # Target is separated below.
    TARGET
]

X = df.drop(
    columns=REMOVE_COLUMNS,
    errors="ignore"
).copy()


# ============================================================
# 6. DEFINE PAST FEATURES
# ============================================================

PAST_FEATURES = [
    "past_diagnosis_category_mode",
    "prior_ed_visits",
    "ed_visits_last_30_days",
    "ed_visits_last_90_days",
    "days_since_last_ed_visit",
    "triage_acuity",
    "care_management_contact_last_90_days",
    "pcp_visits_last_12_months",
    "days_since_last_pcp_visit"
]


# ============================================================
# 7. DEFINE CURRENT FEATURES
# ============================================================

CURRENT_FEATURES = [
    "age",
    "gender",
    "region",
    "condition",
    "diagnosis_category",
    "severity",

    "systolic_bp",
    "diastolic_bp",
    "heart_rate",
    "temperature",
    "respiratory_rate",
    "oxygen_saturation",

    "symptom_fever_chills",
    "symptom_cold_cough",
    "symptom_vomiting",
    "symptom_duration_days",

    "barrier_no_insurance",
    "barrier_after_hours_problem",
    "transportation_barrier",

    "alternative_care_access",
    "has_primary_care_provider"
]


# ============================================================
# 8. CHECK FEATURES
# ============================================================

all_expected_features = (
    PAST_FEATURES +
    CURRENT_FEATURES
)

missing_features = [
    col
    for col in all_expected_features
    if col not in X.columns
]

if missing_features:
    raise ValueError(
        f"Missing expected features: {missing_features}"
    )

print("\nPast features:")
for feature in PAST_FEATURES:
    print(f"  ✓ {feature}")

print("\nCurrent features:")
for feature in CURRENT_FEATURES:
    print(f"  ✓ {feature}")


# ============================================================
# 9. KEEP ONLY APPROVED ML FEATURES
# ============================================================

X = X[all_expected_features].copy()


# ============================================================
# 10. DATA TYPES
# ============================================================

# ------------------------------------------------------------
# CATEGORICAL FEATURES
# ------------------------------------------------------------

CATEGORICAL_FEATURES = [
    "past_diagnosis_category_mode",
    "triage_acuity",
    "gender",
    "region",
    "condition",
    "diagnosis_category",
    "severity",
    "symptom_fever_chills",
    "symptom_cold_cough",
    "symptom_vomiting",
    "alternative_care_access",
    "barrier_no_insurance",
    "barrier_after_hours_problem",
    "transportation_barrier",
    "has_primary_care_provider"
]


# ------------------------------------------------------------
# NUMERICAL FEATURES
# ------------------------------------------------------------

NUMERICAL_FEATURES = [
    "prior_ed_visits",
    "ed_visits_last_30_days",
    "ed_visits_last_90_days",
    "days_since_last_ed_visit",
    "care_management_contact_last_90_days",
    "pcp_visits_last_12_months",
    "days_since_last_pcp_visit",

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
# 11. HANDLE CATEGORICAL MISSING VALUES
# ============================================================

for column in CATEGORICAL_FEATURES:

    X[column] = (
        X[column]
        .fillna("Unknown")
        .astype(str)
    )


# ============================================================
# 12. HANDLE NUMERICAL MISSING VALUES
# ============================================================

print("\nMissing numerical values before handling:")

print(
    X[NUMERICAL_FEATURES]
    .isna()
    .sum()
    .loc[lambda s: s > 0]
)


# Use median for missing numerical values.
# This is appropriate for the current synthetic dataset.
for column in NUMERICAL_FEATURES:

    if X[column].isna().sum() > 0:

        median_value = X[column].median()

        X[column] = X[column].fillna(
            median_value
        )


# ============================================================
# 13. CHECK REMAINING MISSING VALUES
# ============================================================

remaining_missing = X.isna().sum().sum()

print(
    f"\nRemaining missing values: "
    f"{remaining_missing}"
)

if remaining_missing != 0:
    raise ValueError(
        "Missing values still remain."
    )


# ============================================================
# 14. CHECK NUMERICAL VALUES
# ============================================================

print("\nNumerical feature summary:")
print(
    X[NUMERICAL_FEATURES]
    .describe()
    .T
)


# ============================================================
# 15. CHECK CATEGORICAL VALUES
# ============================================================

print("\nCategorical feature cardinality:")

for column in CATEGORICAL_FEATURES:

    print(
        f"{column}: "
        f"{X[column].nunique()} unique values"
    )


# ============================================================
# 16. FINAL DATASET
# ============================================================

processed_df = X.copy()

processed_df[TARGET] = y.values


# ============================================================
# 17. CREATE OUTPUT DIRECTORY
# ============================================================

OUTPUT_FILE.parent.mkdir(
    parents=True,
    exist_ok=True
)


# ============================================================
# 18. SAVE
# ============================================================

processed_df.to_csv(
    OUTPUT_FILE,
    index=False
)


# ============================================================
# 19. FINAL REPORT
# ============================================================

print("\n" + "=" * 70)
print("PREPROCESSING COMPLETED")
print("=" * 70)

print(f"Original rows   : {len(df)}")
print(f"Processed rows  : {len(processed_df)}")
print(f"ML features     : {len(all_expected_features)}")
print(f"Past features   : {len(PAST_FEATURES)}")
print(f"Current features: {len(CURRENT_FEATURES)}")

print(
    f"\nProcessed dataset saved to:\n"
    f"{OUTPUT_FILE}"
)

print("\nFinal columns:")
for column in processed_df.columns:
    print(f"  ✓ {column}")