-- =============================================================================
-- FLEURDIN AI - SUPABASE DATABASE SCHEMA
-- =============================================================================
-- Podporuje: Esenciální oleje, bylinky (kniha+audio), budoucí vitamíny
-- Verzování: V1.0 (2025)
-- =============================================================================

-- Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- =============================================================================
-- 1. CATEGORIES TABLE (Kategorie produktů)
-- =============================================================================
CREATE TABLE categories (
  id BIGSERIAL PRIMARY KEY,
  name TEXT NOT NULL UNIQUE,  -- 'essential_oils', 'herbs', 'vitamins'
  display_name TEXT NOT NULL,  -- 'Esenciální oleje', 'Bylinky', 'Vitamíny'
  description TEXT,
  icon TEXT,  -- emoji nebo icon name
  created_at TIMESTAMP DEFAULT NOW()
);

-- Insert initial categories
INSERT INTO categories (name, display_name, description, icon) VALUES
  ('essential_oils', 'Esenciální oleje', 'Expertní poradenství o esenciálních olejích a aromaterapii', '🌿'),
  ('herbs', 'Bylinky', 'Informace o léčivých bylinkách z knih a audionahrávek', '🌱'),
  ('vitamins', 'Vitamíny a suplementy', 'Informace o vitamínech a doplňcích stravy', '💊');

-- =============================================================================
-- 2. CONTENT_ITEMS TABLE (Hlavní obsah - oleje, bylinky, vitamíny)
-- =============================================================================
CREATE TABLE content_items (
  id BIGSERIAL PRIMARY KEY,
  category_id BIGINT REFERENCES categories(id) ON DELETE CASCADE,

  -- Basic info
  name TEXT NOT NULL,  -- 'Levandule', 'Heřmánek'
  latin_name TEXT,     -- 'Lavandula angustifolia'

  -- Structured data (JSON for flexibility)
  effects_body JSONB,       -- {"general": [...], "digestion": [...], "skin": [...]}
  effects_psyche JSONB,      -- {"calming": true, "stress_relief": true}
  usage_instructions JSONB,  -- {"diffuser": "3 drops", "topical": "2 drops with carrier oil"}

  -- Metadata
  frequency INTEGER,         -- For essential oils (Hz)
  safety_info TEXT,          -- Kontraindikace, varování

  -- For herbs: Book/Audio references
  book_references JSONB,     -- [{"page": 45, "chapter": "Léčivé byliny", "quote": "..."}]
  audio_references JSONB,    -- [{"file": "byliny_01.mp3", "timestamp": "12:34"}]

  -- Tier system (free vs premium)
  tier TEXT DEFAULT 'free' CHECK (tier IN ('free', 'premium')),

  -- Vector embedding for RAG
  embedding VECTOR(384),  -- sentence-transformers embedding dimension

  -- Timestamps
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW(),

  -- Indexes
  CONSTRAINT unique_name_per_category UNIQUE(category_id, name)
);

-- Indexes for performance
CREATE INDEX idx_content_category ON content_items(category_id);
CREATE INDEX idx_content_tier ON content_items(tier);
CREATE INDEX idx_content_embedding ON content_items USING ivfflat (embedding vector_cosine_ops);

