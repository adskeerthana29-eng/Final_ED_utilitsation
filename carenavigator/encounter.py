import uuid
import datetime
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

    # ========================================================
    # 1. GET SELECTED PATIENT
    # ========================================================

    patient_id = st.session_state.get("selected_patient_id")

    if not patient_id:

        st.error("No patient selected.")

        if st.button(
            "Back to Patients",
            key="enc_back_no_patient"
        ):
            st.session_state.page = "patients"
            st.rerun()

        return

    patient = get_patient_by_id(patient_id)

    if not patient:

        st.error(
            f"Patient {patient_id} not found."
        )

        return


    # ========================================================
    # 2. CHECK IF ENCOUNTER ALREADY COMPLETED
    # ========================================================

    saved_info = st.session_state.get(
        "completed_encounter_saved_info"
    )

    if (
        saved_info
        and saved_info.get("patient_id") == patient_id
    ):

        st.success(
            "✅ Encounter completed and saved successfully."
        )

        st.markdown(
            "<div class='section-card'>",
            unsafe_allow_html=True
        )

        st.subheader(
            "Encounter Completion Summary"
        )

        col1, col2 = st.columns(2)

        with col1:

            st.markdown(
                f"**Encounter ID:** "
                f"`{saved_info.get('encounter_id')}`"
            )

            st.markdown(
                f"**Patient ID:** "
                f"`{saved_info.get('patient_id')}`"
            )

            st.markdown(
                f"**Care Manager ID:** "
                f"`{saved_info.get('care_manager_id')}`"
            )

            st.markdown(
                f"**Completed At:** "
                f"`{saved_info.get('completion_timestamp')}`"
            )

        with col2:

            st.markdown(
                f"**Classification:** "
                f"`{saved_info.get('classification')}`"
            )

            prob = float(
                saved_info.get(
                    "potentially_avoidable_probability",
                    0.0
                )
            ) * 100

            st.markdown(
                f"**Avoidability Probability:** "
                f"`{prob:.1f}%`"
            )

            st.markdown(
                f"**Navigation Status:** "
                f"`{saved_info.get('navigation_status')}`"
            )

            if saved_info.get("safety_flag"):

                st.markdown(
                    "**Safety Review:** "
                    "`🚨 Flagged for Clinical Safety Review`"
                )

        st.markdown(
            "</div>",
            unsafe_allow_html=True
        )

        col_btn1, col_btn2 = st.columns(2)

        with col_btn1:

            if st.button(
                "← Back to Patients",
                key="enc_back_completed",
                use_container_width=True
            ):

                st.session_state[
                    "completed_encounter_saved_info"
                ] = None

                st.session_state[
                    "active_encounter_analysis"
                ] = None

                st.session_state.page = "patients"

                st.rerun()

        with col_btn2:

            if st.button(
                "➕ Start New Encounter",
                key="enc_new_completed",
                type="primary",
                use_container_width=True
            ):

                st.session_state[
                    "completed_encounter_saved_info"
                ] = None

                st.session_state[
                    "active_encounter_analysis"
                ] = None

                st.rerun()

        return


    # ========================================================
    # 3. PAGE HEADER
    # ========================================================

    st.title(
        "Patient Encounter Analysis"
    )

    st.caption(
        f"Patient ID: {patient_id}"
    )

    st.divider()


    # ========================================================
    # 4. PATIENT INFORMATION
    # ========================================================

    st.subheader(
        "Patient Information"
    )

    col1, col2, col3 = st.columns(3)

    with col1:

        st.write(
            f"**Patient ID:** "
            f"{patient.get('patient_id', '-')}"
        )

        st.write(
            f"**Name:** "
            f"{patient.get('name', '-')}"
        )

    with col2:

        st.write(
            f"**Gender:** "
            f"{patient.get('gender', '-')}"
        )

        st.write(
            f"**Region:** "
            f"{patient.get('region', '-')}"
        )

    with col3:

        st.write(
            f"**Past Diagnosis:** "
            f"{patient.get('past_diagnosis_category_mode', '-')}"
        )

        st.write(
            f"**Previous ED Visits:** "
            f"{patient.get('prior_ed_visits', '-')}"
        )

    st.divider()


    # ========================================================
    # 5. CLINICAL INFORMATION
    # ========================================================

    st.subheader(
        "Clinical Information"
    )

    col1, col2, col3 = st.columns(3)


    # --------------------------------------------------------
    # AGE
    # --------------------------------------------------------

    with col1:

        patient_age = patient.get("age")

        if (
            patient_age is None
            or pd.isna(patient_age)
        ):

            age = st.number_input(
                "Age",
                min_value=0,
                max_value=120,
                value=50,
                step=1,
                key="enc_age_missing"
            )

        else:

            age = int(patient_age)

            st.number_input(
                "Age",
                min_value=0,
                max_value=120,
                value=age,
                step=1,
                disabled=True,
                key="enc_age_ehr"
            )


    # --------------------------------------------------------
    # CONDITION
    # --------------------------------------------------------

    with col2:

        existing_condition = patient.get(
            "condition"
        )

        condition_options = [
            "Asthma",
            "Back Pain",
            "Chronic Kidney Disease",
            "Coronary Artery Disease",
            "Depression",
            "GERD",
            "Hypertension",
            "Lung Cancer",
            "Multiple Sclerosis",
            "Type 2 Diabetes"
        ]

        condition_index = (
            condition_options.index(
                existing_condition
            )
            if existing_condition
            in condition_options
            else 0
        )

        condition = st.selectbox(
            "Condition",
            condition_options,
            index=condition_index,
            key="enc_condition"
        )


    # --------------------------------------------------------
    # DIAGNOSIS CATEGORY
    # --------------------------------------------------------

    with col3:

        diagnosis_options = [
            "Behavioral Health",
            "Cardiovascular",
            "Endocrine",
            "Gastrointestinal",
            "Musculoskeletal",
            "Neurologic",
            "Renal",
            "Respiratory"
        ]

        existing_diagnosis = patient.get(
            "diagnosis_category"
        )

        diagnosis_index = (
            diagnosis_options.index(
                existing_diagnosis
            )
            if existing_diagnosis
            in diagnosis_options
            else 0
        )

        diagnosis_category = st.selectbox(
            "Diagnosis Category",
            diagnosis_options,
            index=diagnosis_index,
            key="enc_diagnosis_category"
        )

    st.divider()


    # ========================================================
    # 6. CURRENT VITALS
    # ========================================================

    st.subheader(
        "Current Vitals"
    )

    st.caption(
        "Enter only the patient's current encounter values."
    )

    col1, col2, col3 = st.columns(3)


    with col1:

        systolic_bp = st.number_input(
            "Systolic BP (mmHg)",
            min_value=50,
            max_value=250,
            value=120,
            step=1,
            key="enc_systolic_bp"
        )

        diastolic_bp = st.number_input(
            "Diastolic BP (mmHg)",
            min_value=30,
            max_value=150,
            value=80,
            step=1,
            key="enc_diastolic_bp"
        )

        heart_rate = st.number_input(
            "Heart Rate (bpm)",
            min_value=30,
            max_value=220,
            value=80,
            step=1,
            key="enc_heart_rate"
        )


    with col2:

        # ----------------------------------------------------
        # USER ENTERS CELSIUS
        # MODEL RECEIVES FAHRENHEIT
        # ----------------------------------------------------

        temperature = st.number_input(
            "Temperature (°C)",
            min_value=30.0,
            max_value=45.0,
            value=37.0,
            step=0.1,
            key="enc_temperature_c"
        )

        respiratory_rate = st.number_input(
            "Respiratory Rate",
            min_value=5,
            max_value=60,
            value=18,
            step=1,
            key="enc_respiratory_rate"
        )

        oxygen_saturation = st.number_input(
            "Oxygen Saturation (%)",
            min_value=50,
            max_value=100,
            value=98,
            step=1,
            key="enc_oxygen_saturation"
        )


    with col3:

        triage_acuity = st.selectbox(
            "Triage Acuity",
            options=[1, 2, 3, 4, 5],
            index=3,
            key="enc_triage_acuity"
        )

        severity = st.selectbox(
            "Severity",
            options=[
                "Mild",
                "Moderate",
                "Severe"
            ],
            index=0,
            key="enc_severity"
        )

        symptom_duration_days = st.number_input(
            "Symptom Duration (days)",
            min_value=0,
            max_value=365,
            value=3,
            step=1,
            key="enc_symptom_duration"
        )

    st.divider()


    # ========================================================
    # 7. SYMPTOMS & BARRIERS
    # ========================================================

    col1, col2 = st.columns(2)


    with col1:

        st.subheader(
            "Symptoms"
        )

        symptom_fever_chills = st.checkbox(
            "Fever / Chills",
            value=False,
            key="enc_fever_chills"
        )

        symptom_cold_cough = st.checkbox(
            "Cold / Cough",
            value=False,
            key="enc_cold_cough"
        )

        symptom_vomiting = st.checkbox(
            "Vomiting",
            value=False,
            key="enc_vomiting"
        )


    with col2:

        st.subheader(
            "Access Barriers"
        )

        barrier_no_insurance = st.checkbox(
            "No Insurance",
            value=False,
            key="enc_no_insurance"
        )

        barrier_after_hours_problem = st.checkbox(
            "After-hours Access Problem",
            value=False,
            key="enc_after_hours"
        )

        transportation_barrier = st.checkbox(
            "Transportation Barrier",
            value=False,
            key="enc_transportation"
        )

    st.divider()


    # ========================================================
    # 8. ANALYZE ENCOUNTER
    # ========================================================

    analyze = st.button(
        "Analyze Encounter",
        type="primary",
        use_container_width=True,
        key="enc_analyze"
    )


    if analyze:

        # ====================================================
        # TEMPERATURE CONVERSION
        # ====================================================

        temperature_f = (
            temperature * 9 / 5
        ) + 32


        # ====================================================
        # CURRENT ENCOUNTER DATA
        # ====================================================

        encounter_data = {

            "age": age,

            "condition": condition,

            "diagnosis_category":
                diagnosis_category,

            "systolic_bp":
                systolic_bp,

            "diastolic_bp":
                diastolic_bp,

            "heart_rate":
                heart_rate,

            "temperature":
                temperature_f,

            "respiratory_rate":
                respiratory_rate,

            "oxygen_saturation":
                oxygen_saturation,

            "symptom_fever_chills":
                int(symptom_fever_chills),

            "symptom_cold_cough":
                int(symptom_cold_cough),

            "symptom_vomiting":
                int(symptom_vomiting),

            "symptom_duration_days":
                symptom_duration_days,

            "barrier_no_insurance":
                int(barrier_no_insurance),

            "barrier_after_hours_problem":
                int(barrier_after_hours_problem),

            "transportation_barrier":
                int(transportation_barrier),

            "severity":
                severity,

            "triage_acuity":
                triage_acuity
        }


        # ====================================================
        # DEBUG INFORMATION
        # ====================================================

        with st.expander(
            "Model Input Preview"
        ):

            st.write(
                "Temperature entered:"
            )

            st.write(
                f"{temperature:.1f} °C"
            )

            st.write(
                "Temperature sent to model:"
            )

            st.write(
                f"{temperature_f:.2f} °F"
            )

            st.json(
                encounter_data
            )


        # ====================================================
        # FEATURE ENGINEERING
        # ====================================================

        try:

            features = build_prediction_features(
                patient,
                encounter_data
            )

        except Exception as e:

            st.error(
                "Feature engineering failed."
            )

            st.exception(e)

            return


        # ====================================================
        # CATBOOST PREDICTION
        # ====================================================

        try:

            prediction_result = predict_patient(
                features
            )

        except Exception as e:

            st.error(
                "Prediction failed."
            )

            st.exception(e)

            return


        # ====================================================
        # SHAP EXPLANATION
        # ====================================================

        try:

            shap_result = get_top_shap_features(
                features,
                top_n=10
            )

        except Exception as e:

            st.warning(
                "SHAP explanation could not be generated."
            )

            shap_result = pd.DataFrame()


        # ====================================================
        # NAVIGATION
        #
        # IMPORTANT:
        # Use the SAME CatBoost prediction.
        # Do not predict again inside encounter.py.
        # ====================================================

        try:

            navigation_result = navigate_patient(
                features,
                prediction_result
            )

        except TypeError:

            # Compatibility with an older
            # navigation_service.py
            try:

                navigation_result = navigate_patient(
                    features
                )

            except Exception as e:

                st.error(
                    "Navigation analysis failed."
                )

                st.exception(e)

                return

        except Exception as e:

            st.error(
                "Navigation analysis failed."
            )

            st.exception(e)

            return


        # ====================================================
        # SAVE ANALYSIS TO SESSION
        # ====================================================

        st.session_state[
            "active_encounter_analysis"
        ] = {

            "patient_id":
                patient_id,

            "encounter_data":
                encounter_data,

            "features":
                features,

            "prediction_result":
                prediction_result,

            "shap_result":
                shap_result,

            "navigation_result":
                navigation_result
        }


    # ========================================================
    # 9. DISPLAY ANALYSIS RESULTS
    # ========================================================

    analysis_state = st.session_state.get(
        "active_encounter_analysis"
    )

    if (
        analysis_state
        and analysis_state.get(
            "patient_id"
        ) == patient_id
    ):

        enc_data = (
            analysis_state[
                "encounter_data"
            ]
        )

        pred_res = (
            analysis_state[
                "prediction_result"
            ]
        )

        shap_res = (
            analysis_state[
                "shap_result"
            ]
        )

        nav_res = (
            analysis_state[
                "navigation_result"
            ]
        )


        # ====================================================
        # PREDICTION VALUES
        # ====================================================

        probability = float(
            pred_res.get(
                "potentially_avoidable_probability",
                0.0
            )
        )

        prediction = pred_res.get(
            "prediction",
            0
        )

        classification = pred_res.get(
            "classification",
            "Unknown"
        )


        # ====================================================
        # NAVIGATION VALUES
        # ====================================================

        navigation_status = nav_res.get(
            "status_label",
            nav_res.get(
                "navigation_status",
                "Navigation assessment unavailable"
            )
        )

        navigation_state = nav_res.get(
            "status",
            ""
        )

        recommendation = nav_res.get(
            "recommendation",
            ""
        )

        recommended_pathway = nav_res.get(
            "recommended_pathway",
            ""
        )

        care_manager_action = nav_res.get(
            "care_manager_action",
            ""
        )

        safety_flag = nav_res.get(
            "safety_override",
            nav_res.get(
                "safety_flag",
                False
            )
        )

        safety_reasons = nav_res.get(
            "safety_reasons",
            []
        )

        barriers = nav_res.get(
            "barriers",
            []
        )

        navigation_options = nav_res.get(
            "navigation_options",
            []
        )

        disclaimer = nav_res.get(
            "disclaimer",
            ""
        )


        # ====================================================
        # ML PREDICTION RESULT
        # ====================================================

        st.divider()

        st.subheader(
            "ML Prediction Result"
        )

        col1, col2, col3 = st.columns(3)

        with col1:

            st.metric(
                "Avoidability Probability",
                f"{probability * 100:.1f}%"
            )

        with col2:

            st.metric(
                "Prediction",
                str(prediction)
            )

        with col3:

            st.metric(
                "Classification",
                classification
            )


        # ====================================================
        # PREDICTION MESSAGE
        # ====================================================

        if safety_flag:

            st.error(
                "🚨 Clinical Safety Review Required"
            )

        elif navigation_state == "potentially_avoidable":

            st.success(
                " Potentially Avoidable ED Utilization"
            )

        elif navigation_state == "borderline":

            st.warning(
                "🟡 Borderline / Care Manager Review"
            )

        else:

            st.success(
                "🔵 Lower Likelihood of Avoidability"
            )


        # ====================================================
        # SHAP EXPLANATION
        # ====================================================

        st.subheader(
            "Why did the model make this prediction?"
        )


        if (
            isinstance(
                shap_res,
                pd.DataFrame
            )
            and not shap_res.empty
        ):

            required_columns = [
                "feature",
                "shap_value",
                "absolute_shap"
            ]

            available_columns = [
                c
                for c in required_columns
                if c in shap_res.columns
            ]

            if available_columns:

                display_shap = (
                    shap_res[
                        available_columns
                    ].copy()
                )

                if "shap_value" in display_shap.columns:

                    display_shap[
                        "direction"
                    ] = display_shap[
                        "shap_value"
                    ].apply(
                        lambda x:
                        "Increases avoidability"
                        if x > 0
                        else
                        "Decreases avoidability"
                    )

                st.dataframe(
                    display_shap,
                    use_container_width=True,
                    hide_index=True
                )

            else:

                st.write(
                    shap_res
                )

        elif shap_res:

            st.write(
                shap_res
            )

        else:

            st.info(
                "No SHAP explanation available."
            )


        # ====================================================
        # NAVIGATION RECOMMENDATION
        # ====================================================

        st.divider()

        st.subheader(
            "🧭 Navigation Recommendation"
        )


        # ----------------------------------------------------
        # STATUS
        # ----------------------------------------------------

        if safety_flag:

            st.error(
                f"🚨 {navigation_status}"
            )

        elif navigation_state == "potentially_avoidable":

            st.success(
                f"🟢 {navigation_status}"
            )

        elif navigation_state == "borderline":

            st.warning(
                f"🟡 {navigation_status}"
            )

        elif navigation_state in [
            "low_avoidability",
            "non_avoidable",
            "not_avoidable"
        ]:

            st.info(
                f"🔵 {navigation_status}"
            )

        else:

            st.info(
                navigation_status
            )


        # ----------------------------------------------------
        # ASSESSMENT
        # ----------------------------------------------------

        if recommendation:

            st.markdown(
                "**Assessment**"
            )

            st.write(
                recommendation
            )


        # ----------------------------------------------------
        # RECOMMENDED PATHWAY
        # ----------------------------------------------------

        if recommended_pathway:

            st.markdown(
                "**Recommended Pathway**"
            )

            st.info(
                recommended_pathway
            )


        # ----------------------------------------------------
        # SAFETY REVIEW
        # ----------------------------------------------------

        if safety_flag:

            st.markdown(
                "### 🚨 Clinical Safety Review"
            )

            for reason in safety_reasons:

                st.warning(
                    f"• {reason}"
                )


        # ----------------------------------------------------
        # ACCESS BARRIERS
        # ----------------------------------------------------

        if barriers:

            st.markdown(
                "### Access Barriers"
            )

            for barrier in barriers:

                if isinstance(
                    barrier,
                    dict
                ):

                    title = barrier.get(
                        "title",
                        "Access Barrier"
                    )

                    description = barrier.get(
                        "description",
                        ""
                    )

                    action = barrier.get(
                        "action",
                        ""
                    )

                    st.markdown(
                        f"**{title}**"
                    )

                    if description:

                        st.write(
                            description
                        )

                    if action:

                        st.write(
                            f"→ {action}"
                        )

                else:

                    st.write(
                        f"• {barrier}"
                    )


        # ----------------------------------------------------
        # NAVIGATION OPTIONS
        # ----------------------------------------------------

        if navigation_options:

            st.markdown(
                "### Potential Care-Pathway Options"
            )

            for option in navigation_options:

                if isinstance(
                    option,
                    dict
                ):

                    pathway = option.get(
                        "pathway",
                        "Care option"
                    )

                    reason = option.get(
                        "reason",
                        ""
                    )

                    st.markdown(
                        f"**• {pathway}**"
                    )

                    if reason:

                        st.caption(
                            reason
                        )

                else:

                    st.markdown(
                        f"**• {option}**"
                    )


        # ----------------------------------------------------
        # CARE MANAGER ACTION
        # ----------------------------------------------------

        if care_manager_action:

            st.markdown(
                "### 👩‍⚕️ Care Manager Action"
            )

            st.info(
                care_manager_action
            )


        # ----------------------------------------------------
        # DISCLAIMER
        # ----------------------------------------------------

        if disclaimer:

            st.caption(
                f"ℹ️ {disclaimer}"
            )


        st.divider()


        # ====================================================
        # 10. COMPLETE ENCOUNTER
        # ====================================================

        st.markdown(
            "### Care Manager Action"
        )

        st.caption(
            "Review the prediction and navigation "
            "recommendation before finalizing the encounter."
        )


        if st.button(
            "Complete Encounter",
            type="primary",
            use_container_width=True,
            key="enc_complete"
        ):

            if (
                not patient_id
                or pred_res is None
                or nav_res is None
            ):

                st.error(
                    "Cannot complete encounter. "
                    "Missing required analysis information."
                )

                return


            # =================================================
            # SHAP REASON STRING
            # =================================================

            shap_reason_str = ""

            if (
                isinstance(
                    shap_res,
                    pd.DataFrame
                )
                and not shap_res.empty
                and "feature" in shap_res.columns
                and "shap_value" in shap_res.columns
            ):

                shap_reason_str = "; ".join(

                    [
                        (
                            f"{row['feature']}: "
                            f"{row['shap_value']:.4f}"
                        )

                        for _, row
                        in shap_res.head(10).iterrows()
                    ]
                )


            # =================================================
            # ENCOUNTER METADATA
            # =================================================

            enc_id = (
                f"ENC-"
                f"{uuid.uuid4().hex[:8].upper()}"
            )

            completion_ts = (
                datetime.datetime.now().strftime(
                    "%Y-%m-%d %H:%M:%S"
                )
            )

            care_mgr_id = (
                st.session_state.get(
                    "user_id",
                    "CM001"
                )
            )


            # =================================================
            # SAVE PAYLOAD
            # =================================================

            save_payload = {

                "encounter_id":
                    enc_id,

                "patient_id":
                    patient_id,

                "completion_timestamp":
                    completion_ts,

                "care_manager_id":
                    care_mgr_id,

                "age":
                    enc_data["age"],

                "gender":
                    patient.get("gender"),

                "region":
                    patient.get("region"),

                "condition":
                    enc_data["condition"],

                "diagnosis_category":
                    enc_data[
                        "diagnosis_category"
                    ],

                "triage_acuity":
                    enc_data[
                        "triage_acuity"
                    ],

                "severity":
                    enc_data[
                        "severity"
                    ],

                "systolic_bp":
                    enc_data[
                        "systolic_bp"
                    ],

                "diastolic_bp":
                    enc_data[
                        "diastolic_bp"
                    ],

                "heart_rate":
                    enc_data[
                        "heart_rate"
                    ],

                "temperature":
                    enc_data[
                        "temperature"
                    ],

                "respiratory_rate":
                    enc_data[
                        "respiratory_rate"
                    ],

                "oxygen_saturation":
                    enc_data[
                        "oxygen_saturation"
                    ],

                "symptom_fever_chills":
                    enc_data[
                        "symptom_fever_chills"
                    ],

                "symptom_cold_cough":
                    enc_data[
                        "symptom_cold_cough"
                    ],

                "symptom_vomiting":
                    enc_data[
                        "symptom_vomiting"
                    ],

                "symptom_duration_days":
                    enc_data[
                        "symptom_duration_days"
                    ],

                "barrier_no_insurance":
                    enc_data[
                        "barrier_no_insurance"
                    ],

                "barrier_after_hours_problem":
                    enc_data[
                        "barrier_after_hours_problem"
                    ],

                "transportation_barrier":
                    enc_data[
                        "transportation_barrier"
                    ],

                "alternative_care_access":
                    patient.get(
                        "alternative_care_access",
                        0
                    ),

                "has_primary_care_provider":
                    patient.get(
                        "has_primary_care_provider",
                        0
                    ),

                "potentially_avoidable_probability":
                    probability,

                "prediction":
                    prediction,

                "classification":
                    classification,

                # ------------------------------------------------
                # NEW NAVIGATION FIELDS
                # ------------------------------------------------

                "navigation_status":
                    navigation_status,

                "navigation_recommendation":
                    recommendation,

                "recommended_pathway":
                    recommended_pathway,

                "care_manager_action":
                    care_manager_action,

                "navigation_reasons":
                    [
                        (
                            b.get(
                                "description",
                                ""
                            )
                            if isinstance(
                                b,
                                dict
                            )
                            else str(b)
                        )

                        for b in barriers
                    ],

                "navigation_actions":
                    [
                        (
                            o.get(
                                "pathway",
                                ""
                            )
                            if isinstance(
                                o,
                                dict
                            )
                            else str(o)
                        )

                        for o in navigation_options
                    ],

                "safety_flag":
                    safety_flag,

                "safety_reasons":
                    safety_reasons,

                "navigation_disclaimer":
                    disclaimer,

                "shap_reason":
                    shap_reason_str,

                "process_completed":
                    1
            }


            # =================================================
            # SAVE TO DATABASE
            # =================================================

            try:

                saved_enc_id = save_encounter(
                    save_payload
                )

                save_payload[
                    "encounter_id"
                ] = saved_enc_id

                st.session_state[
                    "completed_encounter_saved_info"
                ] = save_payload

                st.session_state[
                    "active_encounter_analysis"
                ] = None

                st.rerun()

            except Exception as e:

                st.error(
                    f"Unable to save encounter: {e}"
                )