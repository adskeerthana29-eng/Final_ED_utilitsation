# ============================================================
# UC07 — ANALYTICS
# ============================================================

import streamlit as st
import pandas as pd

try:
    from carenavigator.database import get_connection
except ImportError:
    from database import get_connection


# ============================================================
# LOAD HISTORICAL DATA
# ============================================================

@st.cache_data(ttl=300)
def load_historical_data():

    with get_connection() as conn:

        df = pd.read_sql_query(
            """
            SELECT *
            FROM ehr_historical_data
            """,
            conn
        )

    return df


# ============================================================
# BASIC SUMMARY
# ============================================================

def get_basic_summary():

    df = load_historical_data()

    if df.empty:

        return {
            "total_patients": 0,
            "ed_visits_last_30_days": 0,
            "ed_visits_last_90_days": 0,
            "high_utilization": 0
        }

    total_patients = len(df)

    ed_30 = pd.to_numeric(
        df.get(
            "ed_visits_last_30_days",
            pd.Series(dtype=float)
        ),
        errors="coerce"
    ).fillna(0)

    ed_90 = pd.to_numeric(
        df.get(
            "ed_visits_last_90_days",
            pd.Series(dtype=float)
        ),
        errors="coerce"
    ).fillna(0)

    return {

        "total_patients":
            int(total_patients),

        "ed_visits_last_30_days":
            int(ed_30.sum()),

        "ed_visits_last_90_days":
            int(ed_90.sum()),

        "high_utilization":
            int((ed_30 >= 2).sum())
    }


# ============================================================
# DIAGNOSIS DISTRIBUTION
# ============================================================

def get_diagnosis_distribution():

    df = load_historical_data()

    if df.empty:

        return pd.DataFrame(
            columns=[
                "diagnosis_category",
                "count"
            ]
        )

    # --------------------------------------------------------
    # IMPORTANT:
    #
    # ehr_historical_data contains:
    #     past_diagnosis_category_mode
    #
    # It does NOT contain:
    #     diagnosis_category
    # --------------------------------------------------------

    source_column = (
        "past_diagnosis_category_mode"
    )

    if source_column not in df.columns:

        return pd.DataFrame(
            columns=[
                "diagnosis_category",
                "count"
            ]
        )

    diagnosis = (
        df[source_column]
        .dropna()
        .astype(str)
        .str.strip()
    )

    diagnosis = diagnosis[
        diagnosis != ""
    ]

    if diagnosis.empty:

        return pd.DataFrame(
            columns=[
                "diagnosis_category",
                "count"
            ]
        )

    diagnosis_counts = (
        diagnosis
        .value_counts()
        .reset_index()
    )

    diagnosis_counts.columns = [
        "diagnosis_category",
        "count"
    ]

    return diagnosis_counts


# ============================================================
# GENDER DISTRIBUTION
# ============================================================

def get_gender_distribution():

    df = load_historical_data()

    if df.empty:

        return pd.DataFrame(
            columns=[
                "gender",
                "count"
            ]
        )

    if "gender" not in df.columns:

        return pd.DataFrame(
            columns=[
                "gender",
                "count"
            ]
        )

    gender = (
        df["gender"]
        .dropna()
        .astype(str)
        .str.strip()
    )

    gender = gender[
        gender != ""
    ]

    if gender.empty:

        return pd.DataFrame(
            columns=[
                "gender",
                "count"
            ]
        )

    result = (
        gender
        .value_counts()
        .reset_index()
    )

    result.columns = [
        "gender",
        "count"
    ]

    return result


# ============================================================
# REGION DISTRIBUTION
# ============================================================

def get_region_distribution():

    df = load_historical_data()

    if df.empty:

        return pd.DataFrame(
            columns=[
                "region",
                "count"
            ]
        )

    if "region" not in df.columns:

        return pd.DataFrame(
            columns=[
                "region",
                "count"
            ]
        )

    region = (
        df["region"]
        .dropna()
        .astype(str)
        .str.strip()
    )

    region = region[
        region != ""
    ]

    if region.empty:

        return pd.DataFrame(
            columns=[
                "region",
                "count"
            ]
        )

    result = (
        region
        .value_counts()
        .reset_index()
    )

    result.columns = [
        "region",
        "count"
    ]

    return result


# ============================================================
# RECENT ED UTILIZATION
# ============================================================

