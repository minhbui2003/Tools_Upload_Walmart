import pandas as pd
import glob
files = glob.glob(r"d:\POD\Tools\POD_Marketplace\Upload-Toni\templates\swe*.xlsx") + glob.glob(r"d:\POD\Tools\POD_Marketplace\Upload-Toni\templates\tshirt1*.xlsx")
for f in sorted(files):
    if "~$" in f: continue
    df = pd.read_excel(f)
    print(f"=== {f.split(chr(92))[-1]} ===")
    print(df.head(2).to_string())
    print("\n")
