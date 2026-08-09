import os
import requests
import streamlit as st


def get_gemini_api_key() -> str | None:
    """Retrieve Gemini API Key safely from Streamlit secrets (st.secrets["GEMINI_API_KEY"])
    or environment variables. Never raises — returns None on any failure.
    """
    try:
        if hasattr(st, "secrets") and "GEMINI_API_KEY" in st.secrets:
            key = str(st.secrets["GEMINI_API_KEY"]).strip()
            if key:
                return key
    except Exception:
        pass

    try:
        key = os.getenv("GEMINI_API_KEY", "").strip()
        if key:
            return key
    except Exception:
        pass

    return None


def call_gemini(prompt: str) -> str:
    """Call Google Gemini API via REST endpoint with fallback handling."""
    api_key = get_gemini_api_key()
    if not api_key:
        return (
            "⚠️ Gemini API key is missing. "
            "Set GEMINI_API_KEY in your .env file to enable AI-powered features."
        )

    url = (
        f"https://generativelanguage.googleapis.com/v1beta/models/"
        f"gemini-2.5-flash:generateContent?key={api_key}"
    )
    headers = {"Content-Type": "application/json"}
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"temperature": 0.4, "maxOutputTokens": 800},
    }

    try:
        response = requests.post(url, json=payload, headers=headers, timeout=12)
        if response.status_code == 200:
            data = response.json()
            candidates = data.get("candidates", [])
            if candidates:
                parts = candidates[0].get("content", {}).get("parts", [])
                if parts:
                    return parts[0].get("text", "").strip()

        elif response.status_code == 404:
            # Fallback to gemini-1.5-flash if 2.5 not available in region
            fallback_url = (
                f"https://generativelanguage.googleapis.com/v1beta/models/"
                f"gemini-1.5-flash:generateContent?key={api_key}"
            )
            resp2 = requests.post(fallback_url, json=payload, headers=headers, timeout=12)
            if resp2.status_code == 200:
                data2 = resp2.json()
                cands2 = data2.get("candidates", [])
                if cands2:
                    parts2 = cands2[0].get("content", {}).get("parts", [])
                    if parts2:
                        return parts2[0].get("text", "").strip()

        return f"💡 AI Insight: Standard recommendations applied. (HTTP {response.status_code})"

    except Exception as e:
        return f"💡 AI Insight: Standard accessibility recommendations generated. ({e})"


# ── Domain-specific helpers ──────────────────────────────────────────────────

def get_accessibility_suggestions(location_name: str, score: float, category: str, missing_features: list) -> str:
    features_str = ", ".join(missing_features) if missing_features else "general infrastructure upgrades"
    prompt = f"""
    You are an expert AI Accessibility Consultant.
    Location Name: {location_name}
    Current Accessibility Score: {score}/100 ({category})
    Missing/Sub-optimal Infrastructure: {features_str}

    Provide 3 concise, highly actionable, cost-effective infrastructure recommendations to improve
    accessibility for disabled citizens, elderly, and parents with strollers. Keep under 150 words.
    """
    return call_gemini(prompt)


def explain_prediction_result(location_name: str, score: float, category: str, key_factors: dict) -> str:
    factors_str = ", ".join([f"{k}: {v}" for k, v in key_factors.items()])
    prompt = f"""
    You are an AI Machine Learning Specialist explaining an Accessibility Score prediction model.
    Location: {location_name}
    Predicted Score: {score}/100
    Category: {category}
    Key Influencing Factors: {factors_str}

    Explain why the model assigned this score and what specific parameters contributed most
    positively or negatively. Keep it readable and professional.
    """
    return call_gemini(prompt)


def get_personalized_recommendation_reason(location_name: str, persona: str, score: float) -> str:
    prompt = f"""
    Explain in 2 sentences why {location_name} (Accessibility Score: {score}/100) is suitable or
    ideal for a {persona}. Highlight relevant features (ramps, Braille, elevators, quietness, wide doors).
    """
    return call_gemini(prompt)


def generate_pdf_summary(location_name: str, score: float, category: str, city: str) -> str:
    prompt = f"""
    Write a 3-sentence executive summary for an official Urban Infrastructure Accessibility Audit Report.
    Location: {location_name}, {city}
    Overall Accessibility Score: {score}/100
    Classification: {category}
    Summarize key strengths, audit findings, and urgent improvement priorities.
    """
    return call_gemini(prompt)


def chat_with_accessibility_bot(user_query: str, persona: str = "General User") -> str:
    prompt = f"""
    You are AccessIQ Assistant, an empathetic and knowledgeable AI chatbot for public accessibility,
    universal design (ADA/RPWD Act guidelines), and urban mobility.
    User Persona context: {persona}
    User Question: "{user_query}"

    Provide a helpful, friendly, and accurate response in 3-4 bullet points or short paragraphs.
    """
    return call_gemini(prompt)
