import pandas as pd
import re

# Load data
file_path = r"C:\Projects\Fleurdin_AI\Raw_data\Pro_trenovani\EO_prehled oleju_raw data.csv.xlsx"
df = pd.read_excel(file_path, skiprows=2)
df = df.dropna(how='all')
df = df[df['ID'].notna()]

print("="*60)
print("ANALYZA KVALITY DAT PRO DLOUHODOBE POUZITI")
print("="*60)

print(f"\nCelkem zaznamu: {len(df)}")
print(f"Sloupce: {list(df.columns)}")

print("\n" + "-"*60)
print("1. KONTROLA PRÁZDNÝCH HODNOT")
print("-"*60)
null_counts = df.isnull().sum()
for col, count in null_counts.items():
    status = "❌ PROBLÉM" if count > len(df) * 0.3 else "✅ OK"
    percentage = (count / len(df)) * 100
    print(f"{status} {col}: {count} prázdných ({percentage:.1f}%)")

print("\n" + "-"*60)
print("2. KONTROLA STRUKTURY KATEGORIÍ")
print("-"*60)

def check_categories(text):
    """Check if text contains category markers"""
    if pd.isna(text):
        return False, []
    categories = re.findall(r'([A-ZĚŠČŘŽÝÁÍÉÚŮŇ/ ]+):', str(text))
    return len(categories) > 0, categories

# Check body effects
body_with_cats = 0
body_categories_found = set()
for idx, row in df.iterrows():
    has_cats, cats = check_categories(row['Účinky na tělo'])
    if has_cats:
        body_with_cats += 1
        body_categories_found.update(cats)

print(f"\n📊 Účinky na tělo:")
print(f"   Záznamy s kategoriemi: {body_with_cats}/{len(df)} ({body_with_cats/len(df)*100:.1f}%)")
if body_categories_found:
    print(f"   Nalezené kategorie: {sorted(body_categories_found)}")
else:
    print(f"   ❌ ŽÁDNÉ KATEGORIE NALEZENY!")

# Check psyche effects
psyche_with_cats = 0
psyche_categories_found = set()
for idx, row in df.iterrows():
    has_cats, cats = check_categories(row['Účinky na psychiku / emoce'])
    if has_cats:
        psyche_with_cats += 1
        psyche_categories_found.update(cats)

print(f"\n📊 Účinky na psychiku:")
print(f"   Záznamy s kategoriemi: {psyche_with_cats}/{len(df)} ({psyche_with_cats/len(df)*100:.1f}%)")
if psyche_categories_found:
    print(f"   Nalezené kategorie: {sorted(psyche_categories_found)}")
else:
    print(f"   ⚠️ Žádné kategorie (ale může být v pořádku)")

print("\n" + "-"*60)
print("3. KONTROLA DÉLKY OBSAHU")
print("-"*60)

body_lengths = []
psyche_lengths = []
for idx, row in df.iterrows():
    body_text = str(row['Účinky na tělo']) if pd.notna(row['Účinky na tělo']) else ""
    psyche_text = str(row['Účinky na psychiku / emoce']) if pd.notna(row['Účinky na psychiku / emoce']) else ""
    body_lengths.append(len(body_text))
    psyche_lengths.append(len(psyche_text))

print(f"\n📏 Účinky na tělo:")
print(f"   Průměrná délka: {sum(body_lengths)/len(body_lengths):.0f} znaků")
print(f"   Min: {min(body_lengths)}, Max: {max(body_lengths)}")
print(f"   Prázdné/velmi krátké (<50 znaků): {sum(1 for l in body_lengths if l < 50)}")

print(f"\n📏 Účinky na psychiku:")
print(f"   Průměrná délka: {sum(psyche_lengths)/len(psyche_lengths):.0f} znaků")
print(f"   Min: {min(psyche_lengths)}, Max: {max(psyche_lengths)}")
print(f"   Prázdné/velmi krátké (<50 znaků): {sum(1 for l in psyche_lengths if l < 50)}")

print("\n" + "-"*60)
print("4. UKÁZKA PRVNÍCH 2 ZÁZNAMŮ")
print("-"*60)

for i in range(min(2, len(df))):
    row = df.iloc[i]
    print(f"\n🌿 {i+1}. {row['Název EO']}")
    print(f"   ID: {row['ID']}")

    body = str(row['Účinky na tělo'])[:300] if pd.notna(row['Účinky na tělo']) else "PRÁZDNÉ"
    print(f"   Účinky na tělo (ukázka): {body}...")

    psyche = str(row['Účinky na psychiku / emoce'])[:200] if pd.notna(row['Účinky na psychiku / emoce']) else "PRÁZDNÉ"
    print(f"   Psychika: {psyche}...")

print("\n" + "="*60)
print("5. DOPORUČENÍ PRO ŠKÁLOVÁNÍ NA 200-300 OLEJŮ")
print("="*60)

recommendations = []

# Check consistency
if body_with_cats < len(df) * 0.8:
    recommendations.append("❌ KRITICKÉ: Méně než 80% záznamů má kategorie v 'Účinky na tělo'")
    recommendations.append("   → DOPORUČENÍ: Reorganizuj všechny záznamy s kategoriemi")
else:
    recommendations.append("✅ Kategorie jsou konzistentně použity")

# Check empty values
empty_body = df['Účinky na tělo'].isnull().sum()
if empty_body > 0:
    recommendations.append(f"⚠️ {empty_body} záznamů má prázdné 'Účinky na tělo'")
    recommendations.append("   → DOPORUČENÍ: Doplň data nebo odstraň tyto záznamy")

# Check naming
unique_names = df['Název EO'].nunique()
if unique_names != len(df):
    recommendations.append(f"❌ PROBLÉM: Duplikátní názvy olejů ({len(df) - unique_names} duplikátů)")
    recommendations.append("   → DOPORUČENÍ: Každý olej musí mít unikátní název")
else:
    recommendations.append("✅ Všechny názvy olejů jsou unikátní")

print("\n")
for rec in recommendations:
    print(rec)

print("\n" + "="*60)
print("ZÁVĚR - JE STRUKTURA VHODNÁ PRO ŠKÁLOVÁNÍ?")
print("="*60)

if body_with_cats >= len(df) * 0.8 and empty_body == 0 and unique_names == len(df):
    print("\n✅✅✅ VÝBORNĚ! Struktura je IDEÁLNÍ pro škálování na 200-300 olejů!")
    print("Můžeš bezpečně přidávat další oleje se stejnou strukturou.")
elif body_with_cats >= len(df) * 0.5:
    print("\n⚠️ DOBRÁ STRUKTURA, ale vyžaduje drobné úpravy před škálováním.")
    print("Oprav výše uvedené problémy a pak můžeš škálovat.")
else:
    print("\n❌ STRUKTURA VYŽADUJE REORGANIZACI před škálováním!")
    print("Reorganizuj data podle doporučení výše.")

print("\n" + "="*60)
