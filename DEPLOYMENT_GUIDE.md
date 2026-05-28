# Tutor Platform - Deployment Guide

**Версия:** 1.0.0  
**Дата:** 29 Май 2026  
**Платформа:** Remote Server (157.245.244.194)

---

## 🚀 Быстрый старт

### Предварительные условия
- Docker & Docker Compose
- Python 3.8+
- curl (для базовой диагностики)

### Запуск система на удаленном сервере

```bash
# 1. Перейти в директорию backend
cd backend

# 2. Запустить все сервисы (БД инициализируется автоматически)
docker-compose up -d

# 3. Дождаться инициализации (2-3 минуты)
sleep 30

# 4. Проверить готовность системы
cd ..
python3 diagnose.py
```

**Ожидаемый результат:**
```
✅ API Connectivity
✅ Database Connection
✅ Keycloak Connectivity
✅ Authentication
✅ API Endpoints
✅ Data Insertion
Result: 6/6 tests passed
```

---

## 📊 Инициализация данных

После первого запуска инициализировать тестовые данные:

```bash
# Инициализировать репетиторов и тестовые данные
python3 init_db.py

# Проверить что всё работает
python3 api_client.py quick
```

---

## 🧪 Тестирование через Python

### Полная демонстрация

```bash
# Запустить все тесты API
python3 api_client.py full

# Это выполнит:
# ✅ Проверка здоровья API
# ✅ Проверка БД
# ✅ Проверка аутентификации (если Keycloak настроен)
# ✅ Добавление тестовых репетиторов
# ✅ Поиск репетиторов с фильтрами
# ✅ Пересчет рейтингов
```

### Быстрый поиск

```bash
# Быстрый тест поиска репетиторов
python3 api_client.py quick
```

### Диагностика системы

```bash
# Проверить готовность всех компонентов
python3 diagnose.py

# С подробным логированием
DEBUG=true python3 diagnose.py
```

---

## 🔧 Конфигурация

### Переменные окружения

```bash
# Установить IP удаленного сервера
export API_BASE_URL="http://157.245.244.194:80"
export KEYCLOAK_URL="http://157.245.244.194:8080"

# Включить подробное логирование
export DEBUG="true"

# Запустить скрипты
python3 api_client.py full
```

### Файл .env для Docker

Скрипты используют конфигурацию из `docker-compose.yml`:

```yaml
services:
  postgres:
    environment:
      POSTGRES_USER: tutordb_user
      POSTGRES_PASSWORD: tutordb_pass
      POSTGRES_DB: tutor_platform_db
```

---

## 📋 Стандартные операции

### Проверка статуса

```bash
# Все сервисы
docker-compose ps

# Логи PostgreSQL
docker-compose logs postgres | tail -20

# Логи FastAPI
docker-compose logs fastapi -f

# Логи Keycloak
docker-compose logs keycloak | head -50
```

### Перестарт сервисов

```bash
# Перезапустить определенный сервис
docker-compose restart postgres
docker-compose restart fastapi
docker-compose restart keycloak

# Перезапустить все сервисы
docker-compose restart
```

### Полный сброс системы

```bash
# ⚠️  Это удалит всё данные!

# 1. Остановить контейнеры
docker-compose down

# 2. Удалить томы данных
docker volume rm postgres_data keycloak_data

# 3. Переустановить систему (БД инициализируется с нуля)
docker-compose up -d

# 4. Дождатьсяинициализации
sleep 30

# 5. Инициализировать данные
python3 init_db.py
```

---

## 🛠️ Python API Клиент

### Использование в своих скриптах

```python
from api_client import TutorPlatformClient, Config

# Создать клиент с конфигом по умолчанию
client = TutorPlatformClient()

# Или использовать пользовательский адрес
config = Config(
    base_url="http://157.245.244.194:80",
    keycloak_url="http://157.245.244.194:8080"
)
client = TutorPlatformClient(config)

# Проверка здоровья
client.health_check()

# Проверка БД
client.db_check()

# Поиск репетиторов
tutors = client.get_suggestions(
    subject="Mathematics",
    max_rate=100,
    min_experience=2,
    desired_tags=["Algebra"]
)

# Добавить репетитора
tutor = client.add_test_tutor(
    email="tutor@example.com",
    full_name="John Doe",
    specialization="Mathematics",
    hourly_rate=75,
    years_experience=5,
    tags=["Algebra", "Calculus"]
)
```

---

## 📉 Мониторинг

### Проверка состояния БД

```python
from api_client import TutorPlatformClient

client = TutorPlatformClient()

# Получить информацию о БД
db_info = client._request("GET", "/db-check")
print(f"Database: {db_info.get('database_name')}")
print(f"PostgreSQL: {db_info.get('postgres_version')}")
```

