"""
TEST FINE-TUNED MODEL (PO FINE-TUNINGU)
========================================

Tento skript testuje fine-tuned Gemma 2-2B-it model PO fine-tuningu
na stejných 9 testovacích otázkách.

Výsledky uloží do: results_after_finetuning.txt
"""

import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from peft import PeftModel
from datetime import datetime

# ============================================
# KONFIGURACE
# ============================================

BASE_MODEL = "google/gemma-2-2b-it"
FINETUNED_MODEL_PATH = "./fleurdin-gemma-2b"  # Lokální cesta k LoRA adapters
OUTPUT_FILE = "results_after_finetuning.txt"

# Testovací otázky (stejné jako v test_base_model.py - aktualizováno 2025-01-30)
TEST_QUESTIONS = [
    "Jaké jsou účinky oregana na tělo?",
    "Jaké oleje bys doporučil na psychickou únavu a stres?",
    "Které esenciální oleje pomáhají při zažívacích obtížích?",
    "Pomůže levandule při nespavosti?",
    "Na co se používá máta peprná?",
    "K čemu je u oleje uvedená jeho frekvence?",
    "Jaké esenciální oleje bys doporučil na bolesti kloubů a svalů?",
    "Který olej je dobrý na trávení?",
    "Jak bys vytvořil směs olejů na podporu spánku?"
]

# System prompt
SYSTEM_PROMPT = """Jsi expert na esenciální oleje a aromaterapii.
Poskytuj přesné, odborné informace o účincích esenciálních olejů na tělo a psychiku.
Odpovídej v češtině, stručně a srozumitelně."""


# ============================================
# FUNKCE
# ============================================

def load_finetuned_model():
    """Načti fine-tuned model (base + LoRA adapters)"""

    print(f"📥 Načítám base model: {BASE_MODEL}")
    print("⚠️  To může trvat několik minut...")

    # Načti base model
    tokenizer = AutoTokenizer.from_pretrained(BASE_MODEL)
    base_model = AutoModelForCausalLM.from_pretrained(
        BASE_MODEL,
        device_map="auto",
        torch_dtype=torch.bfloat16
    )

    # Načti LoRA adapters (fine-tuned weights)
    print(f"📥 Načítám fine-tuned adapters z: {FINETUNED_MODEL_PATH}")
    model = PeftModel.from_pretrained(base_model, FINETUNED_MODEL_PATH)

    # Merge adapters do base model (pro rychlejší inference)
    print("🔀 Mergování adapters...")
    model = model.merge_and_unload()

    print("✅ Fine-tuned model načten!")
    return tokenizer, model


def test_question(question, tokenizer, model):
    """Testuj jednu otázku"""

    # Formátování pro Gemma 2-2B-it
    messages = [
        {"role": "user", "content": f"{SYSTEM_PROMPT}\n\n{question}"}
    ]

    # Tokenizace
    input_text = tokenizer.apply_chat_template(
        messages,
        tokenize=False,
        add_generation_prompt=True
    )

    inputs = tokenizer(input_text, return_tensors="pt").to(model.device)

    # Generování
    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=256,
            temperature=0.7,
            top_p=0.9,
            do_sample=True
        )

    # Dekódování
    response = tokenizer.decode(outputs[0], skip_special_tokens=True)

    # Extrakce odpovědi
    if "<start_of_turn>model" in response:
        answer = response.split("<start_of_turn>model")[-1].strip()
    else:
        answer = response

    return answer


def run_tests():
    """Spusť všechny testy"""

    print("\n" + "="*60)
    print("🧪 TEST FINE-TUNED MODEL (PO FINE-TUNINGU)")
    print("="*60 + "\n")

    # Načti model
    tokenizer, model = load_finetuned_model()

    # Otevři output file
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write("="*60 + "\n")
        f.write("TEST FINE-TUNED MODEL (PO FINE-TUNINGU)\n")
        f.write("="*60 + "\n\n")
        f.write(f"Base model: {BASE_MODEL}\n")
        f.write(f"Fine-tuned: {FINETUNED_MODEL_PATH}\n")
        f.write(f"Datum: {timestamp}\n")
        f.write(f"Počet otázek: {len(TEST_QUESTIONS)}\n")
        f.write("\n" + "="*60 + "\n\n")

        # Testuj každou otázku
        for i, question in enumerate(TEST_QUESTIONS, 1):
            print(f"\n📝 Otázka {i}/{len(TEST_QUESTIONS)}: {question}")

            answer = test_question(question, tokenizer, model)

            print(f"💬 Odpověď: {answer[:100]}...")

            # Ulož
            f.write(f"OTÁZKA {i}:\n")
            f.write(f"{question}\n\n")
            f.write(f"ODPOVĚĎ:\n")
            f.write(f"{answer}\n")
            f.write("\n" + "-"*60 + "\n\n")

    print(f"\n✅ Hotovo! Výsledky uloženy do: {OUTPUT_FILE}")
    print("\n💡 Porovnej s results_before_finetuning.txt")


# ============================================
# MAIN
# ============================================

if __name__ == "__main__":
    run_tests()
