import os

def merge_texts_for_split_pdfs(pdf_stem, page_groups, page_text_dir, output_dir):
    os.makedirs(output_dir, exist_ok=True)

    # Only one merged file per pdf_stem now
    page_file = f"{pdf_stem}.txt"
    page_path = os.path.join(page_text_dir, page_file)

    if not os.path.exists(page_path):
        return  # Nothing to do

    with open(page_path, "r", encoding="utf-8") as f:
        merged_text = f.read()

    out_file = os.path.join(output_dir, f"{pdf_stem}.txt")
    with open(out_file, "w", encoding="utf-8") as f:
        f.write(merged_text)

