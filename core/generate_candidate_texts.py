import os

def merge_texts_for_split_pdfs(pdf_stem, page_groups, page_text_dir, output_dir):
    os.makedirs(output_dir, exist_ok=True)
    for idx, group in enumerate(page_groups):
        merged = ""
        for i in group:
            page_file = f"{pdf_stem}{i+1}.txt"
            page_path = os.path.join(page_text_dir, page_file)
            if os.path.exists(page_path):
                with open(page_path, "r", encoding="utf-8") as f:
                    merged += f"\n--- Page {i+1} ---\n" + f.read()
        out_file = os.path.join(output_dir, f"{pdf_stem}{idx+1}.txt")
        with open(out_file, "w", encoding="utf-8") as f:
            f.write(merged)
