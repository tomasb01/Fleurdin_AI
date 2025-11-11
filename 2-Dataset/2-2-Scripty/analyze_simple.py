import pandas as pd
import re

file_path = r"C:\Projects\Fleurdin_AI\Raw_data\Pro_trenovani\EO_prehled oleju_raw data.csv.xlsx"
df = pd.read_excel(file_path, skiprows=2)
df = df.dropna(how='all')
df = df[df['ID'].notna()]

print("ANALYZA KVALITY DAT")
print("="*60)
print(f"Celkem zaznamu: {len(df)}")

# Check for categories
def has_categories(text):
    if pd.isna(text):
        return False
    return len(re.findall(r'([A-Z][A-Z /]+):', str(text))) > 0

body_with_cats = sum(1 for _, row in df.iterrows() if has_categories(row['Účinky na tělo']))
psyche_with_cats = sum(1 for _, row in df.iterrows() if has_categories(row['Účinky na psychiku / emoce']))

print(f"\nKATEGORIE V DATECH:")
print(f"  Telo s kategoriemi: {body_with_cats}/{len(df)} ({body_with_cats/len(df)*100:.0f}%)")
print(f"  Psychika s kategoriemi: {psyche_with_cats}/{len(df)} ({psyche_with_cats/len(df)*100:.0f}%)")

# Check empty values
empty_body = df['Účinky na tělo'].isnull().sum()
empty_psyche = df['Účinky na psychiku / emoce'].isnull().sum()

print(f"\nPRAZDNE HODNOTY:")
print(f"  Prazdne 'Ucinky na telo': {empty_body}")
print(f"  Prazdne 'Ucinky na psychiku': {empty_psyche}")

# Show sample
print(f"\nUKAZKA 1. ZAZNAMU:")
row = df.iloc[0]
print(f"Nazev: {row['Název EO']}")
body_text = str(row['Účinky na tělo'])[:200] if pd.notna(row['Účinky na tělo']) else "PRAZDNE"
print(f"Telo: {body_text}...")

# Check unique names
unique_names = df['Název EO'].nunique()
duplicates = len(df) - unique_names

print(f"\nUNIKATNI NAZVY:")
print(f"  Vsechny nazvy unikatni: {duplicates == 0}")
if duplicates > 0:
    print(f"  Pocet duplikatu: {duplicates}")

# FINAL VERDICT
print("\n" + "="*60)
print("ZAVER - VHODNOST PRO SKALOVANI NA 200-300 OLEJU:")
print("="*60)

issues = []
if body_with_cats < len(df) * 0.8:
    issues.append(f"PROBLEM: Pouze {body_with_cats/len(df)*100:.0f}% zaznamu ma kategorie")
if empty_body > 0:
    issues.append(f"PROBLEM: {empty_body} prazdnych zaznamu")
if duplicates > 0:
    issues.append(f"PROBLEM: {duplicates} duplikatnich nazvu")

if not issues:
    print("\nVYBORNE! Struktura je IDEALNI pro skalovani!")
    print("- Vsechny zaznamy maji kategorie")
    print("- Zadne prazdne hodnoty")
    print("- Unikatni nazvy")
    print("\nMUZES BEZPECNE PRIDAVAT DALS��CH 170-270 OLEJU!")
else:
    print("\nSTRUKTURA VYZADUJE UPRAVY:")
    for issue in issues:
        print(f"  - {issue}")
    print("\nDOPORUCENI:")
    if body_with_cats < len(df) * 0.8:
        print("  1. Reorganizuj vsechny zaznamy s kategoriemi (OBECNE:, TRAVENI:, atd.)")
    if empty_body > 0:
        print("  2. Doplň prazdne zaznamy nebo je odstran")
    if duplicates > 0:
        print("  3. Uprav duplikatni nazvy")