### Проверка API endpoints

```python
from api_client import TutorPlatformClient

client = TutorPlatformClient()

endpoints = [
    "/health",
    "/api/custom/health",
    "/api/custom/db-check"
]

for endpoint in endpoints:
    try:
        response = client._request("GET", endpoint)
        print(f"✅ {endpoint}")
    except Exception as e:
        print(f"❌ {endpoint}: {e}")
```

---

## 🐛 Решение проблем

### PostgreSQL не инициализируется

```bash
# Проверить логи
docker-compose logs postgres | tail -50

# Пересоздать контейнер
docker-compose down postgres
docker volume rm postgres_data
docker-compose up -d postgres

# Дождаться инициализации
sleep 30

# Проверить готовность
docker-compose exec postgres pg_isready -U tutordb_user
```

### FastAPI не может подключиться

```bash
# Убедиться что PostgreSQL готов
docker-compose logs postgres | grep "ready to accept"

# Перезапустить FastAPI
docker-compose restart fastapi

# Проверить логи
docker-compose logs fastapi -f
```

### Keycloak не запускается

```bash
# Проверить логи
docker-compose logs keycloak | head -100

# Убедиться что PostgreSQL для Keycloak готов
docker-compose exec postgres psql -c "SELECT datname FROM pg_database WHERE datname='keycloak_db';"

# Перезапустить Keycloak
docker-compose restart keycloak
```

---

## 📊 Структура файлов

```
/mnt/projects/mgtu/kr_2026_s/
├── api_client.py              # Основной Python клиент для API
├── diagnose.py                # Диагностический скрипт
├── init_db.py                 # Скрипт инициализации БД
├── API_DOCUMENTATION.md       # Полная документация API
├── DB_TROUBLESHOOTING.md      # Руководство по решению проблем БД
├── DEPLOYMENT_GUIDE.md        # Этот файл
│
├── backend/
│   ├── docker-compose.yml     # Конфигурация сервисов
│   ├── Makefile               # Команды для разработки
│   │
│   ├── fastapi/               # FastAPI микросервис
│   │   ├── src/
│   │   │   ├── main.py        # Основное приложение
│   │   │   ├── config.py      # Конфигурация
│   │   │   ├── api/           # API endpoints
│   │   │   ├── auth/          # Аутентификация
│   │   │   ├── db/            # Функции БД
│   │   │   ├── models/        # Pydantic модели
│   │   │   └── services/      # Бизнес-логика
│   │   │
│   │   ├── requirements.txt   # Python зависимости
│   │   ├── Dockerfile        # Docker контейнер
│   │   └── pytest.ini         # Конфигурация тестов
│   │
│   ├── postgres/
│   │   └── init.sql           # SQL скрипт инициализации БД
│   │
│   ├── keycloak/
│   │   └── realm-export.json  # Конфигурация Keycloak сервера
│   │
│   └── nginx/
│       ├── nginx.conf         # Конфигурация API Gateway
│       └── Dockerfile        # Docker контейнер
```

---

## 🔐 Безопасность

### Развертывание на production

1. **Изменить пароли по умолчанию** в `docker-compose.yml`:
   - POSTGRES_PASSWORD
   - KC_BOOTSTRAP_ADMIN_PASSWORD

2. **Использовать SSL/TLS**:
   - Обновить nginx сертификаты
   - Использовать HTTPS вместо HTTP

3. **Ограничить CORS**:
   - Обновить `allow_origins` в FastAPI

4. **Настроить firewall**:
   - Открыть только port 80 и 443
   - Закрыть direct доступ к портам PostgreSQL, Keycloak, etc.

---

## 📞 Поддержка

### Логирование проблем

Сохранить диагностическую информацию:

```bash
# Создать файл с информацией о системе
{
    echo "=== Docker Version ==="
    docker --version
    docker-compose --version
    
    echo ""
    echo "=== System Status ==="
    docker-compose ps
    
    echo ""
    echo "=== PostgreSQL Logs (last 50 lines) ==="
    docker-compose logs postgres | tail -50
    
    echo ""
    echo "=== Python Tests ==="
    python3 diagnose.py
} > diagnostics_$(date +%s).txt

# Отправить файл support@tutorplatform.com
```

---

## 📝 Версионирование

| Версия | Дата | Изменения |
|--------|------|----------|
| 1.0.0 | 29.05.2026 | Начальная версия - Clean Slate, полностью на Python |

---

**Последнее обновление:** 29 Май 2026  
**Статус:** ✅ Production Ready  
**Автор:** Tutor Platform Team