def get_recent_ed_utilization():

    df = load_historical_data()

    if df.empty:

        return pd.DataFrame(
            columns=[
                "period",
                "visits"
            ]
        )

    visits_30 = 0
    visits_90 = 0

    if "ed_visits_last_30_days" in df.columns:

        values_30 = pd.to_numeric(
            df["ed_visits_last_30_days"],
            errors="coerce"
        ).fillna(0)

        visits_30 = int(
            values_30.sum()
        )

    if "ed_visits_last_90_days" in df.columns:

        values_90 = pd.to_numeric(
            df["ed_visits_last_90_days"],
            errors="coerce"
        ).fillna(0)

        visits_90 = int(
            values_90.sum()
        )

    return pd.DataFrame(
        {
            "period": [
                "Last 30 Days",
                "Last 90 Days"
            ],
            "visits": [
                visits_30,
                visits_90
            ]
        }
    )


# ============================================================
# ACCESS BARRIER SUMMARY
# ============================================================

def get_access_barrier_summary():

    df = load_historical_data()

    if df.empty:

        return pd.DataFrame(
            columns=[
                "barrier",
                "count"
            ]
        )

    barrier_columns = {

        "No Insurance":
            "barrier_no_insurance",

        "After-Hours Access Problem":
            "barrier_after_hours_problem",

        "Transportation Barrier":
            "transportation_barrier",

        "Limited Alternative Care":
            "alternative_care_access",

        "No Primary Care Provider":
            "has_primary_care_provider"
    }

    results = []

    for label, column in barrier_columns.items():

        if column not in df.columns:

            continue

        values = pd.to_numeric(
            df[column],
            errors="coerce"
        ).fillna(0)

        # ----------------------------------------------------
        # For these fields:
        #
        # 0 = access problem
        # 1 = access available
        # ----------------------------------------------------

        if column in [
            "alternative_care_access",
            "has_primary_care_provider"
        ]:

            count = int(
                (values == 0).sum()
            )

        else:

            count = int(
                (values == 1).sum()
            )

        results.append(
            {
                "barrier": label,
                "count": count
            }
        )

    return pd.DataFrame(
        results
    )


# ============================================================
# PRIMARY CARE SUMMARY
# ============================================================

def get_primary_care_summary():

    df = load_historical_data()

    result = {
        "with_pcp": 0,
        "without_pcp": 0
    }

    if df.empty:

        return result

    if "has_primary_care_provider" not in df.columns:

        return result

    pcp = pd.to_numeric(
        df["has_primary_care_provider"],
        errors="coerce"
    ).fillna(0)

    result["with_pcp"] = int(
        (pcp == 1).sum()
    )

    result["without_pcp"] = int(
        (pcp == 0).sum()
    )

    return result


# ============================================================
# HIGH UTILIZATION PATIENTS
# ============================================================

def get_high_utilization_patients():

    df = load_historical_data()

    if df.empty:

        return pd.DataFrame()

    if "ed_visits_last_30_days" not in df.columns:

        return pd.DataFrame()

    visits = pd.to_numeric(
        df["ed_visits_last_30_days"],
        errors="coerce"
    ).fillna(0)

    result = df[
        visits >= 2
    ].copy()

    return result.sort_values(
        "ed_visits_last_30_days",
        ascending=False
    )


# ============================================================
# ANALYTICS SUMMARY
# ============================================================

def get_analytics_summary():

    summary = (
        get_basic_summary()
    )

    diagnosis = (
        get_diagnosis_distribution()
    )

    gender = (
        get_gender_distribution()
    )

    region = (
        get_region_distribution()
    )

    barriers = (
        get_access_barrier_summary()
    )

    return {

        "summary":
            summary,

        "diagnosis":
            diagnosis,

        "gender":
            gender,

        "region":
            region,

        "barriers":
            barriers
    }


# ============================================================
# STREAMLIT ANALYTICS PAGE
# ============================================================

