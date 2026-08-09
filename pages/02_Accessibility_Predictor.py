import streamlit as st
import pandas as pd
from utils.helpers import init_session_state, inject_custom_css, load_dataset
from utils.prediction import predict_accessibility
from utils.charts import create_single_radar
from utils.gemini_helper import explain_prediction_result, get_accessibility_suggestions
from utils.pdf_generator import generate_accessibility_pdf_report
from components.navbar import render_navbar
from components.sidebar import render_sidebar
from components.cards import get_badge_html, get_priority_badge_html
from components.footer import render_footer
from components.chatbot_widget import render_chatbot_widget
from utils.booking_manager import get_realtime_counts_for_location

st.set_page_config(page_title="Predictor - AccessIQ", page_icon="🔮", layout="wide")
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
        <h2 style="margin: 0; font-size: 1.8rem; font-weight: 800;">🔮 Accessibility Score Predictor Engine</h2>
        <p style="color: var(--text-muted); font-size: 0.9rem; margin-top: 0.2rem;">
            Input public venue infrastructure parameters below to predict overall Accessibility Score, Classification, and generate official audit PDFs.
        </p>
    </div>
</div>
""", unsafe_allow_html=True)

# Input Form in glassmorphic card layout
with st.form("prediction_form"):
    st.markdown("""
    <div style="font-size: 1.1rem; font-weight: 700; color: var(--text-primary); margin-bottom: 0.8rem;">🏢 Venue & Spatial Location Parameters</div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        location_name = st.text_input("Venue / Building Name", "Central Metro Station")
        city_name = st.selectbox("City", ["Mumbai", "Delhi", "Bengaluru", "Hyderabad", "Kolkata", "Chennai", "Pune"], index=0)
        building_age = st.number_input("Building Age (Years)", min_value=1, max_value=200, value=15)
        
    with col2:
        latitude = st.number_input("Latitude", value=19.0760, format="%.6f")
        longitude = st.number_input("Longitude", value=72.8777, format="%.6f")
        floors = st.number_input("Number of Floors", min_value=1, max_value=100, value=3)

    with col3:
        user_rating = st.slider("User Rating (1-5)", 1.0, 5.0, 4.0, 0.1)
        maps_rating = st.slider("Google Maps Rating (1-5)", 1.0, 5.0, 3.8, 0.1)
        daily_footfall = st.number_input("Daily Footfall", value=2500)

    st.markdown("<hr style='border-color: var(--card-border); margin: 1.2rem 0;'>", unsafe_allow_html=True)
    st.markdown("""
    <div style="font-size: 1.1rem; font-weight: 700; color: var(--text-primary); margin-bottom: 0.8rem;">♿ Core Physical & Sensory Accessibility Facilities</div>
    """, unsafe_allow_html=True)
    
    c_a, c_b, c_c, c_d = st.columns(4)

    with c_a:
        ramp = st.checkbox("Ramp Available", value=True)
        elevator = st.checkbox("Elevator Available", value=True)
        wheelchair_entry = st.checkbox("Wheelchair Entrance", value=True)

    with c_b:
        braille = st.checkbox("Braille Signage", value=False)
        audio = st.checkbox("Audio Announcements", value=True)
        washroom = st.checkbox("Accessible Washroom", value=True)

    with c_c:
        tactile = st.checkbox("Tactile Paving Path", value=False)
        parking = st.checkbox("Reserved Disabled Parking", value=True)
        trained_staff = st.checkbox("Staff Trained in Accessibility", value=True)

    with c_d:
        door_width = st.slider("Door Width (cm)", 50, 150, 95)
        footpath = st.slider("Footpath Condition (0-2)", 0, 2, 1)
        lighting = st.slider("Lighting Quality (0-2)", 0, 2, 2)

    st.markdown("<hr style='border-color: var(--card-border); margin: 1.2rem 0;'>", unsafe_allow_html=True)
    st.markdown("""
    <div style="font-size: 1.1rem; font-weight: 700; color: var(--text-primary); margin-bottom: 0.8rem;">🛡️ Safety, Crowd & Operational Performance</div>
    """, unsafe_allow_html=True)
    
    s1, s2, s3, s4 = st.columns(4)

    with s1:
        safety_level = st.slider("Safety Level (0-2)", 0, 2, 2)
        cctv = st.checkbox("CCTV Available", value=True)

    with s2:
        crowd_level = st.slider("Crowd Level (0-2)", 0, 2, 1)
        avg_wait = st.number_input("Avg Waiting Time (mins)", value=10.0)

    with s3:
        complaints = st.number_input("Accessibility Complaints Count", value=2)
        complaint_days = st.number_input("Avg Complaint Resolution Days", value=5.0)

    with s4:
        budget = st.number_input("Allocated Budget (Lakh INR)", value=25.0)

    submit_btn = st.form_submit_button("🚀 Execute Predictive Engine Model")

