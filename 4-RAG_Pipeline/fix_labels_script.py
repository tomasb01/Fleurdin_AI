
"""
FLEURDIN AI - FIX LABELS SCRIPT
================================
Opraví labels v chunked_data_with_embeddings.json
"""

import json
from pathlib import Path


# Cesty
INPUT_FILE = Path("/Users/atlas/Projects/Fleurdin_AI/4-RAG_Pipeline/chunked_data_with_embeddings.json")
OUTPUT_FILE = Path("/Users/atlas/Projects/Fleurdin_AI/4-RAG_Pipeline/chunked_data_FIXED.json")


# Mapping: Původní type → Nový label
LABEL_MAPPING = {
    "essential_oil": {
        "type": "essential_oil",
        "entity_type": "oil_profile",
        "content_type": "database",
        "tier": "free"  # Všech 30 současných olejů = free
    },
    "book_paragraph": {
        "type": "herb_knowledge",
        "entity_type": "herb",
        "content_type": "book",
        "tier": "premium"
    },
    "voice_transcript": {
        "type": "herb_knowledge",
        "entity_type": "herb",
        "content_type": "voice_transcript",
        "tier": "premium"
    }
}


print("="*70)
print("🔧 FLEURDIN AI - OPRAVA LABELS")
print("="*70)

def fix_chunk_labels(chunk):
    """
    Opraví labels u jednoho chunku.
    """
    old_type = chunk.get('type', 'unknown')

    # Najdi mapping
    if old_type not in LABEL_MAPPING:
        print(f"  ⚠️  Neznámý type: {old_type}")
        return chunk

    new_labels = LABEL_MAPPING[old_type]

    # Aktualizuj labels
    chunk['type'] = new_labels['type']
    chunk['entity_type'] = new_labels['entity_type']
    chunk['content_type'] = new_labels['content_type']
    chunk['tier'] = new_labels['tier']

    # Přidej category do metadata (pokud ještě není)
    if 'metadata' not in chunk:
        chunk['metadata'] = {}

    if new_labels['type'] == 'herb_knowledge':
        chunk['metadata']['category'] = 'bylinky'
    else:
        chunk['metadata']['category'] = 'esenciální oleje'

    return chunk


def process_all_chunks(data):
    """
    Projde všechny chunky a opraví labels.
    """
    print("\n" + "-"*70)
    print("🔄 OPRAVUJI LABELS")
    print("-"*70)

    stats = {
        "essential_oil": 0,
        "herb_knowledge": 0,
        "total": 0
    }

    for chunk in data['chunks']:
        old_type = chunk.get('type')
        chunk = fix_chunk_labels(chunk)
        new_type = chunk.get('type')

        # Statistiky
        stats[new_type] = stats.get(new_type, 0) + 1
        stats['total'] += 1

    print(f"\n✅ Opraveno {stats['total']} chunků:")
    print(f"  • essential_oil: {stats.get('essential_oil', 0)}")
    print(f"  • herb_knowledge: {stats.get('herb_knowledge', 0)}")

    return data, stats


def main():
    """
    Hlavní funkce - načte data, opraví labels, uloží.
    """

    # 1. Načti data
    print("\n" + "-"*70)
    print("📂 NAČÍTÁM DATA")
    print("-"*70)

    with open(INPUT_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)

    print(f"✅ Načteno {len(data['chunks'])} chunků")

    # 2. Oprav labels
    data, stats = process_all_chunks(data)

    # 3. Ulož opravená data
    print("\n" + "="*70)
    print("💾 UKLÁDÁM OPRAVENÁ DATA")
    print("="*70)

    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"\n✅ HOTOVO!")
    print(f"📂 Výstup: {OUTPUT_FILE}")
    print(f"\n📊 FINÁLNÍ LABELS:")
    print(f"  • essential_oil (tier: free): {stats.get('essential_oil', 0)} chunků")
    print(f"  • herb_knowledge (tier: premium): {stats.get('herb_knowledge', 0)} chunků")
    print(f"  • CELKEM: {stats['total']} chunků")

    print("\n" + "="*70)
    print("🎯 Další krok: Nahrát data do Supabase")
    print("="*70)


# Spusť program
if __name__ == "__main__":
    main()
