from ocr import extract_text
from ai_parser import extract_medicines

text = extract_text("test.jpg")

print("RAW TEXT:\n", text)

print("\nAI OUTPUT:\n")
print(extract_medicines(text))