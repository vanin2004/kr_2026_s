-- ============================================================
-- Database Schema for Tutor-Student Platform
-- Generated from SQLAlchemy ORM models
-- Target: PostgreSQL
-- ============================================================

-- ------------------------------------------------------------
-- ENUM types
-- ------------------------------------------------------------

CREATE TYPE user_role AS ENUM ('tutor', 'student');
CREATE TYPE lesson_status AS ENUM ('planned', 'completed', 'cancelled');
CREATE TYPE application_status AS ENUM ('pending', 'accepted', 'rejected');
CREATE TYPE result_type AS ENUM ('initial_test', 'control_test');
CREATE TYPE device_platform AS ENUM ('android', 'ios');

-- ------------------------------------------------------------
-- 1. subjects
-- ------------------------------------------------------------

CREATE TABLE subjects (
    id  UUID  PRIMARY KEY  DEFAULT gen_random_uuid(),
    name VARCHAR(100) NOT NULL UNIQUE
);

-- ------------------------------------------------------------
-- 2. tags
-- ------------------------------------------------------------

CREATE TABLE tags (
    id  UUID  PRIMARY KEY  DEFAULT gen_random_uuid(),
    name VARCHAR(100) NOT NULL UNIQUE
);

-- ------------------------------------------------------------
-- 3. users
-- ------------------------------------------------------------

CREATE TABLE users (
    id         UUID        PRIMARY KEY,
    email      VARCHAR(255) NOT NULL UNIQUE,
    role       user_role    NOT NULL,
    created_at TIMESTAMPTZ  NOT NULL DEFAULT NOW()
);

-- ------------------------------------------------------------
-- 4. tutor_profiles
-- ------------------------------------------------------------

CREATE TABLE tutor_profiles (
    user_id              UUID         PRIMARY KEY
                       REFERENCES users(id) ON DELETE CASCADE,
    full_name            VARCHAR(255),
    photo_url            VARCHAR(500),
    education            TEXT,
    subject_id           UUID         REFERENCES subjects(id),
    hourly_rate          INTEGER,
    experience_years     INTEGER      NOT NULL DEFAULT 0,
    is_verified          BOOLEAN      NOT NULL DEFAULT FALSE,
    student_count        INTEGER      NOT NULL DEFAULT 0,
    rating_efficiency    NUMERIC(4,3),
    rating_communication NUMERIC(4,3),
    rating_expertise     NUMERIC(4,3),
    rating_responsiveness NUMERIC(4,3),
    is_new_boost         BOOLEAN      NOT NULL DEFAULT TRUE
);

-- ------------------------------------------------------------
-- 5. student_profiles
-- ------------------------------------------------------------

CREATE TABLE student_profiles (
    user_id       UUID   PRIMARY KEY
                  REFERENCES users(id) ON DELETE CASCADE,
    full_name     VARCHAR(255),
    photo_url     VARCHAR(500),
    search_weights JSONB NOT NULL
        DEFAULT '{"k1_effectiveness": 0.30, "k2_communication": 0.15, "k3_expertise": 0.20, "k4_responsiveness": 0.15, "k5_tags": 0.20}'
);

-- ------------------------------------------------------------
-- 6. tutor_tags  (M:N — users ⇉ tags)
-- ------------------------------------------------------------

CREATE TABLE tutor_tags (
    tutor_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    tag_id   UUID NOT NULL REFERENCES tags(id)   ON DELETE CASCADE,
    PRIMARY KEY (tutor_id, tag_id)
);

-- ------------------------------------------------------------
-- 7. student_preferred_tags  (M:N — users ⇉ tags)
-- ------------------------------------------------------------

CREATE TABLE student_preferred_tags (
    student_id  UUID    NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    tag_id      UUID    NOT NULL REFERENCES tags(id)   ON DELETE CASCADE,
    is_required BOOLEAN NOT NULL DEFAULT FALSE,
    PRIMARY KEY (student_id, tag_id)
);

-- ------------------------------------------------------------
-- 8. tutor_certifications
-- ------------------------------------------------------------

CREATE TABLE tutor_certifications (
    id          INTEGER      GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    tutor_id    UUID         NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title       VARCHAR(255) NOT NULL,
    file_url    VARCHAR(500) NOT NULL,
    is_verified BOOLEAN      NOT NULL DEFAULT FALSE,
    created_at  TIMESTAMPTZ  NOT NULL DEFAULT NOW()
);

-- ------------------------------------------------------------
-- 9. schedules
-- ------------------------------------------------------------

