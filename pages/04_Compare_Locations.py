import streamlit as st
import pandas as pd
from utils.helpers import init_session_state, inject_custom_css, load_dataset
from utils.charts import create_radar_comparison
from utils.prediction import score_to_category, score_to_priority
from components.navbar import render_navbar
from components.sidebar import render_sidebar
from components.cards import get_badge_html, get_priority_badge_html
from components.footer import render_footer
from components.chatbot_widget import render_chatbot_widget

st.set_page_config(page_title="Compare Locations - AccessIQ", page_icon="⚔️", layout="wide")
init_session_state()
inject_custom_css()

render_navbar()
df = load_dataset()
cities = df["City"].dropna().unique().tolist() if not df.empty and "City" in df.columns else []
controls = render_sidebar(cities)

# Render Floating AI Assistant Chatbot
render_chatbot_widget(controls["persona"])

st.markdown("""
<div class="page-transition">
    <div style="margin-bottom: 1.5rem;">
        <h2 style="margin: 0; font-size: 1.8rem; font-weight: 800;">⚔️ Multi-Location Accessibility Comparison</h2>
        <p style="color: var(--text-muted); font-size: 0.9rem; margin-top: 0.2rem;">
            Select multiple audited venues side-by-side to evaluate infrastructure, safety, crowd metrics, and improvement priorities.
        </p>
    </div>
</div>
""", unsafe_allow_html=True)

if df.empty:
    st.error("No dataset available to compare locations.")
else:
    # Location Multi-Select dropdown
    available_locations = df["Location_Name"].dropna().unique().tolist()
    default_selections = available_locations[:3] if len(available_locations) >= 3 else available_locations

    selected_locs = st.multiselect(
        "Select Locations to Compare (Pick 2 or more)",
        options=available_locations,
        default=default_selections
    )

    if len(selected_locs) < 2:
        st.warning("Please select at least 2 locations from the dropdown above to render the side-by-side comparison matrix.")
    else:
        compared_df = df[df["Location_Name"].isin(selected_locs)].copy()

        # Compute missing comparison metrics if needed
        if "Infrastructure_Score" not in compared_df.columns:
            infra_cols = ["Ramp_Available", "Elevator_Available", "Wheelchair_Entrance", "Accessible_Washroom", "Reserved_Parking"]
            compared_df["Infrastructure_Score"] = compared_df[[c for c in infra_cols if c in compared_df.columns]].sum(axis=1)

        if "Safety_Index" not in compared_df.columns:
            safe_cols = ["Lighting", "Safety_Level", "CCTV_Available"]
            compared_df["Safety_Index"] = compared_df[[c for c in safe_cols if c in compared_df.columns]].sum(axis=1)

        if "Facility_Score" not in compared_df.columns:
            fac_cols = ["Braille_Signage", "Audio_Announcements", "Tactile_Path"]
            compared_df["Facility_Score"] = compared_df[[c for c in fac_cols if c in compared_df.columns]].sum(axis=1)

        if "Accessibility_Support_Score" not in compared_df.columns:
            supp_cols = ["Staff_Trained_Accessibility", "Multilingual_Signage"]
            compared_df["Accessibility_Support_Score"] = compared_df[[c for c in supp_cols if c in compared_df.columns]].sum(axis=1)

        st.markdown("""
        <div class="section-header">
            <span>🕸️ Multi-Location Accessibility Radar Breakdown</span>
            <div class="section-header-line"></div>
        </div>
        """, unsafe_allow_html=True)
        
        fig_radar = create_radar_comparison(compared_df)
        st.plotly_chart(fig_radar, use_container_width=True)

        st.markdown("""
        <div class="section-header">
            <span>📊 Side-by-Side Comprehensive Comparison Matrix</span>
            <div class="section-header-line"></div>
        </div>
        """, unsafe_allow_html=True)

        # Render venue cards in chunked grid (max 3 cards per row for clean alignment)
        rows_list = [compared_df.iloc[i:i+3] for i in range(0, len(compared_df), 3)]
        
        for row_df in rows_list:
            cols = st.columns(len(row_df))
            for i, (idx, row) in enumerate(row_df.iterrows()):
                with cols[i]:
                    loc_name = str(row.get("Location_Name", "Venue"))
                    city = str(row.get("City", "Urban Region"))
                    score = float(row.get("Accessibility_Score", 65.0))
                    category = str(row.get("Accessibility_Category", score_to_category(score)))
                    priority = str(row.get("Improvement_Priority", score_to_priority(score)))

                    ramp_status = "✅ Yes" if row.get("Ramp_Available", 0) == 1 else "❌ No"
                    elevator_status = "✅ Yes" if row.get("Elevator_Available", 0) == 1 else "❌ No"
                    washroom_status = "✅ Yes" if row.get("Accessible_Washroom", 0) == 1 else "❌ No"
                    braille_status = "✅ Yes" if row.get("Braille_Signage", 0) == 1 else "❌ No"
                    tactile_status = "✅ Yes" if row.get("Tactile_Path", 0) == 1 else "❌ No"

                    safety_score = row.get("Safety_Index", 4)
                    waiting_time = row.get("Average_Waiting_Time", 15.0)

                    b_html = get_badge_html(category)
                    p_html = get_priority_badge_html(priority)

                    st.markdown(f"""
                    <div class="glass-card" style="margin-bottom: 1rem;">
                        <h3 style="margin-top:0; color: var(--text-primary);">{loc_name}</h3>
                        <div style="color: var(--text-muted); font-size: 0.85rem; margin-bottom: 0.5rem;">{city}</div>
                        <div style="font-size: 2.2rem; font-weight: 800; color: var(--primary);">{score:.1f}<span style="font-size: 1rem; color: var(--text-muted);">/100</span></div>
                        <div style="margin-bottom: 1rem;">{b_html}</div>
                        <hr style="border-color: var(--card-border);">
                        <div style="font-size: 0.85rem; line-height: 1.8; color: var(--text-body);">
                            <div><b>Priority:</b> {p_html}</div>
                            <div><b>Ramp Access:</b> {ramp_status}</div>
                            <div><b>Elevator Access:</b> {elevator_status}</div>
                            <div><b>Accessible Washroom:</b> {washroom_status}</div>
                            <div><b>Braille Signage:</b> {braille_status}</div>
                            <div><b>Tactile Path:</b> {tactile_status}</div>
                            <div><b>Safety Index:</b> {safety_score}/6</div>
                            <div><b>Crowd Waiting:</b> {waiting_time} mins</div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # Tabular Export View
        st.markdown("""
        <div class="section-header">
            <span>📋 Comparative Data Matrix Table</span>
            <div class="section-header-line"></div>
        </div>
        """, unsafe_allow_html=True)
        
        table_cols = [c for c in [
            "Location_Name", "City", "Accessibility_Score", "Accessibility_Category",
            "Improvement_Priority", "Infrastructure_Score", "Safety_Index",
            "Average_Waiting_Time", "Accessibility_Complaints", "User_Rating"
        ] if c in compared_df.columns]

        st.dataframe(compared_df[table_cols], use_container_width=True)

render_footer()
