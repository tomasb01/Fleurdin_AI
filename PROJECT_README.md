# 🌿 FLEURDIN AI - KOMPLETNÍ PROJEKT

Konverzační AI chatbot pro expertní konzultace o esenciálních olejích s freemium business modelem.

---

## 📋 DOKUMENTACE

- **[Architektura](./FLEURDIN_ARCHITECTURE.md)** - Kompletní technická architektura, RAG workflow, business model
- **[Security](./SECURITY.md)** - Ochrana před boty, DDoS a cost management
- **[Dataset README](./1-EO_Dataset/README.md)** - HuggingFace dataset dokumentace
- **[Fine-tuning README](./2-Fine_tuning/README.md)** - Návod na fine-tuning Gemma 2-2B-it
- **[AI Solutions Comparison](./AI_Solutions_Comparison.md)** - Porovnání AI řešení na trhu

---

## 🎯 PŘEHLED PROJEKTU

### **Co je Fleurdin AI?**

Chatbot pro **www.fleurdin.cz** poskytující expertní poradenství o esenciálních olejích, jejich účincích a použití.

### **Business Model:**

| Feature | FREE | PREMIUM |
|---|---|---|
| Konverzační AI | ✅ | ✅ |
| Počet olejů | 20-30 | 300 |
| Doporučení | ✅ | ✅ |
| Recepty (kapky, použití) | ❌ | ✅ |
| Cena | Zdarma | 299 Kč/měsíc |

---

## 🏗️ ARCHITEKTURA

```
WIX Website (fleurdin.cz)
    ↓
Vercel Next.js API (+ LangChain)
    ↓
┌─────────────────┬──────────────────┐
↓                 ↓                  ↓
Supabase       HuggingFace      Security
(pgvector)     (Gemma 2B)       (Rate limit)
```

### **Tech Stack:**

- **LLM:** Fine-tuned Gemma 2-2B-it
- **Dataset:** TomasBo/Fleurdin (2,281 Q&A)
- **Vector DB:** Supabase pgvector
- **RAG:** LangChain
- **Backend:** Vercel Next.js
- **Frontend:** WIX + Custom Widget
- **Auth:** Supabase Auth
- **Payments:** Stripe

### **Klíčové koncepty:**

**RAG (Retrieval-Augmented Generation):**
- Model rozumí aromaterapii (fine-tuning)
- Fakta tahá z databáze (RAG)
- Přidání nového oleje = 2 minuty (SQL insert)
- **Žádný re-training nutný!**

---

## 💰 NÁKLADY & REVENUE

### **Infrastruktura:**

| Komponenta | Měsíční náklady |
|---|---|
| HuggingFace Inference | $50-80 |
| Supabase Pro | $25 |
| Vercel Pro | $20 |
| Security (Upstash) | $0-5 |
| **TOTAL** | **$95-130/měsíc** |

### **Revenue projekce:**

| Fáze | Free users | Premium | MRR | Profit |
|---|---|---|---|---|
| Měsíc 1-3 | 100 | 10 | 2,990 Kč | +490 Kč |
| Měsíc 4-6 | 300 | 30 | 8,970 Kč | +6,270 Kč |
| ROK 2 | 1,000 | 100 | 29,900 Kč | +26,400 Kč |

**Break-even:** 3-6 měsíců (10-15 premium users)

---

## 🔒 SECURITY & COST PROTECTION

### **MVP Security (MUST-HAVE):**

1. ✅ **Rate Limiting** (Upstash Redis)
   - Free: 10 zpráv/min, 50/den
   - Premium: 50 zpráv/min, 500/den

2. ✅ **Input Validation**
   - Max 500 znaků
   - XSS/spam protection

3. ✅ **HuggingFace Auto-pause**
   - GPU pause po 5 min idle
   - Savings: $432 → $50-80/měsíc

4. ✅ **Cost Tracking**
   - Real-time monitoring
   - Daily/monthly limits

### **Launch Security (SHOULD-HAVE):**

5. ✅ **CAPTCHA** (Google reCAPTCHA)
   - Pro free tier anonymous users

6. ✅ **IP Blacklisting**
   - Auto-ban po 5 violations

7. ✅ **Email Alerts**
   - Warning: $10/day
   - Critical: $50/day (auto-shutdown)

**📖 Detaily:** [SECURITY.md](./SECURITY.md)

---

## 📁 STRUKTURA PROJEKTU

