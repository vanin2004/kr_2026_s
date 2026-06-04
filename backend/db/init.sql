-- Types
CREATE TYPE user_role AS ENUM ('tutor', 'student');
CREATE TYPE lesson_status AS ENUM ('planned', 'completed', 'cancelled');
CREATE TYPE application_status AS ENUM ('pending', 'accepted', 'rejected');
CREATE TYPE result_type AS ENUM ('initial_test', 'control_test');
CREATE TYPE device_platform AS ENUM ('android', 'ios');

-- 1. Справочники
CREATE TABLE subjects (
    id    SERIAL PRIMARY KEY,
    name  VARCHAR(100) NOT NULL UNIQUE
);

CREATE TABLE tags (
    id    SERIAL PRIMARY KEY,
    name  VARCHAR(100) NOT NULL UNIQUE
);

-- 2. Пользователи
CREATE TABLE users (
    id         UUID PRIMARY KEY,
    email      VARCHAR(255) NOT NULL UNIQUE,
    role       user_role    NOT NULL,
    created_at TIMESTAMPTZ  NOT NULL DEFAULT NOW()
);

-- 3. Профили
CREATE TABLE tutor_profiles (
    user_id               UUID PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
    full_name             VARCHAR(255),
    photo_url             VARCHAR(500),
    education             TEXT,
    subject_id            INT REFERENCES subjects(id),
    hourly_rate           INT,
    experience_years      INT DEFAULT 0,
    is_verified           BOOLEAN NOT NULL DEFAULT FALSE,
    student_count         INT NOT NULL DEFAULT 0,
    rating_efficiency     DECIMAL(4,3),
    rating_communication  DECIMAL(4,3),
    rating_expertise      DECIMAL(4,3),
    rating_responsiveness DECIMAL(4,3),
    is_new_boost          BOOLEAN NOT NULL DEFAULT TRUE
);

CREATE TABLE student_profiles (
    user_id    UUID PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
    full_name  VARCHAR(255),
    photo_url  VARCHAR(500),
    search_weights  JSONB NOT NULL DEFAULT '{
        "k1_effectiveness": 0.30,
        "k2_communication": 0.15,
        "k3_expertise":     0.20,
        "k4_responsiveness":0.15,
        "k5_tags":          0.20
    }'::jsonb
);

-- 4. Теги
CREATE TABLE tutor_tags (
    tutor_id  UUID REFERENCES users(id) ON DELETE CASCADE,
    tag_id    INT  REFERENCES tags(id)  ON DELETE CASCADE,
    PRIMARY KEY (tutor_id, tag_id)
);

CREATE TABLE student_preferred_tags (
    student_id  UUID REFERENCES users(id) ON DELETE CASCADE,
    tag_id      INT  REFERENCES tags(id)  ON DELETE CASCADE,
    is_required BOOLEAN NOT NULL DEFAULT FALSE,
    PRIMARY KEY (student_id, tag_id)
);

