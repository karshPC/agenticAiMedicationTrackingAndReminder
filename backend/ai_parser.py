import re

# ================= OCR PARSER (UNCHANGED BUT CLEANED) ================= #
def extract_medicines(text):

    lines = text.split("\n")
    medicines = []

    for line in lines:
        line = line.strip()

        if len(line) < 3:
            continue

        if any(word in line.lower() for word in ["tab", "cap", "mg", "drop"]):
            medicines.append({
                "name": line[:40],
                "dosage": line
            })

    return medicines[:5]


# ================= ACTION DETECTION ================= #
def detect_action(text):

    text = text.lower()

    if "add" in text:
        return "add"

    if "edit" in text or "update" in text:
        return "edit"

    if "delete" in text or "remove" in text:
        return "delete"

    return "unknown"


# ================= CHAT PARSER (NEW 🔥) ================= #
def parse_chat_query(text):

    text_lower = text.lower()
    words = text_lower.split()

    action = detect_action(text)

    # ---------- NAME ----------
    name = ""
    for i, w in enumerate(words):
        if w in ["add", "edit", "delete", "remove", "update"]:
            if i + 1 < len(words):
                name = words[i + 1]
                break

    # ---------- DOSAGE ----------
    dosage = "Not specified"

    dose_match = re.search(r'(\d+)\s*(dose|doses|times)', text_lower)
    if dose_match:
        dosage = f"{dose_match.group(1)} doses"

    # ---------- TIMES ----------
    times = []

    # Match formats like 09:00, 9:00
    time_matches = re.findall(r'\b\d{1,2}:\d{2}\b', text)
    times.extend(time_matches)

    # Match AM/PM formats like 9am, 2pm
    ampm_matches = re.findall(r'\b(\d{1,2})(am|pm)\b', text_lower)

    for t in ampm_matches:
        hour = int(t[0])
        if t[1] == "pm" and hour != 12:
            hour += 12
        if t[1] == "am" and hour == 12:
            hour = 0
        times.append(f"{hour:02d}:00")

    # Remove duplicates
    times = list(set(times))

    return {
        "action": action,
        "name": name,
        "dosage": dosage,
        "times": times
    }