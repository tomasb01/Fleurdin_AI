# 🧩 FLEURDIN AI - CHUNKING STRATEGY ANALYSIS

**Datum:** 2025-01-11
**Autor:** Claude Code + Tomáš
**Účel:** Návrh chunking strategie pro RAG pipeline

---

## 📊 1. PŘEHLED ZDROJOVÝCH DAT

### **Celkový přehled:**

| Zdroj | Typ | Počet chunků (raw) | Celková velikost | Jazyk |
|-------|-----|-------------------|------------------|-------|
| **Esenciální oleje** | Excel | 28 olejů | ~32,340 znaků | Čeština |
| **Kniha 1** | Word | 1,279 odstavců | ~184,469 znaků | Slovenština |
| **Kniha 2** | Word | 1,513 odstavců | ~270,527 znaků | Slovenština |
| **Transkript** | JSON | 58 vět | ~7,331 znaků | Slovenština |
| **CELKEM** | — | **2,878 raw chunků** | **~494,667 znaků** | CS + SK |

---

## 📖 2. ANALÝZA STRUKTURY DAT

### **2.1 Esenciální oleje (Excel)**

**Struktura:**
- 1 řádek = 1 olej
- Sloupce: Název, Anglický název, Latinský název, Frekvence, Účinky na tělo, Účinky na psychiku

**Statistiky:**
- Průměrná délka: **1,155 znaků/olej**
- Min: 768 znaků
- Max: 1,537 znaků

**Příklad chunk (Oregano):**
```
OLEJ: Oregano - Dobromysl obecná

ÚČINKY NA TĚLO:
   • OBECNÉ: Antioxidant, Antibakteriální, Antivirový...
   • TRÁVENÍ: Uvolňuje svaly trávicího traktu...
   • KŮŽE: Na atletickou nohu, plísně nehtů...

ÚČINKY NA PSYCHIKU:
   • Vytváří pocit jistoty, Posiluje mysl...
```

**✅ Doporučení:** 1 olej = 1 chunk (již hotovo)

---

### **2.2 Kniha 1: "Liečivá sila divokých byliniek"**

**Struktura kapitol:**

| # | Kapitola | Odstavců | Délka (znaků) | Status |
|---|----------|----------|---------------|--------|
| 1 | Úvod | ? | ? | ✅ Krátká |
| 2 | Základné pravidlá zbieranie | 1 | 36 | ✅ Krátká |
| 3 | Prečo zaradiť divoké bylinky | 2 | 93 | ✅ Krátká |
| 4 | Zber byliniek | ? | ? | ✅ Krátká |
| 5 | Bylinky nám našepkávajú | 7 | 402 | ✅ Krátká |
| ... | ... | ... | ... | ... |
| 14 | Bylinkové tinktúry | 7 | 378 | ✅ Krátká |
| 22 | 16 jedlých divokých byliniek | 88 | 7,494 | ⚠️ Dlouhá |
| 22a | PÚPAVA LEKÁRSKA | ~6 | 1,822 | ✅ OK |
| 22b | HLUCHAVKA PURPUROVÁ | ~12 | 2,249 | ⚠️ Hranice |
| 22c | CESNAK MEDVEDÍ | ~79 | 7,160 | ⚠️ Dlouhá |

**Poznatky:**
- Kapitoly 1-21: Velmi krátké (36-402 znaků)
- Kapitola 22 (bylinky): Velmi různorodé (1,822 - 7,160 znaků)
- Některé bylinky přesahují optimální velikost pro embeddings

---

### **2.3 Kniha 2: "Z lesa na stôl"**

**Struktura kapitol:**

| # | Kapitola | Odstavců (odhad) | Délka (znaků) | Status |
|---|----------|------------------|---------------|--------|
| 1 | Sila stromov a kríkov | ~4 | ~156 | ✅ Krátká |
| 1a | Prečo stromy a kríky? | ~4 | ? | ✅ Krátká |
| 2 | Signatúry rastlín | ? | ? | ✅ Krátká |
| 3 | Ako zbierať jedlé časti | ? | ? | ✅ Krátká |
| 3a | Etické princípy | ? | ? | ✅ Krátká |
| 4.1 | Hloh obyčajný | 208 | 35,632 | ⚠️⚠️⚠️ VELMI dlouhá |
| 4.2 | Baza čierná | ? | ? | ⚠️ Pravděpodobně dlouhá |
| 4.3 | JARABINA VTÁČIA | ? | ? | ⚠️ Pravděpodobně dlouhá |

