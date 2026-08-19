import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
try:
    from carenavigator.database import get_dashboard_kpis, get_ed_avoidability_counts, get_all_patients_df
except ImportError:
    from database import get_dashboard_kpis, get_ed_avoidability_counts, get_all_patients_df

def render_dashboard():
    # Retrieve data
    kpis = get_dashboard_kpis()
    avoidability = get_ed_avoidability_counts()
    
    user_name = st.session_state.get("user_name", "Care Manager")
    
    # Custom Header Styling
    st.markdown(f"""
        <div class='welcome-banner'>
            <h2>Good Day, {user_name} 👋</h2>
            <p>Here's your care management overview for today.</p>
        </div>
    """, unsafe_allow_html=True)
    
    st.write("") # Spacing
    
    # 4 Separate KPI Cards in separate columns
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
            <div class='kpi-card'>
                <div class='kpi-title'>Total Patients</div>
                <div class='kpi-value'>{kpis['total_patients']:,}</div>
                <div class='kpi-footer'>Registered in system</div>
            </div>
        """, unsafe_allow_html=True)
        
    with col2:
        st.markdown(f"""
            <div class='kpi-card'>
                <div class='kpi-title'>Recent ED Visits</div>
                <div class='kpi-value'>{kpis['recent_ed_visits']:,}</div>
                <div class='kpi-footer'>Last 30 days</div>
            </div>
        """, unsafe_allow_html=True)
        
    with col3:
        st.markdown(f"""
            <div class='kpi-card'>
                <div class='kpi-title'>Potentially Avoidable ED</div>
                <div class='kpi-value'>{kpis['avoidable_ed']:,}</div>
                <div class='kpi-footer'>Avoidable class count</div>
            </div>
        """, unsafe_allow_html=True)
        
    with col4:
        st.markdown(f"""
            <div class='kpi-card' style='border-left: 4px solid #E63946;'>
                <div class='kpi-title'>High ED Utilization</div>
                <div class='kpi-value'>{kpis['high_utilization']:,}</div>
                <div class='kpi-footer' style='color:#E63946;'>≥ 5 Prior ED visits</div>
            </div>
        """, unsafe_allow_html=True)
        
    st.write("")
    
    # Main Section: Charts
    chart_col1, chart_col2 = st.columns([1, 1])
    
    with chart_col1:
        st.markdown("<div class='section-card'>", unsafe_allow_html=True)
        st.subheader("ED Utilization")
        
        # Donut Chart for Potentially Avoidable vs Non-Avoidable
        labels = ['Potentially Avoidable', 'Non-Avoidable']
        values = [avoidability['avoidable'], avoidability['non_avoidable']]
        
        # Colors: Healthcare blue and light gray
        colors = ['#1D3557', '#E63946' if avoidability['avoidable'] > avoidability['non_avoidable'] else '#A8DADC']
        
        fig = go.Figure(data=[go.Pie(
            labels=labels,
            values=values,
            hole=.6,
            marker_colors=['#457B9D', '#1D3557'],
            textinfo='percent+label',
            showlegend=False
        )])
        
        # Total in the center
        fig.update_layout(
            annotations=[dict(text=f"Total ED<br>{kpis['recent_ed_visits'] + kpis['avoidable_ed']}", x=0.5, y=0.5, font_size=16, showarrow=False, font_family="inherit")],
            margin=dict(t=20, b=20, l=20, r=20),
            height=300,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)'
        )
        st.plotly_chart(fig, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)
        
    with chart_col2:
        st.markdown("<div class='section-card'>", unsafe_allow_html=True)
        st.subheader("ED Utilization Overview")
        
        # Line chart showing avg visits across: Prior ED, Last 90 Days, Last 30 Days
        df_all = get_all_patients_df()
        avg_prior = df_all['prior_ed_visits'].mean()
        avg_90d = df_all['ed_visits_last_90_days'].mean()
        avg_30d = df_all['ed_visits_last_30_days'].mean()
        
        trend_data = pd.DataFrame({
            "Timeframe": ["Prior ED Visits (Avg)", "ED Visits Last 90 Days (Avg)", "ED Visits Last 30 Days (Avg)"],
            "Average Visits": [avg_prior, avg_90d, avg_30d]
        })
        
        fig_trend = px.line(
            trend_data, 
            x="Timeframe", 
            y="Average Visits",
            markers=True,
            color_discrete_sequence=['#457B9D']
        )
        
        fig_trend.update_layout(
            margin=dict(t=20, b=20, l=20, r=20),
            height=300,
            xaxis_title="",
            yaxis_title="Avg Visits Per Patient",
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            yaxis=dict(gridcolor='#F1F1F1')
        )
        st.plotly_chart(fig_trend, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)
        
    # Navigation to Patient Worklist
    st.write("")
    nav_col1, nav_col2 = st.columns([4, 1])
    with nav_col2:
        if st.button("View Patient Worklist →", use_container_width=True):
            st.session_state.page = "patients"
            st.rerun()