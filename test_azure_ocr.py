from core.azure_ocr import extract_text_with_azure
import os

pdf_path = "temp/preprocessed/Comp. Sci. Intern.pdf"
output_path = "temp/raw_texts/sample_resume.txt"

os.makedirs(os.path.dirname(output_path), exist_ok=True)

text = extract_text_with_azure(pdf_path, output_path)
print("Azure OCR extracted text saved to:", output_path)

