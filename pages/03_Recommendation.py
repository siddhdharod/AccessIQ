import streamlit as st
import pandas as pd
from utils.helpers import init_session_state, inject_custom_css, load_dataset, PERSONAS
from utils.recommendation import get_recommendations
from utils.map_utils import render_accessibility_map
from components.navbar import render_navbar
from components.sidebar import render_sidebar
from components.cards import render_recommendation_card
from components.footer import render_footer
from components.chatbot_widget import render_chatbot_widget

st.set_page_config(page_title="Recommendations - AccessIQ", page_icon="🎯", layout="wide")
init_session_state()
inject_custom_css()

render_navbar()
df = load_dataset()
cities = df["City"].dropna().unique().tolist() if not df.empty and "City" in df.columns else []
controls = render_sidebar(cities)

# Persona & Filter Selector Bar
col_p, col_c, col_r = st.columns([1.5, 1, 1])

with col_p:
    persona_choice = st.selectbox(
        "Select User Persona",
        list(PERSONAS.keys()),
        index=list(PERSONAS.keys()).index(st.session_state.get("selected_persona", "Wheelchair User"))
    )
    st.session_state["selected_persona"] = persona_choice

with col_c:
    city_choice = st.selectbox("Select City", ["All"] + sorted([str(c) for c in cities if pd.notna(c)]), index=0)

with col_r:
    top_n = st.slider("Top Recommendations Count", 3, 10, 5)

# Render Floating AI Assistant Chatbot
render_chatbot_widget(persona_choice)

p_spec = PERSONAS[persona_choice]

st.markdown(f"""
<div class="page-transition">
    <div style="margin-bottom: 1rem;">
        <h2 style="margin: 0; font-size: 1.8rem; font-weight: 800;">🎯 Persona-Based Location Recommendation Engine</h2>
        <p style="color: var(--text-muted); font-size: 0.9rem; margin-top: 0.2rem;">
            Discover top accessible venues weighted specifically for {persona_choice} mobility requirements.
        </p>
    </div>
</div>
""", unsafe_allow_html=True)

st.info(f"{p_spec['icon']} **Active Mobility Persona:** {persona_choice} — _{p_spec['description']}_")

# Compute Top Recommendations
recommendations_df = get_recommendations(
    df=df,
    persona=persona_choice,
    city=city_choice,
    top_n=top_n
)

if recommendations_df.empty:
    st.warning("No recommendations available for the selected criteria.")
else:
    st.markdown(f"""
    <div class="section-header">
        <span>🏆 Top {len(recommendations_df)} Recommended Venues for {p_spec['icon']} {persona_choice}</span>
        <div class="section-header-line"></div>
    </div>
    """, unsafe_allow_html=True)

    col_cards, col_map = st.columns([1.3, 1.2])

    with col_cards:
        for idx, row in recommendations_df.iterrows():
            render_recommendation_card(
                location_name=str(row.get("Location_Name", f"Venue {idx}")),
                city=str(row.get("City", "Urban Center")),
                score=float(row.get("Persona_Score", 75.0)),
                category=str(row.get("Category", "Good")),
                reason=str(row.get("Recommendation_Reason", "High accessibility compatibility")),
                priority=str(row.get("Priority", "Low")),
                distance_km=row.get("Distance_km")
            )

    with col_map:
        st.markdown("""
        <div style="font-size: 1.1rem; font-weight: 700; color: var(--text-primary); margin-bottom: 0.6rem;">🗺️ Recommended Spatial Venues Map</div>
        """, unsafe_allow_html=True)
        render_accessibility_map(
            recommendations_df,
            zoom=12 if city_choice != "All" else 5,
            show_hotspots=False,
            height=580
        )

render_footer()
