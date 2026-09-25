-- Inspect how exercise embeddings relate to each other (Step 8).
-- Run from the project folder:
--   docker compose exec -T db psql -U postgres -d ragmotion < db/queries/embedding_neighbors.sql
-- Similarity = 1 - cosine distance (<=>). Higher = more alike.

-- 1. Hand-picked pairs a coach would expect to be close or far apart.
SELECT a.name AS exercise_a, b.name AS exercise_b,
       round((1 - (a.embedding <=> b.embedding))::numeric, 3) AS similarity
FROM (VALUES
  ('bulgarian-split-squat', 'dumbbell-reverse-lunge'),
  ('bulgarian-split-squat', 'push-up'),
  ('dumbbell-romanian-deadlift', 'single-leg-romanian-deadlift'),
  ('dumbbell-romanian-deadlift', 'kettlebell-swing'),
  ('box-jump', 'broad-jump'),
  ('box-jump', 'dead-bug'),
  ('push-up', 'dumbbell-overhead-press'),
  ('band-pull-apart', 'one-arm-dumbbell-row')
) AS p(x, y)
JOIN exercise a ON a.slug = p.x
JOIN exercise b ON b.slug = p.y
ORDER BY similarity DESC;

-- 2. Each exercise's three nearest neighbors.
-- LATERAL runs the inner query once per exercise, so each row gets its own top 3.
SELECT e.name AS exercise,
       string_agg(n.name || ' (' || n.sim || ')', ',  ' ORDER BY n.sim DESC) AS three_nearest
FROM exercise e
CROSS JOIN LATERAL (
  SELECT o.name, round((1 - (e.embedding <=> o.embedding))::numeric, 2) AS sim
  FROM exercise o
  WHERE o.slug <> e.slug
  ORDER BY e.embedding <=> o.embedding
  LIMIT 3
) n
GROUP BY e.name, e.body_region
ORDER BY e.body_region, e.name;
