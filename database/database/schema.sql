-- =============================================================================
-- ED-UTILIZATION-NAVIGATOR
-- SQL DATABASE SCHEMA & QUERY REFERENCE
-- =============================================================================

Database File : ed_utilization.db

Tables
------
1. ehr_historical_data
2. current_patient_data

Description
-----------
Historical patient information is stored in ehr_historical_data.

Current patient encounter information is stored in current_patient_data.

The backend combines both tables before generating the CatBoost prediction.

================================================================================
TABLE 1
================================================================================

Table Name

ehr_historical_data

Purpose

Stores historical patient information.

READ ONLY

Columns

patient_id
name
phone_number
gender
region
past_diagnosis
triage_acuity
prior_ed_visits
ed_visit_last_30_days
day_since_last_ed_visit
alternative_care_access
care_management_contact_last_90_days
pcp_visit_last_12_months
day_since_last_pcp_visit

================================================================================
TABLE 2
================================================================================

Table Name

current_patient_data

Purpose

Stores current patient encounter entered through Streamlit.

WRITE TABLE

Columns

patient_id
age
condition
diagnosis_category
systolic_bp
diastolic_bp
heart_rate
temperature
respiratory_rate
oxygen_saturation
symptoms
reason
severity
potentially_avoidable
navigation
shap_reason
process_completed

================================================================================
PATIENT SEARCH
================================================================================

-- Search Patient

SELECT *
FROM ehr_historical_data
WHERE patient_id = ?;

--------------------------------------------------------------------------------

-- Search by Name

SELECT *
FROM ehr_historical_data
WHERE name LIKE ?;

--------------------------------------------------------------------------------

-- Search by Region

SELECT *
FROM ehr_historical_data
WHERE region = ?;

================================================================================
CURRENT PATIENT
================================================================================

-- Get Current Encounter

SELECT *
FROM current_patient_data
WHERE patient_id = ?;

--------------------------------------------------------------------------------

-- Insert Current Encounter

INSERT INTO current_patient_data
(
patient_id,
age,
condition,
diagnosis_category,
systolic_bp,
diastolic_bp,
heart_rate,
temperature,
respiratory_rate,
oxygen_saturation,
symptoms,
reason,
severity,
potentially_avoidable,
navigation,
shap_reason,
process_completed
)

VALUES
(
?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?
);

================================================================================
HISTORICAL + CURRENT DATA
================================================================================

SELECT
h.*,
c.age,
c.condition,
c.diagnosis_category,
c.systolic_bp,
c.diastolic_bp,
c.heart_rate,
c.temperature,
c.respiratory_rate,
c.oxygen_saturation,
c.symptoms,
c.reason,
c.severity,
c.potentially_avoidable,
c.navigation,
c.shap_reason,
c.process_completed

FROM ehr_historical_data h

LEFT JOIN current_patient_data c

ON h.patient_id = c.patient_id

WHERE h.patient_id = ?;

================================================================================
DASHBOARD
================================================================================

-- Total Patients

SELECT COUNT(*)
FROM ehr_historical_data;

--------------------------------------------------------------------------------

-- Gender Distribution

SELECT
gender,
COUNT(*)
FROM ehr_historical_data
GROUP BY gender;

--------------------------------------------------------------------------------

-- Region Distribution

SELECT
region,
COUNT(*)
FROM ehr_historical_data
GROUP BY region;

--------------------------------------------------------------------------------

-- Diagnosis Distribution

SELECT
past_diagnosis,
COUNT(*)
FROM ehr_historical_data
GROUP BY past_diagnosis;

--------------------------------------------------------------------------------

-- Triage Distribution

SELECT
triage_acuity,
COUNT(*)
FROM ehr_historical_data
GROUP BY triage_acuity;

================================================================================
PREDICTION WORKFLOW
================================================================================

Historical Patient Data

↓

Current Patient Data

↓

Feature Merge

↓

Preprocessing

↓

CatBoost Model

↓

Prediction

↓

SHAP Explainability

↓

Recommendation Engine

↓

Response

================================================================================
IMPORTANT RULES
================================================================================

✓ Never recreate database

✓ Never recreate tables

✓ Never modify schema

✓ Never delete historical data

✓ Historical table is READ ONLY

✓ Current encounter table accepts inserts only through FastAPI

✓ Always use parameterized SQL

✓ Always use sqlite3

✓ Always use context managers

✓ CatBoost model is already trained

✓ SHAP explainer is already saved

✓ Recommendation engine already exists

================================================================================