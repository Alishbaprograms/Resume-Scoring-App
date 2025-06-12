from PyPDF2 import PdfMerger
import json, os
import re

def sanitize_filename(s):
    return re.sub(r'[\\/:"*?<>|]+', "", s)

def build_filename(data):
    name = data.get("Full Name", "Unknown")
    degree = data.get("Degree", "Unknown")
    major = data.get("Major", "Unknown")
    school = data.get("Latest University", "Unknown")
    grad = data.get("Graduation Date", "Unknown")
    score =data.get("Total Score", "Unknown")

    met = ""
    if data.get("Met on Campus", False):
        score = data.get("Campus Score", "Not Captured")
        met = f" – Met on Campus ({score})"

    cam_score = data.get("cam_score")
    score_str = f" – Score: {cam_score}" if cam_score else ""

    full_name = sanitize_filename(
        f"{name} – {degree}, {major} – {school} ({grad}){met}{score}"
    )
    return full_name


def bundle_pdf_and_json(split_pdf_path, json_path, final_output_dir):
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    filename = build_filename(data)
    pdf_output_path = os.path.join(final_output_dir, "final_pdfs", filename + ".pdf")
    json_output_path = os.path.join(final_output_dir, "jsons", filename + ".json")

    os.makedirs(os.path.dirname(pdf_output_path), exist_ok=True)
    os.makedirs(os.path.dirname(json_output_path), exist_ok=True)


    with open(json_output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

    merger = PdfMerger()
    merger.append(split_pdf_path)
    merger.write(pdf_output_path)
    merger.close()

    return pdf_output_path, json_output_path

