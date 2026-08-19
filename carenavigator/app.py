# ============================================================
# UC07 — CARENAVIGATOR MAIN STREAMLIT APPLICATION
# ============================================================

import sys
from pathlib import Path

# Setup project paths for imports
BASE_DIR = Path(__file__).resolve().parents[1]
CARENAVIGATOR_DIR = Path(__file__).resolve().parent

if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

if str(CARENAVIGATOR_DIR) not in sys.path:
    sys.path.insert(0, str(CARENAVIGATOR_DIR))

import streamlit as st

# ============================================================
# 1. PAGE CONFIGURATION (MUST BE FIRST STREAMLIT COMMAND)
# ============================================================

st.set_page_config(
    page_title="CareNavigator - ED Avoidability",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================
# 2. IMPORTS AFTER PAGE CONFIG
# ============================================================

try:
    from carenavigator.auth import authenticate_user, register_user
    from carenavigator.dashboard import render_dashboard
    from carenavigator.patients import render_patients
    from carenavigator.patient_detail import render_patient_detail
    from carenavigator.encounter import render_encounter
    from carenavigator.analysis import render_analytics
except ImportError:
    from auth import authenticate_user, register_user
    from dashboard import render_dashboard
    from patients import render_patients
    from patient_detail import render_patient_detail
    from encounter import render_encounter
    from analysis import render_analytics


# ============================================================
# 3. GLOBAL CUSTOM STYLING
# ============================================================

st.markdown("""
    <style>
    /* Global Base Styling */
    .stApp {
        background-color: #F8F9FA;
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    }
    
    /* Welcome Banner */
    .welcome-banner {
        background: linear-gradient(135deg, #1D3557 0%, #457B9D 100%);
        color: white;
        padding: 1.5rem 2rem;
        border-radius: 12px;
        margin-bottom: 1.5rem;
        box-shadow: 0 4px 12px rgba(29, 53, 87, 0.15);
    }
    .welcome-banner h2 {
        color: white !important;
        margin: 0 0 0.4rem 0 !important;
        font-weight: 700;
    }
    .welcome-banner p {
        color: #E0FBFC !important;
        margin: 0 !important;
        font-size: 1rem;
    }

    /* KPI Cards */
    .kpi-card {
        background-color: #FFFFFF;
        border-radius: 10px;
        padding: 1.2rem;
        border: 1px solid #E9ECEF;
        border-left: 4px solid #457B9D;
        box-shadow: 0 2px 6px rgba(0,0,0,0.04);
    }
    .kpi-title {
        font-size: 0.85rem;
        font-weight: 600;
        color: #6C757D;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .kpi-value {
        font-size: 1.8rem;
        font-weight: 700;
        color: #1D3557;
        margin: 0.3rem 0;
    }
    .kpi-footer {
        font-size: 0.8rem;
        color: #6C757D;
    }

    /* Section Cards */
    .section-card {
        background-color: #FFFFFF;
        border-radius: 10px;
        padding: 1.5rem;
        border: 1px solid #E9ECEF;
        box-shadow: 0 2px 6px rgba(0,0,0,0.03);
        margin-bottom: 1rem;
    }

    /* Table Row Styling */
    .table-header {
        background-color: #E9ECEF;
        padding: 0.75rem 1rem;
        border-radius: 6px;
        font-weight: 600;
        color: #1D3557;
        margin-bottom: 0.5rem;
    }
    .table-row {
        background-color: #FFFFFF;
        padding: 0.75rem 1rem;
        border-radius: 6px;
        border: 1px solid #E9ECEF;
        margin-bottom: 0.4rem;
        display: flex;
        align-items: center;
    }

    /* Badges */
    .badge {
        padding: 0.25rem 0.6rem;
        border-radius: 20px;
        font-size: 0.78rem;
        font-weight: 600;
        display: inline-block;
    }
    .badge-red { background-color: #FFD8D8; color: #900C3F; }
    .badge-orange { background-color: #FFE5D9; color: #D35400; }
    .badge-yellow { background-color: #FFF3CD; color: #856404; }

    /* Detail Tables */
    .detail-table {
        width: 100%;
        border-collapse: collapse;
    }
    .detail-table th, .detail-table td {
        padding: 0.6rem 0.8rem;
        text-align: left;
        border-bottom: 1px solid #F1F1F1;
    }
    .detail-table th {
        color: #6C757D;
        font-weight: 600;
        width: 45%;
    }
    </style>
""", unsafe_allow_html=True)


# ============================================================
# 4. SESSION STATE INITIALIZATION
# ============================================================

if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

if "user_id" not in st.session_state:
    st.session_state["user_id"] = ""

if "user_name" not in st.session_state:
    st.session_state["user_name"] = ""

if "user_role" not in st.session_state:
    st.session_state["user_role"] = ""

if "page" not in st.session_state:
    st.session_state["page"] = "dashboard"

if "selected_patient_id" not in st.session_state:
    st.session_state["selected_patient_id"] = None


# ============================================================
# 5. LOGIN & REGISTRATION PAGE
# ============================================================

def render_login_page():
    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        st.markdown("<div class='section-card' style='margin-top: 3rem;'>", unsafe_allow_html=True)
        st.title("🏥 CareNavigator")
        st.markdown("### Avoidability Emergency Department Utilisation")
        st.caption("AI-assisted clinical decision support for Care Managers")
        st.divider()

        tab_login, tab_register = st.tabs(["🔐 Login", "📝 Register"])

        # ----------------------------------------------------
        # LOGIN TAB
        # ----------------------------------------------------
        with tab_login:
            st.write("")
            with st.form("login_form"):
                user_id = st.text_input("User ID", value="CM001", placeholder="e.g. CM001")
                password = st.text_input("Password", value="password123", type="password")
                submit_login = st.form_submit_button("Login", type="primary", use_container_width=True)

                if submit_login:
                    user = authenticate_user(user_id.strip(), password.strip())
                    if user:
                        st.session_state["authenticated"] = True
                        st.session_state["user_id"] = user["user_id"]
                        st.session_state["user_name"] = user.get("name", "Care Manager")
                        st.session_state["user_role"] = user.get("role", "Care Manager")
                        st.session_state["page"] = "dashboard"
                        st.success(f"Welcome back, {user.get('name', 'User')}!")
                        st.rerun()
                    else:
                        st.error("Invalid User ID or Password. Default login is CM001 / password123")

        # ----------------------------------------------------
        # REGISTER TAB
        # ----------------------------------------------------
        with tab_register:
            st.write("")
            with st.form("register_form"):
                reg_id = st.text_input("New User ID", placeholder="e.g. CM002")
                reg_name = st.text_input("Full Name", placeholder="e.g. Dr. Jane Doe")
                reg_password = st.text_input("New Password", type="password")
                reg_role = st.selectbox("Role", ["Care Manager", "Clinical Analyst", "ED Administrator"])
                submit_reg = st.form_submit_button("Register Account", use_container_width=True)

                if submit_reg:
                    if not reg_id or not reg_name or not reg_password:
                        st.warning("Please fill in all registration fields.")
                    else:
                        success = register_user(reg_id.strip(), reg_name.strip(), reg_password.strip(), reg_role)
                        if success:
                            st.success("Account registered successfully! You can now log in.")
                        else:
                            st.error("User ID already exists. Please choose a different ID.")

        st.markdown("</div>", unsafe_allow_html=True)


# ============================================================
# 6. MAIN ROUTER & SIDEBAR NAVIGATION
# ============================================================

def main():
    # Render Login Page if not authenticated
    if not st.session_state["authenticated"]:
        render_login_page()
        return

    # --------------------------------------------------------
    # SIDEBAR NAVIGATION
    # --------------------------------------------------------
    with st.sidebar:
        st.markdown("## 🏥 CareNavigator")
        st.caption("ED Avoidability Platform")

        st.markdown(f"""
            <div style='background-color:#E9ECEF; padding:0.75rem 1rem; border-radius:8px; margin-bottom:1rem;'>
                <span style='font-size:0.8rem; color:#6C757D; font-weight:600;'>LOGGED IN AS</span><br/>
                <strong style='color:#1D3557;'>{st.session_state["user_name"]}</strong><br/>
                <span style='font-size:0.8rem; color:#457B9D;'>{st.session_state["user_role"]}</span>
            </div>
        """, unsafe_allow_html=True)

        st.divider()

        # Page Mapping
        page_options = {
            "📊 Dashboard": "dashboard",
            "👥 Patients": "patients",
            "🩺 Encounter Analysis": "encounter",
            "📈 Analytics": "analytics"
        }

        if st.session_state.get("selected_patient_id"):
            page_options["📋 Patient Details"] = "patient_detail"

        # Determine current selection index
        current_page = st.session_state.get("page", "dashboard")
        if current_page in ["patient_profile", "patient_detail"]:
            current_page = "patient_detail"
        elif current_page in ["new_encounter", "encounter"]:
            current_page = "encounter"

        labels = list(page_options.keys())
        values = list(page_options.values())

        selected_index = values.index(current_page) if current_page in values else 0

        nav_choice = st.radio("Navigation", options=labels, index=selected_index)

        # Update page if user manually changes radio selection
        chosen_page_value = page_options[nav_choice]
        if chosen_page_value != st.session_state["page"]:
            st.session_state["page"] = chosen_page_value
            st.rerun()

        st.divider()

        # Logout Button
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state["authenticated"] = False
            st.session_state["user_id"] = ""
            st.session_state["user_name"] = ""
            st.session_state["selected_patient_id"] = None
            st.session_state["page"] = "dashboard"
            st.rerun()

    # --------------------------------------------------------
    # PAGE ROUTING
    # --------------------------------------------------------
    page = st.session_state.get("page", "dashboard")

    if page == "dashboard":
        render_dashboard()
    elif page == "patients":
        render_patients()
    elif page in ["patient_detail", "patient_profile"]:
        render_patient_detail()
    elif page in ["encounter", "new_encounter"]:
        render_encounter()
    elif page == "analytics":
        render_analytics()
    else:
        render_dashboard()


if __name__ == "__main__":
    main()