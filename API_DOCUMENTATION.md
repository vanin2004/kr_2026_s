# Tutor Platform API - Полная документация

**Версия:** 1.0.0  
**Дата:** 28 Май 2026  
**Статус:** Production-Ready

---

## Оглавление

1. [Обзор системы](#обзор-системы)
2. [Архитектура](#архитектура)
3. [Аутентификация](#аутентификация)
4. [API Endpoints](#api-endpoints)
5. [Модели данных](#модели-данных)
6. [Примеры использования](#примеры-использования)
7. [Ошибки и статус коды](#ошибки-и-статус-коды)
8. [Постоянные хранилища (БД)](#постоянные-хранилища-бд)

---

## Обзор системы

**Tutor Platform** — это микросервисная платформа для подбора и управления уроками между студентами и репетиторами.

### Основные возможности:
✅ Интеллектуальный подбор репетиторов по критериям  
✅ Расчет рейтинга репетиторов (эффективность/общение)  
✅ Управление расписанием и уроками  
✅ Система чатов и рецензий  
✅ Встроенное тестирование  
✅ Keycloak SSO аутентификация  

---

## Архитектура

### Компоненты системы

```
┌─────────────────────────────────────────────────┐
│         Мобильное приложение / Client            │
└────────────────────┬────────────────────────────┘
                     │ HTTP(S)
                     ▼
┌─────────────────────────────────────────────────┐
│      Nginx API Gateway (Port 80/443)            │
│  ├─ /auth/    → Keycloak                       │
│  ├─ /api/data/ → PostgREST (Auto-generated)    │
│  └─ /api/custom/ → FastAPI (Custom Logic)      │
└──────┬────────────┬────────────┬────────────────┘
       │            │            │
       ▼            ▼            ▼
   ┌────────┐ ┌──────────┐ ┌─────────┐
   │Keycloak│ │PostgREST │ │ FastAPI │
   │(OAuth) │ │ (REST)   │ │ (Logic) │
   └────┬───┘ └─────┬────┘ └────┬────┘
        │           │            │
        └───────────┼────────────┘
                    │
                    ▼
        ┌───────────────────────┐
        │   PostgreSQL (БД)     │
        │ - api schema (RLS)    │
        │ - keycloak schema     │
        └───────────────────────┘
```

### Сервисы и версии

| Сервис | Порт | Версия | Роль |
|--------|------|--------|------|
| **Nginx** | 80/443 | Latest | API Gateway |
| **FastAPI** | 8000 | 0.104.1 | Custom Business Logic |
| **PostgREST** | 3000 | Latest | Auto-REST API |
| **Keycloak** | 8080 | Latest | OAuth2/OIDC SSO |
| **PostgreSQL** | 5432 | Latest | Main Database |

---

## Аутентификация

### Keycloak OIDC

**Конфигурация:**
```
Сервер:     http://keycloak:8080
Realm:      tutor-platform
Client ID:  tutor-api
Admin URL:  http://localhost:8080/admin
```

**Учетные данные (dev):**
```
Пользователь: admin
Пароль:       admin_password
```

###获token (JWT)

#### 1. Получить токен доступа

```bash
# POST запрос к Keycloak
curl -X POST http://keycloak:8080/realms/tutor-platform/protocol/openid-connect/token \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "grant_type=password" \
  -d "client_id=tutor-api" \
  -d "username=student_user@example.com" \
  -d "password=password123"
```

**Ответ:**
```json
{
  "access_token": "eyJhbGc...",
  "expires_in": 300,
  "refresh_expires_in": 1800,
  "refresh_token": "eyJhbGc...",
  "token_type": "Bearer",
  "id_token": "eyJhbGc...",
  "not-before-policy": 0,
  "session_state": "a1b2c3d4",
  "scope": "openid profile email"
}
```

#### 2. Использовать токен в запросах

```bash
curl -H "Authorization: Bearer <access_token>" \
  http://localhost/api/custom/auth-check
```

### Структура JWT токена

```json
{
  "exp": 1234567890,
  "iat": 1234567890,
  "jti": "jti123",
  "iss": "http://keycloak:8080/realms/tutor-platform",
  "aud": "account",
  "sub": "user-uuid-here",
  "typ": "Bearer",
  "azp": "tutor-api",
  "session_state": "a1b2c3d4",
  "name": "John Doe",
  "given_name": "John",
  "family_name": "Doe",
  "email": "john.doe@example.com",
  "email_verified": true,
  "realm_access": {
    "roles": ["student", "default-roles-tutor-platform"]
  },
  "resource_access": {
    "account": {
      "roles": ["manage-account", "view-profile"]
    }
  }
}
```

---

## API Endpoints

### Базовый URL

```
Разработка:  http://localhost/api/custom/
Production:  https://api.tutorplatform.com/api/custom/
```

### Маршруты за Nginx

```
GET  /health                          → Проверка здоровья FastAPI
GET  /db-check                        → Проверка БД
GET  /auth-check                      → Проверка токена [AUTH]
POST /test-data                       → Добавить тестовые данные
POST /suggestions                     → Подобрать репетиторов [AUTH]
POST /jobs/recalculate-ratings        → Пересчитать рейтинги [AUTH]
```

---

### 1. GET /health

**Описание:** Проверка здоровья FastAPI сервиса

**Аутентификация:** Не требуется  
**Метод:** GET

**Example запроса:**
```bash
curl http://localhost/api/custom/health
```

**Пример ответа (200 OK):**
```json
{
  "status": "healthy",
  "timestamp": "2026-05-28T14:30:00Z",
  "service": "tutor-platform-api",
  "version": "1.0.0"
}
```

---

### 2. GET /db-check

**Описание:** Проверка подключения к базе данных

**Аутентификация:** Не требуется  
**Метод:** GET

**Пример запроса:**
```bash
curl http://localhost/api/custom/db-check
```

**Пример ответа (200 OK):**
```json
{
  "database": "connected",
  "database_name": "tutor_platform_db",
  "postgres_version": "15.1",
  "timestamp": "2026-05-28T14:30:15Z"
}
```

**Пример ошибки (500 Internal Server Error):**
```json
{
  "detail": "Database connection failed"
}
```

---

### 3. GET /auth-check

**Описание:** Проверка валидности JWT токена  
**Аутентификация:** Требуется Bearer токен  
**Метод:** GET

**Заголовки:**
```
Authorization: Bearer <jwt_token>
```

**Пример запроса:**
```bash
curl -H "Authorization: Bearer eyJhbGc..." \
  http://localhost/api/custom/auth-check
```

**Пример ответа (200 OK):**
```json
{
  "authenticated": true,
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "john.doe@example.com",
  "roles": ["student"],
  "token_expires_in": 280
}
```

**Пример ошибки (401 Unauthorized):**
```json
{
  "detail": "Not authenticated"
}
```

---

### 4. POST /test-data

**Описание:** Добавить тестовые данные репетитора (только для разработки)  
**Аутентификация:** Не требуется  
**Метод:** POST

**Тело запроса:**
```json
{
  "email": "test_tutor@example.com",
  "full_name": "Test Tutor",
  "specialization": "Mathematics",
  "hourly_rate": 50,
  "years_experience": 5,
  "tags": ["Algebra", "Geometry", "Calculus"]
}
```

**Пример запроса:**
```bash
curl -X POST http://localhost/api/custom/test-data \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test_tutor@example.com",
    "full_name": "Test Tutor",
    "specialization": "Mathematics",
    "hourly_rate": 50,
    "years_experience": 5,
    "tags": ["Algebra", "Geometry", "Calculus"]
  }'
```

**Пример ответа (201 Created):**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "test_tutor@example.com",
  "full_name": "Test Tutor",
  "specialization": "Mathematics",
  "hourly_rate": 50,
  "years_experience": 5,
  "rating_efficiency": 3.5,
  "rating_communication": 3.5,
  "rating_overall": 3.5,
  "created_at": "2026-05-28T14:30:30Z"
}
```

---

### 5. POST /suggestions ⭐ **ГЛАВНЫЙ ENDPOINT**

**Описание:** Интеллектуальный подбор репетиторов по критериям  
**Аутентификация:** Требуется Bearer токен  
**Метод:** POST

#### Алгоритм подбора

Система использует **взвешенный алгоритм скоринга** с 5 факторами:

```
Итоговый Score = (E × w₁) + (C × w₂) + (O × w₃) + (R × w₄) + (T × w₅)

где:
  E = rating_efficiency / 5.0       (Эффективность обучения)
  C = rating_communication / 5.0    (Коммуникативные навыки)
  O = rating_overall / 5.0          (Общий рейтинг)
  R = responsiveness (0-1)          (Оперативность)
  T = tag_overlap_ratio (0-1)       (Совпадение навыков)
  
  w₁ = 0.30 (вес эффективности)
  w₂ = 0.15 (вес общения)
  w₃ = 0.20 (вес общего рейтинга)
  w₄ = 0.15 (вес оперативности)
  w₅ = 0.20 (вес навыков)
```

#### Структура запроса

```json
{
  "subject": "Mathematics",
  "max_rate": 100,
  "min_experience": 2,
  "desired_tags": ["Algebra", "Geometry"],
  "weights": {
    "efficiency": 0.30,
    "communication": 0.15,
    "overall": 0.20,
    "responsiveness": 0.15,
    "tags": 0.20
  }
}
```

**Параметры:**

| Параметр | Тип | Обязательный | Описание | Пример |
|----------|-----|-------------|----------|--------|
| `subject` | string | Да | Предмет обучения | "Mathematics" |
| `max_rate` | integer | Да | Макс. ставка/час (USD) | 150 |
| `min_experience` | integer | Да | Мин. опыт (лет) | 2 |
| `desired_tags` | array[string] | Нет | Желаемые навыки | ["Algebra", "Calculus"] |
| `weights.efficiency` | float (0-1) | Нет | Вес эффективности | 0.30 |
| `weights.communication` | float (0-1) | Нет | Вес общения | 0.15 |
| `weights.overall` | float (0-1) | Нет | Вес рейтинга | 0.20 |
| `weights.responsiveness` | float (0-1) | Нет | Вес оперативности | 0.15 |
| `weights.tags` | float (0-1) | Нет | Вес совпадения | 0.20 |

#### Пример запроса

```bash
curl -X POST http://localhost/api/custom/suggestions \
  -H "Authorization: Bearer eyJhbGc..." \
  -H "Content-Type: application/json" \
  -d '{
    "subject": "Mathematics",
    "max_rate": 100,
    "min_experience": 2,
    "desired_tags": ["Algebra", "Calculus"],
    "weights": {
      "efficiency": 0.30,
      "communication": 0.15,
      "overall": 0.20,
      "responsiveness": 0.15,
      "tags": 0.20
    }
  }'
```

#### Пример ответа (200 OK)

```json
[
  {
    "id": "550e8400-e29b-41d4-a716-446655440001",
    "full_name": "Dr. Sarah Johnson",
    "specialization": "Mathematics",
    "hourly_rate": 75,
    "years_experience": 8,
    "bio": "Ph.D. in Mathematics, 8 years teaching experience",
    "rating_efficiency": 4.8,
    "rating_communication": 4.7,
    "rating_overall": 4.75,
    "tags": ["Algebra", "Calculus", "Statistics"],
    "total_reviews": 42,
    "lessons_completed": 156,
    "match_score": 92.5,
    "match_breakdown": {
      "efficiency_score": 4.8,
      "communication_score": 4.7,
      "overall_score": 4.75,
      "responsiveness": 0.95,
      "tag_overlap": 0.89
    }
  },
  {
    "id": "550e8400-e29b-41d4-a716-446655440002",
    "full_name": "Michael Chen",
    "specialization": "Mathematics",
    "hourly_rate": 55,
    "years_experience": 5,
    "bio": "M.Sc. in Applied Mathematics, passionate educator",
    "rating_efficiency": 4.5,
    "rating_communication": 4.3,
    "rating_overall": 4.4,
    "tags": ["Algebra", "Calculus"],
    "total_reviews": 28,
    "lessons_completed": 89,
    "match_score": 87.3,
    "match_breakdown": {
      "efficiency_score": 4.5,
      "communication_score": 4.3,
      "overall_score": 4.4,
      "responsiveness": 0.9,
      "tag_overlap": 1.0
    }
  }
]
```

**Отсортирован по:** `match_score` (от высокого к низкому)

#### Пример ошибки (401 Unauthorized)

```json
{
  "detail": "Not authenticated"
}
```

---

### 6. POST /jobs/recalculate-ratings

**Описание:** Пересчитать рейтинги репетиторов (байесовский расчет)  
**Аутентификация:** Требуется Bearer токен  
**Метод:** POST

#### Формула расчета

**Рейтинг эффективности:**
```
efficiency_rating = (control_test_score - initial_test_score) / 20 × 5

Нормализуется к диапазону 1-5
```

**Рейтинг общения:**
```
communication_rating = AVERAGE(review.communication_score для всех отзывов)

Берется среднее значение оценок общения (1-5)
```

**Общий рейтинг:**
```
overall_rating = (efficiency_rating × 0.4) + (communication_rating × 0.6)
```

#### Структура запроса

```json
{
  "run_efficiency": true,
  "run_communication": true
}
```

**Параметры:**

| Параметр | Тип | Описание |
|----------|-----|---------|
| `run_efficiency` | boolean | Пересчитать рейтинг эффективности |
| `run_communication` | boolean | Пересчитать рейтинг общения |

#### Пример запроса

```bash
curl -X POST http://localhost/api/custom/jobs/recalculate-ratings \
  -H "Authorization: Bearer eyJhbGc..." \
  -H "Content-Type: application/json" \
  -d '{
    "run_efficiency": true,
    "run_communication": true
  }'
```

#### Пример ответа (200 OK)

```json
{
  "status": "completed",
  "timestamp": "2026-05-28T14:35:00Z",
  "execution_time_seconds": 2.34,
  "tutors_updated": 12,
  "efficiency_updates": {
    "processed": 8,
    "skipped": 4,
    "average_new_efficiency": 4.2
  },
  "communication_updates": {
    "processed": 12,
    "average_new_communication": 4.5
  },
  "summary": "Successfully updated 12 tutors ratings"
}
```

#### Пример ошибки (401 Unauthorized)

```json
{
  "detail": "Not authenticated"
}
```

---

## Модели данных

### Request Models

#### SuggestionRequest

```json
{
  "subject": "Mathematics",
  "max_rate": 100,
  "min_experience": 2,
  "desired_tags": ["Algebra", "Calculus"],
  "weights": {
    "efficiency": 0.30,
    "communication": 0.15,
    "overall": 0.20,
    "responsiveness": 0.15,
    "tags": 0.20
  }
}
```

#### RecalculateJobsRequest

```json
{
  "run_efficiency": true,
  "run_communication": true
}
```

### Response Models

#### TutorResponse

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440001",
  "full_name": "Dr. Sarah Johnson",
  "specialization": "Mathematics",
  "hourly_rate": 75,
  "years_experience": 8,
  "bio": "Ph.D. in Mathematics",
  "rating_efficiency": 4.8,
  "rating_communication": 4.7,
  "rating_overall": 4.75,
  "tags": ["Algebra", "Calculus"],
  "total_reviews": 42,
  "lessons_completed": 156,
  "match_score": 92.5,
  "match_breakdown": {
    "efficiency_score": 4.8,
    "communication_score": 4.7,
    "overall_score": 4.75,
    "responsiveness": 0.95,
    "tag_overlap": 0.89
  }
}
```

#### HealthResponse

```json
{
  "status": "healthy",
  "timestamp": "2026-05-28T14:30:00Z",
  "service": "tutor-platform-api",
  "version": "1.0.0"
}
```

#### AuthCheckResponse

```json
{
  "authenticated": true,
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "john.doe@example.com",
  "roles": ["student"],
  "token_expires_in": 280
}
```

---

## Примеры использования

### Сценарий 1: Студент ищет репетитора по математике

#### Шаг 1: Получить токен доступа

```bash
TOKEN=$(curl -s -X POST http://keycloak:8080/realms/tutor-platform/protocol/openid-connect/token \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "grant_type=password" \
  -d "client_id=tutor-api" \
  -d "username=student@example.com" \
  -d "password=password123" | jq -r '.access_token')

echo "Token: $TOKEN"
```

#### Шаг 2: Проверить токен до использования

```bash
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost/api/custom/auth-check | jq
```

#### Шаг 3: Получить рекомендации

```bash
curl -X POST http://localhost/api/custom/suggestions \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "subject": "Mathematics",
    "max_rate": 80,
    "min_experience": 3,
    "desired_tags": ["Algebra", "Calculus"],
    "weights": {
      "efficiency": 0.40,
      "communication": 0.20,
      "overall": 0.15,
      "responsiveness": 0.15,
      "tags": 0.10
    }
  }' | jq
```

**Ожидаемый результат:** Список репетиторов отсортирован по релевантности

---

### Сценарий 2: Администратор пересчитывает рейтинги

#### Шаг 1: Аутентифицироваться как администратор

```bash
ADMIN_TOKEN=$(curl -s -X POST http://keycloak:8080/realms/tutor-platform/protocol/openid-connect/token \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "grant_type=password" \
  -d "client_id=tutor-api" \
  -d "username=admin@example.com" \
  -d "password=admin_password" | jq -r '.access_token')
```

#### Шаг 2: Запустить пересчет рейтингов

```bash
curl -X POST http://localhost/api/custom/jobs/recalculate-ratings \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "run_efficiency": true,
    "run_communication": true
  }' | jq
```

**Ожидаемый результат:** Статус выполнения задания и кол-во обновленных репетиторов

---

### Сценарий 3: Добавить тестовых репетиторов

```bash
for i in {1..3}; do
  curl -X POST http://localhost/api/custom/test-data \
    -H "Content-Type: application/json" \
    -d "{
      \"email\": \"tutor$i@example.com\",
      \"full_name\": \"Test Tutor $i\",
      \"specialization\": \"Mathematics\",
      \"hourly_rate\": $((50 + i * 10)),
      \"years_experience\": $((3 + i)),
      \"tags\": [\"Algebra\", \"Calculus\", \"Geometry\"]
    }"
  echo "\nTutor $i created"
  sleep 1
done
```

---

## Ошибки и статус коды

### HTTP Status Codes

| Код | Описание | Пример |
|-----|---------|--------|
| **200** | OK | Запрос успешно обработан |
| **201** | Created | Ресурс успешно создан |
| **400** | Bad Request | Некорректное тело запроса |
| **401** | Unauthorized | Требуется аутентификация |
| **403** | Forbidden | Нет прав доступа |
| **404** | Not Found | Ресурс не найден |
| **422** | Validation Error | Ошибка валидации данных |
| **500** | Internal Server Error | Ошибка сервера |
| **503** | Service Unavailable | Сервис недоступен |

### Примеры ответов об ошибках

#### 400 Bad Request

```json
{
  "detail": [
    {
      "loc": ["body", "subject"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

#### 401 Unauthorized

```json
{
  "detail": "Not authenticated"
}
```

#### 422 Validation Error

```json
{
  "detail": [
    {
      "loc": ["body", "max_rate"],
      "msg": "ensure this value is greater than 0",
      "type": "value_error.number.not_gt"
    }
  ]
}
```

#### 500 Internal Server Error

```json
{
  "detail": "Internal server error"
}
```

---

## Постоянные хранилища (БД)

### Схема базы данных

#### Таблица: `api.users`

```sql
CREATE TABLE api.users (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  email VARCHAR(255) UNIQUE NOT NULL,
  password_hash VARCHAR(255),
  role VARCHAR(50),  -- 'tutor', 'student', 'admin'
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### Таблица: `api.tutor_profiles`

```sql
CREATE TABLE api.tutor_profiles (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES api.users(id) ON DELETE CASCADE,
  full_name VARCHAR(255) NOT NULL,
  specialization VARCHAR(255),
  bio TEXT,
  hourly_rate DECIMAL(10, 2),
  years_experience INTEGER,
  rating_efficiency DECIMAL(3, 2) DEFAULT 3.5,  -- 1-5
  rating_communication DECIMAL(3, 2) DEFAULT 3.5,  -- 1-5
  rating_overall DECIMAL(3, 2) DEFAULT 3.5,  -- 1-5
  total_reviews INTEGER DEFAULT 0,
  lessons_completed INTEGER DEFAULT 0,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  
  CONSTRAINT rating_range CHECK (rating_efficiency >= 1 AND rating_efficiency <= 5)
);
```

#### Таблица: `api.tutor_tags`

```sql
CREATE TABLE api.tutor_tags (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tutor_id UUID NOT NULL REFERENCES api.tutor_profiles(id) ON DELETE CASCADE,
  tag_id UUID NOT NULL REFERENCES api.tags(id),
  
  UNIQUE(tutor_id, tag_id)
);
```

#### Таблица: `api.tags`

```sql
CREATE TABLE api.tags (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name VARCHAR(100) UNIQUE NOT NULL,
  category VARCHAR(50),
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### Таблица: `api.student_profiles`

```sql
CREATE TABLE api.student_profiles (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES api.users(id) ON DELETE CASCADE,
  full_name VARCHAR(255) NOT NULL,
  grade_level INTEGER,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### Таблица: `api.schedules`

```sql
CREATE TABLE api.schedules (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tutor_id UUID NOT NULL REFERENCES api.tutor_profiles(id) ON DELETE CASCADE,
  day_of_week INTEGER,  -- 0=Monday, 6=Sunday
  start_time TIME NOT NULL,
  end_time TIME NOT NULL,
  is_available BOOLEAN DEFAULT true,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### Таблица: `api.lessons`

```sql
CREATE TABLE api.lessons (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  student_id UUID NOT NULL REFERENCES api.student_profiles(id) ON DELETE CASCADE,
  tutor_id UUID NOT NULL REFERENCES api.tutor_profiles(id) ON DELETE CASCADE,
  start_datetime TIMESTAMP NOT NULL,
  end_datetime TIMESTAMP NOT NULL,
  status VARCHAR(50),  -- 'scheduled', 'completed', 'cancelled'
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### Таблица: `api.reviews`

```sql
CREATE TABLE api.reviews (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  student_id UUID NOT NULL REFERENCES api.student_profiles(id) ON DELETE CASCADE,
  tutor_id UUID NOT NULL REFERENCES api.tutor_profiles(id) ON DELETE CASCADE,
  communication_score INTEGER CHECK (communication_score >= 1 AND communication_score <= 5),
  text TEXT,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### Таблица: `api.student_results`

```sql
CREATE TABLE api.student_results (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  student_id UUID NOT NULL REFERENCES api.student_profiles(id) ON DELETE CASCADE,
  tutor_id UUID NOT NULL REFERENCES api.tutor_profiles(id) ON DELETE CASCADE,
  test_id UUID NOT NULL REFERENCES api.test_library(id),
  type VARCHAR(50),  -- 'initial_test', 'control_test'
  score DECIMAL(5, 2) NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### Таблица: `api.test_library`

```sql
CREATE TABLE api.test_library (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  subject VARCHAR(100),
  topic VARCHAR(255),
  questions_json JSONB,  -- Array of questions
  difficulty_level VARCHAR(50),  -- 'easy', 'medium', 'hard'
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### Таблица: `api.applications`

```sql
CREATE TABLE api.applications (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  student_id UUID NOT NULL REFERENCES api.student_profiles(id) ON DELETE CASCADE,
  tutor_id UUID NOT NULL REFERENCES api.tutor_profiles(id) ON DELETE CASCADE,
  status VARCHAR(50) DEFAULT 'pending',  -- 'pending', 'accepted', 'rejected'
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  
  UNIQUE(student_id, tutor_id)
);
```

#### Таблица: `api.chats`

```sql
CREATE TABLE api.chats (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  application_id UUID NOT NULL UNIQUE REFERENCES api.applications(id) ON DELETE CASCADE,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### Таблица: `api.messages`

```sql
CREATE TABLE api.messages (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  chat_id UUID NOT NULL REFERENCES api.chats(id) ON DELETE CASCADE,
  sender_id UUID NOT NULL REFERENCES api.users(id) ON DELETE CASCADE,
  text TEXT NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Row-Level Security (RLS)

Все таблицы защищены RLS политиками:

```sql
-- Пример политики для tutor_profiles
ALTER TABLE api.tutor_profiles ENABLE ROW LEVEL SECURITY;

CREATE POLICY tutor_profiles_select ON api.tutor_profiles
  FOR SELECT USING (true);  -- Public read

CREATE POLICY tutor_profiles_update ON api.tutor_profiles
  FOR UPDATE USING (user_id = current_user_id());

CREATE POLICY tutor_profiles_delete ON api.tutor_profiles
  FOR DELETE USING (user_id = current_user_id());
```

---

## Быстрый старт

### 1. Запуск контейнеров

```bash
cd backend
docker-compose up -d
```

### 2. Проверка здоровья

```bash
# FastAPI
curl http://localhost/api/custom/health

# Database
curl http://localhost/api/custom/db-check

# Keycloak (admin console)
open http://localhost:8080/admin
```

### 3. Получить токен

```bash
TOKEN=$(curl -s -X POST http://localhost:8080/realms/tutor-platform/protocol/openid-connect/token \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "grant_type=password" \
  -d "client_id=tutor-api" \
  -d "username=admin@example.com" \
  -d "password=admin_password" | jq -r '.access_token')

echo $TOKEN
```

### 4. Добавить тестовых репетиторов

```bash
curl -X POST http://localhost/api/custom/test-data \
  -H "Content-Type: application/json" \
  -d '{
    "email": "math_tutor@example.com",
    "full_name": "John Smith",
    "specialization": "Mathematics",
    "hourly_rate": 75,
    "years_experience": 5,
    "tags": ["Algebra", "Calculus"]
  }'
```

### 5. Получить рекомендации

```bash
curl -X POST http://localhost/api/custom/suggestions \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "subject": "Mathematics",
    "max_rate": 100,
    "min_experience": 2,
    "desired_tags": ["Algebra"],
    "weights": {
      "efficiency": 0.30,
      "communication": 0.15,
      "overall": 0.20,
      "responsiveness": 0.15,
      "tags": 0.20
    }
  }' | jq
```

---

## Debugging & Logs

### Просмотр логов

```bash
# Все сервисы
docker-compose logs -f

# Только FastAPI
docker-compose logs -f fastapi

# С временными метками
docker-compose logs -f --timestamps fastapi
```

### Вход в контейнер

```bash
docker-compose exec fastapi bash
# или
docker-compose exec fastapi python -m ipdb
```

### Тестирование

```bash
cd backend/fastapi
pytest -v --tb=short
pytest -k "test_suggestions" -v
```

---

## Дополнительные ресурсы

### Документация

- FastAPI: https://fastapi.tiangolo.com/
- Keycloak: https://www.keycloak.org/documentation
- PostgreSQL: https://www.postgresql.org/docs/
- PostgREST: https://postgrest.org/

### Файлы проекта

- [DEVELOPMENT.md](backend/fastapi/DEVELOPMENT.md) — Руководство разработчика
- [TESTING.md](backend/fastapi/TESTING.md) — Инструкции по тестированию
- [docker-compose.yml](backend/docker-compose.yml) — Конфигурация сервисов
- [requirements.txt](backend/fastapi/requirements.txt) — Python зависимости

### Контакты поддержки

- GitHub Issues: [Issues](https://github.com/tutorplatform/issues)
- Email: support@tutorplatform.com
- Slack: #api-support

---

**Последнее обновление:** 28 Май 2026  
**Версия документации:** 1.0.0  
**Статус:** Production-Ready
