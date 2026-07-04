"""
PySide6 Main Window for Upload Toni tool.
"""
import os
from datetime import datetime

import pandas as pd
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QLineEdit, QPushButton, QComboBox, QCheckBox,
    QTreeWidget, QTreeWidgetItem, QTextEdit, QProgressBar,
    QFileDialog, QMessageBox, QFrame, QSplitter, QScrollArea
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QColor

from core.config import get_project_root
from core.utils import is_enabled, normalize_columns
from core.profile import ProductProfileManager
from core.sku import get_sku_by_color, build_full_skuwa_from_row
from core.mapper import read_mapping_file
from ui.workers import RunAllWorker

# ─── Stylesheet ───────────────────────────────────────────────
DARK_STYLESHEET = """
QMainWindow { background-color: #1e1e2e; }
QWidget { color: #cdd6f4; font-family: "Segoe UI"; font-size: 13px; }
QLabel#title { font-size: 20px; font-weight: bold; color: #89b4fa; }
QLabel#sectionLabel { font-size: 12px; color: #a6adc8; font-weight: 600; }
QLineEdit, QComboBox { background-color: #313244; border: 1px solid #45475a; border-radius: 6px; padding: 6px 10px; color: #cdd6f4; selection-background-color: #89b4fa; }
QLineEdit:focus, QComboBox:focus { border: 1px solid #89b4fa; }
QComboBox QAbstractItemView { background-color: #313244; color: #cdd6f4; selection-background-color: #45475a; border: 1px solid #45475a; }
QPushButton { background-color: #45475a; border: 1px solid #585b70; border-radius: 6px; padding: 6px 16px; color: #cdd6f4; font-weight: 600; }
QPushButton:hover { background-color: #585b70; }
QPushButton#browseBtn { background-color: #89b4fa; color: #1e1e2e; border: none; }
QPushButton#browseBtn:hover { background-color: #74c7ec; }
QPushButton#runBtn { background-color: #a6e3a1; color: #1e1e2e; border: none; font-size: 14px; padding: 8px 24px; }
QPushButton#runBtn:hover { background-color: #94e2d5; }
QPushButton#runBtn:disabled { background-color: #585b70; color: #6c7086; }
QPushButton#openBtn { background-color: #f9e2af; color: #1e1e2e; border: none; }
QPushButton#openBtn:hover { background-color: #f5c2e7; }
QTreeWidget { background-color: #313244; border: 1px solid #45475a; alternate-background-color: #2a2a3c; }
QTreeWidget::item { padding: 3px 0; }
QTreeWidget::item:selected { background-color: #45475a; }
QTextEdit { background-color: #181825; border: 1px solid #45475a; border-radius: 6px; padding: 8px; font-family: "Cascadia Code", "Consolas", monospace; font-size: 12px; color: #a6adc8; }
QProgressBar { background-color: #313244; border: 1px solid #45475a; border-radius: 4px; text-align: center; color: #cdd6f4; height: 8px; }
QProgressBar::chunk { background-color: #89b4fa; border-radius: 3px; }
QLabel#selectedTemplate { color: #a6e3a1; font-weight: 600; }
QLabel#statusLabel { color: #f9e2af; font-weight: 600; }
QScrollArea { background-color: transparent; border: none; }
#mainContainer { background-color: transparent; }
"""

