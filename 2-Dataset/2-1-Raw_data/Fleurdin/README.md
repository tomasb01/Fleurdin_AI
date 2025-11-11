---
license: mit
language:
- cs
tags:
- conversational
- essential-oils
- aromatherapy
- czech
- qa
- chatbot
size_categories:
- 1K<n<10K
task_categories:
- question-answering
- text-generation
pretty_name: Fleurdin Essential Oils Dataset
---

# 🌿 Fleurdin Essential Oils Dataset

Dataset obsahující **Q&A páry o esenciálních olejích v českém jazyce** pro fine-tuning jazykových modelů.

## 📊 Přehled

Tento dataset byl vytvořen pro trénování AI modelů jako expertů na esenciální oleje a aromaterapii. Obsahuje podrobné informace o účincích, použití a vlastnostech esenciálních olejů.

### Statistiky
- **Celkem Q&A párů:** 2,281
- **Počet esenciálních olejů:** 30
- **Průměr Q&A na olej:** ~76 otázek
- **Jazyk:** Čeština 🇨🇿
- **Formát:** Konverzační páry (user/assistant)

### Zahrnuté esenciální oleje
Oregano, Petitgrain, Pomeranč sladký, Rozmarýn, Růže, Řebříček, Santalové dřevo, Skořicová kůra, Slaměnka, Smrk černý, Smrk modrý, Heřmánek pravý, Jabloňák, Kadidlo, Kafrovník, Levandule, Limetka, Majoránka, Mandarinka zelená, Máta peprná, Meduňka, Muškátový oříšek, Myrha, Vavřín, Bazalka, Bergamot, Borovice lesní, Koriandr, Frangipani, Ho wood

## 📋 Struktura dat

Každý záznam obsahuje pole `text` s konverzačními zprávami:

```python
{
  "text": [
    {
      "role": "user",
      "content": "Jaké jsou účinky oregana na tělo?"
    },
    {
      "role": "assistant",
      "content": "Oregano má tyto účinky na tělo: OBECNÉ: Antioxidant, Antibakteriální..."
    }
  ]
}
```

### Kategorie účinků
Data jsou organizována do kategorií:
- **OBECNÉ** - Základní vlastnosti (antioxidant, antibakteriální, antivirové...)
- **TRÁVENÍ** - Účinky na trávicí systém
- **KŮŽE** - Dermatologické aplikace
- **DÝCHÁNÍ** - Respirační systém
- **BOLEST** - Analgetické účinky
- **PSYCHIKA/EMOCE** - Mentální a emocionální účinky

## 🎯 Typy otázek

Dataset obsahuje 6 typů otázek pro každý olej:

1. **Obecné otázky** (8 variant)
   - "Co je oregano?"
   - "Řekni mi o oregano."

2. **Účinky na tělo** (8 variant)
   - "Jaké jsou účinky oregana na tělo?"
   - "Jak oregano působí na tělo?"

3. **Účinky na psychiku** (9 variant)
   - "Jak oregano ovlivňuje psychiku?"
   - "Jaké má oregano mentální účinky?"

4. **Použití** (6 variant)
   - "Na co se používá oregano?"
   - "Kdy použít oregano?"

5. **Specifické účinky** (30-40 variant)
   - "Pomůže oregano při nadýmání?"
   - "Je oregano dobrý na bolest hlavy?"

6. **Reverzní otázky** (15-20 variant)
   - "Který esenciální olej pomáhá při stresu?"
   - "Co použít na akné?"

## 💻 Použití

### Načtení datasetu

```python
from datasets import load_dataset

dataset = load_dataset("TomasBo/Fleurdin")

# Přístup k datům
train_data = dataset["train"]

# Zobrazení prvního záznamu
print(train_data[0])
```

### Fine-tuning s Transformers

```python
from transformers import AutoTokenizer, AutoModelForCausalLM, TrainingArguments, Trainer

# Načti model a tokenizer
model_name = "google/gemma-2-2b"  # nebo jiný model
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(model_name)

# Načti dataset
dataset = load_dataset("TomasBo/Fleurdin")

# Fine-tuning konfigurace
training_args = TrainingArguments(
    output_dir="./fleurdin-eo-model",
    num_train_epochs=3,
    per_device_train_batch_size=4,
    save_steps=100,
    logging_steps=50,
)

# Spusť trénink
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=dataset["train"],
)

trainer.train()
```

## 🎓 Případy použití

- **Chatbot o esenciálních olejích** - Conversational AI expert
- **Zdravotnické poradenství** - Informace o aromaterapii
- **E-commerce asistent** - Doporučení produktů
- **Vzdělávací nástroj** - Výuka o esenciálních olejích

## 📝 Příprava dat

Dataset byl vytvořen pomocí automatizovaného procesu:

1. **Sběr zdrojových dat** - Odborné informace o 30 esenciálních olejích
2. **Kategorizace** - Organizace účinků do logických kategorií
3. **Generování Q&A** - Vytvoření 50-100 otázek na olej pomocí template systému
4. **Validace** - Kontrola kvality a konzistence dat
5. **Formátování** - Převod do HuggingFace formátu

### Zajištění kvality
- ✅ Všechny oleje mají kompletní informace
- ✅ Konzistentní kategorizace
- ✅ Žádné duplicity
- ✅ Validace zdrojových dat

## ⚖️ Licence

**MIT License** - Volně použitelné pro komerční i nekomerční účely.

## 👤 Autor

Dataset vytvořil **Fleurdin AI** pro účely vzdělávání a tréninku AI modelů v oblasti aromaterapie a esenciálních olejů.

### Kontakt
- HuggingFace: [@TomasBo](https://huggingface.co/TomasBo)
- Dataset: [Fleurdin](https://huggingface.co/datasets/TomasBo/Fleurdin)

## 🔄 Verze

- **v1.0** (2025) - Iniciální release s 30 esenciálními oleji a 2,281 Q&A páry

## 📚 Citace

Pokud používáš tento dataset ve svém výzkumu nebo projektu, prosím cituj:

```bibtex
@dataset{fleurdin_eo_2025,
  title={Fleurdin Essential Oils Dataset},
  author={Fleurdin AI},
  year={2025},
  publisher={HuggingFace},
  url={https://huggingface.co/datasets/TomasBo/Fleurdin}
}
```

## 🚀 Budoucí plány

- [ ] Rozšíření na 200-300 esenciálních olejů
- [ ] Přidání anglické verze datasetu
- [ ] Zahrnutí informací o bezpečnosti a kontraindikacích
- [ ] Přidání údajů o kombinacích olejů
- [ ] Multimodální data (obrázky olejů)

## 🙏 Poděkování

Děkujeme všem, kteří přispěli k vytvoření tohoto datasetu a podporují open-source AI v oblasti zdraví a wellnessu.

---

**Vytvořeno s ❤️ pro komunitu esenciálních olejů a AI**
