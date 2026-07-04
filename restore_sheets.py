import pandas as pd

source = r"sample-files\Tshirt_mapping_config.xlsx"
target = r"sample-files\Sweatshirt_mapping_config.xlsx"

# Read the current Mapping sheet from the broken target
mapping_df = pd.read_excel(target, sheet_name="Mapping")

# Read all sheets from source
xl = pd.ExcelFile(source)

with pd.ExcelWriter(target, engine="openpyxl") as writer:
    # Write the fixed mapping first
    mapping_df.to_excel(writer, sheet_name="Mapping", index=False)
    
    # Copy all other sheets from source
    for sheet in xl.sheet_names:
        if sheet != "Mapping":
            df = pd.read_excel(source, sheet_name=sheet)
            df.to_excel(writer, sheet_name=sheet, index=False)

print("Restored missing sheets from Tshirt config!")
