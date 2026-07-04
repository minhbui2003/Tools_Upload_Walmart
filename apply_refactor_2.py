import sys

def apply():
    with open('upload_toni.py', 'r', encoding='utf-8') as f:
        content = f.read()

    # 1. Update ProductProfileManager dictionary
    content = content.replace(
        '"Base SKU Shift": clean_text(row.get("Base SKU Shift"))',
        '"Base SKU Shift": clean_text(row.get("Base SKU Shift")),\n                    "Base SKU": clean_text(row.get("Base SKU"))'
    )
    content = content.replace(
        '"Base SKU Shift": ""}',
        '"Base SKU Shift": "", "Base SKU": "UGNT1"}'
    )
    content = content.replace(
        '"Base SKU Shift": "4"}',
        '"Base SKU Shift": "4", "Base SKU": "UGNT1"}'
    )
    content = content.replace(
        '"Base SKU Shift": "3"}',
        '"Base SKU Shift": "3", "Base SKU": "UGNT1"}'
    )
    
    # Add get_base_sku method
    get_base_sku_method = """
    def get_base_sku(self, product_type):
        rules = self.get_rules_for_type(product_type)
        if rules and "Base SKU" in rules[0]:
            return rules[0]["Base SKU"]
        return ""

    def get_color_rule(self, product_type, color_name):"""
    content = content.replace("    def get_color_rule(self, product_type, color_name):", get_base_sku_method)

    # Add fallback to get_color_rule
    content = content.replace(
        'return {"Color Name": color_upper, "Image Suffix": suffix, "SKUWA Letter": "", "Base SKU Shift": ""}',
        'return {"Color Name": color_upper, "Image Suffix": suffix, "SKUWA Letter": "", "Base SKU Shift": "", "Base SKU": ""}'
    )

    # 2. Add auto_fill_sku to UploadToniApp
    auto_fill_method = """
    def auto_fill_sku(self, event=None):
        img_folder = self.image_entry.get().strip()
        if not img_folder:
            return
        import os
        folder_name = os.path.basename(img_folder)
        if not folder_name:
            return
            
        ptype = self.product_type_var.get().strip()
        mapping_path = getattr(self, "mapping_path", None)
        manager = ProductProfileManager(mapping_path)
        base_sku = manager.get_base_sku(ptype)
        
        self.sku_var.set(f"{folder_name}{base_sku}")

    def select_image_folder(self):"""
    content = content.replace("    def select_image_folder(self):", auto_fill_method)

    # 3. Call auto_fill_sku inside select_image_folder
    content = content.replace(
        'self.write_log(f"Image folder: {path}")',
        'self.write_log(f"Image folder: {path}")\n            self.auto_fill_sku()'
    )

    # 4. Call auto_fill_sku inside select_mapping_file
    content = content.replace(
        'self.product_type_var.set(unique_types[0])',
        'self.product_type_var.set(unique_types[0])\n                    self.auto_fill_sku()'
    )

    # 5. Bind auto_fill_sku to Combobox
    content = content.replace(
        'self.product_type_entry.pack(fill="x")',
        'self.product_type_entry.pack(fill="x")\n        self.product_type_entry.bind("<<ComboboxSelected>>", self.auto_fill_sku)\n        self.product_type_entry.bind("<FocusOut>", self.auto_fill_sku)'
    )

    with open('upload_toni.py', 'w', encoding='utf-8') as f:
        f.write(content)
        
    print("Successfully patched upload_toni.py")

if __name__ == "__main__":
    apply()
