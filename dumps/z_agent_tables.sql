-- Agent-side tables + sequence reset
-- Runs after the main dump (z_ sorts last alphabetically).
-- Safe to re-run: IF NOT EXISTS guards on every DDL statement.

SET client_encoding = 'UTF8';

-- ---------------------------------------------------------------------------
-- Enum types
-- ---------------------------------------------------------------------------

DO $$ BEGIN
    CREATE TYPE conversation_status AS ENUM ('active', 'archived', 'escalated');
EXCEPTION WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    CREATE TYPE message_role AS ENUM ('human', 'ai', 'tool', 'system');
EXCEPTION WHEN duplicate_object THEN null;
END $$;

-- ---------------------------------------------------------------------------
-- conversations
-- ---------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS conversations (
    id              BIGSERIAL PRIMARY KEY,
    session_id      TEXT        NOT NULL UNIQUE,
    user_id         TEXT        NOT NULL,
    status          conversation_status NOT NULL DEFAULT 'active',
    started_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    ended_at        TIMESTAMPTZ,
    primary_intent  TEXT,
    turn_count      INTEGER     NOT NULL DEFAULT 0
);

CREATE INDEX IF NOT EXISTS ix_conversations_session_id
    ON conversations (session_id);

CREATE INDEX IF NOT EXISTS ix_conversations_user_id
    ON conversations (user_id);

CREATE INDEX IF NOT EXISTS ix_conversations_user_started
    ON conversations (user_id, started_at);

-- ---------------------------------------------------------------------------
-- messages
-- ---------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS messages (
    id               BIGSERIAL PRIMARY KEY,
    conversation_id  BIGINT      NOT NULL
                         REFERENCES conversations (id) ON DELETE CASCADE,
    role             message_role NOT NULL,
    content          TEXT        NOT NULL,
    turn_index       INTEGER     NOT NULL,
    token_count      INTEGER,
    created_at       TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS ix_messages_conversation_id
    ON messages (conversation_id);

CREATE INDEX IF NOT EXISTS ix_messages_conv_turn
    ON messages (conversation_id, turn_index);

-- ---------------------------------------------------------------------------
-- conversation_summaries
-- ---------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS conversation_summaries (
    id                    BIGSERIAL PRIMARY KEY,
    conversation_id       BIGINT  NOT NULL
                              REFERENCES conversations (id) ON DELETE CASCADE,
    summary_text          TEXT    NOT NULL,
    covered_up_to_turn    INTEGER NOT NULL,
    messages_token_count  INTEGER,
    summary_token_count   INTEGER,
    created_at            TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS ix_summaries_conversation_id
    ON conversation_summaries (conversation_id);

CREATE INDEX IF NOT EXISTS ix_summaries_conv_turn
    ON conversation_summaries (conversation_id, covered_up_to_turn);

-- ---------------------------------------------------------------------------
-- Sequence reset
--
-- pg_dump restores data rows but leaves sequences at their bootstrap value
-- (usually 1) instead of advancing them past the highest restored ID.
-- Without this fix the first INSERT after a fresh init crashes with a
-- duplicate-key violation.
--
-- This block iterates every SERIAL/BIGSERIAL column in the public schema and
-- calls setval() so each sequence continues from max(existing_id) + 1.
-- It is a no-op when a table is empty (COALESCE defaults to 1).
-- ---------------------------------------------------------------------------

DO $$
DECLARE
    r RECORD;
BEGIN
    FOR r IN
        SELECT
            s.relname                                        AS seq_name,
            t.relname                                        AS table_name,
            a.attname                                        AS col_name
        FROM pg_class s
        JOIN pg_depend d  ON d.objid      = s.oid
        JOIN pg_class t   ON t.oid        = d.refobjid
        JOIN pg_attribute a ON a.attrelid = t.oid
                           AND a.attnum   = d.refobjsubid
        JOIN pg_namespace n ON n.oid      = t.relnamespace
        WHERE s.relkind = 'S'           -- sequences only
          AND n.nspname = 'public'
    LOOP
        EXECUTE format(
            'SELECT setval(%L, COALESCE((SELECT MAX(%I) FROM %I), 1), true)',
            r.seq_name, r.col_name, r.table_name
        );
    END LOOP;
END $$;
