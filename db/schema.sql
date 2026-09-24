-- rag-motion database schema
-- Apply with:
--   docker compose exec -T db psql -U postgres -d ragmotion -v ON_ERROR_STOP=1 < db/schema.sql
-- Safe to re-run: nothing is created twice.

-- pgvector: adds the vector column type and the <=> distance operator.
CREATE EXTENSION IF NOT EXISTS vector;

-- One row per exercise in the knowledge base.
CREATE TABLE IF NOT EXISTS exercise (
    -- Auto-numbered internal ID.
    id               integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    -- Stable human-readable ID (e.g. 'goblet-squat'). Citations and evals use this.
    slug             text NOT NULL UNIQUE,

    name             text NOT NULL,

    -- What the exercise is and what it trains. This is the main text we embed.
    description      text NOT NULL,

    -- How to perform it. Optional.
    instructions     text,

    -- ---- Metadata: columns we can filter on with plain SQL ----

    primary_muscles  text[] NOT NULL DEFAULT '{}',

    movement_pattern text NOT NULL
        CHECK (movement_pattern IN ('squat', 'hinge', 'lunge', 'push', 'pull', 'carry', 'core', 'jump')),

    -- A list, because some exercises need more than one item (e.g. dumbbell + bench).
    -- Must be non-empty and only use known equipment names.
    equipment        text[] NOT NULL
        CHECK (cardinality(equipment) > 0)
        CHECK (equipment <@ ARRAY['bodyweight', 'dumbbell', 'band', 'kettlebell', 'barbell', 'bench', 'box']),

    difficulty       text NOT NULL
        CHECK (difficulty IN ('beginner', 'intermediate', 'advanced')),

    laterality       text NOT NULL
        CHECK (laterality IN ('bilateral', 'unilateral')),

    body_region      text NOT NULL
        CHECK (body_region IN ('lower', 'upper', 'core', 'full')),

    -- ---- Provenance ----

    -- Where this information came from. Required: nothing enters without a source.
    source           text NOT NULL,

    -- ---- Semantic search ----

    -- Voyage voyage-4-lite embedding of the description (1024 numbers). Filled in Step 8.
    embedding        vector(1024),

    created_at       timestamptz NOT NULL DEFAULT now()
);
