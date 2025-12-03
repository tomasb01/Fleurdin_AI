"""
FLEURDIN AI - EMBEDDINGS SCRIPT
================================
Vytvoří vector embeddings pro každý chunk.
"""

import json
from pathlib import Path
from sentence_transformers import SentenceTransformer
from tqdm import tqdm


# Konfigurace
EMBEDDING_MODEL = "paraphrase-multilingual-MiniLM-L12-v2"  # Pro češtinu/slovenštinu
BATCH_SIZE = 32  # Kolik chunků zpracovat najednou (rychlost)

# Cesty k souborům
INPUT_FILE = Path("/Users/atlas/Projects/Fleurdin_AI/4-RAG_Pipeline/chunked_data.json")
OUTPUT_FILE = Path("/Users/atlas/Projects/Fleurdin_AI/4-RAG_Pipeline/chunked_data_with_embeddings.json")


print("="*70)
print("🧠 FLEURDIN AI - VYTVÁŘENÍ EMBEDDINGŮ")
print("="*70)
print(f"\nModel: {EMBEDDING_MODEL}")
print(f"Batch size: {BATCH_SIZE}")

def create_embeddings(chunks, model):
    """
    Vytvoří embeddings pro všechny chunky.
    
    Parametry:
    - chunks: seznam chunků
    - model: SentenceTransformer model
    """
    print("\n" + "-"*70)
    print("🔄 VYTVÁŘÍM EMBEDDINGS")
    print("-"*70)
    print(f"Celkem chunků: {len(chunks)}")

    # Připrav texty pro embedding
    texts = [chunk['text'] for chunk in chunks]

    # Vytvoř embeddings (s progress barem)
    print("\n⏳ Zpracovávám chunky...")
    embeddings = model.encode(
        texts,
        batch_size=BATCH_SIZE,
        show_progress_bar=True,
        convert_to_numpy=True
    )

    # Přidej embeddings k chunkům
    print("\n✅ Přidávám embeddings k chunkům...")
    for i, chunk in enumerate(tqdm(chunks, desc="Přidávání embeddingů")):
        chunk['embedding'] = embeddings[i].tolist()

    print(f"\n✅ Hotovo! Vytvořeno {len(chunks)} embeddingů")
    print(f"📏 Velikost embeddingy: {len(embeddings[0])} dimenzí")

    return chunks

def main():
    """
    Hlavní funkce - načte chunky, vytvoří embeddings, uloží.
    """

    # 1. Načti chunked data
    print("\n" + "-"*70)
    print("📂 NAČÍTÁM DATA")
    print("-"*70)

    with open(INPUT_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)

    print(f"✅ Načteno {data['stats']['total_chunks']} chunků")

    # 2. Načti embedding model
    print("\n" + "-"*70)
    print("🤖 NAČÍTÁM AI MODEL")
    print("-"*70)
    print("(První spuštění stáhne model ~120 MB)")

    model = SentenceTransformer(EMBEDDING_MODEL)
    print("✅ Model načten!")

    # 3. Vytvoř embeddings
    chunks_with_embeddings = create_embeddings(data['chunks'], model)

    # 4. Ulož výsledky
    print("\n" + "="*70)
    print("💾 UKLÁDÁM VÝSLEDKY")
    print("="*70)

    output_data = {
        "chunks": chunks_with_embeddings,
        "stats": data['stats'],
        "embedding_model": EMBEDDING_MODEL,
        "embedding_dimensions": len(chunks_with_embeddings[0]['embedding'])
    }

    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)

    print(f"\n✅ HOTOVO!")
    print(f"📂 Výstup: {OUTPUT_FILE}")
    print(f"\n📊 FINÁLNÍ STATISTIKY:")
    print(f"  • Celkem chunků: {len(chunks_with_embeddings)}")
    print(f"  • Embedding model: {EMBEDDING_MODEL}")
    print(f"  • Embedding dimenze: {output_data['embedding_dimensions']}")
    print(f"  • Velikost souboru: ~{OUTPUT_FILE.stat().st_size / 1024 / 1024:.1f} MB")
    print("\n" + "="*70)
    print("\n🎯 Další krok: Nahrát data do vector databáze (Supabase/Chroma)")


# Spusť program
if __name__ == "__main__":
    main()