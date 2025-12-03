-- FLEURDIN AI - OPRAVA RPC FUNKCE
-- ==================================
-- Opravuje match_chunks() funkci - vrací 'name' místo neexistujícího 'entity_name'

-- 1. Nejdřív smazat starou funkci
DROP FUNCTION IF EXISTS match_chunks(vector(384), float, int, text, text);

-- 2. Vytvořit novou s opravou
CREATE OR REPLACE FUNCTION match_chunks(
  query_embedding vector(384),
  match_threshold float,
  match_count int,
  filter_tier text DEFAULT NULL,
  filter_type text DEFAULT NULL
)
RETURNS TABLE (
  id text,
  type text,
  entity_type text,
  content_type text,
  tier text,
  name text,                    -- ✅ Opraveno z 'entity_name'
  text text,
  part int,
  total_parts int,
  chunk_size int,
  metadata jsonb,
  similarity float
)
LANGUAGE plpgsql
AS $$
BEGIN
  RETURN QUERY
  SELECT
    knowledge_chunks.id,
    knowledge_chunks.type,
    knowledge_chunks.entity_type,
    knowledge_chunks.content_type,
    knowledge_chunks.tier,
    knowledge_chunks.name,       -- ✅ Opraveno z 'entity_name'
    knowledge_chunks.text,
    knowledge_chunks.part,
    knowledge_chunks.total_parts,
    knowledge_chunks.chunk_size,
    knowledge_chunks.metadata,
    1 - (knowledge_chunks.embedding <=> query_embedding) AS similarity
  FROM knowledge_chunks
  WHERE
    (filter_tier IS NULL OR knowledge_chunks.tier = filter_tier)
    AND (filter_type IS NULL OR knowledge_chunks.type = filter_type)
    AND 1 - (knowledge_chunks.embedding <=> query_embedding) > match_threshold
  ORDER BY knowledge_chunks.embedding <=> query_embedding
  LIMIT match_count;
END;
$$;
