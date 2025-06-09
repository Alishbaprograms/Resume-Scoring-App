import re

def sanitize_filename(s):
    return re.sub(r'[\\/:"*?<>|]+', "", s)

def build_filename(data):
    name = f"{data.get('Full Name', 'Unknown')}"
    degree = f"{data.get('Degree', 'Unknown')}"
    major = f"{data.get('Major', 'Unknown')}"
    school = f"{data.get('Latest University', 'Unknown')}"
    grad = f"{data.get('Graduation Date', 'Unknown')}"

    met = ""
    if data.get("Met on Campus", False):
        score = data.get("Campus Score", "Not Captured")
        met = f" – Met on Campus ({score})"

    full_name = sanitize_filename(f"{name} – {degree}, {major} – {school} ({grad}){met}")
    return full_name