LIGHT_STYLESHEET = """
QMainWindow { background-color: #f0f0f5; }
QWidget { color: #333333; font-family: "Segoe UI"; font-size: 13px; }
QLabel#title { font-size: 20px; font-weight: bold; color: #2c3e50; }
QLabel#sectionLabel { font-size: 12px; color: #555555; font-weight: 600; }
QLineEdit, QComboBox { background-color: #ffffff; border: 1px solid #cccccc; border-radius: 6px; padding: 6px 10px; color: #333333; selection-background-color: #3498db; }
QLineEdit:focus, QComboBox:focus { border: 1px solid #3498db; }
QComboBox QAbstractItemView { background-color: #ffffff; color: #333333; selection-background-color: #e0e0e0; border: 1px solid #cccccc; }
QPushButton { background-color: #e0e0e0; border: 1px solid #cccccc; border-radius: 6px; padding: 6px 16px; color: #333333; font-weight: 600; }
QPushButton:hover { background-color: #d5d5d5; }
QPushButton#browseBtn { background-color: #3498db; color: #ffffff; border: none; }
QPushButton#browseBtn:hover { background-color: #2980b9; }
QPushButton#runBtn { background-color: #2ecc71; color: #ffffff; border: none; font-size: 14px; padding: 8px 24px; }
QPushButton#runBtn:hover { background-color: #27ae60; }
QPushButton#runBtn:disabled { background-color: #bdc3c7; color: #7f8c8d; }
QPushButton#openBtn { background-color: #f1c40f; color: #333333; border: none; }
QPushButton#openBtn:hover { background-color: #f39c12; }
QTreeWidget { background-color: #ffffff; border: 1px solid #cccccc; alternate-background-color: #f9f9f9; }
QTreeWidget::item { padding: 3px 0; }
QTreeWidget::item:selected { background-color: #3498db; color: #ffffff; }
QTextEdit { background-color: #ffffff; border: 1px solid #cccccc; border-radius: 6px; padding: 8px; font-family: "Cascadia Code", "Consolas", monospace; font-size: 12px; color: #333333; }
QProgressBar { background-color: #e0e0e0; border: 1px solid #cccccc; border-radius: 4px; text-align: center; color: #333333; height: 8px; }
QProgressBar::chunk { background-color: #3498db; border-radius: 3px; }
QLabel#selectedTemplate { color: #27ae60; font-weight: 600; }
QLabel#statusLabel { color: #f39c12; font-weight: 600; }
QScrollArea { background-color: transparent; border: none; }
#mainContainer { background-color: transparent; }
"""

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("🔥 Tools Marketplace")
        self.setMinimumSize(850, 600)
        self.resize(1100, 800)  # Default size when opening
        self.setStyleSheet(DARK_STYLESHEET)

        self.project_root = get_project_root()
        self.env_path = os.path.join(self.project_root, ".env")

        # State
        self.image_folder = ""
        self.getlinks_template_path = ""
        self.seller_template_path = ""
        self.mapping_path = ""
        self.update_file_path = ""
        self.output_folder = ""
        self.output_xlsx = ""
        self.worker = None

        self._build_ui()

    # ─── UI Construction ──────────────────────────────────────
    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)

        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.NoFrame)
        main_layout.addWidget(scroll_area)

        container = QWidget()
        container.setObjectName("mainContainer")
        scroll_area.setWidget(container)

        layout = QVBoxLayout(container)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(8)

        # Title and Theme Toggle
        top_row = QHBoxLayout()
        title = QLabel("🔥 Tools Marketplace")
        title.setObjectName("title")
        top_row.addWidget(title)
        top_row.addStretch()

        self.theme_check = QCheckBox("☀️ Giao diện sáng")
        self.theme_check.stateChanged.connect(self._toggle_theme)
        top_row.addWidget(self.theme_check)

        layout.addLayout(top_row)

        # 1. Image folder
        self.image_entry = self._add_folder_row(layout, "1. Folder ảnh gốc:", self._select_image_folder)

        # Rename checkbox
        self.rename_check = QCheckBox("Đổi tên file trước khi upload")
        self.rename_check.setChecked(True)
        layout.addWidget(self.rename_check)

        # Grid form
        grid = QGridLayout()
        grid.setSpacing(10)

        # 2. SKU Prefix
        lbl_sku = QLabel("2. SKU Prefix:")
        lbl_sku.setObjectName("sectionLabel")
        grid.addWidget(lbl_sku, 0, 0)
        self.sku_entry = QLineEdit()
        grid.addWidget(self.sku_entry, 1, 0)

        # 3. Product Type
        lbl_ptype = QLabel("3. Product Type ID:")
        lbl_ptype.setObjectName("sectionLabel")
        grid.addWidget(lbl_ptype, 0, 1)
        self.product_type_combo = QComboBox()
        self.product_type_combo.setEditable(True)
        self.product_type_combo.addItems(["TSH", "TSH_W", "SWE", "SWE_W"])
        self.product_type_combo.setCurrentText("TSH")
        self.product_type_combo.currentTextChanged.connect(self._auto_fill_sku)
        grid.addWidget(self.product_type_combo, 1, 1)

        layout.addLayout(grid)

        # 4. Getlinks template tree
        lbl_template = QLabel("4. Getlinks/Image Template:")
        lbl_template.setObjectName("sectionLabel")
        layout.addWidget(lbl_template)

        template_dir_row = QHBoxLayout()
        self.template_dir_entry = QLineEdit()
        default_template_dir = os.path.join(self.project_root, "templates")
        self.template_dir_entry.setText(default_template_dir)
        template_dir_row.addWidget(self.template_dir_entry)
        btn_dir = QPushButton("Chọn Thư Mục...")
        btn_dir.setObjectName("browseBtn")
        btn_dir.clicked.connect(self._select_template_directory)
        template_dir_row.addWidget(btn_dir)
        layout.addLayout(template_dir_row)

        self.template_tree = QTreeWidget()
        self.template_tree.setHeaderHidden(True)
        self.template_tree.setMinimumHeight(80)
        self.template_tree.setMaximumHeight(300)
        self.template_tree.setAlternatingRowColors(True)
        self.template_tree.itemClicked.connect(self._on_template_tree_click)
        layout.addWidget(self.template_tree)

        self.selected_template_label = QLabel("Đã chọn: Chưa chọn mẫu")
        self.selected_template_label.setObjectName("selectedTemplate")
        layout.addWidget(self.selected_template_label)

        self._populate_template_tree(default_template_dir)

        # Grid row 2: Seller template + Cloudinary batch
        grid2 = QGridLayout()
        grid2.setSpacing(8)

        self.seller_template_entry = self._add_file_row_to_grid(
            grid2, 0, 0, "5. Walmart Seller Template:", self._select_seller_template
        )
        lbl_batch = QLabel("6. Cloudinary Batch Name:")
        lbl_batch.setObjectName("sectionLabel")
        grid2.addWidget(lbl_batch, 0, 1)
        self.batch_entry = QLineEdit()
        self.batch_entry.setText(datetime.now().strftime("batch-%Y%m%d-%H%M"))
        grid2.addWidget(self.batch_entry, 1, 1)

        layout.addLayout(grid2)

        # Grid row 3: Mapping + Update file
        grid3 = QGridLayout()
        grid3.setSpacing(8)

        self.mapping_entry = self._add_file_row_to_grid(
            grid3, 0, 0, "7. Mapping Config:", self._select_mapping_file
        )
        self.update_entry = self._add_file_row_to_grid(
            grid3, 0, 1, "8. Update File:", self._select_update_file
        )

        layout.addLayout(grid3)

        # 9. Output folder
        self.output_entry = self._add_folder_row(layout, "9. Output Folder:", self._select_output_folder)

        # Buttons
        btn_row = QHBoxLayout()
        btn_row.setSpacing(10)

        self.preview_btn = QPushButton("Preview")
        self.preview_btn.clicked.connect(self._preview)
        btn_row.addWidget(self.preview_btn)

        self.run_btn = QPushButton("Run All")
        self.run_btn.setObjectName("runBtn")
        self.run_btn.clicked.connect(self._start_run_all)
        btn_row.addWidget(self.run_btn)

        self.open_btn = QPushButton("Open XLSX")
        self.open_btn.setObjectName("openBtn")
        self.open_btn.setEnabled(False)
        self.open_btn.clicked.connect(self._open_xlsx)
        btn_row.addWidget(self.open_btn)

        clear_btn = QPushButton("Clear Log")
        clear_btn.clicked.connect(self._clear_log)
        btn_row.addWidget(clear_btn)

        btn_row.addStretch()
        layout.addLayout(btn_row)

        # Progress bar
        self.progress = QProgressBar()
        self.progress.setRange(0, 0)
        self.progress.setVisible(False)
        layout.addWidget(self.progress)

        # Status
        self.status_label = QLabel("Ready")
        self.status_label.setObjectName("statusLabel")
        layout.addWidget(self.status_label)

        # Log
        lbl_log = QLabel("Log:")
        lbl_log.setObjectName("sectionLabel")
        layout.addWidget(lbl_log)

        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setMinimumHeight(60)
        self.log_text.setMaximumHeight(200)
        layout.addWidget(self.log_text)

    # ─── Helper UI builders ──────────────────────────────────
    def _add_folder_row(self, parent_layout, label_text, callback):
        lbl = QLabel(label_text)
        lbl.setObjectName("sectionLabel")
        parent_layout.addWidget(lbl)

        row = QHBoxLayout()
        entry = QLineEdit()
        row.addWidget(entry)
        btn = QPushButton("Browse...")
        btn.setObjectName("browseBtn")
        btn.clicked.connect(callback)
        row.addWidget(btn)
        parent_layout.addLayout(row)
        return entry

    def _add_file_row_to_grid(self, grid, row, col, label_text, callback):
        lbl = QLabel(label_text)
        lbl.setObjectName("sectionLabel")
        grid.addWidget(lbl, row, col)

        container = QWidget()
        h = QHBoxLayout(container)
        h.setContentsMargins(0, 0, 0, 0)
        entry = QLineEdit()
        h.addWidget(entry)
        btn = QPushButton("Browse...")
        btn.setObjectName("browseBtn")
        btn.clicked.connect(callback)
        h.addWidget(btn)
        grid.addWidget(container, row + 1, col)
        return entry

    # ─── Template tree ────────────────────────────────────────
    def _populate_template_tree(self, directory):
        self.template_tree.clear()
        if not os.path.exists(directory):
            return
        self._populate_tree_node(None, directory)

    def _populate_tree_node(self, parent_item, path):
        try:
            items = os.listdir(path)
        except Exception:
            return

        for item_name in sorted(items):
            if item_name.startswith("~$"):
                continue
            abs_path = os.path.join(path, item_name)

            if os.path.isdir(abs_path):
                node = QTreeWidgetItem([item_name])
                node.setData(0, Qt.UserRole, abs_path)
                node.setData(0, Qt.UserRole + 1, "folder")
                if parent_item is None:
                    self.template_tree.addTopLevelItem(node)
                else:
                    parent_item.addChild(node)
                node.setExpanded(True)
                self._populate_tree_node(node, abs_path)
            elif item_name.endswith((".xlsx", ".xls", ".xlsm")):
                is_sel = (abs_path == self.getlinks_template_path)
                prefix = "● " if is_sel else "○ "
                node = QTreeWidgetItem([f"{prefix}{item_name}"])
                node.setData(0, Qt.UserRole, abs_path)
                node.setData(0, Qt.UserRole + 1, "file")
                if parent_item is None:
                    self.template_tree.addTopLevelItem(node)
                else:
                    parent_item.addChild(node)

    def _on_template_tree_click(self, item, column):
        node_type = item.data(0, Qt.UserRole + 1)
        path = item.data(0, Qt.UserRole)

        if node_type == "folder":
            item.setExpanded(not item.isExpanded())
            return

        if node_type == "file":
            self.getlinks_template_path = path
            self.selected_template_label.setText(f"Đã chọn: {os.path.basename(path)}")
            self._write_log(f"Getlinks template selected: {path}")

            # Update checkmarks
            self._update_tree_checkmarks(self.template_tree.invisibleRootItem(), path)

    def _update_tree_checkmarks(self, parent, selected_path):
        for i in range(parent.childCount()):
            child = parent.child(i)
            c_type = child.data(0, Qt.UserRole + 1)
            c_path = child.data(0, Qt.UserRole)
            if c_type == "file":
                name = os.path.basename(c_path)
                prefix = "● " if c_path == selected_path else "○ "
                child.setText(0, f"{prefix}{name}")
            self._update_tree_checkmarks(child, selected_path)

    # ─── File/Folder pickers ──────────────────────────────────
    def _select_image_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select image folder")
        if folder:
            self.image_folder = folder
            self.image_entry.setText(folder)
            self._auto_fill_sku()
            self._write_log(f"Image folder: {folder}")
            if not self.output_folder:
                suggested = os.path.join(folder, "output")
                self.output_folder = suggested
                self.output_entry.setText(suggested)

    def _select_output_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select output folder")
        if folder:
            self.output_folder = folder
            self.output_entry.setText(folder)
            self._write_log(f"Output folder: {folder}")

    def _select_template_directory(self):
        folder = QFileDialog.getExistingDirectory(self, "Chọn thư mục Getlinks Templates")
        if folder:
            self.template_dir_entry.setText(folder)
            self._populate_template_tree(folder)
            self._write_log(f"Template directory changed to: {folder}")

    def _select_seller_template(self):
        path, _ = QFileDialog.getOpenFileName(self, "Select Walmart seller template", "", "Excel files (*.xlsx *.xlsm *.xls)")
        if path:
            self.seller_template_path = path
            self.seller_template_entry.setText(path)
            self._write_log(f"Seller template: {path}")

    def _select_mapping_file(self):
        path, _ = QFileDialog.getOpenFileName(self, "Select mapping config", "", "Excel files (*.xlsx *.xlsm *.xls)")
        if path:
            self.mapping_path = path
            self.mapping_entry.setText(path)
            self._write_log(f"Mapping config: {path}")
            previous_type = self.product_type_combo.currentText().strip().upper()

            try:
                df = pd.read_excel(path, sheet_name="Product Profiles", dtype=str).fillna("")
                types = df["Product Type"].dropna().unique().tolist()
                types = [str(x).strip().upper() for x in types if str(x).strip()]
                if types:
                    unique_types = list(dict.fromkeys(types))
                    selected_type = previous_type if previous_type in unique_types else unique_types[0]
                    self.product_type_combo.blockSignals(True)
                    self.product_type_combo.clear()
                    self.product_type_combo.addItems(unique_types)
                    self.product_type_combo.setCurrentText(selected_type)
                    self.product_type_combo.blockSignals(False)
                    self._write_log(f"Product Type ID kept: {selected_type}")
                    self._auto_fill_sku()
            except Exception:
                pass

    def _select_update_file(self):
        path, _ = QFileDialog.getOpenFileName(self, "Select update file", "", "Excel/CSV files (*.xlsx *.xlsm *.xls *.csv)")
        if path:
            self.update_file_path = path
            self.update_entry.setText(path)
            self._write_log(f"Update file: {path}")

    # ─── Auto SKU fill ────────────────────────────────────────
    def _auto_fill_sku(self):
        # Tính năng tự động điền Prefix đã được vô hiệu hóa theo yêu cầu
        # để giữ nguyên phần Prefix do người dùng tự nhập tay.
        pass
        # img_folder = self.image_entry.text().strip()
        # if not img_folder:
        #     return
        # folder_name = os.path.basename(img_folder)
        # if not folder_name:
        #     return
        # ptype = self.product_type_combo.currentText().strip()
        # manager = ProductProfileManager(self.mapping_path if self.mapping_path else None)
        # base_sku = manager.get_base_sku(ptype)
        # self.sku_entry.setText(f"{folder_name}{base_sku}")

    # ─── Validation ───────────────────────────────────────────
    def _validate_inputs(self):
        self.image_folder = self.image_entry.text().strip()
        self.seller_template_path = self.seller_template_entry.text().strip()
        self.mapping_path = self.mapping_entry.text().strip()
        self.update_file_path = self.update_entry.text().strip()
        self.output_folder = self.output_entry.text().strip()

        sku_prefix = self.sku_entry.text().strip()
        cloud_folder = self.batch_entry.text().strip()
        product_type = self.product_type_combo.currentText().strip()

        checks = [
            (not self.image_folder or not os.path.isdir(self.image_folder), "Missing image folder", "Please select image folder."),
            (not sku_prefix, "Missing SKU Prefix", "Please enter SKU Prefix."),
            (not self.getlinks_template_path or not os.path.exists(self.getlinks_template_path), "Missing getlinks template", "Please select getlinks/image template."),
            (not self.seller_template_path or not os.path.exists(self.seller_template_path), "Missing Walmart template", "Please select Walmart seller template."),
            (not self.mapping_path or not os.path.exists(self.mapping_path), "Missing mapping config", "Please select mapping config."),
            (self.update_file_path and not os.path.exists(self.update_file_path), "Invalid update file", "Selected update file does not exist."),
            (not cloud_folder, "Missing Cloudinary batch", "Please enter Cloudinary batch name."),
            (not self.output_folder, "Missing output folder", "Please select output folder."),
            (not os.path.exists(self.env_path), "Missing .env file", f"Cannot find .env file:\n{self.env_path}"),
        ]

        for condition, title, msg in checks:
            if condition:
                QMessageBox.critical(self, title, msg)
                return None

        return sku_prefix, cloud_folder, product_type

    # ─── Preview ──────────────────────────────────────────────
    def _preview(self):
        result = self._validate_inputs()
        if not result:
            return

        sku_prefix, cloud_folder, product_type = result
        profile_manager = ProductProfileManager(self.mapping_path)

        try:
            getlinks_df = pd.read_excel(
                self.getlinks_template_path,
                dtype=object,
                keep_default_na=False,
            ).fillna("")
            getlinks_df = normalize_columns(getlinks_df)

            mapping_df = read_mapping_file(self.mapping_path)

            self._write_log("===== PREVIEW =====")
            self._write_log(f"SKU Prefix: {sku_prefix}")
            self._write_log(f"Cloudinary batch: {cloud_folder}")
            self._write_log(f"Getlinks rows: {len(getlinks_df)}")
            self._write_log(f"Mapping enabled rows: {mapping_df['Enabled'].apply(is_enabled).sum()}")

            if "COLOR" in getlinks_df.columns and "SIZE" in getlinks_df.columns:
                for idx, row in getlinks_df.head(10).iterrows():
                    color = row.get("COLOR")
                    size = row.get("SIZE")
                    sku = get_sku_by_color(sku_prefix, color, product_type, profile_manager)
                    final_skuwa = build_full_skuwa_from_row(row, sku_prefix, product_type, profile_manager)
                    self._write_log(f"Row {idx + 1}: {color} / {size} → SKU {sku} / SKUWA {final_skuwa}")

        except Exception as e:
            self._write_log(f"Preview error: {str(e)}")
            QMessageBox.critical(self, "Preview error", str(e))

    # ─── Run All ──────────────────────────────────────────────
    def _start_run_all(self):
        result = self._validate_inputs()
        if not result:
            return

        sku_prefix, cloud_folder, product_type = result
        profile_manager = ProductProfileManager(self.mapping_path)

        self.run_btn.setEnabled(False)
        self.open_btn.setEnabled(False)
        self.progress.setVisible(True)
        self.status_label.setText("Running all steps...")
        self._write_log("===== START RUN ALL =====")

        self.worker = RunAllWorker({
            "image_folder": self.image_folder,
            "output_folder": self.output_folder,
            "sku_prefix": sku_prefix,
            "cloud_folder": cloud_folder,
            "product_type": product_type,
            "profile_manager": profile_manager,
            "do_rename": self.rename_check.isChecked(),
            "getlinks_template_path": self.getlinks_template_path,
            "seller_template_path": self.seller_template_path,
            "mapping_path": self.mapping_path,
            "update_file_path": self.update_file_path,
            "env_path": self.env_path,
        })
        self.worker.log_signal.connect(self._write_log)
        self.worker.finished_signal.connect(self._on_success)
        self.worker.error_signal.connect(self._on_error)
        self.worker.start()

    def _on_success(self, result):
        self.progress.setVisible(False)
        self.run_btn.setEnabled(True)
        self.open_btn.setEnabled(True)
        self.status_label.setText("Completed ✓")
        self.output_xlsx = result["output_xlsx"]

        self._write_log("===== DONE =====")
        self._write_log(f"Final Walmart XLSX: {result['output_xlsx']}")
        self._write_log(f"Mapper log: {result['mapper_log_csv']}")
        self._write_log(f"Getlinks backup CSV: {result['getlinks_csv']}")
        self._write_log(f"Upload log: {result['upload_log_csv']}")

        QMessageBox.information(
            self,
            "Completed",
            f"Final Walmart XLSX:\n{result['output_xlsx']}\n\nMapper log:\n{result['mapper_log_csv']}",
        )

    def _on_error(self, error_message):
        self.progress.setVisible(False)
        self.run_btn.setEnabled(True)
        self.status_label.setText("Error ✗")
        self._write_log(f"ERROR: {error_message}")
        QMessageBox.critical(self, "Error", error_message)

    # ─── Utilities ────────────────────────────────────────────
    def _open_xlsx(self):
        if self.output_xlsx and os.path.exists(self.output_xlsx):
            os.startfile(self.output_xlsx)
        else:
            QMessageBox.warning(self, "No XLSX", "No generated XLSX file found.")

    def _clear_log(self):
        self.log_text.clear()
        self.status_label.setText("Ready")

    def _write_log(self, message):
        self.log_text.append(str(message))

    def _toggle_theme(self, state):
        if self.theme_check.isChecked():
            self.theme_check.setText("🌙 Giao diện tối")
            self.setStyleSheet(LIGHT_STYLESHEET)
        else:
            self.theme_check.setText("☀️ Giao diện sáng")
            self.setStyleSheet(DARK_STYLESHEET)

