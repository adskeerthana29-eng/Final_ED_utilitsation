import streamlit as st
import pandas as pd

try:
    from carenavigator.database import get_patient_by_id
except ImportError:
    from database import get_patient_by_id


# ============================================================
# PATIENT DETAIL PAGE
# ============================================================

def render_patient_detail():

    # ========================================================
    # BACK BUTTON
    # ========================================================

    if st.button("← Back to Patients"):
        st.session_state.page = "patients"
        st.rerun()

    # ========================================================
    # GET SELECTED PATIENT ID
    # ========================================================

    patient_id = st.session_state.get(
        "selected_patient_id"
    )

    if not patient_id:
        st.error("No patient selected.")
        return

    # ========================================================
    # GET PATIENT FROM DATABASE
    # ========================================================

    try:
        patient = get_patient_by_id(patient_id)

    except Exception as e:
        st.error(
            f"Unable to load patient data: {e}"
        )
        return

    if not patient:
        st.error(
            f"Patient with ID {patient_id} "
            "not found in database."
        )
        return

    # ========================================================
    # PATIENT PROFILE
    #
    # AGE INTENTIONALLY NOT DISPLAYED
    # ========================================================

    st.markdown("## Patient Profile")

    patient_name = patient.get(
        "name",
        "Unknown"
    )

    patient_gender = patient.get(
        "gender",
        "N/A"
    )

    patient_region = patient.get(
        "region",
        "N/A"
    )

    st.markdown(
        f"### {patient_name}"
    )

    st.write(
        f"**ID:** {patient.get('patient_id', patient_id)}"
    )

    st.write(
        f"**Gender:** {patient_gender}"
    )

    st.write(
        f"**Region:** {patient_region}"
    )

    # ========================================================
    # NEW ENCOUNTER BUTTON
    # ========================================================

    if st.button(
        "➕ New Encounter",
        use_container_width=True
    ):
        st.session_state.page = "new_encounter"
        st.rerun()

    st.divider()

    # ========================================================
    # TWO COLUMN LAYOUT
    # ========================================================

    col_left, col_right = st.columns(
        [1, 1]
    )

    # ========================================================
    # LEFT COLUMN
    # ========================================================

    with col_left:

        # ====================================================
        # CLINICAL SUMMARY
        #
        # AGE NOT DISPLAYED
        # SEVERITY NOT DISPLAYED
        # ====================================================

        st.subheader(
            "Clinical Summary"
        )

       
       
        past_diagnosis = patient.get(
            "past_diagnosis_category_mode"
        )

        if (
            past_diagnosis is None
            or pd.isna(past_diagnosis)
        ):
            past_diagnosis = "N/A"

        triage_acuity = patient.get(
            "triage_acuity",
            3
        )

        try:
            triage_acuity = int(
                triage_acuity
            )
        except (
            TypeError,
            ValueError
        ):
            triage_acuity = 3

        phone_number = patient.get(
            "phone_number"
        )

        if phone_number is None or pd.isna(
            phone_number
        ):
            phone_number = "N/A"

        # ----------------------------------------------------
        # DISPLAY USING NATIVE STREAMLIT
        # NO HTML
        # ----------------------------------------------------

       

        st.write(
            "**Past Diagnosis Mode:**",
            past_diagnosis
        )

        st.write(
            "**Triage Acuity Level:**",
            f"Level {triage_acuity}"
        )

        st.write(
            "**Contact Phone:**",
            phone_number
        )

        st.divider()

        # ====================================================
        # HOSPITALIZATION
        # ====================================================

        st.subheader(
            "Hospitalization Information"
        )

        st.info(
            "No hospitalization field "
            "is available in the current dataset."
        )

        st.divider()

        # ====================================================
        # CARE MANAGEMENT
        # ====================================================

        st.subheader(
            "Care Management & Primary Care"
        )

        # ----------------------------------------------------
        # PCP
        # ----------------------------------------------------

        has_pcp = patient.get(
            "has_primary_care_provider",
            0
        )

        try:
            has_pcp = int(has_pcp)
        except (
            TypeError,
            ValueError
        ):
            has_pcp = 0

        pcp_text = (
            "Yes"
            if has_pcp == 1
            else "No"
        )

        # ----------------------------------------------------
        # PCP VISITS
        # ----------------------------------------------------

        pcp_visits = patient.get(
            "pcp_visits_last_12_months",
            0
        )

        try:
            pcp_visits = int(
                pcp_visits
            )
        except (
            TypeError,
            ValueError
        ):
            pcp_visits = 0

        # ----------------------------------------------------
        # DAYS SINCE PCP
        # ----------------------------------------------------

        days_since_pcp = patient.get(
            "days_since_last_pcp_visit",
            0
        )

        try:
            days_since_pcp = int(
                days_since_pcp
            )
        except (
            TypeError,
            ValueError
        ):
            days_since_pcp = 0

        # ----------------------------------------------------
        # ALTERNATIVE CARE ACCESS
        # ----------------------------------------------------

        alternative_access = patient.get(
            "alternative_care_access",
            0
        )

        try:
            alternative_access = int(
                alternative_access
            )
        except (
            TypeError,
            ValueError
        ):
            alternative_access = 0

        alternative_text = (
            "Has Access"
            if alternative_access == 1
            else "No Access"
        )

        st.write(
            "**Primary Care Provider (PCP):**",
            pcp_text
        )

        st.write(
            "**PCP Visits (Last 12 Months):**",
            f"{pcp_visits} visits"
        )

        st.write(
            "**Days Since Last PCP Visit:**",
            f"{days_since_pcp} days"
        )

        st.write(
            "**Alternative Care Access:**",
            alternative_text
        )

        # ====================================================
        # CARE MANAGEMENT CONTACT
        # ====================================================

        cm_contact = patient.get(
            "care_management_contact_last_90_days",
            0
        )

        try:
            cm_contact = int(
                cm_contact
            )
        except (
            TypeError,
            ValueError
        ):
            cm_contact = 0

        if cm_contact == 1:

            st.success(
                "Care Management Contact "
                "(Last 90 Days): Contacted"
            )

        else:

            st.warning(
                "Care Management Contact "
                "(Last 90 Days): Not Contacted"
            )

    # ========================================================
    # RIGHT COLUMN
    # ========================================================

    with col_right:

        # ====================================================
        # ED UTILIZATION
        # ====================================================

        st.subheader(
            "ED Utilization"
        )

        # ----------------------------------------------------
        # PRIOR ED VISITS
        # ----------------------------------------------------

        prior_ed = patient.get(
            "prior_ed_visits",
            0
        )

        try:
            prior_ed = int(prior_ed)
        except (
            TypeError,
            ValueError
        ):
            prior_ed = 0

        # ----------------------------------------------------
        # ED LAST 30 DAYS
        # ----------------------------------------------------

        ed_30 = patient.get(
            "ed_visits_last_30_days",
            0
        )

        try:
            ed_30 = int(ed_30)
        except (
            TypeError,
            ValueError
        ):
            ed_30 = 0

        # ----------------------------------------------------
        # ED LAST 90 DAYS
        # ----------------------------------------------------

        ed_90 = patient.get(
            "ed_visits_last_90_days",
            0
        )

        try:
            ed_90 = int(ed_90)
        except (
            TypeError,
            ValueError
        ):
            ed_90 = 0

        # ----------------------------------------------------
        # DAYS SINCE LAST ED
        # ----------------------------------------------------

        days_since_ed = patient.get(
            "days_since_last_ed_visit"
        )

        try:

            if (
                days_since_ed is None
                or pd.isna(days_since_ed)
            ):
                days_since_ed_text = "None"

            else:
                days_since_ed_text = (
                    f"{int(days_since_ed)} days"
                )

        except (
            TypeError,
            ValueError
        ):
            days_since_ed_text = "None"

        # ----------------------------------------------------
        # METRICS
        # ----------------------------------------------------

        metric1, metric2 = st.columns(2)

        with metric1:

            st.metric(
                "Prior ED Visits",
                prior_ed
            )

            st.metric(
                "ED Visits (Last 30 Days)",
                ed_30
            )

        with metric2:

            st.metric(
                "ED Visits (Last 90 Days)",
                ed_90
            )

            st.metric(
                "Days Since Last ED Visit",
                days_since_ed_text
            )

        st.divider()

        