# Техническое задание (Концепт)
## Мобильное приложение для совместной работы учеников и репетиторов

**Дата:** 29 апреля 2026  
**Статус:** Концептуальное описание  
**Версия:** 1.0

---

## 1. Общее описание проекта

Платформа для подбора репетиторов, планирования уроков и взаимодействия учеников с преподавателями. Система предназначена для:
- **Учеников:** поиск репетиторов с персонализированным рейтингом, бронирование уроков, отслеживание прогресса
- **Репетиторов:** управление профилем, расписанием, взаимодействие со студентами
- **Администраторов:** мониторинг системы и управление пользователями

---

## 3. Основные объекты системы

### 3.1 Пользователь (User)
Базовая сущность для всех типов пользователей
- **Атрибуты:** ID, email, password_hash, role (student/tutor/admin), is_verified, created_at
- **Роли:** Ученик, Репетитор, Администратор

### 3.2 Ученик (Student)
Расширение User с данными про процесс обучения
- **Атрибуты:** 
  - full_name, avatar_url, bio
  - priority_weights: {k1, k2, k3, k4} - веса приоритетов для рейтинга
  - filters: {max_price, min_experience, verified_only} - критерии исключения
- **Операции:**
  - Обновлять приоритеты и фильтры
  - Просматривать список репетиторов (с персональным рейтингом)
  - Создавать заявки на уроки
  - Оценивать репетиторов
  - Загружать результаты тестов

### 3.3 Репетитор (Tutor)
Расширение User с информацией о преподавании
- **Атрибуты:**
  - full_name, avatar_url, bio
  - specialization: [] (массив предметов)
  - experience_years: число
  - hourly_rate: цена за час
  - is_verified: статус верификации
- **Операции:**
  - Обновлять профиль
  - Управлять расписанием доступности
  - Принимать/отклонять заявки на уроки
  - Загружать результаты тестов ученика
  - Получать оценки от учеников

### 3.4 Свойства репетитора (Tutor Properties)
Рассчитанные метрики для каждого репетитора
- **Атрибуты:**
  - effectiveness (0-1) - скорость прогресса ученика
  - communication_quality (0-1) - качество общения
  - expertise_level (0-1) - уровень знаний
  - responsiveness (0-1) - скорость ответов
  - last_updated: когда были рассчитаны
- **Расчет:** На основе отзывов, тестов прогресса и активности

### 3.5 Урок (Lesson)
Запланированное занятие между учеником и репетитором
- **Атрибуты:**
  - ID, student_id, tutor_id
  - scheduled_at: дата и время
  - duration_minutes: продолжительность
  - status: scheduled | completed | cancelled
  - created_at, completed_at
- **Операции:**
  - Создавать (ученик)
  - Подтверждать (репетитор)
  - Отменять/переносить
  - Отмечать как завершенный

### 3.6 Тесты и прогресс (Student Test)
Результаты тестирования для отслеживания прогресса
- **Атрибуты:**
  - student_id, tutor_id, lesson_id (связь с уроком)
  - test_date
  - score_before, score_after: оценки до и после
  - month_coefficient: коэффициент для месяца (1.0, 1.1, 1.2...)
- **Назначение:** Считать effectiveness репетитора

### 3.7 Оценка и отзыв (Tutor Rating)
Оценка репетитора от ученика
- **Атрибуты:**
  - tutor_id, student_id
  - rating_value: 1-5 звезд (общая оценка)
  - communication_score: 1-5
  - expertise_score: 1-5
  - review_text: текст отзыва (опционально)
  - created_at
- **Назначение:** Источник для communication_quality и expertise_level

### 3.8 Сообщение (Message)
Текстовое общение между пользователями
- **Атрибуты:**
  - ID, sender_id, receiver_id
  - text: содержание
  - is_read: статус прочтения
  - created_at
- **Операции:**
  - Отправлять в реальном времени (WebSocket)
  - Получать историю диалога
  - Отмечать как прочитанное

### 3.9 Вложение (Attachment)
Файл, прикрепленный к сообщению
- **Атрибуты:**
  - ID, message_id
  - file_url: ссылка на файл
  - file_name, file_size, file_type
  - created_at
- **Типы:** документы, изображения
- **Ограничения:** ≤ 10 MB

### 3.10 Уведомление (Notification)
Событие, требующее внимания пользователя
- **Атрибуты:**
  - ID, user_id
  - notification_type: lesson_request | lesson_confirmed | lesson_reminder | new_message | rating_received | test_scheduled
  - data: JSON доп. информация
  - is_read, created_at
- **Доставка:** Push через FCM

### 3.11 Устройство пользователя (Device Token)
Регистрация устройства для push-уведомлений
- **Атрибуты:**
  - user_id, fcm_token
  - device_id, platform (android/ios)
  - created_at, updated_at

---

## 4. Функциональные требования

### 2.1 Модули приложения

