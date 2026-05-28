-- PostgreSQL initialization script for Tutor Platform
-- Database starts fresh each time, no persistent data
-- All data is initialized in a clean slate

-- Create keycloak database (required by Keycloak service)
CREATE DATABASE keycloak_db;

-- Switch to tutor platform database
\c tutor_platform_db;

-- Create API schema for PostgREST
CREATE SCHEMA IF NOT EXISTS api;
SET search_path TO api, public;

-- Migration tracking tables (empty, for compatibility with migration tools)
CREATE TABLE IF NOT EXISTS public.databasechangeloglock (
    ID INT NOT NULL PRIMARY KEY,
    LOCKED BOOLEAN NOT NULL DEFAULT FALSE,
    LOCKGRANTED TIMESTAMP,
    LOCKEDBY VARCHAR(255)
);

INSERT INTO public.databasechangeloglock (ID, LOCKED) 
VALUES (1, FALSE) 
ON CONFLICT DO NOTHING;

-- ENUMs
CREATE TYPE api.user_role AS ENUM ('tutor', 'student');
CREATE TYPE api.lesson_status AS ENUM ('planned', 'completed', 'cancelled');
CREATE TYPE api.application_status AS ENUM ('pending', 'accepted', 'rejected');
CREATE TYPE api.test_type AS ENUM ('initial_test', 'control_test');

