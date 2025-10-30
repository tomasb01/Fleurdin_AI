import pandas as pd

# Load Excel file
file_path = r"C:\Projects\Fleurdin_AI\Raw_data\Pro_trenovani\EO_prehled oleju_raw data.csv.xlsx"

print("Loading Excel file...")
df = pd.read_excel(file_path, skiprows=2)
df = df.dropna(how='all')

print(f"\nShape: {df.shape}")
print(f"\nColumns: {list(df.columns)}")
print(f"\nFirst 5 rows:\n")
print(df.head())
print(f"\nData types:\n{df.dtypes}")
