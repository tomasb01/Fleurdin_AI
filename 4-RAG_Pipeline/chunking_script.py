"""
FLEURDIN AI - CHUNKING SCRIPT
==============================
Rozdělí dlouhé texty na menší chunky (1,200 znaků).
"""

import json
from pathlib import Path
from typing import List, Dict


# Konfigurace chunkingu
CONFIG = {
    "small_chunk_max": 1500,      # Menší než toto = ponechat celé
    "chunk_size": 1200,            # Velikost chunku
    "overlap": 200                 # Překryv mezi chunky (17%)
}

# Cesty k souborům
INPUT_FILE = Path("/Users/atlas/Projects/Fleurdin_AI/4-RAG_Pipeline/parsed_data.json")
OUTPUT_FILE = Path("/Users/atlas/Projects/Fleurdin_AI/4-RAG_Pipeline/chunked_data.json")


print("="*70)
print("🧩 FLEURDIN AI - CHUNKING ZAČÍNÁ")
print("="*70)
print(f"\nParametry:")
print(f"  • Malé texty (<{CONFIG['small_chunk_max']} znaků) = ponechat celé")
print(f"  • Velké texty = rozdělit na {CONFIG['chunk_size']} znaků")
print(f"  • Overlap: {CONFIG['overlap']} znaků")

def split_into_chunks(text, text_id, text_name):
    """
    Rozdělí dlouhý text na menší chunky s overlapem.
    
    Parametry:
    - text: text k rozdělení
    - text_id: ID původního textu
    - text_name: název textu (pro metadata)
    """
    text_length = len(text)

    # Je text malý? → Ponechat celý
    if text_length <= CONFIG['small_chunk_max']:
        return [{
            "id": f"{text_id}_full",
            "text": text,
            "part": 1,
            "total_parts": 1,
            "name": text_name,
            "chunk_size": text_length
        }]

    # Text je velký → Rozdělit na chunky
    chunks = []
    start = 0
    part = 1
    chunk_size = CONFIG['chunk_size']
    overlap = CONFIG['overlap']

    while start < text_length:
        # Vezmi kus textu
        end = start + chunk_size
        chunk_text = text[start:end]

        # Ulož chunk
        chunks.append({
            "id": f"{text_id}_part_{part}",
            "text": chunk_text,
            "part": part,
            "total_parts": 0,  # Vypočítáme později
            "name": text_name,
            "chunk_size": len(chunk_text)
        })

        # Posuň se dál (s overlapem)
        start += (chunk_size - overlap)
        part += 1

    # Aktualizuj total_parts
    total = len(chunks)
    for chunk in chunks:
        chunk['total_parts'] = total

    return chunks

def process_all_data(input_file):
    """
    Načte parsed_data.json a aplikuje chunking.
    """
    print("\n" + "-"*70)
    print("📂 NAČÍTÁM DATA")
    print("-"*70)

    # Načti JSON
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    print(f"  ✅ Načteno {data['stats']['total_items']} položek")

    all_chunks = []
    stats = {
        "oils_chunks": 0,
        "book1_chunks": 0,
        "book2_chunks": 0,
        "drienky_chunks": 0
    }

    # 1. ESENCIÁLNÍ OLEJE - ponechat celé
    print("\n" + "-"*70)
    print("🌿 ZPRACOVÁVÁM: Esenciální oleje")
    print("-"*70)

    for oil in data['essential_oils']:
        chunks = split_into_chunks(
            text=oil['text'],
            text_id=oil['id'],
            text_name=oil['name']
        )

        # Přidej metadata
        for chunk in chunks:
            chunk['type'] = 'essential_oil'
            chunk['tier'] = 'free'  # můžeš změnit
            chunk['metadata'] = oil['metadata']

        all_chunks.extend(chunks)
        stats['oils_chunks'] += len(chunks)

    print(f"  ✅ Vytvořeno {stats['oils_chunks']} chunků")

    # 2. KNIHA 1
    print("\n" + "-"*70)
    print("📖 ZPRACOVÁVÁM: Kniha 1")
    print("-"*70)

    for para in data['book1']:
        chunks = split_into_chunks(
            text=para['text'],
            text_id=para['id'],
            text_name=f"Kniha 1 - odstavec {para['metadata']['paragraph_number']}"
        )

        for chunk in chunks:
            chunk['type'] = 'book_paragraph'
            chunk['tier'] = 'premium'
            chunk['metadata'] = para['metadata']

        all_chunks.extend(chunks)
        stats['book1_chunks'] += len(chunks)

    print(f"  ✅ Vytvořeno {stats['book1_chunks']} chunků")

    # 3. KNIHA 2
    print("\n" + "-"*70)
    print("📖 ZPRACOVÁVÁM: Kniha 2")
    print("-"*70)

    for para in data['book2']:
        chunks = split_into_chunks(
            text=para['text'],
            text_id=para['id'],
            text_name=f"Kniha 2 - odstavec {para['metadata']['paragraph_number']}"
        )

        for chunk in chunks:
            chunk['type'] = 'book_paragraph'
            chunk['tier'] = 'premium'
            chunk['metadata'] = para['metadata']

        all_chunks.extend(chunks)
        stats['book2_chunks'] += len(chunks)

    print(f"  ✅ Vytvořeno {stats['book2_chunks']} chunků")

    # 4. DRIENKY
    print("\n" + "-"*70)
    print("🎤 ZPRACOVÁVÁM: DRIENKY (voice přepis)")
    print("-"*70)

    # Spojit všechny odstavce DRIENKY do jednoho textu
    drienky_text = "\n\n".join([p['text'] for p in data['drienky']])

    chunks = split_into_chunks(
        text=drienky_text,
        text_id="drienky_voice",
        text_name="DRIENKY - voice přepis"
    )

    for chunk in chunks:
        chunk['type'] = 'voice_transcript'
        chunk['tier'] = 'premium'
        chunk['metadata'] = {'source': 'voice_transcript', 'topic': 'drienky'}

    all_chunks.extend(chunks)
    stats['drienky_chunks'] = len(chunks)

    print(f"  ✅ Vytvořeno {stats['drienky_chunks']} chunků")

    return all_chunks, stats

def main():
    """
    Hlavní funkce - spustí chunking.
    """

    # Zpracuj všechna data
    all_chunks, stats = process_all_data(INPUT_FILE)

    # Připrav výstupní data
    output_data = {
        "chunks": all_chunks,
        "stats": {
            "total_chunks": len(all_chunks),
            "oils_chunks": stats['oils_chunks'],
            "book1_chunks": stats['book1_chunks'],
            "book2_chunks": stats['book2_chunks'],
            "drienky_chunks": stats['drienky_chunks']
        }
    }

    # Ulož do JSON
    print("\n" + "="*70)
    print("💾 UKLÁDÁM VÝSLEDKY")
    print("="*70)

    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)

    print(f"\n✅ HOTOVO!")
    print(f"📂 Výstup: {OUTPUT_FILE}")
    print(f"\n📊 FINÁLNÍ STATISTIKY:")
    print(f"  • Esenciální oleje: {stats['oils_chunks']} chunků")
    print(f"  • Kniha 1: {stats['book1_chunks']} chunků")
    print(f"  • Kniha 2: {stats['book2_chunks']} chunků")
    print(f"  • DRIENKY: {stats['drienky_chunks']} chunků")
    print(f"  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print(f"  • CELKEM: {len(all_chunks)} chunků")
    print("\n" + "="*70)
    print("\n🎯 Další krok: Vytvoření embeddings (vektorizace)")


# Spusť program
if __name__ == "__main__":
    main()