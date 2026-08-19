import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px


def render_analysis_result():

    # =========================================================
    # GET ANALYSIS DATA
    # =========================================================

    results = st.session_state.get("analysis_results")
    encounter = st.session_state.get("current_encounter_data")

    if not results or not encounter:
        st.warning("No analysis results found. Please create an encounter first.")

        if st.button("← Back to Patients"):
            st.session_state.page = "patients"
            st.rerun()

        return

    patient_id = encounter.get("patient_id", "Unknown")

    # =========================================================
    # BACK BUTTON
    # =========================================================

    if st.button("← Back to Patient Profile"):
        st.session_state.page = "patient_profile"
        st.rerun()

    st.write("")

    # =========================================================
    # PAGE TITLE
    # =========================================================

    st.title("AI Care Navigation Analysis")

    st.caption(
        f"AI clinical support results for Patient {patient_id}"
    )

    st.divider()

    # =========================================================
    # GET RESULTS
    # =========================================================

    prediction = results.get(
        "prediction",
        "Unknown"
    )

    confidence = float(
        results.get("confidence", 0)
    ) * 100

    prediction_class = results.get(
        "prediction_class",
        0
    )

    care_navigation = results.get(
        "care_navigation",
        {}
    )

    recommended = care_navigation.get(
        "recommended",
        "No recommendation available"
    )

    recommendation_detail = care_navigation.get(
        "detail",
        "No recommendation details available."
    )

    distribution = care_navigation.get(
        "distribution",
        {}
    )

    top_reasons = results.get(
        "top_reasons",
        []
    )

    shap_contributions = results.get(
        "shap_contributions",
        []
    )

    # =========================================================
    # PREDICTION STATUS
    # =========================================================

    is_avoidable = (
        prediction_class == 1
        or (
            "Potentially Avoidable" in prediction
            and "Not Potentially Avoidable" not in prediction
        )
    )

    # =========================================================
    # TOP TWO BOXES
    # =========================================================

    col1, col2 = st.columns(2)

    # ---------------------------------------------------------
    # AI PREDICTION
    # ---------------------------------------------------------

    with col1:

        st.subheader("AI Prediction Result")

        st.metric(
            label="Prediction",
            value=prediction
        )

        st.metric(
            label="Model Confidence",
            value=f"{confidence:.1f}%"
        )

        # Gauge

        fig_gauge = go.Figure(
            go.Indicator(
                mode="gauge+number",
                value=confidence,

                number={
                    "suffix": "%",
                    "font": {
                        "size": 30
                    }
                },

                title={
                    "text": "Confidence Level"
                },

                gauge={
                    "axis": {
                        "range": [0, 100]
                    },

                    "bar": {
                        "color": "#457B9D"
                    },

                    "steps": [
                        {
                            "range": [0, 50],
                            "color": "#F1F1F1"
                        },
                        {
                            "range": [50, 75],
                            "color": "#E5F1F4"
                        },
                        {
                            "range": [75, 100],
                            "color": "#D0E8F0"
                        }
                    ]
                }
            )
        )

        fig_gauge.update_layout(
            height=230,
            margin=dict(
                l=20,
                r=20,
                t=40,
                b=10
            )
        )

        st.plotly_chart(
            fig_gauge,
            use_container_width=True
        )

    # ---------------------------------------------------------
    # RECOMMENDATION
    # ---------------------------------------------------------

    with col2:

        st.subheader("Recommended Next Step")

        st.info(
            recommended
        )

        st.write(
            recommendation_detail
        )

        st.write("")

        if distribution:

            best_score = max(
                distribution.values()
            )

            st.metric(
                label="Best Pathway Match",
                value=f"{best_score}%"
            )

    st.divider()

    # =========================================================
    # MODEL REASONING
    # =========================================================

    st.subheader("Model Reasoning")

    st.caption(
        "Key factors contributing to the AI recommendation"
    )

    col3, col4 = st.columns([1.2, 0.8])

    # =========================================================
    # SHAP FEATURE CONTRIBUTIONS
    # =========================================================

    with col3:

        st.markdown("#### Feature Contributions")

        if shap_contributions:

            shap_df = pd.DataFrame(
                shap_contributions
            )

            if "feature" in shap_df.columns and "value" in shap_df.columns:

                shap_df["Readable Feature"] = (
                    shap_df["feature"]
                    .astype(str)
                    .str.replace("_", " ")
                    .str.title()
                )

                shap_df = shap_df.sort_values(
                    by="value",
                    ascending=True
                )

                fig_shap = go.Figure()

                fig_shap.add_trace(
                    go.Bar(
                        x=shap_df["value"],
                        y=shap_df["Readable Feature"],
                        orientation="h",
                        marker_color=[
                            "#E63946" if value >= 0
                            else "#457B9D"
                            for value in shap_df["value"]
                        ]
                    )
                )

                fig_shap.update_layout(
                    height=330,
                    xaxis_title="SHAP Value",
                    yaxis_title="",
                    margin=dict(
                        l=10,
                        r=20,
                        t=20,
                        b=40
                    )
                )

                st.plotly_chart(
                    fig_shap,
                    use_container_width=True
                )

            else:

                st.info(
                    "SHAP feature data is not available."
                )

        else:

            st.info(
                "No SHAP contribution data available."
            )

    # =========================================================
    # TOP 3 REASONS
    # =========================================================

    with col4:

        st.markdown("#### Top 3 Reasons")

        if top_reasons:

            for index, reason in enumerate(
                top_reasons[:3],
                start=1
            ):

                st.markdown(
                    f"**{index}.** {reason}"
                )

                if index < min(
                    3,
                    len(top_reasons)
                ):
                    st.write("")

        else:

            st.info(
                "No major contributing factors available."
            )

    st.divider()

    # =========================================================
    # CARE NAVIGATION SCORES
    # =========================================================

    col5, col6 = st.columns(2)

    with col5:

        st.subheader(
            "Care Navigation Scores"
        )

        if distribution:

            distribution_df = pd.DataFrame(
                list(
                    distribution.items()
                ),
                columns=[
                    "Pathway",
                    "Match Score"
                ]
            )

            distribution_df = distribution_df.sort_values(
                by="Match Score",
                ascending=True
            )

            fig_distribution = px.bar(
                distribution_df,
                x="Match Score",
                y="Pathway",
                orientation="h",
                text="Match Score"
            )

            fig_distribution.update_layout(
                height=300,
                xaxis_title="Suitability Score (%)",
                yaxis_title="",
                xaxis=dict(
                    range=[0, 105]
                ),
                margin=dict(
                    l=10,
                    r=20,
                    t=20,
                    b=40
                )
            )

            fig_distribution.update_traces(
                texttemplate="%{text}%",
                textposition="outside"
            )

            st.plotly_chart(
                fig_distribution,
                use_container_width=True
            )

        else:

            st.info(
                "No navigation score data available."
            )

    # =========================================================
    # AI EXPLANATION
    # =========================================================

    with col6:

        st.subheader(
            "AI Explanation"
        )

        severity = encounter.get(
            "severity",
            "Not specified"
        )

        systolic = encounter.get(
            "systolic_bp",
            "N/A"
        )

        diastolic = encounter.get(
            "diastolic_bp",
            "N/A"
        )

        temperature = encounter.get(
            "temperature",
            "N/A"
        )

        heart_rate = encounter.get(
            "heart_rate",
            "N/A"
        )

        avoidability_text = (
            "potentially avoidable"
            if is_avoidable
            else "not potentially avoidable"
        )

        st.markdown(
            "### Clinical Decision Summary"
        )

        st.write(
            f"""
            The model analyzed the patient's current encounter
            information together with their historical record.
            """
        )

        st.write(
            f"**Blood Pressure:** {systolic}/{diastolic} mmHg"
        )

        st.write(
            f"**Temperature:** {temperature} °C"
        )

        st.write(
            f"**Heart Rate:** {heart_rate} bpm"
        )

        st.write(
            f"**Clinical Severity:** {severity}"
        )

        st.write(
            f"The model calculated a **{confidence:.1f}% confidence** "
            f"that this presentation is **{avoidability_text}**."
        )

        st.write(
            f"**Recommended Pathway:** {recommended}"
        )

        st.write(
            recommendation_detail
        )

    st.divider()

    # =========================================================
    # DISCLAIMER
    # =========================================================

    st.warning(
        """
        ⚠️ **AI-Assisted Care Navigation Support Tool**

        This application is designed as a clinical decision-support
        tool to assist Care Managers in identifying appropriate care
        navigation options. It does not make clinical diagnoses,
        prescribe treatment, or override the independent clinical
        judgement of qualified healthcare professionals.
        """
    )