-- 5. Верификация
CREATE TABLE tutor_certifications (
    id           SERIAL PRIMARY KEY,
    tutor_id     UUID REFERENCES users(id) ON DELETE CASCADE,
    title        VARCHAR(255) NOT NULL,
    file_url     VARCHAR(500) NOT NULL,
    is_verified  BOOLEAN NOT NULL DEFAULT FALSE,
    created_at   TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- 6. Расписание
CREATE TABLE schedules (
    id           SERIAL PRIMARY KEY,
    tutor_id     UUID REFERENCES users(id) ON DELETE CASCADE,
    day_of_week  INT CHECK (day_of_week BETWEEN 1 AND 7),
    specific_date DATE,
    start_time   TIME NOT NULL,
    end_time     TIME NOT NULL,
    CONSTRAINT schedule_type_check CHECK (
        (day_of_week IS NOT NULL AND specific_date IS NULL) OR
        (day_of_week IS NULL AND specific_date IS NOT NULL)
    )
);

-- 7. Уроки
CREATE TABLE lessons (
    id             UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    student_id     UUID NOT NULL REFERENCES users(id),
    tutor_id       UUID NOT NULL REFERENCES users(id),
    start_datetime TIMESTAMPTZ NOT NULL,
    end_datetime   TIMESTAMPTZ NOT NULL,
    status         lesson_status NOT NULL DEFAULT 'planned',
    meeting_link   VARCHAR(500)
);

CREATE INDEX lessons_start_idx ON lessons(start_datetime);
CREATE INDEX lessons_tutor_idx ON lessons(tutor_id);
CREATE INDEX lessons_student_idx ON lessons(student_id);

-- 8. Заявки
CREATE TABLE applications (
    id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    student_id   UUID NOT NULL REFERENCES users(id),
    tutor_id     UUID NOT NULL REFERENCES users(id),
    status       application_status NOT NULL DEFAULT 'pending',
    created_at   TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    responded_at TIMESTAMPTZ,
    UNIQUE (student_id, tutor_id)
);

-- 9. Чаты и сообщения
CREATE TABLE chats (
    id             UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    application_id UUID NOT NULL UNIQUE REFERENCES applications(id),
    created_at     TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE messages (
    id         UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    chat_id    UUID NOT NULL REFERENCES chats(id) ON DELETE CASCADE,
    sender_id  UUID NOT NULL REFERENCES users(id),
    text       TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    is_read    BOOLEAN NOT NULL DEFAULT FALSE
);

CREATE INDEX messages_chat_idx ON messages(chat_id, created_at DESC);

-- 10. Тестирование
CREATE TABLE test_library (
    id            SERIAL PRIMARY KEY,
    subject_id    INT  NOT NULL REFERENCES subjects(id),
    topic         VARCHAR(255) NOT NULL,
    questions_json JSONB NOT NULL
);

CREATE TABLE student_results (
    id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    student_id   UUID NOT NULL REFERENCES users(id),
    tutor_id     UUID NOT NULL REFERENCES users(id),
    test_id      INT  NOT NULL REFERENCES test_library(id),
    type         result_type NOT NULL,
    score        DECIMAL(5,2),
    assigned_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    completed_at TIMESTAMPTZ
);

-- 11. Отзывы
CREATE TABLE reviews (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    student_id          UUID NOT NULL REFERENCES users(id),
    tutor_id            UUID NOT NULL REFERENCES users(id),
    lesson_id           UUID REFERENCES lessons(id),
    communication_score INT  NOT NULL CHECK (communication_score BETWEEN 1 AND 5),
    text                TEXT,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (student_id, lesson_id)
);

-- 12. Push-уведомления
CREATE TABLE device_tokens (
    id         SERIAL PRIMARY KEY,
    user_id    UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    token      VARCHAR(500) NOT NULL UNIQUE,
    platform   device_platform NOT NULL,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX device_tokens_user_idx ON device_tokens(user_id);

-- -------------------------------------------------------------------------
-- Роли БД для PostgREST
-- -------------------------------------------------------------------------
-- api_user     — служебная роль для FastAPI (custom-api), минует RLS
-- anon_db      — анонимные запросы (без JWT)
-- tutor_db     — аутентифицированные репетиторы
-- student_db   — аутентифицированные ученики
-- -------------------------------------------------------------------------
DO $$
BEGIN
   IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = 'api_user') THEN
      CREATE ROLE api_user NOLOGIN;
   END IF;
   IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = 'anon_db') THEN
      CREATE ROLE anon_db NOLOGIN;
   END IF;
   IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = 'tutor_db') THEN
      CREATE ROLE tutor_db NOLOGIN;
   END IF;
   IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = 'student_db') THEN
      CREATE ROLE student_db NOLOGIN;
   END IF;
END
$$;

-- api_user: полный доступ (для internal-сервисов FastAPI)
GRANT ALL ON ALL TABLES IN SCHEMA public TO api_user;
GRANT ALL ON ALL SEQUENCES IN SCHEMA public TO api_user;
GRANT ALL ON ALL FUNCTIONS IN SCHEMA public TO api_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO api_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO api_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON FUNCTIONS TO api_user;

-- anon_db: только чтение справочников
GRANT USAGE ON SCHEMA public TO anon_db;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO anon_db;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT ON TABLES TO anon_db;

-- tutor_db, student_db: полный доступ к данным (RLS будет фильтровать строки)
GRANT ALL ON ALL TABLES IN SCHEMA public TO tutor_db, student_db;
GRANT ALL ON ALL SEQUENCES IN SCHEMA public TO tutor_db, student_db;
GRANT ALL ON ALL FUNCTIONS IN SCHEMA public TO tutor_db, student_db;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO tutor_db, student_db;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO tutor_db, student_db;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON FUNCTIONS TO tutor_db, student_db;

-- -------------------------------------------------------------------------
-- Вспомогательные функции для RLS
-- -------------------------------------------------------------------------
-- Извлекает user_id (UUID) из JWT-claims, установленных PostgREST
CREATE OR REPLACE FUNCTION current_user_id() RETURNS UUID AS $$
    SELECT (current_setting('request.jwt.claims', true)::jsonb ->> 'sub')::UUID
