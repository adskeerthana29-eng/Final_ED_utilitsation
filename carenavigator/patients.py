import streamlit as st
import pandas as pd
try:
    from carenavigator.database import get_filtered_patients, get_diagnosis_categories
except ImportError:
    from database import get_filtered_patients, get_diagnosis_categories

def render_patients():
    st.markdown("<div class='section-card'>", unsafe_allow_html=True)
    st.title("Patient Profiles")
    st.markdown("<p style='color:#555;'>Search and review patient care utilization history</p>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)
    
    st.write("")
    
    # Search and Filter card
    st.markdown("<div class='section-card'>", unsafe_allow_html=True)
    col_search, col_ed, col_sym = st.columns([2, 1.5, 1.5])
    
    with col_search:
        search_query = st.text_input(
            "Search by Patient ID or Name",
            value=st.session_state.get("patient_search_query", ""),
            placeholder="e.g. P-FE8F2ED3 or Henry..."
        )
        st.session_state["patient_search_query"] = search_query
        
    with col_ed:
        ed_filter = st.selectbox(
            "ED Visit Filter",
            options=["All", "ED visit in last 30 days", "ED visit in last 90 days"],
            index=0
        )
        
    with col_sym:
        # Get diagnosis categories dynamically from database
        db_categories = get_diagnosis_categories()
        symptom_options = ["All", "Fever / Chills", "Cold / Cough", "Vomiting"] + db_categories
        
        symptom_filter = st.selectbox(
            "Symptom / Diagnosis Category",
            options=symptom_options,
            index=0
        )
        
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Load and filter patient data
    df_filtered = get_filtered_patients(search_query, ed_filter, symptom_filter)
    
    st.write("")
    st.markdown(f"**Found {len(df_filtered)} matching patients**")
    
    if len(df_filtered) == 0:
        st.info("No patient records match the selected criteria.")
        return
        
    # Table Header
    st.markdown("<div class='table-header'>", unsafe_allow_html=True)
    h_col1, h_col2, h_col3, h_col4, h_col5, h_col6 = st.columns([1.5, 2.5, 1, 2, 2, 1.5])
    h_col1.markdown("**Patient ID**")
    h_col2.markdown("**Name**")
    h_col3.markdown("**Age**")
    h_col4.markdown("**Days Since Last ED**")
    h_col5.markdown("**ED Utilization**")
    h_col6.markdown("**Action**")
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Pagination
    limit = 20
    total_pages = max(1, (len(df_filtered) + limit - 1) // limit)
    current_page = st.number_input("Page", min_value=1, max_value=total_pages, value=1, step=1)
    
    start_idx = (current_page - 1) * limit
    end_idx = min(start_idx + limit, len(df_filtered))
    
    page_items = df_filtered.iloc[start_idx:end_idx].to_dict('records')
    
    # Display rows
    for p in page_items:
        prior_ed = p.get('prior_ed_visits', 0)
        
        # Determine color indicator badge based on prior ED visits
        if prior_ed >= 5:
            badge_html = "<span class='badge badge-red'>🔴 High ED</span>"
        elif prior_ed >= 2:
            badge_html = "<span class='badge badge-orange'>🟠 Mod ED</span>"
        else:
            badge_html = "<span class='badge badge-yellow'>🟡 Low ED</span>"
            
        st.markdown("<div class='table-row'>", unsafe_allow_html=True)
        r_col1, r_col2, r_col3, r_col4, r_col5, r_col6 = st.columns([1.5, 2.5, 1, 2, 2, 1.5])
        
        # Column 1: Patient ID + Status Indicator
        r_col1.markdown(f"**{p['patient_id']}**", unsafe_allow_html=True)
        
        # Column 2: Patient Name
        r_col2.markdown(p['name'])
        
        # Column 3: Age
        patient_age = p.get('age')
        if patient_age is not None and not pd.isna(patient_age):
            age_str = str(int(patient_age))
        else:
            age_str = "N/A"
        r_col3.markdown(age_str)
        
        # Column 4: Days Since Last ED Visit
        days_since_ed = p.get('days_since_last_ed_visit', 'N/A')
        if pd.isna(days_since_ed):
            days_str = "None"
        else:
            days_str = f"{int(days_since_ed)} days"
        r_col4.markdown(days_str)
        
        # Column 5: ED Utilization Badge
        r_col5.markdown(f"{badge_html} ({int(prior_ed)} visits)", unsafe_allow_html=True)
        
        # Column 6: Action Button
        with r_col6:
            if st.button("View Details", key=f"view_{p['patient_id']}", use_container_width=True):
                st.session_state["selected_patient_id"] = p['patient_id']
                st.session_state.page = "patient_profile"
                st.rerun()
                
        st.markdown("</div>", unsafe_allow_html=True)
