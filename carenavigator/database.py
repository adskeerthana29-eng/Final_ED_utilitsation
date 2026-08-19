# ============================================================
# CARE NAVIGATOR - DATABASE
# ============================================================

import sqlite3
import json
import uuid
import datetime
from pathlib import Path

import pandas as pd
import streamlit as st


# ============================================================
# 1. DATABASE PATH
# ============================================================

BASE_DIR = Path(__file__).resolve().parents[1]

DB_PATH = BASE_DIR / "database" / "ed_utilization.db"


# ============================================================
# 2. DATABASE CONNECTION
# ============================================================

def get_connection():
    """
    Create a connection to the existing SQLite database.

    The database is NOT recreated.
    Existing tables are NOT modified.
    """
    return sqlite3.connect(str(DB_PATH))


# ============================================================
# 3. INITIALIZE DATABASE
# ============================================================

def init_db():
    """
    Verify that the required tables exist.

    Historical data is READ ONLY.

    current_patient_data is used for new encounters.
    """

    with get_connection() as conn:

        tables = conn.execute("""
            SELECT name
            FROM sqlite_master
            WHERE type = 'table'
        """).fetchall()

        table_names = {row[0] for row in tables}

        required_tables = {
            "ehr_historical_data",
            "current_patient_data"
        }

        missing_tables = required_tables - table_names

        if missing_tables:
            raise RuntimeError(
                "Missing required database tables: "
                + ", ".join(sorted(missing_tables))
            )

        # Migration: Ensure age column exists in current_patient_data for encounter saving
        cols = {row[1] for row in conn.execute("PRAGMA table_info(current_patient_data)").fetchall()}
        if "age" not in cols:
            conn.execute("ALTER TABLE current_patient_data ADD COLUMN age INTEGER")

        # Migration / Table setup for encounters table
        if "encounters" in table_names:
            enc_count = conn.execute("SELECT COUNT(*) FROM encounters").fetchone()[0]
            enc_id_type = [r[2] for r in conn.execute("PRAGMA table_info(encounters)").fetchall() if r[1] == "encounter_id"]
            if enc_count == 0 and enc_id_type and enc_id_type[0].upper() != "TEXT":
                conn.execute("DROP TABLE encounters")
                table_names.remove("encounters")

        if "encounters" not in table_names:
            conn.execute("""
                CREATE TABLE encounters (
                    encounter_id TEXT PRIMARY KEY,
                    patient_id TEXT NOT NULL,
                    completion_timestamp TEXT,
                    care_manager_id TEXT,
                    age INTEGER,
                    gender TEXT,
                    region TEXT,
                    condition TEXT,
                    diagnosis_category TEXT,
                    triage_acuity INTEGER,
                    severity TEXT,
                    systolic_bp REAL,
                    diastolic_bp REAL,
                    heart_rate REAL,
                    temperature REAL,
                    respiratory_rate REAL,
                    oxygen_saturation REAL,
                    symptom_fever_chills INTEGER,
                    symptom_cold_cough INTEGER,
                    symptom_vomiting INTEGER,
                    symptom_duration_days INTEGER,
                    barrier_no_insurance INTEGER,
                    barrier_after_hours_problem INTEGER,
                    transportation_barrier INTEGER,
                    alternative_care_access INTEGER,
                    has_primary_care_provider INTEGER,
                    potentially_avoidable_probability REAL,
                    prediction INTEGER,
                    classification TEXT,
                    navigation_status TEXT,
                    navigation_reasons TEXT,
                    navigation_actions TEXT,
                    safety_flag INTEGER,
                    safety_reasons TEXT,
                    shap_reason TEXT,
                    process_completed INTEGER DEFAULT 1
                )
            """)
        else:
            enc_cols = {row[1] for row in conn.execute("PRAGMA table_info(encounters)").fetchall()}
            expected_cols = {
                "encounter_id": "TEXT",
                "patient_id": "TEXT",
                "completion_timestamp": "TEXT",
                "care_manager_id": "TEXT",
                "age": "INTEGER",
                "gender": "TEXT",
                "region": "TEXT",
                "condition": "TEXT",
                "diagnosis_category": "TEXT",
                "triage_acuity": "INTEGER",
                "severity": "TEXT",
                "systolic_bp": "REAL",
                "diastolic_bp": "REAL",
                "heart_rate": "REAL",
                "temperature": "REAL",
                "respiratory_rate": "REAL",
                "oxygen_saturation": "REAL",
                "symptom_fever_chills": "INTEGER",
                "symptom_cold_cough": "INTEGER",
                "symptom_vomiting": "INTEGER",
                "symptom_duration_days": "INTEGER",
                "barrier_no_insurance": "INTEGER",
                "barrier_after_hours_problem": "INTEGER",
                "transportation_barrier": "INTEGER",
                "alternative_care_access": "INTEGER",
                "has_primary_care_provider": "INTEGER",
                "potentially_avoidable_probability": "REAL",
                "prediction": "INTEGER",
                "classification": "TEXT",
                "navigation_status": "TEXT",
                "navigation_reasons": "TEXT",
                "navigation_actions": "TEXT",
                "safety_flag": "INTEGER",
                "safety_reasons": "TEXT",
                "shap_reason": "TEXT",
                "process_completed": "INTEGER"
            }
            for col, ctype in expected_cols.items():
                if col not in enc_cols:
                    conn.execute(f"ALTER TABLE encounters ADD COLUMN {col} {ctype}")

        conn.commit()


