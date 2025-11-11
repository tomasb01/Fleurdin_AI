-- =============================================================================
-- FIX: MATCH_CONTENT_TEXT FUNCTION
-- =============================================================================
-- This function accepts TEXT instead of VECTOR(384) for the embedding
-- Fixes the ambiguous column reference error by using table aliases
-- =============================================================================

CREATE OR REPLACE FUNCTION match_content_text(
  query_embedding_text TEXT,
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
LANGUAGE plpgsql STABLE
AS $$
DECLARE
  query_embedding VECTOR(384);
BEGIN
  -- Convert TEXT to VECTOR
  query_embedding := query_embedding_text::VECTOR(384);
  
  -- Perform vector search with explicit table aliases to avoid ambiguity
  RETURN QUERY
  SELECT
    ci.id,                                                    -- Use ci.id instead of just id
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
END;
$$;