-- =============================================================================
-- 3. RECIPES TABLE (Recepty pro premium uživatele)
-- =============================================================================
CREATE TABLE recipes (
  id BIGSERIAL PRIMARY KEY,

  -- Recipe info
  title TEXT NOT NULL,
  description TEXT,
  condition TEXT NOT NULL,  -- 'nespavost', 'bolest hlavy', 'stres'

  -- Ingredients (multiple items)
  ingredients JSONB NOT NULL,  -- [{"item_id": 1, "drops": 3}, {"item_id": 2, "drops": 2}]

  -- Instructions
  usage_method TEXT,  -- 'diffuser', 'topical', 'bath'
  instructions TEXT NOT NULL,

  -- Metadata
  category_id BIGINT REFERENCES categories(id),
  tier TEXT DEFAULT 'premium' CHECK (tier IN ('free', 'premium')),

  -- Vector embedding (for recipe search)
  embedding VECTOR(384),

  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_recipes_category ON recipes(category_id);
CREATE INDEX idx_recipes_tier ON recipes(tier);
CREATE INDEX idx_recipes_embedding ON recipes USING ivfflat (embedding vector_cosine_ops);

-- =============================================================================
-- 4. USERS TABLE (Auth + Tier management)
-- =============================================================================
CREATE TABLE users (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  email TEXT UNIQUE,
  tier TEXT DEFAULT 'free' CHECK (tier IN ('free', 'premium')),

  -- Stripe integration
  stripe_customer_id TEXT,
  subscription_status TEXT,  -- 'active', 'canceled', 'past_due'
  subscription_end_date TIMESTAMP,

  -- Preferences
  preferences JSONB DEFAULT '{}',

  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_tier ON users(tier);

-- =============================================================================
-- 5. CONVERSATIONS TABLE (Chat history)
-- =============================================================================
CREATE TABLE conversations (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID REFERENCES users(id) ON DELETE CASCADE,
  session_id TEXT NOT NULL,  -- For anonymous users

  messages JSONB NOT NULL,  -- [{"role": "user", "content": "..."}, {"role": "assistant", "content": "..."}]

  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_conversations_user ON conversations(user_id);
CREATE INDEX idx_conversations_session ON conversations(session_id);

-- =============================================================================
-- 6. USAGE TRACKING TABLE (Cost monitoring)
-- =============================================================================
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

CREATE INDEX idx_usage_user_timestamp ON usage_tracking(user_id, timestamp);
CREATE INDEX idx_usage_session_timestamp ON usage_tracking(session_id, timestamp);

-- =============================================================================
-- 7. VECTOR SEARCH FUNCTION
-- =============================================================================
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
LANGUAGE SQL STABLE
AS $$
  SELECT
    ci.id,
    c.name as category_name,
    ci.name,
    ci.latin_name,
    ci.effects_body,
    ci.effects_psyche,
    ci.usage_instructions,
    ci.frequency,
    ci.book_references,
    ci.audio_references,
    1 - (ci.embedding <=> query_embedding) AS similarity
  FROM content_items ci
  JOIN categories c ON ci.category_id = c.id
  WHERE
    1 - (ci.embedding <=> query_embedding) > match_threshold
    AND (ci.tier = 'free' OR user_tier = 'premium')
    AND (category_filter IS NULL OR c.name = category_filter)
  ORDER BY similarity DESC
  LIMIT match_count;
$$;

-- =============================================================================
-- 8. RECIPE SEARCH FUNCTION
-- =============================================================================
CREATE OR REPLACE FUNCTION match_recipes(
  query_embedding VECTOR(384),
  match_threshold FLOAT DEFAULT 0.7,
  match_count INT DEFAULT 3,
  user_tier TEXT DEFAULT 'free'
)
RETURNS TABLE (
  id BIGINT,
  title TEXT,
  description TEXT,
  condition TEXT,
  ingredients JSONB,
  instructions TEXT,
  similarity FLOAT
)
LANGUAGE SQL STABLE
AS $$
  SELECT
    id,
    title,
    description,
    condition,
    ingredients,
    instructions,
    1 - (embedding <=> query_embedding) AS similarity
  FROM recipes
  WHERE
    1 - (embedding <=> query_embedding) > match_threshold
    AND (tier = 'free' OR user_tier = 'premium')
  ORDER BY similarity DESC
  LIMIT match_count;
$$;

-- =============================================================================
-- 9. HELPER FUNCTIONS
-- =============================================================================

-- Get daily costs
CREATE OR REPLACE FUNCTION get_daily_costs()
RETURNS TABLE (
  date DATE,
  total_requests BIGINT,
  total_cost DECIMAL(10, 2)
)
LANGUAGE SQL STABLE
AS $$
  SELECT
    DATE(timestamp) as date,
    COUNT(*) as total_requests,
    SUM(cost_estimate)::DECIMAL(10, 2) as total_cost
  FROM usage_tracking
  WHERE timestamp > NOW() - INTERVAL '30 days'
  GROUP BY DATE(timestamp)
  ORDER BY date DESC;
$$;

-- Update timestamp trigger
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply trigger to tables
CREATE TRIGGER update_content_items_updated_at BEFORE UPDATE ON content_items
  FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
  FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_conversations_updated_at BEFORE UPDATE ON conversations
  FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- =============================================================================
-- 10. ROW LEVEL SECURITY (RLS) - Optional for MVP
-- =============================================================================
-- TODO: Enable RLS after MVP testing
-- ALTER TABLE users ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE conversations ENABLE ROW LEVEL SECURITY;

-- =============================================================================
-- DONE! 🎉
-- =============================================================================
-- Next steps:
-- 1. Run this SQL in Supabase SQL Editor
-- 2. Generate embeddings for content_items
-- 3. Test vector search
-- =============================================================================
