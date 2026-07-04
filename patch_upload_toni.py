import os, json, re

file_path = 'd:/POD/Tools/POD_Marketplace/Upload-Toni/upload_toni.py'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

if 'import json' not in content:
    content = content.replace('import os', 'import os\nimport json', 1)

content = content.replace('self.output_xlsx = ""\n\n        self.build_ui()', 'self.output_xlsx = ""\n        self.config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "app_config.json")\n\n        self.build_ui()')

content = content.replace('self.log_text.configure(yscrollcommand=scrollbar.set)', 'self.log_text.configure(yscrollcommand=scrollbar.set)\n        self.load_config()')

old_mapping = '''                    self.product_type_entry['values'] = unique_types
                    if self.product_type_var.get() not in unique_types:'''
new_mapping = '''                    self.product_type_entry['values'] = unique_types
                    if self.product_type_var.get().strip().upper() not in unique_types:'''
content = content.replace(old_mapping, new_mapping)

save_load_code = '''
    def load_config(self):
        if hasattr(self, "config_path") and os.path.exists(self.config_path):
            try:
                with open(self.config_path, "r", encoding="utf-8") as f:
                    config = json.load(f)
                
                if "image_folder" in config and config["image_folder"]:
                    self.image_folder = config["image_folder"]
                    self.set_entry(self.image_entry, self.image_folder)
                if "getlinks_template_path" in config and config["getlinks_template_path"]:
                    self.getlinks_template_path = config["getlinks_template_path"]
                    import os
                    self.selected_template_label.config(text=f"Đã chọn: {os.path.basename(self.getlinks_template_path)}")
                if "seller_template_path" in config and config["seller_template_path"]:
                    self.seller_template_path = config["seller_template_path"]
                    self.set_entry(self.seller_template_entry, self.seller_template_path)
                if "mapping_path" in config and config["mapping_path"]:
                    self.mapping_path = config["mapping_path"]
                    self.set_entry(self.mapping_entry, self.mapping_path)
                if "update_file_path" in config and config["update_file_path"]:
                    self.update_file_path = config["update_file_path"]
                    self.set_entry(self.update_entry, self.update_file_path)
                if "output_folder" in config and config["output_folder"]:
                    self.output_folder = config["output_folder"]
                    self.set_entry(self.output_entry, self.output_folder)
                    
                if "product_type" in config and config["product_type"]:
                    self.product_type_var.set(config["product_type"])
                if "cloudinary_batch_name" in config and config["cloudinary_batch_name"]:
                    self.cloudinary_batch_name.delete(0, 'end')
                    self.cloudinary_batch_name.insert(0, config["cloudinary_batch_name"])
                    
                self.auto_fill_sku()
            except Exception as e:
                self.write_log(f"Error loading config: {e}")

    def save_config(self, event=None):
        if not hasattr(self, "config_path"): return
        config = {
            "image_folder": getattr(self, "image_folder", ""),
            "getlinks_template_path": getattr(self, "getlinks_template_path", ""),
            "seller_template_path": getattr(self, "seller_template_path", ""),
            "mapping_path": getattr(self, "mapping_path", ""),
            "update_file_path": getattr(self, "update_file_path", ""),
            "output_folder": getattr(self, "output_folder", ""),
            "product_type": self.product_type_var.get(),
            "cloudinary_batch_name": self.cloudinary_batch_name.get()
        }
        try:
            with open(self.config_path, "w", encoding="utf-8") as f:
                import json
                json.dump(config, f, indent=4)
        except Exception:
            pass
'''

content = content.replace('    def write_log(self, message):', save_load_code + '\n    def write_log(self, message):')

content = content.replace('self.product_type_entry.bind("<<ComboboxSelected>>", self.auto_fill_sku)', 'self.product_type_entry.bind("<<ComboboxSelected>>", lambda e: [self.auto_fill_sku(), self.save_config()])')
content = content.replace('self.cloudinary_batch_name.bind("<FocusOut>", self.update_batch_name_state)', 'self.cloudinary_batch_name.bind("<FocusOut>", lambda e: [self.update_batch_name_state(), self.save_config()])')

for log_line in [
    'self.write_log(f"Image folder: {folder}")',
    'self.write_log(f"Output folder: {folder}")',
    'self.write_log(f"Getlinks template selected: {self.getlinks_template_path}")',
    'self.write_log(f"Seller template: {path}")',
    'self.write_log(f"Mapping config: {path}")',
    'self.write_log(f"Update file: {path}")'
]:
    content = content.replace(log_line, log_line + '\n            self.save_config()')

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)
print("Patched successfully!")
