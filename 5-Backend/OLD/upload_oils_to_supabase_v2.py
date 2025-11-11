#!/usr/bin/env python3
"""
🌿 FLEURDIN AI - Upload Essential Oils to Supabase (FIXED VERSION)
Opravená verze - správně ukládá pgvector embeddings
"""

import pandas as pd
from sentence_transformers import SentenceTransformer
from supabase import create_client, Client
from dotenv import load_dotenv
import os
import json

# Load environment variables
load_dotenv()

# Configuration
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
RAW_DATA_PATH = "../Raw_data/Pro_trenovani/EO_prehled oleju_raw data.csv.xlsx"

# Initialize
print("🌿 Fleurdin AI - Data Upload (FIXED)")
print("=" * 60)

# 1. Load embedding model
print("\n📦 Loading embedding model...")
embedder = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
print("✅ Model loaded (384 dimensions)")

# 2. Connect to Supabase
print("\n🔗 Connecting to Supabase...")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
print("✅ Connected")

# 3. CLEAR OLD DATA
print("\n🗑️  Clearing old data...")
try:
    supabase.table('content_items').delete().neq('id', 0).execute()
    print("✅ Old data cleared")
except Exception as e:
    print(f"⚠️  Warning: {e}")

# 4. Load raw data
print(f"\n📊 Loading data from Excel...")
df = pd.read_excel(RAW_DATA_PATH)

# Clean data
df = df[df['Esenciální oleje přehled'].notna()]
df = df[df['Esenciální oleje přehled'] != 'ID']
df.columns = ['id', 'name', 'name_en', 'latin_name', 'frequency', 'effects_body', 'effects_psyche']

print(f"✅ Loaded {len(df)} essential oils")

# 5. Get category ID
print("\n🔍 Getting category ID...")
category_result = supabase.table('categories').select('id').eq('name', 'essential_oils').execute()
category_id = category_result.data[0]['id']
print(f"✅ Category ID: {category_id}")

# 6. Process and upload each oil
print("\n⏳ Processing and uploading oils...")
print("=" * 60)

uploaded_count = 0
errors = []

for idx, row in df.iterrows():
    try:
        oil_name = row['name']
        print(f"\n[{idx+1}/{len(df)}] {oil_name}")

        # Parse frequency
        frequency_str = str(row['frequency'])
        if frequency_str == 'Není údaj' or pd.isna(row['frequency']):
            frequency = None
        else:
            try:
                frequency = int(float(frequency_str))
            except:
                frequency = None

        # Parse effects
        effects_body_text = str(row['effects_body']) if pd.notna(row['effects_body']) else ""
        effects_psyche_text = str(row['effects_psyche']) if pd.notna(row['effects_psyche']) else ""

        effects_body_json = {"text": effects_body_text, "parsed": False}
        effects_psyche_json = {"text": effects_psyche_text, "parsed": False}

        # Create embedding text
        embedding_text = f"{oil_name} {row['latin_name']} {effects_body_text} {effects_psyche_text}"

        # Generate embedding
        print(f"  ↳ Generating embedding...")
        embedding_array = embedder.encode(embedding_text)
        embedding_list = embedding_array.tolist()

        # Verify dimensions
        if len(embedding_list) != 384:
            raise Exception(f"Wrong embedding dimension: {len(embedding_list)}")

        print(f"  ↳ Embedding: {len(embedding_list)} dims ✓")

        # Determine tier
        tier = 'free' if idx < 20 else 'premium'

        # Convert embedding to PostgreSQL array format for pgvector
        # Format: '[0.1, 0.2, 0.3, ...]'
        embedding_str = '[' + ','.join(map(str, embedding_list)) + ']'

        # Prepare data WITHOUT embedding (we'll insert it via RPC)
        oil_data = {
            "category_id": category_id,
            "name": oil_name,
            "latin_name": str(row['latin_name']) if pd.notna(row['latin_name']) else None,
            "effects_body": effects_body_json,
            "effects_psyche": effects_psyche_json,
            "frequency": frequency,
            "tier": tier
        }

        # Insert using RAW SQL to properly handle pgvector
        print(f"  ↳ Uploading to Supabase (tier: {tier})...")

        # Use PostgREST to insert with embedding
        # We need to use raw SQL via RPC or use the proper format
        result = supabase.table('content_items').insert({
            **oil_data,
            "embedding": embedding_str  # Pass as string in pgvector format
        }).execute()

        if result.data:
            print(f"  ✅ Success! ID: {result.data[0]['id']}")
            uploaded_count += 1
        else:
            raise Exception("No data returned from insert")

    except Exception as e:
        error_msg = f"Error processing {oil_name}: {str(e)}"
        print(f"  ❌ {error_msg}")
        errors.append(error_msg)
        continue

# 7. Verify embeddings
print("\n" + "=" * 60)
print("🔍 VERIFYING EMBEDDINGS")
print("=" * 60)

verify_result = supabase.table('content_items').select('id, name, embedding').limit(3).execute()
for oil in verify_result.data:
    if oil.get('embedding'):
        dims = len(oil['embedding']) if isinstance(oil['embedding'], list) else 'Unknown'
        print(f"  • {oil['name']}: {dims} dims")
    else:
        print(f"  • {oil['name']}: No embedding")

# 8. Summary
print("\n" + "=" * 60)
print("📊 UPLOAD SUMMARY")
print("=" * 60)
print(f"✅ Successfully uploaded: {uploaded_count}/{len(df)} oils")
if errors:
    print(f"❌ Errors: {len(errors)}")
    for error in errors[:5]:  # Show first 5 errors
        print(f"  • {error}")
else:
    print("🎉 All oils uploaded successfully!")

print("\n" + "=" * 60)
print("NEXT STEPS:")
print("1. Run: python3 debug_embeddings.py (verify 384 dims)")
print("2. Run: python3 test_rag.py (test search)")
print("=" * 60)
