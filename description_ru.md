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


# Чтобы убедиться, что Supabase-база «жива» и API отвечает, есть два основных пути.

────────────────────────────────────────
1. Через HTTP-эндпоинт сервера
────────────────────────────────────────
Запустите backend ( `uvicorn app.main:app --reload` ) и сделайте запрос:

```bash
curl http://localhost:8000/api/v1/health
```

• Если Supabase доступен, придёт JSON:

```json
{
  "status": "healthy",
  "timestamp": "2024-03-16T12:34:56.123Z",
  "version": "1.0.0"
}
```

• Если нет, сервис вернёт HTTP 503 и detail
  “Service unavailable – database connection failed”.

Таким образом можно проверять из CI/CD или со стороны k8s liveness probe.

────────────────────────────────────────
2. Непосредственно из Python-кода
────────────────────────────────────────
```python
import os
from app.services.supabase_client import supabase_client

# убедитесь, что заданы переменные окружения
# SUPABASE_URL, SUPABASE_ANON_KEY   (и при вставке – SUPABASE_SERVICE_KEY)

ok = supabase_client.health_check()
print("Supabase доступен" if ok else "Supabase недоступен")
```

Функция `health_check()` делает очень лёгкий `GET /rest/v1/sales_data?limit=1` и возвращает `True/False`.

Полезно, когда нужно добавить собственный мониторинг, pytest или скрипт запуска.

────────────────────────────────────────
3. Что нужно, чтобы проверка прошла
────────────────────────────────────────
1. Переменные окружения:
   • `SUPABASE_URL=https://xxx.supabase.co` (без закрывающего `/`)
   • `SUPABASE_ANON_KEY=…` (для чтения)
   • `SUPABASE_SERVICE_KEY=…` (нужен только для insert/updates)

2. Порт 443 (https) из вашей сети до Supabase не должен блокироваться.

3. Если запускаете тесты и настоящей базы нет, задайте
   `ENVIRONMENT=test` или `SUPABASE_URL=dummy_url` → клиент перейдёт в «mock-режим» и `health_check()` всегда вернёт `True`.

────────────────────────────────────────
Итого
• Быстрее всего — дернуть `GET /api/v1/health`.
• Для автоматизации внутри Python — вызывать `supabase_client.health_check()`.

───────────────── Шаг 1 — увидеть реальный код ответа
```bash
<code_block_to_apply_changes_from>
```
• 200 / 206 → всё ок (тогда вопрос в RLS-политике);
• 404 Not Found → таблицы `sales_data` нет;
• 401 Unauthorized → ключ неправильный / “anon” не может читать;
• timeout / 5xx → проблема сети или Supabase лежит.

───────────────── Шаг 2 — устраняем по коду

1. 404 Not Found
   • Создайте таблицу и включите RLS:
   ```sql
   create table if not exists sales_data (
     id serial primary key,
     sku_id text,
     date date,
     sales_quantity int,
     avg_temp float,
     created_at timestamp default now()
   );
   alter table sales_data enable row level security;
   ```
   • Добавьте политику чтения:
   ```sql
   create policy "Anon read" on sales_data
     for select using (true);
   ```

2. 401 Unauthorized
   • Убедитесь, что в переменной окружения именно `anon`-key (а не `service_key`).
   • Проверьте, что RLS-политика «Anon read» создана (см. выше).

3. 5xx / timeout
   • Проверьте, что компьютер или контейнер имеет выход на `*.supabase.co:443`.
   • Попробуйте `curl https://google.com` — исключим проблемы c SSL/прокси.
   • Зайдите в консоль Supabase → «Settings ▸ Infrastructure ▸ Outages» — убедитесь, что проект работает.

4. Всё работает, но Health всё-равно 503
   • Можно смягчить проверку, допустив 404 как «здорово»
     (сделайте после того, как удостоверьтесь, что 404 — это только “таблица пуста”, а не ошибка).
   ```python
   # app/services/supabase_client.py  (метод health_check)
   return response.status_code in (200, 206, 404)
   ```

