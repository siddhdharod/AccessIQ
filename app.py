import streamlit as st
from utils.helpers import init_session_state, inject_custom_css, load_dataset
from components.navbar import render_navbar
from components.sidebar import render_sidebar
from components.footer import render_footer
from components.chatbot_widget import render_chatbot_widget
import pandas as pd

# 1. Streamlit Page Configuration
st.set_page_config(
    page_title="AccessIQ - AI Accessibility Platform",
    page_icon="♿",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. Initialize Session State & CSS Theme
init_session_state()
inject_custom_css()

# 3. Load dataset
df = load_dataset()
cities = df["City"].dropna().unique().tolist() if not df.empty and "City" in df.columns else []

# 4. Render Navigation & Sidebar
render_navbar()
sidebar_data = render_sidebar(cities)

# 5. Render Floating AI Assistant Chatbot
render_chatbot_widget(sidebar_data["persona"])

# 6. Hero SaaS Landing View
st.markdown("""
<div class="page-transition">
    <div class="hero-box">
        <div class="hero-badge">
            🚀 NEXT-GEN URBAN ACCESSIBILITY AI
        </div>
        <h1 class="hero-title">
            Building Accessible Cities for <span class="gradient-text">Everyone, Everywhere</span>
        </h1>
        <p class="hero-subtitle">
            AccessIQ leverages advanced Dual Machine Learning (XGBoost & Random Forest), OpenWeather real-time environmental risk radar, Groq LLaMA-3.3 AI, and Leaflet OpenStreetMap spatial analytics to audit public infrastructure, score mobility venues, and recommend accessible pathways.
        </p>
        <div style="margin-top: 1.5rem;"></div>
    </div>
</div>
""", unsafe_allow_html=True)

col_hero_1, col_hero_2 = st.columns([1, 1])
with col_hero_1:
    st.page_link("pages/01_Dashboard.py", label="📊 Explore Live Dashboard", icon="📊", use_container_width=True)
with col_hero_2:
    st.page_link("pages/02_Accessibility_Predictor.py", label="🔮 Run Predictor Engine", icon="🔮", use_container_width=True)


# Key Feature Highlights Grid
st.markdown("""
<div class="section-header">
    <span>🌟 Core Platform Intelligence Features</span>
    <div class="section-header-line"></div>
</div>
""", unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    <div class="glass-card" style="height: 100%;">
        <div style="font-size: 2.2rem; margin-bottom: 0.6rem;">🤖</div>
        <h4 style="margin: 0 0 0.5rem 0; color: var(--text-primary);">Groq LLaMA-3 & Gemini AI</h4>
        <p style="font-size: 0.88rem; color: var(--text-secondary); line-height: 1.5;">
            Generates natural language accessibility improvement plans, persona reasoning, prediction diagnoses, and executive audit summaries.
        </p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="glass-card" style="height: 100%;">
        <div style="font-size: 2.2rem; margin-bottom: 0.6rem;">🌦️</div>
        <h4 style="margin: 0 0 0.5rem 0; color: var(--text-primary);">Live Weather Risk Radar</h4>
        <p style="font-size: 0.88rem; color: var(--text-secondary); line-height: 1.5;">
            Evaluates real-time OpenWeather data for wheelchair users (slippery ramps) and seniors (extreme heat/cold) to prevent transit hazards.
        </p>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div class="glass-card" style="height: 100%;">
        <div style="font-size: 2.2rem; margin-bottom: 0.6rem;">🗺️</div>
        <h4 style="margin: 0 0 0.5rem 0; color: var(--text-primary);">Leaflet Spatial Heatmap</h4>
        <p style="font-size: 0.88rem; color: var(--text-secondary); line-height: 1.5;">
            Interactive CartoDB Positron maps with complaint hotspot heatmaps, cluster markers, legend filters, and fullscreen audit mode.
        </p>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# Additional Quick Navigation Grid
col_a, col_b, col_c, col_d = st.columns(4)

with col_a:
    st.markdown("""
    <div class="kpi-card">
        <div style="font-size: 1.15rem; font-weight: 700; color: var(--text-primary);">⚔️ Compare Venues</div>
        <p style="font-size: 0.82rem; color: var(--text-muted); margin: 0.4rem 0;">Plotly radar side-by-side venue auditing.</p>
    </div>
    """, unsafe_allow_html=True)

with col_b:
    st.markdown("""
    <div class="kpi-card">
        <div style="font-size: 1.15rem; font-weight: 700; color: var(--text-primary);">🧠 Explainable AI</div>
        <p style="font-size: 0.82rem; color: var(--text-muted); margin: 0.4rem 0;">SHAP summary, waterfall, and dependence plots.</p>
    </div>
    """, unsafe_allow_html=True)

with col_c:
    st.markdown("""
    <div class="kpi-card">
        <div style="font-size: 1.15rem; font-weight: 700; color: var(--text-primary);">📄 PDF Exporter</div>
        <p style="font-size: 0.82rem; color: var(--text-muted); margin: 0.4rem 0;">One-click official audit PDF report exporter.</p>
    </div>
    """, unsafe_allow_html=True)

with col_d:
    st.markdown("""
    <div class="kpi-card">
        <div style="font-size: 1.15rem; font-weight: 700; color: var(--text-primary);">🎯 7 User Personas</div>
        <p style="font-size: 0.82rem; color: var(--text-muted); margin: 0.4rem 0;">Tailored recommendation engine for all needs.</p>
    </div>
    """, unsafe_allow_html=True)

render_footer()
