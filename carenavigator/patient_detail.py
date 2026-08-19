import streamlit as st
import pandas as pd
import plotly.graph_objects as go
try:
    from carenavigator.database import get_patient_by_id, get_patient_encounters
except ImportError:
    from database import get_patient_by_id, get_patient_encounters

def render_patient_detail():
    # Back button
    if st.button("← Back to Patients"):
        st.session_state.page = "patients"
        st.rerun()
        
    patient_id = st.session_state.get("selected_patient_id")
    if not patient_id:
        st.error("No patient selected.")
        return
        
    patient = get_patient_by_id(patient_id)
    if not patient:
        st.error(f"Patient with ID {patient_id} not found in database.")
        return
        
    # Demographic Header Card
    st.markdown("<div class='section-card'>", unsafe_allow_html=True)
    col_hdr, col_btn = st.columns([3, 1])
    p_age = patient.get('age')
    age_str = f"{int(p_age)}" if p_age is not None and not pd.isna(p_age) else "N/A"

    with col_hdr:
        st.markdown(f"""
            <span style='font-size:0.9rem; color:#666; font-weight:600;'>PATIENT PROFILE</span>
            <h1 style='margin:0; color:#1D3557;'>{patient['name']}</h1>
            <p style='margin:0.2rem 0; color:#444;'>
                ID: <b>{patient['patient_id']}</b> &nbsp;|&nbsp; 
                Age: <b>{age_str}</b> &nbsp;|&nbsp; 
                Gender: <b>{patient['gender']}</b> &nbsp;|&nbsp; 
                Region: <b>{patient['region']}</b>
            </p>
        """, unsafe_allow_html=True)
    with col_btn:
        st.write("") # Spacing
        if st.button("➕ New Encounter", use_container_width=True):
            st.session_state.page = "new_encounter"
            st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)
    
    st.write("")
    
    # 2-Column Details Layout
    col_left, col_right = st.columns([1, 1])
    
    with col_left:
        # Medical & Demographics details
        st.markdown("<div class='section-card'>", unsafe_allow_html=True)
        st.subheader("Clinical Summary")
        
        st.markdown(f"""
            <table class='detail-table'>
                <tr><th>Primary Condition</th><td>{patient.get('condition', 'N/A')}</td></tr>
                <tr><th>Diagnosis Category</th><td>{patient.get('diagnosis_category', 'N/A')}</td></tr>
                <tr><th>Past Diagnosis Mode</th><td>{patient.get('past_diagnosis_category_mode', 'N/A')}</td></tr>
                <tr><th>Triage Acuity Level</th><td>Level {int(patient.get('triage_acuity', 3))}</td></tr>
                <tr><th>Clinical Severity</th><td>{patient.get('severity', 'N/A')}</td></tr>
                <tr><th>Contact Phone</th><td>{patient.get('phone_number', 'N/A')}</td></tr>
            </table>
        """, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
        
        st.write("")
        
        # Hospitalization Section
        st.markdown("<div class='section-card'>", unsafe_allow_html=True)
        st.subheader("Hospitalization Information")
        st.info("Hospitalization Information: No hospitalization field available in current dataset.")
        st.markdown("</div>", unsafe_allow_html=True)
        
        st.write("")
        
        # Care Management Section
        st.markdown("<div class='section-card'>", unsafe_allow_html=True)
        st.subheader("Care Management & Primary Care")
        
        has_pcp = int(patient.get('has_primary_care_provider', 0))
        pcp_str = "Yes" if has_pcp == 1 else "No"
        avg_pcp_visits = patient.get('pcp_visits_last_12_months', 0)
        days_since_pcp = patient.get('days_since_last_pcp_visit', 0)
        
        st.markdown(f"""
            <table class='detail-table'>
                <tr><th>Primary Care Provider (PCP)</th><td><b>{pcp_str}</b></td></tr>
                <tr><th>PCP Visits (Last 12 Mo)</th><td>{int(avg_pcp_visits)} visits</td></tr>
                <tr><th>Days Since Last PCP Visit</th><td>{int(days_since_pcp)} days</td></tr>
                <tr><th>Alternative Care Access</th><td>{"Has Access" if patient.get('alternative_care_access') == 1 else "No Access"}</td></tr>
            </table>
        """, unsafe_allow_html=True)
        
        st.write("")
        
        # Visual indicator of CM Contact
        cm_contact = int(patient.get('care_management_contact_last_90_days', 0))
        cm_label = "Contacted" if cm_contact == 1 else "Not Contacted"
        cm_color = "#457B9D" if cm_contact == 1 else "#E63946"
        
        st.markdown(f"""
            <div style='background-color:#F8F9FA; padding:1rem; border-radius:8px; border-left:4px solid {cm_color}; text-align:center;'>
                <span style='font-size:0.85rem; color:#666;'>Care Management Contact (Last 90 Days)</span>
                <h3 style='margin:0.2rem 0; color:{cm_color};'>{cm_label}</h3>
            </div>
        """, unsafe_allow_html=True)
        
        st.markdown("</div>", unsafe_allow_html=True)
        
    with col_right:
        # ED Utilization Section
        st.markdown("<div class='section-card'>", unsafe_allow_html=True)
        st.subheader("ED Utilization")
        
        col_ed1, col_ed2 = st.columns(2)
        with col_ed1:
            st.metric("Prior ED Visits", int(patient.get('prior_ed_visits', 0)))
            st.metric("ED Visits (Last 30 Days)", int(patient.get('ed_visits_last_30_days', 0)))
        with col_ed2:
            st.metric("ED Visits (Last 90 Days)", int(patient.get('ed_visits_last_90_days', 0)))
            days_since_ed = patient.get('days_since_last_ed_visit', 0)
            st.metric("Days Since Last ED Visit", f"{int(days_since_ed)} days" if not pd.isna(days_since_ed) else "None")
            
        st.divider()
        
        # Avoidable Probability Display
        avoidable_status = "Potentially Avoidable" if int(patient.get('potentially_avoidable', 0)) == 1 else "Non-Avoidable"
        prob_val = float(patient.get('potentially_avoidable_probability', 0.0)) * 100
        
        st.markdown(f"""
            <div style='margin-bottom:1rem;'>
                <strong>Historical Avoidable Status:</strong> 
                <span style='font-size:1.1rem; color:#457B9D; font-weight:bold;'>{avoidable_status}</span>
            </div>
        """, unsafe_allow_html=True)
        
        st.markdown(f"**Avoidability Probability: {prob_val:.1f}%**")
        st.progress(prob_val / 100.0)
        st.markdown("</div>", unsafe_allow_html=True)
        
        st.write("")
        
        # Encounter History Section
        st.markdown("<div class='section-card'>", unsafe_allow_html=True)
        st.subheader("Recent Encounter Logs")
        
        encounters = get_patient_encounters(patient_id)
        if not encounters:
            st.info("No previous encounter logs found for this patient.")
        else:
            for idx, enc in enumerate(encounters):
                with st.expander(f"Encounter {enc['encounter_id']} - {enc['timestamp'][:16]}", expanded=(idx == 0)):
                    st.markdown(f"""
                        **Clinical Summary:**
                        - Vitals: BP `{int(enc['systolic_bp'])}/{int(enc['diastolic_bp'])} mmHg`, HR `{int(enc['heart_rate'])} bpm`, Temp `{enc['temperature']} °C`, O2 `{int(enc['oxygen_saturation'])}%`
                        - Severity: `{enc['severity']}` | Symptom Duration: `{enc['symptom_duration_days']} Days`
                        - Recommendation: **{enc.get('recommendation', 'N/A')}**
                        - Predict: `{enc.get('prediction_result', 'N/A')}` ({round(float(enc.get('confidence_score', 0)) * 100, 1)}% Conf)
                    """)
        st.markdown("</div>", unsafe_allow_html=True)
