<div align="center">

  # ⛽ FuelWatch — Мониторинг цен на топливо

  <p align="center">
    <strong>Сервис для отслеживания и анализа цен на АЗС</strong>
  </p>

  <p align="center">
    <img src="https://img.shields.io/badge/Python-3.12-blue?logo=python" alt="Python 3.12"/>
    <img src="https://img.shields.io/badge/FastAPI-0.115-009688?logo=fastapi" alt="FastAPI"/>
    <img src="https://img.shields.io/badge/PostgreSQL-16-4169E1?logo=postgresql" alt="PostgreSQL"/>
    <img src="https://img.shields.io/badge/Redis-7-DC382D?logo=redis" alt="Redis"/>
    <img src="https://img.shields.io/badge/Celery-5.4-37814A?logo=celery" alt="Celery"/>
    <img src="https://img.shields.io/badge/Docker-✓-2496ED?logo=docker" alt="Docker"/>
    <img src="https://img.shields.io/badge/License-MIT-green" alt="License MIT"/>
  </p>

  <h4>
    <a href="#-архитектура">Архитектура</a>
    <span> · </span>
    <a href="#-быстрый-старт">Быстрый старт</a>
    <span> · </span>
    <a href="#-api-endpoints">API</a>
    <span> · </span>
    <a href="#-фоновые-задачи">Фоновые задачи</a>
    <span> · </span>
    <a href="#-стэк-технологий">Стэк</a>
    <span> · </span>
    <a href="#-roadmap">Roadmap</a>
  </h4>

</div>

---

## 📋 О проекте

**FuelWatch** — это backend-сервис, который автоматически парсит цены на топливо с сайтов крупных сетей АЗС (Лукойл, Газпромнефть, Роснефть, Shell, Татнефть) и позволяет пользователям:

- 📍 **Искать АЗС** по городу, бренду, региону
- 💰 **Смотреть актуальные цены** на все виды топлива
- 📈 **Отслеживать историю** изменения цен
- 🔔 **Создавать алерты** — «уведоми меня, когда 95-й бензин будет ≤ 55 ₽»
- ✍️ **Сообщать цены** самостоятельно (crowdsourcing)
- 🤖 **Получать уведомления** через Telegram (в разработке)

> **Статус:** MVP (Minimum Viable Product). Проект активно развивается.

---

## 🏗 Архитектура

```
┌──────────────────────────────────────────────────────────────────┐
│                        Docker Compose                           │
│                                                                  │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │                    FastAPI (app)                            │ │
│  │  ┌─────────────┐  ┌──────────────┐  ┌─────────────────┐   │ │
│  │  │  API Routes  │→ │  Services    │→ │  SQLAlchemy ORM │   │ │
│  │  │  (REST)      │  │  (Бизнес-    │  │  (Модели БД)    │   │ │
│  │  │              │  │   логика)    │  │                 │   │ │
│  │  └─────────────┘  └──────────────┘  └────────┬────────┘   │ │
│  │                                               │            │ │
│  │  ┌────────────────────────────────────────────┘            │ │
│  │  │                                                        │ │
│  │  ▼                                                        │ │
│  │  ┌──────────────────────────────────────────────────┐     │ │
│  │  │            PostgreSQL 16                          │     │ │
│  │  │  gas_stations │ fuel_types │ station_fuel_prices  │     │ │
│  │  │  users        │ price_alerts                      │     │ │
│  │  └──────────────────────────────────────────────────┘     │ │
│  └─────────────────────────────────────────────────────────────┘ │
│                                                                  │
│  ┌──────────────┐   ┌──────────────┐   ┌─────────────────────┐  │
│  │  Celery Beat │   │ Celery Worker│   │  Flower (мониторинг) │  │
│  │  (расписание)│   │ (парсинг +   │   │  http://localhost:5555│  │
│  │  каждые 4ч   │   │  алерты)     │   │                     │  │
│  └──────┬───────┘   └──────┬───────┘   └─────────────────────┘  │
│         │                  │                                     │
│         └────────┬─────────┘                                     │
│                  ▼                                               │
│         ┌────────────────┐                                       │
│         │  Redis 7       │  (брокер сообщений для Celery)        │
│         └────────────────┘                                       │
└──────────────────────────────────────────────────────────────────┘
```

### Слои приложения