**⚠️ KRITICKÝ PROBLÉM:**
- Kapitola "Hloh obyčajný": **35,632 znaků** (208 odstavců)
- To je **~18x větší** než optimální velikost pro embeddings!

---

### **2.4 Transkript (JSON)**

**Struktura:**
- 58 vět z voice-to-text
- Průměrná délka: **126 znaků/věta**
- Max délka: 398 znaků

**✅ Doporučení:** Každá věta = 1 chunk (již hotovo)

---

## 🎯 3. TYPY UŽIVATELSKÝCH DOTAZŮ

**Testovací otázky (z projektu):**

1. **Specifické otázky (1 entita):**
   - "Jaké jsou účinky oregana na tělo?"
   - "Na co se používá máta peprná?"

   → **Potřeba:** Kompletní info o 1 oleji/bylince

2. **Široké otázky (více entit):**
   - "Jaké oleje na stres?"
   - "Které oleje na zažívací obtíže?"

   → **Potřeba:** Najít TOP 3-5 relevantních entit

3. **Recepty/Směsi:**
   - "Jak sestavit recept na spaní?"
   - "Jak vytvořit směs na podporu spánku?"

   → **Potřeba:** Kombinace více entit + LLM vytvoří recept

4. **Obecné znalosti:**
   - "K čemu je frekvence?"

   → **Potřeba:** Teoretické info z kapitol

---

## 📏 4. EMBEDDING MODEL LIMITY

### **Typické limity:**

| Model | Max tokens | Max znaků (odhad) | Doporučená velikost |
|-------|-----------|-------------------|---------------------|
| sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2 | 512 | ~2,048 | 500-1,500 znaků |
| OpenAI text-embedding-3-small | 8,192 | ~32,768 | 500-2,000 znaků |
| OpenAI text-embedding-3-large | 8,192 | ~32,768 | 500-2,000 znaků |

### **⚠️ DŮLEŽITÉ:**
- Delší text = **ztráta přesnosti** embeddings
- Optimální: **800-1,500 znaků** pro multilingual modely
- Maximum: **2,000 znaků** (nad tímto limitem klesá kvalita)

---

## 🧩 5. NAVRHOVANÁ CHUNKING STRATEGIE

### **HYBRIDNÍ STRATEGIE: Entity-based + Fixed-size**

#### **Pravidlo 1: Malé entity (<1,500 znaků)**
```
Celá entita = 1 chunk
```

**Příklady:**
- Esenciální olej "Oregano" (1,014 znaků) → 1 chunk
- Kapitola "Bylinkové tinktúry" (378 znaků) → 1 chunk
- Bylinka "PÚPAVA LEKÁRSKA" (1,822 znaků) → 1 chunk

**Výhoda:** Zachovává kompletní kontext

---

#### **Pravidlo 2: Střední entity (1,500 - 2,500 znaků)**
```
Celá entita = 1 chunk
(ale na hranici limitu)
```

**Příklady:**
- Bylinka "HLUCHAVKA PURPUROVÁ" (2,249 znaků) → 1 chunk

**⚠️ Poznámka:** Na horní hranici - možné rozdělit, pokud embedding model má problémy

---

#### **Pravidlo 3: Velké entity (>2,500 znaků)**
```
Rozdělit na fixed-size chunky:
- Velikost: 1,000 znaků
- Overlap: 150 znaků (15%)
- Metadata: entity_name, part_number
```

**Příklad:**
```json
{
  "id": "book2_hloh_part_1",
  "text": "Hloh obyčajný – tŕnistý poklad... [1000 znaků]",
  "metadata": {
    "entity_name": "Hloh obyčajný",
    "entity_type": "herb",
    "part": 1,
    "total_parts": 36,
    "source": "kniha2",
    "category": "bylinky"
  }
}
```

**Výhoda:**
- Všechny chunky mají stejnou velikost (optimální pro embeddings)
- Metadata umožňují LLM pochopit, že chunky patří k sobě
- Overlap zajišťuje, že info na hranici chunků se neztratí

---

### **5.1 Detekce entit (kapitol/bylin)**

**Heuristika pro detekci nadpisů:**

1. **Kapitoly:**
   - Krátké odstavce (<60 znaků)
   - Začínají velkým písmenem
   - Obsahují klíčová slova: "Kapitola", číslo, otázník

2. **Bylinky:**
   - Krátké odstavce (<100 znaků)
   - Obsahují latinský název nebo uppercase název
   - Následují po kapitole "16 jedlých divokých byliniek" nebo "Kapitola 4"

3. **Konec entity:**
   - Další nadpis (podle pravidel výše)
   - Nebo konec souboru

