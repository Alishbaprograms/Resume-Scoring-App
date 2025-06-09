import zipfile
import os

def extract_zip(file_path, temp_dir):
    extracted_files = []
    with zipfile.ZipFile(file_path, 'r') as zip_ref:
        zip_ref.extractall(temp_dir)
        for root, dirs, files in os.walk(temp_dir):
            for name in files:
                extracted_files.append(os.path.join(root, name))
    return extracted_files
