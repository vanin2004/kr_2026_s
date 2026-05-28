# Документация API платформы

Настоящая документация описывает программные интерфейсы (API) веб-сервисов платформы для подбора репетиторов и планирования уроков. Архитектура построена на базе микросервисной структуры и Low-Code парадигмы: Reverse Proxy (Nginx) маршрутизирует запросы между Keycloak (Авторизация), PostgREST (Data API) и FastAPI (Custom/Business Logic API).

## Базовые URL сервисов

Все запросы клиента проходят через единый API Gateway (Nginx):

*   **Авторизация и Учетные записи (Keycloak):** `https://api.domain.com/auth/`
*   **CRUD Data API (PostgREST):** `https://api.domain.com/api/data/`
*   **Сложная бизнес-логика (FastAPI):** `https://api.domain.com/api/custom/`

Ожидаемый формат взаимодействия — JSON (`application/json`).
Авторизация осуществляется посредством передачи заголовка: 
`Authorization: Bearer <JWT-token>`

---

## 1. Auth API (Identity & Access Management - Keycloak)
*Стандартные эндпоинты Keycloak (OpenID Connect / OAuth2)*

### `POST /auth/realms/{realm_name}/protocol/openid-connect/token`
Получение JWT-токена доступа (авторизация по паролю).
*   **Body (x-www-form-urlencoded):**
    *   `grant_type=password`
    *   `client_id=your_client_id`
    *   `username={email}`
    *   `password={password}`
*   **Ответ:** JSON с токеном `access_token`, `refresh_token` и временем жизни.

### `POST /auth/realms/{realm_name}/protocol/openid-connect/logout`
Завершение сеанса.
*   **Body:** `refresh_token`, `client_id`

*(Регистрация пользователей также может происходить через стандартный User Registration endpoint Keycloak)*

---

## 2. Data API (CRUD - PostgREST)
*Эндпоинты предоставляются автоматически (Zero-Boilerplate) из схемы БД. Доступ регламентируется на уровне БД с помощью Row-Level Security (RLS) на основе JWT.*

Все эндпоинты ниже поддерживают стандартные REST-методы (GET, POST, PATCH, DELETE) и параметры PostgREST (пагинация, фильтрация: `?select=...`, `?age=eq.18`).

### 2.1. Профили
*   **`GET /api/data/tutor_profiles`** 
    Получение списка репетиторов (публичная информация). Поддерживает фильтры по `specialization`, `hourly_rate` (например, `?hourly_rate=lte.150000`).
*   **`PATCH /api/data/tutor_profiles?user_id=eq.{ID}`** 
    Обновление профиля репетитора (доступно только самому репетитору через RLS).
*   **`GET /api/data/student_profiles`** / **`PATCH`**
    Операции с профилями учеников.

### 2.2. Расписание и Уроки
*   **`GET /api/data/schedules?tutor_id=eq.{ID}`**
    Получение доступных слотов для расписания конкретного репетитора.
*   **`POST /api/data/schedules`**
    Добавление слота расписания (только репетитор).
*   **`GET /api/data/lessons`**
    Получение списка своих уроков (RLS: ученик видит свои уроки, репетитор — свои).
*   **`POST /api/data/lessons`**
    Бронирование нового урока (со статусом `planned`).
*   **`PATCH /api/data/lessons?id=eq.{ID}`**
    Изменение статуса (например, отмена урока или прикрепление `meeting_link`).

### 2.3. Заявки и Чаты
*   **`GET /api/data/applications`**
    Список заявок на сотрудничество пользователей (входящие для репетитора, исходящие для ученика).
*   **`POST /api/data/applications`**
    Создание заявки на сотрудничество. В ответ создается триггером чат, либо приложение явно создает чат после подтверждения.
*   **`PATCH /api/data/applications?id=eq.{ID}`**
    Принятие (`accepted`) или отклонение (`rejected`) заявки репетитором.
*   **`GET /api/data/chats`** 
    Список чатов, к которым имеет доступ текущий пользователь.
*   **`GET /api/data/messages?chat_id=eq.{ID}`** 
    Получение истории сообщений по конкретному чату (поддерживает сортировку `order=created_at.desc`).
*   **`POST /api/data/messages`**
    Отправка текстового сообщения в чат.

### 2.4. Тесты и Отзывы
*   **`GET /api/data/test_library`**
    Получение списка и содержимого базовых тестов.
*   **`GET /api/data/student_results`**
    Просмотр результатов сдачи тестов.
*   **`POST /api/data/student_results`**
    Назначение или сохранение результатов теста. (Частично может управляться триггерами БД).
*   **`GET /api/data/reviews?tutor_id=eq.{ID}`**
    Список отзывов на преподавателя.
*   **`POST /api/data/reviews`**
    Публикация отзыва и оценки за проведенный урок.

---

## 3. Custom Business Logic API (FastAPI)
*Сервисы со сложной логикой, требующие вычислений на стороне бэкенда. Проверяют JWT, полученный от Keycloak перед выполнением логики.*

### `POST /api/custom/suggestions`
**Описание:** Умный алгоритм подбора (Recommendation Engine). Возвращает отранжированный список подходящих репетиторов.
*   **Headers:** `Authorization: Bearer <JWT>`
*   **Body (JSON Request):**
    ```json
    {
      "filters": {
        "subject": "Math",
        "max_hourly_rate": 200000,
        "min_experience_years": 2,
        "matches_schedule": [
          {"day": 1, "start": "18:00"}
        ]
      },
      "weights": {
        "efficiency": 0.5,
        "communication": 0.2,
        "tags_match": 0.3
      },
      "desired_tags": [1, 5, 12]
    }
    ```
*   **Response (JSON):**
    ```json
    {
      "results": [
        {
          "tutor_id": "uuid-...",
          "score": 4.87,
          "profile": {
            "full_name": "Иванов Иван",
            "hourly_rate": 150000,
            "rating_overall": 4.9,
            "matched_tags": [1, 5]
          }
        }
      ],
      "total_found": 1
    }
    ```

### `POST /api/custom/jobs/recalculate-ratings`
**Описание:** Системный эндпоинт (может быть вызван по cron-расписанию или через внутренний триггер). Пересчитывает байесовский рейтинг преподавателей (метрики O1...O5) на базе новых отзывов и результатов тестов.
*   **Authentication:** Basic Auth / Private network only
*   **Response:** `{"status": "ok", "recalculated_tutors": 145}`
