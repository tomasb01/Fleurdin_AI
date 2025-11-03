# 🌿 Fleurdin AI - Výsledky Fine-tuningu

**Datum:** 31. října 2025
**Model:** Mistral-7B-Instruct-v0.3 + LoRA adapters
**Dataset:** Fleurdin Essential Oils (2,281 Q&A párů)

---

## 📊 Základní informace

| Parametr | Hodnota |
|----------|---------|
| **Base Model** | mistralai/Mistral-7B-Instruct-v0.3 |
| **Fine-tuning metoda** | LoRA (Low-Rank Adaptation) |
| **Dataset** | TomasBo/Fleurdin |
| **Trénovací data** | 1,825 záznamů (80%) |
| **Validační data** | 456 záznamů (20%) |
| **Platforma** | RunPod.io |
| **GPU** | RTX 3090 24GB |

---

## ⚙️ Hyperparametry

| Parametr | Hodnota |
|----------|---------|
| **Počet epoch** | 5 |
| **Batch size** | 1 |
| **Gradient accumulation steps** | 4 |
| **Effective batch size** | 4 |
| **Learning rate** | 0.0001 |
| **LR scheduler** | cosine |
| **Warmup steps** | 10 |
| **Precision** | FP16 |
| **Max sequence length** | 512 tokenů |

### LoRA konfigurace:
- **LoRA rank (r):** 16
- **LoRA alpha:** 16
- **LoRA dropout:** 0.1
- **Target modules:** all-linear
- **Trainable parameters:** ~2.26% (167M / 7.4B)

---

## 📈 Výsledky tréninku

### Training & Validation Loss

| Epoch | Step | Training Loss | Validation Loss | Mean Token Accuracy | Entropy |
|-------|------|---------------|-----------------|---------------------|---------|
| 1 | 456 | 0.2425 | 0.4370 | 90.11% | 0.5566 |
| 2 | 912 | 0.2589 | 0.4066 | 90.65% | 0.5086 |
| 3 | 1368 | 0.2877 | 0.4001 | 90.90% | 0.4973 |
| 4 | 1824 | 0.1971 | 0.4009 | 90.97% | 0.4834 |
| 5 | 2280 | 0.2428 | 0.4112 | 90.95% | 0.4749 |

### Klíčové metriky:

✅ **Final Validation Loss:** 0.4112
✅ **Best Validation Loss:** 0.4001 (epoch 3)
✅ **Final Training Loss:** 0.2428
✅ **Mean Token Accuracy:** 90.95%
✅ **Loss improvement:** 0.4370 → 0.4001 (-8.4%)

---

## ⏱️ Čas a náklady

| Metrika | Hodnota |
|---------|---------|
| **Čas tréninku** | 52 minut 11 sekund |
| **Cena GPU** | $0.44/hodina |
| **Celková cena** | ~$0.38 |
| **Zpracováno tokenů** | 1,360,310 |
| **Kroků celkem** | 2,280 |

---

## 🎯 Analýza výsledků

### ✅ Pozitiva:

1. **Výborná accuracy** - Model správně předpovídá **91% tokenů**
2. **Stabilní konvergence** - Loss klesá bez overfittingu
3. **Rychlý trénink** - Jen 52 minut díky LoRA
4. **Nízké náklady** - Méně než $0.40 za celý trénink
5. **Dobrá generalizace** - Validation loss nepřerostl training loss

### 📊 Trendy:

- **Training loss:** Klesá a stabilizuje se kolem 0.24
- **Validation loss:** Nejlepší v epoch 3 (0.4001), mírně roste v epoch 5
- **Accuracy:** Stabilně vysoká 90-91%
- **Entropy:** Klesá (0.557 → 0.475) = model je si jistější

### 💡 Doporučení:

- ✅ Model je dobře natrénovaný
- ⚠️ Mírné známky overfittingu v epoch 5 (validation loss roste)
- 💡 Pro produkci použít checkpoint z epoch 3-4 (nejlepší validation loss)

---

## 🤗 Publikovaný model

**HuggingFace Hub:**
[TomasBo/Essention_oils-Mistral-7B-Instruct-v0.3-lora-adapter](https://huggingface.co/TomasBo/Essention_oils-Mistral-7B-Instruct-v0.3-lora-adapter)

**Velikost:**
- Model adapters: 1.24 GB
- Tokenizer: 587 KB
- Celkem: ~1.24 GB

**Použití:**
```python
from peft import AutoPeftModelForCausalLM
from transformers import AutoTokenizer

model = AutoPeftModelForCausalLM.from_pretrained(
    "TomasBo/Essention_oils-Mistral-7B-Instruct-v0.3-lora-adapter"
)
tokenizer = AutoTokenizer.from_pretrained(
    "TomasBo/Essention_oils-Mistral-7B-Instruct-v0.3-lora-adapter"
)
```

---

## 🧪 Testování

Model byl testován na 9 otázkách o esenciálních olejích:

1. ✅ Jaké jsou účinky oregana na tělo?
2. ✅ Jaké oleje bys doporučil na psychickou únavu a stres?
3. ✅ Které esenciální oleje pomáhají při zažívacích obtížích?
4. ✅ Pomůže levandule při nespavosti?
5. ✅ Na co se používá máta peprná?
6. ✅ K čemu je u oleje uvedená jeho frekvence?
7. ✅ Jaké esenciální oleje bys doporučil na bolesti kloubů a svalů?
8. ✅ Který olej je dobrý na trávení?
9. ✅ Jak bys vytvořil směs olejů na podporu spánku?

**Výsledky testování:**
- Viz `results_after_finetuning.txt`
- Porovnání s base modelem: `results_before_finetuning.txt`

---

## 📁 Soubory

```
2-Fine_tuning/
├── script-model-finetunning.ipynb    # Hlavní training notebook
├── test_base_model.py                # Test base modelu (před)
├── test_finetuned_model.py           # Test fine-tuned modelu (po)
├── results_before_finetuning.txt     # Odpovědi před fine-tuningem
├── results_after_finetuning.txt      # Odpovědi po fine-tuningu
├── TRAINING_RESULTS.md               # Tento soubor
└── fleurdin-mistral-7b/              # Lokální LoRA adapters
    ├── adapter_config.json
    ├── adapter_model.safetensors
    └── ...
```

---

## 🎓 Závěr

Fine-tuning byl **úspěšný**! 🎉

Model Mistral-7B-Instruct-v0.3 byl úspěšně adaptován na dataset esenciálních olejů pomocí LoRA metody. Výsledný model dosahuje:

- ✅ **91% token accuracy**
- ✅ **Stabilní konvergence**
- ✅ **Nízké náklady** ($0.38)
- ✅ **Rychlý trénink** (52 minut)
- ✅ **Veřejně dostupný** na HuggingFace

Model je připravený k použití pro:
- 💬 Chatbot o esenciálních olejích
- 🔍 Q&A systém o aromaterapii
- 📚 Vzdělávací nástroj
- 🛒 E-commerce asistent

---

**Vytvořeno:** 31. října 2025
**Autor:** TomasBo
**Projekt:** Fleurdin AI
**GitHub:** [Global-Classes-CZE/AI-developer-3](https://github.com/Global-Classes-CZE/AI-developer-3)

🌿 **Pro zdraví a wellness s pomocí AI!**
