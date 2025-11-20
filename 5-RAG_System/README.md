# Fleurdin AI - RAG System pro Aromaterapii

LangGraph-based RAG (Retrieval-Augmented Generation) systém pro doporučování esenciálních olejů a bylinných přípravků.

## 🎯 Popis

Inteligentní aromatherapeutický asistent, který:
- Kombinuje znalosti o esenciálních olejích a bylinkách
- Odpovídá v jazyce uživatele (čeština/slovenština)
- Používá vector search pro relevantní doporučení
- Nabízí praktické rady na míru

## 🏗️ Architektura

### Framework
- **LangGraph** - orchestrace workflow
- **LangChain** - LLM komponenty

### Komponenty (Nodes)
1. **PrepareQueryNode** - vylepšení uživatelského dotazu pro vector DB
2. **GetDataFromDBNode** - vyhledávání v databázi (50% oleje + 50% bylinky)
3. **AnswerNode** - generování odpovědi přes LLM

### Technologie
- **LLM**: OpenAI GPT-4o-mini
- **Embeddings**: HuggingFace `paraphrase-multilingual-MiniLM-L12-v2` (lokální, zdarma)
- **Vector DB**: JSON-based s cosine similarity
- **Monitoring**: LangSmith (volitelné)

## 📊 Workflow

```
START → PrepareQuery → GetDataFromDB → AnswerNode → END
```

1. Uživatel zadá otázku
2. PrepareQuery vylepší dotaz pro vector search
3. GetDataFromDB najde 3 nejrelevant nější oleje + 3 bylinky
4. AnswerNode vygeneruje přátelskou odpověď

## 🚀 Instalace

### Prerekvizity
- Python 3.12+
- OpenAI API klíč

### Kroky

1. **Naklonovat repozitář**
```bash
git clone https://github.com/tomasb01/Fleurdin_AI.git
cd Fleurdin_AI/5-RAG_System
```

2. **Vytvořit virtual environment**
```bash
python -m venv .venv
source .venv/bin/activate  # Na Windows: .venv\Scripts\activate
```

3. **Nainstalovat závislosti**
```bash
pip install -r requirements.txt
```

4. **Nastavit environment variables**
```bash
cp .env.example .env
# Upravit .env a doplnit OPENAI_API_KEY
```

5. **Stáhnout data** ⚠️
```bash
# Soubor chunked_data_with_embeddings.json (39 MB) není v repozitáři
# Kontaktujte autora pro přístup k datům
```

## 💻 Použití

```bash
python RAG_agents_script.py
```

### Příklad konverzace

```
=== Aromatherapy AI Assistant ===
(Zadej 'konec' pro ukončení)

Vaše otázka: Jaké oleje mohu použít na bolest hlavy?

Odpověď: Pro bolest hlavy doporučuji následující esenciální oleje:

**Oregano (Dobromysl obecná)** - má analgetické účinky.
Můžete ho použít v difuzéru (1-2 kapky) nebo zředěný na masáž spánků.

**Růže** - má protizánětlivé účinky a pomáhá uvolnit napětí.
Přidejte pár kapek do teplé lázně nebo použijte v difuzéru.

Z bylinných alternativ můžete zkusit **řebříček** jako čaj
nebo **levanduli** v tinktuře...
```

## 📁 Struktura souborů

```
5-RAG_System/
├── RAG_agents_script.py          # Hlavní RAG systém
├── visualizer.py                  # Vizualizace LangGraph grafu
├── requirements.txt               # Python dependencies
├── .env.example                   # Šablona pro environment variables
├── README.md                      # Tato dokumentace
└── chunked_data_with_embeddings.json  # Data (není v repozitáři)
```

## ⚙️ Konfigurace

### Změna modelu
V `RAG_agents_script.py`:
```python
llm = ChatOpenAI(model="gpt-4o-mini")  # Změnit na gpt-4, gpt-3.5-turbo, atd.
```

### Změna počtu výsledků
```python
relevant_docs = search_similar_chunks(query_embedding, top_k=6)  # Změnit top_k
```

### Vypnutí LangSmith trackingu
V `.env`:
```
LANGCHAIN_TRACING_V2=false
```

## 📊 Datová struktura

### Chunk formát
```json
{
  "id": "oil_1_full",
  "text": "OLEJ: Oregano...",
  "type": "essential_oil",  // nebo "book_paragraph"
  "name": "Oregano - Dobromysl obecná",
  "embedding": [0.123, -0.456, ...]
}
```

## 🛠️ Development

### Spuštění s debug módem
Odkomentujte v `PrepareQueryNode`:
```python
print("PrepareQueryNode")
print(state)
```

### Vizualizace grafu
Po spuštění se automaticky vytvoří `graph.png` s vizualizací workflow.

## 📝 Logy konverzací

Automaticky se ukládají do `conversation_log_YYYY-MM-DD.txt`:
```
============================================================
Session: 21:30:15
============================================================

[2025-11-19T21:30:20]
Q: Jaké oleje mohu použít na bolest hlavy?
A: Pro bolest hlavy doporučuji...
```

## 🎓 Školní úkol

Tento projekt splňuje zadání:
- ✅ **Framework**: LangGraph + LangChain
- ✅ **Agent s tools**: 3 nodes (PrepareQuery, GetDataFromDB, AnswerNode)
- ✅ **Databáze**: Vector database (JSON-based s embeddings)
- ✅ **LLM odpovědi**: OpenAI GPT-4o-mini

## 📜 Licence

Tento projekt je vytvořen pro vzdělávací účely.

## 👤 Autor

Tomáš Böhm
- GitHub: [@tomasb01](https://github.com/tomasb01)
- Email: kontakt přes GitHub

## 🙏 Poděkování

- Dataset: Fleurdin aromaterapie
- Framework: LangChain & LangGraph
- Embeddings: HuggingFace sentence-transformers
