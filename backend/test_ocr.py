from ocr import extract_text

print("Running OCR...")

text = extract_text("test.jpg")

print("Extracted Text:")
print(text)