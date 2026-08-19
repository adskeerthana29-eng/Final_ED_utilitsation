"""
Database query utilities for ED Utilization Navigator.

Provides reusable, parameterized SQLite queries for
ehr_historical_data and current_patient_data.
"""

import sqlite3
from typing import Any, Dict, List, Optional

from .connection import get_connection
from .schema import (
    TABLE_EHR_HISTORICAL_DATA,
    TABLE_CURRENT_PATIENT_DATA,
    COLUMN_NAMES,
    SORTABLE_COLUMNS,
    ALLOWED_SORT_ORDERS,
    FILTERABLE_COLUMNS,
)


# ==========================================================
# Helper Functions
# ==========================================================

def _dict_factory(cursor, row):
    """
    Convert SQLite rows into dictionaries.
    """
    return {
        column[0]: row[index]
        for index, column in enumerate(cursor.description)
    }


def _execute_query(
    query: str,
    params: tuple = ()
) -> List[Dict[str, Any]]:
    """
    Execute a SELECT query and return list of dictionaries.
    """

    with get_connection() as conn:

        conn.row_factory = _dict_factory

        cursor = conn.cursor()

        cursor.execute(query, params)

        return cursor.fetchall()


# ==========================================================
# Schema Functions
# ==========================================================

def get_table_schema() -> List[Dict[str, Any]]:
    """
    Return schema of ehr_historical_data table.
    """

    query = f"""
        PRAGMA table_info({TABLE_EHR_HISTORICAL_DATA})
    """

    return _execute_query(query)


def get_column_names() -> List[str]:
    """
    Return available column names.
    """

    return COLUMN_NAMES.copy()


def get_total_records_count() -> int:
    """
    Return total number of patients.
    """

    query = f"""
        SELECT COUNT(*)
        AS total
        FROM {TABLE_EHR_HISTORICAL_DATA}
    """

    result = _execute_query(query)

    return result[0]["total"]


# ==========================================================
# Basic Patient Queries
# ==========================================================

def get_all_records(
    page: int = 1,
    limit: int = 20,
    sort_by: str = "patient_id",
    order: str = "ASC"
) -> List[Dict[str, Any]]:
    """
    Return paginated patient records.
    """

    if sort_by not in SORTABLE_COLUMNS:
        sort_by = "patient_id"

    if order.upper() not in ALLOWED_SORT_ORDERS:
        order = "ASC"

    offset = (page - 1) * limit

    query = f"""
        SELECT *
        FROM {TABLE_EHR_HISTORICAL_DATA}
        ORDER BY {sort_by} {order}
        LIMIT ?
        OFFSET ?
    """

    return _execute_query(
        query,
        (limit, offset)
    )


def get_record_by_patient_id(
    patient_id: str
) -> Optional[Dict[str, Any]]:
    """
    Return one patient by ID.
    """

    query = f"""
        SELECT *
        FROM {TABLE_EHR_HISTORICAL_DATA}
        WHERE patient_id = ?
    """

    result = _execute_query(
        query,
        (patient_id,)
    )

    if result:
        return result[0]

    return None


def get_records_by_patient_ids(
    patient_ids: List[str]
) -> List[Dict[str, Any]]:
    """
    Return multiple patients.
    """

    if not patient_ids:
        return []

    placeholders = ",".join(
        "?"
        for _ in patient_ids
    )

    query = f"""
        SELECT *
        FROM {TABLE_EHR_HISTORICAL_DATA}
        WHERE patient_id IN ({placeholders})
    """

    return _execute_query(
        query,
        tuple(patient_ids)
    )
# ==========================================================
# Patient Search
# ==========================================================

def search_patients(
    search: str,
    page: int = 1,
    limit: int = 20
) -> List[Dict[str, Any]]:
    """
    Search patients using Patient ID or Name.
    """

    offset = (page - 1) * limit

    keyword = f"%{search}%"

    query = f"""
        SELECT *
        FROM {TABLE_EHR_HISTORICAL_DATA}
        WHERE
            patient_id LIKE ?
            OR name LIKE ?
        ORDER BY patient_id ASC
        LIMIT ?
        OFFSET ?
    """

    return _execute_query(
        query,
        (
            keyword,
            keyword,
            limit,
            offset,
        ),
    )


