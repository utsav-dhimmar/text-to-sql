-- ============================================================
-- NIFTY 500 — AUTH DATABASE SETUP (Updated Schema)
-- Tables: users, datasets, audit_logs, chat_history
--
-- Command:
--   psql -U postgres -d nifty500 -f auth_db_setup_v2.sql
-- ============================================================


-- ── 1. Extensions ────────────────────────────────────────────
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";


-- ── 2. Drop existing tables & types ─────────────────────────
DROP TABLE IF EXISTS chat_history;
DROP TABLE IF EXISTS audit_logs;
DROP TABLE IF EXISTS datasets;
DROP TABLE IF EXISTS users;

DROP TYPE IF EXISTS user_role;
DROP TYPE IF EXISTS user_status;
DROP TYPE IF EXISTS dataset_status;


-- ── 3. ENUM types ────────────────────────────────────────────
CREATE TYPE user_role      AS ENUM ('user', 'admin', 'superadmin');
CREATE TYPE user_status    AS ENUM ('active', 'banned', 'deleted');
CREATE TYPE dataset_status AS ENUM ('processing', 'ready', 'error');


-- ── 4. Tables ────────────────────────────────────────────────

CREATE TABLE users (
    id            UUID        PRIMARY KEY DEFAULT uuid_generate_v4(),
    email         VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role          user_role   NOT NULL DEFAULT 'user',
    status        user_status NOT NULL DEFAULT 'active',
    created_at    TIMESTAMP   DEFAULT NOW()
);

CREATE TABLE datasets (
    id          UUID           PRIMARY KEY DEFAULT uuid_generate_v4(),
    name        VARCHAR(255)   NOT NULL,
    source      VARCHAR(50),
    uploaded_by UUID           REFERENCES users(id) ON DELETE SET NULL,
    table_name  VARCHAR(100)   UNIQUE,
    row_count   INTEGER,
    status      dataset_status DEFAULT 'processing',
    created_at  TIMESTAMP      DEFAULT NOW()
);

CREATE TABLE audit_logs (
    id         UUID         PRIMARY KEY DEFAULT uuid_generate_v4(),
    actor_id   UUID         NOT NULL REFERENCES users(id) ON DELETE RESTRICT,
    action     VARCHAR(100) NOT NULL,
    target_id  UUID         REFERENCES users(id) ON DELETE SET NULL,  -- nullable
    created_at TIMESTAMP    DEFAULT NOW()
);

CREATE TABLE chat_history (
    id             UUID      PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id        UUID      REFERENCES users(id) ON DELETE CASCADE,
    human_query    TEXT      NOT NULL,
    sql_generated  TEXT,
    result_summary TEXT,
    created_at     TIMESTAMP DEFAULT NOW()
);


-- ── 5. Indexes ───────────────────────────────────────────────
CREATE INDEX idx_users_email          ON users(email);
CREATE INDEX idx_users_role           ON users(role);
CREATE INDEX idx_users_status         ON users(status);
CREATE INDEX idx_datasets_uploaded_by ON datasets(uploaded_by);
CREATE INDEX idx_audit_actor          ON audit_logs(actor_id);
CREATE INDEX idx_audit_target         ON audit_logs(target_id);
CREATE INDEX idx_chat_user            ON chat_history(user_id);
CREATE INDEX idx_chat_created         ON chat_history(created_at);


-- ── 6. Seed superadmin ───────────────────────────────────────
INSERT INTO users (email, password_hash, role, status)
VALUES (
    'admin@nifty500.com',
    '$2b$12$KIXo6J4Z1v7zLQkNz3MBOeQGQn5F9VqY8lR2pX4jA7uH3sD6mCw1G',
    'superadmin',
    'active'
);

-- ── 7. Register Nifty 500 dataset ────────────────────────────
INSERT INTO datasets (name, source, table_name, row_count, status)
VALUES (
    'Nifty 500 Quarterly Results FY2025',
    'kaggle',
    'company_financials',
    2004,
    'ready'
);


-- ── 8. Verify ────────────────────────────────────────────────
SELECT table_name, 
       (SELECT COUNT(*) FROM information_schema.columns
        WHERE table_name = t.table_name
        AND table_schema = 'public') AS column_count
FROM (VALUES 
    ('users'), 
    ('datasets'), 
    ('audit_logs'), 
    ('chat_history')
) AS t(table_name);

-- Expected:
--  users         | 6
--  datasets      | 8
--  audit_logs    | 5
--  chat_history  | 6