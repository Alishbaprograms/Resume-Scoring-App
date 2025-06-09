import os
from docx2pdf import convert

def convert_docx_to_pdf(docx_path, output_dir):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    pdf_path = os.path.join(output_dir, os.path.splitext(os.path.basename(docx_path))[0] + ".pdf")
    convert(docx_path, pdf_path)
    return pdf_path
