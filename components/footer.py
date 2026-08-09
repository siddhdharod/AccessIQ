import streamlit as st

def render_footer():
    """Render premium theme-aware footer with UN SDG badges, tech attribution, and copyright."""
    st.markdown("""
    <div class="footer-container">
        <div style="display: flex; justify-content: center; gap: 0.8rem; margin-bottom: 1rem; flex-wrap: wrap;">
            <span class="footer-badge footer-badge-sdg10">
                🎯 UN SDG 10: Reduced Inequalities
            </span>
            <span class="footer-badge footer-badge-sdg11">
                🏙️ UN SDG 11: Sustainable Cities & Communities
            </span>
        </div>
        <div class="footer-text">
            <b>AccessIQ Platform v2.5</b> • Powered by Groq LLaMA-3.3, Google Gemini AI & OpenWeather REST API
        </div>
        <div class="footer-version">
            Engineered for Production Urban Planning, ADA Compliance & Smart City Infrastructure Audits
        </div>
    </div>
    """, unsafe_allow_html=True)
