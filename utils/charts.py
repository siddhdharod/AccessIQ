import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
import logging

logger = logging.getLogger(__name__)

def get_theme_colors():
    """Return theme-aware color palette for Plotly charts."""
    theme = st.session_state.get("theme", "dark")
    if theme == "dark":
        return {
            "bg": "rgba(0,0,0,0)",
            "paper_bg": "rgba(0,0,0,0)",
            "text": "#F8FAFC",
            "grid": "rgba(49, 46, 129, 0.4)",
            "primary": "#8B5CF6",
            "accent": "#A78BFA",
            "colors": ["#8B5CF6", "#38BDF8", "#22C55E", "#F59E0B", "#EF4444", "#C084FC"]
        }
    else:
        return {
            "bg": "rgba(0,0,0,0)",
            "paper_bg": "rgba(0,0,0,0)",
            "text": "#1E1B4B",
            "grid": "rgba(233, 213, 255, 0.6)",
            "primary": "#7C3AED",
            "accent": "#A855F7",
            "colors": ["#7C3AED", "#2563EB", "#16A34A", "#D97706", "#DC2626", "#A855F7"]
        }

def apply_custom_chart_style(fig: go.Figure, title: str = None) -> go.Figure:
    """Apply consistent, premium SaaS styling to any Plotly figure.
    Uses only valid Plotly layout properties (bgcolor, bordercolor, borderwidth).
    """
    colors = get_theme_colors()

    fig.update_layout(
        paper_bgcolor=colors["paper_bg"],
        plot_bgcolor=colors["bg"],
        font=dict(
            family="Inter, Outfit, sans-serif",
            color=colors["text"],
            size=12
        ),
        title=dict(
            text=f"<b>{title}</b>" if title else "",
            font=dict(size=15, color=colors["text"], family="Poppins, sans-serif")
        ),
        margin=dict(l=30, r=30, t=50 if title else 25, b=30),
        # legend=dict(
        #     orientation="h",
        #     yanchor="bottom",
        #     y=1.02,
        #     xanchor="right",
        #     x=1,
        #     font=dict(size=11, color=colors["text"]),
        #     bgcolor="rgba(0,0,0,0)",       # correct Plotly property
        #     bordercolor="rgba(0,0,0,0)",   # correct Plotly property
        #     borderwidth=0                   # correct Plotly property
        # )
        legend=dict(
            orientation="h",
            bgcolor="rgba(255,255,255,0.8)",    # ✅ Correct
            x=1,
            y=1,
        )
    )
    fig.update_xaxes(showgrid=True, gridcolor=colors["grid"], gridwidth=1, zeroline=False)
    fig.update_yaxes(showgrid=True, gridcolor=colors["grid"], gridwidth=1, zeroline=False)
    return fig


def create_radar_comparison(df_locations: pd.DataFrame) -> go.Figure:
    """Create a multi-location comparison Radar Chart using Plotly with premium styling."""
    categories = [
        "Infrastructure",
        "Accessibility Support",
        "Safety Level",
        "Facility Support",
        "Crowd Comfort",
        "Overall Rating"
    ]

    fig = go.Figure()
    colors = get_theme_colors()

    for idx, row in df_locations.iterrows():
        loc_name = row.get("Location_Name", f"Location {idx}")

        try:
            infra = (float(row.get("Infrastructure_Score", 2)) / 5.0) * 100
        except Exception:
            infra = 50.0
        try:
            supp = (float(row.get("Accessibility_Support_Score", 1)) / 3.0) * 100
        except Exception:
            supp = 50.0
        try:
            safety = (float(row.get("Safety_Index", 2)) / 6.0) * 100
        except Exception:
            safety = 50.0
        try:
            fac = (float(row.get("Facility_Score", 1)) / 2.0) * 100
        except Exception:
            fac = 50.0
        try:
            crowd = max(0.0, 100.0 - (float(row.get("Average_Waiting_Time", 20)) * 2.0))
        except Exception:
            crowd = 50.0
        try:
            rating = (float(row.get("User_Rating", 3.0)) / 5.0) * 100
        except Exception:
            rating = 60.0

        values = [infra, supp, safety, fac, crowd, rating]
        values.append(values[0])  # close the polygon

        fig.add_trace(go.Scatterpolar(
            r=values,
            theta=categories + [categories[0]],
            fill='toself',
            name=str(loc_name)
        ))

    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 100],
                showticklabels=True,
                ticksuffix="%",
                gridcolor=colors["grid"]
            ),
            bgcolor="rgba(0,0,0,0)"
        )
    )
    return apply_custom_chart_style(fig, "Multi-Location Accessibility Comparison Radar")


