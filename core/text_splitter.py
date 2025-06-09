
import os
import pdfplumber
from pathlib import Path

def extract_text_per_page(pdf_path, output_dir):
    os.makedirs(output_dir, exist_ok=True)
    page_texts = []

    with pdfplumber.open(pdf_path) as pdf:
        for i, page in enumerate(pdf.pages):
            text = page.extract_text() or ""
            page_texts.append(text)
            fname = f"{Path(pdf_path).stem}{i+1}.txt"
            with open(os.path.join(output_dir, fname), "w", encoding="utf-8") as f:
                f.write(text)

    return page_texts
