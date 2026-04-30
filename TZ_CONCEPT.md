# Техническое задание (Концепт)
## Мобильное приложение для совместной работы учеников и репетиторов

**Дата:** 29 апреля 2026  
**Версия:** 1.0

---

## 1. Описание проекта

Платформа для подбора репетиторов, планирования уроков и взаимодействия.

**Основные модули:**
1. **Аутентификация** - регистрация и вход пользователей (ученик/репетитор/админ)
2. **Система подбора учителя** - персонализированный рейтинг на основе свойств репетитора и приоритетов ученика
3. **Планирование уроков** - создание, управление, отслеживание с локальной синхронизацией
4. **Мессенджер** - real-time общение с файлами, оффлайн очередь сообщений

---

## 2. Основные объекты системы

### User (Пользователь)
```
id, email, password_hash, role, is_verified, created_at
Роли: student, tutor, admin
```

### Student (Ученик)
```
full_name, avatar_url, bio
priority_weights = {k1, k2, k3, k4}  // веса для рейтинга
filters = {max_price, min_experience, verified_only}
```

### Tutor (Репетитор)
```
full_name, avatar_url, bio
specialization: []  // массив предметов
experience_years: int
hourly_rate: decimal
is_verified: bool
```

### TutorProperties (Свойства репетитора — рассчитанные)
```
effectiveness ∈ [0,1]        // скорость прогресса ученика
communication_quality ∈ [0,1] // качество общения
expertise_level ∈ [0,1]       // уровень знаний
responsiveness ∈ [0,1]        // скорость ответа
last_updated: timestamp
```

### Lesson (Урок)
```
student_id, tutor_id
scheduled_at: datetime
duration_minutes: int
status: scheduled | completed | cancelled
```

### StudentTest (Тест и результаты)
```
student_id, tutor_id, lesson_id
test_date: date
score_before: int
score_after: int
month_coefficient: decimal  // 1.0, 1.1, 1.2 и т.д.
```

### TutorRating (Оценка и отзыв)
```
tutor_id, student_id
rating_value ∈ [1,5]         // общая оценка
communication_score ∈ [1,5]
expertise_score ∈ [1,5]
review_text: string (optional)
created_at: timestamp
```

### Message (Сообщение)
```
sender_id, receiver_id
text: string
attachments: []  // файлы (тип: document, image; размер ≤ 10 MB)
is_read: bool
created_at: timestamp
```

### Notification (Уведомление)
```
user_id
type: lesson_request | lesson_confirmed | lesson_reminder | new_message | rating_received | test_scheduled
data: JSON
is_read: bool
```

### DeviceToken (FCM для push-уведомлений)
```
user_id, fcm_token
device_id, platform (android/ios)
```

---

## 3. Система рейтинга (Ключевой концепт)

### 3.1 Компоненты рейтинга

#### 1) Свойства репетитора (O_i) — объективные метрики
Нормализованы в диапазон [0, 1]

- **O₁ = Effectiveness (Эффективность)**
  - Источник: результаты тестов студентов
  - Формула: `(средний прирост баллов) / (количество месяцев сотрудничества)`
  - Нормализация: `O₁ = min(прирост / max_прогресс, 1.0)`

- **O₂ = Communication Quality (Качество коммуникации)**
  - Источник: оценка `communication_score` в рецензиях от учеников
  - Формула: `O₂ = (средняя оценка) / 5`

- **O₃ = Expertise Level (Уровень экспертизы)**
  - Источник: оценка `expertise_score` в рецензиях
  - Формула: `O₃ = (средняя оценка) / 5`

- **O₄ = Responsiveness (Отзывчивость)**
  - Источник: среднее время ответа на сообщения
  - Формула: `O₄ = max(0, 1 - (среднее_время_ответа_часов / 24))`

#### 2) Приоритеты ученика (k_i) — субъективные веса
Нормализованы: k₁ + k₂ + k₃ + k₄ = 1.0, каждый k_i ∈ [0, 1]

Ученик может выставить свои приоритеты:
- k₁ = приоритет Effectiveness
- k₂ = приоритет Communication
- k₃ = приоритет Expertise
- k₄ = приоритет Responsiveness

По умолчанию: k₁ = k₂ = k₃ = k₄ = 0.25

