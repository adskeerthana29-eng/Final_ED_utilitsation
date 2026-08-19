import uuid
import datetime
import json
import streamlit as st
import pandas as pd

try:
    from carenavigator.database import get_patient_by_id, save_encounter
except ImportError:
    from database import get_patient_by_id, save_encounter

try:
    from ml.prediction.feature_builder import build_prediction_features
    from ml.prediction.prediction_service import predict_patient
    from ml.prediction.shap_service import get_top_shap_features
    from ml.navigation.navigation_service import navigate_patient
except ImportError:
    from prediction.feature_builder import build_prediction_features
    from prediction.prediction_service import predict_patient
    from prediction.shap_service import get_top_shap_features
    from navigation.navigation_service import navigate_patient


# ============================================================
# ENCOUNTER PAGE
# ============================================================

def render_encounter():

    # ============================================================
    # 1. GET SELECTED PATIENT
    # ============================================================

    patient_id = st.session_state.get("selected_patient_id")

    if not patient_id:
        st.error("No patient selected.")
        if st.button("Back to Patients"):
            st.session_state.page = "patients"
            st.rerun()
        return

    patient = get_patient_by_id(patient_id)

    if not patient:
        st.error(f"Patient {patient_id} not found.")
        return

    # ============================================================
    # CHECK IF ENCOUNTER ALREADY COMPLETED & SAVED (SUCCESS SCREEN)
    # ============================================================

    saved_info = st.session_state.get("completed_encounter_saved_info")
    if saved_info and saved_info.get("patient_id") == patient_id:
        st.success("✅ Encounter completed and saved successfully.")

        st.markdown("<div class='section-card'>", unsafe_allow_html=True)
        st.subheader("Encounter Completion Summary")

        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"**Encounter ID:** `{saved_info.get('encounter_id')}`")
            st.markdown(f"**Patient ID:** `{saved_info.get('patient_id')}`")
            st.markdown(f"**Care Manager ID:** `{saved_info.get('care_manager_id')}`")
            st.markdown(f"**Completed At:** `{saved_info.get('completion_timestamp')}`")

        with col2:
            st.markdown(f"**Classification:** `{saved_info.get('classification')}`")
            prob = float(saved_info.get("potentially_avoidable_probability", 0.0)) * 100
            st.markdown(f"**Avoidability Probability:** `{prob:.1f}%`")
            st.markdown(f"**Navigation Status:** `{saved_info.get('navigation_status')}`")
            if saved_info.get("safety_flag"):
                st.markdown("**Safety Review:** `🚨 Flagged for Clinical Safety Review`")

        st.markdown("</div>", unsafe_allow_html=True)

        col_btn1, col_btn2 = st.columns(2)
        with col_btn1:
            if st.button("← Back to Patients", use_container_width=True):
                st.session_state["completed_encounter_saved_info"] = None
                st.session_state["active_encounter_analysis"] = None
                st.session_state.page = "patients"
                st.rerun()
        with col_btn2:
            if st.button("➕ Start New Encounter", type="primary", use_container_width=True):
                st.session_state["completed_encounter_saved_info"] = None
                st.session_state["active_encounter_analysis"] = None
                st.rerun()
        return

    # ============================================================
    # PAGE HEADER
    # ============================================================

    st.title("Patient Encounter Analysis")
    st.caption(f"Patient ID: {patient_id}")
    st.divider()

    # ============================================================
    # 2. PATIENT INFORMATION
    # ============================================================

    st.subheader("Patient Information")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.write(f"**Patient ID:** {patient.get('patient_id', '-')}")
        st.write(f"**Name:** {patient.get('name', '-')}")
    with col2:
        st.write(f"**Gender:** {patient.get('gender', '-')}")
        st.write(f"**Region:** {patient.get('region', '-')}")
    with col3:
        st.write(f"**Past Diagnosis:** {patient.get('past_diagnosis_category_mode', '-')}")
        st.write(f"**Previous ED Visits:** {patient.get('prior_ed_visits', '-')}")

    st.divider()

    # ============================================================
    # 3. CLINICAL & ENCOUNTER INFORMATION
    # ============================================================

    st.subheader("Clinical Information")
    col1, col2, col3 = st.columns(3)

    with col1:
        patient_age = patient.get("age")
        if patient_age is None or pd.isna(patient_age):
            age = st.number_input("Age", min_value=0, max_value=120, value=50, step=1)
        else:
            age = int(patient_age)
            st.number_input("Age", min_value=0, max_value=120, value=age, disabled=True)

    with col2:
        existing_condition = patient.get("condition")
        condition_options = [
            "Asthma", "Back Pain", "Chronic Kidney Disease", "Coronary Artery Disease",
            "Depression", "GERD", "Hypertension", "Lung Cancer", "Multiple Sclerosis", "Type 2 Diabetes"
        ]
        condition_index = condition_options.index(existing_condition) if existing_condition in condition_options else 0
        condition = st.selectbox("Condition", condition_options, index=condition_index)

    with col3:
        diagnosis_options = [
            "Behavioral Health", "Cardiovascular", "Endocrine", "Gastrointestinal",
            "Musculoskeletal", "Neurologic", "Renal", "Respiratory"
        ]
        existing_diagnosis = patient.get("diagnosis_category")
        diagnosis_index = diagnosis_options.index(existing_diagnosis) if existing_diagnosis in diagnosis_options else 0
        diagnosis_category = st.selectbox("Diagnosis Category", diagnosis_options, index=diagnosis_index)

    st.divider()

    # ============================================================
    # 4. CURRENT VITALS
    # ============================================================

    st.subheader("Current Vitals")
    col1, col2, col3 = st.columns(3)

    with col1:
        systolic_bp = st.number_input("Systolic BP (mmHg)", min_value=50, max_value=250, value=140, step=1)
        diastolic_bp = st.number_input("Diastolic BP (mmHg)", min_value=30, max_value=150, value=85, step=1)
        heart_rate = st.number_input("Heart Rate (bpm)", min_value=30, max_value=220, value=82, step=1)

    with col2:
        temperature = st.number_input("Temperature (°C)", min_value=30.0, max_value=45.0, value=38.1, step=0.1)
        respiratory_rate = st.number_input("Respiratory Rate", min_value=5, max_value=60, value=19, step=1)
        oxygen_saturation = st.number_input("Oxygen Saturation (%)", min_value=50, max_value=100, value=96, step=1)

    with col3:
        triage_acuity = st.selectbox("Triage Acuity", options=[1, 2, 3, 4, 5], index=2)
        severity = st.selectbox("Severity", options=["Mild", "Moderate", "Severe"], index=1)
        symptom_duration_days = st.number_input("Symptom Duration (days)", min_value=0, max_value=365, value=3, step=1)

    st.divider()

    # ============================================================
    # 5. SYMPTOMS & BARRIERS
    # ============================================================

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Symptoms")
        symptom_fever_chills = st.checkbox("Fever / Chills", value=True)
        symptom_cold_cough = st.checkbox("Cold / Cough", value=True)
        symptom_vomiting = st.checkbox("Vomiting", value=False)

    with col2:
        st.subheader("Access Barriers")
        barrier_no_insurance = st.checkbox("No Insurance", value=False)
        barrier_after_hours_problem = st.checkbox("After-hours Access Problem", value=True)
        transportation_barrier = st.checkbox("Transportation Barrier", value=False)

    st.divider()

    # ============================================================
    # 6. ANALYZE ENCOUNTER BUTTON
    # ============================================================

    analyze = st.button("Analyze Encounter", type="primary", use_container_width=True)

    if analyze:
        encounter_data = {
            "age": age,
            "condition": condition,
            "diagnosis_category": diagnosis_category,
            "systolic_bp": systolic_bp,
            "diastolic_bp": diastolic_bp,
            "heart_rate": heart_rate,
            "temperature": temperature,
            "respiratory_rate": respiratory_rate,
            "oxygen_saturation": oxygen_saturation,
            "symptom_fever_chills": int(symptom_fever_chills),
            "symptom_cold_cough": int(symptom_cold_cough),
            "symptom_vomiting": int(symptom_vomiting),
            "symptom_duration_days": symptom_duration_days,
            "barrier_no_insurance": int(barrier_no_insurance),
            "barrier_after_hours_problem": int(barrier_after_hours_problem),
            "transportation_barrier": int(transportation_barrier),
            "severity": severity,
            "triage_acuity": triage_acuity
        }

        try:
            features = build_prediction_features(patient, encounter_data)
            prediction_result = predict_patient(features)
            shap_result = get_top_shap_features(features, top_n=10)
            navigation_result = navigate_patient(features)

            st.session_state["active_encounter_analysis"] = {
                "patient_id": patient_id,
                "encounter_data": encounter_data,
                "features": features,
                "prediction_result": prediction_result,
                "shap_result": shap_result,
                "navigation_result": navigation_result
            }
        except Exception as e:
            st.error(f"Analysis calculation failed: {e}")
            return

    # ============================================================
    # 7. DISPLAY ANALYSIS RESULTS & COMPLETE ENCOUNTER BUTTON
    # ============================================================

    analysis_state = st.session_state.get("active_encounter_analysis")
    if analysis_state and analysis_state.get("patient_id") == patient_id:
        enc_data = analysis_state["encounter_data"]
        pred_res = analysis_state["prediction_result"]
        shap_res = analysis_state["shap_result"]
        nav_res = analysis_state["navigation_result"]

        probability = pred_res["potentially_avoidable_probability"]
        prediction = pred_res["prediction"]
        classification = pred_res["classification"]
        navigation_status = nav_res.get("navigation_status", "No recommendation")
        safety_flag = nav_res.get("safety_flag", False)
        safety_reasons = nav_res.get("safety_reasons", [])
        reasons = nav_res.get("reasons", [])
        actions = nav_res.get("navigation_actions", [])

        st.divider()
        st.subheader("ML Prediction Result")

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Avoidability Probability", f"{probability * 100:.1f}%")
        with col2:
            st.metric("Prediction", str(prediction))
        with col3:
            st.metric("Classification", classification)

        if prediction == 1:
            st.warning("⚠️ Potentially Avoidable ED Utilization")
        else:
            st.success("✅ Non-Avoidable ED Utilization")

        # SHAP EXPLANATION
        st.subheader("Why did the model make this prediction?")
        if not shap_res.empty:
            display_shap = shap_res[["feature", "shap_value", "absolute_shap"]].copy()
            display_shap["direction"] = display_shap["shap_value"].apply(
                lambda x: "Increases avoidability" if x > 0 else "Decreases avoidability"
            )
            st.dataframe(display_shap, use_container_width=True, hide_index=True)

        # NAVIGATION RECOMMENDATION
        st.subheader("Navigation Recommendation")
        st.info(navigation_status)

        if safety_flag:
            st.error("🚨 Clinical Safety Review Required")
            for reason in safety_reasons:
                st.warning(f"• {reason}")

        if reasons:
            st.write("**Navigation Reasons**")
            for r in reasons:
                st.write(f"• {r}")

        if actions:
            st.write("**Recommended Actions**")
            for a in actions:
                st.write(f"• {a}")

        st.divider()

        # ============================================================
        # 8. CARE MANAGER "COMPLETE ENCOUNTER" BUTTON
        # ============================================================

        st.markdown("### Care Manager Action")
        st.caption("Review the prediction and recommendations above, then click below to finalize and persist the encounter record.")

        if st.button("Complete Encounter", type="primary", use_container_width=True):
            # Validate required data
            if not patient_id or pred_res is None or nav_res is None:
                st.error("Cannot complete encounter. Missing required analysis information.")
                return

            # Prepare SHAP reason string
            shap_reason_str = ""
            if not shap_res.empty:
                shap_reason_str = "; ".join(
                    [f"{row['feature']}: {row['shap_value']:.4f}" for _, row in shap_res.head(10).iterrows()]
                )

            enc_id = f"ENC-{uuid.uuid4().hex[:8].upper()}"
            completion_ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            care_mgr_id = st.session_state.get("user_id", "CM001")

            save_payload = {
                "encounter_id": enc_id,
                "patient_id": patient_id,
                "completion_timestamp": completion_ts,
                "care_manager_id": care_mgr_id,
                "age": enc_data["age"],
                "gender": patient.get("gender"),
                "region": patient.get("region"),
                "condition": enc_data["condition"],
                "diagnosis_category": enc_data["diagnosis_category"],
                "triage_acuity": enc_data["triage_acuity"],
                "severity": enc_data["severity"],
                "systolic_bp": enc_data["systolic_bp"],
                "diastolic_bp": enc_data["diastolic_bp"],
                "heart_rate": enc_data["heart_rate"],
                "temperature": enc_data["temperature"],
                "respiratory_rate": enc_data["respiratory_rate"],
                "oxygen_saturation": enc_data["oxygen_saturation"],
                "symptom_fever_chills": enc_data["symptom_fever_chills"],
                "symptom_cold_cough": enc_data["symptom_cold_cough"],
                "symptom_vomiting": enc_data["symptom_vomiting"],
                "symptom_duration_days": enc_data["symptom_duration_days"],
                "barrier_no_insurance": enc_data["barrier_no_insurance"],
                "barrier_after_hours_problem": enc_data["barrier_after_hours_problem"],
                "transportation_barrier": enc_data["transportation_barrier"],
                "alternative_care_access": patient.get("alternative_care_access", 0),
                "has_primary_care_provider": patient.get("has_primary_care_provider", 0),
                "potentially_avoidable_probability": probability,
                "prediction": prediction,
                "classification": classification,
                "navigation_status": navigation_status,
                "navigation_reasons": reasons,
                "navigation_actions": actions,
                "safety_flag": safety_flag,
                "safety_reasons": safety_reasons,
                "shap_reason": shap_reason_str,
                "process_completed": 1
            }

            try:
                saved_enc_id = save_encounter(save_payload)
                save_payload["encounter_id"] = saved_enc_id
                st.session_state["completed_encounter_saved_info"] = save_payload
                st.session_state["active_encounter_analysis"] = None
                st.rerun()
            except Exception as e:
                st.error(f"Unable to save encounter: {e}")