```
Fleurdin_AI/
├── 1-EO_Dataset/                  # Dataset & upload
│   ├── README.md                  # HuggingFace dataset card
│   ├── generate_qa_dataset.py     # Generator Q&A párů
│   ├── script-push.py             # Upload na HuggingFace
│   └── EO_dataset_huggingface.json # 2,281 Q&A párů
│
├── 2-Fine_tuning/                 # Fine-tuning scripts
│   ├── README.md                  # Návod na fine-tuning
│   ├── requirements.txt           # Dependencies
│   ├── test_base_model.py         # Test PŘED fine-tuningem
│   ├── finetune_gemma.py          # Fine-tuning script
│   └── test_finetuned_model.py    # Test PO fine-tuningu
│
├── 3-Backend/                     # (TODO) Vercel Next.js API
│   ├── app/api/chat/route.ts     # Chat endpoint
│   ├── lib/ratelimit.ts           # Rate limiting
│   ├── lib/rag.ts                 # RAG pipeline
│   └── lib/security.ts            # Security utils
│
├── 4-Frontend/                    # (TODO) WIX widget
│   └── chat-widget.tsx            # Embedded chatbot
│
├── Raw_data/                      # Zdrojová data
│   └── Pro_trenovani/
│       └── EO_prehled oleju_raw data.csv.xlsx
│
├── FLEURDIN_ARCHITECTURE.md       # 📖 Kompletní architektura
├── SECURITY.md                    # 🔒 Security dokumentace
├── AI_Solutions_Comparison.md     # 💰 Market analysis
├── PROJECT_README.md              # 📋 Tento soubor
└── README.md                      # HuggingFace dataset README
```

---

## 🚀 QUICK START

### **1. Dataset (HOTOVO ✅)**

Dataset je hotový a nahrán na HuggingFace:
- **Repo:** https://huggingface.co/datasets/TomasBo/Fleurdin
- **Q&A páry:** 2,281
- **Oleje:** 30

### **2. Fine-tuning (NEXT STEP 🎯)**

```bash
cd 2-Fine_tuning

# Install dependencies
pip install -r requirements.txt

# Test base model
python test_base_model.py

# Fine-tune
python finetune_gemma.py

# Test fine-tuned model
python test_finetuned_model.py
```

**Čas:** 2-4 hodiny (záleží na GPU)

**📖 Návod:** [2-Fine_tuning/README.md](./2-Fine_tuning/README.md)

### **3. Backend (TODO)**

```bash
cd 3-Backend

# Install dependencies
npm install

# Setup environment variables
cp .env.example .env
# Fill in: SUPABASE_URL, HF_TOKEN, UPSTASH_REDIS_URL

# Run dev server
npm run dev
```

### **4. Deploy (TODO)**

```bash
# Vercel
vercel deploy

# HuggingFace Inference Endpoint
# UI: https://ui.endpoints.huggingface.co
```

---

## 📚 DOKUMENTACE (DETAIL)

### **1. Architektura ([FLEURDIN_ARCHITECTURE.md](./FLEURDIN_ARCHITECTURE.md))**

- Business model (freemium)
- Technická architektura (RAG + fine-tuning)
- Database schema (Supabase)
- RAG workflow (krok po kroku)
- Postupné přidávání olejů (bez re-trainingu)
- Náklady & revenue projekce
- Fáze vývoje (MVP → Growth → Scale)

### **2. Security ([SECURITY.md](./SECURITY.md))**

- Reálná rizika (bot attacks, scraping, DDoS)
- MVP security (rate limiting, input validation, auto-pause, cost tracking)
- Launch security (CAPTCHA, IP blacklisting, email alerts)
- Implementační checklist
- Code examples

### **3. Dataset ([1-EO_Dataset/README.md](./1-EO_Dataset/README.md))**

- Dataset struktura (2,281 Q&A)
- 6 typů otázek
- Kategorie účinků
- Použití (loading, fine-tuning)
- HuggingFace integration

### **4. Fine-tuning ([2-Fine_tuning/README.md](./2-Fine_tuning/README.md))**

- Hardware requirements
- Installation (venv, dependencies)
- Workflow (test → train → test)
- Troubleshooting (OOM, slow training)
- Upload na HuggingFace

### **5. AI Solutions Comparison ([AI_Solutions_Comparison.md](./AI_Solutions_Comparison.md))**

