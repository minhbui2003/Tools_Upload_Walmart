# TikTok POD Upload Tool

Desktop tool for generating TikTok Seller Center upload workbooks from a blank TikTok template, seller update file, image folder, image mixing file, and full mapping file.

## Run From Source

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

Create `.env` from `.env.example` and fill Cloudinary credentials before generating upload files.

## Files To Select

Women:

- TikTok template: `Files/Tiktoksellercenter_160726HN6_20260714_Women's blank template.xlsx`
- Image folder: the folder containing women mockups, for example `Files/Woman`
- Update file: `templates/Tiktok_Update_Womens_Tshirt.xlsx`
- Image mixing file: `templates/Tiktok_Image_Mixing_Womens.xlsx`
- Mapping file: `templates/Tiktok_Mapping_Womens_Tshirt_Full.xlsx`

Men:

- TikTok template: `Tiktoksellercenter_Menswear & Underwear_Template.xlsx`
- Image folder: the folder containing men mockups
- Update file: `templates/Tiktok_Update_Mens_Tshirt.xlsx`
- Image mixing file: `templates/Tiktok_Image_Mixing_Mens.xlsx`
- Mapping file: `templates/Tiktok_Mapping_Mens_Tshirt_Full.xlsx`

## Mapping Source Types

- `auto`: use tool-generated values, with update-file fallback where supported.
- `getlinks`: resolve images from the selected image folder by MK code.
- `update_file`: read the update file column named in `Source Value`.
- `fixed`: write `Fixed Value`.
- `blank`: write an empty value.
- `skip`: do not manage that TikTok column.

## Build Release Locally

```bash
python generate_tiktok_templates.py
pyinstaller --onefile --windowed --name Tools_Tiktok main.py
```

Generated release packages should include the executable/app, `.env.example`, and the generated `templates/` folder. The `Files/` folder and TikTok blank templates are intentionally not committed; users can select their own downloaded TikTok blank template in the UI.
