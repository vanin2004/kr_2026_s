# FastAPI Testing Guide

## Тестовое покрытие

Проект включает комплексные тесты для всех компонентов FastAPI приложения.

### Структура тестов

```
fastapi/
├── pytest.ini                      # Конфигурация pytest
├── requirements.txt                # Зависимости (включая pytest)
└── src/tests/
    ├── __init__.py
    ├── conftest.py                 # Pytest конфигурация и fixtures
    ├── test_main.py                # Тесты основных endpoints (60+ тестов)
    ├── test_config.py              # Тесты конфигурации (30+ тестов)
    └── test_integration.py         # Интеграционные тесты (15+ тестов)
```

### Тестовые категории

#### 1. **test_main.py** (60+ тестов)
Тестирование основных HTTP endpoints:

- **TestHealthCheck** — Проверка `/health` endpoint
  - Статус код 200
  - Правильная структура ответа
  - Тип контента (JSON)

- **TestRoot** — Проверка `/` endpoint
  - Metadata и версия API
  - Структура ответа

- **TestAPIDocumentation** — Документация API
  - Swagger UI (`/docs`)
  - ReDoc (`/redoc`)
  - OpenAPI schema (`/openapi.json`)

- **TestNotFound** — 404 handling

- **TestApplicationMetadata** — Metadata в OpenAPI schema
  - Название
  - Описание
  - Версия

- **TestCORS** — CORS headers

- **TestResponseFormats** — Формат ответов

- **TestEndpointPerformance** — Производительность
  - Response time < 1 секунда

- **TestHTTPMethods** — Проверка HTTP методов
  - GET allowed
  - POST/PUT/DELETE denied (405)

#### 2. **test_config.py** (30+ тестов)
Тестирование конфигурации приложения:

- **TestSettingsDefaults** — Значения по умолчанию
  - Database URL
  - Keycloak settings
  - JWT secret
  - API title и версия
  - CORS origins

- **TestSettingsTypes** — Типы данных

- **TestSettingsValidation** — Валидация
  - Database URL формат
  - Keycloak URL формат
  - Semantic versioning

- **TestJWTSecret** — JWT secret
  - Длина и формат

- **TestKeycloakSettings** — Keycloak конфигурация

#### 3. **test_integration.py** (15+ тестов)
Интеграционные тесты:

- **TestEnvironmentVariables** — Переменные окружения
- **TestDockerEnvironment** — Docker окружение
- **TestServiceConnectivity** — Подключение сервисов
- **TestContainerReadiness** — Готовность контейнера
- **TestFileStructure** — Структура проекта

### Запуск тестов

#### Локально (без Docker)

```bash
cd backend/fastapi

# Установить зависимости
pip install -r requirements.txt

# Запустить все тесты
pytest

# Запустить с verbose output
pytest -v

# Запустить конкретный файл
pytest src/tests/test_main.py -v

# Запустить конкретный класс
pytest src/tests/test_main.py::TestHealthCheck -v

# Запустить конкретный тест
pytest src/tests/test_main.py::TestHealthCheck::test_health_check_status_code -v
```

#### С Docker (Compose)

```bash
cd backend

# Запустить все сервисы
docker-compose up -d

# Запустить тесты в контейнере FastAPI
docker-compose exec fastapi pytest

# Запустить с подробным выводом
docker-compose exec fastapi pytest -v

# Запустить с coverage
docker-compose exec fastapi pytest --cov=src src/tests/

# Запустить tесты для конкретного модуля
docker-compose exec fastapi pytest src/tests/test_main.py -v

# Запустить с маркерами
docker-compose exec fastapi pytest -m unit -v
docker-compose exec fastapi pytest -m integration -v
```

### Test Markers

```bash
# Запустить только unit тесты
pytest -m unit

# Запустить только integration тесты
pytest -m integration

# Запустить только тесты health check
pytest -m health

# Запустить только endpoint тесты
pytest -m endpoints

# Запустить все кроме slow тестов
pytest -m "not slow"
```

### Coverage Report

```bash
# Генерировать HTML report
docker-compose exec fastapi pytest --cov=src --cov-report=html

# View coverage в консоли
docker-compose exec fastapi pytest --cov=src --cov-report=term-missing
```

### Ожидаемые результаты

Все тесты должны пройти успешно:

```
=== test session starts ===
platform linux -- Python 3.11.x, pytest-7.x.x, pluggy-1.x.x
collected 100+ items

src/tests/test_main.py ................                     [ 60%]
src/tests/test_config.py ..................                [ 30%]
src/tests/test_integration.py .............                [ 10%]

=== 100+ passed in 2.5s ===
```

### Troubleshooting

#### Тесты не запускаются

```bash
# Проверить что pytest установлен
pip list | grep pytest

# Переустановить зависимости
pip install -r requirements.txt --force-reinstall
```

#### Import errors

```bash
# Проверить PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# Убедиться что находитесь в правильной папке
cd backend/fastapi
```

#### Тесты падают в Docker

```bash
# Проверить логи контейнера
docker-compose logs fastapi

# Пересобрать образ
docker-compose build fastapi

# Перезагрузить контейнер
docker-compose restart fastapi
```

### Best Practices

1. **Запускать тесты перед каждым коммитом**
   ```bash
   git pre-commit hook: pytest
   ```

2. **Использовать coverage для отслеживания покрытия**
   ```bash
   pytest --cov=src --cov-report=html
   ```

3. **Писать тесты для новых features**
   - Каждый новый endpoint должен иметь минимум 3 теста

4. **Структура тестов (AAA pattern)**
   ```python
   def test_something(self):
       # Arrange - подготовить данные
       client = TestClient(app)
       
       # Act - выполнить операцию
       response = client.get("/endpoint")
       
       # Assert - проверить результат
       assert response.status_code == 200
   ```

### CI/CD Integration

Тесты автоматически запускаются:
- При push в репозиторий (GitHub Actions)
- В docker-compose на старте контейнера (опционально)
- Перед деплоем на production

### Документация генерируется из тестов

Используя pytest docstrings, можно генерировать документацию:

```bash
pytest --collect-only -q
```

### Полезные переменные окружения

```bash
# Для локального тестирования без Docker
export DATABASE_URL="sqlite:///test.db"
export TESTING=True

# Для скипования slow тестов
pytest -m "not slow"
```
