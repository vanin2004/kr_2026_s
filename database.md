# Схема базы данных (ER-модель, исправленная)

> **Изменения относительно исходной версии** отмечены комментарием `-- ADDED` или `-- FIXED`.

---

## 1. Справочники

### `subjects` — ADDED

Справочник предметов. Обеспечивает точное совпадение при Hard Filter в алгоритме подбора.

```sql
CREATE TABLE subjects (
    id    SERIAL PRIMARY KEY,
    name  VARCHAR(100) NOT NULL UNIQUE  -- 'Математика', 'Английский язык'
);
```

### `tags`

Словарь тегов (например, `#подготовка_к_ЕГЭ`, `#строгий_подход`).

```sql
CREATE TABLE tags (
    id    SERIAL PRIMARY KEY,
    name  VARCHAR(100) NOT NULL UNIQUE
);
```

---

## 2. Пользователи

### `users` — FIXED

Базовая таблица пользователей. `id` = UUID из Keycloak. **Поле `password_hash` удалено** — управление паролями полностью делегировано Keycloak.

```sql
CREATE TABLE users (
    id         UUID PRIMARY KEY,            -- = Keycloak sub
    email      VARCHAR(255) NOT NULL UNIQUE,
    role       user_role    NOT NULL,        -- ENUM: 'tutor', 'student'
    created_at TIMESTAMPTZ  NOT NULL DEFAULT NOW()
);

CREATE TYPE user_role AS ENUM ('tutor', 'student');
```

---

## 3. Профили

### `tutor_profiles` — FIXED

Детальная информация о репетиторе.

```sql
CREATE TABLE tutor_profiles (
    user_id               UUID PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
    full_name             VARCHAR(255),
    photo_url             VARCHAR(500),
    education             TEXT,
    subject_id            INT REFERENCES subjects(id),  -- FIXED: FK вместо VARCHAR
    hourly_rate           INT,                          -- в копейках, валюта: RUB
    experience_years      INT DEFAULT 0,
    is_verified           BOOLEAN NOT NULL DEFAULT FALSE,  -- ADDED: для фильтра verified_only
    student_count         INT NOT NULL DEFAULT 0,

    -- Рейтинги (пересчитываются pg_cron ежедневно)
    rating_efficiency     DECIMAL(4,3),  -- O1: [0..1]
    rating_communication  DECIMAL(4,3),  -- O2: [0..1]
    rating_expertise      DECIMAL(4,3),  -- O3: [0..1] -- ADDED
    rating_responsiveness DECIMAL(4,3),  -- O4: [0..1] -- ADDED

    -- Cold-start: снижается после N заявок/просмотров
    is_new_boost          BOOLEAN NOT NULL DEFAULT TRUE   -- ADDED
);
```

> `rating_overall` убран: итоговый `Score` вычисляется динамически в FastAPI с учётом весов конкретного ученика — одного «глобального» рейтинга не существует.

### `student_profiles` — FIXED

```sql
CREATE TABLE student_profiles (
    user_id    UUID PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
    full_name  VARCHAR(255),
    photo_url  VARCHAR(500),

    -- Настройки алгоритма подбора — ADDED
    search_weights  JSONB NOT NULL DEFAULT '{
        "k1_effectiveness": 0.30,
        "k2_communication": 0.15,
        "k3_expertise":     0.20,
        "k4_responsiveness":0.15,
        "k5_tags":          0.20
    }'::jsonb
);
```

> `search_weights` хранит персональные веса k1..k5. Передаётся в `POST /api/custom/suggestions` как дефолт, но может быть переопределён на лету прямо в запросе.

---

## 4. Теги

### `tutor_tags`

Теги, которые репетитор назначил себе.

```sql
CREATE TABLE tutor_tags (
    tutor_id  UUID REFERENCES users(id) ON DELETE CASCADE,
    tag_id    INT  REFERENCES tags(id)  ON DELETE CASCADE,
    PRIMARY KEY (tutor_id, tag_id)
);
```

### `student_preferred_tags` — ADDED

Желаемые теги ученика. Используются для расчёта O5 (Tag Match).

```sql
CREATE TABLE student_preferred_tags (
    student_id  UUID REFERENCES users(id) ON DELETE CASCADE,
    tag_id      INT  REFERENCES tags(id)  ON DELETE CASCADE,
    is_required BOOLEAN NOT NULL DEFAULT FALSE,  -- true = Hard Filter, false = Soft Score
    PRIMARY KEY (student_id, tag_id)
);
```

---

## 5. Верификация репетиторов — ADDED

### `tutor_certifications`

Загруженные документы и сертификаты. Влияют на O3 (Expertise).

```sql
CREATE TABLE tutor_certifications (
    id           SERIAL PRIMARY KEY,
    tutor_id     UUID REFERENCES users(id) ON DELETE CASCADE,
    title        VARCHAR(255) NOT NULL,  -- 'Диплом МГУ', 'Сертификат IELTS'
    file_url     VARCHAR(500) NOT NULL,
    is_verified  BOOLEAN NOT NULL DEFAULT FALSE,  -- подтверждается модератором
    created_at   TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
```

---