───────────────── Шаг 3 — перезапуск
После изменения переменных окружения и/или политики:
```bash
# если запускаете локально
uvicorn app.main:app --reload
# или просто дождитесь автоматического redeploy (Docker/K8s)
```
и снова:
```bash
curl http://localhost:8000/api/v1/health
```
Должен прийти JSON со статусом `"healthy"`.

───────────────── Временный обход
Пока настраиваете Supabase, запустите backend в mock-режиме:
```bash
export ENVIRONMENT=test
uvicorn app.main:app --reload
```
`health` вернёт 200, а все операции с БД будут работать с заглушками.

────────────────────────────────────────
1 . Проверяем конкретный HTTP-ответ
────────────────────────────────────────
```bash
<code_block_to_apply_changes_from>
```

• Запомните статус-код и тело:
  – 200 / 206 → БД отвечает (значит, дело в RLS-политике или имени таблицы).
  – 404 Not Found → таблицы `sales_data` нет или путь неправильный.
  – 401 Unauthorized → ключ неправильный или не даёт прав на SELECT.
  – 5xx / timeout → сеть или сам сервис Supabase недоступен.

Если хотите проверить историю прогнозов, проделайте то же c `/forecasts?limit=1`.

────────────────────────────────────────
2 . Что делать по результату
────────────────────────────────────────
• 404 ⇒ создаём таблицу «sales_data» и «forecasts» (см. ниже SQL)
  либо исправляем путь в curl и в коде (`sales_data` ↔ реальное имя таблицы).

• 401 ⇒ удостоверяемся, что используете именно `anon`-ключ
  (`Role = anon` на вкладке Project Settings → API)
  и что для таблиц включены RLS-политики, разрешающие чтение:

```sql
-- однажды в SQL-editor Supabase
alter table sales_data enable row level security;

create policy "Anon read" on sales_data
  for select using (true);
```
  (аналогично для `forecasts`, если нужна запись → ещё политика INSERT).

• 5xx / timeout ⇒
  – проверяем интернет до `*.supabase.co:443` (`curl https://google.com`).
  – смотрим статус проекта на Supabase → Settings ▸ Infrastructure ▸ Outages.
  – если за прокси / корпоративным фаерволом — открываем исходящий HTTPS.

────────────────────────────────────────
3 . Пример SQL для двух таблиц
────────────────────────────────────────
```sql
-- sales_data
create table if not exists sales_data (
  id serial primary key,
  sku_id text,
  date date,
  sales_quantity int,
  avg_temp float,
  created_at timestamp default now()
);
alter table sales_data enable row level security;
create policy "Anon read" on sales_data for select using (true);
create policy "Anon insert" on sales_data for insert with check (true);

-- forecasts
create table if not exists forecasts (
  id serial primary key,
  sku_id text,
  forecast_date date,
  predicted_sales int,
  confidence_score float,
  key_factors jsonb,
  created_at timestamp default now()
);
alter table forecasts enable row level security;
create policy "Anon read"   on forecasts for select using (true);
create policy "Anon insert" on forecasts for insert with check (true);
```

────────────────────────────────────────
4 . Повторный тест
────────────────────────────────────────
1. Выполните нужные SQL в Supabase-консоли.
2. Перезапустите backend (или дождитесь hot-reload).
3. Снова `curl http://localhost:8000/api/v1/health` – должно стать `{"status":"healthy",…}`.

────────────────────────────────────────
5 . Если всё равно не ясно, соберите данные
────────────────────────────────────────
Пришлите:

• Вывод команды из пункта 1 (`curl -v …`).
• Логи сервера FastAPI (они уже показывают «health check failed», но
  важно увидеть, какой именно код возвращает Supabase).

С этой информацией можно будет указать точную причину.