```
backend/
├── app/
│   ├── api/           # REST endpoints (controllers)
│   │   ├── auth.py    # Регистрация, логин, JWT
│   │   ├── stations.py # АЗС: CRUD, поиск, фильтры
│   │   ├── prices.py   # Цены: история, репорт от пользователей
│   │   └── alerts.py   # Алерты: создание, просмотр, удаление
│   ├── models/        # SQLAlchemy ORM-модели (слой данных)
│   │   ├── station.py # GasStation, FuelType, StationFuelPrice
│   │   ├── user.py    # User
│   │   └── alert.py   # PriceAlert
│   ├── schemas/       # Pydantic схемы (DTO — валидация ввода/вывода)
│   │   ├── station.py
│   │   ├── user.py
│   │   └── alert.py
│   ├── services/      # Бизнес-логика
│   │   ├── auth.py    # JWT, bcrypt, регистрация
│   │   └── parser.py  # Парсинг цен с сайтов АЗС
│   ├── tasks/         # Celery — фоновые задачи
│   │   ├── celery_app.py    # Конфигурация Celery + Beat schedule
│   │   ├── parse_prices.py  # Парсинг цен по расписанию
│   │   └── send_alerts.py   # Проверка и отправка уведомлений
│   ├── templates/     # Jinja2 HTML-шаблоны (SSR-фронтенд)
│   ├── static/        # CSS, JS
│   ├── config.py      # Pydantic Settings (env vars)
│   ├── database.py    # AsyncSession, engine
│   ├── main.py        # FastAPI app, lifespan, роуты
│   └── seed_data.py   # Начальное заполнение БД
├── alembic/           # Миграции БД
├── Dockerfile
└── requirements.txt
```

---

## 🚀 Быстрый старт

### 1. Клонируй репозиторий

```bash
git clone https://github.com/albertildarovich/FuelWatch.git
cd FuelWatch
```

### 2. Запусти одной командой

```bash
docker compose up -d
```

### 3. Открой в браузере

| Сервис | URL | Описание |
|---|---|---|
| 🌐 **Веб-интерфейс** | http://localhost:8000 | HTML-страницы (логин, дашборд, АЗС, алерты) |
| 📖 **Swagger UI** | http://localhost:8000/docs | Автоматическая документация API |
| 📊 **Flower (Celery)** | http://localhost:5555 | Мониторинг фоновых задач |

### Demo-данные

При первом запуске автоматически создаются:
- **12 АЗС** (Москва, Санкт-Петербург, Нижний Новгород)
- **5 типов топлива**: АИ-92, АИ-95, АИ-98, ДТ, Газ
- **Начальные цены** со случайными вариациями

---

## 🔌 API Endpoints

### Аутентификация

| Метод | Endpoint | Описание |
|---|---|---|
| `POST` | `/api/auth/register` | Регистрация нового пользователя |
| `POST` | `/api/auth/login` | Вход, получение JWT (access + refresh) |
| `POST` | `/api/auth/refresh` | Обновление access-токена |
| `GET` | `/api/auth/me` | Информация о текущем пользователе |

### АЗС

| Метод | Endpoint | Описание |
|---|---|---|
| `GET` | `/api/stations/` | Список АЗС (фильтры: `city`, `brand`, `region`) |
| `GET` | `/api/stations/fuel-types` | Список типов топлива |
| `GET` | `/api/stations/{id}` | Информация об АЗС с текущими ценами |

### Цены

| Метод | Endpoint | Описание |
|---|---|---|
| `GET` | `/api/prices/` | Текущие цены (фильтры: `city`, `fuel_type_id`, `station_id`) |
| `GET` | `/api/prices/history/{station_id}/{fuel_type_id}` | История изменения цены |
| `POST` | `/api/prices/report` | Сообщить цену (crowdsourcing) |

### Алерты 🔔

| Метод | Endpoint | Описание |
|---|---|---|
| `POST` | `/api/alerts/` | Создать алерт |
| `GET` | `/api/alerts/` | Мои алерты |
| `DELETE` | `/api/alerts/{id}` | Удалить алерт |

> **Пример алерта:** «Уведоми меня в Telegram, когда АИ-95 на Лукойле будет дешевле 55 ₽»

---

## ⏰ Фоновые задачи

| Задача | Расписание | Описание |
|---|---|---|
| `parse_all_stations` | Каждые 4 часа | Парсинг цен на всех активных АЗС |
| `check_and_send_alerts` | Каждые 4 часа (+5 мин) | Проверка алертов и отправка уведомлений |

---

## 🧰 Стэк технологий

