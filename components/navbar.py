import streamlit as st

def render_navbar():
    """
    Render minimal, professional sticky navbar with brand logo and theme toggle button.
    Clean glassmorphism, blur effect, and shadow.
    """
    current_theme = st.session_state.get("theme", "dark")
    theme_icon = "☀️ Light Mode" if current_theme == "dark" else "🌙 Dark Mode"
    
    col_brand, col_toggle = st.columns([3, 1])
    
    with col_brand:
        st.markdown("""
        <div class="navbar-container" style="margin-bottom: 0;">
            <div class="navbar-brand">
                <span class="navbar-logo">♿</span>
                <div>
                    <div class="navbar-title">AccessIQ</div>
                    <div class="navbar-tagline">AI-Powered Urban Accessibility Platform</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
    with col_toggle:
        if st.button(f"{'☀️ Light' if current_theme == 'dark' else '🌙 Dark'}", key="navbar_theme_toggle_btn", use_container_width=True):
            st.session_state["theme"] = "light" if current_theme == "dark" else "dark"
            st.rerun()
