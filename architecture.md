# Архитектура приложения (Low-Code / Configuration-driven / Microservices)

## Стек технологий

| Компонент | Технология | Роль |
|---|---|---|
| API Gateway | Nginx | Единая точка входа, маршрутизация, CORS |
| IAM | Keycloak | Аутентификация, JWT, управление ролями |
| Data API | PostgREST | Автоматический REST API поверх PostgreSQL |
| База данных | PostgreSQL + pg_cron | Хранение данных, RLS, фоновые джобы |
| Custom Logic | FastAPI (Python) | Алгоритм подбора, push-уведомления, интеграции |

---

## Маршрутизация (Nginx)

```
/auth/*          →  Keycloak        (авторизация, токены)
/api/data/*      →  PostgREST       (CRUD без кода)
/api/custom/*    →  FastAPI         (сложная логика)
```

Nginx валидирует JWT на уровне gateway для `/api/data/` и `/api/custom/` через `auth_request` к Keycloak JWKS-эндпоинту. Запросы без валидного токена отклоняются на уровне прокси.

---

## Сервис 1: IAM — Keycloak

Отвечает за всё, что связано с идентификацией пользователей. Программирование не требуется — только конфигурация Realm.

### Конфигурация

- Realm: `tutorapp`
- Роли: `tutor`, `student`
- Клиент: `tutorapp-client` (тип: public, для мобильного приложения)
- JWT claims: `sub` (= user UUID), `realm_roles` (= [`tutor`] или [`student`])
- Event Listener: при событии `REGISTER` → HTTP webhook → `POST /api/custom/internal/user-created`

### Эндпоинты (стандартный OIDC, без кастомного кода)

| Метод | Путь | Назначение |
|---|---|---|
| `POST` | `/auth/realms/tutorapp/protocol/openid-connect/token` | Получить JWT по логину/паролю |
| `POST` | `/auth/realms/tutorapp/protocol/openid-connect/logout` | Инвалидировать токен |
| `GET` | `/auth/realms/tutorapp/protocol/openid-connect/userinfo` | Данные текущего пользователя |
| `GET` | `/auth/realms/tutorapp/protocol/openid-connect/certs` | Публичный JWKS для валидации JWT |

---

## Сервис 2: Data API — PostgREST

Автоматически генерирует REST API из таблиц и представлений PostgreSQL. **Код не пишется** — только SQL-миграции и RLS-политики.

### Принцип работы

1. Клиент отправляет запрос с заголовком `Authorization: Bearer <JWT>`.
2. PostgREST проверяет подпись токена через Keycloak JWKS.
3. Переключает роль БД: `web_tutor` или `web_student` в зависимости от `realm_roles` в JWT.
4. Устанавливает `request.jwt.claims` в контексте транзакции (доступно в RLS-политиках через `current_setting('request.jwt.claims', true)`).
5. RLS автоматически фильтрует строки по правилам.

### Роли PostgreSQL

| Роль БД | Keycloak-роль | Права |
|---|---|---|
| `anon` | (без токена) | Чтение публичных профилей репетиторов |
| `web_student` | `student` | CRUD своих данных + чтение профилей репетиторов |
| `web_tutor` | `tutor` | CRUD своих данных + чтение заявок/чатов |
| `authenticator` | — | Служебная роль PostgREST (переключает на нужную роль) |
| `service_role` | — | FastAPI-сервис (полный доступ, минуя RLS) |

### Эндпоинты (генерируются автоматически из таблиц)

Все эндпоинты поддерживают фильтрацию (`?field=eq.value`), пагинацию (`?limit=20&offset=0`), сортировку (`?order=created_at.desc`).

#### Профили

| Метод | Путь | RLS | Назначение |
|---|---|---|---|
| `GET` | `/api/data/tutor_profiles` | Публично | Список репетиторов (для поиска) |
| `GET` | `/api/data/tutor_profiles?user_id=eq.:id` | Публично | Карточка репетитора |
| `PATCH` | `/api/data/tutor_profiles?user_id=eq.:id` | Только свой | Редактировать профиль репетитора |
| `GET` | `/api/data/student_profiles?user_id=eq.:id` | Только свой | Профиль ученика |
| `PATCH` | `/api/data/student_profiles?user_id=eq.:id` | Только свой | Редактировать профиль ученика |

#### Теги

