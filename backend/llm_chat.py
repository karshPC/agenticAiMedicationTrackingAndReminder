from google import genai
import os

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))


def llm_chat_response(query, meds):

    prompt = f"""
You are a medical assistant.

User medications:
{meds}

User query:
{query}

Respond ONLY in JSON format like:
{{
  "action": "add/edit/delete/none",
  "name": "",
  "dosage": "",
  "times": [],
  "response": ""
}}
"""

    models_to_try = [
        "models/gemini-2.5-flash",               # ✅ 20/day
        "models/gemini-2.5-flash-lite"           # ✅ 20/day
        "models/gemini-3.1-flash-lite-preview",  # ✅ correct one (500/day)
    ]

    last_error = None

    for model in models_to_try:
        try:
            response = client.models.generate_content(
                model=model,
                contents=prompt
            )

            print(f"✅ USED MODEL: {model}")
            print(f"🔁 TRYING MODEL: {model}")

            if not response.text:
                raise Exception("Empty LLM response")

            return response.text.strip()

        except Exception as e:
            print(f"❌ MODEL FAILED: {model} → {e}")
            last_error = e

    raise Exception(f"All models failed: {last_error}")


