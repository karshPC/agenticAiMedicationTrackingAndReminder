import os
from google import genai

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))


def extract_medicines_llm(text):

    prompt = f"""
You are an expert medical prescription analyzer.

Extract medicines ONLY.

Return STRICT JSON:

[
  {{
    "name": "medicine name",
    "dosage": "dosage instruction"
  }}
]

Rules:
- Max 8 medicines
- Ignore hospital text, emails, numbers, addresses
- Ignore broken OCR words
- Medicine names are usually capitalized or look like drugs
- Dosage includes: tablet, drops, once, twice, daily, etc.
- If text is unclear → SKIP
- DO NOT hallucinate

TEXT:
{text}
"""

    # 🔥 SAFE MODEL LIST (HIGH → LOW PRIORITY)
    models_to_try = [
        "models/gemini-3.1-flash-lite-preview",  # 🔥 MAIN (500/day)
        "models/gemini-2.5-flash",               # backup
        "models/gemini-2.5-flash-lite"           # backup
    ]

    last_error = None

    for model in models_to_try:
        try:
            response = client.models.generate_content(
                model=model,
                contents=prompt
            )

            print(f"✅ OCR USED MODEL: {model}")

            result = response.text.strip()

            # 🔥 CLEAN MARKDOWN IF ANY
            if result.startswith("```"):
                result = result.replace("```json", "").replace("```", "").strip()

            return result

        except Exception as e:
            print(f"❌ OCR MODEL FAILED: {model} → {e}")
            last_error = e

    raise Exception(f"All OCR models failed: {last_error}")