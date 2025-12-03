"""
FLEURDIN AI - KONTROLA OBSAHU DATABÁZE
=======================================
Zkontroluje, co je skutečně uloženo v Supabase.
"""

import os
from dotenv import load_dotenv
from supabase import create_client, Client
import json

# Načti .env
load_dotenv()

# Supabase credentials
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_KEY")


print("="*70)
print("🔍 KONTROLA OBSAHU DATABÁZE")
print("="*70)

# Připoj se k Supabase
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# 1. Zkontroluj první chunk z essential_oil
print("\n" + "-"*70)
print("1️⃣  KONTROLA: První essential_oil chunk")
print("-"*70)

oils = supabase.from_("knowledge_chunks") \
    .select("*") \
    .eq("type", "essential_oil") \
    .limit(1) \
    .execute()

if oils.data:
    chunk = oils.data[0]
    print(f"\n📦 ID: {chunk['id']}")
    print(f"📝 Type: {chunk['type']}")
    print(f"🏷️  Entity Type: {chunk['entity_type']}")
    print(f"📄 Content Type: {chunk['content_type']}")
    print(f"💰 Tier: {chunk['tier']}")
    print(f"👤 Name: {chunk.get('name', 'N/A')}")
    print(f"👤 Entity Name: {chunk.get('entity_name', 'N/A')}")
    print(f"📏 Text length: {len(chunk['text'])} znaků")
    print(f"\n📖 Text (prvních 200 znaků):")
    print(chunk['text'][:200])
    print(f"\n🔧 Metadata:")
    print(json.dumps(chunk.get('metadata', {}), indent=2, ensure_ascii=False))
else:
    print("❌ Žádné essential_oil chunky nenalezeny!")

# 2. Zkontroluj první chunk z herb_knowledge
print("\n" + "-"*70)
print("2️⃣  KONTROLA: První herb_knowledge chunk")
print("-"*70)

herbs = supabase.from_("knowledge_chunks") \
    .select("*") \
    .eq("type", "herb_knowledge") \
    .limit(1) \
    .execute()

if herbs.data:
    chunk = herbs.data[0]
    print(f"\n📦 ID: {chunk['id']}")
    print(f"📝 Type: {chunk['type']}")
    print(f"🏷️  Entity Type: {chunk['entity_type']}")
    print(f"📄 Content Type: {chunk['content_type']}")
    print(f"💰 Tier: {chunk['tier']}")
    print(f"👤 Name: {chunk.get('name', 'N/A')}")
    print(f"👤 Entity Name: {chunk.get('entity_name', 'N/A')}")
    print(f"📏 Text length: {len(chunk['text'])} znaků")
    print(f"\n📖 Text (prvních 200 znaků):")
    print(chunk['text'][:200])
    print(f"\n🔧 Metadata:")
    print(json.dumps(chunk.get('metadata', {}), indent=2, ensure_ascii=False))
else:
    print("❌ Žádné herb_knowledge chunky nenalezeny!")

# 3. Zkontroluj, zda máme Levanduli
print("\n" + "-"*70)
print("3️⃣  HLEDÁM: Levanduli v databázi")
print("-"*70)

# Hledej v textu
lavender_search = supabase.from_("knowledge_chunks") \
    .select("id, type, name, text") \
    .ilike("text", "%levandule%") \
    .execute()

print(f"\n✅ Nalezeno {len(lavender_search.data)} chunků s 'levandule':")
for chunk in lavender_search.data[:3]:  # Prvních 5
    print(f"\n  • ID: {chunk['id']}")
    print(f"    Name: {chunk.get('name', 'N/A')}")
    print(f"    Type: {chunk['type']}")
    print(f"    Text: {chunk['text'][:100]}...")

# 4. Zkontroluj strukturu tabulky
print("\n" + "-"*70)
print("4️⃣  STRUKTURA: Všechny sloupce v tabulce")
print("-"*70)

sample = supabase.from_("knowledge_chunks") \
    .select("*") \
    .limit(1) \
    .execute()

if sample.data:
    print("\n📋 Sloupce v tabulce:")
    for key in sample.data[0].keys():
        print(f"  • {key}")

print("\n" + "="*70)
print("✅ KONTROLA DOKONČENA")
print("="*70)
