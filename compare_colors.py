import pandas as pd
file_path = r"D:/POD/Tools/POD_Marketplace/Upload-Toni/Source/Tools_Marketplace/mapping/Sweatshirt_mapping_config_woman.xlsx"
df = pd.read_excel(file_path, sheet_name="Mapping")
matches = df[df["Source Type"].str.contains("fixed", case=False, na=False)]
print(matches[["Seller Column", "Fixed Value"]].head(20))
