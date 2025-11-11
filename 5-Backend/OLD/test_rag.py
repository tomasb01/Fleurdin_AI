#!/usr/bin/env python3
"""
🌿 FLEURDIN AI - Test RAG System
Testuje RAG pipeline s Supabase + GPT-4o-mini
"""

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
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

print("🌿 Fleurdin AI - RAG Test")
print("=" * 60)

# 1. Initialize
print("\n📦 Loading embedding model...")
embedder = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
print("✅ Embedding model loaded")

print("\n🔗 Connecting to Supabase...")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
print("✅ Connected to Supabase")

# 2. Test Questions (from Excel)
test_questions = [
    "Jaké jsou účinky oregana na tělo?",
    "Jaké oleje bys doporučil na psychickou únavu a stres?",
    "Které esenciální oleje pomáhají při zažívacích obtížích?",
    "What kind of recipe from essential oils would you prepare for a good sleep?",
    "What is mentha essential oil good for?",
    "Which essential oils have the highest frequency? What is it good for? Answer in brief."
]

def search_relevant_oils(question: str, user_tier: str = "premium", top_k: int = 5):
    """
    RAG Retrieval: Find relevant oils using vector search
    """
    print(f"\n  🔍 Searching for: '{question}'")

    # Generate embedding for the question
    question_embedding = embedder.encode(question).tolist()

    # Convert to PostgreSQL array format for pgvector
    # Format: '[0.1, 0.2, 0.3, ...]'
    question_embedding_str = '[' + ','.join(map(str, question_embedding)) + ']'

    # DEBUG: Print what we're sending
    print(f"\n  🐛 DEBUG:")
    print(f"     Embedding length: {len(question_embedding)}")
    print(f"     String format (first 100 chars): {question_embedding_str[:100]}")
    print(f"     Threshold: 0.5")
    print(f"     User tier: {user_tier}")

    # Execute vector search using Supabase RPC (NEW TEXT VERSION)
    try:
        result = supabase.rpc(
            'match_content_text',
            {
                'query_embedding_text': question_embedding_str,  # TEXT parameter!
                'match_threshold': 0.5,  # Lower threshold for more results
                'match_count': top_k,
                'user_tier': user_tier,
                'category_filter': 'essential_oils'
            }
        ).execute()

        print(f"     RPC call successful")
        print(f"     Result type: {type(result.data)}")
        print(f"     Result: {result.data if len(str(result.data)) < 200 else str(result.data)[:200]}")

    except Exception as e:
        print(f"     ❌ RPC ERROR: {str(e)}")
        return []

    oils = result.data
    print(f"\n  ✅ Found {len(oils)} relevant oils")

    for i, oil in enumerate(oils, 1):
        print(f"    {i}. {oil['name']} (similarity: {oil['similarity']:.2f})")

    return oils

def build_context(oils: list) -> str:
    """
    Build context string from retrieved oils
    """
    context_parts = []

    for oil in oils:
        oil_text = f"\n**{oil['name']}**"

        if oil['latin_name']:
            oil_text += f" ({oil['latin_name']})"

        if oil['frequency']:
            oil_text += f"\nFrekvence: {oil['frequency']} Hz"

        # Extract effects_body
        if oil['effects_body']:
            effects_body = oil['effects_body']
            if isinstance(effects_body, dict) and 'text' in effects_body:
                oil_text += f"\n\nÚčinky na tělo:\n{effects_body['text']}"

        # Extract effects_psyche
        if oil['effects_psyche']:
            effects_psyche = oil['effects_psyche']
            if isinstance(effects_psyche, dict) and 'text' in effects_psyche:
                oil_text += f"\n\nÚčinky na psychiku:\n{effects_psyche['text']}"

        context_parts.append(oil_text)

    return "\n\n---\n".join(context_parts)

def generate_answer_simple(question: str, context: str) -> str:
    """
    Simple answer generation (without OpenAI - for testing)
    Just returns the context
    """
    return f"Na základě databáze esenciálních olejů:\n\n{context}"

def test_rag_pipeline():
    """
    Test RAG pipeline on all questions
    """
    print("\n" + "=" * 60)
    print("🧪 TESTING RAG PIPELINE")
    print("=" * 60)

    for i, question in enumerate(test_questions, 1):
        print(f"\n\n{'='*60}")
        print(f"TEST {i}/6")
        print(f"{'='*60}")
        print(f"❓ Question: {question}")

        # 1. Retrieval
        oils = search_relevant_oils(question, user_tier="premium", top_k=5)

        if not oils:
            print("  ⚠️  No relevant oils found")
            continue

        # 2. Build context
        context = build_context(oils)

        # 3. Generate answer (simple version for now)
        print("\n  💬 Answer:")
        print("  " + "-" * 58)
        answer = generate_answer_simple(question, context)

        # Print answer (first 500 chars)
        if len(answer) > 500:
            print(f"  {answer[:500]}...\n  [truncated, full answer available]")
        else:
            print(f"  {answer}")

        print("\n")

    print("\n" + "=" * 60)
    print("✅ RAG PIPELINE TEST COMPLETED")
    print("=" * 60)
    print("\nNEXT STEPS:")
    print("1. Review answers above")
    print("2. Compare with Excel results")
    print("3. Optional: Add OpenAI API for better answers")
    print("=" * 60)

if __name__ == "__main__":
    try:
        test_rag_pipeline()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
