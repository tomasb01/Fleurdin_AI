# 🔒 FLEURDIN - SECURITY & COST PROTECTION

Kompletní bezpečnostní strategie pro ochranu před boty, DDoS útoky a kontrolu nákladů.

---

## 🚨 PROČ JE TO DŮLEŽITÉ?

### **Reálná rizika:**

**1. Bot Attack:**
```
Útočník napíše script:
while True:
    send_request_to_chatbot("random question")

→ 100,000 requestů za hodinu
→ HuggingFace GPU běží 24/7
→ Měsíční náklady: $432 (místo $50-80)
```

**2. Model Scraping:**
```
Konkurence "krade" tvůj model:
→ Posílají tisíce otázek
→ Sbírají odpovědi
→ Rekonstruují dataset
→ Ty platíš za jejich research
```

**3. DDoS Attack:**
```
Zaplavení API requesty
→ Server přetížený
→ Legit uživatelé nemohou používat chatbot
→ Ztráta zákazníků
```

---

## 🛡️ MVP SECURITY (MUST-HAVE)

Minimální ochrana pro launch.

### **1. RATE LIMITING** ⭐ PRIORITA #1

**Co to je:**
- Omezení počtu requestů per uživatel/IP
- Free: 10 zpráv/min, 50/den
- Premium: 50 zpráv/min, 500/den

**Tech stack:**
- **Upstash Redis** (serverless, rate limiting)
- **@upstash/ratelimit** (NPM package)

**Implementace:**

```typescript
// lib/ratelimit.ts
import { Ratelimit } from "@upstash/ratelimit";
import { Redis } from "@upstash/redis";

export const ratelimit = new Ratelimit({
  redis: Redis.fromEnv(),
  limiter: Ratelimit.slidingWindow(10, "1 m"), // 10 req/min
  analytics: true,
});

export const getRateLimit = (userTier: string) => {
  if (userTier === "premium") {
    return {
      perMinute: new Ratelimit({
        redis: Redis.fromEnv(),
        limiter: Ratelimit.slidingWindow(50, "1 m"),
      }),
      perDay: new Ratelimit({
        redis: Redis.fromEnv(),
        limiter: Ratelimit.slidingWindow(500, "1 d"),
      })
    };
  }

  // Free tier
  return {
    perMinute: new Ratelimit({
      redis: Redis.fromEnv(),
      limiter: Ratelimit.slidingWindow(10, "1 m"),
    }),
    perDay: new Ratelimit({
      redis: Redis.fromEnv(),
      limiter: Ratelimit.slidingWindow(50, "1 d"),
    })
  };
};
```

```typescript
// app/api/chat/route.ts
import { ratelimit, getRateLimit } from "@/lib/ratelimit";

export async function POST(req: NextRequest) {
  const { message, sessionId, userId } = await req.json();

  // Determine user tier
  const userTier = userId ? await getUserTier(userId) : "free";

  // Get rate limiter for tier
  const { perMinute, perDay } = getRateLimit(userTier);

  // Identifier (user ID or session+IP)
  const identifier = userId || `${sessionId}:${req.ip}`;

  // Check rate limit
  const { success: successMin, remaining: remainingMin } =
    await perMinute.limit(identifier);

  if (!successMin) {
    return NextResponse.json(
      {
        error: "Příliš mnoho požadavků. Zkuste za chvíli.",
        retryAfter: 60,
        remaining: 0
      },
      { status: 429 }
    );
  }

  const { success: successDay } = await perDay.limit(identifier);

  if (!successDay) {
    return NextResponse.json(
      {
        error: "Dosáhli jste denního limitu zpráv.",
        upgradeUrl: "/pricing"
      },
      { status: 429 }
    );
  }

  // Proceed with chat
  const response = await processChat(message, userId, sessionId);

  return NextResponse.json({
    response,
    rateLimit: { remaining: remainingMin }
  });
}
```

**Setup Upstash:**
1. Registrace: https://upstash.com
2. Vytvoř Redis database (free tier: 10k requestů/den)
3. Copy credentials do `.env`:
   ```
   UPSTASH_REDIS_REST_URL=https://xxx.upstash.io
   UPSTASH_REDIS_REST_TOKEN=xxx
   ```

