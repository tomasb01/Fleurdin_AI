# 🌿 Fleurdin AI Agent - Hybrid RAG Workflow

**Verze:** 1.0
**Autor:** Tomáš
**Datum:** 2025-12-01

---

## 📋 Přehled

AI Agent pro konzultace o esenciálních olejích a bylinách s **hybridním přístupem k datům**:
- 🗄️ **Lokální vektorová databáze** - vlastní knowledge base s embeddings
- 🌐 **Web search** - aktuální informace a studie (Tavily API)

---

## 🎯 Co tento workflow dělá

Agent automaticky:
1. **Přijme dotaz** od uživatele
2. **Rozhodne**, který tool použít (nebo oba):
   - **Fleurdin Vector Search** → hledá v lokální databázi olejů/bylin
   - **Tavily Search** → hledá aktuální info na webu
3. **Zkombinuje výsledky** z obou zdrojů
4. **Vygeneruje odpověď** pomocí LLM (GPT-4, Claude, nebo jiný model)

---

## 🏗️ Architektura workflow

```
┌─────────────┐
│ Chat Input  │ ← Uživatel: "Jaké oleje na stres?"
└──────┬──────┘
       ↓
┌─────────────────────────────────────────┐
│ Agent (Tool Calling) + Language Model   │
│                                         │
│  Rozhodne, který tool použít:          │
│    ↓                    ↓               │
│  ┌─────────────┐  ┌──────────────┐     │
│  │ Fleurdin    │  │ Tavily       │     │
│  │ Vector      │  │ Search       │     │
│  │ Search      │  │ (web)        │     │
│  └─────────────┘  └──────────────┘     │
│         ↓               ↓               │
│    Levandule,      "Studie z 2024      │
│    Bergamot...      ukazují..."        │
│         ↓               ↓               │
│  ┌─────────────────────────────┐       │
│  │ Agent kombinuje výsledky    │       │
│  └─────────────────────────────┘       │
└──────────────────┬──────────────────────┘
                   ↓
            ┌──────────────┐
            │ Chat Output  │ → "Doporučuji lavanduli..."
            └──────────────┘
```

---

## 🔧 Komponenty workflow

| Komponenta | Popis | Konfigurace |
|------------|-------|-------------|
| **Chat Input** | Vstup od uživatele | - |
| **Fleurdin Vector Search Tool** | Custom komponenta pro sémantické vyhledávání v JSON databázi | Cesta k DB: `/app/chunked_data_FIXED.json`, Top K: 3 |
| **Tavily Search API** | Web search pro aktuální informace | API key potřebný |
| **Agent** | Tool Calling Agent orchestrující oba tools | - |
| **Language Model** | LLM pro generování odpovědí | OpenAI/Anthropic/local |
| **Chat Output** | Zobrazení výsledků | - |

---

## 📦 Požadavky

### **1. Python balíčky (v Docker containeru):**
```bash
pip install sentence-transformers numpy langchain langchain-core
```

### **2. Datové soubory:**
- `chunked_data_FIXED.json` - vektorová databáze (~30-40 esenciálních olejů s embeddings)
- Velikost: ~5-10 MB
- Formát: JSON s embeddings (384 dims)

### **3. API klíče:**
- **Tavily API key** - zdarma na https://tavily.com (500 requests/měsíc)
- **OpenAI/Anthropic API key** - pro LLM model (nebo použij local model)

---

## 🚀 Setup Instructions

### **Krok 1: Příprava Docker containeru**

```bash
# Najdi Langflow container ID
docker ps

# Instaluj sentence-transformers
docker exec -it <container-id> pip install sentence-transformers
```

### **Krok 2: Zkopíruj databázi do containeru**

```bash
# Zkopíruj JSON databázi do containeru
docker cp chunked_data_FIXED.json <container-id>:/app/chunked_data_FIXED.json

# Ověř, že se zkopírovala
docker exec -it <container-id> ls -lh /app/chunked_data_FIXED.json
```

**Výstup by měl být:**
```
-rw-r--r-- 1 root root 5.2M Dec  1 10:30 /app/chunked_data_FIXED.json
```

### **Krok 3: Import workflow do Langflow**

1. Otevři Langflow UI
2. Klikni na **"Import"** (nebo drag & drop)
3. Vyber soubor: `Agent_Flow_DBquery.json`
4. Workflow se načte s 6 komponentami

### **Krok 4: Nastavení API klíčů**

#### **A) Tavily Search:**
1. Jdi na https://tavily.com a registruj se (zdarma)
2. Zkopíruj API key
3. V Langflow workflow:
   - Klikni na **Tavily Search API** komponentu
   - Vlož API key do pole "API Key"

#### **B) Language Model:**
1. Klikni na **Language Model** komponentu
2. Zvol model (např. OpenAI GPT-4)
3. Vlož API key
   - OpenAI: https://platform.openai.com/api-keys
   - Anthropic: https://console.anthropic.com/

### **Krok 5: Konfigurace Fleurdin komponenty**

1. Klikni na **Fleurdin Vector Search Tool**
2. Zkontroluj cestu k databázi: `/app/chunked_data_FIXED.json`
3. Top K Results: `3` (kolik výsledků vrátit)

