# 🏔️ Khabarovsk Forecast Buddy - Development Setup

**Полное руководство по настройке локальной среды разработки**

## 📋 Краткий старт

**Одной командой:**
```bash
./start-dev.sh
```

Эта команда автоматически:
- ✅ Проверит все зависимости
- ✅ Запустит backend (FastAPI) на порту 8000
- ✅ Запустит frontend (React) на порту 8080
- ✅ Покажет полезные ссылки и логи

## 🛠️ Детальная настройка

### 1. Системные требования

#### Обязательные компоненты:
- **Python 3.11+**
- **Node.js 18+** и npm
- **Git**

#### Опциональные:
- **GigaChat API credentials** (иначе mock режим)
- **Supabase account** (иначе без базы данных)

### 2. Структура проекта

Убедитесь, что оба репозитория находятся в одной папке:

```
your-projects/
├── khabarovsk-server-dbase/     # Backend (FastAPI)
└── habarovsk-forecast-buddy/    # Frontend (React)
```

### 3. Клонирование репозиториев

```bash
# Создаем рабочую директорию
mkdir khabarovsk-forecast-project
cd khabarovsk-forecast-project

# Клонируем backend
git clone https://github.com/AbayReushenov/khabarovsk-server-dbase.git
cd khabarovsk-server-dbase

# Клонируем frontend (в соседнюю папку)
cd ..
git clone https://github.com/AbayReushenov/habarovsk-forecast-buddy.git
```

### 4. Настройка Backend

```bash
cd khabarovsk-server-dbase

# Создаем виртуальное окружение
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

# Устанавливаем зависимости
pip install -r requirements.txt

# Копируем конфигурацию
cp .env.example .env
# Редактируем .env файл своими настройками
```

### 5. Настройка Frontend

```bash
cd ../habarovsk-forecast-buddy

# Устанавливаем зависимости
npm install

# Создаем .env файл (если нужно)
# Обычно frontend работает без дополнительной настройки
```

## ⚙️ Конфигурация .env

### Базовая конфигурация (минимум для работы):

```bash
# В khabarovsk-server-dbase/.env
ENVIRONMENT=development

# Остальные настройки можно оставить пустыми для mock режима
GIGACHAT_CREDENTIALS=
SUPABASE_URL=
SUPABASE_ANON_KEY=
SUPABASE_SERVICE_KEY=
```

### Полная конфигурация с реальными сервисами:

#### GigaChat API:

