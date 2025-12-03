"""
FLEURDIN AI - PARSING SCRIPT
=============================
Načte zdrojové soubory a vytvoří čisté stringy.
"""

import pandas as pd
import json
from docx import Document
from pathlib import Path

# Cesty ke zdrojovým souborům
BASE_PATH = Path("/Users/atlas/Projects/Fleurdin_AI/2-Dataset/2-1-Raw_data")

# Esenciální oleje
OILS_FILE = BASE_PATH / "Fleurdin/EO_prehled oleju_30oils_updated.csv.xlsx"

# Bylinky
BYLINKY_PATH = BASE_PATH / "Bylinky_DivokaStrava/Data"
BOOK1_FILE = BYLINKY_PATH / "Liečivá sila divokých byliniek_po RU_1.2.2023.docx"
BOOK2_FILE = BYLINKY_PATH / "kniha2_hlavny text_rkp_NP_uprava 22-1-25.docx"
DRIENKY_FILE = BYLINKY_PATH / "DRIENKY.docx"

# Výstup
OUTPUT_FILE = Path("/Users/atlas/Projects/Fleurdin_AI/4-RAG_Pipeline/parsed_data.json")


print("="*70)
print("🚀 FLEURDIN AI - PARSING ZAČÍNÁ")
print("="*70)
  
def parse_essential_oils(excel_path):
    """
    Načte Excel s esenciálními oleji a vrátí čisté stringy
    """
    print("\n📦 PARSING: Esenciální oleje")
      
    print("-" * 70)

    # Načti Excel
    df = pd.read_excel(excel_path)

    oils = []

    # Projdi řádky (od řádku 2, protože první 2 jsou hlavička)
    for idx, row in df.iterrows():
        if idx < 2:  # Přeskoč hlavičku
            continue

        # Přečti data z řádku
        oil_id = row.iloc[0]
        name = row.iloc[1]
        english_name = row.iloc[2]
        latin_name = row.iloc[3]
        frequency = row.iloc[4]
        body_effects = str(row.iloc[5]) if pd.notna(row.iloc[5]) else ""
        psyche_effects = str(row.iloc[6]) if pd.notna(row.iloc[6]) else ""

        # Přeskoč prázdné řádky
        if pd.isna(name) or name == "":
            continue

        # Vytvoř čistý string (text chunk)
        text = f"""OLEJ: {name}

ÚČINKY NA TĚLO:
{body_effects}

ÚČINKY NA PSYCHIKU:
{psyche_effects}"""

        # Ulož jako dictionary
        oil_data = {
            "id": f"oil_{int(oil_id) if pd.notna(oil_id) else idx}",
            "type": "essential_oil",
            "name": name,
            "text": text,
            "metadata": {
                "english_name": english_name if pd.notna(english_name) else "",
                "latin_name": latin_name if pd.notna(latin_name) else "",
                "frequency": frequency if pd.notna(frequency) else ""
            }
        }

        oils.append(oil_data)
        print(f"  ✅ {name}")

    print(f"\n  📊 Celkem načteno: {len(oils)} olejů")
    return oils
    
def parse_word_document(doc_path, doc_name):
    """
    Načte Word dokument a vrátí odstavce jako stringy
    """
    print(f"\n📦 PARSING: {doc_name}")
    print("-" * 70)

    # Načti Word dokument
    doc = Document(doc_path)

    paragraphs = []

    # Projdi všechny odstavce
    for i, para in enumerate(doc.paragraphs):
        text = para.text.strip()

        # Přeskoč prázdné odstavce
        if not text or len(text) < 10:
            continue

        # Ulož odstavec
        para_data = {
            "id": f"{doc_name}_para_{i+1}",
            "type": "paragraph",
            "text": text,
            "metadata": {
                "source": doc_name,
                "paragraph_number": i+1
            }
        }

        paragraphs.append(para_data)

    print(f"  📊 Celkem načteno: {len(paragraphs)} odstavců")
    print(f"  📏 Celková délka: {sum(len(p['text']) for p in paragraphs):,} znaků")

    return paragraphs
    
def main():
    """
    Hlavní funkce - spustí parsing všech souborů
    """

    # 1. Parse esenciální oleje
    oils = parse_essential_oils(OILS_FILE)

    # 2. Parse knihu 1
    book1 = parse_word_document(BOOK1_FILE, "book1")

    # 3. Parse knihu 2
    book2 = parse_word_document(BOOK2_FILE, "book2")

    # 4. Parse DRIENKY (voice přepis)
    drienky = parse_word_document(DRIENKY_FILE, "drienky")

    # Spoj všechno dohromady
    all_data = {
        "essential_oils": oils,
        "book1": book1,
        "book2": book2,
        "drienky": drienky,
        "stats": {
            "total_items": len(oils) + len(book1) + len(book2) + len(drienky),
            "essential_oils_count": len(oils),
            "book1_count": len(book1),
            "book2_count": len(book2),
            "drienky_count": len(drienky)
        }
    }

    # Ulož do JSON
    print("\n" + "="*70)
    print("💾 UKLÁDÁM DATA")
    print("="*70)

    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(all_data, f, ensure_ascii=False, indent=2)

    print(f"\n✅ HOTOVO!")
    print(f"📂 Výstup: {OUTPUT_FILE}")
    print(f"\n📊 STATISTIKY:")
    print(f"  • Esenciální oleje: {len(oils)}")
    print(f"  • Kniha 1: {len(book1)} odstavců")
    print(f"  • Kniha 2: {len(book2)} odstavců")
    print(f"  • DRIENKY: {len(drienky)} odstavců")
    print(f"  • CELKEM: {all_data['stats']['total_items']} položek")
    print("\n" + "="*70)

# Spusť program
if __name__ == "__main__":
    main()