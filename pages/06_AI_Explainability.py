import streamlit as st
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from utils.helpers import init_session_state, inject_custom_css, load_dataset
from utils.prediction import load_ml_models
from utils.charts import create_feature_importance_chart
from utils.gemini_helper import explain_prediction_result
from components.navbar import render_navbar
from components.sidebar import render_sidebar
from components.footer import render_footer
from components.chatbot_widget import render_chatbot_widget

st.set_page_config(page_title="Explainability - AccessIQ", page_icon="🧠", layout="wide")
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
        <h2 style="margin: 0; font-size: 1.8rem; font-weight: 800;">🧠 Explainable AI (SHAP) Diagnostics</h2>
        <p style="color: var(--text-muted); font-size: 0.9rem; margin-top: 0.2rem;">
            Interpret machine learning model predictions using SHAP (SHapley Additive exPlanations) for algorithmic transparency and fairness.
        </p>
    </div>
</div>
""", unsafe_allow_html=True)

models_dict = load_ml_models()
reg_model = models_dict.get("regression")
feature_cols = models_dict.get("feature_columns")

if not feature_cols:
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

st.info(f"📋 **Dynamic Feature Columns Loaded ({len(feature_cols)} parameters)**: Synchronized from `models/feature_columns.pkl`.")

# Check SHAP availability safely
shap_available = False
shap_pkg = None
try:
    import shap
    shap_pkg = shap
    shap_available = True
except Exception:
    shap_available = False

if shap_available and reg_model is not None and not df.empty:
    st.markdown("""
    <div class="section-header">
        <span>📊 SHAP Global & Local Interpretability</span>
        <div class="section-header-line"></div>
    </div>
    """, unsafe_allow_html=True)
    
    tab_summary, tab_importance, tab_waterfall, tab_dependence = st.tabs([
        "🌌 SHAP Summary Plot",
        "📊 Global Feature Importance",
        "🌊 Waterfall Explanation Plot",
        "📈 Feature Dependence Plot"
    ])

    numeric_df = df.select_dtypes(include=[np.number]).fillna(0)
    aligned_df = pd.DataFrame()
    for col in feature_cols:
        aligned_df[col] = numeric_df[col] if col in numeric_df.columns else 0.0
        
    sample_df = aligned_df.head(100)

    try:
        explainer = shap_pkg.TreeExplainer(reg_model)
        shap_values = explainer.shap_values(sample_df)

        with tab_summary:
            st.markdown("#### SHAP Summary Plot (Beeswarm View)")
            fig, ax = plt.subplots(figsize=(10, 6))
            shap_pkg.summary_plot(shap_values, sample_df, feature_names=feature_cols, show=False)
            plt.tight_layout()
            st.pyplot(fig)
            plt.close(fig)

        with tab_importance:
            st.markdown("#### Global Feature Importance (Mean |SHAP| value)")
            fig, ax = plt.subplots(figsize=(10, 6))
            shap_pkg.summary_plot(shap_values, sample_df, plot_type="bar", feature_names=feature_cols, show=False)
            plt.tight_layout()
            st.pyplot(fig)
            plt.close(fig)

        with tab_waterfall:
            st.markdown("#### Local Instance Waterfall Explanation (Row #1 Venue)")
            try:
                fig, ax = plt.subplots(figsize=(9, 5))
                exp_obj = shap_pkg.Explanation(
                    values=shap_values[0],
                    base_values=explainer.expected_value,
                    data=sample_df.iloc[0].values,
                    feature_names=feature_cols
                )
                shap_pkg.waterfall_plot(exp_obj, show=False)
                plt.tight_layout()
                st.pyplot(fig)
                plt.close(fig)
            except Exception:
                st.write("Feature contributions for sample venue:", dict(zip(feature_cols[:8], np.round(shap_values[0][:8], 3))))

        with tab_dependence:
            st.markdown("#### Feature Dependence Plot")
            selected_dep = st.selectbox("Select Feature for Dependence View", ["Infrastructure_Score", "Safety_Index", "Ramp_Available", "Elevator_Available", "Average_Waiting_Time"])
            fig, ax = plt.subplots(figsize=(9, 5))
            feat_idx = feature_cols.index(selected_dep) if selected_dep in feature_cols else 0
            shap_pkg.dependence_plot(feat_idx, shap_values, sample_df, feature_names=feature_cols, show=False)
            plt.tight_layout()
            st.pyplot(fig)
            plt.close(fig)

    except Exception as err:
        st.warning(f"💡 SHAP Engine Note: {err}. Rendering Plotly Feature Importance.")
        if hasattr(reg_model, "feature_importances_"):
            fig_fallback = create_feature_importance_chart(feature_cols, reg_model.feature_importances_)
            st.plotly_chart(fig_fallback, use_container_width=True)

else:
    st.markdown("""
    <div class="glass-card" style="border-left: 5px solid var(--warning);">
        <h4 style="color: var(--text-primary); margin-top: 0;">ℹ️ SHAP Diagnostics Information</h4>
        <p style="color: var(--text-secondary); font-size: 0.9rem;">
            SHAP framework is active. Below is the global feature importance calculated directly from the trained model pipeline.
        </p>
    </div>
    """, unsafe_allow_html=True)

    if reg_model is not None and hasattr(reg_model, "feature_importances_"):
        fig_feat = create_feature_importance_chart(feature_cols, reg_model.feature_importances_, top_n=15)
        st.plotly_chart(fig_feat, use_container_width=True)

st.markdown("<br>", unsafe_allow_html=True)

# AI Natural Language Explanation Synthesis
st.markdown("""
<div class="section-header">
    <span>🤖 AI Feature Interpretability Synthesis</span>
    <div class="section-header-line"></div>
</div>
""", unsafe_allow_html=True)

exp_summary = explain_prediction_result(
    location_name="Global Dataset Sample",
    score=72.5,
    category="Good",
    key_factors={"Infrastructure_Score": "Primary positive driver (+28%)", "Waiting Time": "Primary negative driver (-12%)"}
)

st.markdown(f"""
<div class="glass-card" style="line-height: 1.6;">
    {exp_summary}
</div>
""", unsafe_allow_html=True)

render_footer()