- Out-of-box platformy (Intercom, Tidio, ChatBase)
- Custom API řešení (OpenAI, Anthropic, HuggingFace)
- Pricing comparison
- Decision tree
- Doporučení pro různé use cases

---

## 🎓 KLÍČOVÉ KONCEPTY

### **RAG vs Fine-tuning:**

| Aspekt | Fine-tuning | RAG |
|---|---|---|
| **Update dat** | Re-training (hodiny) | SQL insert (minuty) |
| **Náklady** | $5-20 per update | $0 per update |
| **Use case** | Styl, chování | Faktické info |

**ZÁVĚR:** Kombinace obou! Fine-tuning pro styl, RAG pro data.

### **Tier Filtering:**

```python
# Free users → hledá jen tier='free' oleje (20)
# Premium users → hledá všechny oleje (300)

retriever = vectorstore.as_retriever(
    search_kwargs={
        "user_tier": "free"  # or "premium"
    }
)
```

### **Model Scaling:**

| Fáze | Model | Use case |
|---|---|---|
| **ROK 1** | Gemma 2-2B-it | 100 olejů |
| **ROK 2** | Gemma 2-9B-it | Oleje + bylinky |
| **ROK 3** | Gemma 2-27B-it | Full expansion + medicína |

---

## ✅ PROGRESS TRACKER

### **✅ HOTOVO:**

- [x] Dataset creation (2,281 Q&A)
- [x] Upload na HuggingFace
- [x] Dataset card (README)
- [x] Architecture design
- [x] Security strategy
- [x] Fine-tuning scripts
- [x] Test questions (9 otázek)

### **🎯 AKTUÁLNĚ:**

- [ ] Fine-tuning Gemma 2-2B-it
- [ ] Test & comparison (before vs after)

### **📋 TODO:**

- [ ] Backend (Vercel Next.js)
  - [ ] Chat API endpoint
  - [ ] Rate limiting
  - [ ] RAG pipeline (LangChain)
  - [ ] Security middleware

- [ ] Supabase Setup
  - [ ] Database schema
  - [ ] pgvector extension
  - [ ] Upload 30 olejů + embeddings
  - [ ] Auth setup

- [ ] Frontend (WIX widget)
  - [ ] Chat UI component
  - [ ] Session management
  - [ ] CAPTCHA integration

- [ ] Deploy
  - [ ] HuggingFace Inference Endpoint
  - [ ] Vercel deployment
  - [ ] DNS setup

- [ ] Testing
  - [ ] End-to-end test
  - [ ] Security test (rate limit, spam)
  - [ ] Load test

- [ ] Launch
  - [ ] Beta test (10 users)
  - [ ] Marketing (SEO, social)
  - [ ] Monitoring (analytics, costs)

---

## 💡 NEXT STEPS

### **Týden 1-2: Fine-tuning**
1. Setup GPU environment (Google Colab nebo local)
2. Run `test_base_model.py`
3. Run `finetune_gemma.py` (1-3 hodiny)
4. Run `test_finetuned_model.py`
5. Compare results
6. Upload model na HuggingFace

### **Týden 3-4: Backend**
1. Setup Supabase project
2. Create database schema
3. Implement chat API endpoint
4. Add rate limiting (Upstash)
5. Implement RAG pipeline (LangChain)
6. Test locally

### **Týden 5-6: Frontend & Deploy**
1. Create WIX chat widget
2. Integrate with backend API
3. Add CAPTCHA
4. Deploy HuggingFace Inference Endpoint
5. Deploy Vercel backend
6. End-to-end test
7. **Launch! 🚀**

---

## 📞 KONTAKT & SUPPORT

**Projekt:** Fleurdin AI
**Web:** www.fleurdin.cz
**HuggingFace:** [@TomasBo](https://huggingface.co/TomasBo)
**Dataset:** [TomasBo/Fleurdin](https://huggingface.co/datasets/TomasBo/Fleurdin)

---

## 📚 EXTERNAL RESOURCES

- **HuggingFace Transformers:** https://huggingface.co/docs/transformers
- **LangChain:** https://python.langchain.com
- **Supabase:** https://supabase.com/docs
- **Vercel:** https://vercel.com/docs
- **Gemma:** https://ai.google.dev/gemma

---

**Vytvořeno:** 2025-01-30
**Poslední update:** 2025-01-30
**Status:** In Development (Fine-tuning phase)

**Vytvořeno s ❤️ pro Fleurdin**
