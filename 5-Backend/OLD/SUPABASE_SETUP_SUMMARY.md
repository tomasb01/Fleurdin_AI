# 🌿 FLEURDIN AI - SUPABASE SETUP SHRNUTÍ

**Datum:** 4. listopadu 2025
**Status:** Databáze nastavena, embeddings nahrány, debugging vector search

---

## 📊 PŘEHLED PROJEKTU

**Fleurdin AI** je RAG-based chatbot pro konzultace o esenciálních olejích, bylinkách a (budoucně) vitamínech.

### **Klíčové vlastnosti:**
- ✅ **RAG architektura** (Retrieval-Augmented Generation)
- ✅ **Vector search** pomocí pgvector
- ✅ **Tier systém** (Free: 20 položek, Premium: vše)
- ✅ **Multimodální obsah** (oleje, bylinky + knihy/audio, vitamíny)
- ✅ **Škálovatelné** - přidání nového oleje = 2 minuty (bez re-trainingu)

---

## 🗄️ DATABASE STRUKTURA

### **1. CATEGORIES (Kategorie obsahu)**

```sql
CREATE TABLE categories (
  id BIGSERIAL PRIMARY KEY,
  name TEXT NOT NULL UNIQUE,
  display_name TEXT NOT NULL,
  description TEXT,
  icon TEXT,
  created_at TIMESTAMP DEFAULT NOW()
);
```

**Existující kategorie:**
1. **essential_oils** (🌿 Esenciální oleje) - Aromaterapie
2. **herbs** (🌱 Bylinky) - Léčivé byliny z knih + audio
3. **vitamins** (💊 Vitamíny) - Připraveno pro budoucnost

---

### **2. CONTENT_ITEMS (Hlavní obsah)**

```sql
CREATE TABLE content_items (
  id BIGSERIAL PRIMARY KEY,
  category_id BIGINT REFERENCES categories(id),

  -- Základní info
  name TEXT NOT NULL,
  latin_name TEXT,

  -- Strukturovaná data (JSONB)
  effects_body JSONB,
  effects_psyche JSONB,
  usage_instructions JSONB,

  -- Metadata
  frequency INTEGER,
  safety_info TEXT,

  -- Pro bylinky: Reference na knihy/audio
  book_references JSONB,
  audio_references JSONB,

  -- Tier systém
  tier TEXT DEFAULT 'free' CHECK (tier IN ('free', 'premium')),

  -- Vector embedding pro RAG (384 dimensions)
  embedding VECTOR(384),

  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);
```

**Důležité:**
- `embedding` je typu `VECTOR(384)` (pgvector extension)
- Když Python client čte embedding, vrací ho jako **STRING**, musí se parsovat: `json.loads(embedding)`
- JSONB umožňuje flexibilní strukturu (každá kategorie může mít různá pole)

---

### **3. RECIPES (Recepty - Premium only)**

```sql
CREATE TABLE recipes (
  id BIGSERIAL PRIMARY KEY,
  title TEXT NOT NULL,
  description TEXT,
  condition TEXT NOT NULL,
  ingredients JSONB NOT NULL,
  usage_method TEXT,
  instructions TEXT NOT NULL,
  category_id BIGINT REFERENCES categories(id),
  tier TEXT DEFAULT 'premium',
  embedding VECTOR(384),
  created_at TIMESTAMP DEFAULT NOW()
);
```

---

### **4. USERS (Uživatelé + Tier management)**

```sql
CREATE TABLE users (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  email TEXT UNIQUE,
  tier TEXT DEFAULT 'free' CHECK (tier IN ('free', 'premium')),
  stripe_customer_id TEXT,
  subscription_status TEXT,
  subscription_end_date TIMESTAMP,
  preferences JSONB DEFAULT '{}',
  created_at TIMESTAMP DEFAULT NOW()
);
```

---

### **5. CONVERSATIONS (Historie chatu)**

```sql
CREATE TABLE conversations (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID REFERENCES users(id),
  session_id TEXT NOT NULL,
  messages JSONB NOT NULL,
  created_at TIMESTAMP DEFAULT NOW()
);
```

---

### **6. USAGE_TRACKING (Monitoring nákladů)**

