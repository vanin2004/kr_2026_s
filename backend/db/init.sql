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

-- PostgREST Roles (Simplified for "no restrictions")
-- In a real app we'd have 'authenticator', 'anon', etc.
-- Since the user asked for NO restrictions, we'll grant everything to a single role.

DO $$
BEGIN
   IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = 'api_user') THEN
      CREATE ROLE api_user;
   END IF;
END
$$;

GRANT ALL ON ALL TABLES IN SCHEMA public TO api_user;
GRANT ALL ON ALL SEQUENCES IN SCHEMA public TO api_user;
GRANT ALL ON ALL FUNCTIONS IN SCHEMA public TO api_user;
