# NU Student Platform — Техническая документация

> Комплексная образовательная платформа для студентов Назарбаев Университета с AI-ассистентом для подготовки к экзаменам, управлением курсами, каталогом курсов и персонализированным дашбордом.

---

## Оглавление

1. [Обзор проекта](#1-обзор-проекта)
2. [Архитектура](#2-архитектура)
3. [Технологический стек](#3-технологический-стек)
4. [Структура репозитория](#4-структура-репозитория)
5. [Настройка окружения](#5-настройка-окружения)
6. [База данных](#6-база-данных)
7. [Backend API](#7-backend-api)
8. [Frontend](#8-frontend)
9. [AI-компоненты](#9-ai-компоненты)
10. [Фоновые задачи (Celery)](#10-фоновые-задачи-celery)
11. [Аутентификация и авторизация](#11-аутентификация-и-авторизация)
12. [Система уведомлений](#12-система-уведомлений)
13. [Хранилище файлов](#13-хранилище-файлов)
14. [CI/CD](#14-cicd)
15. [Roadmap по фазам](#15-roadmap-по-фазам)

---

## 1. Обзор проекта

### 1.1 Проблема

Студенты НУ не имеют единого инструмента для отслеживания прогресса обучения, подготовки к экзаменам и выбора курсов на основе статистики. Информация разбросана по разным системам (Registrar, Moodle, Google Calendar), а подготовка к экзаменам не персонализирована.

### 1.2 Решение

Платформа объединяет:

- **Dashboard** — графики успеваемости, календарь дедлайнов, AI-саммари по прогрессу
- **Courses Page** — управление курсами текущего семестра, автоматический парсинг силлабуса для загрузки дедлайнов
- **Course Catalog** — каталог всех курсов НУ со статистикой (avg GPA, распределение грейдов по профессорам), отзывами и рейтингами
- **AI Study Assistant** (киллер-фича) — генерация персонализированных мок-экзаменов, детальные репорты по слабым/сильным сторонам, флеш-карты, рекомендации

### 1.3 Целевая аудитория

Студенты Назарбаев Университета (валидация по домену `@nu.edu.kz`).

---

## 2. Архитектура

### 2.1 Высокоуровневая схема

```
┌─────────────┐     ┌──────────────────────────────────────────┐
│   Frontend   │────▶│              API Gateway                 │
│  Next.js     │◀────│           FastAPI (uvicorn)              │
│  :3000       │     │               :8000                      │
└─────────────┘     └──────┬──────────┬──────────┬─────────────┘
                           │          │          │
                    ┌──────▼───┐ ┌────▼────┐ ┌───▼──────────┐
                    │PostgreSQL│ │  Redis   │ │  S3 / Local  │
                    │  :5432   │ │  :6379   │ │   Storage    │
                    └──────────┘ └────┬────┘ └──────────────┘
                                      │
                               ┌──────▼──────┐
                               │Celery Worker│
                               │  (parsing,  │
                               │  AI tasks)  │
                               └──────┬──────┘
                                      │
                               ┌──────▼──────┐
                               │  LLM API    │
                               │ (OpenAI /   │
                               │  Anthropic) │
                               └─────────────┘
```

### 2.2 Паттерн слоёв (Backend)

```
HTTP Layer (Routers)     — приём запросов, валидация через Pydantic, вызов сервисов
       │
Service Layer            — бизнес-логика, оркестрация между репозиториями
       │
Repository Layer         — доступ к данным, SQL-запросы через SQLAlchemy
       │
Database (Models)        — SQLAlchemy 2.0 Mapped models
```

Каждый слой зависит только от нижележащего. Сервисы получают репозитории через dependency injection (FastAPI Depends).

### 2.3 Принципы

- **Repository → Service → Router** разделение ответственности
- **Pydantic-модели** для всех request/response схем
- **Глобальная обработка ошибок** через `AppException` иерархию
- **Structured logging** через structlog
- **Async everywhere** — asyncpg, async Redis, async HTTP

---

## 3. Технологический стек

### 3.1 Backend

| Компонент | Технология | Назначение |
|-----------|-----------|------------|
| Framework | FastAPI | Async web framework |
| Server | Uvicorn | ASGI server |
| ORM | SQLAlchemy 2.0 (async) | Database access |
| DB Driver | asyncpg | Async PostgreSQL driver |
| Migrations | Alembic | Schema migrations |
| Task Queue | Celery + Redis | Background jobs |
| Cache | Redis | Session store, caching |
| Validation | Pydantic v2 | Request/response models |
| Auth | python-jose | JWT tokens |
| HTTP Client | httpx | Google OAuth, external APIs |
| PDF Parsing | pdfplumber | Transcript extraction |
| Storage | boto3 / local | File uploads (S3) |
| AI | openai | LLM calls (mock exams, parsing) |
| Logging | structlog | Structured JSON logging |
| Linter | ruff | Linting + formatting |
| Types | mypy | Static type checking |
| Tests | pytest + pytest-asyncio | Testing framework |

### 3.2 Frontend

| Компонент | Технология | Назначение |
|-----------|-----------|------------|
| Framework | Next.js 14+ (App Router) | React meta-framework |
| Language | TypeScript | Type safety |
| Styling | Tailwind CSS | Utility-first CSS |
| UI Library | shadcn/ui | Component library |
| State | Zustand | Global state (auth) |
| Charts | Recharts | Dashboard graphs |
| Calendar | FullCalendar | Deadline calendar |
| File Upload | react-dropzone | Drag & drop uploads |
| HTTP | fetch (native) | API client |

### 3.3 Инфраструктура

| Компонент | Технология |
|-----------|-----------|
| Database | PostgreSQL 16 + pgvector |
| Cache/Queue | Redis 7 |
| Containers | Docker + Docker Compose |
| CI/CD | GitHub Actions |
| Frontend Deploy | Vercel |
| Backend Deploy | Railway / Render |

### 3.4 Установка зависимостей

**Backend:**

```bash
# Production
uv add fastapi "uvicorn[standard]" "sqlalchemy[asyncio]" asyncpg alembic \
  "celery[redis]" redis pydantic-settings "python-jose[cryptography]" httpx \
  python-multipart pdfplumber boto3 openai structlog aiofiles

# Development
uv add --dev pytest pytest-asyncio pytest-cov ruff mypy factory-boy faker
```

**Frontend:**

```bash
npm install zustand recharts @fullcalendar/react @fullcalendar/daygrid \
  @fullcalendar/timegrid react-dropzone
npx shadcn@latest add button card input checkbox select table badge \
  avatar alert dialog dropdown-menu separator scroll-area progress tabs toast
```

---

## 4. Структура репозитория

```
nu-platform/
├── docker-compose.yml
├── docker-compose.prod.yml
├── .github/
│   └── workflows/
│       └── ci.yml
│
├── backend/
│   ├── Dockerfile
│   ├── pyproject.toml
│   ├── uv.lock
│   ├── alembic.ini
│   ├── alembic/
│   │   ├── env.py
│   │   └── versions/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                        # FastAPI app factory, lifespan, middleware
│   │   ├── config.py                      # Pydantic BaseSettings
│   │   ├── database.py                    # async engine, session factory
│   │   ├── redis.py                       # Redis client init
│   │   ├── storage.py                     # S3 / local file storage
│   │   ├── dependencies.py                # DI: get_db, get_current_user, service factories
│   │   ├── logging.py                     # structlog configuration
│   │   │
│   │   ├── exceptions/
│   │   │   ├── __init__.py
│   │   │   ├── base.py                    # AppException base class
│   │   │   ├── errors.py                  # NotFound, Unauthorized, Forbidden, etc.
│   │   │   └── handlers.py                # FastAPI exception handlers
│   │   │
│   │   ├── middleware/
│   │   │   ├── cors.py
│   │   │   └── logging.py                 # Request/response logging middleware
│   │   │
│   │   ├── models/
│   │   │   ├── __init__.py                # import all models
│   │   │   ├── base.py                    # Base, IDMixin, TimestampMixin
│   │   │   ├── user.py                    # User, Transcript
│   │   │   ├── course.py                  # Course, CourseSection, Enrollment, MajorRequirement
│   │   │   ├── deadline.py                # UserCourse, Syllabus, Deadline
│   │   │   ├── catalog.py                 # CourseStat, CourseReview, CourseRating, ReviewReport
│   │   │   ├── study.py                   # StudyMaterial, MaterialChunk, MockExam, MockAttempt,
│   │   │   │                              #   MockResult, Recommendation, Flashcard, FlashcardReview
│   │   │   └── notification.py            # Notification, NotificationPreference, EmailQueue
│   │   │
│   │   ├── schemas/
│   │   │   ├── __init__.py
│   │   │   ├── common.py                  # ApiResponse[T], PaginationParams, PaginatedResponse
│   │   │   ├── auth.py                    # GoogleAuthURL, GoogleCallback, TokenPair, RefreshRequest
│   │   │   ├── user.py                    # UserProfileResponse, UserProfileUpdate, UserStats
│   │   │   ├── transcript.py              # CourseRecord, ParsedTranscriptData, TranscriptStatus
│   │   │   ├── course.py                  # CourseResponse, UserCourseCreate, DeadlineCreate/Response
│   │   │   ├── catalog.py                 # CatalogCourse, CourseStatResponse, ReviewCreate/Response
│   │   │   ├── study.py                   # MaterialUpload, MockExamConfig, MockExamResponse,
│   │   │   │                              #   AttemptSubmit, MockResultResponse, FlashcardResponse
│   │   │   └── notification.py            # NotificationResponse, PreferenceUpdate
│   │   │
│   │   ├── repositories/
│   │   │   ├── __init__.py
│   │   │   ├── base.py                    # BaseRepository[T] — generic CRUD
│   │   │   ├── user.py                    # UserRepository (get_by_email, get_by_google_id)
│   │   │   ├── transcript.py              # TranscriptRepository (get_by_user_id)
│   │   │   ├── course.py                  # CourseRepository (get_or_create, search)
│   │   │   ├── enrollment.py              # EnrollmentRepository
│   │   │   ├── deadline.py                # DeadlineRepository (get_by_date_range, by_user)
│   │   │   ├── catalog.py                 # CatalogRepository (stats aggregation, reviews)
│   │   │   ├── study.py                   # MaterialRepo, MockExamRepo, FlashcardRepo
│   │   │   └── notification.py            # NotificationRepository
│   │   │
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── auth.py                    # Google OAuth flow, JWT issuance
│   │   │   ├── user.py                    # Profile CRUD, stats calculation
│   │   │   ├── transcript.py              # Upload, status polling, confirm/manual
│   │   │   ├── transcript_parser.py       # PDF extraction + regex/LLM parsing
│   │   │   ├── course.py                  # Semester course management
│   │   │   ├── syllabus_parser.py         # Syllabus PDF → deadline extraction
│   │   │   ├── deadline.py                # Deadline CRUD, calendar queries
│   │   │   ├── catalog.py                 # Course catalog, stats, reviews
│   │   │   ├── study_assistant.py         # Mock exam generation, result analysis
│   │   │   ├── flashcard.py               # Flashcard generation, SM-2 algorithm
│   │   │   ├── recommendation.py          # Notes generation, YouTube search
│   │   │   ├── notification.py            # Notification creation + dispatch
│   │   │   └── email.py                   # Gmail API email sending
│   │   │
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   ├── router.py                  # include all v1 routers
│   │   │   └── v1/
│   │   │       ├── auth.py                # /auth/*
│   │   │       ├── users.py               # /users/*
│   │   │       ├── transcripts.py         # /transcripts/*
│   │   │       ├── courses.py             # /courses/*
│   │   │       ├── deadlines.py           # /deadlines/*
│   │   │       ├── catalog.py             # /catalog/*
│   │   │       ├── study.py               # /study/*
│   │   │       ├── flashcards.py          # /flashcards/*
│   │   │       └── notifications.py       # /notifications/*
│   │   │
│   │   ├── tasks/
│   │   │   ├── __init__.py
│   │   │   ├── celery_app.py              # Celery configuration
│   │   │   ├── parse_transcript.py        # Async transcript parsing
│   │   │   ├── parse_syllabus.py          # Async syllabus parsing
│   │   │   ├── generate_mock.py           # Mock exam generation
│   │   │   ├── index_material.py          # Chunking + embedding
│   │   │   ├── aggregate_stats.py         # Periodic course stats update
│   │   │   ├── send_email.py              # Email queue processing
│   │   │   └── deadline_reminders.py      # Scheduled deadline notifications
│   │   │
│   │   └── utils/
│   │       ├── jwt.py                     # JWTService class
│   │       ├── pdf.py                     # PDF text extraction helpers
│   │       ├── gpa.py                     # Grade → GPA point conversion
│   │       ├── validators.py              # Email domain validation
│   │       └── sm2.py                     # SM-2 spaced repetition algorithm
│   │
│   └── tests/
│       ├── conftest.py                    # Fixtures: test DB, client, auth
│       ├── test_auth.py
│       ├── test_transcript.py
│       ├── test_courses.py
│       └── ...
│
└── frontend/
    ├── Dockerfile
    ├── package.json
    ├── tsconfig.json
    ├── tailwind.config.ts
    ├── components.json                    # shadcn config
    └── src/
        ├── app/
        │   ├── layout.tsx                 # Root layout, fonts, providers
        │   ├── page.tsx                   # Redirect → /dashboard or /login
        │   ├── (auth)/
        │   │   ├── login/page.tsx
        │   │   └── callback/page.tsx      # OAuth callback
        │   └── (main)/
        │       ├── layout.tsx             # Protected layout + app shell
        │       ├── dashboard/page.tsx
        │       ├── courses/
        │       │   ├── page.tsx           # My courses this semester
        │       │   └── [id]/page.tsx      # Course detail + deadlines
        │       ├── catalog/
        │       │   ├── page.tsx           # Course catalog list
        │       │   └── [id]/page.tsx      # Course stats + reviews
        │       ├── study/
        │       │   ├── page.tsx           # Study assistant home
        │       │   ├── mock/[id]/page.tsx # Take a mock exam
        │       │   └── report/[id]/page.tsx
        │       ├── flashcards/page.tsx
        │       ├── onboarding/
        │       │   ├── page.tsx           # 3-step wizard
        │       │   ├── consent-step.tsx
        │       │   ├── upload-step.tsx
        │       │   └── confirm-step.tsx
        │       ├── profile/page.tsx
        │       └── settings/page.tsx
        │
        ├── components/
        │   ├── ui/                        # shadcn components
        │   ├── layout/
        │   │   ├── app-shell.tsx
        │   │   ├── sidebar.tsx
        │   │   └── header.tsx
        │   ├── dashboard/
        │   │   ├── gpa-chart.tsx
        │   │   ├── deadline-calendar.tsx
        │   │   ├── ai-summary.tsx
        │   │   └── stats-cards.tsx
        │   ├── courses/
        │   │   ├── course-card.tsx
        │   │   ├── deadline-form.tsx
        │   │   └── syllabus-upload.tsx
        │   ├── catalog/
        │   │   ├── course-list.tsx
        │   │   ├── grade-distribution.tsx
        │   │   ├── review-form.tsx
        │   │   └── rating-radar.tsx
        │   ├── study/
        │   │   ├── material-upload.tsx
        │   │   ├── mock-config.tsx
        │   │   ├── question-view.tsx
        │   │   ├── result-report.tsx
        │   │   └── recommendation-list.tsx
        │   ├── flashcards/
        │   │   ├── flashcard-flip.tsx
        │   │   └── review-controls.tsx
        │   └── onboarding/
        │       ├── file-dropzone.tsx
        │       ├── parsed-data-review.tsx
        │       └── consent-form.tsx
        │
        ├── lib/
        │   ├── api.ts                     # API client (fetch wrapper + refresh)
        │   ├── auth.ts                    # Token helpers
        │   └── utils.ts                   # Date formatting, GPA colors, etc.
        │
        ├── hooks/
        │   ├── use-auth.ts                # Zustand auth store
        │   ├── use-courses.ts
        │   ├── use-deadlines.ts
        │   └── use-flashcards.ts
        │
        └── types/
            ├── auth.ts
            ├── user.ts
            ├── course.ts
            ├── transcript.ts
            ├── catalog.ts
            ├── study.ts
            └── notification.ts
```

---

## 5. Настройка окружения

### 5.1 Переменные окружения

Создать `backend/.env`:

```env
# App
APP_NAME="NU Student Platform"
DEBUG=true
ALLOWED_ORIGINS=["http://localhost:3000"]

# Database
DATABASE_URL=postgresql+asyncpg://app:secret@localhost:5432/nu_platform
DB_POOL_SIZE=10
DB_MAX_OVERFLOW=20

# Redis
REDIS_URL=redis://localhost:6379/0

# Google OAuth
GOOGLE_CLIENT_ID=<your-client-id>.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=<your-client-secret>
GOOGLE_REDIRECT_URI=http://localhost:3000/auth/callback

# JWT
JWT_SECRET=<random-32-char-string>
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# Storage
USE_LOCAL_STORAGE=true
LOCAL_STORAGE_PATH=/app/uploads
S3_ENDPOINT_URL=
S3_ACCESS_KEY=
S3_SECRET_KEY=
S3_BUCKET=nu-platform
S3_REGION=us-east-1

# Celery
CELERY_BROKER_URL=redis://localhost:6379/1
CELERY_RESULT_BACKEND=redis://localhost:6379/2

# LLM
OPENAI_API_KEY=sk-...
```

Создать `frontend/.env.local`:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
```

### 5.2 Запуск через Docker

```bash
# Полный стек
docker-compose up --build

# Только инфраструктура (БД + Redis), backend/frontend локально
docker-compose up postgres redis

# Backend
cd backend && uv run uvicorn app.main:app --reload --port 8000

# Celery worker
cd backend && uv run celery -A app.tasks.celery_app worker -l info

# Frontend
cd frontend && npm run dev
```

### 5.3 Миграции

```bash
cd backend

# Создать миграцию
uv run alembic revision --autogenerate -m "описание изменений"

# Применить
uv run alembic upgrade head

# Откатить
uv run alembic downgrade -1
```

### 5.4 Google OAuth Setup

1. Перейти в [Google Cloud Console](https://console.cloud.google.com/)
2. Создать проект или выбрать существующий
3. APIs & Services → Credentials → Create OAuth 2.0 Client ID
4. Authorized redirect URIs: `http://localhost:3000/auth/callback`
5. Скопировать Client ID и Client Secret в `.env`

---

## 6. База данных

### 6.1 ER-диаграмма (упрощённая)

```
users 1──1 transcripts
users 1──* enrollments *──1 courses
users 1──* user_courses *──1 courses
courses 1──* course_sections
user_courses 1──1 syllabi
user_courses 1──* deadlines
user_courses 1──* study_materials 1──* material_chunks
user_courses 1──* mock_exams 1──* mock_attempts 1──1 mock_results 1──* recommendations
users 1──* flashcards *──1 user_courses
flashcards 1──* flashcard_reviews
courses 1──* course_stats
courses 1──* course_reviews 1──* course_ratings
users 1──* notifications
users 1──* notification_preferences
```

### 6.2 Таблицы (полный список)

| # | Таблица | Описание | Домен |
|---|---------|----------|-------|
| 1 | `users` | Профиль студента | Auth |
| 2 | `transcripts` | Загруженные транскрипты | Auth |
| 3 | `courses` | Каталог курсов | Academics |
| 4 | `course_sections` | Секции (профессор + семестр) | Academics |
| 5 | `enrollments` | Историческая связь user↔course | Academics |
| 6 | `major_requirements` | Требования программы | Academics |
| 7 | `user_courses` | Курсы текущего семестра | Calendar |
| 8 | `syllabi` | Загруженные силлабусы | Calendar |
| 9 | `deadlines` | Все дедлайны | Calendar |
| 10 | `course_stats` | Агрегированная статистика | Catalog |
| 11 | `course_reviews` | Отзывы о курсах | Catalog |
| 12 | `course_ratings` | Оценки по критериям (1–10) | Catalog |
| 13 | `review_reports` | Жалобы на отзывы | Catalog |
| 14 | `study_materials` | Учебные материалы | AI |
| 15 | `material_chunks` | Чанки для RAG + embeddings | AI |
| 16 | `mock_exams` | Сгенерированные мок-экзамены | AI |
| 17 | `mock_attempts` | Попытки прохождения моков | AI |
| 18 | `mock_results` | Детальные результаты | AI |
| 19 | `recommendations` | Рекомендации (ноутсы, видео) | AI |
| 20 | `flashcards` | Флеш-карты с SM-2 | AI |
| 21 | `flashcard_reviews` | История повторений | AI |
| 22 | `notifications` | Уведомления | Notifications |
| 23 | `notification_preferences` | Настройки уведомлений | Notifications |
| 24 | `email_queue` | Очередь email-рассылки | Notifications |

### 6.3 Ключевые модели

Все модели используют **SQLAlchemy 2.0 Mapped** синтаксис с `Mapped[T]` и `mapped_column()`.

Общие миксины:

```python
class IDMixin:
    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)

class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
```

Все enum'ы наследуются от `str, enum.Enum` для совместимости с Pydantic:

```python
class TranscriptStatus(str, enum.Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
```

Полные модели — см. файл `backend/app/models/` в репозитории.

### 6.4 Расширения PostgreSQL

```sql
-- Для AI Study Assistant (embeddings)
CREATE EXTENSION IF NOT EXISTS vector;

-- Для полнотекстового поиска в каталоге (опционально)
CREATE EXTENSION IF NOT EXISTS pg_trgm;
```

---

## 7. Backend API

### 7.1 Общие принципы

**Формат ответов** — все эндпоинты возвращают `ApiResponse[T]`:

```json
{
  "success": true,
  "data": { ... },
  "message": null
}
```

**Формат ошибок:**

```json
{
  "success": false,
  "error_code": "NOT_FOUND",
  "message": "User not found"
}
```

**Аутентификация** — Bearer token в заголовке `Authorization`:

```
Authorization: Bearer <access_token>
```

### 7.2 Иерархия ошибок

```python
AppException(message, status_code, error_code)  # base
├── NotFoundError(entity)                        # 404 NOT_FOUND
├── UnauthorizedError(message)                   # 401 UNAUTHORIZED
├── ForbiddenError(message)                      # 403 FORBIDDEN
├── InvalidEmailDomainError(message)             # 403 INVALID_EMAIL_DOMAIN
├── InvalidTokenError(message)                   # 401 INVALID_TOKEN
├── OAuthError(message)                          # 400 OAUTH_ERROR
├── FileValidationError(message)                 # 422 FILE_VALIDATION_ERROR
├── TranscriptParsingError(message)              # 422 TRANSCRIPT_PARSE_ERROR
└── RateLimitError(message)                      # 429 RATE_LIMITED
```

### 7.3 Полная таблица эндпоинтов

#### Auth

| Метод | Путь | Описание | Auth |
|-------|------|----------|------|
| GET | `/auth/google/url` | Получить URL для Google OAuth | Нет |
| POST | `/auth/google/callback` | Обменять code на JWT пару | Нет |
| POST | `/auth/refresh` | Обновить access token | Нет* |
| POST | `/auth/logout` | Инвалидировать refresh token | Да |

#### Users

| Метод | Путь | Описание | Auth |
|-------|------|----------|------|
| GET | `/users/me` | Профиль текущего пользователя | Да |
| PATCH | `/users/me` | Обновить профиль | Да |
| GET | `/users/me/enrollments` | История курсов | Да |
| GET | `/users/me/stats` | Статистика (GPA, кредиты) | Да |

#### Transcripts

| Метод | Путь | Описание | Auth |
|-------|------|----------|------|
| POST | `/transcripts/upload` | Загрузить PDF транскрипт | Да |
| GET | `/transcripts/status` | Статус парсинга | Да |
| POST | `/transcripts/confirm` | Подтвердить распарсенные данные | Да |
| POST | `/transcripts/manual` | Ручной ввод данных (без PDF) | Да |

#### Courses (текущий семестр)

| Метод | Путь | Описание | Auth |
|-------|------|----------|------|
| GET | `/courses` | Мои курсы текущего семестра | Да |
| POST | `/courses` | Добавить курс в текущий семестр | Да |
| GET | `/courses/{id}` | Детали курса | Да |
| DELETE | `/courses/{id}` | Удалить курс из семестра | Да |
| POST | `/courses/{id}/syllabus` | Загрузить силлабус для парсинга | Да |
| GET | `/courses/{id}/syllabus/status` | Статус парсинга силлабуса | Да |

#### Deadlines

| Метод | Путь | Описание | Auth |
|-------|------|----------|------|
| GET | `/deadlines` | Все дедлайны (фильтр по дате) | Да |
| POST | `/deadlines` | Создать дедлайн вручную | Да |
| PATCH | `/deadlines/{id}` | Обновить дедлайн | Да |
| DELETE | `/deadlines/{id}` | Удалить дедлайн | Да |
| PATCH | `/deadlines/{id}/complete` | Отметить выполненным | Да |

#### Catalog

| Метод | Путь | Описание | Auth |
|-------|------|----------|------|
| GET | `/catalog` | Список курсов (пагинация, поиск, фильтры) | Да |
| GET | `/catalog/{id}` | Детали курса + статистика | Да |
| GET | `/catalog/{id}/stats` | Статистика (GPA, грейды по профессорам) | Да |
| GET | `/catalog/{id}/reviews` | Отзывы | Да |
| POST | `/catalog/{id}/reviews` | Оставить отзыв + рейтинги | Да |
| POST | `/catalog/reviews/{id}/report` | Пожаловаться на отзыв | Да |

#### Study Assistant

| Метод | Путь | Описание | Auth |
|-------|------|----------|------|
| GET | `/study/{course_id}/materials` | Список загруженных материалов | Да |
| POST | `/study/{course_id}/materials` | Загрузить материал | Да |
| DELETE | `/study/materials/{id}` | Удалить материал | Да |
| POST | `/study/{course_id}/mock` | Сгенерировать мок-экзамен | Да |
| GET | `/study/mock/{id}` | Получить мок-экзамен | Да |
| POST | `/study/mock/{id}/submit` | Сдать мок-экзамен | Да |
| GET | `/study/mock/{id}/result` | Результат + репорт | Да |
| GET | `/study/{course_id}/history` | История моков по курсу | Да |

#### Flashcards

| Метод | Путь | Описание | Auth |
|-------|------|----------|------|
| GET | `/flashcards/due` | Карты на сегодня (SM-2) | Да |
| GET | `/flashcards/course/{id}` | Карты по курсу | Да |
| POST | `/flashcards/{id}/review` | Оценить карту (again/hard/good/easy) | Да |
| POST | `/flashcards/generate/{course_id}` | Сгенерировать новые карты | Да |

#### Notifications

| Метод | Путь | Описание | Auth |
|-------|------|----------|------|
| GET | `/notifications` | Список уведомлений | Да |
| PATCH | `/notifications/{id}/read` | Отметить прочитанным | Да |
| PATCH | `/notifications/read-all` | Отметить все прочитанными | Да |
| GET | `/notifications/preferences` | Настройки уведомлений | Да |
| PATCH | `/notifications/preferences` | Обновить настройки | Да |

### 7.4 Паттерн Repository

Все репозитории наследуют `BaseRepository[T]`:

```python
class BaseRepository(Generic[T]):
    def __init__(self, session: AsyncSession, model: type[T]):
        self.session = session
        self.model = model

    async def get_by_id(self, id: UUID) -> T | None
    async def get_all(self, skip: int = 0, limit: int = 20) -> list[T]
    async def create(self, **kwargs) -> T
    async def update(self, instance: T, **kwargs) -> T
    async def delete(self, instance: T) -> None
    async def count(self) -> int
```

Специфичные репозитории добавляют свои методы:

```python
class UserRepository(BaseRepository[User]):
    async def get_by_email(self, email: str) -> User | None
    async def get_by_google_id(self, google_id: str) -> User | None

class CourseRepository(BaseRepository[Course]):
    async def get_by_code(self, code: str) -> Course | None
    async def get_or_create(self, code: str, defaults: dict) -> Course
    async def search(self, query: str, filters: dict, pagination: PaginationParams) -> PaginatedResponse
```

### 7.5 Dependency Injection

Сервисы получают зависимости через FastAPI `Depends`:

```python
async def get_auth_service(
    db: AsyncSession = Depends(get_db),
    redis: Redis = Depends(get_redis),
) -> AuthService:
    return AuthService(
        settings=get_settings(),
        user_repo=UserRepository(db),
        jwt_service=get_jwt_service(),
        redis=redis,
    )
```

Два уровня auth-зависимостей:

```python
get_current_user          # Проверяет Bearer token, возвращает User
get_current_onboarded_user  # + проверяет is_onboarded == True
```

---

## 8. Frontend

### 8.1 Роутинг

```
/login                  — экран входа (публичный)
/auth/callback          — обработка OAuth redirect (публичный)
/onboarding             — 3-шаговый wizard (auth required, не onboarded)
/dashboard              — главная страница (auth + onboarded)
/courses                — курсы текущего семестра
/courses/[id]           — детали курса + дедлайны
/catalog                — каталог курсов
/catalog/[id]           — статистика + отзывы курса
/study                  — AI Study Assistant
/study/mock/[id]        — прохождение мок-экзамена
/study/report/[id]      — результат мока
/flashcards             — флеш-карты
/profile                — профиль студента
/settings               — настройки уведомлений
```

### 8.2 Auth Flow

```
1. User нажимает "Войти через Google"
2. Frontend GET /auth/google/url → получает Google OAuth URL
3. Redirect на Google → пользователь логинится
4. Google redirect на /auth/callback?code=XXX
5. Frontend POST /auth/google/callback {code} → получает TokenPair
6. Сохраняет access_token + refresh_token в localStorage
7. GET /users/me → проверяет is_onboarded
8. Redirect на /onboarding (если false) или /dashboard (если true)
```

Auto-refresh:

```
1. API client получает 401
2. Пробует POST /auth/refresh с refresh_token
3. Если успех → обновляет токены, повторяет запрос
4. Если неудача → redirect на /login
```

### 8.3 API Client

Обёртка над `fetch` с автоматическим:
- Добавлением `Authorization: Bearer` заголовка
- Рефрешем токена при 401
- Парсингом `ApiResponse<T>` формата
- Обработкой ошибок

```typescript
// Использование:
const user = await api.get<UserProfile>("/users/me");
const tokens = await api.post<TokenPair>("/auth/google/callback", { code });
const status = await api.uploadFile<TranscriptStatus>("/transcripts/upload", file);
```

### 8.4 State Management

**Zustand** для глобального состояния:
- `useAuth` — user, isAuthenticated, isLoading, tokens
- React Query или SWR (опционально) для серверного состояния и кэширования

Локальный state (`useState`) — для форм, UI state, wizard steps.

### 8.5 Ключевые компоненты

| Компонент | Библиотека | Где используется |
|-----------|-----------|-----------------|
| Calendar | FullCalendar | Dashboard, Courses |
| Charts (line, bar, pie) | Recharts | Dashboard, Catalog, Report |
| Radar chart | Recharts | Catalog (рейтинги) |
| File dropzone | react-dropzone | Onboarding, Syllabus upload, Materials |
| Data tables | shadcn Table | Courses, Catalog, Enrollments |
| Flashcard flip | Custom CSS | Flashcards page |

---

## 9. AI-компоненты

### 9.1 Transcript Parser

**Стратегия:** Regex-first → LLM fallback.

1. Извлечь текст из PDF через `pdfplumber`
2. Попробовать regex-парсинг (формат НУ транскрипта)
3. Если regex не сработал → отправить текст в LLM с промптом:

```
Extract the following from this university transcript:
- major (string)
- gpa (float)
- total_credits (int)
- courses: list of {code, title, credits, grade, semester, year}

Return ONLY valid JSON, no markdown or explanation.
```

### 9.2 Syllabus Parser

Аналогичная стратегия. LLM-промпт:

```
Extract all deadlines from this course syllabus:
- title (string)
- type: one of [assignment, midterm, final, quiz, project, lab, other]
- due_date (ISO format YYYY-MM-DD)
- weight (percentage, nullable)
- description (nullable)

Return ONLY valid JSON array.
```

### 9.3 Mock Exam Generation (RAG)

```
1. User запрашивает мок → POST /study/{course_id}/mock с config
2. Backend:
   a. Загружает material_chunks для course_id
   b. Если есть weak topics из предыдущих mock_results → similarity search по ним
   c. Собирает контекст (top-k чанков)
   d. Промпт в LLM:
      "Generate a mock exam with {n} questions based on these materials.
       Focus on weak topics: {topics}.
       Question types: {mcq, open_ended, true_false}.
       Return JSON: [{id, type, question, options?, correct_answer, topic, difficulty, points}]"
3. Сохраняет MockExam в БД
```

### 9.4 Result Analysis

```
1. User сдаёт мок → POST /study/mock/{id}/submit
2. Backend:
   a. MCQ → автопроверка
   b. Open-ended → LLM-оценка с rubric:
      "Score this answer 0-10. Question: {q}. Correct answer: {a}. Student answer: {sa}.
       Return JSON: {score, feedback}"
   c. Группировка по topics → strengths/weaknesses
   d. Генерация overall_feedback через LLM
   e. Сохранение MockResult
```

### 9.5 Flashcard Generation

```
Based on these weak topics: {topics}
And these study materials: {chunks}
Generate {n} flashcards as JSON: [{question, answer, topic, difficulty}]
Questions should test understanding, not memorization.
```

### 9.6 SM-2 Algorithm

Реализация SuperMemo SM-2 для spaced repetition:

```python
def sm2_update(card: Flashcard, rating: FlashcardRating) -> Flashcard:
    q = {"again": 0, "hard": 2, "good": 4, "easy": 5}[rating]

    if q < 3:  # Failed
        card.interval = 1
        card.review_count = 0
    else:
        if card.review_count == 0:
            card.interval = 1
        elif card.review_count == 1:
            card.interval = 6
        else:
            card.interval = round(card.interval * card.ease_factor)

        card.ease_factor = max(1.3, card.ease_factor + 0.1 - (5 - q) * (0.08 + (5 - q) * 0.02))
        card.review_count += 1

    card.next_review_date = date.today() + timedelta(days=card.interval)
    return card
```

---

## 10. Фоновые задачи (Celery)

### 10.1 Конфигурация

```python
# app/tasks/celery_app.py
from celery import Celery
from celery.schedules import crontab

celery_app = Celery("nu_platform")
celery_app.config_from_object({
    "broker_url": settings.CELERY_BROKER_URL,
    "result_backend": settings.CELERY_RESULT_BACKEND,
    "task_serializer": "json",
    "accept_content": ["json"],
    "timezone": "Asia/Almaty",
    "task_track_started": True,
    "task_acks_late": True,
    "worker_prefetch_multiplier": 1,
})

celery_app.conf.beat_schedule = {
    "deadline-reminders": {
        "task": "app.tasks.deadline_reminders.send_deadline_reminders",
        "schedule": crontab(hour=9, minute=0),  # каждый день в 9:00
    },
    "aggregate-stats": {
        "task": "app.tasks.aggregate_stats.aggregate_course_stats",
        "schedule": crontab(hour=3, minute=0),  # каждую ночь
    },
    "process-email-queue": {
        "task": "app.tasks.send_email.process_email_queue",
        "schedule": 60.0,  # каждую минуту
    },
}
```

### 10.2 Список задач

| Задача | Триггер | Описание |
|--------|---------|----------|
| `parse_transcript` | Upload endpoint | PDF → текст → structured data |
| `parse_syllabus` | Syllabus upload | PDF → дедлайны |
| `index_material` | Material upload | Chunking → embeddings → vector store |
| `generate_mock` | Mock request | LLM → mock exam JSON |
| `aggregate_stats` | Cron (ночь) | Пересчёт course_stats |
| `send_deadline_reminders` | Cron (утро) | Проверка дедлайнов → notifications |
| `process_email_queue` | Cron (минута) | Отправка pending emails |

---

## 11. Аутентификация и авторизация

### 11.1 Flow

```
Google OAuth2 → Validate @nu.edu.kz → Find/Create User → Issue JWT (access + refresh)
```

### 11.2 Токены

| Тип | TTL | Хранение (frontend) | Хранение (backend) |
|-----|-----|--------------------|--------------------|
| Access Token | 30 мин | localStorage | Не хранится (stateless) |
| Refresh Token | 7 дней | localStorage | Redis (для revocation) |

### 11.3 Защита эндпоинтов

```python
# Любой аутентифицированный пользователь
@router.get("/", dependencies=[Depends(get_current_user)])

# Только прошедшие онбординг
@router.get("/", dependencies=[Depends(get_current_onboarded_user)])
```

### 11.4 Refresh Flow

```
1. Client sends request with expired access token
2. Server returns 401
3. Client calls POST /auth/refresh with refresh_token
4. Server:
   a. Validates refresh token JWT
   b. Checks Redis for token existence (not revoked)
   c. Deletes old refresh token from Redis
   d. Issues new token pair
   e. Stores new refresh token in Redis
5. Client retries original request with new access token
```

---

## 12. Система уведомлений

### 12.1 Типы

| Тип | Триггер | Каналы |
|-----|---------|--------|
| `deadline_reminder` | За N дней до дедлайна | In-app, Email |
| `mock_ready` | Мок-экзамен сгенерирован | In-app |
| `report_ready` | Результат мока готов | In-app, Email |
| `weekly_digest` | Cron (понедельник) | Email |
| `system` | Админ | In-app |

### 12.2 Email

Gmail API через service account. HTML-шаблоны для каждого типа. Очередь через таблицу `email_queue` + Celery beat.

---

## 13. Хранилище файлов

### 13.1 Что хранится

| Тип файла | Путь в storage | Формат |
|-----------|---------------|--------|
| Транскрипт | `transcripts/{user_id}/{filename}` | PDF |
| Силлабус | `syllabi/{user_course_id}/{filename}` | PDF, DOCX |
| Учебные материалы | `materials/{user_course_id}/{filename}` | PDF, DOCX, PNG, JPG |
| Аватар (опц.) | `avatars/{user_id}` | JPG, PNG |

### 13.2 Dev vs Prod

- **Dev:** локальное хранение в `/app/uploads` (USE_LOCAL_STORAGE=true)
- **Prod:** AWS S3 или Supabase Storage

---

## 14. CI/CD

### 14.1 GitHub Actions

**На каждый push/PR:**
- Backend: `ruff check`, `ruff format --check`, `mypy`, `pytest`
- Frontend: `npm run lint`, `tsc --noEmit`

**На push в main:**
- Build Docker images
- Deploy (Vercel для frontend, Railway/Render для backend)

### 14.2 Линтинг

```toml
# backend/pyproject.toml
[tool.ruff]
line-length = 120
target-version = "py312"

[tool.ruff.lint]
select = ["E", "F", "I", "N", "W", "UP", "B", "SIM"]
```

---

## 15. Roadmap по фазам

### Фаза 1: Фундамент (Недели 1–3)

- Скелет проекта + Docker Compose
- Конфигурация core (БД, Redis, S3, логгер)
- Google OAuth2 + JWT
- Middleware + DI
- API загрузки транскрипта + Celery парсинг
- Frontend: Login → OAuth callback → Onboarding wizard → Profile
- CI/CD

### Фаза 2: Courses + Dashboard (Недели 4–6)

- CRUD курсов текущего семестра
- Загрузка силлабуса + AI-парсинг дедлайнов
- Ручное управление дедлайнами
- Календарь с цветовой кодировкой
- Dashboard: метрики, графики, AI summary
- Course audit

### Фаза 3: Course Catalog (Недели 7–9)

- Каталог курсов с поиском и фильтрами
- Статистика: avg GPA, enrolled count, grade distribution
- Группировка по профессорам
- Система отзывов и рейтингов (1–10 по критериям)
- Модерация

### Фаза 4: AI Study Assistant (Недели 10–13)

- Загрузка и индексация учебных материалов (RAG)
- Генерация мок-экзаменов (персонализация по слабым сторонам)
- Проверка ответов (auto + LLM)
- Детальные репорты + рекомендации
- Флеш-карты с SM-2 spaced repetition

### Фаза 5: Интеграции и деплой (Недели 14–16)

- Email-уведомления (Gmail API)
- E2E тестирование
- Оптимизация производительности
- Production deploy
- Бета-тестирование со студентами НУ

---

## Appendix A: Конвенции

### Naming

- **Python:** snake_case для переменных/функций, PascalCase для классов
- **TypeScript:** camelCase для переменных/функций, PascalCase для компонентов/типов
- **Database:** snake_case для таблиц и колонок
- **API:** kebab-case не используется, snake_case в JSON body
- **Endpoints:** lowercase, множественное число (`/users`, `/courses`, `/deadlines`)

### Commits

```
feat: add mock exam generation endpoint
fix: correct GPA calculation for withdrawn courses
refactor: extract PDF parsing into separate service
docs: update API endpoint table
test: add auth service unit tests
chore: update dependencies
```

### Branching

```
main        — production-ready код
develop     — интеграционная ветка
feat/xxx    — новые фичи
fix/xxx     — баг-фиксы
```

### PR Process

1. Создать ветку от `develop`
2. Написать код + тесты
3. Убедиться что CI проходит
4. Создать PR с описанием изменений
5. Code review (минимум 1 approve)
6. Squash merge в `develop`