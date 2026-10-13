-- Phase 0: core foundation.
-- Conventions (see docs/DATABASE.md):
--   * primary keys are UUID strings, timestamps are UTC ISO-8601 TEXT ('...Z')
--   * polymorphic references use (entity_type, entity_id) and have no FK;
--     the service layer cleans them up when the referenced row is purged
--   * the FTS tokenizer placeholder is filled in by the migrator
--     (trigram when SQLite supports it, otherwise unicode61)

CREATE TABLE app_settings (
    key         TEXT PRIMARY KEY,
    value       TEXT NOT NULL CHECK (json_valid(value)),
    updated_at  TEXT NOT NULL
);

-- ---------------------------------------------------------------- Wiki
CREATE TABLE wiki_pages (
    page_id           TEXT PRIMARY KEY,
    title             TEXT NOT NULL,
    folder            TEXT NOT NULL DEFAULT '',      -- '/'-separated path, '' = root
    content           TEXT NOT NULL DEFAULT '',
    summary           TEXT,                          -- AI summary (later phase)
    source_type       TEXT NOT NULL DEFAULT 'user',  -- user | import_file | import_chat | ai_draft
    source_ref        TEXT,                          -- e.g. original file name
    current_revision  INTEGER NOT NULL DEFAULT 1,
    status            TEXT NOT NULL DEFAULT 'active' CHECK (status IN ('active', 'deleted')),
    created_at        TEXT NOT NULL,
    updated_at        TEXT NOT NULL,
    deleted_at        TEXT
);
CREATE INDEX ix_wiki_pages_status_updated ON wiki_pages (status, updated_at DESC);
CREATE INDEX ix_wiki_pages_folder ON wiki_pages (folder);
CREATE INDEX ix_wiki_pages_title ON wiki_pages (title COLLATE NOCASE);

-- Every save creates a full snapshot; pages are never overwritten without history.
CREATE TABLE wiki_revisions (
    revision_id      TEXT PRIMARY KEY,
    page_id          TEXT NOT NULL REFERENCES wiki_pages (page_id) ON DELETE CASCADE,
    revision_number  INTEGER NOT NULL,
    title            TEXT NOT NULL,
    folder           TEXT NOT NULL,
    content          TEXT NOT NULL,
    content_hash     TEXT NOT NULL,
    change_note      TEXT,
    author           TEXT NOT NULL DEFAULT 'user',   -- user | ai | import | system
    created_at       TEXT NOT NULL,
    UNIQUE (page_id, revision_number)
);

-- Retrieval units for search and RAG (and, later, embeddings keyed by chunk_id).
CREATE TABLE wiki_chunks (
    chunk_id         TEXT PRIMARY KEY,
    page_id          TEXT NOT NULL REFERENCES wiki_pages (page_id) ON DELETE CASCADE,
    revision_number  INTEGER NOT NULL,
    chunk_index      INTEGER NOT NULL,
    heading          TEXT NOT NULL DEFAULT '',
    content          TEXT NOT NULL,
    char_start       INTEGER NOT NULL,
    char_end         INTEGER NOT NULL,
    content_hash     TEXT NOT NULL,
    UNIQUE (page_id, chunk_index)
);

-- ---------------------------------------------------------------- Tags
CREATE TABLE tags (
    tag_id      TEXT PRIMARY KEY,
    name        TEXT NOT NULL COLLATE NOCASE UNIQUE,
    created_at  TEXT NOT NULL
);

CREATE TABLE entity_tags (
    tag_id       TEXT NOT NULL REFERENCES tags (tag_id) ON DELETE CASCADE,
    entity_type  TEXT NOT NULL,                     -- wiki_page | memory | project | task | chat_session
    entity_id    TEXT NOT NULL,
    created_at   TEXT NOT NULL,
    PRIMARY KEY (tag_id, entity_type, entity_id)
);
CREATE INDEX ix_entity_tags_entity ON entity_tags (entity_type, entity_id);