```sql
CREATE TABLE usage_tracking (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID REFERENCES users(id),
  session_id TEXT,
  message_length INTEGER,
  tokens_used INTEGER,
  response_time_ms INTEGER,
  cost_estimate DECIMAL(10, 6),
  timestamp TIMESTAMP DEFAULT NOW()
);
```

---

## 🔍 VECTOR SEARCH FUNKCE

### **match_content() - Hlavní RAG funkce**

```sql
CREATE OR REPLACE FUNCTION match_content(
  query_embedding VECTOR(384),
  match_threshold FLOAT DEFAULT 0.7,
  match_count INT DEFAULT 5,
  user_tier TEXT DEFAULT 'free',
  category_filter TEXT DEFAULT NULL
)
RETURNS TABLE (
  id BIGINT,
  category_name TEXT,
  name TEXT,
  latin_name TEXT,
  effects_body JSONB,
  effects_psyche JSONB,
  usage_instructions JSONB,
  frequency INTEGER,
  book_references JSONB,
  audio_references JSONB,
  similarity FLOAT
)
```

**Funguje takto:**
1. Přijme query embedding (384 dims)
2. Hledá v `content_items` pomocí cosine similarity (`<=>` operátor)
3. Filtruje podle:
   - `match_threshold` (minimální podobnost)
   - `user_tier` (free vidí jen tier='free', premium vidí vše)
   - `category_filter` (volitelně filtruje kategorii)
4. Vrací top K nejpodobnějších položek

**⚠️ DŮLEŽITÉ:**
- Embedding musí být typu `VECTOR(384)`, ne string/list
- Similarity score: 1.0 = identické, 0.0 = nepodobné
- Použití: `1 - (embedding <=> query_embedding)` vrací similarity (vyšší = lepší)

---

## 📈 SOUČASNÝ STAV

### **Nahrané data:**
- ✅ **30 esenciálních olejů** s embeddings
- ✅ **20 free tier** (ID 31-50)
- ✅ **10 premium tier** (ID 51-60)

### **Embeddings:**
- ✅ Model: `paraphrase-multilingual-MiniLM-L12-v2`
- ✅ Dimenze: 384
- ✅ Formát v DB: `VECTOR(384)` (pgvector)
- ⚠️ Python client čte jako STRING - musí se parsovat

### **Vector search status:**
- ✅ **Funguje v SQL** (Test 2 úspěšný: našlo Oregano → Majoránka similarity 0.76)
- ❌ **Nefunguje z Pythonu** (Test RAG: hledá Oregano → najde Řebříček)
- 🔍 **Debugging:** Testujeme RPC funkci `match_content()`

---

## 🎯 TIER SYSTÉM

### **Free tier:**
- Vidí jen položky s `tier='free'`
- 20 esenciálních olejů
- Základní doporučení (bez receptů)

### **Premium tier:**
- Vidí VŠECHNY položky (free + premium)
- 300+ esenciálních olejů (budoucně)
- Recepty s přesnými dávkami
- Historie konverzací
- Bylinky + audio/knihy

**Implementace v RPC:**
```sql
WHERE (ci.tier = 'free' OR user_tier = 'premium')
```

---

## 🔄 WORKFLOW PRO PŘIDÁNÍ NOVÉHO OLEJE

```python
# 1. Připrav data
new_oil = {
    "category_id": 1,  # essential_oils
    "name": "Ylang-Ylang",
    "latin_name": "Cananga odorata",
    "effects_body": {"text": "...", "parsed": False},
    "effects_psyche": {"text": "...", "parsed": False},
    "frequency": 105,
    "tier": "premium"
}

# 2. Vygeneruj embedding
text = f"{new_oil['name']} {new_oil['latin_name']} {effects_text}"
embedding = embedder.encode(text).tolist()

# 3. Vlož do DB
supabase.table('content_items').insert({
    **new_oil,
    "embedding": '[' + ','.join(map(str, embedding)) + ']'  # String formát pro pgvector
}).execute()
```

**Čas:** 2 minuty
**Náklady:** $0
**Re-training:** NEPOTŘEBA ✅

---

## 🌱 BYLINKY - BUDOUCÍ ROZŠÍŘENÍ

### **Struktura dat pro bylinky:**