**Náklady:** $0-5/měsíc (free tier štědrý)

---

### **2. INPUT VALIDATION** ⭐ PRIORITA #2

**Co to chrání:**
- XSS (Cross-Site Scripting)
- Spam
- Long inputs (vysoké náklady)

**Implementace:**

```typescript
// lib/validation.ts
export const validateMessage = (message: string) => {
  // 1. Max length
  if (message.length > 500) {
    throw new Error("Zpráva je příliš dlouhá (max 500 znaků)");
  }

  // 2. Min length
  if (message.length < 3) {
    throw new Error("Zpráva je příliš krátká (min 3 znaky)");
  }

  // 3. Spam patterns
  const spamPatterns = [
    /(.)\1{10,}/,           // Repeating chars (aaaaaaa)
    /http[s]?:\/\//i,       // URLs
    /<script>/i,            // XSS
    /<iframe>/i,            // XSS
    /javascript:/i,         // XSS
  ];

  for (const pattern of spamPatterns) {
    if (pattern.test(message)) {
      throw new Error("Neplatný obsah zprávy");
    }
  }

  // 4. Only allowed characters (Czech + common symbols)
  const allowedChars = /^[a-zA-ZáčďéěíňóřšťúůýžÁČĎÉĚÍŇÓŘŠŤÚŮÝŽ0-9\s.,!?()-]+$/;
  if (!allowedChars.test(message)) {
    throw new Error("Zpráva obsahuje nepovolené znaky");
  }

  return true;
};
```

```typescript
// app/api/chat/route.ts
import { validateMessage } from "@/lib/validation";

export async function POST(req: NextRequest) {
  const { message } = await req.json();

  try {
    validateMessage(message);
  } catch (error) {
    return NextResponse.json(
      { error: error.message },
      { status: 400 }
    );
  }

  // Proceed...
}
```

**Náklady:** $0 (jen kód)

---

### **3. HUGGINGFACE AUTO-PAUSE** ⭐ PRIORITA #3

**Co to dělá:**
- GPU se automaticky vypne po 5 min bez requestů
- Žádné náklady když nikdo nepoužívá chatbot
- Auto-start při prvním requestu (cold start 30-60s)

**Setup v HuggingFace Inference Endpoint:**

```json
{
  "compute": {
    "accelerator": "gpu",
    "instanceType": "nvidia-t4-small",
    "scaling": {
      "minReplicas": 0,        // ← Může jít na 0 (žádné náklady)
      "maxReplicas": 2         // ← Max 2 instance (cost cap)
    }
  },
  "provider": {
    "region": "us-east-1",
    "vendor": "aws"
  },
  "model": {
    "framework": "pytorch",
    "task": "text-generation",
    "repository": "TomasBo/fleurdin-gemma-2b"
  },
  "auto_pause": {
    "enabled": true,
    "idle_timeout": 300        // ← 5 minut (300 sekund)
  }
}
```

**UI Setup:**
1. HuggingFace → Inference Endpoints → Create
2. Select model: `TomasBo/fleurdin-gemma-2b`
3. Instance: `nvidia-t4-small`
4. Advanced settings:
   - Min replicas: `0`
   - Max replicas: `2`
   - Auto-pause: `300s`

**Náklady:**
- Idle (paused): $0/hod
- Active: $0.60/hod
- Reálné (s auto-pause): $50-80/měsíc (místo $432)

---

### **4. BASIC COST TRACKING** ⭐ PRIORITA #4

**Co to trackuje:**
- Počet requestů per user/session
- Estimovaná cena per request
- Denní/měsíční náklady

**Database schema:**

