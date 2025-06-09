from core.final_bundler import bundle_pdf_and_json
import os

split_dir = "temp/resume_splits"
json_dir = "output/jsons"
final_dir = "output"


for file in os.listdir(split_dir):
    if file.endswith(".pdf"):
        pdf_path = os.path.join(split_dir, file)
        json_name = file.replace(".pdf", ".json")
        json_path = os.path.join(json_dir, json_name)

        if os.path.exists(json_path):
            pdf_out, json_out = bundle_pdf_and_json(pdf_path, json_path, final_dir)
            print(" Saved:", pdf_out)
        else:
            print(" JSON missing for:", file)