#### 3) Фильтры ученика (исключающие условия)
- max_price: исключить репетиторов дороже
- min_experience: исключить с опытом менее N лет
- verified_only: показывать только верифицированных

### 3.2 Формула рейтинга для ученика

Рейтинг репетитора T для ученика S:
```
Rating(T, S) = O₁(T) × k₁(S) + O₂(T) × k₂(S) + O₃(T) × k₃(S) + O₄(T) × k₄(S)

Диапазон: [0, 1]
```

### 3.3 Ежемесячный пересчет коэффициентов

За каждый завершённый месяц сотрудничества ученика с репетитором:
```
month_coefficient(m) = 1.0 + 0.1 × (m - 1)

Месяц 1: 1.0
Месяц 2: 1.1
Месяц 3: 1.2
...
Месяц n: 1.0 + 0.1(n-1)
```

Этот коэффициент используется при расчёте effectiveness:
```
Adjusted_effectiveness = effectiveness × month_coefficient
```

### 3.4 Процесс поиска репетитора (для ученика)

1. **Применить фильтры (исключения)**
   ```
   Candidates = {T ∈ All_Tutors | 
     T.hourly_rate ≤ student.max_price AND
     T.experience_years ≥ student.min_experience AND
     (NOT student.verified_only OR T.is_verified)}
   ```

2. **Вычислить рейтинг для каждого кандидата**
   ```
   FOR each T in Candidates:
       Rating(T, S) = O₁(T)×k₁(S) + O₂(T)×k₂(S) + O₃(T)×k₃(S) + O₄(T)×k₄(S)
   ```

3. **Отсортировать по убыванию рейтинга**

4. **Вернуть топ-N репетиторов**

---

## 4. Функциональные компоненты

### 4.1 Аутентификация
- Регистрация: email, пароль, роль (student/tutor)
- Вход: JWT токены (access + refresh)
- Верификация: email (опционально)

### 4.2 Управление профилем
- **Ученик**: обновлять приоритеты (k_i) и фильтры, загружать тесты
- **Репетитор**: обновлять данные, специализацию, расписание
- **Администратор**: верифицировать пользователей, просматривать статистику

### 4.3 Уроки и календарь
- Создание урока: ученик выбирает репетитора и время
- Статусы: scheduled → completed → rated (или cancelled)
- **Локальная синхронизация (Android)**:
  - Хранить уроки локально (Room DB)
  - При offline: использовать локальные данные
  - При online: синхронизировать с сервером

### 4.4 Мессенджер
- **REST API**: отправка сообщений, история, вложения
- **WebSocket**: real-time доставка (низкая latency)
- **Offline очередь**: сохранять сообщения локально до подключения

### 4.5 Уведомления
- **FCM (Firebase Cloud Messaging)** для push-уведомлений
- Типы: lesson_request, lesson_reminder, new_message, rating_received, test_scheduled
- История уведомлений в приложении

---

## 5. API Endpoints (примерная структура)

### Auth
- POST `/auth/register` - регистрация
- POST `/auth/login` - вход
- POST `/auth/refresh` - обновить токен

### Tutors
- GET `/tutors/search?filters=...&sort=...` - поиск с рейтингом
- GET `/tutors/{id}` - профиль
- GET `/tutors/{id}/properties` - свойства (рассчитанные)

### Students
- GET `/students/me/preferences` - мои приоритеты
- PUT `/students/me/preferences` - обновить приоритеты
- GET `/students/me/filters` - мои фильтры
- PUT `/students/me/filters` - обновить фильтры

### Lessons
- POST `/lessons` - создать урок
- GET `/lessons` - мои уроки
- PUT `/lessons/{id}/status` - обновить статус
- POST `/lessons/{id}/test-results` - загрузить результаты теста

### Messages
- GET `/messages/conversations` - диалоги
- GET `/messages/with/{user_id}` - история с пользователем
- POST `/messages/send` - отправить сообщение
- WS `/ws/messages/{user_id}` - real-time подключение

### Ratings
- POST `/tutors/{id}/rate` - оценить репетитора
- GET `/tutors/{id}/ratings` - все оценки

### Notifications
- GET `/notifications` - список
- POST `/notifications/device-token` - регистрировать FCM токен

### Admin
- GET `/admin/stats` - статистика
- GET `/admin/users` - список пользователей
- PUT `/admin/users/{id}/verify` - верифицировать

---