```sql
-- Supabase
CREATE TABLE usage_tracking (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID REFERENCES users(id),
  session_id TEXT,
  timestamp TIMESTAMP DEFAULT NOW(),
  message_length INTEGER,
  tokens_used INTEGER,
  response_time_ms INTEGER,
  cost_estimate DECIMAL(10, 6),

  INDEX idx_user_timestamp (user_id, timestamp),
  INDEX idx_session_timestamp (session_id, timestamp)
);

-- Function: Get daily costs
CREATE OR REPLACE FUNCTION get_daily_costs()
RETURNS TABLE (
  date DATE,
  total_requests BIGINT,
  total_cost DECIMAL(10, 2)
) AS $$
  SELECT
    DATE(timestamp) as date,
    COUNT(*) as total_requests,
    SUM(cost_estimate)::DECIMAL(10, 2) as total_cost
  FROM usage_tracking
  WHERE timestamp > NOW() - INTERVAL '30 days'
  GROUP BY DATE(timestamp)
  ORDER BY date DESC;
$$ LANGUAGE SQL;
```

**Implementace:**

```typescript
// lib/tracking.ts
export const trackUsage = async (data: {
  userId?: string;
  sessionId: string;
  messageLength: number;
  tokensUsed: number;
  responseTimeMs: number;
}) => {
  // Estimate cost (simplified)
  // HF Inference: $0.60/hour = $0.000167/second
  const costPerSecond = 0.000167;
  const costEstimate = (data.responseTimeMs / 1000) * costPerSecond;

  await supabase.from("usage_tracking").insert({
    user_id: data.userId,
    session_id: data.sessionId,
    message_length: data.messageLength,
    tokens_used: data.tokensUsed,
    response_time_ms: data.responseTimeMs,
    cost_estimate: costEstimate
  });
};
```

```typescript
// app/api/chat/route.ts
export async function POST(req: NextRequest) {
  const startTime = Date.now();

  // Process chat
  const response = await processChat(message, userId, sessionId);

  const responseTime = Date.now() - startTime;

  // Track usage
  await trackUsage({
    userId,
    sessionId,
    messageLength: message.length,
    tokensUsed: response.tokensUsed,
    responseTimeMs: responseTime
  });

  return NextResponse.json({ response });
}
```

**Dashboard (simple):**

```typescript
// app/admin/dashboard/page.tsx
export default async function DashboardPage() {
  const dailyCosts = await supabase.rpc("get_daily_costs");

  return (
    <div>
      <h1>Cost Dashboard</h1>
      <table>
        <thead>
          <tr>
            <th>Date</th>
            <th>Requests</th>
            <th>Cost</th>
          </tr>
        </thead>
        <tbody>
          {dailyCosts.data.map(day => (
            <tr key={day.date}>
              <td>{day.date}</td>
              <td>{day.total_requests}</td>
              <td>${day.total_cost}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
```

**Náklady:** $0 (included in Supabase)

---

## 🚀 LAUNCH SECURITY (SHOULD-HAVE)

Přidej před veřejným launchem.

### **5. CAPTCHA PRO FREE TIER**

**Kdy se zobrazuje:**
- Před prvním použitím chatbotu (anonymous)
- Po 10 zprávách (ověř že nejsi bot)

**Tech stack:**
- Google reCAPTCHA v3 (invisible)

**Setup:**

1. **Google reCAPTCHA:**
   - https://www.google.com/recaptcha/admin
   - Vytvoř site key (v3)
   - Copy site key + secret key

2. **Frontend (WIX widget):**

```tsx
// components/ChatWidget.tsx
import { useGoogleReCaptcha } from "react-google-recaptcha-v3";

export const ChatWidget = () => {
  const { executeRecaptcha } = useGoogleReCaptcha();

  const sendMessage = async (message: string) => {
    // Get CAPTCHA token (invisible, no user interaction)
    const token = await executeRecaptcha("chat_message");

    // Send with request
    const response = await fetch("/api/chat", {
      method: "POST",
      body: JSON.stringify({
        message,
        captchaToken: token
      })
    });
  };
};
```

3. **Backend validation:**

```typescript
// lib/captcha.ts
export const verifyCaptcha = async (token: string): Promise<boolean> => {
  const response = await fetch(
    `https://www.google.com/recaptcha/api/siteverify`,
    {
      method: "POST",
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
      body: new URLSearchParams({
        secret: process.env.RECAPTCHA_SECRET_KEY!,
        response: token
      })
    }
  );

  const data = await response.json();

  // Score 0.0-1.0 (1.0 = human, 0.0 = bot)
  return data.success && data.score > 0.5;
};
```

```typescript
// app/api/chat/route.ts
import { verifyCaptcha } from "@/lib/captcha";