1. Регистрируемся на [developers.sber.ru](https://developers.sber.ru/portal/products/gigachat-api)
2. Получаем Client ID и Client Secret
3. Генерируем auth key:

```bash
echo -n "YOUR_CLIENT_ID:YOUR_CLIENT_SECRET" | base64
```

4. Заполняем в .env:

```bash
GIGACHAT_CLIENT_ID=your_client_id
GIGACHAT_CLIENT_SECRET=your_client_secret
GIGACHAT_CLIENT_AUTH_KEY=generated_base64_key
GIGACHAT_SCOPE=GIGACHAT_API_PERS
```

#### Supabase Database:

**📖 Подробная инструкция**: [SUPABASE_SETUP.md](SUPABASE_SETUP.md)

**Краткий процесс**:
1. Создаем проект на [supabase.com](https://supabase.com)
2. Выполняем SQL скрипт `supabase_schema.sql` в SQL Editor
3. Копируем данные из Settings → API
4. Заполняем в .env:

```bash
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your_anon_key
SUPABASE_SERVICE_KEY=your_service_key
```

**Тестирование**:
```bash
python test_database.py
```

## 🚀 Запуск разработки

### Автоматический запуск (рекомендуется):

```bash
cd khabarovsk-server-dbase
./start-dev.sh
```

**Результат:**
```
🎉 Development environment is ready!
=================================================
📱 Frontend:    http://localhost:8080
⚙️  Backend:     http://localhost:8000
📚 API Docs:    http://localhost:8000/docs
💾 Health:      http://localhost:8000/api/v1/health
=================================================
```

### Ручной запуск:

#### Backend:
```bash
cd khabarovsk-server-dbase
source venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### Frontend (в отдельном терминале):
```bash
cd habarovsk-forecast-buddy
npm run dev -- --host 0.0.0.0 --port 8080
```

## 🔧 Полезные команды

### Backend команды:

```bash
# Запуск сервера
uvicorn app.main:app --reload

# Тестирование
pytest

# Форматирование кода
black app/

# Линтинг
flake8 app/

# Проверка типов
mypy app/
```

### Frontend команды:

```bash
# Запуск dev сервера
npm run dev

# Сборка для продакшена
npm run build

# Предварительный просмотр сборки
npm run preview

# Линтинг
npm run lint

# Тестирование
npm run test
```

## 🧪 Тестирование API

### Проверка работоспособности:

```bash
# Health check
curl http://localhost:8000/api/v1/health

# Тест прогноза
curl -X POST "http://localhost:8000/api/v1/forecast" \
  -H "Content-Type: application/json" \
  -d '{
    "sku_id": "DOWN_JACKET_001",
    "period": "7",
    "context": "Test forecast"
  }'

# Скачать sample CSV
curl http://localhost:8000/api/v1/sample-csv -o sample.csv
```

### Swagger UI:
Откройте http://localhost:8000/docs для интерактивного тестирования API.

## 📁 Структура файлов

### Backend (khabarovsk-server-dbase):
```
├── app/
│   ├── api/           # API endpoints
│   ├── models/        # Pydantic schemas
│   ├── services/      # Business logic
│   └── utils/         # Utilities
├── tests/             # Tests
├── mok-data/          # Mock CSV data
├── start-dev.sh       # Dev startup script
├── .env.example       # Environment template
└── requirements.txt   # Python dependencies
```

### Frontend (habarovsk-forecast-buddy):
```
├── src/
│   ├── components/    # UI components
│   ├── hooks/         # Custom React hooks
│   ├── lib/           # Utilities & API client
│   └── pages/         # Page components
├── public/            # Static assets
└── package.json       # Node dependencies
```

## 🔍 Отладка

### Логи разработки:

При использовании `start-dev.sh`:
- **Backend логи**: `backend.log`
- **Frontend логи**: `frontend.log`

### Распространенные проблемы:

#### "Port already in use":
```bash
# Найти процесс
lsof -i :8000  # или :8080

# Убить процесс
kill -9 PID
```

#### "Module not found":
```bash
# Backend
pip install -r requirements.txt

# Frontend
npm install
```

#### "GigaChat authentication failed":
- Проверьте credentials в .env
- Попробуйте сгенерировать auth key заново
- Используйте mock режим (пустые credentials)

#### "Database connection failed":
- Проверьте Supabase настройки
- Система работает без базы в dev режиме

## 🔄 Автоматическая перезагрузка

- **Backend**: FastAPI автоматически перезагружается при изменении Python файлов
- **Frontend**: Vite автоматически обновляет браузер при изменении React компонентов

## 🎨 VS Code настройка

Рекомендуемые расширения:

```json
{
  "recommendations": [
    "ms-python.python",
    "ms-python.black-formatter",
    "bradlc.vscode-tailwindcss",
    "esbenp.prettier-vscode",
    "ms-vscode.vscode-typescript-next"
  ]
}
```

Создайте `.vscode/settings.json`:

```json
{
  "python.defaultInterpreterPath": "./venv/bin/python",
  "python.formatting.provider": "black",
  "editor.formatOnSave": true,
  "typescript.preferences.includePackageJsonAutoImports": "auto"
}
```

## 📚 Дополнительные ресурсы

- **Backend документация**: [FastAPI docs](https://fastapi.tiangolo.com)
- **Frontend документация**: [React docs](https://react.dev)
- **GigaChat API**: [developers.sber.ru](https://developers.sber.ru/portal/products/gigachat-api)
- **Supabase**: [supabase.com/docs](https://supabase.com/docs)

## 🆘 Получение помощи

- **Backend Issues**: [khabarovsk-server-dbase/issues](https://github.com/AbayReushenov/khabarovsk-server-dbase/issues)
- **Frontend Issues**: [habarovsk-forecast-buddy/issues](https://github.com/AbayReushenov/habarovsk-forecast-buddy/issues)

---

**Happy coding! 🚀**

*Khabarovsk Forecast Buddy Development Team*
