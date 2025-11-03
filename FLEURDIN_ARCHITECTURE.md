# 🌿 FLEURDIN AI - KOMPLETNÍ ARCHITEKTURA & PLÁN

**Vytvořeno:** 2025-01-30
**Verze:** 1.0
**Účel:** Chatbot pro konzultace esenciálních olejů s freemium modelem

---

## 📋 OBSAH

1. [Přehled projektu](#přehled-projektu)
2. [Business model](#business-model)
3. [Technická architektura](#technická-architektura)
4. [RAG workflow](#rag-workflow)
5. [Tier systém (Free vs Premium)](#tier-systém)
6. [Postupné přidávání olejů](#postupné-přidávání-olejů)
7. [Implementační stack](#implementační-stack)
8. [Security & Cost Protection](#security--cost-protection) ⭐ NOVÉ
9. [Náklady a revenue](#náklady-a-revenue)
10. [Fáze vývoje](#fáze-vývoje)
11. [Next steps](#next-steps)

---

## 🎯 PŘEHLED PROJEKTU

### **Co je Fleurdin AI?**

Konverzační AI chatbot pro **www.fleurdin.cz** (WIX), který poskytuje expertní konzultace o esenciálních olejích.

### **Dvě verze:**

| Funkce | FREE (bez registrace) | PREMIUM (platba) |
|---|---|---|
| **Konverzační AI** | ✅ Pamatuje si kontext | ✅ Pamatuje si kontext |
| **Počet olejů** | 20-30 olejů | 300 olejů |
| **Doporučení olejů** | ✅ | ✅ |
| **Recepty (kapky, použití)** | ❌ | ✅ |
| **Cena** | Zdarma | 299 Kč/měsíc |

### **Příklad konverzace:**

```
USER: "Nemůžu spát, jaké bys mi doporučil oleje?"

BOT (ZDARMA):
"Pro lepší spánek doporučuji levanduli nebo meduňku.
Levandule má uklidňující účinky na nervový systém..."

USER: "A jak to mám použít?"

BOT (ZDARMA):
"💎 Pro detailní recepty s počtem kapek a způsobem
užití si prosím vytvořte účet v placené verzi."

---

BOT (PREMIUM):
"Pro lepší spánek doporučuji:

**Recept:**
- **Levandule**: 3 kapky
- **Meduňka**: 2 kapky
- **Bergamot**: 1 kapka

**Použití:** Přidej do difuzéru 30 minut před spaním,
nebo namíchej s mandlovým olejem (10ml) a potři záda
před uložením."
```

---

## 💰 BUSINESS MODEL

### **Freemium strategie:**

**FREE tier:**
- Neomezený přístup k chatbotu
- 20-30 olejů
- Doporučení bez receptů
- Lead generation pro premium

**PREMIUM tier:**
- 299 Kč/měsíc (cca $13/měsíc)
- 300 esenciálních olejů
- Detailní recepty (kapky, použití)
- Ukládání konverzací
- Personalizované doporučení

### **Revenue projection:**

| Měsíc | Free users | Premium users | MRR (Kč) | MRR ($) |
|---|---|---|---|---|
| 1-3 (Launch) | 100 | 5 | 1,495 | $65 |
| 4-6 | 300 | 20 | 5,980 | $260 |
| 7-12 | 500 | 50 | 14,950 | $650 |
| ROK 2 | 1,000 | 100 | 29,900 | $1,300 |
| ROK 3 | 2,000 | 200 | 59,800 | $2,600 |

**Conversion rate:** 5-10% (free → premium)

---

## 🏗️ TECHNICKÁ ARCHITEKTURA

### **High-level diagram:**

```
┌─────────────────────────────────────────────────────┐
│               WIX Website (fleurdin.cz)             │
│            Embedded Chatbot Widget                  │
└──────────────────────┬──────────────────────────────┘
                       ↓
┌─────────────────────────────────────────────────────┐
│           Vercel (Next.js Backend)                  │
│                                                     │
│  POST /api/chat                                     │
│  - Check user tier (free vs premium)               │
│  - Load conversation history (LangChain Memory)    │
│  - Execute RAG pipeline                             │
│  - Format response based on tier                    │
│  - Save conversation                                │
└──────────────────────┬──────────────────────────────┘
                       ↓
         ┌─────────────┴─────────────┐
         ↓                           ↓
┌────────────────────┐    ┌──────────────────────────┐
│   SUPABASE         │    │   HUGGINGFACE            │
│                    │    │                          │
│ - pgvector (RAG)   │    │ - Fine-tuned Gemma 2B    │
│ - Users            │    │ - Inference Endpoint     │
│ - Conversations    │    │ - Auto-scaling           │
│ - Essential oils   │    │                          │
│ - Recipes          │    │                          │
│ - Auth             │    │                          │
└────────────────────┘    └──────────────────────────┘
```

### **Komponenty:**

1. **Frontend:** WIX + Embedded Chat Widget
2. **Backend:** Vercel Next.js + Python FastAPI (pro LangChain)
3. **Vector DB:** Supabase pgvector (RAG data)
4. **LLM:** Fine-tuned Gemma 2B (HuggingFace Inference Endpoint)
5. **Auth:** Supabase Auth
6. **Payments:** Stripe
7. **Orchestration:** LangChain (RAG + Memory)

---

## 🔄 RAG WORKFLOW (KLÍČOVÁ ČÁST!)

### **Co je RAG?**

**RAG = Retrieval-Augmented Generation**

Model **NETAHÁ znalosti z paměti**, ale **dostává relevantní data při každém dotazu**.

### **Dvě komponenty systému:**

```
┌──────────────────────────────────────────────────┐
│      1. FINE-TUNED MODEL (Gemma 2B)              │
│                                                  │
│  Co umí:                                         │
│  ✅ Rozumí aromaterapii (terminologie)          │
│  ✅ Mluví stylem experta                        │
│  ✅ Generuje přirozené odpovědi v češtině       │
│                                                  │
│  Co NEUMÍ (a nemusí):                            │
│  ❌ Pamatovat si všech 300 olejů nazpaměť       │
│                                                  │
│  UPDATE: Jen když chceš změnit STYL/CHOVÁNÍ     │
│  (např. 1x za 6-12 měsíců, nebo nikdy)          │
└──────────────────────────────────────────────────┘

                    ↓ používá ↓

┌──────────────────────────────────────────────────┐
│   2. VECTOR DATABASE (Supabase pgvector)         │
│                                                  │
│  Co obsahuje:                                    │
│  📊 300 olejů (postupně přidáváš)               │
│  📊 Účinky na tělo, psychiku                    │
│  📊 Recepty (kapky, použití)                    │
│  📊 Vector embeddings pro search                │
│                                                  │
│  UPDATE: Kdykoliv přidáš nový olej (2 min)      │
└──────────────────────────────────────────────────┘
```

### **Workflow při dotazu:**

```
USER: "Který olej pomáhá při nespavosti?"
    ↓
┌─────────────────────────────────────────────┐
│ 1. RETRIEVAL (Vector Search)                │
│                                             │
│ - Embed otázku do vektoru                   │
│ - Hledej v Supabase pgvector                │
│ - Filtr podle tier (free vs premium)        │
│ - Vrať top 3-5 nejrelevantnějších olejů     │
└─────────────────────────────────────────────┘
    ↓
    Retrieved: Levandule, Meduňka, Bergamot
    ↓
┌─────────────────────────────────────────────┐
│ 2. AUGMENTATION (Build Context)             │
│                                             │
│ System: "Jsi expert na aromaterapii..."     │
│ Context:                                    │
│   "Levandule: PSYCHIKA: Uklidňující..."     │
│   "Meduňka: PSYCHIKA: Relaxační..."         │
│ User: "Který olej pomáhá při nespavosti?"   │
└─────────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────────┐
│ 3. GENERATION (LLM Response)                │
│                                             │
│ Fine-tuned model dostane:                   │
│ - System prompt                             │
│ - Context (3-5 olejů z databáze)            │
│ - User otázku                               │
│ - Conversation history (LangChain Memory)   │
│                                             │
│ → Generuje odpověď                          │
└─────────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────────┐
│ 4. FORMAT (Based on Tier)                   │
│                                             │
│ IF premium:                                 │
│   → Add recipes (kapky, použití)            │
│ ELSE:                                       │
│   → Show oils only + CTA for premium        │
└─────────────────────────────────────────────┘
    ↓
RESPONSE: "Pro nespavost doporučuji levanduli..."
```

### **Proč RAG?**

| Vlastnost | Bez RAG | S RAG |
|---|---|---|
| **Přidání nového oleje** | Re-training (5 hod) | SQL insert (2 min) |
| **Náklady update** | $5-20 | $0 |
| **Flexibilita** | Nízká | Vysoká |
| **Aktuálnost dat** | Static (frozen) | Real-time |
| **Škálovatelnost** | Omezená | Unlimited |

---

## 🔐 TIER SYSTÉM (Free vs Premium)

### **Jak funguje filtrování:**

**Databáze:**
```sql
CREATE TABLE essential_oils (
  id BIGSERIAL PRIMARY KEY,
  name TEXT NOT NULL,
  effects_body TEXT,
  effects_psyche TEXT,
  tier TEXT DEFAULT 'free',  -- 'free' nebo 'premium'
  embedding VECTOR(384)
);
```

**Vector Search s filtrem:**
```python
# FREE USER
retriever = vectorstore.as_retriever(
    search_kwargs={
        "k": 3,
        "user_tier": "free"  # ← Hledá jen tier='free' (20 olejů)
    }
)

# PREMIUM USER
retriever = vectorstore.as_retriever(
    search_kwargs={
        "k": 5,
        "user_tier": "premium"  # ← Hledá všechny oleje (300)
    }
)
```

**Response formatting:**
```python
def format_response(result, user_tier):
    answer = result["result"]
    sources = result["source_documents"]

    if user_tier == "premium":
        # Přidej recepty
        recipes = get_recipes_for_oils(sources)
        return f"{answer}\n\n**Recept:**\n{recipes}"

    else:  # free
        return f"{answer}\n\n💎 Pro detailní recepty zkuste premium verzi."
```

### **Co vidí každý tier:**

| Feature | Free | Premium |
|---|---|---|
| Vector search | 20 olejů (tier='free') | 300 olejů (všechny) |
| Konverzační AI | ✅ | ✅ |
| Memory (paměť) | ✅ | ✅ |
| Recepty | ❌ | ✅ |
| Uložené konverzace | ❌ | ✅ |

---

## ➕ POSTUPNÉ PŘIDÁVÁNÍ OLEJŮ

### **KLÍČOVÁ VÝHODA RAG:**

**Nemusíš re-trainovat model při každém novém oleji!**

### **Workflow: Přidání nového oleje**

```python
# add_new_oil.py

from sentence_transformers import SentenceTransformer
from supabase import create_client

# Setup
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
embedder = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')

# Nový olej
new_oil = {
    "name": "Ylang-Ylang",
    "effects_body": "OBECNÉ: Antispasmodický, Afrodisiakum. KŮŽE: Vyvažuje tvorbu kožního mazu.",
    "effects_psyche": "PSYCHIKA: Uklidňující, antidepresivní, afrodisiakální.",
    "tier": "premium"  # nebo "free"
}

# 1. Vygeneruj embedding
text = f"{new_oil['name']} {new_oil['effects_body']} {new_oil['effects_psyche']}"
embedding = embedder.encode(text).tolist()

# 2. Ulož do databáze
supabase.table('essential_oils').insert({
    **new_oil,
    'embedding': embedding
}).execute()

# 3. Přidej recepty (pro premium)
recipes = [
    {
        "oil_id": 301,  # ID nového oleje
        "condition": "stres",
        "drops": 2,
        "usage_instructions": "Přidej do difuzéru...",
        "tier": "premium"
    }
]

supabase.table('recipes').insert(recipes).execute()

print("✅ Ylang-Ylang přidán! Model ho hned vidí.")
```

**⏱️ Čas:** 2 minuty
**💰 Cena:** $0
**🔄 Re-training:** NEPOTŘEBA

### **Časová osa (První rok):**

```
MĚSÍC 1 (MVP):
✅ Fine-tune Gemma 2B na 30 olejích
✅ Setup RAG s 30 oleji v databázi
✅ Launch free (20 olejů) + premium (30 olejů)

MĚSÍC 2-6:
✅ Přidáváš 50 nových olejů (po 10/měsíc)
✅ Každý olej = 2 minuty (SQL insert)
❌ ŽÁDNÝ re-training

MĚSÍC 7-12:
✅ Přidáváš dalších 100 olejů
✅ Celkem: 180 olejů
❌ STÁLE žádný re-training

ROK 2:
✅ Databáze: 300 olejů
🔄 Možná 1x re-training (pro vylepšení stylu)
```

### **Kdy RE-TRAINOVAT model?**

**POUZE když chceš změnit:**

1. **Styl konverzace** (např. více neformální)
2. **Nové dovednosti** (např. recepty pro těhotné)
3. **Vylepšení kvality** odpovědí

**Frekvence:** 1x za 6-12 měsíců (nebo nikdy)

---

## 🛠️ IMPLEMENTAČNÍ STACK

### **LLM & Training:**

| Komponenta | Technologie | Proč |
|---|---|---|
| **Base model** | Google Gemma 2B | Levný, kvalitní, open-source |
| **Fine-tuning** | HuggingFace Transformers | Standard pro LLM training |
| **Dataset** | TomasBo/Fleurdin (2,281 Q&A) | Vlastní data na HuggingFace |
| **Inference** | HuggingFace Inference Endpoints | Auto-scaling, managed |

### **RAG & Orchestration:**

| Komponenta | Technologie | Proč |
|---|---|---|
| **Vector DB** | Supabase pgvector | PostgreSQL + embeddings |
| **Embeddings** | sentence-transformers (multilingual) | Česká podpora |
| **RAG framework** | LangChain | Orchestrace RAG + Memory |
| **Memory** | ConversationBufferMemory | Pamatuje kontext |

### **Backend & Frontend:**

| Komponenta | Technologie | Proč |
|---|---|---|
| **Backend** | Vercel Next.js + Python FastAPI | Serverless, škálovatelné |
| **Frontend** | WIX + Custom Widget | Existující web |
| **Auth** | Supabase Auth | Email/password, OAuth |
| **Payments** | Stripe | Standard pro subscriptions |
| **Hosting** | Vercel (BE) + Supabase (DB) | Managed, auto-scale |

### **Database Schema (Supabase):**

```sql
-- 1. Essential Oils (Vector Store)
CREATE TABLE essential_oils (
  id BIGSERIAL PRIMARY KEY,
  name TEXT NOT NULL,
  effects_body TEXT,
  effects_psyche TEXT,
  tier TEXT DEFAULT 'free',
  embedding VECTOR(384)
);

-- 2. Recipes
CREATE TABLE recipes (
  id BIGSERIAL PRIMARY KEY,
  oil_id BIGINT REFERENCES essential_oils(id),
  condition TEXT,
  drops INTEGER,
  usage_instructions TEXT,
  tier TEXT DEFAULT 'premium'
);

-- 3. Users
CREATE TABLE users (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  email TEXT UNIQUE,
  tier TEXT DEFAULT 'free',
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

-- 5. Vector Search Function
CREATE OR REPLACE FUNCTION match_oils(
  query_embedding VECTOR(384),
  match_threshold FLOAT,
  match_count INT,
  user_tier TEXT DEFAULT 'free'
)
RETURNS TABLE (
  id BIGINT,
  name TEXT,
  effects_body TEXT,
  effects_psyche TEXT,
  similarity FLOAT
)
LANGUAGE SQL STABLE
AS $$
  SELECT
    id, name, effects_body, effects_psyche,
    1 - (embedding <=> query_embedding) AS similarity
  FROM essential_oils
  WHERE
    1 - (embedding <=> query_embedding) > match_threshold
    AND (tier = 'free' OR user_tier = 'premium')
  ORDER BY similarity DESC
  LIMIT match_count;
$$;
```

---

## 🔒 SECURITY & COST PROTECTION

### **Proč je to kritické?**

**Reálné riziko:** Bot attack může zvýšit náklady z $80 → $500+/měsíc během jednoho dne.

**📖 Kompletní dokumentace:** [SECURITY.md](./SECURITY.md)

---

### **MVP SECURITY (MUST-HAVE)**

#### **1. Rate Limiting** ⭐ PRIORITA #1

**Konfigurace:**
- **Free tier:** 10 zpráv/min, 50/den
- **Premium tier:** 50 zpráv/min, 500/den

**Tech:** Upstash Redis + @upstash/ratelimit

**Náklady:** $0-5/měsíc

---

#### **2. Input Validation** ⭐ PRIORITA #2

**Ochrana před:**
- XSS (Cross-Site Scripting)
- Spam
- Dlouhé inputy (vysoké náklady)

**Limity:**
- Max 500 znaků per zpráva
- Pouze povolené znaky (CS + common symbols)
- Blocked patterns (URLs, scripts)

**Náklady:** $0 (jen kód)

---

#### **3. HuggingFace Auto-Pause** ⭐ PRIORITA #3

**Konfigurace:**
```json
{
  "scaling": {
    "minReplicas": 0,        // Může jít na 0 (žádné náklady)
    "maxReplicas": 2         // Cost cap (max 2 instance)
  },
  "auto_pause": {
    "enabled": true,
    "idle_timeout": 300      // 5 minut bez requestů → pause
  }
}
```

**Savings:** $432/měsíc → $50-80/měsíc (83% úspora!)

---

#### **4. Cost Tracking** ⭐ PRIORITA #4

**Database:**
```sql
CREATE TABLE usage_tracking (
  id UUID PRIMARY KEY,
  user_id UUID,
  session_id TEXT,
  timestamp TIMESTAMP,
  tokens_used INTEGER,
  cost_estimate DECIMAL(10, 6)
);
```

**Dashboard:** Real-time monitoring denních/měsíčních nákladů

**Náklady:** $0 (included in Supabase)

---

### **LAUNCH SECURITY (SHOULD-HAVE)**

#### **5. CAPTCHA (Pro Free Tier)**

**Kdy:** Před prvním použitím + po 10 zprávách (anonymous users)

**Tech:** Google reCAPTCHA v3 (invisible)

**Náklady:** $0 (1M assessments/měsíc zdarma)

---

#### **6. IP Blacklisting**

**Auto-ban:** Po 5 rate limit violations → ban na 24h

**Tech:** Upstash Redis

**Náklady:** $0 (included)

---

#### **7. Email Alerts**

**Thresholds:**
- Warning: $10/den (email alert)
- Critical: $50/den (auto-shutdown API + email)

**Tech:** Resend + Vercel Cron

**Náklady:** $0 (100 emails/měsíc free)

---

### **Security Cost Summary:**

| Feature | Cost/měsíc | Priority |
|---|---|---|
| Rate Limiting | $0-5 | ⭐⭐⭐ |
| Input Validation | $0 | ⭐⭐⭐ |
| Auto-pause | $0 (savings) | ⭐⭐⭐ |
| Cost Tracking | $0 | ⭐⭐⭐ |
| CAPTCHA | $0 | ⭐⭐ |
| IP Blacklisting | $0 | ⭐⭐ |
| Email Alerts | $0 | ⭐⭐ |
| **TOTAL** | **$0-5/měsíc** | |

**ROI:** Saves $300-500/měsíc při attack

---

## 💰 NÁKLADY A REVENUE

### **Měsíční náklady (Infrastructure):**

| Komponenta | Cena | Poznámka |
|---|---|---|
| **HuggingFace Inference** | $50-80 | Auto-scale (T4 GPU) |
| **Supabase** | $25 | Pro tier (pgvector + auth) |
| **Vercel** | $20 | Pro tier (serverless) |
| **Security** | $0-5 | Upstash Redis (rate limiting) |
| **Stripe** | 1.4% + 6 Kč | Per transakce |
| **Domain + SSL** | $2 | Cloudflare |
| **TOTAL** | **$97-132/měsíc** | (~2,300-3,100 Kč) |

### **Náklady při škálování:**

| Users | Konverzací/měsíc | Infra costs | Cost per user |
|---|---|---|---|
| 100 | 500 | $97 | $0.97 |
| 500 | 2,500 | $120 | $0.24 |
| 1,000 | 5,000 | $150 | $0.15 |
| 5,000 | 25,000 | $250 | $0.05 |

### **Revenue projekce:**

#### **Konzervativní scénář (5% conversion):**

| Měsíc | Free users | Premium (5%) | MRR (Kč) | Costs (Kč) | Profit |
|---|---|---|---|---|---|
| 1-3 | 100 | 5 | 1,495 | 2,500 | **-1,005** |
| 4-6 | 300 | 15 | 4,485 | 2,700 | **+1,785** |
| 7-12 | 500 | 25 | 7,475 | 3,000 | **+4,475** |
| ROK 2 | 1,000 | 50 | 14,950 | 3,500 | **+11,450** |
| ROK 3 | 2,000 | 100 | 29,900 | 5,000 | **+24,900** |

#### **Optimistický scénář (10% conversion):**

| Měsíc | Free users | Premium (10%) | MRR (Kč) | Costs (Kč) | Profit |
|---|---|---|---|---|---|
| 1-3 | 100 | 10 | 2,990 | 2,500 | **+490** |
| 4-6 | 300 | 30 | 8,970 | 2,700 | **+6,270** |
| 7-12 | 500 | 50 | 14,950 | 3,000 | **+11,950** |
| ROK 2 | 1,000 | 100 | 29,900 | 3,500 | **+26,400** |
| ROK 3 | 2,000 | 200 | 59,800 | 5,000 | **+54,800** |

### **Break-even:**

- **Konzervativní:** Měsíc 4-6 (15 premium users)
- **Optimistický:** Měsíc 1-3 (10 premium users)

### **ROI Timeline:**

```
Initial investment: $500-1,000 (fine-tuning + setup)
Break-even: 3-6 měsíců
ROI 100%: 9-12 měsíců
ROI 300%: ROK 2
```

---

## 🚀 FÁZE VÝVOJE

### **FÁZE 1: MVP (Měsíc 1-2)**

**Cíl:** Launch funkční chatbot s 30 oleji

**Tasks:**
- [ ] Fine-tune Gemma 2B na datasetu (2,281 Q&A)
- [ ] Setup Supabase (schema, pgvector, auth)
- [ ] Implementace LangChain RAG pipeline
- [ ] Vercel Next.js API endpoints
- [ ] WIX chat widget integration
- [ ] Stripe platební flow
- [ ] Testing & QA

**Deliverables:**
- ✅ Free verze (20 olejů, bez receptů)
- ✅ Premium verze (30 olejů, s recepty)
- ✅ Registrace + platba

**Budget:** $500-1,000

---

### **FÁZE 2: Growth (Měsíc 3-6)**

**Cíl:** Škálování na 100 olejů + marketing

**Tasks:**
- [ ] Přidat 70 nových olejů (po 20/měsíc)
- [ ] Analytics (Mixpanel/PostHog)
- [ ] SEO optimalizace
- [ ] Email marketing (ConvertKit)
- [ ] A/B testing (pricing, messaging)
- [ ] Customer feedback loop

**Deliverables:**
- ✅ 100 olejů v databázi
- ✅ 100+ active users
- ✅ 10-20 premium subscribers

**Budget:** $300/měsíc (marketing + infra)

---

### **FÁZE 3: Scale (Měsíc 7-12)**

**Cíl:** 300 olejů + partnering

**Tasks:**
- [ ] Dokončit 300 olejů
- [ ] Multi-tenant architektura (pro partnery)
- [ ] API pro třetí strany
- [ ] Mobile app (optional)
- [ ] Expansion: bylinky, přírodní léky

**Deliverables:**
- ✅ 300 olejů
- ✅ 500+ users
- ✅ 50+ premium subscribers
- ✅ Partner integrace (1-2 e-shopy)

**Budget:** $500/měsíc

---

## ✅ NEXT STEPS (Konkrétní akce)

### **Týden 1-2:**
1. [ ] Fine-tuning Gemma 2B
   - Použij dataset: `TomasBo/Fleurdin`
   - Model: `google/gemma-2-2b-it`
   - Platform: Google Colab nebo HuggingFace AutoTrain

2. [ ] Setup Supabase
   - Vytvoř projekt
   - Spusť SQL schema (pgvector extension)
   - Upload 30 olejů + embeddings

3. [ ] Test RAG pipeline lokálně
   - LangChain + local Gemma (Ollama)
   - Verifikuj kvalitu odpovědí

### **Týden 3-4:**
4. [ ] Deploy fine-tuned model
   - HuggingFace Inference Endpoint
   - Test auto-scaling

5. [ ] Backend API
   - Vercel Next.js projekt
   - `/api/chat` endpoint
   - Integrace LangChain + Supabase

6. [ ] Frontend widget
   - WIX embedded chatbot
   - Session management
   - Auth flow (Supabase)

### **Týden 5-6:**
7. [ ] Stripe integrace
   - Subscription checkout
   - Webhook handling
   - Tier management

8. [ ] Testing
   - 10 test questions
   - Free vs Premium flow
   - Edge cases

9. [ ] Launch 🚀

---

## 📚 DŮLEŽITÉ LINKY

### **Dataset & Model:**
- Dataset: https://huggingface.co/datasets/TomasBo/Fleurdin
- Base model: https://huggingface.co/google/gemma-2-2b-it
- Fine-tuned model: `TomasBo/fleurdin-gemma-2b` (po trainingu)

### **Tools & Platforms:**
- Supabase: https://supabase.com
- HuggingFace: https://huggingface.co
- Vercel: https://vercel.com
- Stripe: https://stripe.com
- LangChain docs: https://python.langchain.com

### **Tutorials:**
- Fine-tuning Gemma: https://huggingface.co/blog/gemma-peft
- LangChain RAG: https://python.langchain.com/docs/use_cases/question_answering/
- Supabase pgvector: https://supabase.com/docs/guides/database/extensions/pgvector

---

## 🎓 KLÍČOVÉ KONCEPTY (Pro budoucí referenci)

### **RAG vs Fine-tuning:**

| Aspekt | Fine-tuning | RAG |
|---|---|---|
| **Update dat** | Re-training (hodiny) | SQL insert (minuty) |
| **Náklady** | $5-20 per update | $0 per update |
| **Flexibilita** | Nízká | Vysoká |
| **Use case** | Styl, chování | Faktické info |

**ZÁVĚR:** Kombinace obou! Fine-tuning pro styl, RAG pro data.

### **LangChain komponenty:**

- **VectorStore:** Supabase pgvector (embeddings)
- **Retriever:** Vector search (top-k)
- **Memory:** ConversationBufferMemory (kontext)
- **Chain:** ConversationalRetrievalChain (orchestrace)

### **Tier filtering:**

```python
# Free users → tier='free' oils (20)
# Premium users → všechny oleje (300)
```

---

## 📞 KONTAKT & SUPPORT

**Projekt:** Fleurdin AI
**Web:** www.fleurdin.cz
**HuggingFace:** [@TomasBo](https://huggingface.co/TomasBo)
**Dataset:** [Fleurdin](https://huggingface.co/datasets/TomasBo/Fleurdin)

---

**Vytvořeno s ❤️ pro Fleurdin**
**Poslední update:** 2025-01-30