---

## ⚙️ 6. KLÍČOVÉ PARAMETRY

### **📐 Chunking parametry:**

```python
CHUNKING_CONFIG = {
    # Entity-based thresholds
    "small_entity_max": 1500,      # znaků - celá entita = 1 chunk
    "medium_entity_max": 2500,     # znaků - celá entita = 1 chunk (hranice)

    # Fixed-size parameters (pro velké entity)
    "fixed_chunk_size": 1000,      # znaků
    "fixed_chunk_overlap": 150,    # znaků (15%)

    # Heading detection
    "heading_max_length": 100,     # znaků - max délka nadpisu
    "heading_keywords": [
        "Kapitola", "kapitola",
        "Úvod", "úvod",
        "Prečo", "Ako", "Čo",
        "?", ":"
    ],

    # Entity detection
    "herb_indicators": [
        "LEKÁRSKA", "OBYČAJNÝ", "VTÁČIA",  # Uppercase názvy
        "Latinský názov:",                  # Latinský název
        "Český názov:"
    ]
}
```

---

### **📊 Očekávané výsledky:**

| Typ | Počet entit (raw) | Očekávané chunky | Průměrná délka |
|-----|-------------------|------------------|----------------|
| **Esenciální oleje** | 28 | 28 | ~1,155 znaků |
| **Kniha 1 - kapitoly** | 21 | 21 | ~300 znaků |
| **Kniha 1 - bylinky** | 16 | ~40-50 | ~1,000 znaků |
| **Kniha 2 - kapitoly** | ~10 | ~10 | ~500 znaků |
| **Kniha 2 - stromy** | 3+ | ~150-200 | ~1,000 znaků |
| **Transkript** | 58 | 58 | ~126 znaků |
| **CELKEM** | ~136 | **~300-370 chunků** | ~800-1,200 znaků |

**📉 Redukce:** Z 2,878 raw odstavců → **~300-370 optimalizovaných chunků**

---

## ✅ 7. VÝHODY NAVRHOVANÉ STRATEGIE

1. **Zachovává logickou strukturu:**
   - Malé entity (oleje, krátké kapitoly) zůstávají celé
   - Kontext není rozsekán

2. **Optimální velikost pro embeddings:**
   - Většina chunků: 800-1,500 znaků
   - Ideální pro multilingual modely

3. **Flexibilní:**
   - Funguje pro různé typy dat (strukturované vs. volný text)
   - Adaptuje se na velikost entity

4. **Metadata pro kontext:**
   - LLM ví, že chunk #5 a #6 patří k "Hloh obyčajný"
   - Může poskládat kompletní odpověď z více chunků

5. **Overlap prevence ztráty:**
   - 150 znaků overlap = ~1-2 věty
   - Zajišťuje kontinuitu na hranicích

---

## ⚠️ 8. POTENCIÁLNÍ NEVÝHODY & RIZIKA

1. **Komplexnost implementace:**
   - Detekce entit (nadpisů) není triviální
   - Může selhat u nestandardních formátů

2. **Různé velikosti chunků:**
   - Entity-based chunky: 300-2,500 znaků
   - Fixed-size chunky: přesně 1,000 znaků
   - Embedding model může mít různou přesnost

3. **Velké entity rozsekané:**
   - "Hloh obyčajný" → 36 chunků
   - RAG musí najít správný chunk z těchto 36
   - Uživatel může dostat neúplnou odpověď

4. **Overlap = duplicita:**
   - 150 znaků overlap = ~15% navíc dat
   - Větší databáze, pomalejší vyhledávání

---

## 🤔 9. ALTERNATIVNÍ PŘÍSTUPY

### **Alternativa 1: Pure Fixed-size**
```
Všechny chunky = 800 znaků, overlap 150 znaků
```

**Výhody:**
- Jednoduchá implementace
- Konzistentní velikost

**Nevýhody:**
- Rozsekává i malé entity
- Ztráta logické struktury

---

### **Alternativa 2: Semantic Chunking**
```
Použít LLM/NLP pro detekci sémantických hranic
```

**Výhody:**
- Nejinteligentnější
- Zachovává význam

**Nevýhody:**
- Velmi komplexní
- Pomalé (potřebuje LLM)
- Drahé

---

### **Alternativa 3: Pure Entity-based (bez limitu)**
```
1 entita = 1 chunk (i když má 35k znaků)
```

**Výhody:**
- Nejjednodušší
- Zachovává kompletní kontext

**Nevýhody:**
- Embedding modely selhávají na dlouhých textech
- Špatná přesnost vyhledávání

