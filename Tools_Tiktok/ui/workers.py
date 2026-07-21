"""
Background workers for the TikTok upload UI.
"""
from PySide6.QtCore import QThread, Signal


class TiktokRunWorker(QThread):
    log_signal = Signal(str)
    finished_signal = Signal(dict)
    error_signal = Signal(str)

    def __init__(self, params, parent=None):
        super().__init__(parent)
        self.params = params

    def run(self):
        try:
            from core.tiktok_generator import generate_tiktok_upload_file

            output_xlsx, log_csv = generate_tiktok_upload_file(
                template_path=self.params["template_path"],
                image_folder=self.params["image_folder"],
                output_folder=self.params["output_folder"],
                sku_prefix=self.params["sku_prefix"],
                profile_key=self.params["profile_key"],
                cloud_folder=self.params["cloud_folder"],
                env_path=self.params["env_path"],
                product_name=self.params.get("product_name", ""),
                product_description=self.params.get("product_description", ""),
                brand=self.params.get("brand", "No brand"),
                price=self.params.get("price", 19.99),
                quantity=self.params.get("quantity", 100),
                size_chart=self.params.get("size_chart", "7660455797738030862"),
                update_file_path=self.params["update_file_path"],
                image_mixing_path=self.params["image_mixing_path"],
                mapping_path=self.params["mapping_path"],
                upload_images=True,
                log_callback=self.log_signal.emit,
            )

            self.finished_signal.emit({"output_xlsx": output_xlsx, "log_csv": log_csv})
        except Exception as exc:
            self.error_signal.emit(str(exc))