if submit_btn or "last_prediction" in st.session_state:
    input_dict = {
        "Location_Type": 1,
        "City": 1,
        "State": 1,
        "Latitude": latitude,
        "Longitude": longitude,
        "Ownership_Type": 1,
        "Building_Age_Years": building_age,
        "Last_Renovation_Years_Ago": 3.0,
        "Number_of_Floors": floors,
        "Ramp_Available": int(ramp),
        "Elevator_Available": int(elevator),
        "Wheelchair_Entrance": int(wheelchair_entry),
        "Braille_Signage": int(braille),
        "Audio_Announcements": int(audio),
        "Accessible_Washroom": int(washroom),
        "Tactile_Path": int(tactile),
        "Reserved_Parking": int(parking),
        "Door_Width_cm": door_width,
        "Footpath_Condition": footpath,
        "Lighting": lighting,
        "Safety_Level": safety_level,
        "CCTV_Available": int(cctv),
        "Staff_Trained_Accessibility": int(trained_staff),
        "Multilingual_Signage": 1,
        "Public_Transport_Nearby": 1,
        "Parking_Available": int(parking),
        "Crowd_Level": crowd_level,
        "Average_Waiting_Time": avg_wait,
        "Daily_Footfall": daily_footfall,
        "Staff_Count": 15.0,
        "Budget_Allocated_Lakh_INR": budget,
        "Complaint_Resolution_Days": complaint_days,
        "Accessibility_Complaints": complaints,
        "User_Rating": user_rating,
        "Google_Maps_Rating": maps_rating,
        "Last_Inspection_Months": 6.0,
        "Lift_Condition": 2 if elevator else 0,
        "Emergency_Exit_Accessibility": 2
    }

    result = predict_accessibility(input_dict)
    st.session_state["last_prediction"] = (location_name, city_name, result, input_dict)

    score = result["score"]
    category = result["category"]
    priority = result["priority"]

    st.markdown("""
    <div class="section-header">
        <span>📊 Predictive Intelligence Results</span>
        <div class="section-header-line"></div>
    </div>
    """, unsafe_allow_html=True)
    
    res_col1, res_col2 = st.columns([1.2, 1.8])

    with res_col1:
        badge_html = get_badge_html(category)
        p_badge_html = get_priority_badge_html(priority)

        st.markdown(f"""
        <div class="glass-card" style="text-align: center; padding: 2rem;">
            <div style="font-size: 0.78rem; color: var(--text-muted); font-weight: 700; text-transform: uppercase; letter-spacing: 0.1em;">PREDICTED ACCESSIBILITY INDEX</div>
            <div style="font-size: 3.8rem; font-weight: 800; color: var(--primary); margin: 0.5rem 0; line-height: 1;">
                {score:.1f}<span style="font-size: 1.4rem; color: var(--text-muted);">/100</span>
            </div>
            <div style="margin-bottom: 1.2rem;">
                {badge_html} &nbsp; {p_badge_html}
            </div>
            <div style="font-size: 0.85rem; color: var(--text-secondary);">
                Audited Venue: <b style="color: var(--text-primary);">{location_name}</b> ({city_name})
            </div>
        </div>
        """, unsafe_allow_html=True)

        # PDF Download Button
        pdf_bytes = generate_accessibility_pdf_report(
            location_name=location_name,
            score=score,
            category=category,
            priority=priority,
            city=city_name,
            features_dict=input_dict
        )
        st.download_button(
            label="📥 Download Official Audit PDF Report",
            data=pdf_bytes,
            file_name=f"AccessIQ_Audit_{location_name.replace(' ', '_')}.pdf",
            mime="application/pdf",
            use_container_width=True
        )

    with res_col2:
        st.markdown("""
        <div style="font-size: 1.1rem; font-weight: 700; color: var(--text-primary); margin-bottom: 0.5rem;">🕸️ Feature Infrastructure Radar Profile</div>
        """, unsafe_allow_html=True)
        fig_single_radar = create_single_radar(result["features"])
        st.plotly_chart(fig_single_radar, use_container_width=True)

    # Gemini / Groq AI Natural Language Explanation
    st.markdown("""
    <div class="section-header">
        <span>🤖 AI Model Reasoning & Infrastructure Suggestions</span>
        <div class="section-header-line"></div>
    </div>
    """, unsafe_allow_html=True)
    
    key_factors = {
        "Ramp": "Available" if ramp else "Missing",
        "Elevator": "Available" if elevator else "Missing",
        "Braille": "Available" if braille else "Missing",
        "Waiting Time": f"{avg_wait} mins"
    }

    ai_exp = explain_prediction_result(location_name, score, category, key_factors)
    
    missing_list = [k for k, v in [("Ramp", ramp), ("Elevator", elevator), ("Braille", braille), ("Tactile Paving", tactile)] if not v]
    ai_recs = get_accessibility_suggestions(location_name, score, category, missing_list)

    st.markdown(f"""
    <div class="glass-card">
        <h4 style="color: var(--text-primary); margin-top: 0;">🤖 Algorithmic Diagnosis & Model Reasoning</h4>
        <p style="font-size: 0.9rem; color: var(--text-body); line-height: 1.6;">{ai_exp}</p>
        <hr style="border-color: var(--card-border); margin: 1rem 0;">
        <h4 style="color: var(--text-primary);">💡 Priority Actionable Infrastructure Upgrades</h4>
        <p style="font-size: 0.9rem; color: var(--text-body); line-height: 1.6;">{ai_recs}</p>
    </div>
    """, unsafe_allow_html=True)

    # Smart Accessibility Booking Integration Card
    st.markdown("""
    <div class="section-header">
        <span>♿ Real-Time Smart Accessibility Slot Booking</span>
        <div class="section-header-line"></div>
    </div>
    """, unsafe_allow_html=True)

    avail_w, avail_p = get_realtime_counts_for_location(location_name)

    bk_col1, bk_col2, bk_col3 = st.columns([1, 1, 1.2])

    with bk_col1:
        st.markdown(f"""
        <div class="kpi-card" style="text-align: center;">
            <div style="font-size: 2rem;">♿</div>
            <div class="kpi-title">Available Wheelchairs</div>
            <div class="kpi-value" style="color: #22c55e;">{avail_w} <span style="font-size: 1rem; color: var(--text-muted);">/ 20</span></div>
            <div class="kpi-subtitle">Slots W01–W20</div>
        </div>
        """, unsafe_allow_html=True)

    with bk_col2:
        st.markdown(f"""
        <div class="kpi-card" style="text-align: center;">
            <div style="font-size: 2rem;">🅿️</div>
            <div class="kpi-title">Available Parking</div>
            <div class="kpi-value" style="color: #3b82f6;">{avail_p} <span style="font-size: 1rem; color: var(--text-muted);">/ 30</span></div>
            <div class="kpi-subtitle">Slots P01–P30</div>
        </div>
        """, unsafe_allow_html=True)

    with bk_col3:
        st.markdown("""
        <div class="glass-card" style="height: 100%; display: flex; flex-direction: column; justify-content: center; align-items: center; text-align: center; padding: 1.2rem;">
            <div style="font-size: 0.9rem; font-weight: 700; color: var(--text-primary); margin-bottom: 0.5rem;">
                Reserve Facility at {loc_name}
            </div>
            <p style="font-size: 0.78rem; color: var(--text-muted); margin-bottom: 1rem;">
                Lock in an available wheelchair or disabled parking space before your visit.
            </p>
        </div>
        """.replace("{loc_name}", location_name), unsafe_allow_html=True)

        if st.button("🚀 Reserve Now", key="reserve_now_from_predictor", use_container_width=True):
            st.session_state["prefill_booking_location"] = location_name
            st.switch_page("pages/09_Smart_Accessibility_Booking.py")

render_footer()
