from core.ai_extractor import extract_fields_from_text
import os, json

input_dir = "temp/raw_texts_per_page"
output_dir = "output/jsons"
os.makedirs(output_dir, exist_ok=True)

for filename in os.listdir(input_dir):
    if filename.endswith(".txt"):
        path = os.path.join(input_dir, filename)
        with open(path, "r", encoding="utf-8") as f:
            text = f.read()

        # Use the exact filename, just change extension to .json
        json_filename = filename.replace(".txt", ".json")
        out_path = os.path.join(output_dir, json_filename)

        result = extract_fields_from_text(text)

        with open(out_path, "w", encoding="utf-8") as out_file:
            json.dump(result, out_file, indent=2)

        print(f"Extracted fields saved to: {out_path}")