$$ LANGUAGE sql STABLE;

-- Извлекает название роли (tutor/student) из JWT
CREATE OR REPLACE FUNCTION current_user_role() RETURNS TEXT AS $$
    SELECT current_setting('request.jwt.claims', true)::jsonb ->> 'role'
$$ LANGUAGE sql STABLE;

-- Извлекает массив ролей (realm_roles) из JWT
CREATE OR REPLACE FUNCTION current_user_realm_roles() RETURNS TEXT[] AS $$
    SELECT ARRAY(
        SELECT jsonb_array_elements_text(
            current_setting('request.jwt.claims', true)::jsonb -> 'realm_roles'
        )
    )
$$ LANGUAGE sql STABLE;

-- -------------------------------------------------------------------------
-- Функция для PostgREST: определяет роль БД из JWT-claims
-- -------------------------------------------------------------------------
-- PostgREST вызывает её при каждом запросе через PGRST_DB_PRE_REQUEST,
-- чтобы переключиться на правильную роль БД.
-- Функция БЕЗ аргументов — PostgREST v12 передаёт JWT claims через
-- current_setting('request.jwt.claims', true).
CREATE OR REPLACE FUNCTION api_user_role() RETURNS name AS $$
    SELECT CASE
        WHEN current_setting('request.jwt.claims', true)::jsonb->'realm_roles' @> '"tutor"'::jsonb THEN 'tutor_db'::name
        WHEN current_setting('request.jwt.claims', true)::jsonb->'realm_roles' @> '"student"'::jsonb THEN 'student_db'::name
        ELSE 'anon_db'::name
    END;
$$ LANGUAGE sql STABLE;

-- -------------------------------------------------------------------------
-- RLS: включение Row-Level Security на всех защищаемых таблицах
-- -------------------------------------------------------------------------
ALTER TABLE users                    ENABLE ROW LEVEL SECURITY;
ALTER TABLE tutor_profiles           ENABLE ROW LEVEL SECURITY;
ALTER TABLE student_profiles         ENABLE ROW LEVEL SECURITY;
ALTER TABLE tutor_tags               ENABLE ROW LEVEL SECURITY;
ALTER TABLE student_preferred_tags   ENABLE ROW LEVEL SECURITY;
ALTER TABLE tutor_certifications     ENABLE ROW LEVEL SECURITY;
ALTER TABLE schedules                ENABLE ROW LEVEL SECURITY;
ALTER TABLE lessons                  ENABLE ROW LEVEL SECURITY;
ALTER TABLE applications             ENABLE ROW LEVEL SECURITY;
ALTER TABLE chats                    ENABLE ROW LEVEL SECURITY;
ALTER TABLE messages                 ENABLE ROW LEVEL SECURITY;
ALTER TABLE student_results          ENABLE ROW LEVEL SECURITY;
ALTER TABLE reviews                  ENABLE ROW LEVEL SECURITY;
ALTER TABLE device_tokens            ENABLE ROW LEVEL SECURITY;

-- -------------------------------------------------------------------------
-- RLS-политики
-- -------------------------------------------------------------------------
-- Принцип: api_user (сервисная роль) видит всё.
-- Обычные пользователи видят/редактируют только свои данные.
-- Публичные справочники (subjects, tags) доступны всем,
-- но писать могут только аутентифицированные пользователи.

-- *** users ***
CREATE POLICY users_select ON users FOR SELECT
    USING (current_setting('role') = 'api_user' OR current_user_id() = id);
CREATE POLICY users_insert ON users FOR INSERT
    WITH CHECK (current_setting('role') = 'api_user');
CREATE POLICY users_update ON users FOR UPDATE
    USING (current_setting('role') = 'api_user');
CREATE POLICY users_delete ON users FOR DELETE
    USING (current_setting('role') = 'api_user');

-- *** subjects (публичный справочник) ***
CREATE POLICY subjects_select ON subjects FOR SELECT USING (true);
CREATE POLICY subjects_insert ON subjects FOR INSERT
    WITH CHECK (current_setting('role') IN ('api_user', 'tutor_db', 'student_db'));
CREATE POLICY subjects_update ON subjects FOR UPDATE
    USING (current_setting('role') IN ('api_user', 'tutor_db', 'student_db'));
CREATE POLICY subjects_delete ON subjects FOR DELETE
    USING (current_setting('role') IN ('api_user', 'tutor_db', 'student_db'));

