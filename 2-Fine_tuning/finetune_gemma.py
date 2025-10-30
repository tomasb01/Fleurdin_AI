"""
FINE-TUNING GEMMA 2-2B-IT PRO FLEURDIN
=======================================

Tento skript fine-tunuje Gemma 2-2B-it model na datasetu TomasBo/Fleurdin
s 2,281 Q&A páry o esenciálních olejích.

Používá:
- LoRA (Low-Rank Adaptation) pro efektivní training
- 4-bit quantization (QLoRA) pro úsporu paměti
- HuggingFace Transformers + PEFT

Hardware requirements:
- GPU: 12GB+ VRAM (RTX 3060+, T4, A10G)
- RAM: 16GB+
- Disk: 20GB free

Alternativně: Google Colab (free tier s T4 GPU)
"""

import torch
from datasets import load_dataset
from transformers import (
    AutoTokenizer,
    AutoModelForCausalLM,
    BitsAndBytesConfig,
    TrainingArguments,
    Trainer
)
from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training
from datetime import datetime

# ============================================
# KONFIGURACE
# ============================================

# Model
BASE_MODEL = "google/gemma-2-2b-it"
OUTPUT_DIR = "./fleurdin-gemma-2b"  # Lokální výstup
HF_REPO_NAME = "TomasBo/fleurdin-gemma-2b"  # HuggingFace repo (pro upload)

# Dataset
DATASET_NAME = "TomasBo/Fleurdin"

# Training hyperparameters
TRAINING_CONFIG = {
    "num_train_epochs": 3,           # Počet epoch (3 je dobrý start)
    "per_device_train_batch_size": 4, # Batch size (4 pro 12GB GPU)
    "gradient_accumulation_steps": 4, # = effective batch 16
    "learning_rate": 2e-4,            # Learning rate pro LoRA
    "warmup_steps": 100,              # Warmup
    "logging_steps": 10,              # Log každých 10 kroků
    "save_steps": 100,                # Save checkpoint každých 100 kroků
    "max_steps": -1,                  # -1 = train celý dataset
}

# LoRA config (pro memory efficient training)
LORA_CONFIG = {
    "r": 16,                    # Rank (16 je standard)
    "lora_alpha": 32,           # Alpha (2x rank)
    "target_modules": [         # Které layers trainovat
        "q_proj",
        "k_proj",
        "v_proj",
        "o_proj",
        "gate_proj",
        "up_proj",
        "down_proj"
    ],
    "lora_dropout": 0.05,       # Dropout
    "bias": "none",
    "task_type": "CAUSAL_LM"
}


# ============================================
# PŘÍPRAVA DATASETU
# ============================================

def prepare_dataset(dataset_name):
    """Načti a připrav dataset pro training"""

    print(f"\n📥 Načítám dataset: {dataset_name}")
    dataset = load_dataset(dataset_name)

    print(f"✅ Dataset načten!")
    print(f"   Počet training příkladů: {len(dataset['train'])}")

    return dataset


def format_chat_for_gemma(example, tokenizer):
    """
    Formátuj konverzaci pro Gemma 2-2B-it chat format

    Input example:
    {
      "text": [
        {"role": "user", "content": "Jaké jsou účinky oregana?"},
        {"role": "assistant", "content": "Oregano má tyto účinky..."}
      ]
    }

    Output: Tokenizovaný text v Gemma formátu
    """

    # Gemma chat template
    messages = example["text"]

    # Apply chat template
    formatted_text = tokenizer.apply_chat_template(
        messages,
        tokenize=False,
        add_generation_prompt=False  # Už máme assistant odpověď
    )

    # Tokenize
    tokenized = tokenizer(
        formatted_text,
        truncation=True,
        max_length=512,  # Max délka (Gemma podporuje až 8k, ale 512 stačí)
        padding=False
    )

    # Labels = stejné jako input_ids (pro causal LM)
    tokenized["labels"] = tokenized["input_ids"].copy()

    return tokenized


# ============================================
# MODEL SETUP
# ============================================

def load_model_for_training():
    """Načti model v 4-bit quantization s LoRA"""

    print(f"\n📥 Načítám base model: {BASE_MODEL}")
    print("⚠️  To může trvat několik minut...")

    # 4-bit quantization config (QLoRA)
    bnb_config = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_use_double_quant=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_compute_dtype=torch.bfloat16
    )

    # Načti model
    model = AutoModelForCausalLM.from_pretrained(
        BASE_MODEL,
        quantization_config=bnb_config,
        device_map="auto",
        trust_remote_code=True
    )

    # Tokenizer
    tokenizer = AutoTokenizer.from_pretrained(BASE_MODEL)
    tokenizer.padding_side = 'right'  # Důležité pro training

    # Připrav model pro k-bit training
    model = prepare_model_for_kbit_training(model)

    # Přidej LoRA adapters
    lora_config = LoraConfig(**LORA_CONFIG)
    model = get_peft_model(model, lora_config)

    # Print trainable parameters
    model.print_trainable_parameters()

    print("✅ Model připraven pro training!")

    return model, tokenizer