-- ---------------------------------------------------------------- Chat
-- Holds both conversations made in the app (origin='app') and, from Phase 3,
-- imported ones (origin='import'). started_at is when the conversation really
-- happened; created_at is when this database recorded it.
CREATE TABLE chat_sessions (
    session_id      TEXT PRIMARY KEY,
    title           TEXT NOT NULL,
    origin          TEXT NOT NULL DEFAULT 'app',    -- app | import
    source_service  TEXT,                           -- chatgpt | claude | generic (imports)
    external_id     TEXT,                           -- conversation id inside the export
    content_hash    TEXT,                           -- duplicate detection for imports
    model           TEXT,
    started_at      TEXT NOT NULL,
    created_at      TEXT NOT NULL,
    updated_at      TEXT NOT NULL,
    archived        INTEGER NOT NULL DEFAULT 0 CHECK (archived IN (0, 1))
);
CREATE INDEX ix_chat_sessions_updated ON chat_sessions (archived, updated_at DESC);
CREATE UNIQUE INDEX ux_chat_sessions_external
    ON chat_sessions (source_service, external_id) WHERE external_id IS NOT NULL;

CREATE TABLE chat_messages (
    message_id   TEXT PRIMARY KEY,
    session_id   TEXT NOT NULL REFERENCES chat_sessions (session_id) ON DELETE CASCADE,
    seq          INTEGER NOT NULL,
    role         TEXT NOT NULL CHECK (role IN ('user', 'assistant', 'system')),
    content      TEXT NOT NULL,
    model        TEXT,
    status       TEXT NOT NULL DEFAULT 'complete' CHECK (status IN ('complete', 'partial', 'error')),
    external_id  TEXT,
    created_at   TEXT NOT NULL,                     -- when the message was written (original time for imports)
    recorded_at  TEXT NOT NULL,                     -- when this database stored it
    metadata     TEXT NOT NULL DEFAULT '{}' CHECK (json_valid(metadata)),
    UNIQUE (session_id, seq)
);

-- ---------------------------------------------------------------- Provenance
-- "X was supported by / extracted from Y". Phase 0 uses it for the wiki
-- passages an assistant answer cited; later phases reuse it for memories.
CREATE TABLE source_references (
    reference_id  TEXT PRIMARY KEY,
    owner_type    TEXT NOT NULL,                    -- chat_message | memory | wiki_page | ...
    owner_id      TEXT NOT NULL,
    source_type   TEXT NOT NULL,                    -- wiki_chunk | wiki_page | chat_message | memory | file
    source_id     TEXT NOT NULL,
    relation      TEXT NOT NULL DEFAULT 'cited',    -- cited | extracted_from | derived_from
    quote         TEXT,                             -- passage as it was when referenced
    locator       TEXT NOT NULL DEFAULT '{}' CHECK (json_valid(locator)),
    rank          INTEGER,
    created_at    TEXT NOT NULL
);
CREATE INDEX ix_source_refs_owner ON source_references (owner_type, owner_id);
CREATE INDEX ix_source_refs_source ON source_references (source_type, source_id);

-- ---------------------------------------------------------------- Timeline
CREATE TABLE timeline_events (
    event_id     TEXT PRIMARY KEY,
    event_type   TEXT NOT NULL,
    title        TEXT NOT NULL,
    description  TEXT NOT NULL DEFAULT '',
    occurred_at  TEXT NOT NULL,                     -- when it actually happened
    recorded_at  TEXT NOT NULL,                     -- when the system recorded it
    source_type  TEXT,
    source_id    TEXT,
    project_id   TEXT,
    importance   INTEGER NOT NULL DEFAULT 0 CHECK (importance BETWEEN 0 AND 2),
    metadata     TEXT NOT NULL DEFAULT '{}' CHECK (json_valid(metadata))
);
CREATE INDEX ix_timeline_occurred ON timeline_events (occurred_at DESC);
CREATE INDEX ix_timeline_type_occurred ON timeline_events (event_type, occurred_at DESC);
CREATE INDEX ix_timeline_project_occurred ON timeline_events (project_id, occurred_at DESC);
CREATE INDEX ix_timeline_source ON timeline_events (source_type, source_id);

-- ---------------------------------------------------------------- Search
-- One full-text index for every searchable entity. Rows are written by the
-- service layer in the same transaction as the source row.
CREATE VIRTUAL TABLE search_index USING fts5 (
    title,
    body,
    entity_type UNINDEXED,
    entity_id UNINDEXED,
    chunk_id UNINDEXED,
    tokenize = '{{FTS_TOKENIZER}}'
);
