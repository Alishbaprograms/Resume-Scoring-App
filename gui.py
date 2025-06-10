# gui.py
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QVBoxLayout, QHBoxLayout, QPushButton, QFileDialog,
    QListWidget, QListWidgetItem, QLineEdit, QTextEdit, QProgressBar, QMessageBox
)
from PyQt5.QtCore import Qt
import sys, os
from core.preprocessor import preprocess_file  # assuming you save it in core/preprocessor.py
import temp
from core.text_splitter import extract_text_per_page
from core.resume_split_logic import group_resume_pages
from core.split_pdf import split_pdf_by_groups
from core.azure_ocr import extract_text_with_azure
from core.generate_candidate_texts import merge_texts_for_split_pdfs  
from core.ai_extractor import extract_fields_from_text
import json
from core.final_bundler import bundle_pdf_and_json








class ResumeProcessorGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("The Team")
        self.resize(800, 600)

        self.selected_files = []
        self.pdf_output = ""
        self.json_output = ""

        layout = QVBoxLayout()

        # Output Directories
        layout.addWidget(QLabel("Output Directories"))

        self.pdf_output_field = QLineEdit()
        self.pdf_output_field.setReadOnly(True)
        self.pdf_browse_btn = QPushButton("Browse...")
        self.pdf_browse_btn.clicked.connect(lambda: self.select_folder("pdf"))
        pdf_layout = QHBoxLayout()
        pdf_layout.addWidget(QLabel("PDF Output:"))
        pdf_layout.addWidget(self.pdf_output_field)
        pdf_layout.addWidget(self.pdf_browse_btn)
        layout.addLayout(pdf_layout)

        self.json_output_field = QLineEdit()
        self.json_output_field.setReadOnly(True)
        self.json_browse_btn = QPushButton("Browse...")
        self.json_browse_btn.clicked.connect(lambda: self.select_folder("json"))
        json_layout = QHBoxLayout()
        json_layout.addWidget(QLabel("JSON Output:"))
        json_layout.addWidget(self.json_output_field)
        json_layout.addWidget(self.json_browse_btn)
        layout.addLayout(json_layout)

        # External Dependency Status
        layout.addWidget(QLabel("External Dependencies Status"))
        self.status_label = QLabel("Azure DI:  Connected\nAzure Handwriting:  Not Connected\nAzure Vision: Connected\nOpenAI GPT:  Connected")
        layout.addWidget(self.status_label)
        self.refresh_btn = QPushButton("Refresh API Status")
        layout.addWidget(self.refresh_btn)

        # File List + Add/Remove/Clear
        layout.addWidget(QLabel("Select Input Files (Drag & Drop or Add)"))

        self.file_list = QListWidget()
        layout.addWidget(self.file_list)

        btn_row = QHBoxLayout()
        self.add_btn = QPushButton("Add Files...")
        self.add_btn.clicked.connect(self.add_files)
        self.remove_btn = QPushButton("Remove Selected")
        self.remove_btn.clicked.connect(self.remove_selected)
        self.clear_btn = QPushButton("Clear All")
        self.clear_btn.clicked.connect(self.clear_all)
        btn_row.addWidget(self.add_btn)
        btn_row.addWidget(self.remove_btn)
        btn_row.addWidget(self.clear_btn)
        layout.addLayout(btn_row)

        # Start Button
        self.start_btn = QPushButton("Start Processing Selected Files")
        self.start_btn.clicked.connect(self.start_processing)
        layout.addWidget(self.start_btn)

        # Progress Monitor
        layout.addWidget(QLabel("Progress Monitor"))
        self.progress_log = QTextEdit()
        self.progress_log.setReadOnly(True)
        layout.addWidget(self.progress_log)

        self.setLayout(layout)

    def select_folder(self, folder_type):
        folder = QFileDialog.getExistingDirectory(self, "Select Output Folder")
        if folder:
            if folder_type == "pdf":
                self.pdf_output = folder
                self.pdf_output_field.setText(folder)
            else:
                self.json_output = folder
                self.json_output_field.setText(folder)

    def add_files(self):
        files, _ = QFileDialog.getOpenFileNames(self, "Select Files")
        for file in files:
            if file not in self.selected_files:
                self.selected_files.append(file)
                self.file_list.addItem(QListWidgetItem(file))

    def remove_selected(self):
        for item in self.file_list.selectedItems():
            self.selected_files.remove(item.text())
            self.file_list.takeItem(self.file_list.row(item))

    def clear_all(self):
        self.selected_files = []
        self.file_list.clear()

    def start_processing(self):
        if not self.selected_files:
            QMessageBox.warning(self, "No Files", "Please add files to process.")
            return
        if not self.pdf_output or not self.json_output:
            QMessageBox.warning(self, "Missing Output", "Please set both PDF and JSON output folders.")
            return

        self.progress_log.clear()
        self.progress_log.append("Starting preprocessing...")
        
        temp_dir = os.path.abspath("temp/preprocessed")
        os.makedirs(temp_dir, exist_ok=True)
        self.progress_log.append(f"Preprocessed files saved to: {temp_dir}")

        merged_text_dir = os.path.abspath("temp/raw_texts_per_candidate")
        os.makedirs(merged_text_dir, exist_ok=True)

        json_output_dir = os.path.abspath(self.json_output)  # already user-defined in GUI
        os.makedirs(json_output_dir, exist_ok=True)
        
        final_output_dir = os.path.abspath("output")
        os.makedirs(os.path.join(final_output_dir, "final_pdfs"), exist_ok=True)
        os.makedirs(os.path.join(final_output_dir, "jsons"), exist_ok=True)



        all_preprocessed = []

        for idx, file in enumerate(self.selected_files, start=1):
            self.progress_log.append(f"[{idx}/{len(self.selected_files)}] Preprocessing: {os.path.basename(file)}")
            try:
                result_pdfs = preprocess_file(file, temp_dir)
                all_preprocessed.extend(result_pdfs)
                self.progress_log.append(f" Processed: {os.path.basename(file)} → {len(result_pdfs)} PDFs")
            except Exception as e:
                self.progress_log.append(f" Failed: {os.path.basename(file)} — {str(e)}")

        self.progress_log.append("Preprocessing complete.")
        self.progress_log.append(f"All cleaned PDFs are in: {temp_dir}")

        #split logix :)
        resume_split_dir = os.path.abspath("temp/resume_splits")
        os.makedirs(resume_split_dir, exist_ok=True)
        text_dir = os.path.abspath("temp/raw_texts_per_page")
        os.makedirs(text_dir, exist_ok=True)
        ocr_output_dir = os.path.abspath("temp/raw_texts_per_page")
        os.makedirs(ocr_output_dir, exist_ok=True)

        self.progress_log.append("Starting resume splitting phase...")

        for pdf_file in os.listdir(temp_dir):
            if not pdf_file.lower().endswith(".pdf"):
                continue
            full_path = os.path.join(temp_dir, pdf_file)
            self.progress_log.append(f" Reading: {pdf_file}")

            try:
                pages = extract_text_per_page(full_path, text_dir)
                groups = group_resume_pages(pages)
                split_paths = split_pdf_by_groups(full_path, groups, resume_split_dir)

                self.progress_log.append(f"{len(split_paths)} resumes split from {pdf_file}")
            except Exception as e:
                self.progress_log.append(f"Failed splitting {pdf_file}: {str(e)}")
        
        #ocr
        self.progress_log.append("Starting Azure OCR Phase...")

        for split_pdf in os.listdir(resume_split_dir):
            if not split_pdf.lower().endswith(".pdf"):
                continue

            full_pdf_path = os.path.join(resume_split_dir, split_pdf)
            txt_filename = os.path.splitext(split_pdf)[0] + ".txt"
            txt_output_path = os.path.join(ocr_output_dir, txt_filename)

            self.progress_log.append(f" OCR: {split_pdf}")
            try:
                extract_text_with_azure(full_pdf_path, txt_output_path)
                self.progress_log.append(f" OCR success: {split_pdf}")
            except Exception as e:
                self.progress_log.append(f" OCR failed: {split_pdf} — {str(e)}")



        self.progress_log.append("Merging OCR text into full candidate blocks...")
        #merging
        for split_pdf in os.listdir(resume_split_dir):
            if not split_pdf.lower().endswith(".pdf"):
                continue

            pdf_path = os.path.join(resume_split_dir, split_pdf)
            pdf_stem = os.path.splitext(split_pdf)[0]

            try:
                # Re-run per-page text extraction (no OCR now)
                page_texts = extract_text_per_page(pdf_path, ocr_output_dir)  # ensures filenames exist
                page_groups = group_resume_pages(page_texts)

                merge_texts_for_split_pdfs(
                    pdf_stem=pdf_stem,
                    page_groups=page_groups,
                    page_text_dir=ocr_output_dir,
                    output_dir=merged_text_dir
                )
                self.progress_log.append(f" Merged text: {split_pdf} → {len(page_groups)} candidates")
            except Exception as e:
                self.progress_log.append(f"Failed to merge text for {split_pdf}: {str(e)}")
        
        
        self.progress_log.append("Starting AI field extraction with GPT...")

        merged_text_dir = os.path.abspath("temp/raw_texts_per_candidate")

        for file in os.listdir(merged_text_dir):
            if not file.endswith(".txt"):
                continue

            txt_path = os.path.join(merged_text_dir, file)
            json_filename = os.path.splitext(file)[0] + ".json"
            json_path = os.path.join(json_output_dir, json_filename)

            self.progress_log.append(f" Extracting fields from: {file}")
            try:
                with open(txt_path, "r", encoding="utf-8") as f:
                    text = f.read()

                result = extract_fields_from_text(text)

                with open(json_path, "w", encoding="utf-8") as out_f:
                    json.dump(result, out_f, indent=2)

                self.progress_log.append(f"Extracted and saved: {json_filename}")
            except Exception as e:
                self.progress_log.append(f" Extraction failed for {file}: {str(e)}")

        #final bundling
        self.progress_log.append("Starting final bundling and renaming of PDFs...")

        for split_pdf in os.listdir(resume_split_dir):
            if not split_pdf.endswith(".pdf"):
                continue

            pdf_path = os.path.join(resume_split_dir, split_pdf)
            base_name = os.path.splitext(split_pdf)[0]
            json_path = os.path.join(json_output_dir, base_name + ".json")

            if not os.path.exists(json_path):
                self.progress_log.append(f"⚠️ Skipping: No matching JSON for {split_pdf}")
                continue

            try:
                final_pdf, final_json = bundle_pdf_and_json(pdf_path, json_path, final_output_dir)
                self.progress_log.append(f" Bundled → {os.path.basename(final_pdf)}")
            except Exception as e:
                self.progress_log.append(f" Bundle failed for {split_pdf}: {str(e)}")





                

                



