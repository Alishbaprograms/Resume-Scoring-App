# test_preprocessor.py
from core.preprocessor import preprocess_file
import os

input_path = "samples/sample_input_folder"
output_path = "temp/preprocessed"

all_results = []

for file in os.listdir(input_path):
    full = os.path.join(input_path, file)
    print(f"Processing: {file}")
    results = preprocess_file(full, output_path)
    all_results.extend(results)

print("\n Final standardized output:")
for r in all_results:
    print("→", r)
