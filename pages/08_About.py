import streamlit as st
from utils.helpers import init_session_state, inject_custom_css, load_dataset
from components.navbar import render_navbar
from components.sidebar import render_sidebar
from components.footer import render_footer
from components.chatbot_widget import render_chatbot_widget

st.set_page_config(page_title="About - AccessIQ", page_icon="ℹ️", layout="wide")
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
        <h2 style="margin: 0; font-size: 1.8rem; font-weight: 800;">ℹ️ About AccessIQ Platform</h2>
        <p style="color: var(--text-muted); font-size: 0.9rem; margin-top: 0.2rem;">
            Discover system architecture, ML intelligence capabilities, and UN SDG alignment.
        </p>
    </div>
</div>
""", unsafe_allow_html=True)

tab_about, tab_sdg = st.tabs([
    "🏛️ System Architecture",
    "🎯 UN Sustainable Development Goals"
])

with tab_about:
    st.markdown("""
    <div class="glass-card" style="line-height: 1.7;">
        <h3 style="margin-top: 0; color: var(--text-primary);">🏗️ Enterprise Architectural Overview</h3>
        <p style="color: var(--text-body);">
            AccessIQ is an end-to-end AI-driven urban accessibility intelligence platform engineered for municipal planners, disability advocates, and citizens.
        </p>
        <ul style="color: var(--text-secondary); padding-left: 1.2rem;">
            <li><b>Data Engineering & 43 Parameters:</b> Quantifies physical infrastructure (ramps, elevators, tactile paths, door widths), safety indices, queue wait times, and complaint rates.</li>
            <li><b>Dual Machine Learning Core:</b> Trained Scikit-Learn / XGBoost & Random Forest models executing continuous Accessibility Score regression (0-100) and 4-class categorical classification.</li>
            <li><b>Groq LLaMA-3.3 & Gemini Generative AI:</b> Natural language model explanations, persona recommendation reasoning, and automated PDF audit reports.</li>
            <li><b>Live Weather Risk Radar:</b> REST API integration calculating real-time hazard warnings for wheelchair users and senior citizens.</li>
            <li><b>Spatial Leaflet Heatmap:</b> Interactive CartoDB Positron maps with complaint hotspot heatmaps, cluster markers, and fullscreen audit mode.</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

with tab_sdg:
    st.markdown("""
    <div class="glass-card" style="line-height: 1.7;">
        <h3 style="margin-top: 0; color: var(--text-primary);">🎯 Alignment with UN Sustainable Development Goals (SDGs)</h3>
        <p style="color: var(--text-body);">AccessIQ directly advances two United Nations Sustainable Development Goals:</p>
        
        <div style="background: var(--gradient-card); border-left: 4px solid var(--accent); padding: 1rem; border-radius: var(--radius-md); margin-bottom: 1rem;">
            <h4 style="margin: 0; color: var(--text-primary);">1. SDG 10: Reduced Inequalities (Target 10.2)</h4>
            <blockquote style="margin: 0.5rem 0 0 0; font-style: italic; color: var(--text-secondary);">
                "By 2030, empower and promote the social, economic and political inclusion of all, irrespective of age, sex, disability, race, ethnicity, origin, religion or economic or other status."
            </blockquote>
        </div>
        
        <div style="background: var(--gradient-card); border-left: 4px solid var(--primary); padding: 1rem; border-radius: var(--radius-md);">
            <h4 style="margin: 0; color: var(--text-primary);">2. SDG 11: Sustainable Cities and Communities (Target 11.2 & 11.7)</h4>
            <blockquote style="margin: 0.5rem 0 0 0; font-style: italic; color: var(--text-secondary);">
                "Provide access to safe, affordable, accessible and sustainable transport systems for all, improving road safety, notably by expanding public transport, with special attention to the needs of those in vulnerable situations, women, children, persons with disabilities and older persons."
            </blockquote>
        </div>
    </div>
    """, unsafe_allow_html=True)

render_footer()
