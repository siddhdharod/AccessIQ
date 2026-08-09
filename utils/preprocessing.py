import numpy as np
import pandas as pd

def add_engineered_features(df: pd.DataFrame) -> pd.DataFrame:
    """Compute and add engineered features to the dataset."""
    df_out = df.copy()
    
    # Infrastructure Score
    infra_cols = ["Ramp_Available", "Elevator_Available", "Wheelchair_Entrance", "Accessible_Washroom", "Reserved_Parking"]
    avail_infra = [c for c in infra_cols if c in df_out.columns]
    if avail_infra:
        df_out["Infrastructure_Score"] = df_out[avail_infra].sum(axis=1)
        
    # Accessibility Support Score
    supp_cols = ["Braille_Signage", "Audio_Announcements", "Tactile_Path"]
    avail_supp = [c for c in supp_cols if c in df_out.columns]
    if avail_supp:
        df_out["Accessibility_Support_Score"] = df_out[avail_supp].sum(axis=1)
        
    # Safety Index
    safe_cols = ["Lighting", "Safety_Level", "CCTV_Available"]
    avail_safe = [c for c in safe_cols if c in df_out.columns]
    if avail_safe:
        df_out["Safety_Index"] = df_out[avail_safe].sum(axis=1)
        
    # Facility Score
    fac_cols = ["Parking_Available", "Public_Transport_Nearby"]
    avail_fac = [c for c in fac_cols if c in df_out.columns]
    if avail_fac:
        df_out["Facility_Score"] = df_out[avail_fac].sum(axis=1)
        
    # Crowd Risk
    if "Crowd_Level" in df_out.columns and "Average_Waiting_Time" in df_out.columns:
        df_out["Crowd_Risk"] = df_out["Crowd_Level"] * df_out["Average_Waiting_Time"]
        
    # Complaint Rate
    if "Accessibility_Complaints" in df_out.columns and "Daily_Footfall" in df_out.columns:
        df_out["Complaint_Rate"] = df_out["Accessibility_Complaints"] / (df_out["Daily_Footfall"] + 1)
        
    # Accessibility Efficiency
    if "Accessibility_Score" in df_out.columns and "Average_Waiting_Time" in df_out.columns:
        df_out["Accessibility_Efficiency"] = df_out["Accessibility_Score"] / (df_out["Average_Waiting_Time"] + 1)
        
    return df_out

def compute_dict_features(data_dict: dict) -> dict:
    """Compute engineered features for a single sample input dictionary."""
    d = data_dict.copy()
    d["Infrastructure_Score"] = sum([d.get(k, 0) for k in ["Ramp_Available", "Elevator_Available", "Wheelchair_Entrance", "Accessible_Washroom", "Reserved_Parking"]])
    d["Accessibility_Support_Score"] = sum([d.get(k, 0) for k in ["Braille_Signage", "Audio_Announcements", "Tactile_Path"]])
    d["Safety_Index"] = sum([d.get(k, 0) for k in ["Lighting", "Safety_Level", "CCTV_Available"]])
    d["Facility_Score"] = sum([d.get(k, 0) for k in ["Parking_Available", "Public_Transport_Nearby"]])
    d["Crowd_Risk"] = d.get("Crowd_Level", 1) * d.get("Average_Waiting_Time", 10.0)
    d["Complaint_Rate"] = d.get("Accessibility_Complaints", 0) / (d.get("Daily_Footfall", 1000) + 1)
    return d
