# Схема базы данных (ER-модель)

## 1. Пользователи и Авторизация

### `users`
Базовая таблица для всех пользователей платформы (аутентификация).
* `id` (UUID, PK) — Уникальный идентификатор.
* `email` (VARCHAR, Unique) — Email адрес.
* `password_hash` (VARCHAR) — Хэш пароля.
* `role` (ENUM: 'tutor', 'student') — Роль в системе.
* `created_at` (TIMESTAMP) — Дата и время регистрации.

## 2. Профили

### `tutor_profiles`
Детальная информация о репетиторах.
* `user_id` (UUID, PK, FK -> users.id)
* `full_name` (VARCHAR) — ФИО.
* `education` (TEXT) — Данные об образовании.
* `specialization` (VARCHAR) — Основной предмет / специализация.
* `hourly_rate` (INT) — Стоимость часа занятий в копейках (ставка).
* `experience_years` (INT) — Стаж работы (в годах).
* `rating_overall` (DECIMAL) — Вычисляемый общий рейтинг репетитора.
* `rating_efficiency` (DECIMAL) — $O_1$: Рейтинг эффективности.
* `rating_communication` (DECIMAL) — $O_2$: Рейтинг коммуникабельности.
* `student_count` (INT) — Текущее количество активных учеников.

### `student_profiles`
Детальная информация об учениках.
* `user_id` (UUID, PK, FK -> users.id)
* `full_name` (VARCHAR) — ФИО.

## 3. Теги и Фильтрация

### `tags`
Словарь всех доступных тегов (например, #подготовка_к_ЕГЭ, #строгий_подход).
* `id` (INT, PK) — Идентификатор тега.
* `name` (VARCHAR, Unique) — Название тега.

### `tutor_tags`
Связь "Многие-ко-Многим" (Репетитор <-> Теги).
* `tutor_id` (UUID, FK -> users.id)
* `tag_id` (INT, FK -> tags.id)
* (PK: tutor_id, tag_id)

## 4. Расписание и Уроки

### `schedules` (Свободные слоты репетитора)
Настройки регулярного расписания доступности репетитора.
* `id` (INT, PK)
* `tutor_id` (UUID, FK -> users.id)
* `day_of_week` (INT, 1-7) — День недели.
* `start_time` (TIME) — Начало доступного слота.
* `end_time` (TIME) — Конец доступного слота.

### `lessons` (Занятия)
Конкретные забронированные и проведенные уроки.
* `id` (UUID, PK)
* `student_id` (UUID, FK -> users.id)
* `tutor_id` (UUID, FK -> users.id)
* `start_datetime` (TIMESTAMP) — Дата и время начала урока.
* `end_datetime` (TIMESTAMP) — Дата и время конца урока.
* `status` (ENUM: 'planned', 'completed', 'cancelled')
* `meeting_link` (VARCHAR, Nullable) — Ссылка на онлайн-комнату (Zoom/Meet).

## 5. Взаимодействие (Заявки и Чаты)

### `applications` (Заявки на сотрудничество)
* `id` (UUID, PK)
* `student_id` (UUID, FK -> users.id)
* `tutor_id` (UUID, FK -> users.id)
* `status` (ENUM: 'pending', 'accepted', 'rejected')
* `created_at` (TIMESTAMP)

### `chats`
Контекстные чаты, привязанные к заявкам.
* `id` (UUID, PK)
* `application_id` (UUID, Unique, FK -> applications.id)
* `created_at` (TIMESTAMP)

### `messages`
* `id` (UUID, PK)
* `chat_id` (UUID, FK -> chats.id)
* `sender_id` (UUID, FK -> users.id)
* `text` (TEXT)
* `created_at` (TIMESTAMP)

## 6. Тестирование и Аналитика

### `test_library` (База тестов)
* `id` (INT, PK)
* `subject` (VARCHAR) — Предмет.
* `topic` (VARCHAR) — Тема среза.
* `questions_json` (JSON) — JSON-структура вопросов и ответов.

### `student_results` (Назначенные и пройденные тесты учениками)
Отслеживание динамики успеваемости и учет эффективности.
* `id` (UUID, PK)
* `student_id` (UUID, FK -> users.id)
* `tutor_id` (UUID, FK -> users.id)
* `test_id` (INT, FK -> test_library.id)
* `type` (ENUM: 'initial_test', 'control_test') — Вводный или контрольный тест.
* `score` (DECIMAL, Nullable) — Оценка/балл (заполняется после прохождения).
* `assigned_at` (TIMESTAMP) — Время назначения.
* `completed_at` (TIMESTAMP, Nullable) — Время сдачи.

## 7. Отзывы

### `reviews` (Отзывы на репетиторов)
* `id` (UUID, PK)
* `student_id` (UUID, FK -> users.id)
* `tutor_id` (UUID, FK -> users.id)
* `lesson_id` (UUID, Nullable, FK -> lessons.id) — Привязка к проведенному уроку (опционально).
* `communication_score` (INT, 1-5) — Оценка за коммуникабельность/качество занятия.
* `text` (TEXT, Nullable) — Текст отзыва.
* `created_at` (TIMESTAMP)
