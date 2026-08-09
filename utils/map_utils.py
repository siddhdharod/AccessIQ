import folium
from folium.plugins import MarkerCluster, HeatMap, Fullscreen, LocateControl
import pandas as pd
import streamlit as st
from streamlit_folium import st_folium

CATEGORY_HEX = {
    "Excellent": "#22C55E",
    "Good": "#3B82F6",
    "Fair": "#F59E0B",
    "Poor": "#EF4444"
}

CATEGORY_COLORS = {
    "Excellent": "green",
    "Good": "blue",
    "Fair": "orange",
    "Poor": "red"
}

def render_accessibility_map(
    df: pd.DataFrame,
    center_lat: float = 20.5937,
    center_lon: float = 78.9629,
    zoom: int = 5,
    show_hotspots: bool = True,
    selected_location_id: str = None,
    height: int = 520
):
    """Render an interactive, modern Leaflet + OpenStreetMap Folium map with custom markers, legend, and controls."""
    if df.empty:
        st.warning("No location data available for map rendering.")
        return None

    # Calculate center from data if default
    if "Latitude" in df.columns and "Longitude" in df.columns and len(df) > 0:
        valid_df = df.dropna(subset=["Latitude", "Longitude"])
        if not valid_df.empty:
            center_lat = float(valid_df["Latitude"].mean())
            center_lon = float(valid_df["Longitude"].mean())

    # Map Tiles: Positron / OpenStreetMap with clean tiles
    m = folium.Map(
        location=[center_lat, center_lon],
        zoom_start=zoom,
        tiles="CartoDB positron",
        control_scale=True
    )

    # Fullscreen & Locate Me Controls
    Fullscreen(position="topright", title="Expand Fullscreen", title_cancel="Exit Fullscreen").add_to(m)
    try:
        LocateControl(position="topleft", auto_start=False).add_to(m)
    except Exception:
        pass

    marker_cluster = MarkerCluster(name="Audited Venues").add_to(m)

    hotspot_data = []

    for idx, row in df.iterrows():
        lat = row.get("Latitude")
        lon = row.get("Longitude")
        if pd.isna(lat) or pd.isna(lon):
            continue

        loc_id = str(row.get("Location_ID", f"LOC_{idx}"))
        loc_name = str(row.get("Location_Name", "Public Venue"))
        score = float(row.get("Accessibility_Score", row.get("Predicted_Accessibility", 50.0)))
        category = str(row.get("Accessibility_Category", row.get("Predicted_Category", "Fair")))
        city = str(row.get("City", "Urban Area"))
        complaints = int(row.get("Accessibility_Complaints", 0))

        color_name = CATEGORY_COLORS.get(category, "blue")
        hex_color = CATEGORY_HEX.get(category, "#3B82F6")

        # Highlight selected location vs regular
        if selected_location_id and loc_id == selected_location_id:
            icon = folium.Icon(color="purple", icon="star", prefix="fa")
        else:
            icon = folium.Icon(color=color_name, icon="info-sign")

        popup_html = f"""
        <div style="font-family: 'Inter', sans-serif; min-width: 200px; padding: 4px;">
            <div style="font-size: 14px; font-weight: 800; color: #0F172A; margin-bottom: 4px;">{loc_name}</div>
            <div style="font-size: 11px; color: #64748B; margin-bottom: 8px;">City: <b>{city}</b></div>
            <div style="background: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 8px; padding: 8px; margin-bottom: 6px;">
                <div style="display: flex; justify-content: space-between; font-size: 12px; margin-bottom: 2px;">
                    <span>Accessibility Score:</span>
                    <b style="color: {hex_color}; font-size: 13px;">{score:.1f}/100</b>
                </div>
                <div style="display: flex; justify-content: space-between; font-size: 12px;">
                    <span>Classification:</span>
                    <b style="color: {hex_color};">{category}</b>
                </div>
            </div>
            <div style="font-size: 11px; color: #64748B;">Accessibility Complaints: <b>{complaints}</b></div>
        </div>
        """

        folium.Marker(
            location=[lat, lon],
            popup=folium.Popup(popup_html, max_width=280),
            tooltip=f"{loc_name} ({category} • {score:.1f}/100)",
            icon=icon
        ).add_to(marker_cluster)

        # Collect complaint hotspots
        if complaints > 0:
            hotspot_data.append([lat, lon, complaints])

    # Complaint Hotspot Overlay
    if show_hotspots and len(hotspot_data) > 0:
        HeatMap(
            hotspot_data,
            name="Complaint Hotspots Heatmap",
            radius=18,
            blur=12,
            max_zoom=1,
            gradient={0.3: '#FDE047', 0.6: '#F97316', 1.0: '#EF4444'}
        ).add_to(m)

    # Custom Map Legend HTML Overlay
    legend_html = """
    <div style="
        position: fixed;
        bottom: 30px; left: 30px; width: 160px; height: 110px;
        background: rgba(255, 255, 255, 0.92);
        backdrop-filter: blur(10px);
        border: 1px solid #E2E8F0;
        border-radius: 12px;
        z-index: 9999;
        font-family: 'Inter', sans-serif;
        font-size: 11px;
        padding: 8px 12px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    ">
        <b style="color: #0F172A; font-size: 11px;">Accessibility Legend</b><br>
        <div style="margin-top: 6px;">
            <span style="color: #22C55E; font-size: 13px;">●</span> Excellent (80-100)<br>
            <span style="color: #3B82F6; font-size: 13px;">●</span> Good (65-79)<br>
            <span style="color: #F59E0B; font-size: 13px;">●</span> Fair (45-64)<br>
            <span style="color: #EF4444; font-size: 13px;">●</span> Poor (0-44)
        </div>
    </div>
    """
    m.get_root().html.add_child(folium.Element(legend_html))

    folium.LayerControl(position="topright").add_to(m)

    return st_folium(m, height=height, width=None, use_container_width=True)