CREATE TABLE schedules (
    id            INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    tutor_id      UUID    NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    day_of_week   INTEGER CHECK (day_of_week BETWEEN 1 AND 7),
    specific_date DATE,
    start_time    TIME    NOT NULL,
    end_time      TIME    NOT NULL,

    CONSTRAINT schedule_type_check CHECK (
        (day_of_week IS NOT NULL AND specific_date IS NULL) OR
        (day_of_week IS NULL AND specific_date IS NOT NULL)
    )
);

-- ------------------------------------------------------------
-- 10. lessons
-- ------------------------------------------------------------

CREATE TABLE lessons (
    id            UUID          PRIMARY KEY DEFAULT gen_random_uuid(),
    student_id    UUID          NOT NULL REFERENCES users(id),
    tutor_id      UUID          NOT NULL REFERENCES users(id),
    start_datetime TIMESTAMPTZ  NOT NULL,
    end_datetime   TIMESTAMPTZ  NOT NULL,
    status        lesson_status NOT NULL DEFAULT 'planned',
    meeting_link  VARCHAR(500)
);

CREATE INDEX lessons_start_idx   ON lessons (start_datetime);
CREATE INDEX lessons_tutor_idx   ON lessons (tutor_id);
CREATE INDEX lessons_student_idx ON lessons (student_id);

-- ------------------------------------------------------------
-- 11. applications
-- ------------------------------------------------------------

CREATE TABLE applications (
    id            UUID               PRIMARY KEY DEFAULT gen_random_uuid(),
    student_id    UUID               NOT NULL REFERENCES users(id),
    tutor_id      UUID               NOT NULL REFERENCES users(id),
    status        application_status NOT NULL DEFAULT 'pending',
    created_at    TIMESTAMPTZ         NOT NULL DEFAULT NOW(),
    responded_at  TIMESTAMPTZ,
    UNIQUE (student_id, tutor_id)
);

-- ------------------------------------------------------------
-- 12. chats
-- ------------------------------------------------------------

CREATE TABLE chats (
    id             UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    application_id UUID NOT NULL UNIQUE REFERENCES applications(id),
    created_at     TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- ------------------------------------------------------------
-- 13. messages
-- ------------------------------------------------------------

CREATE TABLE messages (
    id         UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    chat_id    UUID        NOT NULL REFERENCES chats(id) ON DELETE CASCADE,
    sender_id  UUID        NOT NULL REFERENCES users(id),
    text       TEXT        NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    is_read    BOOLEAN     NOT NULL DEFAULT FALSE
);

CREATE INDEX messages_chat_idx ON messages (chat_id, created_at);

-- ------------------------------------------------------------
-- 14. test_library
-- ------------------------------------------------------------

CREATE TABLE test_library (
    id             UUID         PRIMARY KEY DEFAULT gen_random_uuid(),
    subject_id     UUID         NOT NULL REFERENCES subjects(id),
    topic          VARCHAR(255) NOT NULL,
    questions_json JSONB        NOT NULL
);

-- ------------------------------------------------------------
-- 15. student_results
-- ------------------------------------------------------------

CREATE TABLE student_results (
    id           UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    student_id   UUID        NOT NULL REFERENCES users(id),
    tutor_id     UUID        NOT NULL REFERENCES users(id),
    test_id      UUID        NOT NULL REFERENCES test_library(id),
    type         result_type NOT NULL,
    score        NUMERIC(5,2),
    assigned_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    completed_at TIMESTAMPTZ
);

-- ------------------------------------------------------------
-- 16. reviews
-- ------------------------------------------------------------

CREATE TABLE reviews (
    id                  UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    student_id          UUID        NOT NULL REFERENCES users(id),
    tutor_id            UUID        NOT NULL REFERENCES users(id),
    lesson_id           UUID        REFERENCES lessons(id),
    communication_score INTEGER     NOT NULL CHECK (communication_score BETWEEN 1 AND 5),
    text                TEXT,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (student_id, lesson_id)
);

-- ------------------------------------------------------------
-- 17. device_tokens
-- ------------------------------------------------------------

CREATE TABLE device_tokens (
    id         INTEGER         GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    user_id    UUID            NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    token      VARCHAR(500)    NOT NULL UNIQUE,
    platform   device_platform NOT NULL,
    updated_at TIMESTAMPTZ     NOT NULL DEFAULT NOW()
);

CREATE INDEX device_tokens_user_idx ON device_tokens (user_id);
