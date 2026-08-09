import streamlit as st
import pandas as pd
import plotly.express as px
from utils.helpers import init_session_state, inject_custom_css, load_dataset
from utils.weather_helper import render_weather_widget
from utils.map_utils import render_accessibility_map
from utils.gemini_helper import get_accessibility_suggestions
from utils.charts import apply_custom_chart_style, get_theme_colors
from components.navbar import render_navbar
from components.sidebar import render_sidebar
from components.metrics import render_metrics_summary
from components.cards import get_badge_html
from components.footer import render_footer
from components.chatbot_widget import render_chatbot_widget

st.set_page_config(page_title="Dashboard - AccessIQ", page_icon="📊", layout="wide")
init_session_state()
inject_custom_css()

render_navbar()
df = load_dataset()
cities = df["City"].dropna().unique().tolist() if not df.empty and "City" in df.columns else []
controls = render_sidebar(cities)

persona = controls["persona"]
selected_city = controls["city"]

# Render Floating AI Assistant Chatbot
render_chatbot_widget(persona)

st.markdown("""
<div class="page-transition">
    <div style="margin-bottom: 1.5rem;">
        <h2 style="margin: 0; font-size: 1.8rem; font-weight: 800;">📊 Real-Time Urban Accessibility Dashboard</h2>
        <p style="color: var(--text-muted); font-size: 0.9rem; margin-top: 0.2rem;">
            Live spatial metrics, OpenWeather persona risk analysis, AI suggestions, and categorical audit breakdowns.
        </p>
    </div>
</div>
""", unsafe_allow_html=True)

# Filter DataFrame by city selection
filtered_df = df.copy()
if selected_city != "All" and "City" in filtered_df.columns:
    filtered_df = filtered_df[filtered_df["City"].astype(str) == str(selected_city)]

# Metrics Summary KPI Cards
render_metrics_summary(filtered_df)

st.markdown("<br>", unsafe_allow_html=True)

# Main Grid: Weather Widget + Live Map
col_map, col_weather = st.columns([2.2, 1])

with col_weather:
    st.markdown("""
    <div class="section-header" style="margin-top: 0;">
        <span>🌤️ Environmental Risk Radar</span>
    </div>
    """, unsafe_allow_html=True)
    
    lat_center = float(filtered_df["Latitude"].mean()) if not filtered_df.empty and "Latitude" in filtered_df.columns else 28.6139
    lon_center = float(filtered_df["Longitude"].mean()) if not filtered_df.empty and "Longitude" in filtered_df.columns else 77.2090
    
    render_weather_widget(
        lat=lat_center,
        lon=lon_center,
        city=selected_city if selected_city != "All" else None,
        persona=persona
    )

    st.markdown("""
    <div class="section-header" style="margin-top: 1rem;">
        <span>💡 AI Infrastructure Insight</span>
    </div>
    """, unsafe_allow_html=True)
    
    if not filtered_df.empty:
        sample_row = filtered_df.iloc[0]
        missing = [f for f in ["Ramp_Available", "Elevator_Available", "Braille_Signage", "Tactile_Path"] if sample_row.get(f, 0) == 0]
        ai_suggestion = get_accessibility_suggestions(
            location_name=str(sample_row.get("Location_Name", "Urban Center")),
            score=float(sample_row.get("Accessibility_Score", 65.0)),
            category=str(sample_row.get("Accessibility_Category", "Good")),
            missing_features=missing
        )
        st.markdown(f"""
        <div class="glass-card" style="font-size: 0.88rem; line-height: 1.55;">
            {ai_suggestion}
        </div>
        """, unsafe_allow_html=True)

with col_map:
    st.markdown("""
    <div class="section-header" style="margin-top: 0;">
        <span>🗺️ Interactive Spatial Accessibility Map</span>
    </div>
    """, unsafe_allow_html=True)
    show_hotspots = st.checkbox("Show Complaint Hotspots", value=True, key="dashboard_hotspot_toggle")
    render_accessibility_map(
        filtered_df,
        zoom=11 if selected_city != "All" else 5,
        show_hotspots=show_hotspots,
        height=520
    )

st.markdown("<br>", unsafe_allow_html=True)

# Charts Section: Distribution & Category breakdown
c1, c2 = st.columns(2)

theme_palette = get_theme_colors()

with c1:
    st.markdown("""
    <div class="section-header" style="margin-top: 0;">
        <span>📈 Score Distribution Histogram</span>
    </div>
    """, unsafe_allow_html=True)
    if not filtered_df.empty and "Accessibility_Score" in filtered_df.columns:
        fig_hist = px.histogram(
            filtered_df,
            x="Accessibility_Score",
            nbins=20,
            color="Accessibility_Category" if "Accessibility_Category" in filtered_df.columns else None,
            color_discrete_sequence=theme_palette["colors"]
        )
        apply_custom_chart_style(fig_hist, "Distribution of Accessibility Scores across Venues")
        st.plotly_chart(fig_hist, use_container_width=True)

with c2:
    st.markdown("""
    <div class="section-header" style="margin-top: 0;">
        <span>🥧 Categorical Classification Breakdown</span>
    </div>
    """, unsafe_allow_html=True)
    if not filtered_df.empty and "Accessibility_Category" in filtered_df.columns:
        cat_counts = filtered_df["Accessibility_Category"].value_counts().reset_index()
        cat_counts.columns = ["Category", "Count"]
        fig_pie = px.pie(
            cat_counts,
            names="Category",
            values="Count",
            color_discrete_sequence=theme_palette["colors"],
            hole=0.45
        )
        apply_custom_chart_style(fig_pie, "Percentage Breakdown by Accessibility Tier")
        st.plotly_chart(fig_pie, use_container_width=True)

# Top 10 Audited Venues Table
st.markdown("""
<div class="section-header">
    <span>📋 Top Audited Urban Locations</span>
    <div class="section-header-line"></div>
</div>
""", unsafe_allow_html=True)

if not filtered_df.empty:
    display_cols = [c for c in ["Location_Name", "City", "Accessibility_Score", "Accessibility_Category", "Improvement_Priority", "Accessibility_Complaints"] if c in filtered_df.columns]
    st.dataframe(
        filtered_df[display_cols].head(10),
        use_container_width=True
    )

render_footer()