### **Krok 6: Test workflow**

1. Klikni na **▶️ Play** button (vpravo nahoře)
2. Otevře se chat
3. Zkus testovací dotaz: **"Jaké oleje na stres?"**

**Očekávaný výsledek:**
```
Agent použije Fleurdin Vector Search tool a najde:
- Levandule (Similarity: 0.89)
- Bergamot (Similarity: 0.85)
- Meduňka (Similarity: 0.82)

Pak vygeneruje odpověď s detaily o účincích.
```

---

## 🧪 Testovací dotazy

### **1. Jen lokální databáze:**
```
"Jaké jsou účinky oregana na tělo?"
"Co je levandule a na co se používá?"
```
→ Agent použije **jen Fleurdin tool**

### **2. Kombinace (lokální + web):**
```
"Jaké oleje na stres a co o nich říkají nejnovější studie?"
"Které esenciální oleje jsou nejlepší podle vědeckých výzkumů?"
```
→ Agent použije **oba tools**:
1. Fleurdin → najde oleje z databáze
2. Tavily → najde aktuální studie
3. Zkombinuje odpověď

### **3. Jen web:**
```
"Co je nového v aromaterapii v roce 2024?"
"Jaké jsou trendy v přírodní medicíně?"
```
→ Agent použije **jen Tavily**

---

## 🔍 Technické detaily

### **Vector Search:**
- **Model:** `paraphrase-multilingual-MiniLM-L12-v2`
- **Dimenze:** 384
- **Metrika:** Cosine similarity
- **Top K:** 3 výsledky
- **Jazyky:** Čeština + Slovenština

### **Databáze:**
- **Formát:** JSON
- **Velikost:** ~30-40 chunků (esenciální oleje)
- **Struktura:**
  ```json
  {
    "chunks": [
      {
        "id": "oil_1",
        "name": "Oregano - Dobromysl obecná",
        "text": "OLEJ: Oregano...",
        "type": "essential_oil",
        "tier": "free",
        "metadata": {...},
        "embedding": [0.1, 0.2, ...]  // 384 dims
      }
    ]
  }
  ```

### **Výkon:**
- **První spuštění:** ~10-15 sekund (stahuje embedding model)
- **Další dotazy:** ~1-2 sekundy
- **Caching:** Model a databáze zůstávají v RAM

---

## ⚠️ Troubleshooting

### **Problém 1: "ModuleNotFoundError: No module named 'sentence_transformers'"**

**Řešení:**
```bash
docker exec -it <container-id> pip install sentence-transformers
docker restart <container-id>
```

### **Problém 2: "FileNotFoundError: chunked_data_FIXED.json"**

**Řešení:**
```bash
# Zkontroluj, že soubor je v containeru
docker exec -it <container-id> ls /app/chunked_data_FIXED.json

# Pokud není, zkopíruj ho znovu
docker cp chunked_data_FIXED.json <container-id>:/app/chunked_data_FIXED.json
```

### **Problém 3: "Agent nevolá Fleurdin tool"**

**Možné příčiny:**
- LLM model není správně nakonfigurován
- API key chybí nebo je neplatný
- Tool není připojen k Agentovi

**Řešení:**
1. Zkontroluj připojení: Fleurdin komponenta → Agent (Tools input)
2. Zkontroluj Language Model: API key musí být platný
3. Zkus explicitní dotaz: "Použij fleurdin_knowledge_search tool a najdi oleje na stres"

### **Problém 4: "Tavily API error"**

**Řešení:**
- Zkontroluj API key
- Free tier má limit 500 requests/měsíc
- Zkontroluj https://app.tavily.com/usage

---

## 📊 Co workflow obsahuje (metadata)

Soubor `Agent_Flow_DBquery.json` obsahuje na začátku kompletní metadata:

```json
{
  "name": "Fleurdin AI Agent - Hybrid RAG Workflow",
  "description": "...",
  "metadata": {
    "purpose": "...",
    "features": [...],
    "components": {...},
    "workflow": "...",
    "use_cases": [...],
    "requirements": {...},
    "setup_instructions": {...},
    "technical_details": {...},
    "demo_queries": [...],
    "notes": [...],
    "future_enhancements": [...]
  },
  "data": { ... }  // samotný workflow
}
```

Můžeš si metadata přečíst v libovolném JSON editoru nebo přímo v souboru.

---

## 🚀 Budoucí vylepšení

1. **Rozšíření databáze:**
   - Přidat voice transkripty (chunky z audio nahrávek)
   - Přidat knihy o bylinkách
   - Rozšířit na 300 olejů

2. **Tier systém:**
   - Free: 20 olejů
   - Premium: 300 olejů + recepty

3. **Recepty:**
   - Detailní návody (počet kapek, použití)
   - Směsi pro konkrétní stavy

4. **Production deployment:**
   - Supabase (pgvector) místo JSON
   - Vercel (backend API)
   - WIX (frontend widget)

---

## 📞 Podpora

**Projekt:** Fleurdin AI
**GitHub:** [doplnit URL]
**Kontakt:** [doplnit email]

---

## 📄 Licence

[Doplnit podle potřeby]

---

**Vytvořeno s ❤️ pro Fleurdin**
**Poslední update:** 2025-12-01
