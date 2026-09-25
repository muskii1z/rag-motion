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

    -- Voyage voyage-4-lite embedding of the exercise text (1024 numbers). Filled in Step 8.
    embedding        vector(1024),

    -- Which model produced `embedding`. Vectors from different models can't be compared,
    -- so after a model change this shows exactly which rows need re-embedding.
    embedding_model  text,

    created_at       timestamptz NOT NULL DEFAULT now()
);

-- ---- Changes to tables that already exist ----
-- CREATE TABLE IF NOT EXISTS skips existing tables, so new columns also need an ALTER.
-- Step 8: record which model made each embedding.
ALTER TABLE exercise ADD COLUMN IF NOT EXISTS embedding_model text;

-- ---- Step 12: document chunks ----
-- One row per passage cut from a source document or project note (see data/sources.toml).
-- Kept separate from `exercise`: exercises are structured records, chunks are passages of prose.
CREATE TABLE IF NOT EXISTS document_chunk (
    id             integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    -- Provenance: where this text came from and what we're allowed to do with it.
    source_id      text NOT NULL,                  -- id in data/sources.toml
    source_type    text NOT NULL CHECK (source_type IN ('document', 'notes')),
    source_title   text NOT NULL,
    source_url     text,
    license        text NOT NULL,
    license_group  text NOT NULL CHECK (license_group IN ('A', 'B', 'C')),  -- D is never ingested

    -- Position inside the source, for citations.
    chunk_index    integer NOT NULL,               -- order within the source
    chapter        text NOT NULL,
    headings       text[] NOT NULL DEFAULT '{}',   -- section headings this chunk covers
    page_start     integer,                        -- null for notes
    page_end       integer,

    -- The text. `text` is shown to the LLM and the user; `embed_text` adds the
    -- "title > chapter > sections" label and is exactly what gets embedded.
    text           text NOT NULL,
    embed_text     text NOT NULL,
    word_count     integer NOT NULL CHECK (word_count > 0),

    -- Which chunking method and settings produced this row, so variants can be compared.
    chunker        text NOT NULL,

    -- Filled in Step 13.
    embedding       vector(1024),
    embedding_model text,

    created_at     timestamptz NOT NULL DEFAULT now(),
    UNIQUE (source_id, chunker, chunk_index)
);
