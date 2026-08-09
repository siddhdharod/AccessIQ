import pandas as pd
import streamlit as st
from utils.helpers import PERSONAS

def render_sidebar(cities: list = None):
    """
    Render redesigned premium sidebar with logo header, status badge, persona selector,
    city filter, theme switcher, and navigation guide.
    """
    with st.sidebar:
        # Premium Brand Header with Gradient Logo & Live Status Indicator
        st.markdown("""
        <div class="sidebar-header">
            <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 0.4rem;">
                <div style="display: flex; align-items: center; gap: 0.6rem;">
                    <span style="font-size: 1.8rem; filter: drop-shadow(0 2px 8px rgba(139,92,246,0.4));">♿</span>
                    <div>
                        <div class="sidebar-logo">AccessIQ</div>
                        <div class="sidebar-subtitle">Smart AI Accessibility Platform</div>
                    </div>
                </div>
            </div>
            <div style="display: flex; align-items: center; justify-content: space-between; margin-top: 0.6rem;">
                <div class="sidebar-status">
                    <div class="sidebar-status-dot"></div>
                    <span>System Online</span>
                </div>
                <span style="font-size: 0.68rem; color: var(--text-dim); font-weight: 500;">v2.5 Pro</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # ── User Persona Selector ──
        st.markdown('<div class="sidebar-section-title">👤 Mobility Persona</div>', unsafe_allow_html=True)
        persona_list = list(PERSONAS.keys())
        current_persona = st.session_state.get("selected_persona", "Wheelchair User")

        selected_p = st.selectbox(
            "Select Persona",
            persona_list,
            index=persona_list.index(current_persona) if current_persona in persona_list else 0,
            key="persona_select",
            label_visibility="collapsed"
        )
        st.session_state["selected_persona"] = selected_p

        # Persona Spec Glass Card
        p_info = PERSONAS[selected_p]
        st.markdown(f"""
        <div style="background: var(--card-bg); border: 1px solid var(--card-border); border-radius: var(--radius-lg); padding: 0.8rem 0.9rem; margin-top: 0.4rem; backdrop-filter: blur(12px);">
            <div style="font-size: 0.88rem; font-weight: 700; color: var(--text-primary); display: flex; align-items: center; gap: 0.4rem;">
                <span>{p_info['icon']}</span>
                <span>{selected_p}</span>
            </div>
            <div style="font-size: 0.74rem; color: var(--text-secondary); margin-top: 0.35rem; line-height: 1.45;">
                {p_info['description']}
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown('<hr class="sidebar-divider">', unsafe_allow_html=True)

        # ── City / Region Filter ──
        selected_city = "All"
        if cities and len(cities) > 0:
            st.markdown('<div class="sidebar-section-title">🏙️ Region Filter</div>', unsafe_allow_html=True)
            valid_cities = [str(c) for c in cities if pd.notna(c) and str(c).strip() != ""]
            city_options = ["All"] + sorted(list(set(valid_cities)))
            selected_city = st.selectbox(
                "Select City",
                city_options,
                key="city_sidebar_select",
                label_visibility="collapsed"
            )

        st.markdown('<hr class="sidebar-divider">', unsafe_allow_html=True)

        # ── Theme Toggle ──
        st.markdown('<div class="sidebar-section-title">🎨 Appearance Theme</div>', unsafe_allow_html=True)
        current_theme = st.session_state.get("theme", "dark")
        theme_choice = st.radio(
            "Theme",
            ["🌙 Purple Dark", "☀️ Soft Lavender"],
            index=0 if current_theme == "dark" else 1,
            key="theme_radio",
            label_visibility="collapsed"
        )
        new_theme = "dark" if "Dark" in theme_choice else "light"
        if new_theme != current_theme:
            st.session_state["theme"] = new_theme
            st.rerun()

        st.markdown('<hr class="sidebar-divider">', unsafe_allow_html=True)

        # Footer Tip Card
        st.markdown("""
        <div style="font-size: 0.72rem; color: var(--text-muted); padding: 0.3rem 0; line-height: 1.4;">
            💡 <b>Pro Tip:</b> Use pages sidebar above to navigate predictor, analytics, SHAP, and report generator.
        </div>
        """, unsafe_allow_html=True)

        return {
            "theme": st.session_state["theme"],
            "persona": selected_p,
            "city": selected_city
        }
