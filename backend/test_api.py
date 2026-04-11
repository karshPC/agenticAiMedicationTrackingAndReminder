import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

# Configure with your key
genai.configure(api_key="AIzaSyAyDSCa1alWbYwpZZlrPElJ_cCGYXQR2xI")

# List all models supported by the key
for m in genai.list_models():
    if 'generateContent' in m.supported_generation_methods:
        print(f"Model Name: {m.name}")