#### 2.1.1 Аутентификация и авторизация
- **Регистрация пользователя** с выбором роли (Ученик / Репетитор)
- **Вход в систему** через email и пароль
- **JWT токены** для безопасной передачи (access token + refresh token)
- **Выход из системы** с инвалидацией токена
- **Верификация email** (опционально)

**Роли:**
- **Ученик** - поиск репетиторов, бронирование уроков, общение, оценивание
- **Репетитор** - создание профиля, управление расписанием, прием заявок
- **Администратор** - управление пользователями, статистика, модерация

#### 2.1.2 Система подбора учителя (рейтинг)

**Компоненты рейтинга:**

1. **Свойства репетитора (Oi):**
   - **Effectiveness (Эффективность)** - средняя скорость роста знаний ученика
     - Рассчитывается как: (среднее улучшение баллов) / месяцы сотрудничества
     - Измеряется через тесты до и после занятий
   - **Communication Quality (Качество коммуникации)** - оценка от учеников
     - Средняя оценка по этому критерию в рецензиях
     - Диапазон: 1-5 баллов
   - **Expertise Level (Уровень экспертизы)** - глубина знаний по предметам
     - Оценивается учениками в рецензиях
     - Диапазон: 1-5 баллов
   - **Responsiveness (Отзывчивость)** - скорость ответов на сообщения
     - Среднее время ответа в часах
     - Нормализуется в шкалу 1-5

2. **Приоритеты ученика (ki):**
   - Каждый ученик может установить приоритеты для каждого свойства репетитора
   - Представляют собой нормализованные веса (сумма = 1.0)
   - По умолчанию все веса равны 0.25
   - Могут быть отредактированы в профиле ученика
   - Формат: k1, k2, k3, k4 (где сумма = 1.0)

3. **Фильтры ученика (исключающие условия):**
   - Максимальная стоимость часа занятия
   - Минимальный стаж преподавателя (в годах)
   - Только верифицированные репетиторы
   - Наличие свободных мест у репетитора

**Формула расчета рейтинга для ученика:**
```
Рейтинг(T, S) = О1(T) × к1(S) + О2(T) × к2(S) + О3(T) × к3(S) + О4(T) × к4(S)

где:
- T = репетитор
- S = ученик
- О1, О2, О3, О4 = свойства репетитора (нормализованные 0-1)
- к1, к2, к3, к4 = приоритеты ученика (нормализованные, сумма = 1)
```

**Ежемесячный пересчет коэффициентов:**
- За каждый месяц сотрудничества коэффициент увеличивается
- Месяц 1: коэф = 1.0
- Месяц 2: коэф = 1.1
- Месяц 3: коэф = 1.2 и т.д.
- Автоматический пересчет 1-го числа каждого месяца (задача Celery)

**Процесс поиска:**
1. Применить фильтры (исключить не подходящих)
2. Для оставшихся репетиторов рассчитать рейтинг по формуле выше
3. Отсортировать по убыванию рейтинга
4. Вернуть список с топ N репетиторов

#### 2.1.3 Планирование уроков

**Функциональность:**
- **Создание урока:** Ученик выбирает репетитора и время из доступных слотов
- **Статусы урока:**
  - `scheduled` - запланирован
  - `completed` - завершен
  - `cancelled` - отменен
  - `rescheduled` - перенесен
- **Календарь:** Месячный/недельный вид с отмеченными уроками
- **Оффлайн доступ:** Локальное хранилище календаря (Room Database на Android)
- **Синхронизация:** При подключении к интернету синхронизирование с сервером
- **Напоминания:** Push-уведомления за 1 час до урока (FCM)
- **Загрузка результатов тестирования:**
  - Результат теста до урока (score_before)
  - Результат теста после урока (score_after)
  - Дата проведения теста

#### 2.1.4 Мессенджер

**Характеристики:**
- **Типы сообщений:** текст, файлы (документы, изображения)
- **Диалоги:** отдельная переписка между учеником и репетитором
- **Real-time обновления:** WebSocket для мгновенного получения сообщений
- **История сообщений:** пагинация, сортировка по времени
- **Индикатор набора текста:** "Someone is typing..."
- **Статус прочитанности:** отмечать прочитанные сообщения
- **Оффлайн очередь:** сохранять сообщения локально при отсутствии соединения

**Вложения:**
- Типы: документы (PDF, DOC), изображения (JPG, PNG)
- Максимальный размер файла: 10 MB
- Preview изображений в чате
- Download файла на устройство

#### 2.1.5 Система уведомлений

**Типы уведомлений:**
- Новое предложение урока (ученик отправил заявку)
- Подтверждение урока репетитором
- Напоминание об уроке (за 1 час)
- Новое сообщение в чате
- Получена оценка от ученика
- Запланирован тест по прогрессу

