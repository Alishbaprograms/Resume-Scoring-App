from core.text_splitter import extract_text_per_page
from core.resume_split_logic import group_resume_pages
from core.split_pdf import split_pdf_by_groups

import os

input_pdf = "temp/preprocessed/DigitalBulkResumes.pdf"
text_dir = "temp/raw_texts_per_page"
output_dir = "temp/resume_splits"

# 1. Extract per-page text
pages = extract_text_per_page(input_pdf, text_dir)

# 2. Detect groups
groups = group_resume_pages(pages)
print("Detected Groups:", groups)

# 3. Split actual PDF
splits = split_pdf_by_groups(input_pdf, groups, output_dir)
print("Split Files:", splits)
