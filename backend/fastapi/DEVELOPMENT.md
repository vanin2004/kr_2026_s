# Backend Development Guide

## Структура папок FastAPI приложения

```
fastapi/
├── Dockerfile                   # Docker образ приложения
├── requirements.txt             # Python зависимости (pip)
├── pyproject.toml              # Альтернативно для poetry
├── src/
│   ├── __init__.py             # Package инициализация
│   ├── main.py                 # FastAPI приложение (entry point)
│   ├── config.py               # Конфигурация и переменные окружения
│   ├── models/                 # Pydantic модели (запросы/ответы)
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── tutor.py
│   │   └── student.py
│   ├── routes/                 # API endpoints (путь /api/custom/)
│   │   ├── __init__.py
│   │   ├── suggestions.py      # Алгоритм подбора репетиторов
│   │   ├── users.py            # APIユーザов
│   │   ├── profiles.py         # Профили студентов/репетиторов
│   │   └── ratings.py          # Рейтинги и отзывы
│   ├── services/               # Бизнес-логика
│   │   ├── __init__.py
│   │   ├── recommendation_service.py  # Suggestion Engine
│   │   ├── rating_service.py   # Расчет рейтингов
│   │   └── database_service.py # Запросы к БД
│   ├── middleware/             # Middleware
│   │   ├── __init__.py
│   │   └── auth.py             # JWT валидация
│   ├── utils/                  # Утилит-функции
│   │   ├── __init__.py
│   │   ├── logger.py           # Логирование
│   │   └── validators.py       # Валидаторы
│   └── tests/                  # Unit-тесты
│       ├── __init__.py
│       ├── test_suggestions.py
│       └── test_ratings.py
```

## Как начать разработку

### 1. Создать папки для компонентов

```bash
cd backend/fastapi/src

# Создать папки
mkdir -p models routes services middleware utils tests
touch models/__init__.py routes/__init__.py services/__init__.py middleware/__init__.py utils/__init__.py tests/__init__.py
```

### 2. Добавить базовые Pydantic модели

в `models/user.py`:
```python
from pydantic import BaseModel, EmailStr
from typing import Optional

class UserBase(BaseModel):
    email: EmailStr
    full_name: str

class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    id: int
    role: str
    created_at: datetime
    
    class Config:
        from_attributes = True
```

### 3. Развивать endpoints

в `routes/suggestions.py`:
```python
from fastapi import APIRouter, Query, Depends
from typing import List

router = APIRouter(prefix="/suggestions", tags=["recommendations"])

@router.post("/match-tutors")
async def get_tutor_suggestions(
    student_id: int,
    subject: str,
    budget: float,
    weights: dict = None
):
    """Get recommended tutors for student"""
    # Реализовать логику подбора
    pass
```

### 4. Подключить routes в main.py

```python
from src.routes import suggestions, users

app.include_router(suggestions.router)
app.include_router(users.router)
```

## Разработка локально

### Без Docker
```bash
cd backend/fastapi

# Создать virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Установить зависимости
pip install -r requirements.txt

# Запустить сервер
uvicorn src.main:app --reload
```

### С Docker
```bash
cd backend

# Rebuild образ при изменении requirements
docker-compose build fastapi

# Запустить
docker-compose up fastapi
```

## Тестирование

```bash
# Запустить тесты
pytest src/tests/

# С coverage
pytest --cov=src src/tests/

# Конкретный тест
pytest src/tests/test_suggestions.py::test_match_tutors
```

## Лучшие практики

1. **Type hints** — используй везде
2. **Async** — используй async/await для I/O операций
3. **Validation** — используй Pydantic для валидации входов
4. **Logging** — логируй важные события
5. **Testing** — покрывай функции unit-тестами
6. **Documentation** — используй docstrings и FastAPI docs

## Полезные ссылки

- [FastAPI документация](https://fastapi.tiangolo.com/)
- [SQLAlchemy ORM](https://docs.sqlalchemy.org/)
- [Pydantic docs](https://docs.pydantic.dev/)
- [Uvicorn](https://www.uvicorn.org/)
