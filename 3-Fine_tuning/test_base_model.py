"""
TEST BASE MODEL (PŘED FINE-TUNINGEM)
=====================================

Tento skript testuje base Gemma 2-2B-it model PŘED fine-tuningem
na 10 testovacích otázkách z test_questions.txt

Výsledky uloží do: results_before_finetuning.txt
"""

import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from datetime import datetime

# ============================================
# KONFIGURACE
# ============================================

MODEL_NAME = "google/gemma-2-2b-it"
TEST_QUESTIONS_FILE = "../1-EO_Dataset/test_questions.txt"
OUTPUT_FILE = "results_before_finetuning.txt"

# Testovací otázky (z test_questions.txt - aktualizováno 2025-01-30)
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

# System prompt (stejný jako budeme používat po fine-tuningu)
SYSTEM_PROMPT = """Jsi expert na esenciální oleje a aromaterapii.
Poskytuj přesné, odborné informace o účincích esenciálních olejů na tělo a psychiku.
Odpovídej v češtině, stručně a srozumitelně."""


# ============================================
# FUNKCE
# ============================================

def load_model():
    """Načti base model a tokenizer"""
    print(f"📥 Načítám model: {MODEL_NAME}")
    print("⚠️  To může trvat několik minut...")

    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
    model = AutoModelForCausalLM.from_pretrained(
        MODEL_NAME,
        device_map="auto",
        torch_dtype=torch.bfloat16  # Úspora paměti
    )

    print("✅ Model načten!")
    return tokenizer, model


def test_question(question, tokenizer, model):
    """Testuj jednu otázku"""

    # Formátování pro Gemma 2-2B-it (chat format)
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

    # Generování odpovědi
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

    # Extrakce jen odpovědi (bez promptu)
    # Gemma formát: <start_of_turn>user\n...<end_of_turn>\n<start_of_turn>model\nODPOVĚĎ
    if "<start_of_turn>model" in response:
        answer = response.split("<start_of_turn>model")[-1].strip()
    else:
        answer = response

    return answer


def run_tests():
    """Spusť všechny testy"""

    print("\n" + "="*60)
    print("🧪 TEST BASE MODEL (PŘED FINE-TUNINGEM)")
    print("="*60 + "\n")

    # Načti model
    tokenizer, model = load_model()

    # Otevři output file
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write("="*60 + "\n")
        f.write("TEST BASE MODEL (PŘED FINE-TUNINGEM)\n")
        f.write("="*60 + "\n\n")
        f.write(f"Model: {MODEL_NAME}\n")
        f.write(f"Datum: {timestamp}\n")
        f.write(f"Počet otázek: {len(TEST_QUESTIONS)}\n")
        f.write("\n" + "="*60 + "\n\n")

        # Testuj každou otázku
        for i, question in enumerate(TEST_QUESTIONS, 1):
            print(f"\n📝 Otázka {i}/{len(TEST_QUESTIONS)}: {question}")

            answer = test_question(question, tokenizer, model)

            print(f"💬 Odpověď: {answer[:100]}...")  # Preview

            # Ulož do souboru
            f.write(f"OTÁZKA {i}:\n")
            f.write(f"{question}\n\n")
            f.write(f"ODPOVĚĎ:\n")
            f.write(f"{answer}\n")
            f.write("\n" + "-"*60 + "\n\n")

    print(f"\n✅ Hotovo! Výsledky uloženy do: {OUTPUT_FILE}")
    print("\n💡 Porovnej tyto odpovědi s odpověďmi PO fine-tuningu.")


# ============================================
# MAIN
# ============================================

if __name__ == "__main__":
    run_tests()
