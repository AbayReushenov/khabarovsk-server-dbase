# Cursor AI Pro Prompt: Backend Generation (Step 2)

Ниже приведён готовый промпт в формате Markdown для запуска генератора кода в **Cursor AI Pro**.
Он создаёт полноценный Python-бэкенд (FastAPI + Supabase Postgres + GigaChat) и сразу подготавливает проект к деплою на Render. Текст можно вставить «как есть» в окно задания Cursor AI Pro.

## 📄 Prompt

```markdown
### Задание

Сгенерируй рабочий backend-репозиторий на Python 3.11 c архитектурой FastAPI → Supabase (PostgreSQL) → GigaChat. Проект предназначен для MVP-приложения «Habarovsk Forecast Buddy» (прогнозирование продаж пуховиков).

**Требования верхнего уровня**

1. **Стек**
   - FastAPI 1.0+
   - Pydantic 2.x
   - pandas 2.x
   - psycopg2-binary
   - python-multipart
   - gigachat (официальный SDK)
   - dotenv
2. **Структура каталогов**

```
project/
├── app/
│   ├── __init__.py
│   ├── main.py                # точка входа FastAPI
│   ├── api/
│   │   ├── __init__.py
│   │   └── endpoints.py       # upload_csv, forecast, health, data, history
│   ├── models/
│   │   ├── __init__.py
│   │   └── schemas.py         # Pydantic models
│   ├── services/
│   │   ├── __init__.py
│   │   ├── supabase_client.py # подключение к Supabase
│   │   ├── gigachat_service.py
│   │   ├── csv_service.py     # валидация/парсинг CSV
│   │   └── forecast_service.py
│   └── utils/
│       └── logger.py
├── tests/
│   └── test_health.py
├── requirements.txt
├── .env.example
├── Dockerfile
└── README.md
```

3. **Функциональность**
   - POST `/upload-csv` — загрузка CSV, сохранение в таблицу `sales_data`
   - POST `/forecast` — генерация прогноза (7 | 14 | 30 дней) через GigaChat, запись в `forecasts`
   - GET  `/data/{sku_id}` — выборка последних 52 записей
   - GET  `/forecast-history/{sku_id}` — история прогнозов
   - GET  `/health` — ping для Render health check

4. **Supabase**
   - Использовать переменные `SUPABASE_URL`, `SUPABASE_SERVICE_KEY`
   - Подключаться через psycopg2, а не через JS SDK
   - Таблицы уже созданы (sales_data, forecasts, user_inputs) — описать ORM-like helpers

5. **GigaChat**
   - Переменная `GIGACHAT_CREDENTIALS`
   - Класс `GigaChatService.generate_forecast()` строит prompt по шаблону few-shot, отдает JSON
   - Обработка таймаутов и ошибок SDK

6. **Безопасность / RLS**
   - Запросы к Supabase выполняются единственным service-key; проверка лимитов и SQL-инъекций не требуется (MVP)

7. **Docker**
   - Базовый образ `python:3.11-slim`
   - Команда запуска:
     `uvicorn app.main:app --host 0.0.0.0 --port 8000`
   - Expose 8000

8. **GitHub Actions**
   - Workflow `deploy.yml` для автодеплоя в Render
     *тесты → docker build → push*

9. **README.md**
   - Инструкции локального запуска, переменные env, пример curl-запросов

10. **Code style**
    - Docstrings Google-style
    - Логирование через стандартный `logging` в `utils/logger.py`

### Выход Cursor AI Pro

1. Полный набор файлов в одной виртуальной рабочей директории
2. Содержимое `requirements.txt`, `Dockerfile`, `.env.example`
3. Минимальные unit-тесты (`tests/test_health.py` → ожидает 200 OK)

**Не включай реальные ключи.** Для чувствительных данных ставь заглушки `""`.
Код должен успешно `docker build` и проходить `pytest` без ошибок.
```

## Что уже учтено

| Блок             | Статус | Комментарий |
|------------------|--------|-------------|
| Структура БД     | ✔      | Таблицы и RLS созданы в шаге 1 |
| API-спецификация | ✔      | В prompt заложены все энд-поинты |
| Логика CSV       | ✔      | `csv_service.py` валидирует и пишет в `sales_data` |
| Интеграция LLM   | ✔      | Класс `GigaChatService` + обработка JSON-ответа |
| Деплой           | ✔      | Dockerfile и GitHub Actions для Render |

## Что можно доработать позже

1. **Авторизация** — добавить Supabase JWT и RLS-политику per-user.
2. **Кеширование прогнозов** — Redis Cloud Free (30 MB).
3. **Мониторинг** — Render Metrics + Evidently AI.
4. **Rate Limiting** — fastapi-limiter на Redis.

> Скопируйте prompt в окно Cursor AI Pro, дождитесь генерации репозитория и затем подключите GitHub → Render для автоматического деплоя.