**Способ доставки:**
- **Push-уведомления** через Firebase Cloud Messaging (FCM)
- Требуется регистрация FCM токена устройства на сервере
- Обновление токена при необходимости

**Управление уведомлениями:**
- История уведомлений в приложении
- Отметить как прочитанное
- Удалить уведомление
- In-app уведомления (всплывающие баннеры)

---

## 3. Технические требования

### 3.1 Backend (Python FastAPI)

**Framework & Libraries:**
- `fastapi` - веб-фреймворк
- `uvicorn` - ASGI сервер
- `sqlalchemy` - ORM для работы с БД
- `alembic` - миграции БД
- `psycopg2-binary` - драйвер PostgreSQL
- `python-jose[cryptography]` - работа с JWT
- `passlib` - хеширование паролей
- `firebase-admin` - интеграция с FCM
- `celery` - асинхронные задачи
- `redis` - кеш и message broker для Celery
- `python-multipart` - обработка файлов
- `pydantic` - валидация данных
- `pytest`, `httpx` - тестирование

**Структура проекта:**
```
/backend
├── main.py                 # Точка входа FastAPI приложения
├── config.py              # Конфигурация (DB, JWT, FCM, Redis)
├── requirements.txt       # Зависимости
├── Dockerfile             # Docker контейнер
├── .env.example          # Пример переменных окружения
├── /app
│   ├── models.py         # SQLAlchemy ORM модели
│   ├── schemas.py        # Pydantic схемы валидации
│   ├── database.py       # Подключение к БД
│   ├── /api              # API endpoints
│   │   ├── auth.py       # Аутентификация
│   │   ├── tutors.py     # Репетиторы
│   │   ├── students.py   # Ученики
│   │   ├── lessons.py    # Уроки
│   │   ├── messages.py   # Мессенджер
│   │   ├── notifications.py  # Уведомления
│   │   ├── files.py      # Загрузка файлов
│   │   └── admin.py      # Администратор
│   ├── /services         # Бизнес-логика
│   │   ├── rating_service.py    # Расчет рейтинга
│   │   ├── notification_service.py # FCM отправка
│   │   ├── search_service.py    # Поиск с фильтрами
│   │   ├── websocket_manager.py # Управление WebSocket
│   │   └── user_service.py      # Операции с пользователями
│   ├── /tasks            # Celery задачи
│   │   ├── monthly_rating_update.py  # Ежемесячный пересчет
│   │   └── notification_tasks.py     # Отправка уведомлений
│   ├── /utils
│   │   └── validators.py # Валидация данных
│   └── /tests            # Unit тесты
│       ├── test_auth.py
│       ├── test_rating.py
│       ├── test_search.py
│       └── test_messages.py
├── /alembic              # Миграции БД
│   ├── env.py
│   ├── script.py.mako
│   └── /versions
└── README.md
```

**Базовая конфигурация:**
```python
# config.py
DATABASE_URL = "postgresql://user:password@localhost/tutoring_db"
JWT_SECRET_KEY = "your-secret-key"
JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7

FIREBASE_CREDENTIALS = "path/to/firebase-adminsdk.json"

REDIS_URL = "redis://localhost:6379"
CELERY_BROKER_URL = REDIS_URL
CELERY_RESULT_BACKEND = REDIS_URL

MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB
```

### 3.2 База данных (PostgreSQL)

**Таблицы:**

1. **users** - базовая информация о пользователях
   - id (PRIMARY KEY, UUID)
   - email (UNIQUE, VARCHAR)
   - password_hash (VARCHAR)
   - role (ENUM: student, tutor, admin)
   - is_verified (BOOLEAN, default: false)
   - created_at (TIMESTAMP)
   - updated_at (TIMESTAMP)

2. **students** - дополнительная информация об учениках
   - id (PRIMARY KEY, UUID)
   - user_id (FOREIGN KEY → users)
   - full_name (VARCHAR)
   - avatar_url (VARCHAR, nullable)
   - bio (TEXT, nullable)
   - priority_weights JSON (k1, k2, k3, k4)
   - filters JSON (max_price, min_experience, verified_only)
   - created_at (TIMESTAMP)

3. **tutors** - дополнительная информация о репетиторах
   - id (PRIMARY KEY, UUID)
   - user_id (FOREIGN KEY → users)
   - full_name (VARCHAR)
   - avatar_url (VARCHAR, nullable)
   - bio (TEXT)
   - specialization (VARCHAR[])  -- массив предметов
   - experience_years (INTEGER)
   - hourly_rate (DECIMAL)
   - is_verified (BOOLEAN)
   - created_at (TIMESTAMP)
   - updated_at (TIMESTAMP)

4. **tutor_properties** - свойства репетитора (рассчитанные)
   - id (PRIMARY KEY)
   - tutor_id (FOREIGN KEY → tutors)
   - effectiveness (DECIMAL 0-1)  -- скорость прогресса
   - communication_quality (DECIMAL 0-1)
   - expertise_level (DECIMAL 0-1)
   - responsiveness (DECIMAL 0-1)
   - last_updated (TIMESTAMP)

