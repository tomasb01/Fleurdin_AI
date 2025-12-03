"""
FLEURDIN AI - TEST VECTOR SEARCH
=================================
Testuje vector search v Supabase (pgvector).
"""

import os
from dotenv import load_dotenv
from supabase import create_client, Client
from sentence_transformers import SentenceTransformer
import json

# Načti .env
load_dotenv()

# Supabase credentials
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_KEY")

# Hugging Face token (pokud je potřeba autentizace)
HF_TOKEN = os.getenv("HF_TOKEN")

# Embedding model
EMBEDDING_MODEL = "paraphrase-multilingual-MiniLM-L12-v2"


print("="*70)
print("🔍 FLEURDIN AI - TEST VECTOR SEARCH")
print("="*70)


def test_vector_search():
    """
    Testuje vector search s různými filtry.
    """

    # 1. Připoj se k Supabase
    print("\n" + "-"*70)
    print("📡 PŘIPOJUJI SE K SUPABASE")
    print("-"*70)

    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    print(f"✅ Připojeno k: {SUPABASE_URL}")

    # 2. Načti embedding model
    print("\n" + "-"*70)
    print("🤖 NAČÍTÁM EMBEDDING MODEL")
    print("-"*70)

    # Načti model s tokenem (pokud je k dispozici)
    if HF_TOKEN:
        model = SentenceTransformer(EMBEDDING_MODEL, token=HF_TOKEN)
        print(f"✅ Model načten s autentizací: {EMBEDDING_MODEL}")
    else:
        model = SentenceTransformer(EMBEDDING_MODEL)
        print(f"✅ Model načten: {EMBEDDING_MODEL}")

    # 3. Testovací dotazy
    test_queries = [
        {
            "query": "Jak použít levanduli na spaní?",
            "filters": {"filter_type": "essential_oil"},
            "description": "TEST 1: Hledám info o olejích (free tier)"
        },
        {
            "query": "Jaké jsou léčivé účinky púpavy?",
            "filters": {"filter_type": "herb_knowledge"},
            "description": "TEST 2: Hledám info o bylinkách (premium tier)"
        },
        {
            "query": "Bolest hlavy",
            "filters": {"filter_tier": "free"},
            "description": "TEST 3: Obecné hledání (pouze free)"
        },
        {
            "query": "Drienka na zdraví",
            "filters": {},
            "description": "TEST 4: Hledání bez filtrů (všechno)"
        }
    ]

    # 4. Spusť testy
    print("\n" + "="*70)
    print("🧪 SPOUŠTÍM TESTY")
    print("="*70)

    for i, test in enumerate(test_queries, 1):
        print(f"\n\n{'='*70}")
        print(f"{test['description']}")
        print(f"{'='*70}")
        print(f"📝 Dotaz: \"{test['query']}\"")
        print(f"🔧 Filtry: {test['filters']}")

        # Vytvoř embedding pro dotaz
        query_embedding = model.encode(test['query']).tolist()

        # Zavolej match_chunks funkci
        try:
            # Připrav parametry
            params = {
                "query_embedding": query_embedding,
                "match_threshold": 0.3,  # Min similarity (0-1)
                "match_count": 5         # Top 5 výsledků
            }

            # Přidej filtry (pokud jsou)
            if "filter_tier" in test["filters"]:
                params["filter_tier"] = test["filters"]["filter_tier"]
            if "filter_type" in test["filters"]:
                params["filter_type"] = test["filters"]["filter_type"]

            # Zavolej RPC funkci
            response = supabase.rpc("match_chunks", params).execute()

            # Zobraz výsledky
            results = response.data

            print(f"\n✅ Nalezeno {len(results)} výsledků:")
            print("-"*70)

            if len(results) == 0:
                print("❌ Žádné výsledky!")
            else:
                for j, result in enumerate(results, 1):
                    print(f"\n{j}. [{result['type']}] - Tier: {result['tier']}")
                    print(f"   Similarity: {result['similarity']:.3f}")
                    print(f"   Name: {result.get('name', 'N/A')}")
                    print(f"   Text (preview): {result['text'][:150]}...")
                    print(f"   ID: {result['id']}")

        except Exception as e:
            print(f"\n❌ CHYBA: {e}")

    # 5. Statistiky databáze
    print("\n\n" + "="*70)
    print("📊 STATISTIKY DATABÁZE")
    print("="*70)

    try:
        # Počet chunků podle typu
        stats_type = supabase.from_("knowledge_chunks") \
            .select("type", count="exact") \
            .execute()

        # Počet podle typu
        oils = supabase.from_("knowledge_chunks") \
            .select("*", count="exact") \
            .eq("type", "essential_oil") \
            .execute()

        herbs = supabase.from_("knowledge_chunks") \
            .select("*", count="exact") \
            .eq("type", "herb_knowledge") \
            .execute()

        # Počet podle tier
        free = supabase.from_("knowledge_chunks") \
            .select("*", count="exact") \
            .eq("tier", "free") \
            .execute()

        premium = supabase.from_("knowledge_chunks") \
            .select("*", count="exact") \
            .eq("tier", "premium") \
            .execute()

        print(f"\n📦 CELKEM chunků: {oils.count + herbs.count}")
        print(f"\n📋 PODLE TYPU:")
        print(f"  • essential_oil: {oils.count}")
        print(f"  • herb_knowledge: {herbs.count}")
        print(f"\n💰 PODLE TIER:")
        print(f"  • free: {free.count}")
        print(f"  • premium: {premium.count}")

    except Exception as e:
        print(f"\n❌ Chyba při získávání statistik: {e}")

    print("\n" + "="*70)
    print("✅ TESTY DOKONČENY!")
    print("="*70)


# Spusť testy
if __name__ == "__main__":
    test_vector_search()
