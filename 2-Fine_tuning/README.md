# 🌿 FLEURDIN - FINE-TUNING GEMMA 2-2B-IT

Fine-tuning Gemma 2-2B-it modelu na datasetu **TomasBo/Fleurdin** (2,281 Q&A párů o esenciálních olejích).

---

## 📋 OBSAH

1. [Hardware požadavky](#hardware-požadavky)
2. [Instalace](#instalace)
3. [Workflow](#workflow)
4. [Spuštění](#spuštění)
5. [Výsledky](#výsledky)
6. [Troubleshooting](#troubleshooting)

---

## 💻 HARDWARE POŽADAVKY

### **Minimální:**
- GPU: 12GB VRAM (RTX 3060, RTX 4060 Ti, T4)
- RAM: 16GB
- Disk: 20GB free space

### **Doporučené:**
- GPU: 16GB+ VRAM (RTX 4080, A10G, A100)
- RAM: 32GB
- Disk: 50GB free

### **Alternativy:**
- **Google Colab** (free tier s T4 GPU) ✅ DOPORUČENO pro začátek
- **Kaggle Notebooks** (free P100 GPU)
- **RunPod / Vast.ai** (pronájem GPU od $0.30/hodina)

---

## 📦 INSTALACE

### **1. Klonuj repozitář (nebo jsi už v něm)**

```bash
cd C:\Projects\Fleurdin_AI\2-Fine_tuning
```

### **2. Vytvoř virtual environment**

```bash
# Python 3.10+ required
python -m venv venv

# Aktivuj
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate
```

### **3. Nainstaluj dependencies**

```bash
pip install -r requirements.txt
```

**⚠️ DŮLEŽITÉ:** Pokud máš **NVIDIA GPU**, nainstaluj CUDA-enabled PyTorch:

```bash
# CUDA 11.8
pip install torch --index-url https://download.pytorch.org/whl/cu118

# CUDA 12.1
pip install torch --index-url https://download.pytorch.org/whl/cu121
```

### **4. Ověř GPU**

```bash
python -c "import torch; print(torch.cuda.is_available())"
# Mělo by vrátit: True
```

---

## 🔄 WORKFLOW

```
1. TEST BASE MODEL (PŘED fine-tuningem)
   ↓
   python test_base_model.py
   → Výstup: results_before_finetuning.txt

2. FINE-TUNING
   ↓
   python finetune_gemma.py
   → Training (1-3 hodiny)
   → Model uložen do: ./fleurdin-gemma-2b/

3. TEST FINE-TUNED MODEL (PO fine-tuningu)
   ↓
   python test_finetuned_model.py
   → Výstup: results_after_finetuning.txt

4. POROVNÁNÍ
   ↓
   Porovnej results_before_finetuning.txt vs results_after_finetuning.txt
```

---

## 🚀 SPUŠTĚNÍ

### **KROK 1: Test base modelu (baseline)**

```bash
python test_base_model.py
```

**Co to dělá:**
- Načte base Gemma 2-2B-it (bez fine-tuningu)
- Zeptá se 9 testovacích otázek
- Uloží odpovědi do `results_before_finetuning.txt`

**Čas:** ~5-10 minut (stahování modelu + inference)

---

### **KROK 2: Fine-tuning**

```bash
python finetune_gemma.py
```

**Co to dělá:**
- Načte dataset `TomasBo/Fleurdin` (2,281 Q&A)
- Načte Gemma 2-2B-it v 4-bit quantization
- Přidá LoRA adapters (parameter-efficient)
- Trénuje 3 epochy
- Uloží model do `./fleurdin-gemma-2b/`

**Parametry (můžeš upravit v `finetune_gemma.py`):**
```python
TRAINING_CONFIG = {
    "num_train_epochs": 3,           # Počet epoch
    "per_device_train_batch_size": 4,
    "learning_rate": 2e-4,
}
```

**Čas:** 1-3 hodiny (záleží na GPU)

**Průběžné logy:**
```
Epoch 1/3:  33%|███████████         | 100/300 [15:20<30:40,  9.20s/it]
```

**⚠️ Pokud dojde paměť (OOM):**
- Sniž `per_device_train_batch_size` na 2 nebo 1
- Sniž `max_length` z 512 na 256

---

### **KROK 3: Test fine-tuned modelu**

```bash
python test_finetuned_model.py
```

**Co to dělá:**
- Načte fine-tuned model z `./fleurdin-gemma-2b/`
- Zeptá se stejných 9 otázek
- Uloží odpovědi do `results_after_finetuning.txt`

**Čas:** ~2-5 minut

---

### **KROK 4: Porovnání výsledků**

Otevři oba soubory vedle sebe:
- `results_before_finetuning.txt`
- `results_after_finetuning.txt`

**Očekávané zlepšení:**
✅ Přesnější odpovědi (konkrétní oleje)
✅ Lepší terminologie (aromaterapie)
✅ Stručnější, strukturovanější text
✅ Správné odpovědi na frekvence

---

## 📊 VÝSLEDKY

### **Testovací otázky:**

1. Jaké jsou účinky oregana na tělo?
2. Jaké oleje bys doporučil na psychickou únavu a stres?
3. Které esenciální oleje pomáhají při zažívacích obtížích?
4. Pomůže levandule při nespavosti?
5. Na co se používá máta peprná?
6. K čemu je u oleje uvedená jeho frekvence?
7. Jaké esenciální oleje bys doporučil na bolesti kloubů a svalů?
8. Který olej je dobrý na trávení?
9. Jak bys vytvořil směs olejů na podporu spánku?

### **Metriky k hodnocení:**

| Aspekt | Base model | Fine-tuned model |
|---|---|---|
| **Přesnost** | Obecné odpovědi | Konkrétní oleje z datasetu |
| **Terminologie** | Standardní | Aromaterapie specifická |
| **Styl** | Generický | Expert on EO |
| **Faktičnost** | Možné halucinace | Fakta z datasetu |

---

## 📤 UPLOAD NA HUGGINGFACE

Po úspěšném fine-tuningu:

```bash
# V Python konzoli nebo scriptu
from huggingface_hub import login
login()  # Zadej svůj HF token

# Upload
model.push_to_hub("TomasBo/fleurdin-gemma-2b")
tokenizer.push_to_hub("TomasBo/fleurdin-gemma-2b")
```

Nebo v `finetune_gemma.py` odpověz "y" na výzvu k uploadu.

---

## 🐛 TROUBLESHOOTING

### **Problém: CUDA out of memory**

```
RuntimeError: CUDA out of memory
```

**Řešení:**
1. Sniž batch size v `finetune_gemma.py`:
   ```python
   "per_device_train_batch_size": 2  # nebo 1
   ```

2. Sniž max_length:
   ```python
   max_length=256  # místo 512
   ```

3. Použij gradient checkpointing (už je enabled v LoRA)

---

### **Problém: Model se nestahuje**

```
ConnectionError: Failed to download model
```

**Řešení:**
1. Ověř internet spojení
2. Login do HuggingFace:
   ```bash
   huggingface-cli login
   ```

3. Zkus ručně stáhnout:
   ```python
   from transformers import AutoModelForCausalLM
   model = AutoModelForCausalLM.from_pretrained("google/gemma-2-2b-it")
   ```

---

### **Problém: Slow training**

```
Training trvá 10+ hodin
```

**Řešení:**
1. Ověř že používáš GPU:
   ```python
   import torch
   print(torch.cuda.is_available())  # Mělo by být True
   ```

2. Zkontroluj GPU využití:
   ```bash
   nvidia-smi
   ```

3. Použij mixed precision (už enabled via bf16)

---

### **Problém: Fine-tuned model je horší než base**

**Možné příčiny:**
1. **Overfitting** - zkus méně epoch (1-2 místo 3)
2. **Learning rate moc vysoký** - zkus 1e-4 místo 2e-4
3. **Dataset issues** - zkontroluj kvalitu datasetu

**Řešení:**
```python
# Upravit v finetune_gemma.py
"num_train_epochs": 2,  # místo 3
"learning_rate": 1e-4,  # místo 2e-4
```

---

## 🎯 NEXT STEPS (po fine-tuningu)

1. ✅ Porovnej výsledky (before vs after)
2. ✅ Upload na HuggingFace: `TomasBo/fleurdin-gemma-2b`
3. ✅ Deploy Inference Endpoint (HuggingFace nebo Modal.com)
4. ✅ Integrace do Fleurdin architektury (RAG pipeline)

---

## 📚 RESOURCES

- **Dataset:** https://huggingface.co/datasets/TomasBo/Fleurdin
- **Base model:** https://huggingface.co/google/gemma-2-2b-it
- **PEFT docs:** https://huggingface.co/docs/peft
- **Gemma fine-tuning guide:** https://huggingface.co/blog/gemma-peft

---

**Vytvořeno:** 2025-01-30
**Pro:** Fleurdin AI
**Kontakt:** [@TomasBo](https://huggingface.co/TomasBo)