| Метод | Путь | RLS | Назначение |
|---|---|---|---|
| `GET` | `/api/data/tags` | Публично | Справочник тегов |
| `GET` | `/api/data/tutor_tags?tutor_id=eq.:id` | Публично | Теги репетитора |
| `POST` | `/api/data/tutor_tags` | Только свой | Добавить тег репетитору |
| `DELETE` | `/api/data/tutor_tags?tutor_id=eq.:id&tag_id=eq.:tag_id` | Только свой | Удалить тег |
| `GET` | `/api/data/student_preferred_tags?student_id=eq.:id` | Только свой | Желаемые теги ученика |
| `POST` | `/api/data/student_preferred_tags` | Только свой | Добавить желаемый тег |
| `DELETE` | `/api/data/student_preferred_tags?student_id=eq.:id&tag_id=eq.:tag_id` | Только свой | Удалить желаемый тег |

#### Расписание

| Метод | Путь | RLS | Назначение |
|---|---|---|---|
| `GET` | `/api/data/schedules?tutor_id=eq.:id` | Публично | Расписание репетитора |
| `POST` | `/api/data/schedules` | Только свой | Добавить слот |
| `PATCH` | `/api/data/schedules?id=eq.:id` | Только свой | Изменить слот |
| `DELETE` | `/api/data/schedules?id=eq.:id` | Только свой | Удалить слот |

#### Уроки

| Метод | Путь | RLS | Назначение |
|---|---|---|---|
| `GET` | `/api/data/lessons` | Свои уроки | Список уроков (ученик или репетитор) |
| `POST` | `/api/data/lessons` | `student` | Забронировать урок |
| `PATCH` | `/api/data/lessons?id=eq.:id` | Репетитор | Подтвердить / изменить статус / добавить meeting_link |

#### Заявки

| Метод | Путь | RLS | Назначение |
|---|---|---|---|
| `POST` | `/api/data/applications` | `student` | Подать заявку репетитору |
| `GET` | `/api/data/applications` | Свои заявки | Список заявок (входящих / исходящих) |
| `PATCH` | `/api/data/applications?id=eq.:id` | Репетитор | Принять / отклонить (`status`, `responded_at`) |

#### Чаты и сообщения

| Метод | Путь | RLS | Назначение |
|---|---|---|---|
| `GET` | `/api/data/chats` | Участники чата | Список чатов пользователя |
| `GET` | `/api/data/messages?chat_id=eq.:id` | Участники чата | История сообщений |
| `POST` | `/api/data/messages` | Участники чата | Отправить сообщение |

#### Тестирование

| Метод | Путь | RLS | Назначение |
|---|---|---|---|
| `GET` | `/api/data/test_library` | `tutor` | Список тестов |
| `GET` | `/api/data/student_results?student_id=eq.:id` | Свои результаты | История тестов ученика |
| `POST` | `/api/data/student_results` | `tutor` | Назначить тест ученику |
| `PATCH` | `/api/data/student_results?id=eq.:id` | `student` | Сдать тест (заполнить `score`, `completed_at`) |

#### Отзывы

| Метод | Путь | RLS | Назначение |
|---|---|---|---|
| `GET` | `/api/data/reviews?tutor_id=eq.:id` | Публично | Отзывы на репетитора |
| `POST` | `/api/data/reviews` | `student` | Оставить отзыв |

---

## Сервис 3: Custom Logic — FastAPI

Используется **только** для задач, которые невозможно решить средствами SQL или PostgREST. Подключается к PostgreSQL через `asyncpg` с ролью `service_role` (минуя RLS).

Все эндпоинты, кроме `/internal/*`, требуют заголовка `Authorization: Bearer <JWT>`. Middleware декодирует токен и извлекает `user_id` и `role`.

### Группа: Подбор репетиторов

#### `POST /api/custom/suggestions`

Запускает алгоритм подбора: Hard Filters (SQL) → Soft Scoring (Python) → сортировка по `score`.

**Тело запроса:**
```json
{
  "subject_id": 1,
  "max_price": 150000,
  "min_experience": 2,
  "verified_only": true,
  "schedule_slots": [
    {"day_of_week": 1, "start_time": "18:00", "end_time": "20:00"}
  ],
  "required_tag_ids": [3, 7],
  "weights": {
    "k1_effectiveness": 0.30,
    "k2_communication": 0.15,
    "k3_expertise": 0.20,
    "k4_responsiveness": 0.15,
    "k5_tags": 0.20
  }
}
```