5. **lessons** - планируемые уроки
   - id (PRIMARY KEY, UUID)
   - student_id (FOREIGN KEY → students)
   - tutor_id (FOREIGN KEY → tutors)
   - scheduled_at (TIMESTAMP)
   - duration_minutes (INTEGER)
   - status (ENUM: scheduled, completed, cancelled)
   - created_at (TIMESTAMP)
   - completed_at (TIMESTAMP, nullable)
   - cancelled_by (VARCHAR: student/tutor, nullable)
   - INDEX: (student_id, tutor_id), (tutor_id, scheduled_at)

6. **student_tests** - результаты тестирования ученика
   - id (PRIMARY KEY, UUID)
   - student_id (FOREIGN KEY → students)
   - tutor_id (FOREIGN KEY → tutors)
   - lesson_id (FOREIGN KEY → lessons, nullable)
   - test_date (TIMESTAMP)
   - score_before (INTEGER)
   - score_after (INTEGER)
   - month_coefficient (DECIMAL)
   - created_at (TIMESTAMP)

7. **tutor_ratings** - оценки и отзывы
   - id (PRIMARY KEY, UUID)
   - tutor_id (FOREIGN KEY → tutors)
   - student_id (FOREIGN KEY → students)
   - rating_value (DECIMAL 1-5)
   - communication_score (INTEGER 1-5)
   - expertise_score (INTEGER 1-5)
   - review_text (TEXT, nullable)
   - created_at (TIMESTAMP)
   - INDEX: (tutor_id, created_at)

8. **messages** - сообщения в чате
   - id (PRIMARY KEY, UUID)
   - sender_id (FOREIGN KEY → users)
   - receiver_id (FOREIGN KEY → users)
   - text (TEXT)
   - is_read (BOOLEAN, default: false)
   - created_at (TIMESTAMP)
   - INDEX: (sender_id, receiver_id, created_at)

9. **attachments** - вложения в сообщениях
   - id (PRIMARY KEY, UUID)
   - message_id (FOREIGN KEY → messages)
   - file_url (VARCHAR)
   - file_name (VARCHAR)
   - file_size (BIGINT)
   - file_type (VARCHAR: document, image)
   - created_at (TIMESTAMP)

10. **notifications** - история уведомлений
    - id (PRIMARY KEY, UUID)
    - user_id (FOREIGN KEY → users)
    - notification_type (VARCHAR: lesson_request, lesson_confirmed, lesson_reminder, new_message, rating_received, test_scheduled)
    - data JSON (дополнительные данные для уведомления)
    - is_read (BOOLEAN, default: false)
    - created_at (TIMESTAMP)

11. **device_tokens** - FCM токены устройств
    - id (PRIMARY KEY)
    - user_id (FOREIGN KEY → users)
    - fcm_token (VARCHAR)
    - device_id (VARCHAR)
    - platform (VARCHAR: android, ios)
    - created_at (TIMESTAMP)
    - updated_at (TIMESTAMP)
    - UNIQUE: (user_id, device_id)

### 3.3 Android приложение (Java)

**Минимальная версия Android:** API 24 (Android 7.0)  
**Целевая версия:** API 34 (Android 14)

**Основные библиотеки:**
- `androidx.appcompat` - компонент совместимости
- `androidx.navigation` - навигация между фрагментами
- `androidx.room` - локальная БД
- `retrofit2` - HTTP клиент для REST API
- `okhttp3` - перехватчик запросов
- `com.google.firebase:firebase-messaging` - FCM
- `com.squareup.picasso` - загрузка изображений
- `com.google.code.gson` - JSON сериализация
- `org.java-websocket:Java-WebSocket` - WebSocket клиент