# Verify database when application starts
init_db()


# ============================================================
# 4. LOAD HISTORICAL PATIENTS
# ============================================================

@st.cache_data(ttl=300)
def get_all_patients_df():
    """
    Load historical patient information.

    IMPORTANT:
    This reads ONLY from ehr_historical_data.

    Current encounter information is NOT loaded here.
    """

    with get_connection() as conn:

        df = pd.read_sql_query(
            """
            SELECT *
            FROM ehr_historical_data
            """,
            conn
        )

    # Convert numeric fields when they exist
    numeric_columns = [
        "triage_acuity",
        "prior_ed_visits",
        "ed_visits_last_30_days",
        "day_since_last_ed_visit",
        "alternative_care_access",
        "care_management_contact_last_90_days",
        "pcp_visit_last_12_months",
        "day_since_last_pcp_visit",
    ]

    for column in numeric_columns:

        if column in df.columns:

            df[column] = pd.to_numeric(
                df[column],
                errors="coerce"
            )

    return df


# ============================================================
# 5. FILTER PATIENTS
# ============================================================

def get_filtered_patients(
    search_query="",
    ed_filter="All",
    symptom_filter="All"
):
    """
    Search and filter historical patients.

    No current encounter data is modified.
    """

    df = get_all_patients_df().copy()

    # --------------------------------------------------------
    # Search by Patient ID or Name
    # --------------------------------------------------------

    if search_query:

        search_query = (
            str(search_query)
            .strip()
            .lower()
        )

        patient_mask = (
            df["patient_id"]
            .astype(str)
            .str.lower()
            .str.contains(
                search_query,
                na=False
            )
        )

        if "name" in df.columns:

            name_mask = (
                df["name"]
                .astype(str)
                .str.lower()
                .str.contains(
                    search_query,
                    na=False
                )
            )

            patient_mask = patient_mask | name_mask

        df = df[patient_mask]

    # --------------------------------------------------------
    # ED visit filter
    # --------------------------------------------------------

    if ed_filter == "ED visit in last 30 days":

        if "ed_visits_last_30_days" in df.columns:

            df = df[
                df["ed_visits_last_30_days"] > 0
            ]

    elif ed_filter == "ED visit in last 90 days":

        # Your current historical table does not show a
        # 90-day column.
        #
        # Therefore we do NOT apply this filter unless
        # such a column exists.

        if "ed_visit_last_90_days" in df.columns:

            df = df[
                df["ed_visit_last_90_days"] > 0
            ]

    # --------------------------------------------------------
    # Diagnosis filter
    # --------------------------------------------------------

    if symptom_filter != "All":

        if "past_diagnosis" in df.columns:

            df = df[
                df["past_diagnosis"]
                .astype(str)
                == str(symptom_filter)
            ]

    return df


