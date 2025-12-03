# 🌿 FLEURDIN AI - TECHNICAL SUMMARY

**Verze:** 2.0
**Datum:** 2025-12-02
**Status:** RAG Pipeline implementována ✅

---

## 🎯 USE CASE

### **Co řeší:**
AI chatbot pro **www.fleurdin.cz** poskytující expertní konzultace o:
- **Esenciálních olejích** (30 olejů ve free databázi / 300 olejů v premium)
- **Bylinkách** (3,475 chunků z knih a voice transkriptů - opět bude rozdělení na free/premium)
- **Aromaterapii a přírodní medicíně**

### **Příklad použití:**

```
USER: "Nemůžu spát, jaký olej mi pomůže?"

BOT: "Pro lepší spánek doporučuji levanduli. Má uklidňující
účinky na nervový systém a pomáhá při nespavosti."

USER: "A jak to mám použít?"

BOT (PREMIUM):
"Recept:
- Levandule: 3 kapky
- Meduňka: 2 kapky
- Bergamot: 1 kapka

Použití: Přidej do difuzéru 30 minut před spaním."
```

### **Freemium model:**

| Feature | FREE | PREMIUM |
|---------|------|---------|
| Konverzační AI | ✅ | ✅ |
| Esenciální oleje | 30 olejů | 300 olejů |
| Bylinky | ❌ | ✅ 3,475 chunků |
| Recepty (kapky, použití) | ❌ | ✅ |
| Cena | Zdarma | XXX Kč/měsíc |

---

## 🏗️ TECHNICKÁ ARCHITEKTURA

### **High-level diagram:**

```
┌─────────────────────────────────────────┐
│      WIX Website (fleurdin.cz)          │
│         Embedded Chat Widget            │
└──────────────────┬──────────────────────┘
                   ↓ HTTPS
┌──────────────────────────────────────────┐
│   Vercel Next.js API + LangChain         │
│                                          │
│  /api/chat:                              │
│  1. Rate limiting                        │
│  2. User tier check                      │
│  3. Vector search (top 5-10 chunks)      │
│  4. Call OpenAI GPT-4-mini               │
│  5. Format response                      │
└──────────────────┬───────────────────────┘
                   ↓
         ┌─────────┴─────────┐
         ↓                   ↓
┌──────────────────┐  ┌──────────────────┐
│   SUPABASE       │  │   OPENAI         │
│                  │  │                  │
│ • pgvector       │  │ • GPT-4-mini     │
│ • Auth           │  │                  │
│ • 3,505 chunků   │  │                  │
└──────────────────┘  └──────────────────┘
```

### **Tech Stack:**

| Komponenta | Technologie | Status |
|-----------|-------------|--------|
| **LLM** | OpenAI GPT-4-mini | ✅ |
| **Vector DB** | Supabase pgvector | ✅ |
| **Embeddings** | sentence-transformers (384-dim) | ✅ |
| **Backend** | Vercel Next.js | 🔄 TODO |
| **Frontend** | WIX Widget | 🔄 TODO |
| **Auth** | Supabase Auth | 🔄 TODO |
| **Payments** | Stripe | 🔄 TODO |
| **Security** | Upstash Redis (rate limiting) | 🔄 TODO |

### **Databáze (Supabase pgvector):**

```sql
-- Knowledge chunks s vector embeddings
CREATE TABLE knowledge_chunks (
  id TEXT PRIMARY KEY,
  type TEXT NOT NULL,              -- 'essential_oil', 'herb_knowledge'
  tier TEXT NOT NULL,              -- 'free', 'premium'
  name TEXT NOT NULL,              -- Název (Levandule, Púpava)
  text TEXT NOT NULL,              -- Samotný text
  embedding VECTOR(384),           -- Vector pro similarity search
  -- ... další metadata
);

-- Vector similarity search
CREATE INDEX ON knowledge_chunks
USING ivfflat (embedding vector_cosine_ops);
```