---

## 📝 10. IMPLEMENTAČNÍ KROKY

### **Krok 1: Detekce entit**
```python
def detect_entities(paragraphs):
    entities = []
    current_entity = None

    for para in paragraphs:
        if is_heading(para):
            if current_entity:
                entities.append(current_entity)
            current_entity = {"name": para, "content": []}
        else:
            if current_entity:
                current_entity["content"].append(para)

    return entities
```

### **Krok 2: Chunking podle velikosti**
```python
def chunk_entity(entity):
    text = "\n\n".join(entity["content"])

    if len(text) <= SMALL_ENTITY_MAX:
        return [create_chunk(text, entity["name"], part=1, total=1)]

    elif len(text) <= MEDIUM_ENTITY_MAX:
        return [create_chunk(text, entity["name"], part=1, total=1)]

    else:
        return fixed_size_chunking(text, entity["name"])
```

### **Krok 3: Fixed-size chunking s overlapem**
```python
def fixed_size_chunking(text, entity_name):
    chunks = []
    start = 0
    part = 1

    while start < len(text):
        end = start + FIXED_CHUNK_SIZE
        chunk_text = text[start:end]

        chunks.append(create_chunk(
            chunk_text,
            entity_name,
            part=part,
            total=math.ceil(len(text) / FIXED_CHUNK_SIZE)
        ))

        start += (FIXED_CHUNK_SIZE - FIXED_CHUNK_OVERLAP)
        part += 1

    return chunks
```

---

## 🎯 11. OTEVŘENÉ OTÁZKY PRO FEEDBACK

### **Otázky k diskuzi:**

1. **Je 1,000 znaků optimální pro fixed-size chunky?**
   - Alternativa: 800 znaků (menší, více chunků)
   - Alternativa: 1,500 znaků (větší, méně chunků)

2. **Je 150 znaků overlap dostatečný?**
   - Alternativa: 100 znaků (10% overlap)
   - Alternativa: 200 znaků (20% overlap)

3. **Měli bychom použít semantic chunking pro velké entity?**
   - Např. LLM rozdělí "Hloh" na logické sekce (účinky, použití, recepty)
   - Trade-off: komplexnost vs. kvalita

4. **Jak řešit velmi dlouhé entity (35k znaků)?**
   - Současný návrh: 36 chunků po 1,000 znaků
   - Alternativa: Summarization → 1 chunk se shrnutím + detailní chunky

5. **Transkript (58 vět) - spojit nebo nechat jednotlivé?**
   - Současný návrh: Každá věta = 1 chunk
   - Alternativa: Spojit do 5-10 větších chunků

6. **Jak řešit multilingual (čeština + slovenština)?**
   - Jeden embedding model pro oboje?
   - Nebo separátní modely?

---

## 📚 12. DOPORUČENÉ EMBEDDING MODELY

### **Pro multilingual (čeština + slovenština):**

| Model | Velikost | Max tokens | Výhody | Nevýhody |
|-------|----------|-----------|---------|----------|
| **paraphrase-multilingual-MiniLM-L12-v2** | 418 MB | 512 | ✅ Zdarma, Rychlý | ⚠️ Menší přesnost |
| **intfloat/multilingual-e5-large** | 2.24 GB | 512 | ✅ Vysoká přesnost | ⚠️ Větší, pomalejší |
| **OpenAI text-embedding-3-small** | API | 8,192 | ✅ Velmi dobrý, dlouhý kontext | ⚠️ Platba za API |

**Doporučení:** `paraphrase-multilingual-MiniLM-L12-v2` pro začátek (zdarma, dobrý pro slovenštinu/češtinu)

---

## 📊 13. OČEKÁVANÉ METRIKY

### **Po implementaci měřit:**

1. **Počet chunků:**
   - Cíl: ~300-400 chunků

2. **Průměrná délka chunku:**
   - Cíl: 800-1,200 znaků

3. **Retrieval přesnost:**
   - Test na 9 otázkách z `test_questions.txt`
   - Metrika: Top-3 relevance (jsou relevantní chunky v top 3?)

4. **Context completeness:**
   - Dostane LLM dostatek kontextu k odpovědi?
   - Nebo musí kombinovat více chunků?

---

## 🚀 14. NEXT STEPS

### **Implementace:**

1. ✅ Parsing zdrojových dat (HOTOVO)
2. 🔄 Implementace chunking strategie (PROBÍHÁ)
   - Detekce entit
   - Hybridní chunking