# ============================================================
# 6. DIAGNOSIS CATEGORIES
# ============================================================

@st.cache_data(ttl=300)
def get_diagnosis_categories():
    """
    Get diagnosis categories from the available historical data.
    """

    with get_connection() as conn:
        rows = conn.execute("""
            SELECT DISTINCT past_diagnosis_category_mode
            FROM ehr_historical_data
            WHERE past_diagnosis_category_mode IS NOT NULL
              AND TRIM(past_diagnosis_category_mode) != ''
            ORDER BY past_diagnosis_category_mode
        """).fetchall()

    return [row[0] for row in rows]

# ============================================================
# 7. GET PATIENT BY ID
# ============================================================

def get_patient_by_id(patient_id):
    """
    Retrieve one historical patient by patient ID.
    """

    with get_connection() as conn:

        row = conn.execute(
            """
            SELECT *
            FROM ehr_historical_data
            WHERE patient_id = ?
            LIMIT 1
            """,
            (patient_id,)
        ).fetchone()

        if row is None:
            return None

        columns = [
            description[0]
            for description in conn.execute(
                """
                SELECT *
                FROM ehr_historical_data
                WHERE patient_id = ?
                LIMIT 1
                """,
                (patient_id,)
            ).description
        ]

    return dict(zip(columns, row))


# ============================================================
# 8. DASHBOARD KPIs
# ============================================================

def get_dashboard_kpis():
    """
    Simple dashboard KPIs based ONLY on historical data.
    """

    with get_connection() as conn:

        # Total historical patients
        total_patients = conn.execute(
            """
            SELECT COUNT(*)
            FROM ehr_historical_data
            """
        ).fetchone()[0]

        # ED visits in last 30 days
        recent_ed_visits = conn.execute(
            """
            SELECT COALESCE(
                SUM(ed_visits_last_30_days),
                0
            )
            FROM ehr_historical_data
            """
        ).fetchone()[0]

        # High ED utilization
        high_utilization = conn.execute(
            """
            SELECT COUNT(*)
            FROM ehr_historical_data
            WHERE prior_ed_visits >= 5
            """
        ).fetchone()[0]

        # Current encounters
        current_encounters = conn.execute(
            """
            SELECT COUNT(*)
            FROM current_patient_data
            """
        ).fetchone()[0]

    return {
        "total_patients": int(
            total_patients or 0
        ),

        "recent_ed_visits": int(
            recent_ed_visits or 0
        ),

        "avoidable_ed": 0,

        "high_utilization": int(
            high_utilization or 0
        ),

        "current_encounters": int(
            current_encounters or 0
        )
    }


# ============================================================
# 9. AVOIDABILITY COUNTS
# ============================================================

def get_ed_avoidability_counts():
    """
    Avoidability is generated by the ML model for CURRENT
    encounters.

    Historical table does not contain potentially_avoidable.

    Therefore this function reads prediction results from
    current_patient_data.
    """

    with get_connection() as conn:

        # Prediction = 1
        avoidable = conn.execute(
            """
            SELECT COUNT(*)
            FROM current_patient_data
            WHERE prediction = 1
            """
        ).fetchone()[0]

        # Prediction = 0
        non_avoidable = conn.execute(
            """
            SELECT COUNT(*)
            FROM current_patient_data
            WHERE prediction = 0
            """
        ).fetchone()[0]

    return {
        "avoidable": int(
            avoidable or 0
        ),

        "non_avoidable": int(
            non_avoidable or 0
        )
    }