# ============================================
# TRAINING
# ============================================

def train_model(model, tokenizer, dataset):
    """Spusť fine-tuning"""

    print("\n" + "="*60)
    print("🚀 SPOUŠTÍM FINE-TUNING")
    print("="*60)

    # Formátuj dataset
    print("\n📝 Formátuji dataset pro Gemma...")
    tokenized_dataset = dataset.map(
        lambda x: format_chat_for_gemma(x, tokenizer),
        remove_columns=dataset["train"].column_names
    )

    # Training arguments
    training_args = TrainingArguments(
        output_dir=OUTPUT_DIR,
        **TRAINING_CONFIG,
        fp16=False,              # Gemma 2 používá bfloat16
        bf16=torch.cuda.is_available(),
        optim="paged_adamw_8bit",  # Optimizer pro QLoRA
        save_total_limit=3,      # Drž max 3 checkpointy
        push_to_hub=False,       # Zatím nenahráváme (uděláme manuálně)
        report_to="none",        # Nebo "wandb" pokud chceš tracking
    )

    # Trainer
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=tokenized_dataset["train"],
        tokenizer=tokenizer,
    )

    # Spusť training
    print("\n⏰ Training začíná...")
    print(f"   Počet epoch: {TRAINING_CONFIG['num_train_epochs']}")
    print(f"   Batch size: {TRAINING_CONFIG['per_device_train_batch_size']}")
    print(f"   Learning rate: {TRAINING_CONFIG['learning_rate']}")
    print("\n💡 Training může trvat 1-3 hodiny (záleží na GPU)\n")

    start_time = datetime.now()

    trainer.train()

    end_time = datetime.now()
    duration = end_time - start_time

    print("\n" + "="*60)
    print("✅ TRAINING DOKONČEN!")
    print("="*60)
    print(f"⏱️  Čas: {duration}")
    print(f"📁 Model uložen do: {OUTPUT_DIR}")

    return trainer


# ============================================
# ULOŽENÍ & UPLOAD
# ============================================

def save_and_upload(trainer, tokenizer):
    """Ulož model lokálně a nahraj na HuggingFace"""

    print("\n💾 Ukládám model...")

    # Ulož LoRA adapters
    trainer.model.save_pretrained(OUTPUT_DIR)
    tokenizer.save_pretrained(OUTPUT_DIR)

    print(f"✅ Model uložen do: {OUTPUT_DIR}")

    # Volitelně: Upload na HuggingFace
    upload = input("\n📤 Chceš nahrát model na HuggingFace? (y/n): ")

    if upload.lower() == 'y':
        print(f"\n📤 Nahrávám na HuggingFace: {HF_REPO_NAME}")
        print("⚠️  Budeš potřebovat HuggingFace token (zadej při výzvě)")

        from huggingface_hub import login
        login()

        trainer.model.push_to_hub(HF_REPO_NAME)
        tokenizer.push_to_hub(HF_REPO_NAME)

        print(f"✅ Model nahrán!")
        print(f"🔗 https://huggingface.co/{HF_REPO_NAME}")
    else:
        print("\n💡 Model můžeš nahrát později pomocí:")
        print(f"   model.push_to_hub('{HF_REPO_NAME}')")


# ============================================
# MAIN
# ============================================

def main():
    print("\n" + "="*60)
    print("🌿 FLEURDIN - FINE-TUNING GEMMA 2-2B-IT")
    print("="*60)

    # 1. Načti dataset
    dataset = prepare_dataset(DATASET_NAME)

    # 2. Načti model
    model, tokenizer = load_model_for_training()

    # 3. Trainuj
    trainer = train_model(model, tokenizer, dataset)

    # 4. Ulož
    save_and_upload(trainer, tokenizer)

    print("\n" + "="*60)
    print("🎉 HOTOVO!")
    print("="*60)
    print("\n📋 NEXT STEPS:")
    print("1. Otestuj fine-tuned model: python test_finetuned_model.py")
    print("2. Porovnej s base modelem")
    print("3. Deploy na HuggingFace Inference Endpoint")
    print("\n")


if __name__ == "__main__":
    main()
