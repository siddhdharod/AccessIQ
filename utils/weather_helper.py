import os
import requests
import streamlit as st

def get_weather_api_key() -> str | None:
    """Retrieve OpenWeather API Key safely from Streamlit secrets (st.secrets["WEATHER_API_KEY"])
    or environment variables. Never raises — returns None on any failure.
    """
    try:
        if hasattr(st, "secrets") and "WEATHER_API_KEY" in st.secrets:
            key = str(st.secrets["WEATHER_API_KEY"]).strip()
            if key:
                return key
    except Exception:
        pass

    try:
        key = os.getenv("WEATHER_API_KEY", "").strip()
        if key:
            return key
    except Exception:
        pass

    return None

@st.cache_data(ttl=1800)
def fetch_weather_data(lat: float = 28.6139, lon: float = 77.2090, city_name: str = None):
    """Fetch current weather data from OpenWeather API with caching."""
    api_key = get_weather_api_key()
    if not api_key:
        return {
            "available": False,
            "message": "Weather API key missing in .env"
        }
    
    try:
        if city_name and city_name != "All":
            url = f"https://api.openweathermap.org/data/2.5/weather?q={city_name}&units=metric&appid={api_key}"
        else:
            url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&units=metric&appid={api_key}"
        
        response = requests.get(url, timeout=8)
        if response.status_code == 200:
            data = response.json()
            main = data.get("main", {})
            weather = data.get("weather", [{}])[0]
            wind = data.get("wind", {})
            return {
                "available": True,
                "city": data.get("name", "Unknown Location"),
                "temp": round(main.get("temp", 25.0), 1),
                "feels_like": round(main.get("feels_like", 25.0), 1),
                "humidity": main.get("humidity", 50),
                "condition": weather.get("main", "Clear"),
                "description": weather.get("description", "clear sky").title(),
                "icon": weather.get("icon", "01d"),
                "wind_speed": wind.get("speed", 3.0)
            }
        else:
            return {
                "available": False,
                "message": f"Weather API status code {response.status_code}"
            }
    except Exception as e:
        return {
            "available": False,
            "message": f"Weather service unavailable ({str(e)})"
        }

def evaluate_weather_persona_risk(weather_info: dict, persona: str) -> dict:
    """Evaluate weather risks and recommendations for specific user personas."""
    if not weather_info.get("available"):
        return {
            "level": "info",
            "warning": "Weather data unavailable. Exercise standard caution.",
            "suggestion": "Check local weather forecasts before traveling."
        }
    
    condition = weather_info.get("condition", "").lower()
    temp = weather_info.get("temp", 25.0)
    
    if persona == "Wheelchair User":
        if "rain" in condition or "drizzle" in condition or "thunderstorm" in condition:
            return {
                "level": "danger",
                "warning": "🌧️ RAIN ALERT FOR WHEELCHAIR USERS: Outdoor ramps and footpaths may be slippery.",
                "suggestion": "Prioritize indoor venues with sheltered parking and indoor elevator access."
            }
        elif temp > 36.0:
            return {
                "level": "warning",
                "warning": "☀️ EXTREME HEAT ALERT: Metal ramps and handrails can become hot to touch.",
                "suggestion": "Use covered walkways and carry drinking water."
            }
            
    elif persona == "Senior Citizen" or persona == "Pregnant Woman":
        if temp > 35.0:
            return {
                "level": "danger",
                "warning": "🔥 HEATWAVE WARNING: High ambient temperature detected.",
                "suggestion": "Select air-conditioned indoor locations with low waiting times and elevator access."
            }
        elif temp < 10.0:
            return {
                "level": "warning",
                "warning": "❄️ COLD WEATHER ALERT: Low outdoor temperature.",
                "suggestion": "Seek heated public facilities and minimize outdoor exposure."
            }
        elif "rain" in condition:
            return {
                "level": "warning",
                "warning": "🌧️ RAIN WARNING: Slippery walkways and outdoor footpaths.",
                "suggestion": "Choose locations with indoor seating and tactile safety flooring."
            }
            
    elif persona == "Visually Impaired":
        if "rain" in condition or "snow" in condition:
            return {
                "level": "warning",
                "warning": "🌧️ WEATHER HAZARD: Wet or covered tactile paving may alter surface feel.",
                "suggestion": "Request staff assistance and utilize audio guidance features."
            }

    return {
        "level": "success",
        "warning": "☀️ FAVORABLE WEATHER: Conditions are good for outdoor transit.",
        "suggestion": "Standard accessibility features apply."
    }

def render_weather_widget(lat: float = 28.6139, lon: float = 77.2090, city: str = None, persona: str = "Wheelchair User"):
    """Render a modern glassmorphic weather card in Streamlit with theme support."""
    w = fetch_weather_data(lat, lon, city)
    if not w.get("available"):
        st.info(f"🌤️ Weather Widget: {w.get('message', 'Key missing in .env')}")
        return

    risk = evaluate_weather_persona_risk(w, persona)
    
    border_color = "var(--success)" if risk["level"] == "success" else ("var(--warning)" if risk["level"] == "warning" else "var(--danger)")
    
    st.markdown(f"""
    <div style="background: var(--card-bg); backdrop-filter: blur(16px); border-radius: var(--radius-xl); padding: 1.25rem; border: 1px solid var(--card-border); border-left: 5px solid {border_color}; margin-bottom: 1rem; box-shadow: var(--shadow-md);">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <div>
                <span style="font-size: 0.78rem; color: var(--text-muted); font-weight: 600; text-transform: uppercase; letter-spacing: 0.08em;">Live Weather • {w['city']}</span>
                <div style="font-size: 1.8rem; font-weight: 800; color: var(--text-primary); margin-top: 0.2rem;">
                    {w['temp']}°C <span style="font-size: 0.95rem; color: var(--text-secondary); font-weight: 400;">({w['description']})</span>
                </div>
            </div>
            <div style="text-align: right; color: var(--text-muted); font-size: 0.82rem;">
                <div>💧 Humidity: <b style="color: var(--text-primary);">{w['humidity']}%</b></div>
                <div>💨 Wind: <b style="color: var(--text-primary);">{w['wind_speed']} m/s</b></div>
            </div>
        </div>
        <hr style="border-color: var(--card-border); margin: 0.8rem 0;">
        <div style="font-size: 0.88rem; font-weight: 600; color: {'var(--danger)' if risk['level']=='danger' else ('var(--warning)' if risk['level']=='warning' else 'var(--success)')};">
            {risk['warning']}
        </div>
        <div style="font-size: 0.82rem; color: var(--text-secondary); margin-top: 0.25rem;">
            💡 <b>Advice:</b> {risk['suggestion']}
        </div>
    </div>
    """, unsafe_allow_html=True)
