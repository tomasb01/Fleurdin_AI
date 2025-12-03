"""
FLEURDIN AI - UPLOAD TO SUPABASE
=================================
Nahraje chunked_data_FIXED.json do Supabase (pgvector).
"""

import json
import os
from pathlib import Path
from supabase import create_client, Client
from dotenv import load_dotenv
from tqdm import tqdm


# Načti environment variables
load_dotenv()

# Supabase credentials
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY")

# Cesty
INPUT_FILE = Path("/Users/atlas/Projects/Fleurdin_AI/4-RAG_Pipeline/chunked_data_FIXED.json")

# Upload konfigurace
BATCH_SIZE = 100  # Kolik chunků nahrát najednou


print("="*70)
print("📤 FLEURDIN AI - UPLOAD DO SUPABASE")
print("="*70)
print(f"\nSupabase URL: {SUPABASE_URL}")
print(f"Batch size: {BATCH_SIZE}")

def prepare_chunk_for_upload(chunk):
    """
    Připraví chunk pro upload do Supabase.
    """
    return {
        "id": chunk["id"],
        "type": chunk["type"],
        "entity_type": chunk["entity_type"],
        "content_type": chunk["content_type"],
        "tier": chunk["tier"],
        "name": chunk.get("name", ""),
        "text": chunk["text"],
        "part": chunk.get("part", 1),
        "total_parts": chunk.get("total_parts", 1),
        "chunk_size": chunk.get("chunk_size", len(chunk["text"])),
        "metadata": chunk.get("metadata", {}),
        "embedding": chunk["embedding"]
    }


def upload_chunks(supabase: Client, chunks, batch_size=100):
    """
    Nahraje chunky do Supabase po dávkách.
    """
    print("\n" + "-"*70)
    print("📤 NAHRÁVÁM CHUNKY DO SUPABASE")
    print("-"*70)

    total = len(chunks)
    uploaded = 0
    errors = 0

    # Zpracuj po dávkách
    for i in tqdm(range(0, total, batch_size), desc="Nahrávání dávek"):
        batch = chunks[i:i + batch_size]

        # Připrav data
        prepared_batch = [prepare_chunk_for_upload(chunk) for chunk in batch]

        try:
            # Nahraj dávku
            response = supabase.table("knowledge_chunks").insert(prepared_batch).execute()
            uploaded += len(batch)

        except Exception as e:
            print(f"\n❌ Chyba při nahrávání dávky {i//batch_size + 1}: {str(e)}")
            errors += len(batch)

    print(f"\n✅ Upload dokončen!")
    print(f"  • Úspěšně nahráno: {uploaded} chunků")
    print(f"  • Chyby: {errors} chunků")

    return uploaded, errors

def main():
    """
    Hlavní funkce - připojí se k Supabase a nahraje data.
    """

    # 1. Zkontroluj credentials
    if not SUPABASE_URL or not SUPABASE_SERVICE_KEY:
        print("❌ CHYBA: Chybí Supabase credentials v .env souboru!")
        print("Zkontroluj, že máš v .env:")
        print("  - SUPABASE_URL")
        print("  - SUPABASE_SERVICE_KEY")
        return

    # 2. Připoj se k Supabase
    print("\n" + "-"*70)
    print("🔌 PŘIPOJUJI SE K SUPABASE")
    print("-"*70)

    try:
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)
        print("✅ Připojeno k Supabase!")
    except Exception as e:
        print(f"❌ Chyba při připojení: {e}")
        return

    # 3. Načti data
    print("\n" + "-"*70)
    print("📂 NAČÍTÁM DATA")
    print("-"*70)

    with open(INPUT_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)

    chunks = data['chunks']
    print(f"✅ Načteno {len(chunks)} chunků")

    # 4. Nahraj do Supabase
    uploaded, errors = upload_chunks(supabase, chunks, BATCH_SIZE)

    # 5. Ověř upload
    print("\n" + "="*70)
    print("🔍 OVĚŘUJI UPLOAD")
    print("="*70)

    try:
        result = supabase.table("knowledge_chunks").select("id", count="exact").execute()
        count = result.count
        print(f"\n✅ V databázi je celkem: {count} chunků")

        if count == len(chunks):
            print("🎉 Všechny chunky byly úspěšně nahrány!")
        else:
            print(f"⚠️ Očekáváno {len(chunks)}, ale v databázi je {count}")

    except Exception as e:
        print(f"❌ Chyba při ověřování: {e}")

    print("\n" + "="*70)
    print("✅ HOTOVO!")
    print("="*70)
    print("\n🎯 Další krok: Otestovat vector search")


# Spusť program
if __name__ == "__main__":
    main()