```python
{
    "category_id": 2,  # herbs
    "name": "Heřmánek pravý",
    "latin_name": "Matricaria chamomilla",
    "effects_body": {
        "text": "Protizánětlivý, uklidňující..."
    },
    "book_references": [
        {
            "book_title": "Velká kniha bylin",
            "page": 125,
            "chapter": "Léčivé byliny",
            "quote": "Heřmánek je jednou z nejdůležitějších..."
        }
    ],
    "audio_references": [
        {
            "file": "byliny_lecive_01.mp3",
            "timestamp": "12:34",
            "duration": "05:20",
            "description": "Heřmánek - příprava a použití"
        }
    ],
    "tier": "premium"  # Bylinky budou premium
}
```

**Cross-category search:**
- Uživatel: "Co pomáhá na nespavost?"
- RAG najde: Levandule (olej) + Heřmánek (bylinka) + Melatonin (vitamín)

---

## 🔧 KNOWN ISSUES & WORKAROUNDS

### **Issue #1: Python client čte embedding jako STRING**

**Problém:**
```python
oil = supabase.table('content_items').select('embedding').eq('id', 1).execute()
type(oil.data[0]['embedding'])  # = <class 'str'>
len(oil.data[0]['embedding'])   # = 4504 (počet znaků, ne elementů!)
```

**Workaround:**
```python
import json
embedding_str = oil.data[0]['embedding']
embedding_list = json.loads(embedding_str)  # List[float] s 384 elementy
```

### **Issue #2: RPC funkce vyžaduje string formát**

**Při volání RPC z Pythonu:**
```python
# ❌ Nefunguje:
result = supabase.rpc('match_content', {
    'query_embedding': [0.1, 0.2, ...]  # List
})

# ✅ Funguje:
result = supabase.rpc('match_content', {
    'query_embedding': '[0.1,0.2,...]'  # String
})
```

---

## 📝 CREDENTIALS & PŘÍSTUP

**Supabase Project:**
- URL: `https://[project-id].supabase.co`
- API Key: `anon public` key (z Settings → API)

**Environment variables (.env):**
```env
SUPABASE_URL=https://xxxxx.supabase.co
SUPABASE_KEY=eyJhbGci...
```

---

## 🚀 NEXT STEPS

1. **[CURRENT]** Debug RPC funkce `match_content()` - zjistit proč nefunguje z Pythonu
2. **[PENDING]** Přidat OpenAI GPT-4o-mini pro generování odpovědí
3. **[PENDING]** Otestovat na 6 otázkách z Excelu a porovnat s výsledky
4. **[FUTURE]** Přidat bylinky (kniha + audio reference)
5. **[FUTURE]** Rozšířit na 200-300 olejů
6. **[FUTURE]** Implementovat recepty (premium tier)

---

## 📚 TECHNOLOGIE

- **Database:** Supabase (PostgreSQL + pgvector)
- **Embeddings:** sentence-transformers (`paraphrase-multilingual-MiniLM-L12-v2`)
- **Vector dimensions:** 384
- **LLM (plánováno):** GPT-4o-mini nebo fine-tuned model
- **Backend:** Python + Supabase client
- **Future:** Vercel Next.js API + LangChain

---

**Vytvořeno:** 4. listopadu 2025
**Projekt:** Fleurdin AI
**Status:** Development (RAG setup phase)

---

## 🔍 UŽITEČNÉ SQL QUERIES

### Zkontrolovat embeddings:
```sql
SELECT
  name,
  pg_typeof(embedding) as type,
  embedding IS NOT NULL as has_embedding
FROM content_items
LIMIT 5;
```

### Test vector similarity:
```sql
WITH query_embedding AS (
  SELECT embedding FROM content_items WHERE name = 'Oregano - Dobromysl obecná'
)
SELECT
  name,
  1 - (embedding <=> (SELECT embedding FROM query_embedding)) AS similarity
FROM content_items
ORDER BY similarity DESC
LIMIT 10;
```

### Smazat všechna data z content_items:
```sql
DELETE FROM content_items;
```

### Resetovat ID counter:
```sql
ALTER SEQUENCE content_items_id_seq RESTART WITH 1;
```

---

**🌿 Fleurdin AI - Přirozená cesta ke zdraví s pomocí AI**
