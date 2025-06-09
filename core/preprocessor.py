
import os
from pathlib import Path
from shutil import copyfile

from core.zip_handler import extract_zip
from core.doc_converter import convert_docx_to_pdf
from core.email_parser import process_eml_file, process_msg_file

SUPPORTED = [".pdf", ".docx", ".zip", ".eml", ".msg"]

def preprocess_file(file_path, output_dir):
    os.makedirs(output_dir, exist_ok=True)
    file_path = Path(file_path)
    ext = file_path.suffix.lower()

    result_pdfs = []

    if ext == ".zip":
        extracted = extract_zip(str(file_path), os.path.join(output_dir, "unzipped"))
        for inner_file in extracted:
            result_pdfs += preprocess_file(inner_file, output_dir)

    elif ext == ".docx":
        try:
            pdf = convert_docx_to_pdf(str(file_path), output_dir)
            result_pdfs.append(pdf)
        except Exception as e:
            print(f" Failed to convert DOCX: {file_path.name} — {e}")

    elif ext == ".eml":
        body_txt, attachments = process_eml_file(str(file_path), output_dir)
        result_pdfs.append(body_txt)
        for att in attachments:
            result_pdfs += preprocess_file(att, output_dir)

    elif ext == ".msg":
        body_txt, attachments = process_msg_file(str(file_path), output_dir)
        result_pdfs.append(body_txt)
        for att in attachments:
            result_pdfs += preprocess_file(att, output_dir)

    elif ext == ".pdf":
        target = os.path.join(output_dir, file_path.name)
        copyfile(file_path, target)
        result_pdfs.append(target)

    else:
        print(f"Skipping unsupported file: {file_path}")

    return result_pdfs
