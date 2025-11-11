#!/usr/bin/env python3
"""
Debug script - zkontroluje jestli jsou embeddings v databázi
"""

from supabase import create_client
from dotenv import load_dotenv
import os

load_dotenv()

supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))

print("🔍 Checking database content...\n")

# 1. Check how many oils we have
result = supabase.table('content_items').select('id, name, tier, embedding').execute()
oils = result.data

print(f"📊 Total oils in database: {len(oils)}\n")

# 2. Check specific oils
print("🌿 First 5 oils:")
for oil in oils[:5]:
    has_embedding = oil['embedding'] is not None and len(oil['embedding']) > 0
    embedding_dim = len(oil['embedding']) if has_embedding else 0
    print(f"  • {oil['name']} (tier: {oil['tier']}, embedding: {embedding_dim} dims)")

# 3. Check if Oregano exists
oregano = [o for o in oils if 'oregan' in o['name'].lower()]
print(f"\n🔍 Searching for 'Oregano':")
if oregano:
    for o in oregano:
        print(f"  ✅ Found: {o['name']} (ID: {o['id']}, tier: {o['tier']})")
else:
    print("  ❌ Oregano not found!")

# 4. Check embedding dimensions
print(f"\n📐 Embedding dimensions:")
for oil in oils[:3]:
    if oil['embedding']:
        print(f"  • {oil['name']}: {len(oil['embedding'])} dimensions")

# 5. Sample the full data structure
print(f"\n📋 Sample oil data structure:")
sample_oil = supabase.table('content_items').select('*').limit(1).execute()
if sample_oil.data:
    oil = sample_oil.data[0]
    print(f"  Name: {oil['name']}")
    print(f"  Latin name: {oil.get('latin_name')}")
    print(f"  Frequency: {oil.get('frequency')}")
    print(f"  Effects body type: {type(oil.get('effects_body'))}")
    print(f"  Effects psyche type: {type(oil.get('effects_psyche'))}")
    print(f"  Embedding: {len(oil['embedding'])} dims" if oil.get('embedding') else "  Embedding: None")
