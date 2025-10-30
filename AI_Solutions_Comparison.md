# POROVNÁNÍ AI ŘEŠENÍ PRO ZÁKAZNICKÝ KONTAKT

## 🏆 TOP DOPORUČENÍ PRO RŮZNÉ POTŘEBY

| **Use Case** | **Doporučené řešení** | **Cena/měsíc** | **Proč** |
|---|---|---|---|
| **Malý e-shop (začátek)** | Tidio | $29 | Levné, jednoduché, česky |
| **FAQ chatbot** | ChatBase | $19-99 | Rychlý setup, kvalitní AI |
| **Custom AI (Fleurdin)** | HuggingFace + Vercel | $50-150 | Plná kontrola, škálovatelné |
| **Enterprise support** | Intercom | $139+ | Komplexní, proven solution |
| **Multi-channel marketing** | ManyChat | $15-145 | WhatsApp/IG/FB integrace |
| **B2B sales** | Drift | $2,500+ | Lead qualification |

---

## 💰 CENOVÉ SROVNÁNÍ

### **Out-of-Box (Subscription)**

| Platforma | Free Tier | Starter | Pro | Enterprise |
|---|---|---|---|---|
| **Tidio** | ✅ 50 konv. | $29 | $329 | Custom |
| **ChatBase** | ✅ 30 zpráv | $19 | $99 | $399 |
| **Intercom** | ❌ | $39 + pay-per-conv | $99 | $139 |
| **Voiceflow** | ✅ 3 projekty | $40 | $125 | Custom |
| **Zendesk** | ❌ | $55/agent | $89/agent | $115/agent |
| **Drift** | ❌ | - | $2,500 | Custom |

### **API-Based (Pay-per-use)**

| Provider | Model | Cena za 1M tokenů | Typická konverzace |
|---|---|---|---|
| **OpenAI** | GPT-4o | $2.50 in / $10 out | $0.006 |
| **OpenAI** | GPT-4o-mini | $0.15 in / $0.60 out | $0.0004 |
| **Anthropic** | Claude 3.5 Sonnet | $3 in / $15 out | $0.009 |
| **Anthropic** | Claude 3 Haiku | $0.25 in / $1.25 out | $0.0008 |
| **HuggingFace** | Gemma 2B (vlastní) | $0.60/hodina GPU | $0.0001 |

**Příklad (1000 konverzací/měsíc):**
- GPT-4o-mini: **~$0.40**
- Claude Haiku: **~$0.80**
- GPT-4o: **~$6**
- HuggingFace (auto-scale): **~$50** (fixed cost)

---

## ✅ VÝHODY & ❌ NEVÝHODY

### **OUT-OF-BOX PLATFORMY**

#### ✅ **VÝHODY:**
- Rychlý setup (hodiny/dny)
- Žádné programování
- Support team k dispozici
- Pravidelné updaty
- Compliance (GDPR, SOC2)
- Analytics built-in
- Multi-channel (web, mobile, social)

#### ❌ **NEVÝHODY:**
- Drahé long-term
- Omezená personalizace
- Vendor lock-in
- Obecné AI (ne specialized)
- Data na jejich serverech
- Měsíční poplatky + per-use fees

---

### **CUSTOM API ŘEŠENÍ**

#### ✅ **VÝHODY:**
- Plná kontrola
- Vlastní UI/UX
- Specialized AI (fine-tuning)
- Škálovatelné
- Levnější long-term (high volume)
- Data security (vlastní servery)
- Žádný vendor lock-in

#### ❌ **NEVÝHODY:**
- Vyžaduje vývojáře
- Delší time-to-market (týdny/měsíce)
- Maintenance na tobě
- Musíš řešit security sám
- Compliance sám
- Monitoring a analytics musíš postavit

---

## 🎯 DECISION TREE

