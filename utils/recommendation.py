import numpy as np
import pandas as pd
from utils.helpers import PERSONAS
from utils.prediction import score_to_category, score_to_priority

def calculate_haversine_distance(lat1, lon1, lat2, lon2):
    """Calculate distance in km between two lat/lon points."""
    R = 6371.0 # Earth radius in kilometers
    dlat = np.radians(lat2 - lat1)
    dlon = np.radians(lon2 - lon1)
    a = np.sin(dlat / 2)**2 + np.cos(np.radians(lat1)) * np.cos(np.radians(lat2)) * np.sin(dlon / 2)**2
    c = 2 * np.atan2(np.sqrt(a), np.sqrt(1 - a))
    return R * c

def calculate_persona_score(row: pd.Series, persona: str) -> float:
    """Calculate weighted accessibility score tailored to persona requirements."""
    spec = PERSONAS.get(persona, PERSONAS["Normal User"])
    weights = spec["weights"]
    
    base_score = row.get("Accessibility_Score", 50.0)
    persona_bonus = 0.0
    
    for feature, weight in weights.items():
        if feature in row:
            val = float(row[feature])
            persona_bonus += val * weight * 3.0
            
    final_score = np.clip(base_score + persona_bonus, 5.0, 99.9)
    return round(final_score, 1)

def get_recommendations(df: pd.DataFrame, persona: str, city: str = "All", user_lat: float = None, user_lon: float = None, top_n: int = 5) -> pd.DataFrame:
    """Return top N recommended locations tailored to user persona and location."""
    if df.empty:
        return pd.DataFrame()
        
    filtered = df.copy()
    
    if city != "All" and "City" in filtered.columns:
        filtered = filtered[filtered["City"].astype(str) == str(city)]
        if filtered.empty:
            filtered = df.copy() # fallback if city filter leaves 0 rows
            
    # Calculate persona score
    scores = []
    distances = []
    reasons = []
    
    for idx, row in filtered.iterrows():
        p_score = calculate_persona_score(row, persona)
        scores.append(p_score)
        
        # Distance
        if user_lat is not None and user_lon is not None and "Latitude" in row and "Longitude" in row:
            dist = calculate_haversine_distance(user_lat, user_lon, row["Latitude"], row["Longitude"])
            distances.append(round(dist, 1))
        else:
            distances.append(None)
            
        # Reason building
        r_reasons = []
        if persona == "Wheelchair User":
            if row.get("Ramp_Available", 0) == 1: r_reasons.append("Step-free ramp")
            if row.get("Elevator_Available", 0) == 1: r_reasons.append("Elevator access")
            if row.get("Wheelchair_Entrance", 0) == 1: r_reasons.append("Wide wheelchair entry")
        elif persona == "Visually Impaired":
            if row.get("Tactile_Path", 0) == 1: r_reasons.append("Tactile paving")
            if row.get("Braille_Signage", 0) == 1: r_reasons.append("Braille signs")
            if row.get("Audio_Announcements", 0) == 1: r_reasons.append("Audio support")
        elif persona == "Senior Citizen":
            if row.get("Lighting", 0) >= 2: r_reasons.append("High lighting & visibility")
            if row.get("Average_Waiting_Time", 30) < 15: r_reasons.append("Low waiting time")
            if row.get("Reserved_Parking", 0) == 1: r_reasons.append("Reserved parking")
        else:
            if row.get("Accessibility_Score", 0) > 75: r_reasons.append("High overall accessibility")
            if row.get("Safety_Level", 0) >= 2: r_reasons.append("Enhanced safety level")
            
        reason_str = ", ".join(r_reasons) if r_reasons else "High overall infrastructural compatibility"
        reasons.append(reason_str)

    filtered["Persona_Score"] = scores
    filtered["Distance_km"] = distances
    filtered["Recommendation_Reason"] = reasons
    filtered["Category"] = filtered["Persona_Score"].apply(score_to_category)
    filtered["Priority"] = filtered["Persona_Score"].apply(score_to_priority)

    # Sort by persona score descending
    recommendations = filtered.sort_values(by="Persona_Score", ascending=False).head(top_n)
    return recommendations
