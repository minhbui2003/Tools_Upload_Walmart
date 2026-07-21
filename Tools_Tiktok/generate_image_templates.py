import os

from core.tiktok_generator import create_tiktok_image_mixing_template


os.makedirs("templates", exist_ok=True)

create_tiktok_image_mixing_template(
    "templates/Tiktok_Image_Mixing_Mens.xlsx",
    profile_key="mens_tshirt",
)
create_tiktok_image_mixing_template(
    "templates/Tiktok_Image_Mixing_Womens.xlsx",
    profile_key="womens_tshirt",
)

print("Generated image mixing templates.")