**Data v databázi:**
Bude postupně doplňováno o další zdrojová data
```
Aktuálně:
✅ 3,505 chunků celkem
  • 30 essential_oil (free tier)
  • 3,475 herb_knowledge (premium tier)
  • Chunk size: ~1,200 znaků
  • Embedding model: multilingual-MiniLM-L12-v2
```

---

## 🔄 WORKFLOW

### **Request flow:**

```
1. User query → Chat Widget (WIX)
                    ↓
2. POST /api/chat (Vercel)
   • Check rate limit (Upstash Redis)
   • Verify user tier (Supabase Auth)
                    ↓
3. Vector search (Supabase)
   • Embed query → 384-dim vector
   • Match podobné chunky
   • Filter by tier (free/premium)
   • Return top 5-10 chunks
                    ↓
4. Build context
   • System prompt: "Jsi expert na aromaterapii..."
   • Retrieved chunks: "OLEJ: Levandule..."
   • User query
   • Conversation history
                    ↓
5. LLM inference (OpenAI GPT-4-mini)
   • Generate response
                    ↓
6. Format response
   • IF premium → include recipes
   • ELSE → basic info + CTA
                    ↓
7. Save conversation (Supabase)
                    ↓
8. Return response → User
```

---

## 💰 NÁKLADY

| Komponenta | Měsíční cena |
|-----------|--------------|
| OpenAI GPT-4-mini | $20-40 |
| Supabase Pro | $25 |
| Vercel Pro | $20 |
| Upstash Redis | $0-5 |
| **TOTAL** | **$67-92** (~1,600-2,200 Kč) |

**Škálování:**
- 100 users: $67/měsíc ($0.67/user)
- 1,000 users: $120/měsíc ($0.12/user)
- 5,000 users: $200/měsíc ($0.04/user)

---

## ✅ AKTUÁLNÍ STAV

### **Implementováno:**

```
✅ Data pipeline:
  • Parsing (Excel/Word → JSON)
  • Chunking (1,200 znaků, 200 overlap)
  • Embeddings (384-dim vectors)
  • Upload do Supabase (3,505 chunků)

✅ Database:
  • Supabase pgvector setup
  • Vector search funkce
  • Tier filtering

✅ Testing:
  • Vector similarity search testován
  • Tier filtering funguje
```

### **TODO:**

```
🔄 Backend API:
  • Vercel Next.js
  • LangChain integration
  • OpenAI GPT-4-mini API

🔄 Frontend:
  • WIX chat widget
  • Session management

🔄 Auth & Payments:
  • Supabase Auth
  • Stripe integration

🔄 Security:
  • Rate limiting
  • Input validation
  • Cost tracking
```

---

## ⚠️ IDENTIFIKOVANÉ PROBLÉMY

### **Relevance vector search:**

**Problém:**
- Query: "Jak použít levanduli na spaní?"
- Očekávané: Levandule #1
- Skutečné: Levandule #9/30 (similarity 0.333)

**Důvod:**
- Levandule má 970 znaků s 15+ kategoriemi
- Info o spaní je pouze ~5% textu
- Embedding reprezentuje průměr všech témat

**Možná řešení (k diskuzi):**
1. Metadata tags + hybrid search
2. Re-chunking na menší části
3. Zvýšit match_count z 5 na 10
4. Kombinace 1+3

---

## 🎯 NEXT STEPS

### **1-2 týdny:**
1. Vyřešit relevance problém
2. Backend API (Vercel + LangChain)
3. Frontend widget (WIX)

### **3-4 týdny:**
4. Auth & Payments (Supabase + Stripe)
5. Security (rate limiting, validation)
6. Testing (E2E, load, security)

### **5-6 týdnů:**
7. Beta test
8. 🚀 Launch

---

## 📋 OTÁZKY K VYŘEŠENÍ

1. **Relevance problém:** Pokračovat v tunningu RAGu nebo zkusit ElasticSearch? 

2. **Pro RAG:** Který přístup doporučuješ pro vyřešení aktuálních chyb?
   - A) Metadata tags
   - B) Re-chunking
   - C) Zvýšit match_count
   - D) Hybrid

3. **Security:** Co implementovat před launchem? 

---

