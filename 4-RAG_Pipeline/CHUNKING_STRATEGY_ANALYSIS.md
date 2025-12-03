# 🧩 FLEURDIN AI - CHUNKING STRATEGY ANALYSIS (UPDATED)

**Datum vytvoření:** 2025-01-11
**Poslední update:** 2025-12-01
**Autor:** Claude Code + Tomáš
**Status:** ✅ IMPLEMENTOVÁNO A OTESTOVÁNO

---

## 📋 OBSAH

1. [Přehled zdrojových dat](#1-přehled-zdrojových-dat)
2. [Implementované skripty](#2-implementované-skripty)
3. [Chunking strategie](#3-chunking-strategie)
4. [Label structure](#4-label-structure)
5. [Finální výsledky](#5-finální-výsledky)
6. [Embedding model](#6-embedding-model)
7. [Budoucí rozšíření](#7-budoucí-rozšíření)

---

## 📊 1. PŘEHLED ZDROJOVÝCH DAT

### **Současné zdroje (implementováno):**

| Zdroj | Typ | Počet | Velikost | Jazyk | Status |
|-------|-----|-------|----------|-------|--------|
| **Esenciální oleje** | Excel | 30 olejů | ~34,650 znaků | Čeština | ✅ Hotovo |
| **Kniha 1** | Word | 1,590 odstavců | ~184,469 znaků | Slovenština | ✅ Hotovo |
| **Kniha 2** | Word | 1,877 odstavců | ~270,527 znaků | Slovenština | ✅ Hotovo |
| **Voice DRIENKY** | Word | 3 odstavce | ~7,388 znaků | Slovenština | ✅ Hotovo |

### **Budoucí zdroje (plánované):**

| Zdroj | Typ | Očekávaný počet | Kdy přidat |
|-------|-----|----------------|------------|
| **1a) Obecné instrukce oleje** | Text/JSON | 5-10 dokumentů | Postupně |
| **1c) Instrukce pro směsi** | Text/JSON | 5-10 dokumentů | Postupně |
| **Voice transkripty bylinky** | JSON | 10-100 nahrávek | Postupně |
| **Voice transkripty oleje** | JSON | 10-100 nahrávek | Postupně |

---

## 🛠️ 2. IMPLEMENTOVANÉ SKRIPTY

### **Pipeline:**

```
1. parsing_script.py        → Načte zdrojové soubory
2. chunking_script.py        → Vytvoří chunky (1,200 znaků, 200 overlap)
3. embeddings_script.py      → Vytvoří embeddings (384 dimenzí)
4. fix_labels_script.py      → Opraví labels (herb_knowledge, tier)
```

### **Výstupní soubory:**

| Soubor | Velikost | Popis |
|--------|----------|-------|
| `parsed_data.json` | ~1.2 MB | Raw data (3,500 položek) |
| `chunked_data.json` | ~1.7 MB | Chunky (3,505 chunků) |
| `chunked_data_with_embeddings.json` | ~39.5 MB | Chunky + embeddings |
| `chunked_data_FIXED.json` | ~39.5 MB | **FINÁLNÍ** - opravené labels |

---

## 🧩 3. CHUNKING STRATEGIE

### **Parametry (optimalizováno pro GPT-4-mini + náklady):**

```python
CONFIG = {
    "small_chunk_max": 1500,      # Menší než toto = ponechat celé
    "chunk_size": 1200,            # Velikost chunku (KOMPROMIS)
    "overlap": 200                 # Překryv 17%
}
```

### **Proč 1,200 znaků?**

| Velikost | Input náklady | Kvalita | Verdikt |
|----------|--------------|---------|---------|
| 1,000 znaků | $0.000225/query | Dobrá | ❌ Méně kontextu |
| **1,200 znaků** | $0.000319/query | Velmi dobrá | ✅ **OPTIMÁLNÍ** |
| 1,500 znaků | $0.000409/query | Výborná | ❌ Dražší (+30%) |

**Rozdíl:** 1,000 vs 1,200 = **+$0.14/měsíc** (7%) při 5,000 queries
**Benefit:** Lepší kontext, méně follow-up otázek

---

## 🏷️ 4. LABEL STRUCTURE

### **Finální struktura chunků:**

```python
{
  "id": "oil_1_full",
  "type": "essential_oil",           # Hlavní kategorie
  "entity_type": "oil_profile",      # Podkategorie
  "content_type": "database",        # Typ obsahu
  "tier": "free",                    # Business model
  "text": "OLEJ: Oregano...",
  "name": "Oregano - Dobromysl obecná",
  "part": 1,
  "total_parts": 1,
  "chunk_size": 1014,
  "embedding": [0.23, -0.45, ...],   # 384 dimenzí
  "metadata": {
    "category": "esenciální oleje",
    "english_name": "Oregano",
    "latin_name": "Origanum vulgare",
    "frequency": "Doplnit"
  }
}
```

### **Label mapping:**

| Původní type | Nový type | entity_type | content_type | tier |
|-------------|-----------|-------------|--------------|------|
| `essential_oil` | `essential_oil` | `oil_profile` | `database` | `free` |
| `book_paragraph` | `herb_knowledge` | `herb` | `book` | `premium` |
| `voice_transcript` | `herb_knowledge` | `herb` | `voice_transcript` | `premium` |

### **Budoucí typy (připravené):**

| Zdroj | type | entity_type | content_type | tier |
|-------|------|-------------|--------------|------|
| Obecné instrukce oleje | `essential_oil_knowledge` | `general_instruction` | `usage_guide` | `free` |
| Instrukce směsi | `essential_oil_knowledge` | `blend_instruction` | `recipe_guide` | `free` |
| Voice bylinky (nové) | `herb_knowledge` | `herb` | `voice_transcript` | `premium` |

---

## 📊 5. FINÁLNÍ VÝSLEDKY

### **Statistiky:**

```
📂 VSTUP:
  • 4 soubory (1× Excel + 3× Word)
  ↓
📝 PARSING:
  • 3,500 raw položek
  ↓
🧩 CHUNKING:
  • 3,505 chunků (1,200 znaků, 200 overlap)
  ↓
🧠 EMBEDDINGS:
  • 3,505 vektorů (384 dimenzí)
  ↓
🔧 FIX LABELS:
  • 30 essential_oil (tier: free)
  • 3,475 herb_knowledge (tier: premium)
```

### **Rozdělení chunků:**

| Kategorie | Počet | Tier | Průměrná velikost |
|-----------|-------|------|-------------------|
| **Esenciální oleje** | 30 (0.9%) | free | ~1,155 znaků |
| **Knihy o bylinkách** | 3,467 (98.9%) | premium | ~800-1,200 znaků |
| **Voice DRIENKY** | 8 (0.2%) | premium | ~1,098 znaků |
| **CELKEM** | **3,505** | — | ~1,050 znaků |

---

## 🤖 6. EMBEDDING MODEL

### **Model:**
```
paraphrase-multilingual-MiniLM-L12-v2
```

### **Parametry:**
- **Dimenze:** 384
- **Max tokens:** 512 (~2,048 znaků)
- **Jazyky:** Čeština + Slovenština ✅
- **Velikost:** ~420 MB

### **Proč tento model?**
- ✅ Optimalizovaný pro češtinu/slovenštinu
- ✅ Menší (rychlejší inference)
- ✅ Zdarma (open-source)
- ✅ Dobře funguje s 1,200 znakovými chunky

---

## 🚀 7. BUDOUCÍ ROZŠÍŘENÍ

### **7.1 Nové zdroje dat:**

#### **A) Obecné instrukce o olejích (1a):**
```python
{
  "type": "essential_oil_knowledge",
  "entity_type": "general_instruction",
  "content_type": "usage_guide",
  "tier": "free",
  "text": "Jak používat esenciální oleje bezpečně..."
}
```

**Postup přidání:**
1. Vytvoř text/JSON soubory
2. Spusť `parsing_script.py` (aktualizovaný)
3. Spusť `chunking_script.py`
4. Spusť `embeddings_script.py`
5. Nahraj do databáze

---

#### **B) Instrukce pro směsi (1c):**
```python
{
  "type": "essential_oil_knowledge",
  "entity_type": "blend_instruction",
  "content_type": "recipe_guide",
  "tier": "free",
  "text": "Jak vytvořit směs na spaní: Levandule 3 kapky..."
}
```

**Postup:** Stejný jako u 1a

---

#### **C) Voice transkripty (více nahrávek):**
```python
{
  "type": "herb_knowledge",
  "entity_type": "herb",
  "content_type": "voice_transcript",
  "tier": "premium",
  "text": "Každý rok spadnú tony ovocia... [chunk 1/20]",
  "part": 1,
  "total_parts": 20
}
```

**Postup:**
1. Voice-to-text (sentences.json)
2. Parsing (spojit věty)
3. Chunking (1,200 znaků, 200 overlap)
4. Embeddings
5. Upload

**Očekávaný output:** 15-45 chunků/transkript

---

### **7.2 Změna tier (free/premium):**

#### **Příklad: Přesunout vybrané bylinky do free:**

```python
# Script: update_tier_script.py

# Seznam bylin pro free tier
FREE_HERBS = [
    "PÚPAVA LEKÁRSKA",
    "Základné pravidlá zbieranie",
    # ... dalších 10-20
]

# Update tier
for chunk in data['chunks']:
    if chunk['type'] == 'herb_knowledge':
        if any(herb in chunk['text'] for herb in FREE_HERBS):
            chunk['tier'] = 'free'
```

---

### **7.3 Přidání nového oleje:**

#### **Postup (bez re-chunkingu celého datasetu):**

```python
# 1. Přidej olej do Excel
# 2. Spusť pouze:

from sentence_transformers import SentenceTransformer

model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')

new_oil = {
    "id": "oil_31",
    "type": "essential_oil",
    "entity_type": "oil_profile",
    "content_type": "database",
    "tier": "premium",  # nebo "free" - řekneš mi
    "text": "OLEJ: Ylang-Ylang...",
    "name": "Ylang-Ylang",
    ...
}

# Vytvoř embedding
new_oil['embedding'] = model.encode(new_oil['text']).tolist()

# Nahraj do databáze (bez znovu-chunkingu všech dat!)
```

---

## ✅ 8. CHECKLIST PRO NOVÁ DATA

### **Před přidáním nových dat:**

- [ ] Zkontroluj formát (Excel/Word/JSON)
- [ ] Urči `tier` (free/premium)
- [ ] Urči `type`, `entity_type`, `content_type`
- [ ] Parsing → Chunking → Embeddings → Upload
- [ ] Test retrieval (najde se správně?)

### **Po přidání:**

- [ ] Aktualizuj statistiky v tomto dokumentu
- [ ] Test RAG s novými daty
- [ ] Zkontroluj, že tier filtering funguje

---

## 📞 KONTAKT & POZNÁMKY

**Projekt:** Fleurdin AI
**Aktuální stav:** Data připravena pro Supabase upload
**Další krok:** Nahrát `chunked_data_FIXED.json` do Supabase (pgvector)

### **Důležité soubory:**

```
4-RAG_Pipeline/
├── parsing_script.py              # ✅ Hotovo
├── chunking_script.py             # ✅ Hotovo
├── embeddings_script.py           # ✅ Hotovo
├── fix_labels_script.py           # ✅ Hotovo
├── chunked_data_FIXED.json        # ✅ Finální data (39.5 MB)
└── CHUNKING_STRATEGY_ANALYSIS.md  # 📖 Tento dokument
```

---

**Poslední update:** 2025-12-01
**Vytvořeno s ❤️ pro Fleurdin AI**
