import os
import json
from scoring_engine import load_cam_weights, score_resume

txt_dir = "temp/raw_texts_per_page"
json_dir = "output/jsons"
weights = load_cam_weights()

for filename in os.listdir(txt_dir):
    if filename.endswith(".txt"):
        name_stem = filename.replace(".txt", "")
        txt_path = os.path.join(txt_dir, filename)
        json_path = os.path.join(json_dir, name_stem + ".json")

        if not os.path.exists(json_path):
            print(" Missing JSON for:", filename)
            continue

        with open(txt_path, "r", encoding="utf-8") as f:
            text = f.read()

        score = score_resume(text, weights)

        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        data["cam_score"] = score

        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

        print(f"Scored {filename} → {score}")
