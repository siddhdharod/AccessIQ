import streamlit as st
import pandas as pd
from utils.helpers import init_session_state, inject_custom_css, load_dataset
from utils.pdf_generator import generate_accessibility_pdf_report
from utils.gemini_helper import generate_pdf_summary, get_accessibility_suggestions
from utils.weather_helper import fetch_weather_data
from utils.prediction import score_to_category, score_to_priority
from components.navbar import render_navbar
from components.sidebar import render_sidebar
from components.cards import get_badge_html, get_priority_badge_html
from components.footer import render_footer
from components.chatbot_widget import render_chatbot_widget

st.set_page_config(page_title="Report Generator - AccessIQ", page_icon="📄", layout="wide")
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
        <h2 style="margin: 0; font-size: 1.8rem; font-weight: 800;">📄 Official Urban Accessibility Report Generator</h2>
        <p style="color: var(--text-muted); font-size: 0.9rem; margin-top: 0.2rem;">
            Select an audited public venue to preview and export an official PDF evaluation document featuring AI insights and environmental risk analysis.
        </p>
    </div>
</div>
""", unsafe_allow_html=True)

if df.empty:
    st.error("No dataset available to generate report.")
else:
    available_locs = df["Location_Name"].dropna().unique().tolist()
    selected_venue_name = st.selectbox("Select Public Venue / Location for Audit Report", available_locs, index=0)

    # Fetch venue details safely
    venue_rows = df[df["Location_Name"] == selected_venue_name]
    venue = venue_rows.iloc[0] if not venue_rows.empty else df.iloc[0]

    city = str(venue.get("City", "Urban Region"))
    score = float(venue.get("Accessibility_Score", venue.get("Predicted_Accessibility", 65.0)))
    category = str(venue.get("Accessibility_Category", score_to_category(score)))
    priority = str(venue.get("Improvement_Priority", score_to_priority(score)))

    # Fetch live weather context safely
    try:
        lat = float(venue.get("Latitude", 28.6139))
        lon = float(venue.get("Longitude", 77.2090))
    except Exception:
        lat, lon = 28.6139, 77.2090
        
    weather_res = fetch_weather_data(lat, lon, city)
    weather_text = f"Live Weather ({city}): {weather_res.get('temp', 25.0)}°C, {weather_res.get('description', 'Clear')}." if weather_res.get("available") else "Standard local climate conditions."

    # Gemini AI executive summary & suggestions
    missing_feats = [f for f in ["Ramp_Available", "Elevator_Available", "Braille_Signage", "Tactile_Path"] if venue.get(f, 0) == 0]
    ai_suggestions = get_accessibility_suggestions(selected_venue_name, score, category, missing_feats)
    ai_exec_summary = generate_pdf_summary(selected_venue_name, score, category, city)

    # Report Preview Card
    st.markdown("""
    <div class="section-header">
        <span>🔍 Live PDF Report Executive Preview</span>
        <div class="section-header-line"></div>
    </div>
    """, unsafe_allow_html=True)

    p_col1, p_col2 = st.columns([1.2, 1.8])

    with p_col1:
        st.markdown(f"""
        <div class="glass-card">
            <h3 style="margin-top:0; color: var(--text-primary);">{selected_venue_name}</h3>
            <div style="color: var(--text-muted); font-size: 0.85rem; margin-bottom: 0.5rem;">Region: {city}</div>
            <div style="font-size: 3rem; font-weight: 800; color: var(--primary); margin: 0.5rem 0;">
                {score:.1f}<span style="font-size: 1.2rem; color: var(--text-muted);">/100</span>
            </div>
            <div style="margin-bottom: 1rem;">
                {get_badge_html(category)} &nbsp; {get_priority_badge_html(priority)}
            </div>
            <hr style="border-color: var(--card-border);">
            <div style="font-size: 0.85rem; color: var(--text-secondary); line-height: 1.8;">
                <div><b>Ramp Facility:</b> {"✅ Available" if venue.get("Ramp_Available", 0)==1 else "❌ Missing"}</div>
                <div><b>Elevator Access:</b> {"✅ Available" if venue.get("Elevator_Available", 0)==1 else "❌ Missing"}</div>
                <div><b>Braille Signage:</b> {"✅ Available" if venue.get("Braille_Signage", 0)==1 else "❌ Missing"}</div>
                <div><b>Tactile Path:</b> {"✅ Available" if venue.get("Tactile_Path", 0)==1 else "❌ Missing"}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with p_col2:
        st.markdown(f"""
        <div class="glass-card" style="height: 100%;">
            <h4 style="color: var(--text-primary); margin-top: 0;">🤖 Executive AI Report Summary</h4>
            <p style="font-size: 0.9rem; color: var(--text-body); line-height: 1.6;">{ai_exec_summary}</p>
            <hr style="border-color: var(--card-border); margin: 1rem 0;">
            <h4 style="color: var(--text-primary);">💡 Recommended Infrastructure Action Plan</h4>
            <p style="font-size: 0.88rem; color: var(--text-body); line-height: 1.55;">{ai_suggestions}</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Generate PDF raw bytes
    features_dict = venue.to_dict()
    pdf_bytes = generate_accessibility_pdf_report(
        location_name=selected_venue_name,
        score=score,
        category=category,
        priority=priority,
        city=city,
        features_dict=features_dict,
        ai_suggestions=f"{ai_exec_summary}\n\nRecommendations:\n{ai_suggestions}",
        weather_info=weather_text
    )

    # Download Button
    st.download_button(
        label=f"📥 Download Official PDF Audit Report for {selected_venue_name}",
        data=pdf_bytes,
        file_name=f"AccessIQ_Audit_Report_{selected_venue_name.replace(' ', '_')}.pdf",
        mime="application/pdf",
        use_container_width=True
    )

render_footer()
