# Руководство по развертыванию Habarovsk Forecast Buddy API

## 🚀 Готовый к деплою проект

Ваш полноценный Python-бэкенд готов к развертыванию! Проект включает:

- ✅ FastAPI приложение с полным набором эндпоинтов
- ✅ Интеграция с Supabase PostgreSQL
- ✅ Интеграция с GigaChat (mock режим по умолчанию)
- ✅ Валидация и обработка CSV файлов
- ✅ Автоматическое тестирование
- ✅ Docker контейнеризация
- ✅ GitHub Actions CI/CD пайплайн
- ✅ Готовность к деплою на Render

## 📋 Предварительные настройки

### 1. Настройка базы данных Supabase

Выполните SQL скрипт из файла `setup_database.sql` в Supabase SQL Editor:

```sql
-- Скопируйте и выполните весь контент из setup_database.sql
```

### 2. Настройка переменных окружения

Ваш `.env` файл уже содержит:
```bash
SUPABASE_URL=https://nklzooanyyctoqowgimb.supabase.co
SUPABASE_SERVICE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
GIGACHAT_CREDENTIALS=  # оставьте пустым для mock режима
ENVIRONMENT=development
```

## 🔧 Локальная разработка

### Запуск приложения

```bash
# Активация виртуальной среды
source venv/bin/activate

# Запуск сервера разработки
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Приложение будет доступно по адресу:
- API: http://localhost:8000
- Документация: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### Запуск тестов

```bash
# Все тесты
ENVIRONMENT=test python -m pytest tests/ -v

# Только health check
ENVIRONMENT=test python -m pytest tests/test_health.py -v
```

### Docker

```bash
# Сборка образа
docker build -t habarovsk-forecast-buddy .

# Запуск контейнера
docker run -p 8000:8000 \
  -e SUPABASE_URL=your-url \
  -e SUPABASE_SERVICE_KEY=your-key \
  habarovsk-forecast-buddy
```

## 🌐 Развертывание на Render

### 1. Создание нового Web Service

1. Войдите в [Render Dashboard](https://dashboard.render.com/)
2. Нажмите "New" → "Web Service"
3. Подключите ваш GitHub репозиторий

### 2. Конфигурация Render

**Build Command:**
```bash
pip install -r requirements.txt
```

**Start Command:**
```bash
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

**Environment Variables:**
```
SUPABASE_URL=https://nklzooanyyctoqowgimb.supabase.co
SUPABASE_SERVICE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
GIGACHAT_CREDENTIALS=  # добавьте реальные учетные данные при необходимости
ENVIRONMENT=production
```

### 3. Автоматический деплой (опционально)

Для настройки автоматического деплоя через GitHub Actions:

1. Получите API ключ в Render Dashboard → Account Settings → API Keys
2. Найдите Service ID в настройках вашего сервиса
3. Добавьте GitHub Secrets в репозитории:
   - `RENDER_API_KEY`: ваш API ключ
   - `RENDER_SERVICE_ID`: ID сервиса

После этого каждый push в ветку `main` будет автоматически деплоить обновления.

## 📊 API Эндпоинты

### Основные эндпоинты

| Метод | Путь | Описание |
|-------|------|----------|
| GET | `/` | Информация о API |
| GET | `/api/v1/health` | Проверка состояния |
| GET | `/api/v1/sample-csv` | Скачать пример CSV |
| POST | `/api/v1/upload-csv` | Загрузить данные о продажах |
| POST | `/api/v1/forecast` | Сгенерировать прогноз |
| GET | `/api/v1/data/{sku_id}` | Получить данные о продажах |
| GET | `/api/v1/forecast-history/{sku_id}` | История прогнозов |

### Примеры использования

**Загрузка CSV:**
```bash
curl -X POST "https://your-app.onrender.com/api/v1/upload-csv" \
  -F "file=@sales_data.csv"
```

**Генерация прогноза:**
```bash
curl -X POST "https://your-app.onrender.com/api/v1/forecast" \
  -H "Content-Type: application/json" \
  -d '{
    "sku_id": "DOWN_JACKET_001",
    "period": "7",
    "context": "Ожидается холодная погода"
  }'
```

## 🔍 Мониторинг и отладка

### Логи

Приложение использует структурированное логирование. В production режиме логи доступны в Render Dashboard.

### Проверка состояния

```bash
curl https://your-app.onrender.com/api/v1/health
```

### Документация API

Интерактивная документация доступна по адресу:
`https://your-app.onrender.com/docs`

## 🛠 Устранение неполадок

### Проблемы с базой данных

1. Убедитесь, что выполнили SQL скрипт в Supabase
2. Проверьте правильность SUPABASE_URL и SUPABASE_SERVICE_KEY
3. Убедитесь, что IP адрес Render добавлен в разрешенные в Supabase (если включен RLS)

### Проблемы с GigaChat

1. Если не указаны учетные данные, приложение работает в mock режиме
2. Для реальной интеграции добавьте `GIGACHAT_CREDENTIALS` в переменные окружения

### Проблемы с деплоем

1. Проверьте логи сборки в Render Dashboard
2. Убедитесь, что все переменные окружения установлены правильно
3. Проверьте, что start command указан корректно

## 📈 Следующие шаги

### Рекомендуемые улучшения:

1. **Авторизация**: Добавить JWT авторизацию через Supabase Auth
2. **Кеширование**: Интегрировать Redis для кеширования прогнозов
3. **Мониторинг**: Добавить интеграцию с сервисами мониторинга
4. **Rate Limiting**: Ограничить количество запросов на IP
5. **Backup**: Настроить автоматическое резервное копирование БД

### Готовые возможности:

- ✅ Полноценный REST API
- ✅ Автоматическая валидация данных
- ✅ Обработка ошибок
- ✅ Документация API
- ✅ Контейнеризация
- ✅ CI/CD пайплайн
- ✅ Готовность к production

## 🎉 Поздравляем!

Ваш проект полностью готов к использованию и развертыванию. Все основные компоненты реализованы и протестированы!
