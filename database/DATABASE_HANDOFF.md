# ED-Utilization-Navigator Database Handoff Guide

---

# Project Overview

## Project Name

Avoidable ED Utilization Navigator

## Project Description

Avoidable ED Utilization Navigator is a healthcare decision-support application that predicts whether an Emergency Department (ED) visit is potentially avoidable.

The application combines:

- Historical patient information
- Current patient encounter information

to generate:

- Avoidable ED Prediction
- SHAP Explainability
- Clinical Recommendation Pathway

---

# Technology Stack

## Backend

- Python
- FastAPI
- SQLite
- sqlite3
- Pandas
- Pydantic
- Uvicorn

## Frontend

- Streamlit

## Machine Learning

- CatBoost (Pre-trained)
- SHAP

---

# Database Information

## Database File

```
ed_utilization.db
```

The database already exists.

## IMPORTANT

DO NOT

- Recreate database
- Recreate tables
- Modify schema
- Drop tables
- Delete data
- Insert fake/sample data
- Retrain the ML model

Only connect to the existing database.

---

# Database Architecture

The SQLite database contains two tables.

---

# Table 1

## ehr_historical_data

Purpose

Stores historical patient information imported from the healthcare dataset.

This table is READ ONLY.

Contains approximately **10,000 historical patient records**.

### Columns

- patient_id
- name
- phone_number
- gender
- region
- past_diagnosis
- triage_acuity
- prior_ed_visits
- ed_visit_last_30_days
- day_since_last_ed_visit
- alternative_care_access
- care_management_contact_last_90_days
- pcp_visit_last_12_months
- day_since_last_pcp_visit

This table should never be modified.

---

# Table 2

## current_patient_data

Purpose

Stores the patient's current hospital encounter entered from the Streamlit application.

Initially this table is empty.

The Streamlit application submits the current encounter to the FastAPI backend.

The backend stores the encounter in current_patient_data before running prediction.

### Columns

- patient_id
- age
- condition
- diagnosis_category
- systolic_bp
- diastolic_bp
- heart_rate
- temperature
- respiratory_rate
- oxygen_saturation
- symptoms
- reason
- severity
- potentially_avoidable
- navigation
- shap_reason
- process_completed

This table is writable.

---

# Complete Workflow

```
Historical Patient Data
        +
Current Patient Encounter
        │
        ▼
SQLite Database
        │
        ▼
FastAPI Backend
        │
        ▼
Feature Preprocessing
        │
        ▼
CatBoost Model
        │
        ▼
Prediction
        │
        ▼
SHAP Explainability
        │
        ▼
Recommendation Engine
        │
        ▼
Streamlit Dashboard
```

---

# Backend Responsibilities

The backend should

- Connect to SQLite
- Read historical patient information
- Read current encounter information
- Merge historical and current encounter data
- Apply the same preprocessing used during CatBoost training
- Load the saved CatBoost model
- Generate prediction
- Generate SHAP explanation
- Generate recommendation
- Return structured JSON responses
- Save the submitted current encounter into current_patient_data.

---

# Frontend Responsibilities

The Streamlit application should

- Search patients
- Display historical patient information
- Collect current encounter information
- Submit encounter information to FastAPI for storage and prediction.
- Display prediction
- Display SHAP explanation
- Display recommendation
- Display dashboard analytics

---

# Machine Learning Integration

The CatBoost model has already been trained.

Backend should

- Load the model once during application startup
- Reuse the model instance
- Never retrain the model
- Preserve preprocessing pipeline
- Preserve feature ordering

---
# Prediction Flow

1. Search patient from ehr_historical_data.

2. Enter current encounter in Streamlit.

3. Backend stores encounter in current_patient_data.

4. Backend combines historical data and current encounter.

5. Apply preprocessing.

6. Load CatBoost model.

7. Generate prediction.

8. Generate SHAP explanation.

9. Generate recommendation.

10. Return complete response to Streamlit.

# SHAP Explainability

Generate

- Top SHAP Features
- Positive Contributors
- Negative Contributors
- Feature Contribution Values
- Clinical Explanation
- Human-readable Explanation

---

# Recommendation Engine

The recommendation engine already exists.

Recommendations depend on

- Prior ED Visits
- PCP Visits
- Alternative Care Access
- Care Management Contact
- Triage Acuity
- Diagnosis
- Current Encounter
- Prediction Score

Possible recommendations include

- Primary Care
- Specialist Referral
- Care Management
- Telehealth
- Urgent Care
- Emergency Department

---

# Database Access Rules

Use

- sqlite3
- Parameterized SQL
- Context Managers

Never use

- DROP TABLE
- ALTER TABLE
- DELETE
- TRUNCATE
- REPLACE

Historical patient information must always remain read-only.

Only the `current_patient_data` table should receive new records from the frontend.

---

# Backend APIs

The backend will expose APIs for

- Patient Search
- Patient Details
- Dashboard Statistics
- Dashboard Charts
- Prediction
- Explainability
- Recommendation

---

# Security

Always use

- Parameterized SQL
- Input Validation
- Proper HTTP Status Codes
- Structured JSON Responses
- Exception Handling

Never expose internal database errors.

---

# Verification Checklist

Before deployment verify

- Database connection
- ehr_historical_data table exists
- current_patient_data table exists
- Historical data retrieval works
- Current patient insertion works
- Prediction API works
- SHAP explanation works
- Recommendation engine works
- Streamlit integration works

---

# Project Structure

```
database/
│
├── __init__.py
├── connection.py
├── schema.py
├── queries.py
├── validation.py
│
database.py
verify_database.py
check_tables.py
```

---

# Important Notes

- Use only the existing SQLite database.
- Do not recreate any table.
- Do not modify the schema.
- Historical patient data is read-only.
- Current encounter data is entered only through the Streamlit frontend.
- Backend combines historical and current encounter data before prediction.
- CatBoost model and SHAP explainer are already implemented.
- Maintain a clean, modular architecture.
- Preserve production-ready code quality.
- All SQL queries must be parameterized.
- Do not generate fake or sample data.