```
START: Potřebuješ AI chatbot?
│
├─ Mám <$100/měsíc budget?
│  ├─ ANO → Tidio nebo ChatBase
│  └─ NE → Pokračuj dolů
│
├─ Potřebuji launch za <1 týden?
│  ├─ ANO → Out-of-box (Intercom, Tidio)
│  └─ NE → Pokračuj dolů
│
├─ Je to jednoduché FAQ/support?
│  ├─ ANO → ChatBase nebo Tidio
│  └─ NE → Pokračuj dolů
│
├─ Specialized knowledge (jako Fleurdin)?
│  ├─ ANO → Custom AI (HuggingFace + Vercel)
│  └─ NE → Pokračuj dolů
│
├─ Potřebuji multi-channel (WhatsApp, IG)?
│  ├─ ANO → ManyChat nebo Voiceflow
│  └─ NE → Pokračuj dolů
│
├─ Enterprise firma (>100 zaměstnanců)?
│  ├─ ANO → Intercom nebo Zendesk
│  └─ NE → Custom nebo Voiceflow
│
└─ Maximální data privacy?
   └─ ANO → Self-hosted (Ollama nebo Botpress)
```

---

## 📈 ŠKÁLOVÁNÍ

### **Malý provoz (<1000 konverzací/měsíc)**
- **Tidio nebo ChatBase** ($19-99/měsíc)
- Nebo API s GPT-4o-mini (<$10/měsíc)

### **Střední provoz (1k-10k konverzací/měsíc)**
- **Voiceflow + OpenAI API** ($40 + $50-100 API)
- Nebo **Intercom** ($139 + pay-per-use)

### **Vysoký provoz (10k-100k konverzací/měsíc)**
- **Custom API** s Claude Haiku ($80-800/měsíc)
- Nebo **HuggingFace vlastní model** ($200-500/měsíc)

### **Enterprise (100k+ konverzací/měsíc)**
- **HuggingFace vlastní model** ($500-2000/měsíc)
- Nebo **dedicated GPU** ($1000+/měsíc)

---

## 🔐 DATA & PRIVACY

| Řešení | Data Storage | GDPR | On-Premise |
|---|---|---|---|
| **Tidio** | EU servery | ✅ | ❌ |
| **Intercom** | US/EU | ✅ | ❌ |
| **ChatBase** | US | ✅ | ❌ |
| **OpenAI API** | US | ⚠️ (DPA nutné) | ❌ |
| **HuggingFace** | EU možné | ✅ | ✅ |
| **Ollama** | Lokální | ✅ | ✅ |

---

## 💡 DOPORUČENÍ PRO FLEURDIN

### **MVP (Fáze 1):**
**HuggingFace + Vercel + Supabase**

**Proč:**
- ✅ Plná kontrola (recepty s kapkami)
- ✅ Specialized AI (300 olejů)
- ✅ Škálovatelné (stovky → tisíce uživatelů)
- ✅ Rozumná cena ($50-150/měsíc start)
- ✅ Multi-tenant ready (pro partnery)
- ✅ Data privacy (EU hosting)

**Alternativa (rychlejší launch):**
**Voiceflow + OpenAI API**
- ⚡ Rychlejší vývoj (vizuální builder)
- 💰 Vyšší cena long-term
- 🔒 Menší kontrola

---

## 📚 RESOURCES

### **Začátečníci:**
- Tidio: https://www.tidio.com
- ChatBase: https://www.chatbase.co

### **Intermediate:**
- Voiceflow: https://www.voiceflow.com
- Botpress: https://botpress.com

### **Advanced:**
- LangChain: https://www.langchain.com
- HuggingFace: https://huggingface.co
- OpenAI API: https://platform.openai.com

### **Tutoriály:**
- Build AI chatbot (no-code): https://youtube.com/watch?v=voiceflow
- Custom GPT integration: https://platform.openai.com/docs
- Fine-tuning guide: https://huggingface.co/docs

---

**Vytvořeno:** 2025-01-30
**Pro:** Fleurdin AI Decision Making