# ============================================================
# 10. SAVE CURRENT ENCOUNTER
# ============================================================

def save_encounter(encounter_data):
    """
    Save the completed current encounter and ML results.
    Inserts into the encounters table and current_patient_data for backward compatibility.
    """
    def to_json_str(val):
        if isinstance(val, (list, dict)):
            return json.dumps(val)
        return str(val) if val is not None else ""

    encounter_id = encounter_data.get("encounter_id")
    if not encounter_id:
        encounter_id = f"ENC-{uuid.uuid4().hex[:8].upper()}"

    timestamp = encounter_data.get("completion_timestamp") or datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    care_manager_id = encounter_data.get("care_manager_id") or "CM001"

    nav_reasons = to_json_str(encounter_data.get("navigation_reasons", []))
    nav_actions = to_json_str(encounter_data.get("navigation_actions", []))
    safety_reasons = to_json_str(encounter_data.get("safety_reasons", []))

    query_encounters = """
        INSERT INTO encounters (
            encounter_id, patient_id, completion_timestamp, care_manager_id,
            age, gender, region, condition, diagnosis_category, triage_acuity, severity,
            systolic_bp, diastolic_bp, heart_rate, temperature, respiratory_rate, oxygen_saturation,
            symptom_fever_chills, symptom_cold_cough, symptom_vomiting, symptom_duration_days,
            barrier_no_insurance, barrier_after_hours_problem, transportation_barrier,
            alternative_care_access, has_primary_care_provider,
            potentially_avoidable_probability, prediction, classification,
            navigation_status, navigation_reasons, navigation_actions,
            safety_flag, safety_reasons, shap_reason, process_completed
        ) VALUES (
            ?, ?, ?, ?,
            ?, ?, ?, ?, ?, ?, ?,
            ?, ?, ?, ?, ?, ?,
            ?, ?, ?, ?,
            ?, ?, ?,
            ?, ?,
            ?, ?, ?,
            ?, ?, ?,
            ?, ?, ?, ?
        )
    """

    values_encounters = (
        encounter_id,
        encounter_data.get("patient_id"),
        timestamp,
        care_manager_id,
        encounter_data.get("age"),
        encounter_data.get("gender"),
        encounter_data.get("region"),
        encounter_data.get("condition"),
        encounter_data.get("diagnosis_category"),
        encounter_data.get("triage_acuity"),
        encounter_data.get("severity"),
        encounter_data.get("systolic_bp"),
        encounter_data.get("diastolic_bp"),
        encounter_data.get("heart_rate"),
        encounter_data.get("temperature"),
        encounter_data.get("respiratory_rate"),
        encounter_data.get("oxygen_saturation"),
        encounter_data.get("symptom_fever_chills", 0),
        encounter_data.get("symptom_cold_cough", 0),
        encounter_data.get("symptom_vomiting", 0),
        encounter_data.get("symptom_duration_days"),
        encounter_data.get("barrier_no_insurance", 0),
        encounter_data.get("barrier_after_hours_problem", 0),
        encounter_data.get("transportation_barrier", 0),
        encounter_data.get("alternative_care_access", 0),
        encounter_data.get("has_primary_care_provider", 0),
        encounter_data.get("potentially_avoidable_probability"),
        encounter_data.get("prediction"),
        encounter_data.get("classification"),
        encounter_data.get("navigation_status") or encounter_data.get("navigation"),
        nav_reasons,
        nav_actions,
        1 if encounter_data.get("safety_flag") else 0,
        safety_reasons,
        to_json_str(encounter_data.get("shap_reason")),
        encounter_data.get("process_completed", 1)
    )

    query_current = """
        INSERT INTO current_patient_data (
            patient_id, age, heart_rate, systolic_bp, diastolic_bp, temperature,
            respiratory_rate, oxygen_saturation, symptom_fever_chills, symptom_cold_cough,
            symptom_vomiting, symptom_duration_days, triage_acuity, severity,
            potentially_avoidable_probability, prediction, classification, navigation,
            shap_reason, process_completed
        ) VALUES (
            ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
        )
    """
    values_current = (
        encounter_data.get("patient_id"),
        encounter_data.get("age"),
        encounter_data.get("heart_rate"),
        encounter_data.get("systolic_bp"),
        encounter_data.get("diastolic_bp"),
        encounter_data.get("temperature"),
        encounter_data.get("respiratory_rate"),
        encounter_data.get("oxygen_saturation"),
        encounter_data.get("symptom_fever_chills", 0),
        encounter_data.get("symptom_cold_cough", 0),
        encounter_data.get("symptom_vomiting", 0),
        encounter_data.get("symptom_duration_days"),
        encounter_data.get("triage_acuity"),
        encounter_data.get("severity"),
        encounter_data.get("potentially_avoidable_probability"),
        encounter_data.get("prediction"),
        encounter_data.get("classification"),
        encounter_data.get("navigation_status") or encounter_data.get("navigation"),
        to_json_str(encounter_data.get("shap_reason")),
        encounter_data.get("process_completed", 1)
    )

    with get_connection() as conn:
        conn.execute(query_encounters, values_encounters)
        try:
            conn.execute(query_current, values_current)
        except Exception:
            pass
        conn.commit()

    return encounter_id