def render_analytics():

    st.title(
        "Analytics"
    )

    # --------------------------------------------------------
    # LOAD DATA
    # --------------------------------------------------------

    df = load_historical_data()

    if df.empty:

        st.warning(
            "No historical patient data available."
        )

        return

    # --------------------------------------------------------
    # KPI ROW
    # --------------------------------------------------------

    summary = (
        get_basic_summary()
    )

    col1, col2, col3, col4 = (
        st.columns(4)
    )

    with col1:

        st.metric(
            "Total Patients",
            summary[
                "total_patients"
            ]
        )

    with col2:

        st.metric(
            "ED Visits — 30 Days",
            summary[
                "ed_visits_last_30_days"
            ]
        )

    with col3:

        st.metric(
            "ED Visits — 90 Days",
            summary[
                "ed_visits_last_90_days"
            ]
        )

    with col4:

        st.metric(
            "High Utilization Patients",
            summary[
                "high_utilization"
            ]
        )

    st.divider()

    # ========================================================
    # DIAGNOSIS + GENDER
    # ========================================================

    col1, col2 = (
        st.columns(2)
    )

    # --------------------------------------------------------
    # DIAGNOSIS
    # --------------------------------------------------------

    with col1:

        st.subheader(
            "Diagnosis Category Distribution"
        )

        diag_counts = (
            get_diagnosis_distribution()
        )

        if not diag_counts.empty:

            st.bar_chart(
                diag_counts.set_index(
                    "diagnosis_category"
                )["count"]
            )

        else:

            st.info(
                "No diagnosis category data available."
            )

    # --------------------------------------------------------
    # GENDER
    # --------------------------------------------------------

    with col2:

        st.subheader(
            "Gender Distribution"
        )

        gender_counts = (
            get_gender_distribution()
        )

        if not gender_counts.empty:

            st.bar_chart(
                gender_counts.set_index(
                    "gender"
                )["count"]
            )

        else:

            st.info(
                "No gender data available."
            )

    st.divider()

    # ========================================================
    # REGION + ED UTILIZATION
    # ========================================================

    col1, col2 = (
        st.columns(2)
    )

    # --------------------------------------------------------
    # REGION
    # --------------------------------------------------------

    with col1:

        st.subheader(
            "Region Distribution"
        )

        region_counts = (
            get_region_distribution()
        )

        if not region_counts.empty:

            st.bar_chart(
                region_counts.set_index(
                    "region"
                )["count"]
            )

        else:

            st.info(
                "No region data available."
            )

    # --------------------------------------------------------
    # ED UTILIZATION
    # --------------------------------------------------------

    with col2:

        st.subheader(
            "ED Utilization"
        )

        utilization = (
            get_recent_ed_utilization()
        )

        if not utilization.empty:

            st.bar_chart(
                utilization.set_index(
                    "period"
                )["visits"]
            )

        else:

            st.info(
                "No ED utilization data available."
            )

    st.divider()

    # ========================================================
    # ACCESS BARRIERS
    # ========================================================

    st.subheader(
        "Care Access Barriers"
    )

    barriers = (
        get_access_barrier_summary()
    )

    if not barriers.empty:

        st.bar_chart(
            barriers.set_index(
                "barrier"
            )["count"]
        )

    else:

        st.info(
            "No access barrier data available."
        )

    st.divider()

    # ========================================================
    # PRIMARY CARE SUMMARY
    # ========================================================

    st.subheader(
        "Primary Care Access"
    )

    pcp_summary = (
        get_primary_care_summary()
    )

    pcp_col1, pcp_col2 = (
        st.columns(2)
    )

    with pcp_col1:

        st.metric(
            "Patients With PCP",
            pcp_summary[
                "with_pcp"
            ]
        )

    with pcp_col2:

        st.metric(
            "Patients Without PCP",
            pcp_summary[
                "without_pcp"
            ]
        )

    st.divider()

    # ========================================================
    # HIGH UTILIZATION PATIENTS
    # ========================================================

    st.subheader(
        "High ED Utilization Patients"
    )

    high_utilization = (
        get_high_utilization_patients()
    )

    if not high_utilization.empty:

        display_columns = [

            "patient_id",

            "name",

            "gender",

            "region",

            "past_diagnosis_category_mode",

            "prior_ed_visits",

            "ed_visits_last_30_days",

            "ed_visits_last_90_days"
        ]

        available_columns = [
            column
            for column in display_columns
            if column in high_utilization.columns
        ]

        st.dataframe(
            high_utilization[
                available_columns
            ],
            use_container_width=True,
            hide_index=True
        )

    else:

        st.info(
            "No high-utilization patients found."
        )

    st.divider()

    # ========================================================
    # COMPLETED CURRENT ENCOUNTERS
    # ========================================================

    st.subheader(
        "Completed Encounters Log"
    )

    try:
        from carenavigator.database import get_completed_encounters
    except ImportError:
        from database import get_completed_encounters

    completed = get_completed_encounters()

    if completed:
        df_comp = pd.DataFrame(completed)
        cols_to_show = [c for c in ["encounter_id", "patient_id", "completion_timestamp", "care_manager_id", "classification", "potentially_avoidable_probability", "navigation_status", "safety_flag"] if c in df_comp.columns]
        st.dataframe(
            df_comp[cols_to_show],
            use_container_width=True,
            hide_index=True
        )
    else:
        st.info(
            "No completed current encounters logged yet."
        )