-- *** tags (публичный справочник) ***
CREATE POLICY tags_select ON tags FOR SELECT USING (true);
CREATE POLICY tags_insert ON tags FOR INSERT
    WITH CHECK (current_setting('role') IN ('api_user', 'tutor_db', 'student_db'));
CREATE POLICY tags_update ON tags FOR UPDATE
    USING (current_setting('role') IN ('api_user', 'tutor_db', 'student_db'));

-- *** tutor_profiles ***
CREATE POLICY tutor_profiles_select ON tutor_profiles FOR SELECT USING (true);
CREATE POLICY tutor_profiles_insert ON tutor_profiles FOR INSERT
    WITH CHECK (current_setting('role') = 'api_user'
                OR (current_user_id() = user_id AND current_user_role() = 'tutor'));
CREATE POLICY tutor_profiles_update ON tutor_profiles FOR UPDATE
    USING (current_setting('role') = 'api_user'
           OR (current_user_id() = user_id AND current_user_role() = 'tutor'));
CREATE POLICY tutor_profiles_delete ON tutor_profiles FOR DELETE
    USING (current_setting('role') = 'api_user');

-- *** student_profiles ***
CREATE POLICY student_profiles_select ON student_profiles FOR SELECT
    USING (current_setting('role') = 'api_user' OR current_user_id() = user_id);
CREATE POLICY student_profiles_insert ON student_profiles FOR INSERT
    WITH CHECK (current_setting('role') = 'api_user'
                OR (current_user_id() = user_id AND current_user_role() = 'student'));
CREATE POLICY student_profiles_update ON student_profiles FOR UPDATE
    USING (current_setting('role') = 'api_user'
           OR (current_user_id() = user_id AND current_user_role() = 'student'));
CREATE POLICY student_profiles_delete ON student_profiles FOR DELETE
    USING (current_setting('role') = 'api_user');

-- *** tutor_tags ***
CREATE POLICY tutor_tags_select ON tutor_tags FOR SELECT USING (true);
CREATE POLICY tutor_tags_insert ON tutor_tags FOR INSERT
    WITH CHECK (tutor_id = current_user_id() OR current_setting('role') = 'api_user');
CREATE POLICY tutor_tags_update ON tutor_tags FOR UPDATE
    USING (tutor_id = current_user_id() OR current_setting('role') = 'api_user');
CREATE POLICY tutor_tags_delete ON tutor_tags FOR DELETE
    USING (tutor_id = current_user_id() OR current_setting('role') = 'api_user');

-- *** student_preferred_tags ***
CREATE POLICY student_preferred_tags_select ON student_preferred_tags FOR SELECT USING (true);
CREATE POLICY student_preferred_tags_insert ON student_preferred_tags FOR INSERT
    WITH CHECK (student_id = current_user_id() OR current_setting('role') = 'api_user');
CREATE POLICY student_preferred_tags_update ON student_preferred_tags FOR UPDATE
    USING (student_id = current_user_id() OR current_setting('role') = 'api_user');
CREATE POLICY student_preferred_tags_delete ON student_preferred_tags FOR DELETE
    USING (student_id = current_user_id() OR current_setting('role') = 'api_user');

-- *** tutor_certifications ***
CREATE POLICY tutor_certifications_select ON tutor_certifications FOR SELECT USING (true);
CREATE POLICY tutor_certifications_insert ON tutor_certifications FOR INSERT
    WITH CHECK (tutor_id = current_user_id() OR current_setting('role') = 'api_user');
CREATE POLICY tutor_certifications_update ON tutor_certifications FOR UPDATE
    USING (tutor_id = current_user_id() OR current_setting('role') = 'api_user');
CREATE POLICY tutor_certifications_delete ON tutor_certifications FOR DELETE
    USING (tutor_id = current_user_id() OR current_setting('role') = 'api_user');

-- *** schedules ***
CREATE POLICY schedules_select ON schedules FOR SELECT USING (true);
CREATE POLICY schedules_insert ON schedules FOR INSERT
    WITH CHECK (tutor_id = current_user_id() OR current_setting('role') = 'api_user');
CREATE POLICY schedules_update ON schedules FOR UPDATE
    USING (tutor_id = current_user_id() OR current_setting('role') = 'api_user');
CREATE POLICY schedules_delete ON schedules FOR DELETE
    USING (tutor_id = current_user_id() OR current_setting('role') = 'api_user');

