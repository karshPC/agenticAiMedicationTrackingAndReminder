import re

def extract_medicines(text):

    lines = text.split("\n")

    medicines = []
    i = 0

    while i < len(lines):

        line = lines[i].strip()

        if re.match(r'^\d+\.', line):

            name = re.sub(r'^\d+\.\s*', '', line)
            name = re.sub(r'[^a-zA-Z0-9\s\-\+]', '', name).strip()

            dosage = "Not specified"

            for j in range(i+1, min(i+6, len(lines))):
                next_line = lines[j].strip().lower()

                if any(word in next_line for word in [
                    "day", "times", "daily", "bed time", "once", "twice", "drop", "tablet"
                ]):
                    dosage = lines[j].strip()
                    break

            medicines.append({
                "name": name,
                "dosage": dosage
            })

        i += 1

    return medicines