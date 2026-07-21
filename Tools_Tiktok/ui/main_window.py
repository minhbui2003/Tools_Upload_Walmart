import os
from datetime import datetime

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFileDialog,
    QComboBox,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QProgressBar,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from core.config import ensure_env_file, get_project_root, get_resource_path, get_resource_root
from core.tiktok_generator import (
    SIZE_DEFINITIONS,
    create_tiktok_image_mixing_template,
    create_tiktok_update_template,
    generate_variants,
    get_profile_options,
)
from ui.workers import TiktokRunWorker


STYLE = """
QMainWindow { background-color: #f5f7fb; }
QWidget { color: #1f2937; font-family: "Segoe UI"; font-size: 13px; }
QLabel#title { font-size: 20px; font-weight: 700; color: #111827; }
QGroupBox { border: 1px solid #d1d5db; border-radius: 6px; margin-top: 14px; padding: 10px; font-weight: 600; }
QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 0 4px; }
QLineEdit, QComboBox, QTextEdit {
    background-color: #ffffff;
    border: 1px solid #cbd5e1;
    border-radius: 5px;
    padding: 6px 8px;
}
QLineEdit:focus, QComboBox:focus, QTextEdit:focus { border-color: #2563eb; }
QComboBox QAbstractItemView {
    background-color: #ffffff;
    color: #111827;
    border: 1px solid #94a3b8;
    selection-background-color: #2563eb;
    selection-color: #ffffff;
    outline: 0;
}
QComboBox QAbstractItemView::item {
    min-height: 24px;
    padding: 4px 8px;
}
QComboBox QAbstractItemView::item:hover {
    background-color: #dbeafe;
    color: #111827;
}
QPushButton {
    background-color: #e5e7eb;
    border: 1px solid #d1d5db;
    border-radius: 5px;
    padding: 7px 12px;
    font-weight: 600;
}
QPushButton:hover { background-color: #dbeafe; border-color: #93c5fd; }
QPushButton#runBtn { background-color: #16a34a; border-color: #16a34a; color: #ffffff; }
QPushButton#runBtn:hover { background-color: #15803d; }
QPushButton#runBtn:disabled { background-color: #9ca3af; border-color: #9ca3af; }
QPushButton#openBtn { background-color: #f59e0b; border-color: #f59e0b; color: #111827; }
QTextEdit#logBox { background-color: #0f172a; color: #d1d5db; font-family: "Cascadia Code", Consolas, monospace; }
QProgressBar { height: 8px; border: 1px solid #cbd5e1; border-radius: 4px; text-align: center; }
QProgressBar::chunk { background-color: #2563eb; border-radius: 3px; }
QMessageBox, QFileDialog {
    background-color: #ffffff;
    color: #111827;
}
QMessageBox QLabel, QFileDialog QLabel {
    color: #111827;
}
QMessageBox QPushButton, QFileDialog QPushButton {
    background-color: #e5e7eb;
    color: #111827;
    border: 1px solid #cbd5e1;
    border-radius: 5px;
    padding: 6px 12px;
}
QMessageBox QPushButton:hover, QFileDialog QPushButton:hover {
    background-color: #dbeafe;
}
"""


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("TikTok POD Upload Tool")
        self.resize(980, 760)
        self.setStyleSheet(STYLE)

        self.project_root = get_project_root()
        self.resource_root = get_resource_root()
        self.env_path = ensure_env_file()
        self.output_xlsx = ""
        self.worker = None

        self._build_ui()
        self._set_defaults()

    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)

        root = QVBoxLayout(central)
        root.setContentsMargins(16, 16, 16, 16)
        root.setSpacing(10)

        title = QLabel("TikTok POD Upload Tool")
        title.setObjectName("title")
        root.addWidget(title)

        file_group = QGroupBox("File và ảnh")
        file_layout = QGridLayout(file_group)
        file_layout.setColumnStretch(0, 1)

        self.template_entry = QLineEdit()
        file_layout.addWidget(QLabel("TikTok template trống"), 0, 0)
        file_layout.addWidget(self.template_entry, 1, 0)
        file_layout.addWidget(self._button("Chọn...", self._select_template), 1, 1)

        self.image_folder_entry = QLineEdit()
        file_layout.addWidget(QLabel("Folder ảnh MK/main/color"), 2, 0)
        file_layout.addWidget(self.image_folder_entry, 3, 0)
        file_layout.addWidget(self._button("Chọn...", self._select_image_folder), 3, 1)

        self.output_folder_entry = QLineEdit()
        file_layout.addWidget(QLabel("Output folder"), 4, 0)
        file_layout.addWidget(self.output_folder_entry, 5, 0)
        file_layout.addWidget(self._button("Chọn...", self._select_output_folder), 5, 1)

        self.update_file_entry = QLineEdit()
        file_layout.addWidget(QLabel("Update file tùy chọn"), 6, 0)
        file_layout.addWidget(self.update_file_entry, 7, 0)
        file_layout.addWidget(self._button("Chọn...", self._select_update_file), 7, 1)

        self.image_mixing_entry = QLineEdit()
        file_layout.addWidget(QLabel("Image mixing file optional"), 8, 0)
        file_layout.addWidget(self.image_mixing_entry, 9, 0)
        file_layout.addWidget(self._button("Select...", self._select_image_mixing_file), 9, 1)

        self.mapping_entry = QLineEdit()
        file_layout.addWidget(QLabel("Mapping file optional"), 10, 0)
        file_layout.addWidget(self.mapping_entry, 11, 0)
        file_layout.addWidget(self._button("Select...", self._select_mapping_file), 11, 1)

        root.addWidget(file_group)

        sku_group = QGroupBox("SKU và profile")
        sku_layout = QGridLayout(sku_group)

        self.profile_combo = QComboBox()
        for key, label in get_profile_options():
            self.profile_combo.addItem(label, key)
        self.profile_combo.currentIndexChanged.connect(self._on_profile_changed)
        sku_layout.addWidget(QLabel("Product type"), 0, 0)
        sku_layout.addWidget(self.profile_combo, 1, 0)

        self.sku_entry = QLineEdit()
        self.sku_entry.setPlaceholderText("VD: 060726TA7TW")
        sku_layout.addWidget(QLabel("SKU prefix"), 0, 1)
        sku_layout.addWidget(self.sku_entry, 1, 1)

        self.cloud_folder_entry = QLineEdit()
        sku_layout.addWidget(QLabel("Cloudinary batch/folder"), 0, 2)
        sku_layout.addWidget(self.cloud_folder_entry, 1, 2)

        root.addWidget(sku_group)

        button_row = QHBoxLayout()
        self.preview_btn = self._button("Preview SKU", self._preview)
        button_row.addWidget(self.preview_btn)

        self.run_btn = self._button("Tạo file upload TikTok", self._run)
        self.run_btn.setObjectName("runBtn")
        button_row.addWidget(self.run_btn)

        self.open_btn = self._button("Open XLSX", self._open_xlsx)
        self.open_btn.setObjectName("openBtn")
        self.open_btn.setEnabled(False)
        button_row.addWidget(self.open_btn)

        button_row.addWidget(self._button("Clear log", self._clear_log))
        button_row.addStretch()
        root.addLayout(button_row)

        self.progress = QProgressBar()
        self.progress.setRange(0, 0)
        self.progress.setVisible(False)
        root.addWidget(self.progress)

        self.status_label = QLabel("Ready")
        root.addWidget(self.status_label)

        self.log_box = QTextEdit()
        self.log_box.setObjectName("logBox")
        self.log_box.setReadOnly(True)
        self.log_box.setMinimumHeight(170)
        root.addWidget(self.log_box)

    def _button(self, text, callback):
        button = QPushButton(text)
        button.clicked.connect(callback)
        return button

    def _set_defaults(self):
        self.output_folder_entry.setText(os.path.join(self.project_root, "output"))
        self.cloud_folder_entry.setText(datetime.now().strftime("tiktok-%Y%m%d-%H%M"))
        self._set_default_template_path(force=True)
        self._set_default_image_mixing_path(force=True)
        self._set_default_mapping_path(force=True)
        self._write_log(f".env: {self.env_path}")

    def _default_template_path_for_profile(self):
        candidates_by_profile = {
            "mens_tshirt": [
                os.path.join(self.project_root, "Tiktoksellercenter_Menswear & Underwear_Template.xlsx"),
                os.path.join(self.resource_root, "Tiktoksellercenter_Menswear & Underwear_Template.xlsx"),
                os.path.join(
                    self.project_root,
                    "Tiktoksellercenter_Menswear & Underwear_20260708_Men's Short-sleeve T-shirts_template.xlsx",
                ),
                os.path.join(
                    self.resource_root,
                    "Tiktoksellercenter_Menswear & Underwear_20260708_Men's Short-sleeve T-shirts_template.xlsx",
                ),
            ],
            "womens_tshirt": [
                os.path.join(
                    self.project_root,
                    "Files",
                    "Tiktoksellercenter_160726HN6_20260714_Women's blank template.xlsx",
                ),
                os.path.join(
                    self.resource_root,
                    "Files",
                    "Tiktoksellercenter_160726HN6_20260714_Women's blank template.xlsx",
                ),
            ],
        }
        for path in candidates_by_profile.get(self._profile_key(), []):
            if os.path.exists(path):
                return path
        return ""

    def _default_mapping_path_for_profile(self):
        filename_by_profile = {
            "mens_tshirt": "Tiktok_Mapping_Mens_Tshirt_Full.xlsx",
            "womens_tshirt": "Tiktok_Mapping_Womens_Tshirt_Full.xlsx",
        }
        filename = filename_by_profile.get(self._profile_key())
        if not filename:
            return ""
        candidates = [
            os.path.join(self.project_root, "templates", filename),
            get_resource_path("templates", filename),
        ]
        for path in candidates:
            if os.path.exists(path):
                return path
        return candidates[0]

    def _default_image_mixing_path_for_profile(self):
        filename_by_profile = {
            "mens_tshirt": "Tiktok_Image_Mixing_Mens.xlsx",
            "womens_tshirt": "Tiktok_Image_Mixing_Womens.xlsx",
        }
        filename = filename_by_profile.get(self._profile_key())
        if not filename:
            return ""
        candidates = [
            os.path.join(self.project_root, "templates", filename),
            get_resource_path("templates", filename),
        ]
        for path in candidates:
            if os.path.exists(path):
                return path
        return candidates[0]

    def _set_default_template_path(self, force=False):
        template_path = self._default_template_path_for_profile()
        if not template_path:
            return

        current = self.template_entry.text().strip()
        current_name = os.path.basename(current)
        is_auto_template = current_name.startswith("Tiktoksellercenter_")
        if force or not current or is_auto_template:
            self.template_entry.setText(template_path)

    def _set_default_mapping_path(self, force=False):
        if not hasattr(self, "mapping_entry"):
            return

        mapping_path = self._default_mapping_path_for_profile()
        if not mapping_path or not os.path.exists(mapping_path):
            return

        current = self.mapping_entry.text().strip()
        current_name = os.path.basename(current)
        is_auto_mapping = current_name.startswith("Tiktok_Mapping_")
        if force or not current or is_auto_mapping:
            self.mapping_entry.setText(mapping_path)

    def _set_default_image_mixing_path(self, force=False):
        image_mixing_path = self._default_image_mixing_path_for_profile()
        if not image_mixing_path or not os.path.exists(image_mixing_path):
            return

        current = self.image_mixing_entry.text().strip()
        current_name = os.path.basename(current)
        is_auto_image_mixing = current_name.startswith("Tiktok_Image_Mixing_")
        if force or not current or is_auto_image_mixing:
            self.image_mixing_entry.setText(image_mixing_path)

    def _on_profile_changed(self):
        self._set_default_template_path()
        self._set_default_image_mixing_path()
        self._set_default_mapping_path()

    def _select_template(self):
        path, _ = QFileDialog.getOpenFileName(self, "Chọn TikTok template trống", self.project_root, "Excel files (*.xlsx *.xlsm)")
        if path:
            self.template_entry.setText(path)

    def _select_image_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Chọn folder ảnh")
        if folder:
            self.image_folder_entry.setText(folder)
            if not self.output_folder_entry.text().strip():
                self.output_folder_entry.setText(os.path.join(folder, "Tiktok_Output"))

    def _select_output_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Chọn output folder")
        if folder:
            self.output_folder_entry.setText(folder)

    def _select_update_file(self):
        path, _ = QFileDialog.getOpenFileName(self, "Chọn update file", self.project_root, "Data files (*.xlsx *.xlsm *.xls *.csv)")
        if path:
            self.update_file_entry.setText(path)

    def _select_image_mixing_file(self):
        path, _ = QFileDialog.getOpenFileName(self, "Select image mixing file", self.project_root, "Data files (*.xlsx *.xlsm *.xls *.csv)")
        if path:
            self.image_mixing_entry.setText(path)

    def _select_mapping_file(self):
        path, _ = QFileDialog.getOpenFileName(self, "Select mapping file", self.project_root, "Data files (*.xlsx *.xlsm *.xls *.csv)")
        if path:
            self.mapping_entry.setText(path)

    def _profile_key(self):
        return self.profile_combo.currentData()

    def _validate(self):
        template_path = self.template_entry.text().strip()
        image_folder = self.image_folder_entry.text().strip()
        output_folder = self.output_folder_entry.text().strip()
        sku_prefix = self.sku_entry.text().strip()
        cloud_folder = self.cloud_folder_entry.text().strip()

        checks = [
            (not template_path or not os.path.exists(template_path), "Chưa chọn TikTok template hợp lệ."),
            (not image_folder or not os.path.isdir(image_folder), "Chưa chọn folder ảnh hợp lệ."),
            (not output_folder, "Chưa chọn output folder."),
            (not sku_prefix, "Chưa nhập SKU prefix."),
            (not cloud_folder, "Chưa nhập Cloudinary batch/folder."),
            (not os.path.exists(self.env_path), f"Không tìm thấy file .env: {self.env_path}"),
        ]

        update_file = self.update_file_entry.text().strip()
        if update_file and not os.path.exists(update_file):
            checks.append((True, "Update file không tồn tại."))

        image_mixing_file = self.image_mixing_entry.text().strip()
        if image_mixing_file and not os.path.exists(image_mixing_file):
            checks.append((True, "Image mixing file does not exist."))

        mapping_file = self.mapping_entry.text().strip()
        if mapping_file and not os.path.exists(mapping_file):
            checks.append((True, "Mapping file does not exist."))

        for condition, message in checks:
            if condition:
                QMessageBox.critical(self, "Thiếu thông tin", message)
                return None

        return {
            "template_path": template_path,
            "image_folder": image_folder,
            "output_folder": output_folder,
            "sku_prefix": sku_prefix,
            "profile_key": self._profile_key(),
            "cloud_folder": cloud_folder,
            "env_path": self.env_path,
            "update_file_path": update_file,
            "image_mixing_path": image_mixing_file,
            "mapping_path": mapping_file,
        }

    def _create_update_template(self):
        sku_prefix = self.sku_entry.text().strip()
        if not sku_prefix:
            QMessageBox.critical(self, "Thiếu SKU Prefix", "Nhập SKU prefix trước khi tạo update template.")
            return

        output_folder = self.output_folder_entry.text().strip() or os.path.join(self.project_root, "output")
        os.makedirs(output_folder, exist_ok=True)
        profile_key = self._profile_key()
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = os.path.join(output_folder, f"tiktok_update_template_{profile_key}_{timestamp}.xlsx")

        try:
            create_tiktok_update_template(output_path, profile_key=profile_key, sku_prefix=sku_prefix)
            self.update_file_entry.setText(output_path)
            self._write_log(f"Update template: {output_path}")
            QMessageBox.information(self, "Đã tạo update template", output_path)
        except Exception as exc:
            self._write_log(f"ERROR: {exc}")
            QMessageBox.critical(self, "Lỗi", str(exc))

    def _create_image_mixing_template_file(self, randomize=False):
        sku_prefix = self.sku_entry.text().strip()
        if not sku_prefix:
            QMessageBox.critical(self, "Missing SKU Prefix", "Enter SKU prefix before creating image mixing.")
            return

        output_folder = self.output_folder_entry.text().strip() or os.path.join(self.project_root, "output")
        os.makedirs(output_folder, exist_ok=True)
        profile_key = self._profile_key()
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        suffix = "random" if randomize else "template"
        output_path = os.path.join(output_folder, f"tiktok_image_mixing_{suffix}_{profile_key}_{timestamp}.xlsx")

        try:
            create_tiktok_image_mixing_template(
                output_path,
                profile_key=profile_key,
                sku_prefix=sku_prefix,
                randomize=randomize,
            )
            self.image_mixing_entry.setText(output_path)
            self._write_log(f"Image mixing template: {output_path}")
            QMessageBox.information(self, "Created image mixing", output_path)
        except Exception as exc:
            self._write_log(f"ERROR: {exc}")
            QMessageBox.critical(self, "Error", str(exc))

    def _create_image_mixing_template(self):
        self._create_image_mixing_template_file(randomize=False)

    def _create_random_image_mixing_template(self):
        self._create_image_mixing_template_file(randomize=True)

    def _preview(self):
        params = self._validate()
        if not params:
            return

        variants = generate_variants(params["profile_key"], params["sku_prefix"])
        self._write_log("===== PREVIEW SKU =====")
        self._write_log(f"Total variants: {len(variants)}")
        self._write_log("Size order: " + ", ".join(item["label"] for item in SIZE_DEFINITIONS))
        for variant in variants[:12]:
            self._write_log(f"{variant['color']} / {variant['size_input']} -> {variant['sku']}")

    def _run(self):
        params = self._validate()
        if not params:
            return

        self.run_btn.setEnabled(False)
        self.open_btn.setEnabled(False)
        self.progress.setVisible(True)
        self.status_label.setText("Running...")
        self._write_log("===== START TIKTOK GENERATION =====")

        self.worker = TiktokRunWorker(params)
        self.worker.log_signal.connect(self._write_log)
        self.worker.finished_signal.connect(self._on_success)
        self.worker.error_signal.connect(self._on_error)
        self.worker.start()

    def _on_success(self, result):
        self.progress.setVisible(False)
        self.run_btn.setEnabled(True)
        self.open_btn.setEnabled(True)
        self.status_label.setText("Completed")
        self.output_xlsx = result["output_xlsx"]

        self._write_log("===== DONE =====")
        self._write_log(f"Final TikTok XLSX: {result['output_xlsx']}")
        self._write_log(f"Generation log: {result['log_csv']}")

        QMessageBox.information(self, "Hoàn tất", f"Đã tạo file TikTok:\n{result['output_xlsx']}")

    def _on_error(self, message):
        self.progress.setVisible(False)
        self.run_btn.setEnabled(True)
        self.status_label.setText("Error")
        self._write_log(f"ERROR: {message}")
        QMessageBox.critical(self, "Lỗi", message)

    def _open_xlsx(self):
        if self.output_xlsx and os.path.exists(self.output_xlsx):
            os.startfile(self.output_xlsx)
        else:
            QMessageBox.warning(self, "Chưa có file", "Chưa có file XLSX được tạo.")

    def _clear_log(self):
        self.log_box.clear()
        self.status_label.setText("Ready")

    def _write_log(self, message):
        self.log_box.append(str(message))
        self.log_box.verticalScrollBar().setValue(self.log_box.verticalScrollBar().maximum())