-- 1. Users
CREATE TABLE api.users (
    id UUID PRIMARY KEY,
    email VARCHAR UNIQUE,
    password_hash VARCHAR,
    role api.user_role NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. Profiles
CREATE TABLE api.tutor_profiles (
    user_id UUID PRIMARY KEY REFERENCES api.users(id) ON DELETE CASCADE,
    full_name VARCHAR NOT NULL,
    education TEXT,
    specialization VARCHAR,
    hourly_rate INT,
    experience_years INT,
    rating_overall DECIMAL(3, 2),
    rating_efficiency DECIMAL(3, 2),
    rating_communication DECIMAL(3, 2),
    student_count INT DEFAULT 0
);

CREATE TABLE api.student_profiles (
    user_id UUID PRIMARY KEY REFERENCES api.users(id) ON DELETE CASCADE,
    full_name VARCHAR NOT NULL
);

-- 3. Tags
CREATE TABLE api.tags (
    id SERIAL PRIMARY KEY,
    name VARCHAR UNIQUE NOT NULL
);

CREATE TABLE api.tutor_tags (
    tutor_id UUID REFERENCES api.users(id) ON DELETE CASCADE,
    tag_id INT REFERENCES api.tags(id) ON DELETE CASCADE,
    PRIMARY KEY (tutor_id, tag_id)
);

-- 4. Schedules and Lessons
CREATE TABLE api.schedules (
    id SERIAL PRIMARY KEY,
    tutor_id UUID NOT NULL REFERENCES api.users(id) ON DELETE CASCADE,
    day_of_week INT CHECK (day_of_week BETWEEN 1 AND 7),
    start_time TIME NOT NULL,
    end_time TIME NOT NULL
);

CREATE TABLE api.lessons (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    student_id UUID NOT NULL REFERENCES api.users(id) ON DELETE CASCADE,
    tutor_id UUID NOT NULL REFERENCES api.users(id) ON DELETE CASCADE,
    start_datetime TIMESTAMP NOT NULL,
    end_datetime TIMESTAMP NOT NULL,
    status api.lesson_status DEFAULT 'planned',
    meeting_link VARCHAR
);

-- 5. Applications and Chats
CREATE TABLE api.applications (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    student_id UUID NOT NULL REFERENCES api.users(id) ON DELETE CASCADE,
    tutor_id UUID NOT NULL REFERENCES api.users(id) ON DELETE CASCADE,
    status api.application_status DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE api.chats (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    application_id UUID UNIQUE NOT NULL REFERENCES api.applications(id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE api.messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    chat_id UUID NOT NULL REFERENCES api.chats(id) ON DELETE CASCADE,
    sender_id UUID NOT NULL REFERENCES api.users(id) ON DELETE CASCADE,
    text TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 6. Tests and Results
CREATE TABLE api.test_library (
    id SERIAL PRIMARY KEY,
    subject VARCHAR NOT NULL,
    topic VARCHAR NOT NULL,
    questions_json JSONB NOT NULL
);

CREATE TABLE api.student_results (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    student_id UUID NOT NULL REFERENCES api.users(id) ON DELETE CASCADE,
    tutor_id UUID NOT NULL REFERENCES api.users(id) ON DELETE CASCADE,
    test_id INT NOT NULL REFERENCES api.test_library(id) ON DELETE CASCADE,
    type api.test_type NOT NULL,
    score DECIMAL(5, 2),
    assigned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP
);

-- 7. Reviews
CREATE TABLE api.reviews (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    student_id UUID NOT NULL REFERENCES api.users(id) ON DELETE CASCADE,
    tutor_id UUID NOT NULL REFERENCES api.users(id) ON DELETE CASCADE,
    lesson_id UUID REFERENCES api.lessons(id) ON DELETE SET NULL,
    communication_score INT CHECK (communication_score BETWEEN 1 AND 5),
    text TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create health_check table that was previously there
CREATE TABLE IF NOT EXISTS api.health_check (
    id SERIAL PRIMARY KEY,
    service_name VARCHAR(100) NOT NULL,
    status VARCHAR(20) NOT NULL,
    checked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Privileges
-- Create postgres role if it doesn't exist (for compatibility)
DO $$
BEGIN
  CREATE ROLE postgres;
EXCEPTION WHEN duplicate_object THEN
  NULL;
END $$;

GRANT USAGE ON SCHEMA api TO postgres;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA api TO postgres;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA api TO postgres;

-- Create basic roles for Row-Level Security
DO $$
BEGIN
  CREATE ROLE authenticator NOINHERIT LOGIN PASSWORD 'tutordb_pass';
EXCEPTION WHEN duplicate_object THEN
  NULL;
END $$;

DO $$
BEGIN
  CREATE ROLE web_student NOINHERIT;
EXCEPTION WHEN duplicate_object THEN
  NULL;
END $$;

DO $$
BEGIN
  CREATE ROLE web_tutor NOINHERIT;
EXCEPTION WHEN duplicate_object THEN
  NULL;
END $$;

DO $$
BEGIN
  CREATE ROLE anon NOINHERIT;
EXCEPTION WHEN duplicate_object THEN
  NULL;
END $$;

-- Grant schema access
GRANT USAGE ON SCHEMA api TO authenticator, web_student, web_tutor, anon;
GRANT USAGE ON SCHEMA api TO postgres;

-- Required grants for PostgREST mapped users
GRANT web_student, web_tutor, anon TO authenticator;
GRANT ALL ON ALL TABLES IN SCHEMA api TO authenticator, web_student, web_tutor, anon;
GRANT ALL ON ALL SEQUENCES IN SCHEMA api TO authenticator, web_student, web_tutor, anon;

-- Инициализируем RLS политики для проекта

-- Включаем RLS
ALTER TABLE api.users ENABLE ROW LEVEL SECURITY;
ALTER TABLE api.tutor_profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE api.student_profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE api.schedules ENABLE ROW LEVEL SECURITY;
ALTER TABLE api.lessons ENABLE ROW LEVEL SECURITY;
ALTER TABLE api.applications ENABLE ROW LEVEL SECURITY;
ALTER TABLE api.chats ENABLE ROW LEVEL SECURITY;
ALTER TABLE api.messages ENABLE ROW LEVEL SECURITY;
ALTER TABLE api.student_results ENABLE ROW LEVEL SECURITY;
ALTER TABLE api.reviews ENABLE ROW LEVEL SECURITY;

-- 1. Пользователи могут читать свои данные и публичные данные
CREATE POLICY "Users can read own data" ON api.users FOR SELECT USING (id = current_setting('request.jwt.claim.sub', true)::uuid);
CREATE POLICY "Public profile data for tutors" ON api.tutor_profiles FOR SELECT USING (true);
CREATE POLICY "Public profile data for students" ON api.student_profiles FOR SELECT USING (true);

-- Репетиторы могут редактировать свой профиль
CREATE POLICY "Tutors update own profile" ON api.tutor_profiles FOR UPDATE USING (user_id = current_setting('request.jwt.claim.sub', true)::uuid);
CREATE POLICY "Students update own profile" ON api.student_profiles FOR UPDATE USING (user_id = current_setting('request.jwt.claim.sub', true)::uuid);

-- 2. Расписание
CREATE POLICY "Anyone can see tutor schedules" ON api.schedules FOR SELECT USING (true);
CREATE POLICY "Tutors control own schedules" ON api.schedules FOR ALL USING (tutor_id = current_setting('request.jwt.claim.sub', true)::uuid);

-- 3. Занятия и Заявки
CREATE POLICY "Students/Tutors see own applications" ON api.applications FOR SELECT USING (
    student_id = current_setting('request.jwt.claim.sub', true)::uuid OR tutor_id = current_setting('request.jwt.claim.sub', true)::uuid
);
CREATE POLICY "Students create applications" ON api.applications FOR INSERT WITH CHECK (
    student_id = current_setting('request.jwt.claim.sub', true)::uuid
);
CREATE POLICY "Tutors can update applications" ON api.applications FOR UPDATE USING (
    tutor_id = current_setting('request.jwt.claim.sub', true)::uuid
);

CREATE POLICY "Participants see own lessons" ON api.lessons FOR SELECT USING (
    student_id = current_setting('request.jwt.claim.sub', true)::uuid OR tutor_id = current_setting('request.jwt.claim.sub', true)::uuid
);
CREATE POLICY "Tutors manage lessons" ON api.lessons FOR ALL USING (
    tutor_id = current_setting('request.jwt.claim.sub', true)::uuid
);
CREATE POLICY "Students create lessons" ON api.lessons FOR INSERT WITH CHECK (
    student_id = current_setting('request.jwt.claim.sub', true)::uuid
);

-- 4. Чаты и сообщения
CREATE POLICY "Participants see chat" ON api.chats FOR SELECT USING (
    EXISTS (
        SELECT 1 FROM api.applications a 
        WHERE a.id = application_id 
        AND (a.student_id = current_setting('request.jwt.claim.sub', true)::uuid OR a.tutor_id = current_setting('request.jwt.claim.sub', true)::uuid)
    )
);
CREATE POLICY "Participants read messages" ON api.messages FOR SELECT USING (
    EXISTS (
        SELECT 1 FROM api.chats c
        JOIN api.applications a ON c.application_id = a.id
        WHERE c.id = chat_id 
        AND (a.student_id = current_setting('request.jwt.claim.sub', true)::uuid OR a.tutor_id = current_setting('request.jwt.claim.sub', true)::uuid)
    )
);
CREATE POLICY "Participants send messages" ON api.messages FOR INSERT WITH CHECK (
    sender_id = current_setting('request.jwt.claim.sub', true)::uuid
);

-- 5. Тестирование и оценки (Read only for users, system will write results)
CREATE POLICY "Students see own results" ON api.student_results FOR SELECT USING (
    student_id = current_setting('request.jwt.claim.sub', true)::uuid OR tutor_id = current_setting('request.jwt.claim.sub', true)::uuid
);
CREATE POLICY "Students create own results" ON api.student_results FOR INSERT WITH CHECK (
    student_id = current_setting('request.jwt.claim.sub', true)::uuid
);

-- 6. Отзывы
CREATE POLICY "Public reviews" ON api.reviews FOR SELECT USING (true);
CREATE POLICY "Students create reviews" ON api.reviews FOR INSERT WITH CHECK (
    student_id = current_setting('request.jwt.claim.sub', true)::uuid
);
-- Trigger for automatic user profile creation

CREATE OR REPLACE FUNCTION api.create_profile_for_new_user()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.role = 'tutor' THEN
        INSERT INTO api.tutor_profiles (user_id, full_name, student_count)
        VALUES (NEW.id, 'New Tutor', 0);
    ELSIF NEW.role = 'student' THEN
        INSERT INTO api.student_profiles (user_id, full_name)
        VALUES (NEW.id, 'New Student');
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

CREATE TRIGGER on_user_created
    AFTER INSERT ON api.users
    FOR EACH ROW
    EXECUTE FUNCTION api.create_profile_for_new_user();

-- Trigger for chat creation when application is accepted

CREATE OR REPLACE FUNCTION api.create_chat_on_application_accepted()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.status = 'accepted' AND OLD.status != 'accepted' THEN
        INSERT INTO api.chats (application_id)
        VALUES (NEW.id);
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

CREATE TRIGGER on_application_accepted
    AFTER UPDATE ON api.applications
    FOR EACH ROW
    EXECUTE FUNCTION api.create_chat_on_application_accepted();

-- ============================================================
-- Database initialization complete
-- ============================================================
-- Clean slate - no migration tables, no legacy data tracking
