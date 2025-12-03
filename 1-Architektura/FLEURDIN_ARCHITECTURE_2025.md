# 🌿 FLEURDIN AI - ARCHITEKTURA 2025

**Verze:** 2.0 (Aktualizováno)
**Datum:** 2025-12-02
**Status:** RAG Pipeline implementována ✅
**Účel:** AI chatbot pro konzultace o esenciálních olejích a bylinkách

---

## 📋 OBSAH

1. [Přehled projektu](#přehled-projektu)
2. [Business model](#business-model)
3. [Technická architektura](#technická-architektura)
4. [RAG Pipeline (Klíčová změna)](#rag-pipeline)
5. [Databáze a data](#databáze-a-data)
6. [Security](#security)
7. [Náklady a revenue](#náklady-a-revenue)
8. [Aktuální stav](#aktuální-stav)
9. [Otevřené otázky](#otevřené-otázky)

---

## 🎯 PŘEHLED PROJEKTU

### **Co je Fleurdin AI?**

Konverzační AI chatbot pro **www.fleurdin.cz** poskytující expertní konzultace o:
- **Esenciálních olejích** (30 olejů v databázi)
- **Bylinkách** (3,475 chunků z knih a voice transkriptů)
- **Aromaterapii a přírodní medicíně**

### **Příklad konverzace:**

```
USER: "Nemůžu spát, jaký olej mi pomůže?"

BOT (FREE):
"Pro lepší spánek doporučuji levanduli. Má uklidňující účinky
na nervový systém a pomáhá při nespavosti."

USER: "A jak to mám použít?"

BOT (FREE):
"💎 Pro detailní recepty s počtem kapek si prosím vytvořte
účet v placené verzi."

---

BOT (PREMIUM):
"Pro lepší spánek doporučuji:

**Recept:**
- Levandule: 3 kapky
- Meduňka: 2 kapky
- Bergamot: 1 kapka

**Použití:** Přidej do difuzéru 30 minut před spaním, nebo
namíchej s mandlovým olejem (10ml) a potři záda před uložením."
```

---

## 💰 BUSINESS MODEL

### **Freemium strategie:**

| Feature | FREE | PREMIUM |
|---------|------|---------|
| Konverzační AI | ✅ Pamatuje kontext | ✅ Pamatuje kontext |
| Počet olejů | 30 olejů | 30 olejů (+ budoucí rozšíření) |
| Doporučení | ✅ | ✅ |
| Recepty (kapky, použití) | ❌ | ✅ |
| **Bylinky (premium obsah)** | ❌ | ✅ 3,475 chunků |
| Cena | Zdarma | 299 Kč/měsíc (~$13) |

### **Revenue projekce:**

| Fáze | Free users | Premium | MRR (Kč) | Profit |
|------|-----------|---------|---------|---------|
| Měsíc 1-3 | 100 | 10 | 2,990 | +490 Kč |
| Měsíc 4-6 | 300 | 30 | 8,970 | +6,270 Kč |
| ROK 2 | 1,000 | 100 | 29,900 | +26,400 Kč |

**Break-even:** 3-6 měsíců (10-15 premium users)

---

## 🏗️ TECHNICKÁ ARCHITEKTURA

### **High-level diagram:**

```
┌─────────────────────────────────────────────────┐
│         WIX Website (fleurdin.cz)               │
│            Embedded Chat Widget                 │
└──────────────────┬──────────────────────────────┘
                   ↓ HTTPS
┌─────────────────────────────────────────────────┐
│       Vercel Next.js API + LangChain            │
│                                                 │
│  /api/chat:                                     │
│  1. Rate limiting (free vs premium)            │
│  2. User tier check (Supabase Auth)            │
│  3. RAG Pipeline:                               │
│     - Vector search (Supabase pgvector)        │
│     - Retrieve top 5-10 relevant chunks         │
│     - Build context + system prompt             │
│     - Call OpenAI GPT-4-mini                    │
│  4. Format response (based on tier)            │
│  5. Save conversation history                  │
└──────────────────┬──────────────────────────────┘
                   ↓
         ┌─────────┴─────────┐
         ↓                   ↓
┌──────────────────┐  ┌──────────────────────┐
│   SUPABASE       │  │   OPENAI             │
│                  │  │                      │
│ • pgvector (RAG) │  │ • GPT-4-mini         │
│ • Auth           │  │   (nebo GPT-4o-nano) │
│ • Users          │  │                      │
│ • Conversations  │  │ • Inference API      │
│ • knowledge_     │  │ • $0.150/1M input    │
│   chunks (3,505) │  │ • $0.600/1M output   │
└──────────────────┘  └──────────────────────┘
```

### **Klíčová změna: RAG místo fine-tuningu**

#### **PŮVODNÍ PLÁN (Fine-tuning):**
```
❌ Fine-tune Gemma 2B na vlastním datasetu
❌ HuggingFace Inference Endpoint ($50-80/měsíc)
❌ Re-training při každé změně
❌ Komplikované update procesu
```

#### **AKTUÁLNÍ ŘEŠENÍ (RAG + GPT-4-mini):**
```
✅ Použití OpenAI GPT-4-mini (state-of-the-art)
✅ RAG Pipeline s Supabase pgvector
✅ Žádný training - data v databázi
✅ Update = SQL insert (2 minuty)
✅ Levnější ($20-40/měsíc místo $50-80)
✅ Lepší kvalita odpovědí (GPT-4 > Gemma 2B)
```

---

## 🔄 RAG PIPELINE

### **Co je RAG?**

**RAG = Retrieval-Augmented Generation**

Model **nedostává všechna data najednou**, ale:
1. **Najde relevantní informace** v databázi (vector search)
2. **Dá je do kontextu** pro LLM
3. **LLM generuje odpověď** na základě těchto dat

### **Workflow při dotazu:**

```
USER: "Který olej pomáhá při nespavosti?"
    ↓
┌─────────────────────────────────────────────┐
│ 1. VECTOR SEARCH (Supabase pgvector)       │
│                                             │
│ - Embed otázku (384-dim vektor)            │
│ - Hledej podobné chunky v databázi         │
│ - Filtr podle tier (free vs premium)       │
│ - Vrať top 5-10 nejrelevantnějších chunků  │
└─────────────────────────────────────────────┘
    ↓
    Retrieved: Levandule (0.85), Meduňka (0.78), ...
    ↓
┌─────────────────────────────────────────────┐
│ 2. BUILD CONTEXT                            │
│                                             │
│ System: "Jsi expert na aromaterapii..."     │
│ Context:                                    │
│   "OLEJ: Levandule                          │
│    PSYCHIKA: Podporuje spánek..."           │
│   "OLEJ: Meduňka                            │
│    PSYCHIKA: Uklidňující..."                │
│ User: "Který olej pomáhá při nespavosti?"   │
└─────────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────────┐
│ 3. LLM INFERENCE (OpenAI GPT-4-mini)        │
│                                             │
│ Dostane:                                    │
│ - System prompt                             │
│ - Retrieved context (5-10 chunků)          │
│ - User query                                │
│ - Conversation history                      │
│                                             │
│ → Generuje odpověď                          │
└─────────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────────┐
│ 4. FORMAT RESPONSE (based on tier)         │
│                                             │
│ IF premium:                                 │
│   → Include recipes (kapky, použití)        │
│ ELSE:                                       │
│   → Show basic info + CTA for premium       │
└─────────────────────────────────────────────┘
    ↓
RESPONSE: "Pro nespavost doporučuji levanduli..."
```

### **Proč RAG?**

| Vlastnost | Fine-tuning | RAG |
|-----------|-------------|-----|
| **Přidání nového oleje** | Re-training (5 hod) | SQL insert (2 min) |
| **Náklady update** | $5-20 | $0 |
| **Kvalita** | Závisí na trainingu | GPT-4 quality |
| **Flexibilita** | Nízká | Vysoká |
| **Aktuálnost dat** | Static | Real-time |

---

## 💾 DATABÁZE A DATA

### **Supabase Schema:**

```sql
-- 1. Knowledge Chunks (RAG data)
CREATE TABLE knowledge_chunks (
  id TEXT PRIMARY KEY,
  type TEXT NOT NULL,                  -- 'essential_oil', 'herb_knowledge'
  entity_type TEXT NOT NULL,           -- 'oil_profile', 'herb'
  content_type TEXT NOT NULL,          -- 'database', 'book', 'voice_transcript'
  tier TEXT NOT NULL,                  -- 'free', 'premium'
  name TEXT NOT NULL,                  -- Název (Levandule, Púpava, ...)
  text TEXT NOT NULL,                  -- Samotný text chunku
  part INT,                            -- Číslo části
  total_parts INT,                     -- Celkový počet částí
  chunk_size INT,                      -- Velikost v znacích
  metadata JSONB,                      -- Extra metadata
  embedding VECTOR(384),               -- Vector embedding (pgvector)
  created_at TIMESTAMP DEFAULT NOW()
);

-- Indexy pro rychlé vyhledávání
CREATE INDEX idx_type ON knowledge_chunks(type);
CREATE INDEX idx_tier ON knowledge_chunks(tier);
CREATE INDEX idx_entity_type ON knowledge_chunks(entity_type);

-- Vector index pro similarity search
CREATE INDEX ON knowledge_chunks
USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);

-- 2. Vector Search Function
CREATE OR REPLACE FUNCTION match_chunks(
  query_embedding VECTOR(384),
  match_threshold FLOAT,
  match_count INT,
  filter_tier TEXT DEFAULT NULL,
  filter_type TEXT DEFAULT NULL
)
RETURNS TABLE (
  id TEXT,
  type TEXT,
  tier TEXT,
  name TEXT,
  text TEXT,
  similarity FLOAT
)
LANGUAGE plpgsql
AS $$
BEGIN
  RETURN QUERY
  SELECT
    knowledge_chunks.id,
    knowledge_chunks.type,
    knowledge_chunks.tier,
    knowledge_chunks.name,
    knowledge_chunks.text,
    1 - (knowledge_chunks.embedding <=> query_embedding) AS similarity
  FROM knowledge_chunks
  WHERE
    (filter_tier IS NULL OR knowledge_chunks.tier = filter_tier)
    AND (filter_type IS NULL OR knowledge_chunks.type = filter_type)
    AND 1 - (knowledge_chunks.embedding <=> query_embedding) > match_threshold
  ORDER BY knowledge_chunks.embedding <=> query_embedding
  LIMIT match_count;
END;
$$;

-- 3. Users
CREATE TABLE users (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  email TEXT UNIQUE,
  tier TEXT DEFAULT 'free',            -- 'free', 'premium'
  stripe_customer_id TEXT,
  created_at TIMESTAMP DEFAULT NOW()
);

-- 4. Conversations
CREATE TABLE conversations (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID REFERENCES users(id),
  session_id TEXT,
  messages JSONB,
  created_at TIMESTAMP DEFAULT NOW()
);
```

### **Aktuální data v databázi:**

```
📊 STATISTIKY:
  • Celkem chunků: 3,505
  • Essential oils (free): 30 chunků
  • Herb knowledge (premium): 3,475 chunků
  • Embedding model: paraphrase-multilingual-MiniLM-L12-v2
  • Vector dimenze: 384
  • Průměrná velikost chunku: ~1,050 znaků
```

### **Rozdělení podle typu:**

| Type | Count | Tier | Popis |
|------|-------|------|-------|
| `essential_oil` | 30 | free | Profily 30 esenciálních olejů |
| `herb_knowledge` | 3,475 | premium | Knihy o bylinkách + voice transkripty |

### **Chunking strategie:**

```python
CONFIG = {
    "chunk_size": 1200,         # Optimalizováno pro GPT-4-mini
    "overlap": 200,             # 17% překryv
    "small_chunk_max": 1500     # Malé texty ponechat celé
}
```

**Důvod 1,200 znaků:**
- Kompromis mezi kvalitou a cenou
- GPT-4-mini má dostatečný kontext
- $0.14/měsíc rozdíl vs 1,000 znaků (+17%)
- Výrazně lepší kvalita odpovědí

---

## 🔒 SECURITY

### **MVP Security (implementováno):**

#### **1. Rate Limiting (Upstash Redis)**
```
Free tier:  10 zpráv/min, 50/den
Premium:    50 zpráv/min, 500/den
```

#### **2. Input Validation**
```typescript
- Max 500 znaků
- XSS/spam protection
- Allowed characters only
```

#### **3. Cost Tracking**
```sql
-- Supabase tracking
CREATE TABLE usage_tracking (
  id UUID PRIMARY KEY,
  user_id UUID,
  session_id TEXT,
  tokens_used INT,
  cost_estimate DECIMAL(10, 6),
  timestamp TIMESTAMP DEFAULT NOW()
);
```

#### **4. Tier Filtering**
```python
# Free users → only tier='free' chunks (30 oils)
# Premium users → all chunks (3,505)
```

### **Plánované (před launchem):**

5. ✅ **CAPTCHA** (Google reCAPTCHA v3)
6. ✅ **IP Blacklisting** (auto-ban po 5 violations)
7. ✅ **Email Alerts** (warning $10/day, critical $50/day)

**Náklady security:** $0-5/měsíc

---

## 💰 NÁKLADY A REVENUE

### **Měsíční náklady (aktuální architektura):**

| Komponenta | Cena | Poznámka |
|-----------|------|----------|
| **OpenAI GPT-4-mini** | $20-40 | Závisí na traffic |
| **Supabase Pro** | $25 | pgvector + auth |
| **Vercel Pro** | $20 | Serverless backend |
| **Upstash Redis** | $0-5 | Rate limiting |
| **Domain + SSL** | $2 | Cloudflare |
| **TOTAL** | **$67-92/měsíc** | (~1,600-2,200 Kč) |

**Úspora vs původní plán:** $28-38/měsíc (fine-tuning byl $95-130)

### **Náklady při škálování:**

| Users | Konverzací/měsíc | Náklady | Cena/user |
|-------|-----------------|---------|-----------|
| 100 | 500 | $67 | $0.67 |
| 500 | 2,500 | $90 | $0.18 |
| 1,000 | 5,000 | $120 | $0.12 |
| 5,000 | 25,000 | $200 | $0.04 |

### **Revenue projekce:**

#### **Konzervativní (5% conversion):**

| Fáze | Free | Premium | MRR | Profit |
|------|------|---------|-----|--------|
| M 1-3 | 100 | 5 | 1,495 Kč | -505 Kč |
| M 4-6 | 300 | 15 | 4,485 Kč | +2,485 Kč |
| M 7-12 | 500 | 25 | 7,475 Kč | +5,475 Kč |
| ROK 2 | 1,000 | 50 | 14,950 Kč | +12,950 Kč |

**Break-even:** Měsíc 2-3 (8-10 premium users)

---

## ✅ AKTUÁLNÍ STAV

### **Implementováno:**

#### **1. RAG Pipeline ✅**
```
✅ Parsing script (Excel + Word → JSON)
✅ Chunking script (1,200 znaků, 200 overlap)
✅ Embeddings script (384-dim vectors)
✅ Label fixing (essential_oil, herb_knowledge)
✅ Supabase upload (3,505 chunků)
✅ Vector search testing
```

#### **2. Database ✅**
```
✅ Supabase pgvector setup
✅ knowledge_chunks table
✅ match_chunks() RPC function
✅ Tier filtering (free/premium)
✅ Type filtering (essential_oil/herb_knowledge)
```

#### **3. Testování ✅**
```
✅ Vector similarity search funguje
✅ Tier filtering funguje
✅ Type filtering funguje
✅ Statistiky databáze ověřeny
```

### **Problémy identifikované:**

#### **❌ Problém: Relevance výsledků**

**Popis:**
- Dotaz: "Jak použít levanduli na spaní?"
- Očekávaný výsledek: Levandule #1
- Skutečný výsledek: Levandule #9/30 (similarity 0.333)

**Důvod:**
- Levandule má 970 znaků textu s 15+ kategoriemi
- Info o spaní je pouze ~50 znaků (5% textu)
- Embedding reprezentuje průměr všech témat
- "Spaní" má malou váhu v celkovém vektoru

**Možná řešení (k diskuzi):**

1. **Metadata tags + Hybrid search**
   - Přidat tags: ["spaní", "nespavost", "relaxace", ...]
   - Re-rank: vector similarity + tag matching
   - Čas: 2-4 hodiny (30 olejů)

2. **Re-chunking (menší chunky)**
   - Rozdělit podle kategorií (psychika, kůže, ...)
   - Více chunků = vyšší náklady
   - Ztráta celkového kontextu

3. **Zvýšit match_count**
   - Z 5 na 10 výsledků
   - Levandule by se zobrazila
   - +100% input tokens náklady

4. **Kombinace 1+3 (doporučeno)**
   - Metadata tags + 10 kandidátů
   - Re-rank a vrátit top 5

---

## ❓ OTEVŘENÉ OTÁZKY

### **Pro lektora na diskuzi:**

#### **1. RAG vs Fine-tuning rozhodnutí**
```
Q: Je RAG + GPT-4-mini správná cesta?
   Nebo by měl Fleurdin fine-tunovat vlastní model?

Pros RAG:
  ✅ Levnější ($67 vs $95/měsíc)
  ✅ Jednodušší update (SQL insert)
  ✅ GPT-4 kvalita
  ✅ Žádný training

Cons RAG:
  ❌ Závislost na OpenAI
  ❌ Problémy s relevancí (viz výše)
```

#### **2. Řešení relevance problému**
```
Q: Která z variant řešit nízkou relevanci?
   A) Metadata tags
   B) Re-chunking
   C) Zvýšit match_count
   D) Hybrid (A+C)
```

#### **3. Model choice**
```
Q: GPT-4-mini nebo GPT-4o-nano?

GPT-4-mini:
  • $0.150/1M input tokens
  • Velmi dobrá kvalita
  • Standard pro RAG

GPT-4o-nano:
  • $0.075/1M input tokens (50% levnější!)
  • Nový model (12/2024)
  • Méně testovaný
```

#### **4. Škálování strategie**
```
Q: Jak připravit na růst?

Aktuálně:
  • 3,505 chunků (30 olejů + bylinky)
  • Supabase Free tier

Budoucnost:
  • 300+ olejů?
  • Více bylin?
  • Vlastní hlasové nahrávky?

→ Bude potřeba upgrade Supabase?
→ Očekávaná velikost databáze?
```

#### **5. Security prioritization**
```
Q: Co implementovat před launchem?

Must-have:
  ✅ Rate limiting
  ✅ Input validation
  ✅ Cost tracking

Nice-to-have:
  ⏳ CAPTCHA
  ⏳ IP blacklisting
  ⏳ Email alerts

→ Je free tier bez CAPTCHA bezpečný?
```

---

## 📚 TECH STACK SUMMARY

### **Aktuální implementace:**

| Komponenta | Technologie | Status |
|-----------|-------------|--------|
| **LLM** | OpenAI GPT-4-mini | ✅ Rozhodnuto |
| **RAG Framework** | LangChain | 🔄 Bude implementováno |
| **Vector DB** | Supabase pgvector | ✅ Setup hotovo |
| **Embeddings** | sentence-transformers | ✅ Implementováno |
| **Backend** | Vercel Next.js | 🔄 TODO |
| **Frontend** | WIX Widget | 🔄 TODO |
| **Auth** | Supabase Auth | 🔄 TODO |
| **Payments** | Stripe | 🔄 TODO |
| **Security** | Upstash Redis | 🔄 TODO |

### **Data pipeline:**

```
Excel/Word → parsing_script.py → parsed_data.json
                ↓
         chunking_script.py → chunked_data.json
                ↓
      embeddings_script.py → chunked_data_with_embeddings.json
                ↓
       fix_labels_script.py → chunked_data_FIXED.json
                ↓
      upload_to_supabase.py → Supabase (3,505 chunků) ✅
```

---

## 🎯 NEXT STEPS

### **Immediate (1-2 týdny):**

1. **Vyřešit relevance problém**
   - Rozhodnout: Tags vs Re-chunking vs Hybrid
   - Implementovat zvolené řešení
   - Re-test vector search

2. **Backend API implementace**
   - Vercel Next.js projekt
   - `/api/chat` endpoint
   - LangChain RAG pipeline
   - OpenAI GPT-4-mini integrace

3. **Frontend Widget**
   - WIX embedded chatbot
   - Session management
   - Basic UI/UX

### **Short-term (3-4 týdny):**

4. **Auth & Payments**
   - Supabase Auth setup
   - Stripe integration
   - Tier management

5. **Security**
   - Rate limiting (Upstash)
   - Input validation
   - Cost tracking dashboard

6. **Testing**
   - End-to-end test
   - Load test
   - Security test

### **Launch (5-6 týdnů):**

7. **Beta test** (10 users)
8. **Marketing** (SEO, social)
9. **Monitoring** (analytics, costs)
10. **🚀 Launch!**

---

## 📞 KONTAKT & DOKUMENTACE

**Projekt:** Fleurdin AI
**Web:** www.fleurdin.cz
**Dataset:** 3,505 chunků (30 olejů + 3,475 bylinky)
**Database:** Supabase pgvector
**Model:** OpenAI GPT-4-mini

**Dokumentace:**
- Architecture (tento soubor)
- Security: `/1-Architektura/SECURITY.md`
- RAG Status Report: `/4-RAG_Pipeline/RAG_PIPELINE_STATUS_REPORT.txt`
- Chunking Analysis: `/4-RAG_Pipeline/CHUNKING_STRATEGY_ANALYSIS.md`

---

**Vytvořeno s ❤️ pro Fleurdin**
**Poslední update:** 2025-12-02
**Status:** RAG Pipeline hotová, Backend TODO
