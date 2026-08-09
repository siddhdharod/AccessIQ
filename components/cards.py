import streamlit as st

def render_kpi_card(title: str, value: str, subtitle: str = None, icon: str = "📊", color: str = "indigo"):
    """Render a premium glassmorphic KPI card using theme-aware CSS classes."""
    st.markdown(f"""
    <div class="kpi-card">
        <div style="display: flex; justify-content: space-between; align-items: flex-start;">
            <div>
                <div class="kpi-title">{title}</div>
                <div class="kpi-value">{value}</div>
                {f'<div class="kpi-subtitle">{subtitle}</div>' if subtitle else ''}
            </div>
            <div class="kpi-icon">{icon}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

def get_badge_html(category: str) -> str:
    """Return HTML status badge based on category."""
    cat = str(category).lower()
    if "excellent" in cat:
        return '<span class="badge-excellent">★ Excellent</span>'
    elif "good" in cat:
        return '<span class="badge-good">✔ Good</span>'
    elif "fair" in cat:
        return '<span class="badge-fair">⚠ Fair</span>'
    else:
        return '<span class="badge-poor">✖ Poor</span>'

def get_priority_badge_html(priority: str) -> str:
    """Return HTML badge for improvement priority."""
    p = str(priority).lower()
    if "high" in p:
        return '<span style="background: var(--danger-bg); color: var(--danger); border: 1px solid var(--danger-border); padding: 0.2rem 0.65rem; border-radius: 6px; font-weight: 700; font-size: 0.75rem; letter-spacing: 0.03em;">HIGH PRIORITY</span>'
    elif "medium" in p:
        return '<span style="background: var(--warning-bg); color: var(--warning); border: 1px solid var(--warning-border); padding: 0.2rem 0.65rem; border-radius: 6px; font-weight: 700; font-size: 0.75rem; letter-spacing: 0.03em;">MEDIUM PRIORITY</span>'
    else:
        return '<span style="background: var(--success-bg); color: var(--success); border: 1px solid var(--success-border); padding: 0.2rem 0.65rem; border-radius: 6px; font-weight: 700; font-size: 0.75rem; letter-spacing: 0.03em;">LOW PRIORITY</span>'

def render_recommendation_card(
    location_name: str,
    city: str,
    score: float,
    category: str,
    reason: str,
    priority: str,
    distance_km: float = None
):
    """Render a detailed recommendation card with theme-aware styling."""
    badge = get_badge_html(category)
    p_badge = get_priority_badge_html(priority)
    dist_str = f"📍 <b>{distance_km:.1f} km</b> away" if distance_km is not None else "📍 Urban Center"

    st.markdown(f"""
    <div class="glass-card" style="margin-bottom: 1rem;">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.6rem;">
            <div>
                <h3 style="margin: 0; font-size: 1.2rem; color: var(--text-primary);">{location_name}</h3>
                <span style="font-size: 0.85rem; color: var(--text-muted);">{city} • {dist_str}</span>
            </div>
            <div style="text-align: right;">
                <div style="font-size: 1.6rem; font-weight: 800; color: var(--primary);">{score:.1f}<span style="font-size: 0.9rem; color: var(--text-muted);">/100</span></div>
                {badge}
            </div>
        </div>
        <hr style="border-color: var(--card-border); margin: 0.6rem 0;">
        <div style="font-size: 0.88rem; color: var(--text-body); margin-bottom: 0.6rem; line-height: 1.5;">
            💡 <b>Persona Key Reason:</b> {reason}
        </div>
        <div style="display: flex; justify-content: space-between; align-items: center; font-size: 0.78rem; color: var(--text-muted);">
            <div>{p_badge}</div>
            <div style="color: var(--text-muted);">AccessIQ Verified Location</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