# ============================================================
# 11. GET ENCOUNTER BY ID
# ============================================================

def get_encounter_by_id(encounter_id):
    """
    Retrieve one completed encounter by encounter_id.
    """
    with get_connection() as conn:
        df = pd.read_sql_query(
            "SELECT * FROM encounters WHERE encounter_id = ?",
            conn,
            params=(encounter_id,)
        )
    if df.empty:
        return None
    return df.iloc[0].to_dict()


# ============================================================
# 12. GET PATIENT ENCOUNTERS
# ============================================================

def get_patient_encounters(patient_id):
    """
    Get current completed encounter records for a patient.
    """
    with get_connection() as conn:
        df = pd.read_sql_query(
            """
            SELECT *
            FROM encounters
            WHERE patient_id = ?
            ORDER BY completion_timestamp DESC
            """,
            conn,
            params=(patient_id,)
        )
        if df.empty:
            df = pd.read_sql_query(
                """
                SELECT *
                FROM current_patient_data
                WHERE patient_id = ?
                ORDER BY rowid DESC
                """,
                conn,
                params=(patient_id,)
            )

    return df.to_dict(orient="records")


# ============================================================
# 13. GET ALL COMPLETED ENCOUNTERS
# ============================================================

def get_completed_encounters():
    """
    Get all completed encounters across all patients.
    """
    with get_connection() as conn:
        df = pd.read_sql_query(
            """
            SELECT *
            FROM encounters
            WHERE process_completed = 1
            ORDER BY completion_timestamp DESC
            """,
            conn
        )
        if df.empty:
            df = pd.read_sql_query(
                """
                SELECT *
                FROM current_patient_data
                WHERE process_completed = 1
                ORDER BY rowid DESC
                """,
                conn
            )
    return df.to_dict(orient="records")


# ============================================================
# 14. GET LATEST ENCOUNTER FOR PATIENT
# ============================================================

def get_latest_encounter(patient_id):
    encounters = get_patient_encounters(patient_id)
    return encounters[0] if encounters else None


# ============================================================
# 15. GET CURRENT ENCOUNTER COUNT
# ============================================================

def get_current_encounter_count():
    with get_connection() as conn:
        count = conn.execute("SELECT COUNT(*) FROM encounters").fetchone()[0]
        if not count:
            count = conn.execute("SELECT COUNT(*) FROM current_patient_data").fetchone()[0]
    return int(count or 0)