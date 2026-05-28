# Backend Infrastructure & Docker Compose Setup

Документация для TASK-1.1: Настройка Docker Compose среды для локальной разработки

## Описание

Docker Compose конфигурация для локальной разработки платформы "Подбор репетиторов и планирования уроков". Включает интеграцию всех основных компонентов:

- **PostgreSQL** — основная база данных
- **Keycloak** — сервис аутентификации (SSO, OAuth2/OpenID Connect)  
- **PostgREST** — zero-code REST API к БД
- **FastAPI** — микросервис для сложной бизнес-логики
- **Nginx** — API Gateway и reverse proxy

## Вступление

Данная папка содержит полную инфраструктуру для поднятия всех сервисов локально в контейнерах. Структура оптимизирована для быстрой разработки и тестирования.

## Файловая структура

```
backend/
├── docker-compose.yml          # Главная конфигурация всех сервисов
├── .env                         # Переменные окружения (для локальной разработки)
├── .dockerignore               # Исключения при сборке Docker образов
├── .gitignore                  # Git исключения (создать при необходимости)
├── README.md                   # Эта документация
├── fastapi/                    # FastAPI микросервис
│   ├── Dockerfile              # Docker образ для FastAPI
│   ├── requirements.txt         # Python зависимости
│   └── src/                    # Исходный код приложения
│       ├── __init__.py
│       ├── main.py             # Entry point приложения
│       ├── config.py           # Конфигурация и переменные
│       ├── models/             # Pydantic модели (создать)
│       ├── routes/             # API endpoints (создать)
│       ├── services/           # Business logic (создать)
│       ├── middleware/         # Middleware компоненты (создать)
│       └── utils/              # Утилиты (создать)
├── postgres/                   # PostgreSQL конфигурация
│   └── init.sql                # SQL скрипт инициализации БД
├── nginx/                      # Nginx конфигурация
│   ├── Dockerfile              # Docker образ для Nginx
│   └── nginx.conf              # Конфигурация маршрутизации
└── keycloak/                   # Keycloak конфигурация (будет в TASK-1.2)
    └── realm-export.json       # Экспорт realm (создать)
```

## Сервисы и их роли

### PostgreSQL (порт 5432)
```yaml
- Контейнер: mgtu_postgres
- Образ: postgres:15-alpine
- БД: tutor_platform_db
- Данные: persistenter через volume postgres_data
```

**Учетные данные по умолчанию (в .env):**
- Username: `tutordb_user`
- Password: `tutordb_pass`
- Database: `tutor_platform_db`

### Keycloak (порт 8080)
```yaml
- Контейнер: mgtu_keycloak
- Образ: keycloak/keycloak:latest
- Функция: OAuth2/OpenID Connect провайдер
- Admin UI: http://localhost:8080/admin
```

**Учетные данные администратора:**
- Username: `admin`
- Password: `admin_password`

### PostgREST (порт 3000)
```yaml
- Контейнер: mgtu_postgrest
- Образ: postgrest/postgrest
- Функция: Автоматическое преобразование SQL schema в REST API
- Schema: api
- Доступ через: /api/data/
```

Примеры запросов:
```bash
# Читать из таблицы api.health_check
curl http://localhost/api/data/health_check

# С авторизацией JWT токеном
curl -H "Authorization: Bearer <token>" http://localhost/api/data/health_check
```

### FastAPI (порт 8000)
```yaml
- Контейнер: mgtu_fastapi
- Функция: Сложная бизнес-логика (алгоритм подбора, рейтинги)
- Доступ через: /api/custom/
- Документация: http://localhost:8000/docs
```

### Nginx (порты 80, 443)
```yaml
- Контейнер: mgtu_nginx
- Функция: Маршрутизация и reverse proxy
- Маршруты:
  - /auth/      → Keycloak
  - /api/data/  → PostgREST
  - /api/custom/ → FastAPI
  - /health     → FastAPI health check
```

## Критерии приемки (TASK-1.1)

✅ **Все контейнеры поднимаются**
- Каждый сервис имеет успешный запуск без ошибок
- Health checks настроены для критических сервисов

✅ **Сервисы видят друг друга во внутренней сети**
- Все контейнеры подключены к сети `tutor_network`
- Между сервисами доступна коммуникация по DNS имени контейнера

✅ **Правильная последовательность запуска**
- Используется `depends_on` и health checks для управления порядком запуска
- FastAPI ждет готовности PostgreSQL и Keycloak

## Быстрый старт

### Предварительные требования
- Docker Desktop (или Docker + Docker Compose)
- Git

### Запуск всех сервисов

```bash
cd backend
docker-compose up -d
```

Проверка статуса:
```bash
docker-compose ps
```

Логи:
```bash
docker-compose logs -f fastapi
docker-compose logs -f postgres
docker-compose logs -f keycloak
```

### Проверка доступности

```bash
# FastAPI health check
curl http://localhost/health

# PostgreSQL
psql -h localhost -U tutordb_user -d tutor_platform_db

# Keycloak admin console
open http://localhost:8080/admin

# PostgREST
curl http://localhost/api/data/health_check

# FastAPI docs
open http://localhost:8000/docs

# Nginx root
curl http://localhost/
```

### Остановка сервисов

```bash
docker-compose down
```

Удалить также все volumes (данные):
```bash
docker-compose down -v
```

## Управление сервисами

### Перестроить образ FastAPI
```bash
docker-compose build fastapi
```

### Перестартить конкретный сервис
```bash
docker-compose restart fastapi
```

### Вход в контейнер
```bash
docker-compose exec fastapi bash
docker-compose exec postgres psql -U tutordb_user -d tutor_platform_db
```

### Просмотр логов
```bash
# Все логи
docker-compose logs

# Последние 50 строк
docker-compose logs --tail=50

# В реальном времени
docker-compose logs -f

# Конкретного сервиса
docker-compose logs -f fastapi
```

## Переменные окружения

Основные переменные находятся в файле `.env`. Для production окружения:

- Изменить пароли (POSTGRES_PASSWORD, KEYCLOAK_ADMIN_PASSWORD)
- Установить реальный JWT_SECRET
- Настроить CORS_ORIGINS
- Включить SSL в Nginx

## Networking

Все контейнеры подключены к сети `tutor_network` (bridge network). Сервисы обращаются друг к другу по DNS имени контейнера:

```
postgres:5432
keycloak:8080
postgrest:3000
fastapi:8000
nginx:80
```

Пример снутри FastAPI:
```python
# Подключение к БД
database_url = "postgresql://user:pass@postgres:5432/db"

# Обращение к Keycloak
keycloak_url = "http://keycloak:8080"
```

## Volumes (Persistence)

- `postgres_data` — хранит данные PostgreSQL
- `keycloak_data` — хранит данные и кэш Keycloak

Данные сохраняются между перезапусками контейнеров.

## Следующие шаги

После успешного поднятия инфраструктуры:

1. **TASK-1.2** — Настроить Keycloak (создать realm, роли, OAuth2 клиент)
2. **TASK-1.3** — Проверить Nginx маршрутизацию
3. **TASK-2.1** — Создать миграции БД (полную схему)
4. **TASK-2.2** — Настроить PostgREST с JWT аутентификацией
5. **TASK-3.1** — Разработать FastAPI endpoints