## 6. Расписание — FIXED

### `schedules`

Слоты доступности репетитора. Поддерживает как регулярные (по дням недели), так и разовые слоты.

```sql
CREATE TABLE schedules (
    id           SERIAL PRIMARY KEY,
    tutor_id     UUID REFERENCES users(id) ON DELETE CASCADE,

    -- Регулярный слот (NULL для разового)
    day_of_week  INT CHECK (day_of_week BETWEEN 1 AND 7),  -- 1=Пн, 7=Вс

    -- Разовый слот (NULL для регулярного) -- ADDED
    specific_date DATE,

    start_time   TIME NOT NULL,
    end_time     TIME NOT NULL,

    CONSTRAINT schedule_type_check CHECK (
        (day_of_week IS NOT NULL AND specific_date IS NULL) OR
        (day_of_week IS NULL AND specific_date IS NOT NULL)
    )
);
```

---

## 7. Уроки

### `lessons`

Забронированные и проведённые уроки.

```sql
CREATE TABLE lessons (
    id             UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    student_id     UUID NOT NULL REFERENCES users(id),
    tutor_id       UUID NOT NULL REFERENCES users(id),
    start_datetime TIMESTAMPTZ NOT NULL,
    end_datetime   TIMESTAMPTZ NOT NULL,
    status         lesson_status NOT NULL DEFAULT 'planned',
    meeting_link   VARCHAR(500)  -- Zoom / Google Meet / Discord
);

CREATE TYPE lesson_status AS ENUM ('planned', 'completed', 'cancelled');

CREATE INDEX lessons_start_idx ON lessons(start_datetime);
CREATE INDEX lessons_tutor_idx ON lessons(tutor_id);
CREATE INDEX lessons_student_idx ON lessons(student_id);
```

---

## 8. Заявки

### `applications` — FIXED

```sql
CREATE TABLE applications (
    id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    student_id   UUID NOT NULL REFERENCES users(id),
    tutor_id     UUID NOT NULL REFERENCES users(id),
    status       application_status NOT NULL DEFAULT 'pending',
    created_at   TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    responded_at TIMESTAMPTZ,  -- ADDED: для расчёта O4 (время ответа репетитора)

    UNIQUE (student_id, tutor_id)  -- одна активная заявка между парой
);

CREATE TYPE application_status AS ENUM ('pending', 'accepted', 'rejected');
```

---

## 9. Чаты и сообщения

### `chats`

Чат создаётся автоматически триггером при `applications.status = 'accepted'`.

```sql
CREATE TABLE chats (
    id             UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    application_id UUID NOT NULL UNIQUE REFERENCES applications(id),
    created_at     TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
```

### `messages`

```sql
CREATE TABLE messages (
    id         UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    chat_id    UUID NOT NULL REFERENCES chats(id) ON DELETE CASCADE,
    sender_id  UUID NOT NULL REFERENCES users(id),
    text       TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    is_read    BOOLEAN NOT NULL DEFAULT FALSE  -- ADDED: для счётчика непрочитанных
);

CREATE INDEX messages_chat_idx ON messages(chat_id, created_at DESC);
```

---

## 10. Тестирование

### `test_library` — FIXED

```sql
CREATE TABLE test_library (
    id            SERIAL PRIMARY KEY,
    subject_id    INT  NOT NULL REFERENCES subjects(id),  -- FIXED: FK вместо VARCHAR
    topic         VARCHAR(255) NOT NULL,
    questions_json JSONB NOT NULL
);
```

### `student_results`

```sql
CREATE TABLE student_results (
    id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    student_id   UUID NOT NULL REFERENCES users(id),
    tutor_id     UUID NOT NULL REFERENCES users(id),
    test_id      INT  NOT NULL REFERENCES test_library(id),
    type         result_type NOT NULL,
    score        DECIMAL(5,2),         -- NULL до прохождения
    assigned_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    completed_at TIMESTAMPTZ           -- NULL до прохождения
);

CREATE TYPE result_type AS ENUM ('initial_test', 'control_test');
```

---

## 11. Отзывы

### `reviews`

```sql
CREATE TABLE reviews (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    student_id          UUID NOT NULL REFERENCES users(id),
    tutor_id            UUID NOT NULL REFERENCES users(id),
    lesson_id           UUID REFERENCES lessons(id),
    communication_score INT  NOT NULL CHECK (communication_score BETWEEN 1 AND 5),
    text                TEXT,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    UNIQUE (student_id, lesson_id)  -- один отзыв на урок
);
```

---

## 12. Push-уведомления — ADDED

### `device_tokens`

FCM-токены мобильных устройств пользователей.

```sql
CREATE TABLE device_tokens (
    id         SERIAL PRIMARY KEY,
    user_id    UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    token      VARCHAR(500) NOT NULL UNIQUE,
    platform   device_platform NOT NULL,  -- 'android', 'ios'
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TYPE device_platform AS ENUM ('android', 'ios');
CREATE INDEX device_tokens_user_idx ON device_tokens(user_id);
```

---

## 13. RLS-политики (ключевые)

