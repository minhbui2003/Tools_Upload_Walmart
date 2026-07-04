import pandas as pd
import os

template_dir = r"d:\POD\Tools\POD_Marketplace\Upload-Toni\templates"
swe_original = os.path.join(template_dir, "swe_template.xlsx")

# Load original
df1 = pd.read_excel(swe_original)

# Save as swe1_template.xlsx (same as original)
df1.to_excel(os.path.join(template_dir, "swe1_template.xlsx"), index=False)

# Helper function to swap mockups
def swap_mockups(df, new_main, new_add2, new_add3):
    new_df = df.copy()
    # The original mockups are prefix-color. 
    # For example MK3-AntiqueCherryRed
    # We will replace the prefix MK3, MK4, MK2 with the new ones.
    
    # Define how to map old to new for this specific permutation
    # Original is MK3 (Main), MK4 (Add 2), MK2 (Add 3)
    def map_val(val, target_prefix):
        if pd.isna(val): return val
        # Extract the color part after the dash
        if "-" in str(val):
            parts = str(val).split("-", 1)
            return f"{target_prefix}-{parts[1]}"
        return val

    new_df['Main'] = df['Main'].apply(lambda x: map_val(x, new_main))
    new_df['Add 2'] = df['Add 2'].apply(lambda x: map_val(x, new_add2))
    new_df['Add 3'] = df['Add 3'].apply(lambda x: map_val(x, new_add3))
    
    return new_df

# SWE2: Main=MK2, Add2=MK3, Add3=MK4
df2 = swap_mockups(df1, "MK2", "MK3", "MK4")
df2.to_excel(os.path.join(template_dir, "swe2_template.xlsx"), index=False)

# SWE3: Main=MK4, Add2=MK2, Add3=MK3
df3 = swap_mockups(df1, "MK4", "MK2", "MK3")
df3.to_excel(os.path.join(template_dir, "swe3_template.xlsx"), index=False)

# SWE4: Main=MK3, Add2=MK2, Add3=MK4
df4 = swap_mockups(df1, "MK3", "MK2", "MK4")
df4.to_excel(os.path.join(template_dir, "swe4_template.xlsx"), index=False)

# SWE5: Main=MK5, Add2=MK3, Add3=MK4
df5 = swap_mockups(df1, "MK5", "MK3", "MK4")
df5.to_excel(os.path.join(template_dir, "swe5_template.xlsx"), index=False)

# SWE6: Main=MK6, Add2=MK3, Add3=MK4
df6 = swap_mockups(df1, "MK6", "MK3", "MK4")
df6.to_excel(os.path.join(template_dir, "swe6_template.xlsx"), index=False)

print("Created 6 SWE templates.")