-- *** lessons ***
CREATE POLICY lessons_select ON lessons FOR SELECT
    USING (student_id = current_user_id() OR tutor_id = current_user_id());
CREATE POLICY lessons_insert ON lessons FOR INSERT
    WITH CHECK (current_setting('role') = 'api_user'
                OR (student_id = current_user_id() OR tutor_id = current_user_id()));
CREATE POLICY lessons_update ON lessons FOR UPDATE
    USING (student_id = current_user_id() OR tutor_id = current_user_id());
CREATE POLICY lessons_delete ON lessons FOR DELETE
    USING (current_setting('role') = 'api_user');

-- *** applications ***
CREATE POLICY applications_select ON applications FOR SELECT
    USING (student_id = current_user_id() OR tutor_id = current_user_id());
CREATE POLICY applications_insert ON applications FOR INSERT
    WITH CHECK (student_id = current_user_id());
CREATE POLICY applications_update ON applications FOR UPDATE
    USING (tutor_id = current_user_id() AND current_user_role() = 'tutor')
    WITH CHECK (tutor_id = current_user_id() AND current_user_role() = 'tutor');
CREATE POLICY applications_delete ON applications FOR DELETE
    USING (current_setting('role') = 'api_user');

-- *** chats ***
CREATE POLICY chats_select ON chats FOR SELECT
    USING (application_id IN (
        SELECT id FROM applications
        WHERE student_id = current_user_id() OR tutor_id = current_user_id()
    ));
CREATE POLICY chats_insert ON chats FOR INSERT
    WITH CHECK (current_setting('role') = 'api_user');
CREATE POLICY chats_update ON chats FOR UPDATE
    USING (current_setting('role') = 'api_user');
CREATE POLICY chats_delete ON chats FOR DELETE
    USING (current_setting('role') = 'api_user');

-- *** messages ***
CREATE POLICY messages_select ON messages FOR SELECT
    USING (chat_id IN (
        SELECT c.id FROM chats c
        JOIN applications a ON a.id = c.application_id
        WHERE a.student_id = current_user_id() OR a.tutor_id = current_user_id()
    ));
CREATE POLICY messages_insert ON messages FOR INSERT
    WITH CHECK (
        sender_id = current_user_id()
        AND chat_id IN (
            SELECT c.id FROM chats c
            JOIN applications a ON a.id = c.application_id
            WHERE a.student_id = current_user_id() OR a.tutor_id = current_user_id()
        )
    );
CREATE POLICY messages_update ON messages FOR UPDATE
    USING (sender_id = current_user_id());
CREATE POLICY messages_delete ON messages FOR DELETE
    USING (sender_id = current_user_id());

-- *** student_results ***
CREATE POLICY student_results_select ON student_results FOR SELECT
    USING (student_id = current_user_id() OR tutor_id = current_user_id());
CREATE POLICY student_results_insert ON student_results FOR INSERT
    WITH CHECK (current_setting('role') = 'api_user'
                OR (tutor_id = current_user_id() AND current_user_role() = 'tutor'));
CREATE POLICY student_results_update ON student_results FOR UPDATE
    USING (tutor_id = current_user_id() AND current_user_role() = 'tutor');
CREATE POLICY student_results_delete ON student_results FOR DELETE
    USING (current_setting('role') = 'api_user');

-- *** reviews ***
CREATE POLICY reviews_select ON reviews FOR SELECT USING (true);
CREATE POLICY reviews_insert ON reviews FOR INSERT
    WITH CHECK (student_id = current_user_id() AND current_user_role() = 'student');
CREATE POLICY reviews_update ON reviews FOR UPDATE
    USING (student_id = current_user_id());
CREATE POLICY reviews_delete ON reviews FOR DELETE
    USING (current_setting('role') = 'api_user');

-- *** device_tokens ***
CREATE POLICY device_tokens_select ON device_tokens FOR SELECT
    USING (user_id = current_user_id() OR current_setting('role') = 'api_user');
CREATE POLICY device_tokens_insert ON device_tokens FOR INSERT
    WITH CHECK (user_id = current_user_id() OR current_setting('role') = 'api_user');
CREATE POLICY device_tokens_update ON device_tokens FOR UPDATE
    USING (user_id = current_user_id() OR current_setting('role') = 'api_user')
    WITH CHECK (user_id = current_user_id() OR current_setting('role') = 'api_user');
CREATE POLICY device_tokens_delete ON device_tokens FOR DELETE
    USING (user_id = current_user_id() OR current_setting('role') = 'api_user');