export async function POST(req: NextRequest) {
  const { captchaToken, userId } = await req.json();

  // Verify CAPTCHA (only for anonymous users)
  if (!userId) {
    const isHuman = await verifyCaptcha(captchaToken);

    if (!isHuman) {
      return NextResponse.json(
        { error: "CAPTCHA validace selhala. Zkuste to znovu." },
        { status: 403 }
      );
    }
  }

  // Proceed...
}
```

**Náklady:** $0 (1M assessments/měsíc zdarma)

---

### **6. IP BLACKLISTING**

**Auto-ban abusive IPs:**

```typescript
// lib/blacklist.ts
import { Redis } from "@upstash/redis";

const redis = Redis.fromEnv();

export const banIP = async (ip: string, reason: string, durationHours = 24) => {
  await redis.set(
    `banned:${ip}`,
    JSON.stringify({
      reason,
      bannedAt: Date.now(),
      expiresAt: Date.now() + (durationHours * 3600 * 1000)
    }),
    { ex: durationHours * 3600 }
  );

  console.log(`🚫 IP banned: ${ip} (${reason})`);
};

export const isBanned = async (ip: string): Promise<boolean> => {
  const banned = await redis.get(`banned:${ip}`);
  return banned !== null;
};

export const trackViolation = async (ip: string): Promise<number> => {
  const key = `violations:${ip}`;
  const violations = await redis.incr(key);
  await redis.expire(key, 3600); // Reset po 1 hodině

  // Auto-ban po 5 violations
  if (violations >= 5) {
    await banIP(ip, "Repeated rate limit violations", 24);
  }

  return violations;
};
```

```typescript
// app/api/chat/route.ts
import { isBanned, trackViolation } from "@/lib/blacklist";

export async function POST(req: NextRequest) {
  const ip = req.ip || req.headers.get("x-forwarded-for") || "unknown";

  // Check if banned
  if (await isBanned(ip)) {
    return NextResponse.json(
      { error: "Vaše IP adresa je dočasně blokována" },
      { status: 403 }
    );
  }

  // Rate limit check
  const { success } = await ratelimit.limit(ip);

  if (!success) {
    // Track violation
    await trackViolation(ip);

    return NextResponse.json(
      { error: "Příliš mnoho požadavků" },
      { status: 429 }
    );
  }

  // Proceed...
}
```

**Náklady:** $0 (included in Upstash Redis)

---

### **7. EMAIL ALERTS PRO HIGH COSTS**

**Automatické notifikace:**

```typescript
// lib/alerts.ts
import { Resend } from "resend";

const resend = new Resend(process.env.RESEND_API_KEY);

export const checkDailyCosts = async () => {
  // Get today's costs
  const { data } = await supabase.rpc("get_daily_costs");
  const today = data[0];

  // Thresholds
  const DAILY_WARNING = 10;   // $10/day
  const DAILY_CRITICAL = 50;  // $50/day

  if (today.total_cost >= DAILY_CRITICAL) {
    // CRITICAL: Disable API
    await disableAPI();

    await resend.emails.send({
      from: "alerts@fleurdin.cz",
      to: "admin@fleurdin.cz",
      subject: "🚨 CRITICAL: API vypnuto - vysoké náklady!",
      html: `
        <h1>API bylo automaticky vypnuto</h1>
        <p>Dnešní náklady: <strong>$${today.total_cost}</strong></p>
        <p>Limit: $${DAILY_CRITICAL}</p>
        <p>Requestů: ${today.total_requests}</p>
      `
    });
  } else if (today.total_cost >= DAILY_WARNING) {
    // WARNING: Alert only
    await resend.emails.send({
      from: "alerts@fleurdin.cz",
      to: "admin@fleurdin.cz",
      subject: "⚠️ Varování: Vysoké denní náklady",
      html: `
        <h1>Denní náklady jsou vysoké</h1>
        <p>Dnešní náklady: <strong>$${today.total_cost}</strong></p>
        <p>Warning threshold: $${DAILY_WARNING}</p>
        <p>Critical threshold: $${DAILY_CRITICAL}</p>
      `
    });
  }
};

