Read file: app/main.py

Read file: app/api/endpoints.py

Read file: app/models/schemas.py

Read file: app/services/csv_service.py

Read file: app/services/forecast_service.py

Read file: app/services/gigachat_service.py

Read file: app/services/supabase_client.py

Read file: app/utils/logger.py

Эта репозиторий — сервер-ная часть проекта «Habarovsk Forecast Buddy».
Кратко: это REST API, которое помогает магазину прогнозировать продажи пуховиков в Хабаровске, хранит историю прогнозов и позволяет загружать/просматривать реальные продажи. Ниже по компонентам.

1. Точка входа (`app/main.py`)
   • Создаёт приложение FastAPI, подключает CORS, логирование, обработчики ошибок.
   • При старте проверяет соединение с базой (Supabase) и готовность сервиса GigaChat.
   • Экспортирует объект `app`, поэтому сервер запускается командой
     `uvicorn app.main:app`.

2. API-роуты (`app/api/endpoints.py`)
   URL-префикс: `/api/v1`
   • `GET /health` — проверка живости сервиса и БД.
   • `POST /upload-csv` — загрузка CSV с историей продаж; файл разбирается, очищается и данные пишутся в БД.
   • `POST /forecast` — получить прогноз продаж по SKU на 7/14/30 дней.
   • `GET /data/{sku_id}` — отдать исторические продажи SKU.
   • `GET /forecast-history/{sku_id}` — история прогнозов.
   • `GET /sku-list` — список всех SKU, присутствующих в таблице продаж.
   • `GET /sample-csv` — скачать шаблон CSV.

3. Сервисы
   • `csv_service.py` — валидирует и парсит CSV:
     – распознаёт названия столбцов (sku_id, date, sales_quantity и опционально avg_temp/season);
     – поддерживает разные разделители, кодировки и форматы дат;
     – возвращает структуры `SalesDataRow` + список найденных ошибок.

   • `supabase_client.py` — тонкий клиент к Supabase REST API: вставка и выборка продаж и прогнозов. При переменной `ENVIRONMENT=test` работает в «мок-режиме», что упрощает юнит-тесты.

   • `gigachat_service.py` — интеграция с внешним ИИ «GigaChat» от Сбера.
     – Формирует русскоязычный промпт с выжимкой по историческим данным.
     – Получает OAuth-токен или работает в `mock_mode`, если ключей нет.
     – При ответе парсит JSON с полями `predictions`, `explanation`, `confidence_scores`.
     – В mock-режиме генерирует правдоподобные тестовые данные.

   • `forecast_service.py` — «дирижёр» прогноза.
     1. Берёт историю продаж из Supabase.
     2. Запрашивает GigaChat (или mock).
     3. Конвертирует ответ в Pydantic-модель `ForecastResponse`, считает суммы/среднее доверие.
     4. Сохраняет прогноз в таблицу `forecasts`.
     5. При сбое возвращает простой fallback-прогноз.

4. Схемы (`app/models/schemas.py`)
   Набор Pydantic-моделей: валидация входов/выходов, типы перечислений, структуры прогнозов и ошибок.

5. Логика работы в тестах (`tests/…`)
   • Запускается в полностью моковом окружении: Supabase и GigaChat заменяются на stub-режимы, чтобы проверять логику API без внешних сервисов.

6. Инфраструктура
   • `Dockerfile`, скрипты запуска, SQL-дампы схемы, Markdown-инструкции по развёртыванию, настройке Supabase и GigaChat.
   • `requirements.txt` фиксирует зависимости (FastAPI, requests, pandas, python-dotenv и др.).

Итого: приложение предоставляет удобный HTTP-интерфейс для:

• загрузки реальных продаж (CSV) → хранится в Supabase;
• генерации AI-прогноза на 7/14/30 дней через GigaChat (с fallback);
• получения продаж, прогнозов и справочной информации;
• мониторинга здоровья сервиса.
