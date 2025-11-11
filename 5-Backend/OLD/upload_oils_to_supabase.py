#!/usr/bin/env python3
"""
🌿 FLEURDIN AI - Upload Essential Oils to Supabase
Načte data z raw Excel souboru, vygeneruje embeddings a uploadne do Supabase
"""

import pandas as pd
from sentence_transformers import SentenceTransformer
from supabase import create_client, Client
from dotenv import load_dotenv
import os
import json
from typing import Dict, Any, List

# Load environment variables
load_dotenv()

# Configuration
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL:
    raise ValueError("SUPABASE_URL not found in environment variables. Make sure your .env file is configured correctly.")
if not SUPABASE_KEY:
    raise ValueError("SUPABASE_KEY not found in environment variables. Make sure your .env file is configured correctly.")
RAW_DATA_PATH = "../Raw_data/Pro_trenovani/EO_prehled oleju_raw data.csv.xlsx"

# Initialize
print("🌿 Fleurdin AI - Data Upload")
print("=" * 60)

# 1. Load embedding model
print("\n📦 Loading embedding model...")
embedder = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
print("✅ Model loaded (384 dimensions)")

# 2. Connect to Supabase
print("\n🔗 Connecting to Supabase...")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
print("✅ Connected")

# 3. Load raw data
print(f"\n📊 Loading data from Excel...")
df = pd.read_excel(RAW_DATA_PATH)

# Clean data (skip header rows)
df = df[df['Esenciální oleje přehled'].notna()]
df = df[df['Esenciální oleje přehled'] != 'ID']  # Skip header
df.columns = ['id', 'name', 'name_en', 'latin_name', 'frequency', 'effects_body', 'effects_psyche']

print(f"✅ Loaded {len(df)} essential oils")

# 4. Get category ID for essential_oils
print("\n🔍 Getting category ID...")
category_result = supabase.table('categories').select('id').eq('name', 'essential_oils').execute()
category_id = category_result.data[0]['id']
print(f"✅ Category ID: {category_id}")

# 5. Process and upload each oil
print("\n⏳ Processing and uploading oils...")
print("=" * 60)

uploaded_count = 0
errors = []

for idx, row in df.iterrows():
    try:
        oil_name = row['name']
        print(f"\n[{idx+1}/{len(df)}] {oil_name}")

        # Parse frequency (handle "Není údaj")
        frequency_str = str(row['frequency'])
        if frequency_str == 'Není údaj' or pd.isna(row['frequency']):
            frequency = None
        else:
            try:
                frequency = int(float(frequency_str))
            except:
                frequency = None

        # Parse effects_body (keep as text for now, can be structured later)
        effects_body_text = str(row['effects_body']) if pd.notna(row['effects_body']) else ""
        effects_psyche_text = str(row['effects_psyche']) if pd.notna(row['effects_psyche']) else ""

        # For now, store as JSONB with simple structure
        # TODO: Later can parse into categories (OBECNÉ, TRÁVENÍ, etc.)
        effects_body_json = {
            "text": effects_body_text,
            "parsed": False  # Flag for future parsing
        }

        effects_psyche_json = {
            "text": effects_psyche_text,
            "parsed": False
        }

        # Create embedding text (combine all text for better search)
        embedding_text = f"{oil_name} {row['latin_name']} {effects_body_text} {effects_psyche_text}"

        # Generate embedding
        print(f"  ↳ Generating embedding...")
        embedding = embedder.encode(embedding_text).tolist()

        # Determine tier (first 20 = free, rest = premium)
        tier = 'free' if idx < 20 else 'premium'

        # Prepare data
        oil_data = {
            "category_id": category_id,
            "name": oil_name,
            "latin_name": str(row['latin_name']) if pd.notna(row['latin_name']) else None,
            "effects_body": effects_body_json,
            "effects_psyche": effects_psyche_json,
            "frequency": frequency,
            "tier": tier,
            "embedding": embedding
        }

        # Insert into Supabase
        print(f"  ↳ Uploading to Supabase (tier: {tier})...")
        result = supabase.table('content_items').insert(oil_data).execute()

        print(f"  ✅ Success! ID: {result.data[0]['id']}")
        uploaded_count += 1

    except Exception as e:
        error_msg = f"Error processing {oil_name}: {str(e)}"
        print(f"  ❌ {error_msg}")
        errors.append(error_msg)
        continue

# 6. Summary
print("\n" + "=" * 60)
print("📊 UPLOAD SUMMARY")
print("=" * 60)
print(f"✅ Successfully uploaded: {uploaded_count}/{len(df)} oils")
if errors:
    print(f"❌ Errors: {len(errors)}")
    for error in errors:
        print(f"  • {error}")
else:
    print("🎉 All oils uploaded successfully!")

print("\n" + "=" * 60)
print("NEXT STEPS:")
print("1. Test vector search: python test_rag.py")
print("2. View data in Supabase Table Editor")
print("=" * 60)
