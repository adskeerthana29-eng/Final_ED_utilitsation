# Avoidable ED Utilization – CareNavigator

## Overview

CareNavigator is an AI-powered healthcare navigation system designed to identify potentially avoidable Emergency Department (ED) utilization and support care managers in selecting appropriate care-navigation interventions.

The system analyzes patient history, current clinical information, ED utilization patterns, and other relevant features to estimate avoidability risk and provide explainable recommendations for care management.

## Problem Statement

Frequent and potentially avoidable Emergency Department visits can increase healthcare costs and place additional pressure on emergency care services.

CareNavigator aims to help care managers identify patients who may benefit from alternative care pathways and appropriate follow-up interventions.

## Key Features

- Patient information and current vital collection
- ED utilization analysis
- Avoidability risk prediction
- Machine learning-based prediction
- CatBoost-based classification
- SHAP-based model explainability
- Care-navigation recommendations
- Care manager workflow
- Analysis results and recommendations
- Backend storage of completed care-management actions

## Machine Learning

The system uses a trained machine learning model to predict ED utilization avoidability.

### Model

- CatBoost Classifier
- SHAP for model explainability
- Feature engineering for patient and utilization data

### Example Input Features

- Age
- Triage acuity
- Prior ED visits
- ED visits in the last 30 days
- ED visits in the last 90 days
- Days since previous ED visit
- Past diagnosis category
- Current vital signs
- Other relevant patient and utilization features

## System Workflow

1. Care manager selects a patient.
2. Patient information and historical data are retrieved.
3. Current clinical/vital information is collected.
4. Features are prepared for the ML model.
5. The trained model predicts ED utilization avoidability.
6. SHAP explains the major factors influencing the prediction.
7. The navigation engine generates appropriate care recommendations.
8. The care manager reviews and completes the recommended action.
9. Completed actions are stored in the backend for future reference.

## Technology Stack

### Frontend / Application

- Streamlit

### Programming Language

- Python

### Machine Learning

- CatBoost
- Scikit-learn
- SHAP

### Data Processing

- Pandas
- NumPy

### Visualization

- Matplotlib
- Seaborn

### Model Management

- Joblib

### Data Storage

- CSV / backend database