| Категория | Технология | Назначение |
|---|---|---|
| **Язык** | ![Python](https://img.shields.io/badge/Python-3.12-3776AB?logo=python) | Основной язык разработки |
| **Веб-фреймворк** | ![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?logo=fastapi) | Асинхронный REST API + Swagger docs |
| **Сервер** | ![Uvicorn](https://img.shields.io/badge/Uvicorn-0.30-000?logo=uvicorn) | ASGI сервер |
| **База данных** | ![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-4169E1?logo=postgresql) | Основное хранилище данных |
| **ORM** | ![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0-D71F00?logo=sqlalchemy) | Асинхронная работа с БД |
| **Миграции** | ![Alembic](https://img.shields.io/badge/Alembic-1.13-000) | Управление схемой БД |
| **Валидация** | ![Pydantic](https://img.shields.io/badge/Pydantic-2.8-E92063?logo=pydantic) | Валидация данных (DTO) |
| **Аутентификация** | ![JWT](https://img.shields.io/badge/JWT-3.3-000?logo=jsonwebtokens) | Access + Refresh токены |
| **Фоновые задачи** | ![Celery](https://img.shields.io/badge/Celery-5.4-37814A?logo=celery) | Очередь задач для парсинга и алертов |
| **Брокер** | ![Redis](https://img.shields.io/badge/Redis-7-DC382D?logo=redis) | Брокер сообщений для Celery |
| **Парсинг** | ![BeautifulSoup](https://img.shields.io/badge/BeautifulSoup-4.12-000) | HTML-парсинг сайтов АЗС |
| **HTTP клиент** | ![httpx](https://img.shields.io/badge/httpx-0.27-000) | Асинхронные HTTP запросы |
| **Шаблоны** | ![Jinja2](https://img.shields.io/badge/Jinja2-3.1-B41717?logo=jinja) | SSR страницы |
| **Мониторинг** | ![Flower](https://img.shields.io/badge/Flower-2.0-000) | Веб-интерфейс для Celery |
| **Контейнеризация** | ![Docker](https://img.shields.io/badge/Docker-✓-2496ED?logo=docker) | Docker Compose (5 сервисов) |
| **Telegram** | ![Aiogram](https://img.shields.io/badge/Aiogram-3.12-0088CC?logo=telegram) | Telegram Bot API (в разработке) |

### Что внутри коробки

| Компонент | Статус |
|---|---|
| ✅ REST API (FastAPI) | Работает |
| ✅ PostgreSQL + SQLAlchemy (async) | Работает |
| ✅ JWT аутентификация (access + refresh) | Работает |
| ✅ Парсинг цен (BeautifulSoup) | Базовый |
| ✅ Celery + Redis | Работает |
| ✅ Docker Compose | Работает |
| ✅ Swagger/OpenAPI docs | Работает |
| ✅ Alembic миграции | Работает |
| ✅ Seed data (12 АЗС, 5 видов топлива) | Работает |
| ✅ HTML-интерфейс (Jinja2) | Работает |
| 🟡 Реальный парсинг с сайтов АЗС | В процессе |
| 🟡 Telegram-бот | Запланирован |
| 🟡 Тесты (pytest) | Запланированы |
| 🟡 Отправка email-уведомлений | Запланирована |

---

## 🗺 Roadmap

### 🔴 Ближайшие задачи

- [ ] Реальный парсинг цен через `FuelPriceParser` (httpx + BeautifulSoup)
- [ ] Юнит-тесты на `AuthService` и API endpoints
- [ ] Логирование вместо `print()` (logging + Sentry)

### 🟡 В разработке

- [ ] Telegram-бот на aiogram 3.x
- [ ] Отправка email через SMTP
- [ ] Rate limiting на API
- [ ] CI/CD (GitHub Actions: тесты + линтер)
- [ ] Docker Compose для разработки (hot-reload)

### 🟢 В планах

- [ ] Кэширование списка АЗС и цен в Redis
- [ ] WebSockets для real-time уведомлений
- [ ] Расширенная seed data (реальные АЗС по РФ)
- [ ] Аналитика: графики изменения цен (Chart.js)
- [ ] Мобильное приложение (React Native)

---

## ⚙️ Конфигурация

Все настройки берутся из переменных окружения (`.env` файл):

```env
# Database
DATABASE_URL=postgresql+asyncpg://fuelwatch:fuelwatch_pass@localhost:5432/fuelwatch

# Redis
REDIS_URL=redis://localhost:6379/0

# JWT
JWT_SECRET_KEY=your-secret-key-here
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7

# Celery
CELERY_BROKER_URL=redis://localhost:6379/1
CELERY_RESULT_BACKEND=redis://localhost:6379/2

# Telegram
TELEGRAM_BOT_TOKEN=

# Parsing
PARSE_INTERVAL_HOURS=4
```

---

## 🧪 Запуск тестов

> Тесты в разработке. Скоро появятся pytest + httpx для интеграционного тестирования.

```bash
# TODO
pytest backend/tests/
```

---

## 🤝 Как помочь проекту

1. Форкни репозиторий
2. Создай ветку (`git checkout -b feature/awesome`)
3. Закоммить изменения (`git commit -m 'Add awesome feature'`)
4. Запушь (`git push origin feature/awesome`)
5. Открой Pull Request

Или просто создай [issue](https://github.com/albertildarovich/FuelWatch/issues) с багом или идеей.

---

## 📄 Лицензия

MIT — делай что хочешь, но упомяни автора.

---

<div align="center">
  <sub>Built with ❤️ by Albert</sub>
  <br>
  <sub>Открыт для предложений и контрибьюций</sub>
</div>