```sql
-- Включить RLS на всех таблицах
ALTER TABLE tutor_profiles    ENABLE ROW LEVEL SECURITY;
ALTER TABLE student_profiles  ENABLE ROW LEVEL SECURITY;
ALTER TABLE schedules         ENABLE ROW LEVEL SECURITY;
ALTER TABLE lessons           ENABLE ROW LEVEL SECURITY;
ALTER TABLE applications      ENABLE ROW LEVEL SECURITY;
ALTER TABLE chats             ENABLE ROW LEVEL SECURITY;
ALTER TABLE messages          ENABLE ROW LEVEL SECURITY;
ALTER TABLE student_results   ENABLE ROW LEVEL SECURITY;
ALTER TABLE reviews           ENABLE ROW LEVEL SECURITY;
ALTER TABLE device_tokens     ENABLE ROW LEVEL SECURITY;

-- Вспомогательная функция: извлекает user_id из JWT-клеймов транзакции
CREATE OR REPLACE FUNCTION current_user_id() RETURNS UUID AS $$
    SELECT (current_setting('request.jwt.claims', true)::jsonb ->> 'sub')::UUID
$$ LANGUAGE sql STABLE;

-- Примеры политик

-- Профиль репетитора: читают все, редактирует только владелец
CREATE POLICY tutor_profile_select ON tutor_profiles FOR SELECT USING (true);
CREATE POLICY tutor_profile_update ON tutor_profiles FOR UPDATE USING (user_id = current_user_id());

-- Профиль ученика: только владелец
CREATE POLICY student_profile_all ON student_profiles USING (user_id = current_user_id());

-- Уроки: видят только участники
CREATE POLICY lessons_access ON lessons FOR ALL
    USING (student_id = current_user_id() OR tutor_id = current_user_id());

-- Заявки: ученик видит свои исходящие, репетитор — входящие
CREATE POLICY applications_access ON applications FOR ALL
    USING (student_id = current_user_id() OR tutor_id = current_user_id());

-- Чаты: только участники (через заявку)
CREATE POLICY chats_access ON chats FOR SELECT
    USING (
        application_id IN (
            SELECT id FROM applications
            WHERE student_id = current_user_id() OR tutor_id = current_user_id()
        )
    );

-- Сообщения: участники чата
CREATE POLICY messages_access ON messages FOR ALL
    USING (
        chat_id IN (
            SELECT c.id FROM chats c
            JOIN applications a ON a.id = c.application_id
            WHERE a.student_id = current_user_id() OR a.tutor_id = current_user_id()
        )
    );

-- Device tokens: только свои
CREATE POLICY device_tokens_own ON device_tokens USING (user_id = current_user_id());
```

---

## 14. Триггеры

### Создание чата при принятии заявки

```sql
CREATE OR REPLACE FUNCTION create_chat_on_accept() RETURNS TRIGGER AS $$
BEGIN
    IF NEW.status = 'accepted' AND OLD.status = 'pending' THEN
        INSERT INTO chats (application_id) VALUES (NEW.id);
        PERFORM pg_notify('application_accepted',
            json_build_object('application_id', NEW.id,
                              'student_id', NEW.student_id,
                              'tutor_id', NEW.tutor_id)::text);
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_create_chat
    AFTER UPDATE ON applications
    FOR EACH ROW EXECUTE FUNCTION create_chat_on_accept();
```

### Уведомление при новой заявке

```sql
CREATE OR REPLACE FUNCTION notify_new_application() RETURNS TRIGGER AS $$
BEGIN
    PERFORM pg_notify('new_application',
        json_build_object('application_id', NEW.id,
                          'tutor_id', NEW.tutor_id)::text);
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_new_application
    AFTER INSERT ON applications
    FOR EACH ROW EXECUTE FUNCTION notify_new_application();
```

### Уведомление при новом сообщении

```sql
CREATE OR REPLACE FUNCTION notify_new_message() RETURNS TRIGGER AS $$
BEGIN
    PERFORM pg_notify('new_message',
        json_build_object('message_id', NEW.id,
                          'chat_id', NEW.chat_id,
                          'sender_id', NEW.sender_id)::text);
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_new_message
    AFTER INSERT ON messages
    FOR EACH ROW EXECUTE FUNCTION notify_new_message();
```

---

## 15. pg_cron джобы

```sql
-- Расширение
CREATE EXTENSION IF NOT EXISTS pg_cron;

-- Пересчёт рейтингов O1, O2, O3 — ежедневно в 03:00
SELECT cron.schedule('recalculate-ratings', '0 3 * * *',
    $$SELECT recalculate_tutor_ratings()$$);

-- Пересчёт O4 (отзывчивость) — ежедневно в 04:00
SELECT cron.schedule('recalculate-responsiveness', '0 4 * * *',
    $$SELECT recalculate_responsiveness()$$);

-- Напоминания об уроках — каждые 15 минут
SELECT cron.schedule('lesson-reminders', '*/15 * * * *',
    $$SELECT notify_upcoming_lessons()$$);

-- Назначение контрольных тестов — ежедневно в 09:00
SELECT cron.schedule('assign-control-tests', '0 9 * * *',
    $$SELECT assign_control_tests()$$);
```

