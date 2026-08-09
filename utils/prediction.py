import os
import pickle
from pathlib import Path
import joblib
import numpy as np
import pandas as pd
import streamlit as st
from utils.preprocessing import compute_dict_features

_BASE_DIR = Path(__file__).resolve().parent.parent

@st.cache_resource
def load_ml_models():
    """Load pickled models, scaler, label encoder, and feature columns."""
    models_dir = _BASE_DIR / "models"
    models = {}
    
    # 1. Feature columns
    feat_path = models_dir / "feature_columns.pkl"
    if feat_path.exists():
        models["feature_columns"] = joblib.load(feat_path)
    else:
        models["feature_columns"] = None
        
    # 2. Regression model
    reg_path = models_dir / "best_regression_model.pkl"
    if reg_path.exists():
        models["regression"] = joblib.load(reg_path)
    else:
        models["regression"] = None
        
    # 3. Classification model
    clf_path = models_dir / "best_classification_model.pkl"
    if clf_path.exists():
        models["classification"] = joblib.load(clf_path)
    else:
        models["classification"] = None
        
    # 4. Scaler
    scaler_path = models_dir / "scaler.pkl"
    if scaler_path.exists():
        models["scaler"] = joblib.load(scaler_path)
    else:
        models["scaler"] = None

    # 5. Label Encoder
    encoder_path = models_dir / "label_encoder.pkl"
    if encoder_path.exists():
        models["label_encoder"] = joblib.load(encoder_path)
    else:
        models["label_encoder"] = None

    return models

def score_to_category(score: float) -> str:
    """Map numerical score to accessibility category."""
    if score >= 80:
        return "Excellent"
    elif score >= 65:
        return "Good"
    elif score >= 45:
        return "Fair"
    else:
        return "Poor"

def score_to_priority(score: float) -> str:
    """Map numerical score to improvement priority."""
    if score < 50:
        return "High"
    elif score < 75:
        return "Medium"
    else:
        return "Low"

def predict_accessibility(input_dict: dict):
    """Make accessibility predictions given an input feature dictionary."""
    models = load_ml_models()
    full_dict = compute_dict_features(input_dict)
    
    feature_cols = models.get("feature_columns")
    reg_model = models.get("regression")
    clf_model = models.get("classification")
    
    if feature_cols is None:
        # Fallback list if pickle missing
        feature_cols = [
            'Location_Type', 'City', 'State', 'Latitude', 'Longitude', 'Ownership_Type',
            'Building_Age_Years', 'Last_Renovation_Years_Ago', 'Number_of_Floors',
            'Ramp_Available', 'Elevator_Available', 'Wheelchair_Entrance', 'Braille_Signage',
            'Audio_Announcements', 'Accessible_Washroom', 'Tactile_Path', 'Reserved_Parking',
            'Door_Width_cm', 'Footpath_Condition', 'Lighting', 'Safety_Level', 'CCTV_Available',
            'Staff_Trained_Accessibility', 'Multilingual_Signage', 'Public_Transport_Nearby',
            'Parking_Available', 'Crowd_Level', 'Average_Waiting_Time', 'Daily_Footfall',
            'Staff_Count', 'Budget_Allocated_Lakh_INR', 'Complaint_Resolution_Days',
            'Accessibility_Complaints', 'User_Rating', 'Google_Maps_Rating',
            'Last_Inspection_Months', 'Lift_Condition', 'Emergency_Exit_Accessibility',
            'Infrastructure_Score', 'Accessibility_Support_Score', 'Safety_Index',
            'Facility_Score', 'Crowd_Risk', 'Complaint_Rate'
        ]

    # Create 1-row DataFrame aligned with feature columns
    row_data = {}
    for col in feature_cols:
        row_data[col] = full_dict.get(col, 0.0)
    input_df = pd.DataFrame([row_data])

    predicted_score = None
    predicted_category = None

    if reg_model is not None:
        try:
            val = reg_model.predict(input_df)[0]
            predicted_score = float(np.clip(val, 0.0, 100.0))
        except Exception:
            pass

    # Dynamic baseline score if model fails
    if predicted_score is None:
        base = (full_dict["Infrastructure_Score"] * 12 +
                full_dict["Accessibility_Support_Score"] * 10 +
                full_dict["Safety_Index"] * 5 +
                full_dict["Facility_Score"] * 5)
        predicted_score = float(np.clip(base + 15, 10.0, 98.0))

    if clf_model is not None:
        try:
            cat_val = clf_model.predict(input_df)[0]
            encoder = models.get("label_encoder")
            if encoder is not None and hasattr(encoder, "inverse_transform"):
                predicted_category = encoder.inverse_transform([cat_val])[0]
            else:
                predicted_category = str(cat_val)
        except Exception:
            pass

    if not predicted_category or predicted_category in ["0", "1", "2", "3"]:
        predicted_category = score_to_category(predicted_score)

    priority = score_to_priority(predicted_score)

    return {
        "score": round(predicted_score, 1),
        "category": predicted_category,
        "priority": priority,
        "features": full_dict
    }
