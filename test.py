from core.zip_handler import extract_zip
from core.doc_converter import convert_docx_to_pdf
import os

if __name__ == "__main__":
    temp_dir = "temp/extracted_files"
    os.makedirs(temp_dir, exist_ok=True)

    zip_files = extract_zip("Sample Files.zip", temp_dir)
    print("Unzipped Files:", zip_files)

    for file in zip_files:
        if file.endswith(".docx"):
            pdf_path = convert_docx_to_pdf(file, temp_dir)
            print("Converted to PDF:", pdf_path)