# ==========================================================
# Dynamic Filtering
# ==========================================================

def filter_records(
    filters: Dict[str, Any],
    page: int = 1,
    limit: int = 20,
    sort_by: str = "patient_id",
    order: str = "ASC",
) -> List[Dict[str, Any]]:
    """
    Dynamic filtering with parameterized SQL.
    """

    if sort_by not in SORTABLE_COLUMNS:
        sort_by = "patient_id"

    if order.upper() not in ALLOWED_SORT_ORDERS:
        order = "ASC"

    where_conditions = []
    parameters = []

    for key, value in filters.items():

        if key not in FILTERABLE_COLUMNS:
            continue

        if value is None:
            continue

        where_conditions.append(f"{key} = ?")
        parameters.append(value)

    where_sql = ""

    if where_conditions:
        where_sql = "WHERE " + " AND ".join(where_conditions)

    offset = (page - 1) * limit

    query = f"""
        SELECT *
        FROM {TABLE_EHR_HISTORICAL_DATA}
        {where_sql}
        ORDER BY {sort_by} {order}
        LIMIT ?
        OFFSET ?
    """

    parameters.extend(
        [
            limit,
            offset,
        ]
    )

    return _execute_query(
        query,
        tuple(parameters),
    )


# ==========================================================
# Current Patient Table
# ==========================================================

def get_current_patient(
    patient_id: str,
) -> Optional[Dict[str, Any]]:
    """
    Return current encounter information.
    """

    query = f"""
        SELECT *
        FROM {TABLE_CURRENT_PATIENT_DATA}
        WHERE patient_id = ?
    """

    result = _execute_query(
        query,
        (
            patient_id,
        ),
    )

    if result:
        return result[0]

    return None


# ==========================================================
# Merge Historical + Current
# ==========================================================

def get_complete_patient_profile(
    patient_id: str,
) -> Dict[str, Any]:
    """
    Merge historical and current encounter data.
    """

    historical = get_record_by_patient_id(
        patient_id
    )

    current = get_current_patient(
        patient_id
    )

    return {
        "historical_data": historical,
        "current_encounter": current,
    }
# ==========================================================
# Dashboard Statistics
# ==========================================================

def get_overall_summary_metrics() -> Dict[str, Any]:
    """
    Return dashboard summary statistics.
    """

    query = f"""
        SELECT

            COUNT(*) AS total_patients,

            ROUND(AVG(triage_acuity),2) AS average_triage_acuity,

            COUNT(DISTINCT region) AS total_regions,

            COUNT(DISTINCT past_diagnosis) AS diagnosis_categories,

            ROUND(AVG(prior_ed_visits),2) AS average_prior_ed_visits,

            ROUND(AVG(ed_visit_last_30_days),2) AS average_ed_last_30_days,

            ROUND(AVG(care_management_contact_last_90_days),2)
                AS average_care_management_contacts,

            ROUND(AVG(pcp_visit_last_12_months),2)
                AS average_pcp_visits

        FROM {TABLE_EHR_HISTORICAL_DATA}
    """

    result = _execute_query(query)

    return result[0]


# ==========================================================
# Gender Distribution
# ==========================================================

def get_gender_distribution():

    query = f"""
        SELECT

            gender,
            COUNT(*) AS count

        FROM {TABLE_EHR_HISTORICAL_DATA}

        GROUP BY gender

        ORDER BY count DESC
    """

    return _execute_query(query)


# ==========================================================
# Region Distribution
# ==========================================================

def get_region_distribution():

    query = f"""
        SELECT

            region,
            COUNT(*) AS count

        FROM {TABLE_EHR_HISTORICAL_DATA}

        GROUP BY region

        ORDER BY count DESC
    """

    return _execute_query(query)


# ==========================================================
# Diagnosis Distribution
# ==========================================================

def get_diagnosis_distribution():

    query = f"""
        SELECT

            past_diagnosis,
            COUNT(*) AS count

        FROM {TABLE_EHR_HISTORICAL_DATA}

        GROUP BY past_diagnosis

        ORDER BY count DESC
    """

    return _execute_query(query)


# ==========================================================
# Triage Distribution
# ==========================================================

