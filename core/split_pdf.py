from PyPDF2 import PdfReader, PdfWriter
from pathlib import Path
import os

def split_pdf_by_groups(pdf_path, groups, output_dir):
    os.makedirs(output_dir, exist_ok=True)
    reader = PdfReader(pdf_path)
    output_paths = []

    for idx, page_group in enumerate(groups):
        writer = PdfWriter()
        for p in page_group:
            writer.add_page(reader.pages[p])

        out_file = os.path.join(output_dir, f"{Path(pdf_path).stem}{idx+1}.pdf")
        with open(out_file, "wb") as f:
            writer.write(f)
        output_paths.append(out_file)

    return output_paths
