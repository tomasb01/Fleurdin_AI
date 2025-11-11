#!/usr/bin/env python3
"""
Check embedding format issue
"""

from sentence_transformers import SentenceTransformer
import numpy as np

print("🔍 Testing embedding generation...\n")

# Load model
embedder = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')

# Test text
test_text = "Oregano má antibakteriální účinky"

# Generate embedding
embedding = embedder.encode(test_text)

print(f"Embedding type: {type(embedding)}")
print(f"Embedding shape: {embedding.shape}")
print(f"Embedding dimensions: {len(embedding)}")
print(f"First 5 values: {embedding[:5]}")

# Convert to list (as we do in upload script)
embedding_list = embedding.tolist()

print(f"\nAs list:")
print(f"  Type: {type(embedding_list)}")
print(f"  Length: {len(embedding_list)}")
print(f"  First 5: {embedding_list[:5]}")

# Check if it's flat
print(f"\n  Is flat list? {isinstance(embedding_list, list) and all(isinstance(x, (int, float)) for x in embedding_list)}")