> Если `weights` не переданы — используются дефолтные значения из алгоритма. Если ученик не указал теги, O5 = 1.0 для всех.

**Ответ:**
```json
[
  {
    "tutor_id": "uuid",
    "full_name": "...",
    "score": 0.847,
    "score_breakdown": {
      "o1": 0.72, "o2": 0.90, "o3": 0.65, "o4": 0.95, "o5": 0.80
    },
    "hourly_rate": 120000,
    "is_new": false
  }
]
```

### Группа: Внутренние (internal)

Не проксируются через Nginx наружу — только внутренняя сеть Docker.

#### `POST /api/custom/internal/user-created`

Вызывается Keycloak Event Listener при регистрации нового пользователя.

**Тело запроса (от Keycloak):**
```json
{
  "userId": "keycloak-uuid",
  "email": "user@example.com",
  "realmRole": "student"
}
```

**Действия сервиса:**
1. INSERT в `users` (`id` = Keycloak UUID, `email`, `role`).
2. INSERT пустой профиль в `tutor_profiles` или `student_profiles` в зависимости от роли.

**Ответ:** `201 Created`

### Группа: Push-уведомления (внутренний воркер)

FastAPI слушает PostgreSQL `NOTIFY`-события через `asyncpg` (LISTEN/NOTIFY). При поступлении события формирует и отправляет push через Firebase FCM.

**Каналы NOTIFY из БД-триггеров:**

| Канал | Триггер | Получатель push |
|---|---|---|
| `new_application` | INSERT в `applications` | Репетитор |
| `application_accepted` | UPDATE `applications.status = accepted` | Ученик |
| `new_message` | INSERT в `messages` | Участник чата (не отправитель) |
| `lesson_reminder` | pg_cron за 2 часа до `lessons.start_datetime` | Оба участника |
| `test_assigned` | INSERT в `student_results` | Ученик |

> Таблица `device_tokens` хранит FCM-токены устройств. FastAPI читает токен получателя и вызывает Firebase FCM API.

---

## Фоновые джобы — pg_cron (без Python)

Все периодические задачи выполняются внутри PostgreSQL. Python-код не требуется.

| Джоб | Расписание | SQL-функция | Назначение |
|---|---|---|---|
| Пересчёт рейтингов O1, O2, O3 | `0 3 * * *` (03:00 ежедневно) | `recalculate_tutor_ratings()` | Байесовский пересчёт метрик по новым отзывам и результатам тестов |
| Пересчёт O4 (отзывчивость) | `0 4 * * *` | `recalculate_responsiveness()` | Среднее время ответа на заявки |
| Напоминание об уроке | `*/15 * * * *` (каждые 15 мин) | `notify_upcoming_lessons()` | `pg_notify('lesson_reminder', ...)` за 2 часа до урока |
| Назначение контрольных тестов | `0 9 * * *` | `assign_control_tests()` | Если прошло 30 дней с вводного теста — INSERT контрольного |

---

## Жизненный цикл ключевых сценариев

### Регистрация

```
Мобильное приложение → POST /auth/.../token (Keycloak)
Keycloak → Event Listener → POST /api/custom/internal/user-created (FastAPI)
FastAPI → INSERT users + INSERT tutor/student_profiles (PostgreSQL)
```

### Подбор репетитора

```
Приложение → POST /api/custom/suggestions (FastAPI)
FastAPI → Hard Filter SQL (PostgreSQL, service_role)
FastAPI → Soft Scoring Python (расчёт Score по O1..O5 и весам k1..k5)
FastAPI → Ответ: отсортированный список с breakdown
```

### Принятие заявки → создание чата

```
Репетитор → PATCH /api/data/applications (PostgREST)
PostgREST → UPDATE applications SET status='accepted', responded_at=NOW()
БД-триггер → INSERT chats (application_id) + pg_notify('application_accepted')
FastAPI LISTEN → Firebase FCM push → Ученик
```

### Урок завершён → отзыв → пересчёт рейтинга

```
Репетитор → PATCH /api/data/lessons?status=completed (PostgREST)
Ученик → POST /api/data/reviews (PostgREST)
pg_cron 03:00 → recalculate_tutor_ratings() → UPDATE tutor_profiles
```
