import os

import google.generativeai as genai

try:
    from dotenv import load_dotenv

    load_dotenv()
except Exception:
    # Environment loading is optional; fallback to system env vars.
    pass


def generate_underwriting_summary(company, financials, risk_level, explanation, recommendation):
    """Generate an optional AI summary using Gemini when GEMINI_API_KEY is configured."""
    api_key = os.getenv("GEMINI_API_KEY", "").strip()
    if not api_key:
        return "AI summary unavailable: GEMINI_API_KEY not configured."

    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-2.5-flash-lite")
        prompt = (
            "You are a senior credit analyst. Provide a concise appraisal summary.\n"
            f"Company: {company}\n"
            f"Financials: {financials}\n"
            f"Risk Level: {risk_level}\n"
            f"Explanation: {explanation}\n"
            f"Recommendation: {recommendation}\n"
            "Return 5 short bullet points with risk, strengths, red flags, covenants, and next steps."
        )
        response = model.generate_content(prompt)
        return (response.text or "AI summary unavailable").strip()
    except Exception:
        return "AI summary unavailable: model call failed."
