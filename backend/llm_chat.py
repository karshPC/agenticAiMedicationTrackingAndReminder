from google import genai
import os

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

def llm_chat_response(query, meds, history=""):

    prompt = f"""
You are a medical assistant.

Conversation history:
{history}

User medications:
{meds}

User query:
{query}

IMPORTANT:
- Understand context (like "one more", "that medicine", etc.)
- Use previous conversation when needed

Respond ONLY JSON:
{{
  "action": "add/edit/delete/none",
  "name": "",
  "dosage": "",
  "times": [],
  "response": ""
}}
"""

    models_to_try = [
        "models/gemini-3.1-flash-lite-preview",
        "models/gemini-2.5-flash",
        "models/gemini-2.5-flash-lite"
    ]

    for model in models_to_try:
        try:
            response = client.models.generate_content(
                model=model,
                contents=prompt
            )
            return response.text

        except Exception as e:
            print(f"❌ MODEL FAILED: {model} → {e}")

    return None
    prompt = f"""
You are a smart medical assistant.

Conversation history:
{history}

User medications:
{meds}

User query:
{query}

Respond ONLY in JSON:
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