**Структура проекта:**
```
/android
├── app/build.gradle          # Конфигурация сборки
├── settings.gradle
├── app/src/main/
│   ├── AndroidManifest.xml
│   ├── java/com/tutoring/
│   │   ├── MainActivity.java                 # Главная активность
│   │   ├── /activity
│   │   │   ├── LoginActivity.java
│   │   │   ├── RegisterActivity.java
│   │   │   ├── SplashActivity.java
│   │   │   └── TutorProfileActivity.java
│   │   ├── /fragment
│   │   │   ├── HomeFragment.java             # Главный экран
│   │   │   ├── SearchTutorsFragment.java     # Поиск репетиторов
│   │   │   ├── CalendarFragment.java         # Календарь с уроками
│   │   │   ├── MessagesFragment.java         # Список диалогов
│   │   │   ├── ChatFragment.java             # Чат с репетитором
│   │   │   ├── NotificationsFragment.java    # Уведомления
│   │   │   └── ProfileFragment.java          # Профиль пользователя
│   │   ├── /service
│   │   │   ├── ApiService.java               # REST клиент (Retrofit)
│   │   │   ├── WebSocketService.java         # WebSocket управление
│   │   │   ├── FCMService.java               # Обработка push уведомлений
│   │   │   └── SyncService.java              # Синхронизация локальных данных
│   │   ├── /model
│   │   │   ├── User.java
│   │   │   ├── Tutor.java
│   │   │   ├── Student.java
│   │   │   ├── Lesson.java
│   │   │   ├── Message.java
│   │   │   ├── Rating.java
│   │   │   └── Notification.java
│   │   ├── /database
│   │   │   ├── AppDatabase.java              # Room DB
│   │   │   ├── LessonDAO.java                # Доступ к урокам
│   │   │   ├── MessageDAO.java               # Доступ к сообщениям
│   │   │   └── CacheDAO.java                 # Кеш данных
│   │   ├── /adapter
│   │   │   ├── TutorsListAdapter.java
│   │   │   ├── ConversationsAdapter.java
│   │   │   ├── ChatMessagesAdapter.java
│   │   │   ├── LessonsAdapter.java
│   │   │   └── NotificationsAdapter.java
│   │   ├── /util
│   │   │   ├── TokenManager.java             # Управление JWT токенами
│   │   │   ├── PreferenceManager.java        # SharedPreferences
│   │   │   ├── Constants.java                # Константы
│   │   │   ├── DateUtils.java                # Утилиты для дат
│   │   │   └── ValidationUtils.java          # Валидация
│   │   └── /receiver
│   │       └── NotificationReceiver.java    # Приемник FCM
│   ├── res/
│   │   ├── layout/
│   │   │   ├── activity_login.xml
│   │   │   ├── activity_main.xml
│   │   │   ├── fragment_home.xml
│   │   │   ├── fragment_search_tutors.xml
│   │   │   ├── fragment_calendar.xml
│   │   │   ├── fragment_messages.xml
│   │   │   ├── fragment_chat.xml
│   │   │   ├── fragment_profile.xml
│   │   │   ├── item_tutor_card.xml
│   │   │   ├── item_message.xml
│   │   │   └── item_lesson.xml
│   │   ├── values/
│   │   │   ├── strings.xml
│   │   │   ├── colors.xml
│   │   │   ├── dimens.xml
│   │   │   └── styles.xml
│   │   ├── drawable/
│   │   │   └── [иконки и картинки]
│   │   └── menu/
│   │       └── bottom_navigation.xml
│   └── AndroidManifest.xml
├── app/src/test/
├── app/src/androidTest/
└── README.md
```

**Локальная синхронизация:**
- Room Database для хранения уроков, сообщений, кеша
- SharedPreferences для хранения JWT токенов и параметров пользователя
- При запуске приложения: проверка internet connection
- Если есть интернет: синхронизировать локальные изменения → получить обновления с сервера
- Если нет интернета: использовать локальные данные, сохранить очередь изменений

### 3.4 Web администратор (HTML, CSS, JavaScript)

**Структура:**
```
/web-admin
├── index.html                # Точка входа
├── /css
│   ├── style.css            # Основные стили
│   └── responsive.css       # Адаптивный дизайн
├── /js
│   ├── api.js              # Клиент для REST API
│   ├── auth.js             # Аутентификация администратора
│   ├── dashboard.js        # Главная панель
│   ├── users.js            # Управление пользователями
│   ├── tutors-report.js    # Отчет по репетиторам
│   ├── notifications.js    # Отправка уведомлений
│   └── utils.js            # Вспомогательные функции
├── /assets
│   ├── logo.png
│   └── [иконки]
└── README.md
```

**Страницы:**
1. **Login Page** - вход администратора
2. **Dashboard** - главная панель со статистикой
3. **Users Management** - таблица пользователей с фильтрацией
4. **Tutors Report** - отчет по репетиторам
5. **Notifications** - отправка массовых уведомлений

---

## 4. API Endpoints

### 4.1 Аутентификация

| Метод | Endpoint | Описание | Параметры |
|-------|----------|---------|-----------|
| POST | `/auth/register` | Регистрация пользователя | email, password, role, full_name |
| POST | `/auth/login` | Вход в систему | email, password |
| POST | `/auth/logout` | Выход | - |
| POST | `/auth/refresh` | Обновить токен | refresh_token |
| GET | `/auth/me` | Текущий пользователь | - |

### 4.2 Поиск и профили репетиторов

| Метод | Endpoint | Описание | Query параметры |
|-------|----------|---------|-----------------|
| GET | `/tutors/search` | Поиск с фильтрацией и рейтингом | filters.max_price, filters.min_experience, filters.verified_only, sort_by |
| GET | `/tutors/{tutor_id}` | Профиль репетитора | - |
| PUT | `/tutors/{tutor_id}` | Обновить профиль (репетитор) | full_name, bio, hourly_rate, specialization |
| GET | `/tutors/{tutor_id}/properties` | Свойства репетитора (рассчитанные) | - |
| GET | `/tutors/{tutor_id}/ratings` | Все рецензии на репетитора | - |