3. ⏳ Vytvoření embeddings (sentence-transformers)
4. ⏳ Upload do Supabase (pgvector)
5. ⏳ RAG pipeline (retrieval + LLM)
6. ⏳ Testing & evaluace

---

## 📞 KONTAKT & FEEDBACK

**Projekt:** Fleurdin AI
**GitHub:** [doplnit]
**Feedback:** Prosím o review:
- Jsou parametry (1000/150) správné?
- Máte zkušenosti s multilingual embeddings?
- Doporučujete jinou strategii?

---

**Vytvořeno:** 2025-01-11
**Verze:** 1.0
**Status:** Návrh pro review

---

## 📎 PŘÍLOHY

### **A. Testovací otázky (test_questions.txt)**

```
1. Jaké jsou účinky oregana na tělo?
2. Jaké oleje bys doporučil na psychickou únavu a stres?
3. Které esenciální oleje pomáhají při zažívacích obtížích?
4. Jak bys sestavil recept na spaní?
5. Na co se používá máta peprná?
6. K čemu je u oleje uvedená jeho frekvence?
7. Jaké esenciální oleje bys doporučil na bolesti kloubů a svalů?
8. Který olej je dobrý na trávení?
9. Jak bys vytvořil směs olejů na podporu spánku?
```

### **B. Příklad vyčištěného chunku (Oregano)**

```json
{
  "id": "oil_1",
  "type": "essential_oil",
  "name": "Oregano - Dobromysl obecná",
  "text": "OLEJ: Oregano - Dobromysl obecná\n\nÚČINKY NA TĚLO:\n   • OBECNÉ: Antioxidant, Antibakteriální, Antivirový, Protiplísňový, Přírodní antibiotikum, Protizánětlivý, Účinný proti zlatému stafylokoku, Pomáhá snižovat vedlejší účinky léků\n\n   • TRÁVENÍ: Trávení – uvolňuje svaly trávicího traktu, Obnovuje bakteriální rovnováhu, Při pálení žáhy, Nadýmání, Plynatost, Reflux, Při léčbě přerůstání bakterií tenkého střeva (SIBO), Proti střevním parazitům\n\n   • KŮŽE: Na atletickou nohu, Plísně nehtů, Proti bradavicím\n\n   • DÝCHÁNÍ: U pneumonie, bronchitida, nachlazení\n\n   • BOLEST: Analgetikum – na bolest uší, zubů, dásní, Proti bolesti hlavy\n\n   • SVALY / ŠLACHY / KLOUBY: Při revmatismu\n\n   • SRDCE/CÉVY: Podporuje správnou hladinu cholesterolu\n\n   • OSTATNÍ: Repelent, Podporuje hubnutí, Při léčbě obezity, Vaginální kvasinkové infekce, Podporuje přirozené obranné procesy buněk (podpora proti rakovině)\n\nÚČINKY NA PSYCHIKU:\n   • PSYCHIKA / EMOCE: Vytváří pocit jistoty, Posiluje mysl, Obnovuje silné odhodlání v životě",
  "metadata": {
    "source": "excel",
    "category": "esenciální oleje",
    "english_name": "Oregano",
    "latin_name": "Origanum vulgare",
    "frequency": "Není údaj"
  }
}
```

### **C. Příklad velkého chunku rozděleného (Hloh - část 1)**

```json
{
  "id": "book2_hloh_part_1",
  "type": "herb_book",
  "name": "Hloh obyčajný - část 1/36",
  "text": "Hloh obyčajný – tŕnistý poklad našich lesov\n\nLatinský názov: Crataegus laevigata\n\nČeský názov: hloh obecný\n\nKedysi som hloh poznala len ako rastlinu na podporu srdca. Bola to pre mňa suchá informácia, ktorá ma nijako neoslovila. Až keď som sa začala venovať divokým bylinkám, uvedomila som si, že hloh je oveľa viac než len liek. Je to živý organizmus s vlastnou históriou, ktorý má čo ponúknuť nielen nášmu zdraviu, ale aj duši.\n\nNa jar sa hloh zahalí do závoja bielych alebo ružových kvetov, ktoré vonia sladko a jemne. V lete dozrievajú malé červené plody, ktoré sú plné živín. Hloh je rastlina, ktorá nás sprevádza celým rokom a pripomína nám cykly prírody... [pokračování do 1000 znaků]",
  "metadata": {
    "source": "kniha2",
    "category": "bylinky",
    "entity_name": "Hloh obyčajný",
    "entity_type": "herb",
    "part": 1,
    "total_parts": 36,
    "chapter": "4.1"
  }
}
```

---

**Konec dokumentu**