def get_triage_distribution():

    query = f"""
        SELECT

            triage_acuity,
            COUNT(*) AS count

        FROM {TABLE_EHR_HISTORICAL_DATA}

        GROUP BY triage_acuity

        ORDER BY triage_acuity
    """

    return _execute_query(query)


# ==========================================================
# ED Visit Statistics
# ==========================================================

def get_ed_visit_statistics():

    query = f"""
        SELECT

            SUM(prior_ed_visits) AS total_prior_ed_visits,

            SUM(ed_visit_last_30_days) AS total_last_30_days,

            ROUND(AVG(days_since_last_ed_visit),2)
                AS average_days_since_last_ed

        FROM {TABLE_EHR_HISTORICAL_DATA}
    """

    result = _execute_query(query)

    return result[0]


# ==========================================================
# Care Management Statistics
# ==========================================================

def get_care_management_statistics():

    query = f"""
        SELECT

            SUM(care_management_contact_last_90_days)
                AS total_contacts,

            ROUND(AVG(care_management_contact_last_90_days),2)
                AS average_contacts

        FROM {TABLE_EHR_HISTORICAL_DATA}
    """

    result = _execute_query(query)

    return result[0]


# ==========================================================
# PCP Visit Statistics
# ==========================================================

def get_pcp_statistics():

    query = f"""
        SELECT

            SUM(pcp_visit_last_12_months)
                AS total_pcp_visits,

            ROUND(AVG(days_since_last_pcp_visit),2)
                AS average_days_since_last_pcp

        FROM {TABLE_EHR_HISTORICAL_DATA}
    """

    result = _execute_query(query)

    return result[0]
# ==========================================================
# Dashboard Charts
# ==========================================================

def get_dashboard_charts():
    """
    Returns all dashboard chart data.
    """

    return {
        "gender_distribution": get_gender_distribution(),
        "region_distribution": get_region_distribution(),
        "diagnosis_distribution": get_diagnosis_distribution(),
        "triage_distribution": get_triage_distribution(),
        "ed_visit_statistics": get_ed_visit_statistics(),
        "pcp_statistics": get_pcp_statistics(),
        "care_management_statistics": get_care_management_statistics(),
    }


# ==========================================================
# High Risk Patients
# ==========================================================

def get_high_risk_patients(
    limit: int = 20
):
    """
    Patients with highest ED utilization.
    """

    query = f"""
        SELECT *

        FROM {TABLE_EHR_HISTORICAL_DATA}

        ORDER BY
            prior_ed_visits DESC,
            triage_acuity DESC,
            ed_visit_last_30_days DESC

        LIMIT ?
    """

    return _execute_query(
        query,
        (limit,),
    )


# ==========================================================
# Recommendation Statistics
# ==========================================================

def get_recommendation_statistics():
    """
    Statistics used by Recommendation Dashboard.
    """

    query = f"""
        SELECT

            alternative_care_access,

            COUNT(*) AS patient_count

        FROM {TABLE_EHR_HISTORICAL_DATA}

        GROUP BY alternative_care_access

        ORDER BY patient_count DESC
    """

    return _execute_query(query)


# ==========================================================
# Patient Exists
# ==========================================================

def patient_exists(
    patient_id: str,
) -> bool:

    query = f"""
        SELECT COUNT(*)
        AS total

        FROM {TABLE_EHR_HISTORICAL_DATA}

        WHERE patient_id = ?
    """

    result = _execute_query(
        query,
        (
            patient_id,
        ),
    )

    return result[0]["total"] > 0


# ==========================================================
# Current Encounter Exists
# ==========================================================

def current_encounter_exists(
    patient_id: str,
) -> bool:

    query = f"""
        SELECT COUNT(*)
        AS total

        FROM {TABLE_CURRENT_PATIENT_DATA}

        WHERE patient_id = ?
    """

    result = _execute_query(
        query,
        (
            patient_id,
        ),
    )

    return result[0]["total"] > 0


# ==========================================================
# Database Health
# ==========================================================

def get_database_health():
    """
    Simple database health information.
    """

    historical = get_total_records_count()

    query = f"""
        SELECT COUNT(*)
        AS total

        FROM {TABLE_CURRENT_PATIENT_DATA}
    """

    current = _execute_query(query)

    return {
        "historical_records": historical,
        "current_encounters": current[0]["total"],
        "status": "healthy",
    }