### 4.3 Профили учеников

| Метод | Endpoint | Описание | Параметры |
|-------|----------|---------|-----------|
| GET | `/students/me` | Мой профиль (ученик) | - |
| PUT | `/students/me` | Обновить профиль | full_name, avatar_url, bio |
| GET | `/students/me/preferences` | Мои приоритеты | - |
| PUT | `/students/me/preferences` | Установить приоритеты | k1, k2, k3, k4 |
| GET | `/students/me/filters` | Мои фильтры поиска | - |
| PUT | `/students/me/filters` | Обновить фильтры | max_price, min_experience, verified_only |
| GET | `/students/me/rating-for-tutor/{tutor_id}` | Рейтинг репетитора для меня (рассчитанный) | - |

### 4.4 Уроки

| Метод | Endpoint | Описание | Параметры |
|-------|----------|---------|-----------|
| POST | `/lessons` | Создать урок | tutor_id, scheduled_at, duration_minutes |
| GET | `/lessons` | Мои уроки | status, date_from, date_to |
| GET | `/lessons/{lesson_id}` | Детали урока | - |
| PUT | `/lessons/{lesson_id}` | Обновить урок | scheduled_at, duration_minutes |
| PUT | `/lessons/{lesson_id}/status` | Изменить статус | status (completed, cancelled) |
| DELETE | `/lessons/{lesson_id}` | Отменить урок | - |

### 4.5 Тесты и прогресс

| Метод | Endpoint | Описание | Параметры |
|-------|----------|---------|-----------|
| POST | `/lessons/{lesson_id}/test-results` | Загрузить результаты теста | score_before, score_after |
| GET | `/students/{student_id}/progress` | Прогресс ученика | tutor_id |

### 4.6 Рейтинг и оценки

| Метод | Endpoint | Описание | Параметры |
|-------|----------|---------|-----------|
| POST | `/tutors/{tutor_id}/rate` | Оценить репетитора | rating_value, communication_score, expertise_score, review_text |
| GET | `/tutors/{tutor_id}/ratings` | Все оценки репетитора | - |

### 4.7 Мессенджер (REST)

| Метод | Endpoint | Описание | Параметры |
|-------|----------|---------|-----------|
| GET | `/messages/conversations` | Список диалогов | limit, offset |
| GET | `/messages/with/{user_id}` | История с пользователем | limit, offset |
| POST | `/messages/send` | Отправить сообщение | receiver_id, text, attachments[] |
| DELETE | `/messages/{message_id}` | Удалить сообщение | - |

### 4.8 WebSocket для мессенджера

| Событие | Направление | Данные |
|---------|------------|--------|
| `connection` | Server → Client | {type: "connection", status: "ok"} |
| `message_sent` | Обе стороны | {type: "message", sender_id, text, timestamp} |
| `typing` | Обе стороны | {type: "typing", user_id} |
| `message_read` | Обе стороны | {type: "read", message_id} |
| `connection_closed` | Server → Client | {type: "connection", status: "closed"} |

**Подключение:** `WS /ws/messages/{user_id}`

### 4.9 Уведомления

| Метод | Endpoint | Описание | Параметры |
|-------|----------|---------|-----------|
| POST | `/notifications/device-token` | Регистрировать FCM токен | fcm_token, device_id, platform |
| PUT | `/notifications/device-token` | Обновить FCM токен | fcm_token, device_id |
| GET | `/notifications` | Список уведомлений | is_read, limit, offset |
| PUT | `/notifications/{notification_id}/read` | Отметить как прочитанное | - |
| DELETE | `/notifications/{notification_id}` | Удалить уведомление | - |

### 4.10 Загрузка файлов

| Метод | Endpoint | Описание | Параметры |
|-------|----------|---------|-----------|
| POST | `/files/upload` | Загрузить файл | file (multipart) |
| GET | `/files/{file_id}` | Скачать файл | - |
| DELETE | `/files/{file_id}` | Удалить файл | - |

### 4.11 Администратор

| Метод | Endpoint | Описание | Параметры |
|-------|----------|---------|-----------|
| GET | `/admin/stats` | Общая статистика | - |
| GET | `/admin/users` | Список пользователей | role, status, limit, offset |
| GET | `/admin/users/{user_id}` | Детали пользователя | - |
| PUT | `/admin/users/{user_id}/verify` | Верифицировать пользователя | - |
| DELETE | `/admin/users/{user_id}` | Удалить пользователя | - |
| GET | `/admin/tutors/report` | Отчет по репетиторам | - |
| POST | `/admin/notifications/send-all` | Отправить массовое уведомление | notification_type, data |

---

## 5. UI страницы Android приложения

