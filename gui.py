# gui.py
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QVBoxLayout, QHBoxLayout, QPushButton, QFileDialog,
    QListWidget, QListWidgetItem, QLineEdit, QTextEdit, QProgressBar, QMessageBox
)
from PyQt5.QtCore import Qt
import sys, os
from pathlib import Path
from core.preprocessor import preprocess_file
from core.text_splitter import extract_text_per_page
from core.resume_split_logic import group_resume_pages
from core.split_pdf import split_pdf_by_groups
from core.azure_ocr import extract_text_with_azure
from core.generate_candidate_texts import merge_texts_for_split_pdfs  

from PyQt5.QtCore import QThread, pyqtSignal
import traceback

class ResumeWorker(QThread):
    log_signal = pyqtSignal(str)  # Send messages back to GUI

    def __init__(self, files, pdf_output, json_output):
        super().__init__()
        self.files = files
        self.pdf_output = pdf_output
        self.json_output = json_output

    def run(self):
        try:
            from core.preprocessor import preprocess_file
            from core.azure_ocr import extract_text_with_azure
            from core.text_splitter import extract_text_per_page
            from core.resume_split_logic import group_resume_pages
            from core.split_pdf import split_pdf_by_groups
            from core.generate_candidate_texts import merge_texts_for_split_pdfs

            pre_dir = "temp/preprocessed"
            txt_per_page_dir = "temp/raw_texts_per_page"
            txt_per_candidate_dir = "temp/raw_texts_per_candidate"

            os.makedirs(pre_dir, exist_ok=True)
            os.makedirs(txt_per_page_dir, exist_ok=True)
            os.makedirs(txt_per_candidate_dir, exist_ok=True)
            os.makedirs(self.pdf_output, exist_ok=True)
            os.makedirs(self.json_output, exist_ok=True)

            for file_path in self.files:
                self.log_signal.emit(f"🔧 Preprocessing: {os.path.basename(file_path)}")
                preprocessed_pdfs = preprocess_file(file_path, pre_dir)

                for pdf in preprocessed_pdfs:
                    self.log_signal.emit(f"OCR: {os.path.basename(pdf)}")
                    output_txt_path = os.path.join(txt_per_page_dir, f"{Path(pdf).stem}.txt")
                    self.log_signal.emit(f"🧠 Azure OCR → {output_txt_path}")
                    extract_text_with_azure(pdf, output_txt_path)
                    page_texts = extract_text_per_page(pdf, txt_per_page_dir)
                    groups = group_resume_pages(page_texts)
                    self.log_signal.emit(f"📊 Detected {len(groups)} candidate(s).")

                    split_paths = split_pdf_by_groups(pdf, groups, self.pdf_output)
                    merge_texts_for_split_pdfs(split_paths, groups, txt_per_page_dir, txt_per_candidate_dir)

            self.log_signal.emit("✅ Processing complete.")

        except Exception as e:
            self.log_signal.emit(f" Error: {str(e)}\n{traceback.format_exc()}")

class ResumeProcessorGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Resume Parser- Adam")
        self.resize(800, 600)

        self.selected_files = []
        self.pdf_output = ""
        self.json_output = ""

        layout = QVBoxLayout()

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

        layout.addWidget(QLabel("External Dependencies Status"))
        self.status_label = QLabel("Azure DI: Connected\nAzure Handwriting: Not Connected\nAzure Vision: Connected\nOpenAI GPT: Connected")
        layout.addWidget(self.status_label)
        self.refresh_btn = QPushButton("Refresh API Status")
        layout.addWidget(self.refresh_btn)

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

        self.start_btn = QPushButton("Start Processing Selected Files")
        self.start_btn.clicked.connect(self.start_processing)
        layout.addWidget(self.start_btn)

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
        self.progress_log.append("Starting threaded resume processing...\n")

        self.worker = ResumeWorker(
            files=self.selected_files,
            pdf_output=self.pdf_output,
            json_output=self.json_output
        )
        self.worker.log_signal.connect(self.progress_log.append)
        self.worker.start()

        pre_dir = "temp/preprocessed"
        txt_per_page_dir = "temp/raw_texts_per_page"
        split_dir = self.pdf_output
        txt_per_candidate_dir = "temp/raw_texts_per_candidate"

        os.makedirs(pre_dir, exist_ok=True)
        os.makedirs(txt_per_page_dir, exist_ok=True)
        os.makedirs(split_dir, exist_ok=True)
        os.makedirs(txt_per_candidate_dir, exist_ok=True)

        self.progress_log.append("Starting file processing...\n")

        for file_path in self.selected_files:
            file_name = os.path.basename(file_path)
            self.progress_log.append(f"🔧 Preprocessing: {file_name}")
            preprocessed_paths = preprocess_file(file_path, pre_dir)

            for pdf in preprocessed_paths:
                base_name = Path(pdf).stem
                self.progress_log.append(f" Extracting: {base_name}.pdf")

                extract_text_with_azure(pdf, os.path.join(txt_per_page_dir, f"{base_name}.txt"))
                page_texts = extract_text_per_page(pdf, txt_per_page_dir)

                groups = group_resume_pages(page_texts)
                self.progress_log.append(f" Resumes Detected: {len(groups)}")

                split_pdf_by_groups(pdf, groups, split_dir)
                merge_texts_for_split_pdfs(base_name, groups, txt_per_page_dir, txt_per_candidate_dir)

                self.progress_log.append(" All files processed and split successfully.\n")

        self.progress_log.append("DEBUG: Starting processing...")
        for file in self.selected_files:
            self.progress_log.append(f"DEBUG: File queued - {file}")
        self.progress_log.append(f"DEBUG: PDF Output → {self.pdf_output}")
        self.progress_log.append(f"DEBUG: JSON Output → {self.json_output}")
        self.progress_log.append("DEBUG: Simulated connection test for OpenAI and Azure APIs successful.")

