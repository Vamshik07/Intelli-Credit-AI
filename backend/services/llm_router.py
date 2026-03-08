import os

from dotenv import load_dotenv
from groq import Groq
import google.generativeai as genai


load_dotenv()


def _gemini_call(prompt: str) -> str:
    api_key = os.getenv("GEMINI_API_KEY", "")
    if not api_key:
        return ""

    try:
        genai.configure(api_key=api_key)
        for model_name in ("gemini-2.5-flash-lite", "gemini-1.5-flash"):
            try:
                model = genai.GenerativeModel(model_name)
                response = model.generate_content(prompt)
                text = (response.text or "").strip()
                if text:
                    return text
            except Exception:
                continue
    except Exception:
        return ""

    return ""


def _groq_call(prompt: str) -> str:
    api_key = os.getenv("GROQ_API_KEY", "")
    if not api_key:
        return ""

    try:
        client = Groq(api_key=api_key)
        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
        )
        return (completion.choices[0].message.content or "").strip()
    except Exception:
        return ""


def route_llm(task_type: str, prompt: str) -> str:
    gemini_tasks = {"research", "regulatory", "news_summary"}
    if task_type in gemini_tasks:
        return _gemini_call(prompt) or _groq_call(prompt) or "LLM unavailable"

    return _groq_call(prompt) or _gemini_call(prompt) or "LLM unavailable"
