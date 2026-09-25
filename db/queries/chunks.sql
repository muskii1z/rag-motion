-- Inspect document chunks (Step 12).
-- Run from the project folder:
--   docker compose exec -T db psql -U postgres -d ragmotion < db/queries/chunks.sql

-- 1. Chunks per source, with size range.
SELECT source_id, source_type, count(*) AS chunks,
       min(word_count) AS min_words, round(avg(word_count)) AS avg_words, max(word_count) AS max_words
FROM document_chunk GROUP BY 1, 2 ORDER BY 1;

-- 2. The first line (location label) of every chunk from one chapter.
SELECT chunk_index, page_start || '-' || page_end AS pages, word_count,
       split_part(embed_text, E'\n', 1) AS label
FROM document_chunk
WHERE source_id = 'pag2' AND chapter LIKE 'Chapter 4.%'
ORDER BY chunk_index;