const disableAPI = async () => {
  // Set flag in DB
  await supabase.from("system_config").update({
    api_enabled: false,
    disabled_reason: "Daily cost limit exceeded"
  });
};
```

**Cron job (Vercel):**

```typescript
// app/api/cron/check-costs/route.ts
import { checkDailyCosts } from "@/lib/alerts";

export async function GET(req: NextRequest) {
  // Verify cron secret
  if (req.headers.get("authorization") !== `Bearer ${process.env.CRON_SECRET}`) {
    return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
  }

  await checkDailyCosts();

  return NextResponse.json({ success: true });
}
```

**vercel.json:**

```json
{
  "crons": [{
    "path": "/api/cron/check-costs",
    "schedule": "0 * * * *"  // Každou hodinu
  }]
}
```

**Náklady:**
- Resend: $0 (100 emails/měsíc free)
- Vercel Cron: $0 (included in Hobby plan)

---

## 📊 SECURITY SUMMARY

### **MVP (MUST-HAVE):**

| Feature | Tech | Cost/měsíc | Priority |
|---|---|---|---|
| **Rate Limiting** | Upstash Redis | $0-5 | ⭐⭐⭐ |
| **Input Validation** | Custom code | $0 | ⭐⭐⭐ |
| **HF Auto-pause** | HuggingFace | $0 (savings) | ⭐⭐⭐ |
| **Cost Tracking** | Supabase | $0 | ⭐⭐⭐ |

**Total MVP cost:** $0-5/měsíc

---

### **LAUNCH (SHOULD-HAVE):**

| Feature | Tech | Cost/měsíc | Priority |
|---|---|---|---|
| **CAPTCHA** | Google reCAPTCHA | $0 | ⭐⭐ |
| **IP Blacklisting** | Upstash Redis | $0 | ⭐⭐ |
| **Email Alerts** | Resend | $0 | ⭐⭐ |

**Total LAUNCH cost:** $0/měsíc

---

### **CELKOVÉ NÁKLADY:**

```
MVP + LAUNCH Security: $0-5/měsíc
Infrastructure: $95-125/měsíc
────────────────────────────────
TOTAL: $95-130/měsíc
```

**Bez security:** Riziko $500+ měsíčně při attacku

---

## 🎯 IMPLEMENTATION CHECKLIST

### **Pre-Launch (2-3 dny práce):**

- [ ] Setup Upstash Redis
  - [ ] Create database
  - [ ] Add credentials to `.env`

- [ ] Implement rate limiting
  - [ ] Create `/lib/ratelimit.ts`
  - [ ] Add to `/app/api/chat/route.ts`
  - [ ] Test: Try 11 requests in 1 minute

- [ ] Implement input validation
  - [ ] Create `/lib/validation.ts`
  - [ ] Add to chat endpoint
  - [ ] Test: Send spam, XSS, long message

- [ ] Configure HuggingFace auto-pause
  - [ ] Set min_replicas: 0
  - [ ] Set idle_timeout: 300s
  - [ ] Test: Wait 5 min, check if paused

- [ ] Setup cost tracking
  - [ ] Create Supabase table
  - [ ] Implement tracking function
  - [ ] Create simple dashboard

### **Launch Week:**

- [ ] Add CAPTCHA
  - [ ] Setup Google reCAPTCHA
  - [ ] Add to frontend
  - [ ] Add backend validation

- [ ] Implement IP blacklisting
  - [ ] Create blacklist functions
  - [ ] Add auto-ban logic
  - [ ] Test: Trigger 5 violations

- [ ] Setup email alerts
  - [ ] Setup Resend account
  - [ ] Create alert function
  - [ ] Add Vercel cron job
  - [ ] Test: Manually trigger alert

---

## 📚 RESOURCES

- **Upstash Redis:** https://upstash.com
- **reCAPTCHA:** https://www.google.com/recaptcha
- **Resend:** https://resend.com
- **HuggingFace Inference:** https://huggingface.co/docs/inference-endpoints

---

**Vytvořeno:** 2025-01-30
**Pro:** Fleurdin AI Security
**Autor:** [@TomasBo](https://huggingface.co/TomasBo)