## 6. UI страницы (концептуально)

### Мобильное приложение (Android)
1. **Auth Screen** - регистрация/вход
2. **Home Screen** - список ближайших уроков, быстрые фильтры
3. **Search Tutors Screen** - поиск с фильтрами (price, experience, rating, verified)
4. **Tutor Profile Screen** - профиль, отзывы, расписание, кнопка "Book Lesson"
5. **Calendar Screen** - месячный/недельный вид уроков, локальное хранилище
6. **Messages Screen** - диалоги с остальными пользователями
7. **Chat Screen** - переписка, real-time обновление, вложения
8. **Notifications Screen** - история уведомлений
9. **Profile Screen** (Ученик) - профиль, приоритеты (слайдеры k_i), фильтры
10. **Profile Screen** (Репетитор) - профиль, свойства, мои студенты

### Web администратора (HTML+CSS+JS)
1. **Dashboard** - статистика (Total users, Active tutors, Total lessons, Avg rating)
2. **Users Management** - таблица, фильтры, верификация/удаление
3. **Tutors Report** - рейтинги, количество студентов, effectiveness score
4. **Notifications** - отправка массовых push-уведомлений

---

## 7. Примеры расчётов

### Пример 1: Рейтинг репетитора для конкретного ученика

**Репетитор Иван:**
- O₁ = 0.85 (effectiveness - студенты улучшили знания на 85%)
- O₂ = 0.9 (communication_quality - средняя оценка 4.5/5)
- O₃ = 0.8 (expertise_level - средняя оценка 4/5)
- O₄ = 0.95 (responsiveness - ответ в среднем за 2 часа)

**Ученик Мария (приоритеты):**
- k₁ = 0.4 (результативность важнее всего)
- k₂ = 0.2 (коммуникация)
- k₃ = 0.25 (экспертиза)
- k₄ = 0.15 (скорость ответа)

**Расчёт рейтинга:**
```
Rating = 0.85 × 0.4 + 0.9 × 0.2 + 0.8 × 0.25 + 0.95 × 0.15
       = 0.34 + 0.18 + 0.2 + 0.1425
       = 0.8625
```

Перевод в звёзды (0-5): 0.8625 × 5 = 4.31 ⭐

### Пример 2: Effectiveness репетитора

**Студент занимается 3 месяца:**
- Месяц 1: score_before = 50, score_after = 65, прирост = 15, коэф = 1.0
- Месяц 2: score_before = 65, score_after = 78, прирост = 13, коэф = 1.1
- Месяц 3: score_before = 78, score_after = 88, прирост = 10, коэф = 1.2

**Средний прирост:** (15 + 13 + 10) / 3 = 12.67 баллов в месяц

**Weighted average** (с учётом коэффициентов):
```
Effectiveness = (15×1.0 + 13×1.1 + 10×1.2) / (1.0 + 1.1 + 1.2)
              = (15 + 14.3 + 12) / 3.3
              = 41.3 / 3.3
              = 12.5 баллов/месяц (взвешено)
```

При нормализации (max_прирост = 15): O₁ = 12.5 / 15 = 0.83

### Пример 3: Месячный коэффициент

Если ученик и репетитор работают вместе:
- **Месяц 1:** month_coefficient = 1.0
- **Месяц 2:** month_coefficient = 1.1 (на 10% выше)
- **Месяц 3:** month_coefficient = 1.2 (на 20% выше)

Это даёт бонус долгосрочным отношениям ученик-репетитор.

---

## 8. Ключевые параметры

| Параметр | Значение |
|----------|----------|
| Max file size | 10 MB |
| JWT access timeout | 30 минут |
| JWT refresh timeout | 7 дней |
| Ежемесячное обновление properties | 1-го числа каждого месяца |
| WebSocket latency target | < 100 ms |
| Search response time | < 200 ms |
| Default priority weights | k₁=0.25, k₂=0.25, k₃=0.25, k₄=0.25 |
| Month coefficient increase | +0.1 за каждый месяц |

---

## 9. Вопросы для уточнения

1. Где хранятся файлы (облако/локально)?
2. Email верификация обязательна?
3. История сообщений - всё или только N последних?
4. Требуется двухфакторная аутентификация?
5. Возможность экспорта данных?
6. Многоязычность приложения?

---

**Версия:** 1.0  
**Дата:** 29 апреля 2026
