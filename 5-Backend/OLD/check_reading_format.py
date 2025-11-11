#!/usr/bin/env python3
"""
Check HOW Supabase reads pgvector data
"""

from supabase import create_client
from dotenv import load_dotenv
import os
import json

load_dotenv()

supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))

print("🔍 Checking how Supabase reads pgvector...\n")

# Get one oil
result = supabase.table('content_items').select('name, embedding').limit(1).execute()
oil = result.data[0]

print(f"Oil: {oil['name']}")
print(f"\nEmbedding type: {type(oil['embedding'])}")
print(f"Embedding content (first 100 chars): {str(oil['embedding'])[:100]}")

if isinstance(oil['embedding'], str):
    print("\n❌ PROBLEM: Embedding is a STRING!")
    print(f"   String length: {len(oil['embedding'])} characters")

    # Try to parse it
    try:
        import json
        parsed = json.loads(oil['embedding'])
        print(f"\n✅ Can be parsed as JSON")
        print(f"   Parsed type: {type(parsed)}")
        print(f"   Parsed length: {len(parsed)} elements")
        print(f"   First 5 elements: {parsed[:5]}")
    except:
        print("\n❌ Cannot parse as JSON")

elif isinstance(oil['embedding'], list):
    print("\n✅ Embedding is a LIST!")
    print(f"   Length: {len(oil['embedding'])} elements")
    print(f"   First 5: {oil['embedding'][:5]}")
else:
    print(f"\n⚠️  Unknown type: {type(oil['embedding'])}")