def create_single_radar(input_features: dict) -> go.Figure:
    """Create a radar chart for a single location's feature profile."""
    categories = ['Infrastructure', 'Support', 'Safety', 'Facility', 'Rating', 'Low Crowd']
    colors = get_theme_colors()

    infra  = (float(input_features.get("Infrastructure_Score", 2)) / 5.0) * 100
    supp   = (float(input_features.get("Accessibility_Support_Score", 1)) / 3.0) * 100
    safe   = (float(input_features.get("Safety_Index", 2)) / 6.0) * 100
    fac    = (float(input_features.get("Facility_Score", 1)) / 2.0) * 100
    rating = (float(input_features.get("User_Rating", 3.0)) / 5.0) * 100
    crowd  = max(0.0, 100.0 - (float(input_features.get("Average_Waiting_Time", 20)) * 2.0))

    values = [infra, supp, safe, fac, rating, crowd]
    values.append(values[0])

    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=values,
        theta=categories + [categories[0]],
        fill='toself',
        fillcolor='rgba(139, 92, 246, 0.25)',
        line=dict(color=colors["primary"], width=2.5),
        name="Location Profile"
    ))
    fig.update_layout(
        polar=dict(
            radialaxis=dict(visible=True, range=[0, 100], gridcolor=colors["grid"]),
            bgcolor="rgba(0,0,0,0)"
        )
    )
    return apply_custom_chart_style(fig)


def create_confusion_matrix_chart(cm: np.ndarray, labels: list) -> go.Figure:
    """Generate confusion matrix heatmap."""
    fig = px.imshow(
        cm,
        x=labels,
        y=labels,
        color_continuous_scale="Purples" if st.session_state.get("theme", "dark") == "dark" else "Blues",
        text_auto=True
    )
    fig.update_layout(
        xaxis_title="Predicted Category",
        yaxis_title="True Category"
    )
    return apply_custom_chart_style(fig, "Classification Model Confusion Matrix")


def create_roc_curve_chart(fpr: dict, tpr: dict, roc_auc: dict) -> go.Figure:
    """Generate multi-class ROC Curve plot."""
    colors = get_theme_colors()
    fig = go.Figure()
    for i, cls in enumerate(fpr.keys()):
        fig.add_trace(go.Scatter(
            x=fpr[cls],
            y=tpr[cls],
            mode='lines',
            line=dict(color=colors["colors"][i % len(colors["colors"])], width=2),
            name=f'Class {cls} (AUC = {roc_auc[cls]:.2f})'
        ))
    fig.add_trace(go.Scatter(
        x=[0, 1], y=[0, 1],
        mode='lines',
        line=dict(dash='dash', color='gray'),
        name='Random Chance'
    ))
    fig.update_layout(
        xaxis_title="False Positive Rate",
        yaxis_title="True Positive Rate"
    )
    return apply_custom_chart_style(fig, "Receiver Operating Characteristic (ROC) Curve")


def create_feature_importance_chart(feature_names: list, importance_values, top_n: int = 15) -> go.Figure:
    """Generate horizontal bar chart of top N features.

    Defensively checks that feature_names and importance_values have matching
    lengths and logs a warning if they ever diverge (real mismatch should now
    be impossible after model retraining, but we keep this guard for safety).
    """
    colors = get_theme_colors()

    feat_list = list(feature_names)
    imp_list  = list(importance_values)

    if len(feat_list) != len(imp_list):
        logger.warning(
            "create_feature_importance_chart: length mismatch — "
            f"feature_names={len(feat_list)}, importance_values={len(imp_list)}. "
            "Truncating to minimum. Check model/feature_columns consistency."
        )
        min_len   = min(len(feat_list), len(imp_list))
        feat_list = feat_list[:min_len]
        imp_list  = imp_list[:min_len]

    df_imp = pd.DataFrame({
        "Feature": feat_list,
        "Importance": imp_list
    }).sort_values(by="Importance", ascending=True).tail(top_n)

    fig = px.bar(
        df_imp,
        x="Importance",
        y="Feature",
        orientation="h",
        color="Importance",
        color_continuous_scale="Purples" if st.session_state.get("theme", "dark") == "dark" else "Viridis"
    )
    fig.update_layout(height=450)
    return apply_custom_chart_style(fig, f"Top {len(df_imp)} Most Important Feature Columns")


def create_dimensionality_reduction_chart(X_proj: np.ndarray, labels: pd.Series, method_name: str = "PCA") -> go.Figure:
    """Generate 2D scatter plot for PCA / LDA / SVD projections."""
    colors = get_theme_colors()
    min_len = min(len(X_proj), len(labels))

    df_proj = pd.DataFrame({
        "Component 1": X_proj[:min_len, 0],
        "Component 2": X_proj[:min_len, 1],
        "Category":    list(labels)[:min_len]
    })
    fig = px.scatter(
        df_proj,
        x="Component 1",
        y="Component 2",
        color="Category",
        color_discrete_sequence=colors["colors"]
    )
    return apply_custom_chart_style(fig, f"2D Projection View via {method_name}")


def create_cluster_scatter_chart(df: pd.DataFrame, x_col: str, y_col: str, cluster_col: str = "Cluster") -> go.Figure:
    """Generate scatter plot for K-Means clustering results."""
    colors = get_theme_colors()
    hover_cols = [c for c in ["Location_Name", "Accessibility_Score"] if c in df.columns] or None
    fig = px.scatter(
        df,
        x=x_col,
        y=y_col,
        color=cluster_col,
        hover_data=hover_cols,
        color_discrete_sequence=colors["colors"]
    )
    return apply_custom_chart_style(fig, f"K-Means Clustering Analysis ({x_col} vs {y_col})")
