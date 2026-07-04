"""
QThread worker for running the upload pipeline in the background.
"""
from PySide6.QtCore import QThread, Signal


class RunAllWorker(QThread):
    log_signal = Signal(str)
    finished_signal = Signal(dict)
    error_signal = Signal(str)

    def __init__(self, params, parent=None):
        super().__init__(parent)
        self.params = params

    def run(self):
        import os
        import shutil
        from core.image import rename_images
        from core.getlinks import process_getlinks_template
        from core.mapper import generate_walmart_xlsx_from_getlinks_df

        p = self.params
        try:
            os.makedirs(p["output_folder"], exist_ok=True)

            image_folder_for_upload = p["image_folder"]
            renamed_folder = os.path.join(p["output_folder"], "renamed_images")

            if p["do_rename"]:
                self.log_signal.emit("Step 1: Rename images")

                if os.path.exists(renamed_folder):
                    shutil.rmtree(renamed_folder)

                os.makedirs(renamed_folder, exist_ok=True)

                renamed_count, skipped_count, rename_log = rename_images(
                    input_folder=p["image_folder"],
                    output_folder=renamed_folder,
                    sku_prefix=p["sku_prefix"],
                    product_type=p["product_type"],
                    profile_manager=p["profile_manager"],
                    log_callback=self.log_signal.emit,
                )

                image_folder_for_upload = renamed_folder

                self.log_signal.emit(f"Rename done: {renamed_count} renamed, {skipped_count} skipped")
                self.log_signal.emit(f"Rename log: {rename_log}")
            else:
                self.log_signal.emit("Step 1: Rename skipped")

            self.log_signal.emit("Step 2: Upload images and generate getlinks data")

            getlinks_df, getlinks_csv, upload_log_csv = process_getlinks_template(
                template_path=p["getlinks_template_path"],
                image_folder=image_folder_for_upload,
                output_folder=p["output_folder"],
                env_path=p["env_path"],
                sku_prefix=p["sku_prefix"],
                cloud_folder=p["cloud_folder"],
                product_type=p["product_type"],
                profile_manager=p["profile_manager"],
                log_callback=self.log_signal.emit,
            )

            self.log_signal.emit(f"Getlinks output: {getlinks_csv}")
            self.log_signal.emit(f"Upload log: {upload_log_csv}")

            self.log_signal.emit("Step 3: Fill Walmart XLSX template")

            output_xlsx, mapper_log_csv = generate_walmart_xlsx_from_getlinks_df(
                seller_template_path=p["seller_template_path"],
                getlinks_df=getlinks_df,
                mapping_path=p["mapping_path"],
                update_file_path=p["update_file_path"],
                output_folder=p["output_folder"],
                sku_prefix=p["sku_prefix"],
                product_type=p["product_type"],
                profile_manager=p["profile_manager"],
                log_callback=self.log_signal.emit,
            )

            self.finished_signal.emit({
                "output_xlsx": output_xlsx,
                "mapper_log_csv": mapper_log_csv,
                "getlinks_csv": getlinks_csv,
                "upload_log_csv": upload_log_csv,
            })

        except Exception as e:
            self.error_signal.emit(str(e))