### 5.1 Экран авторизации (Registration/Login)
- Выбор роли: "I'm a Student" / "I'm a Tutor"
- Поля для ввода:
  - Email (валидация формата)
  - Password (минимум 8 символов)
  - Full Name (при регистрации)
- Кнопки: Sign Up / Sign In
- Ссылка: "Forgot password?" (опционально)
- Валидация в реальном времени с сообщениями об ошибках

### 5.2 Home Screen (Ученик)
- Top bar: Профиль (иконка пользователя) + Уведомления (иконка с бейджем)
- Секция "Upcoming Lessons":
  - Карточки с ближайшими уроками
  - Информация: репетитор, дата, время, статус
  - Сортировка по дате
- Секция быстрых фильтров:
  - "All Tutors", "Top Rated", "Recommended"
- Кнопка "+ Book a Lesson" (переход на Search)
- Bottom navigation: Home, Messages, Calendar, Profile

### 5.3 Search Tutors Screen
- Search bar: "Find a tutor by name, subject..."
- Expandable фильтры:
  - Price range (slider)
  - Min experience (dropdown)
  - Rating (≥ 3.0, ≥ 4.0, ≥ 4.5)
  - Verified only (checkbox)
- Сортировка: "Recommended For You", "Highest Rated", "Most Popular"
- Результаты (список с прокруткой):
  - Карточка репетитора: фото, имя, рейтинг (звёзды), цена/час
  - Краткая биография
  - Кнопка "View Profile" / "Book Lesson"

### 5.4 Tutor Profile Screen
- Заголовок: Фото + Имя + Рейтинг (звёзды)
- Вкладки: About, Reviews, Schedule
- **About вкладка:**
  - Bio, Specialization, Experience (лет)
  - Hourly rate
  - Визуализация свойств (Communication, Expertise, Responsiveness)
- **Reviews вкладка:**
  - Лист отзывов (аватар, имя, оценка, текст, дата)
- **Schedule вкладка:**
  - Календарь с доступными слотами
  - Кнопка "Pick a Time" (выбор даты/времени)
- Кнопка внизу: "Book a Lesson"

### 5.5 Calendar Screen
- Calendar view (месячный или недельный)
- Уроки отмечены цветом:
  - Синий: scheduled
  - Зелёный: completed
  - Серый: cancelled
- Tap на дату → детали урока (время, репетитор, кнопки действия)
- Синхронизация при открытии экрана
- Локальное хранилище для offline режима

### 5.6 Messages Screen
- Лист диалогов:
  - Аватар, имя, last message preview, timestamp
  - Бейдж с кол-вом непрочитанных сообщений
  - Swipe для удаления диалога
- Tap на диалог → Chat Screen

### 5.7 Chat Screen
- Top bar: Имя собеседника + статус (онлайн/офлайн)
- История сообщений:
  - Исходящие: справа, синие bubble
  - Входящие: слева, серые bubble
  - Время и статус (Read/Unread) для исходящих
  - Вложения: иконка файла, preview для изображений
- Typing indicator: "Someone is typing..."
- Input area:
  - Text field + Send button
  - Attach button (файл/изображение)
  - File upload progress
- Real-time обновления (WebSocket)
- Offline очередь сообщений

### 5.8 Notifications Screen
- Лист уведомлений:
  - Иконка, текст, timestamp
  - Типы: "New lesson request", "Lesson reminder", "New message", "Rating received", "Test scheduled"
  - Кнопка действия (Open, Mark as read)
- Swipe для удаления

### 5.9 Profile Screen (Ученик)
- Профиль: Фото, Имя, Email
- Кнопка: "Edit Profile"
- Мои уроки (link to Calendar)
- Мои репетиторы (список с рейтингом)
- Preferences:
  - **Priority Weights:** Слайдеры для каждого параметра
    - Effectiveness
    - Communication Quality
    - Expertise Level
    - Responsiveness
  - **Фильтры:**
    - Max price (input)
    - Min experience (input)
    - Verified only (checkbox)
- Кнопка: Logout

### 5.10 Tutor Home Screen
- Top bar: Профиль + Уведомления (аналогично ученику)
- Секция "My Students": лист активных студентов
- Секция "Upcoming Lessons": ближайшие уроки
- Кнопка: "My Availability" (управление расписанием)
- Статистика: кол-во 5-звездочных, средний рейтинг
- Bottom navigation: Home, Messages, Calendar, Profile

### 5.11 Tutor Profile Edit Screen
- Редактируемые поля:
  - Full Name
  - Bio
  - Specialization (множественный выбор)
  - Experience (лет)
  - Hourly rate
  - Avatar upload
  - Availability (по дням недели)
- Кнопка: Save

---

## 6. Admin Web Panel (HTML+CSS+JS)

### 6.1 Dashboard
- Карточки со статистикой:
  - Total Users
  - Active Tutors
  - Total Lessons
  - Avg Rating
