# Database Troubleshooting Guide

**Дата:** 29 Май 2026  
**Статус:** Clean Slate Architecture

---

## Архитектура БД

- ✅ Все миграции удалены
- ✅ БД инициализируется с нуля при каждом запуске
- ✅ Нет сохранения старых данных между запусками
- ✅ Используется `init.sql` для полной инициализации

---

## Запуск на удаленном сервере

### Инициализация БД

```bash
# 1. Перейти в директорию backend
cd backend

# 2. Запустить все сервисы (БД инициализируется автоматически)
docker-compose up -d

# 3. Проверить статус PostgreSQL
docker-compose logs postgres | tail -20
```

**Ожидаемый вывод:**
```
postgresql (1) LOG: database system is ready to accept connections
```

### Проверка инициализации

```bash
# Проверить создание схемы api
docker-compose exec postgres psql -U tutordb_user -d tutor_platform_db -c \
  "SELECT schema_name FROM information_schema.schemata WHERE schema_name = 'api';"

# Проверить таблицы в схеме api
docker-compose exec postgres psql -U tutordb_user -d tutor_platform_db -c \
  "\dt api.*"
```

---

## Тестирование через Python скрипты

### Основной тестовый скрипт

```bash
# Полная демонстрация API
python3 api_client.py full

# Быстрый поиск репетиторов
python3 api_client.py quick
```

### Примеры использования Python

```python
from api_client import TutorPlatformClient, Config

# Инициализация клиента
client = TutorPlatformClient()

# Проверка здоровья
client.health_check()

# Проверка БД
client.db_check()

# Аутентификация
client.authenticate("admin@example.com", "admin_password")

# Поиск репетиторов
suggestions = client.get_suggestions(
    subject="Mathematics",
    max_rate=100,
    min_experience=2
)
```

---

## Общие проблемы и решения

### ❌ PostgreSQL не инициализируется

**Решение:**
```bash
# Удалить старые данные
docker volume rm postgres_data

# Переустановить контейнеры
docker-compose down
docker-compose up -d postgres

# Проверить логи
docker-compose logs postgres -f
```

### ❌ Ошибка подключения к БД

**Проверка:**
```bash
# Проверить запущены ли контейнеры
docker-compose ps

# Проверить доступность PostgreSQL
docker-compose exec postgres pg_isready -U tutordb_user -d tutor_platform_db

# Проверить логи
docker-compose logs postgres
```

### ❌ FastAPI не может подключиться к БД

**Решение:**
```bash
# Убедиться что PostgreSQL готов перед запуском FastAPI
docker-compose logs postgres | grep "database system is ready"

# Перезапустить FastAPI
docker-compose restart fastapi

# Проверить логи FastAPI
docker-compose logs fastapi -f
```

---

## Проверка данных

### Просмотр всех таблиц в схеме api

```python
from api_client import TutorPlatformClient

client = TutorPlatformClient()

# Прямой запрос к БД
import asyncio
from sqlalchemy import text
from src.db.session import get_db

async def check_tables():
    async for db in get_db():
        result = await db.execute(text(
            "SELECT table_name FROM information_schema.tables "
            "WHERE table_schema = 'api' ORDER BY table_name"
        ))
        tables = result.fetchall()
        for (table,) in tables:
            print(f"  - {table}")
```

### Ожидаемые таблицы

```
- applications
- chats
- health_check
- lessons
- messages
- reviews
- schedules
- student_profiles
- student_results
- tags
- test_library
- tutor_profiles
- tutor_tags
- users
```

---

## Диагностика через Python

```python
#!/usr/bin/env python3
"""Diagnostic script for database setup"""

from api_client import TutorPlatformClient

def diagnose():
    client = TutorPlatformClient()
    
    print("🔍 Database Diagnostics\n")
    
    # 1. Health check
    print("1️⃣  FastAPI Health:")
    if client.health_check():
        print("   ✅ FastAPI is running\n")
    else:
        print("   ❌ FastAPI is not responding\n")
        return
    
    # 2. Database check
    print("2️⃣  Database Connection:")
    if client.db_check():
        print("   ✅ PostgreSQL is connected\n")
    else:
        print("   ❌ Database connection failed\n")
        return
    
    # 3. Keycloak check
    print("3️⃣  Keycloak Authentication:")
    if client.authenticate("admin@example.com", "admin_password"):
        print("   ✅ Keycloak is accessible\n")
        if client.auth_check():
            print("   ✅ JWT token is valid\n")
        else:
            print("   ⚠️  Token validation issue\n")
    else:
        print("   ⚠️  Keycloak authentication failed\n")
    
    print("✅ Diagnostics complete!")

if __name__ == "__main__":
    diagnose()
```

**Сохранить как `diagnose.py` и запустить:**
```bash
python3 diagnose.py
```

---

## Логирование и отладка

### Просмотр логов всех сервисов

```bash
# Все сервисы
docker-compose logs -f

# Только PostgreSQL (last 50 lines)
docker-compose logs postgres | tail -50

# Только FastAPI (real-time)
docker-compose logs fastapi -f

# Только Keycloak (last 100 lines)
docker-compose logs keycloak | tail -100
```

### Сохранение логов в файл

```bash
# Диагностический дамп всех логов
docker-compose logs > logs_dump_$(date +%s).txt

# Логи PostgreSQL в файл
docker-compose logs postgres > postgres_logs.txt
```

---

## Очистка и переинициализация

### Полный сброс системы

```bash
# 1. Остановить все контейнеры
docker-compose down

# 2. Удалить все томы данных (⚠️ Это удалит все данные!)
docker volume rm postgres_data keycloak_data

# 3. Пересоздать контейнеры (init.sql выполнится автоматически)
docker-compose up -d

# 4. Дождаться инициализации
sleep 30

# 5. Проверить готовность
docker-compose exec postgres pg_isready -U tutordb_user -d tutor_platform_db
```

### Проверка после переинициализации

```python
from api_client import TutorPlatformClient

client = TutorPlatformClient()

# Должны повторить инициализацию:
print("✅ Health check:", client.health_check())
print("✅ Database check:", client.db_check())

# Добавить тестовых репетиторов
tutors = [
    {
        "email": "tutor1@test.com",
        "full_name": "Tutor One",
        "specialization": "Mathematics",
        "hourly_rate": 50,
        "years_experience": 5,
        "tags": ["Algebra", "Calculus"]
    }
]

for tutor in tutors:
    client.add_test_tutor(**tutor)
    print(f"✅ Added: {tutor['full_name']}")
```

---

## Полезные команды

### Подключение к БД через CLI

```bash
docker-compose exec postgres psql -U tutordb_user -d tutor_platform_db
```

### Выполнение SQL запроса

```bash
docker-compose exec postgres psql -U tutordb_user -d tutor_platform_db -c \
  "SELECT COUNT(*) FROM api.users;"
```

### Сохранение дампа БД (для резервной копии)

```bash
docker-compose exec postgres pg_dump -U tutordb_user tutor_platform_db > backup_$(date +%s).sql
```

---

## Контакт/Поддержка

**Email:** support@tutorplatform.com  
**Версия API:** 1.0.0  
**Версия БД:** PostgreSQL 15+

