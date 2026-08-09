import os
import requests
import streamlit as st
from utils.gemini_helper import call_gemini


def get_groq_api_key() -> str | None:
    """Retrieve Groq API Key safely from Streamlit secrets (st.secrets["GROQ_API_KEY"])
    or environment variables. Never raises — returns None on any failure.
    """
    try:
        if hasattr(st, "secrets") and "GROQ_API_KEY" in st.secrets:
            key = str(st.secrets["GROQ_API_KEY"]).strip()
            if key:
                return key
    except Exception:
        pass

    try:
        key = os.getenv("GROQ_API_KEY", "").strip()
        if key:
            return key
    except Exception:
        pass

    return None


SYSTEM_PROMPT = """
You are AccessIQ AI, an empathetic, highly knowledgeable Senior AI Assistant and Urban Accessibility
Specialist for the AccessIQ Platform.

Your Core Capabilities:
1. Public Accessibility & Universal Design: ADA, RPWD Act 2016 (India), ISO accessibility standards,
   wheelchair ramp slopes (1:12 standard), tactile paving (warning vs directional), Braille signage
   specs, accessible washroom ergonomics.
2. AccessIQ Platform Knowledge: Explaining the 44 feature parameters, ML models (RandomForest dual
   regressor/classifier), persona scoring, SHAP explainability, OpenWeather live risk radar, and PDF
   report generation.
3. AI Recommendations & Predictions: Explaining accessibility scores (0-100), categories (Excellent,
   Good, Average, Poor), and urban mobility improvement priorities.
4. Smart City Awareness: Advising city planners, municipal officials, citizens, and advocates on
   building inclusive public infrastructure.
5. Smart Accessibility Booking: Explaining slot reservations for Wheelchairs (slots W01–W20) and Accessible Parking
   (slots P01–P30) across dataset locations. Rates in INR (₹): Wheelchair 30m ₹30 to Full Day ₹600; Parking 30m ₹20
   to Full Day ₹450. Explaining login requirement, real-time slot availability, overlap protection, QR gate passes,
   downloadable PDF receipts, and immediate cancellation slot release.

Tone & Style:
- Professional, empathetic, clear, and actionable.
- Format responses cleanly with Markdown (bullet points, bold key terms, concise paragraphs).
- Keep responses concise (under 250 words) unless asked to elaborate.
"""


def query_groq_chatbot(messages_history: list, persona: str = "Wheelchair User") -> str:
    """Query Groq API (LLaMA-3.3-70b) with automatic Gemini AI fallback.

    Always returns a user-facing string — never raises.
    """
    try:
        groq_key = get_groq_api_key()

        if not groq_key:
            # No Groq key — fall through to Gemini
            return _gemini_fallback(messages_history, persona)

        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {groq_key}",
            "Content-Type": "application/json",
        }

        formatted_messages = [
            {"role": "system", "content": f"{SYSTEM_PROMPT}\nCurrent Active Persona: {persona}"}
        ]
        for msg in messages_history[-8:]:
            role = "assistant" if msg.get("role") in ["assistant", "bot"] else "user"
            formatted_messages.append({"role": role, "content": msg.get("content", "")})

        payload = {
            "model": "llama-3.3-70b-versatile",
            "messages": formatted_messages,
            "temperature": 0.5,
            "max_tokens": 400,
        }

        response = requests.post(url, json=payload, headers=headers, timeout=10)

        if response.status_code == 200:
            choices = response.json().get("choices", [])
            if choices:
                return choices[0].get("message", {}).get("content", "").strip()

        # Groq returned non-200 — try the lighter model once
        if response.status_code in [400, 404, 429]:
            payload["model"] = "llama-3.1-8b-instant"
            resp2 = requests.post(url, json=payload, headers=headers, timeout=10)
            if resp2.status_code == 200:
                choices2 = resp2.json().get("choices", [])
                if choices2:
                    return choices2[0].get("message", {}).get("content", "").strip()

        # Both Groq models failed — fall back to Gemini
        return _gemini_fallback(messages_history, persona)

    except Exception:
        return _gemini_fallback(messages_history, persona)


def _gemini_fallback(messages_history: list, persona: str) -> str:
    """Extract last user message and call Gemini as a fallback. Never raises."""
    try:
        last_user_msg = ""
        for m in reversed(messages_history):
            if m.get("role") == "user":
                last_user_msg = m.get("content", "")
                break
        if not last_user_msg:
            return (
                "Hello! I am AccessIQ AI Assistant. "
                "How can I help you with public venue accessibility or urban mobility today?"
            )
        prompt = f"{SYSTEM_PROMPT}\n\nUser Persona Context: {persona}\nUser Query: {last_user_msg}"
        return call_gemini(prompt)
    except Exception as e:
        return f"⚠️ AI Assistant temporarily unavailable. Please try again. ({e})"
