import pandas as pd
import re

file_path = r"C:\Projects\Fleurdin_AI\Raw_data\Pro_trenovani\EO_prehled oleju_raw data.csv.xlsx"
df = pd.read_excel(file_path, skiprows=2)
df = df.dropna(how='all')
df = df[df['ID'].notna()]

print("HLEDANI OLEJU BEZ KATEGORII V 'UCINKY NA TELO'")
print("="*60)

def has_categories(text):
    if pd.isna(text):
        return False
    # Look for pattern like "OBECNE:", "TRAVENI:", etc.
    categories = re.findall(r'([A-ZĚŠČŘŽÝÁÍÉÚŮŇ][A-ZĚŠČŘŽÝÁÍÉÚŮŇ /]+):', str(text))
    return len(categories) > 0

# Find oils without categories
oils_without_categories = []

for idx, row in df.iterrows():
    has_cats = has_categories(row['Účinky na tělo'])
    if not has_cats:
        oils_without_categories.append({
            'ID': row['ID'],
            'Nazev': row['Název EO'],
            'Ucinky_na_telo': str(row['Účinky na tělo'])[:500]
        })

print(f"\nCelkem oleju BEZ kategorii: {len(oils_without_categories)}\n")

if oils_without_categories:
    for oil in oils_without_categories:
        print(f"ID: {oil['ID']}")
        print(f"Nazev: {oil['Nazev']}")
        print(f"Ucinky na telo:")
        print(f"  {oil['Ucinky_na_telo']}")
        print("\n" + "-"*60 + "\n")
else:
    print("VSECHNY OLEJE MAJI KATEGORIE!")

print("\nDOPORUCENI:")
if oils_without_categories:
    print("Doplň kategorie u vyse uvedenych oleju ve formatu:")
    print("OBECNE: ..., TRAVENI: ..., KUZE: ..., atd.")
else:
    print("Vše je v poradku!")