- Графики:
  - Users Over Time (линейный график)
  - Lessons Per Month (столбчатая диаграмма)

### 6.2 Users Management
- Таблица:
  - Колонки: ID, Email, Name, Role, Status, Actions
  - Строки: список пользователей с пагинацией
- Фильтры:
  - Role (Student, Tutor)
  - Status (Active, Verified, Banned)
  - Created Date (date range)
- Actions (кнопки в каждой строке):
  - View details
  - Verify
  - Ban/Unban
  - Delete

### 6.3 Tutors Report
- Таблица:
  - Колонки: ID, Name, Avg Rating, Num Students, Num Lessons, Effectiveness Score
  - Сортируемые колонки
  - Пагинация
- Кнопки:
  - View details
  - Export to CSV

### 6.4 Notifications
- Форма отправки:
  - Title (input)
  - Message (textarea)
  - Target: All / Students / Tutors (radio)
  - Кнопка Send
- История отправленных уведомлений (таблица):
  - Дата, целевая группа, текст, статус

---

## 7. Требования безопасности

- **Пароли:** Хеширование bcrypt
- **Токены:** JWT с экспирацией (access: 30 мин, refresh: 7 дней)
- **HTTPS:** Обязательное использование SSL/TLS
- **CORS:** Настройка для мобильного клиента и веб-панели
- **Валидация:** Все входные данные валидируются на сервере
- **Файлы:** Проверка типов файлов, размер ≤ 10 MB
- **WebSocket:** Проверка аутентификации при подключении
- **FCM:** Безопасное хранение и управление токенами устройств

---

## 8. Нефункциональные требования

### 8.1 Производительность
- Поиск репетиторов: < 200 ms
- Загрузка мессенджера: < 500 ms
- WebSocket latency: < 100 ms
- 100 одновременных WebSocket соединений поддерживаются

### 8.2 Надежность
- Uptime: 99%
- Backup БД: ежедневно
- Обработка ошибок: graceful error messages
- Retry logic для failed operations

### 8.3 Масштабируемость
- Горизонтальное масштабирование FastAPI (несколько workers)
- CDN для статических файлов
- Кеширование (Redis) часто запрашиваемых данных
- Database indexing для быстрых queries

### 8.4 Доступность и оффлайн
- Локальное хранилище календаря (Room DB)
- Локальная очередь сообщений
- Синхронизация при подключении к интернету
- Graceful degradation при потере соединения

---

## 9. Процесс разработки

### Этап 1: Подготовка (Week 1)
- [ ] Определить точные форматы данных
- [ ] Настроить окружение (PostgreSQL, Redis, Firebase)
- [ ] Создать schema миграции (Alembic)
- [ ] Подготовить Firebase Project для FCM

### Этап 2: Backend (Week 2-3)
- [ ] Реализовать модели данных
- [ ] Реализовать endpoints аутентификации
- [ ] Реализовать рейтинг сервис
- [ ] Реализовать поиск с фильтрами
- [ ] Реализовать мессенджер (REST + WebSocket)
- [ ] Интегрировать FCM
- [ ] Написать unit тесты
- [ ] Развернуть на тестовый сервер

### Этап 3: Android UI (Week 2-3 параллельно)
- [ ] Создать Activity и Fragment структуру
- [ ] Реализовать Navigation
- [ ] Реализовать Login/Register экраны
- [ ] Реализовать Home, Search, Calendar, Messages
- [ ] Интегрировать Retrofit для REST API
- [ ] Интегрировать WebSocket для мессенджера
- [ ] Интегрировать Room DB для локального хранилища
- [ ] Интегрировать FCM

### Этап 4: Admin Web Panel (Week 3)
- [ ] Реализовать Dashboard
- [ ] Реализовать Users Management
- [ ] Реализовать Tutors Report
- [ ] Реализовать Notifications

### Этап 5: Тестирование и итоги (Week 4)
- [ ] E2E тенты
- [ ] Нагрузочное тестирование
- [ ] Security audit
- [ ] Документирование

---

## 10. Вопросы для уточнения

1. **Хранение файлов:** Локально в приложении → синхронизация, или прямая загрузка на облачное хранилище (AWS S3, Google Cloud Storage)?
2. **Email верификация:** Требуется ли обязательная верификация email при регистрации?
3. **История сообщений:** Хранить всю историю или только последние N сообщений / N дней?
4. **Push-уведомления:** Требуется ли также отправка email уведомлений?
5. **Платежи:** Упомянуто, что уроки бесплатные. Нужна ли система подарков/бонусов?
6. **Две-факторная аутентификация:** Требуется ли для администратора?
7. **Экспорт данных:** Нужна ли возможность экспорта данных пользователем?
8. **Многоязычность:** Приложение должно быть многоязычным?

---

**Дата подготовки:** 29 апреля 2026  
**Версия:** 1.0  
**Статус:** Утверждено для разработки
