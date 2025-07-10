# 🛠️ Development Quick Reference

**Быстрые команды для ежедневной разработки**

## 🚀 Запуск проекта

### Полная система (frontend + backend):
```bash
# Linux/Mac
./start-dev.sh

# Windows
start-dev.bat
```

### Только backend:
```bash
# Активировать виртуальное окружение
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

# Запустить сервер
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## 📊 Тестирование API

### Быстрая проверка:
```bash
# Health check
curl http://localhost:8000/api/v1/health

# Тест прогноза
curl -X POST http://localhost:8000/api/v1/forecast \
  -H "Content-Type: application/json" \
  -d '{"sku_id": "DOWN_JACKET_001", "period": "7", "context": "test"}'

# Скачать образец CSV
curl http://localhost:8000/api/v1/sample-csv -o sample.csv
```

### Swagger UI:
http://localhost:8000/docs

## 🔧 Полезные команды

### Зависимости:
```bash
# Установить новую зависимость
pip install package_name
pip freeze > requirements.txt

# Обновить все зависимости
pip install -r requirements.txt --upgrade
```

### Форматирование кода:
```bash
# Установить инструменты (один раз)
pip install black flake8 mypy

# Форматировать код
black app/

# Проверить стиль
flake8 app/

# Проверить типы
mypy app/
```

### Тестирование:
```bash
# Запустить все тесты
pytest

# Запустить с подробным выводом
pytest -v

# Запустить конкретный тест
pytest tests/test_api.py::test_health_endpoint
```

### Логи и отладка:
```bash
# Посмотреть логи при запуске start-dev.sh
tail -f backend.log
tail -f frontend.log

# Проверить запущенные процессы
ps aux | grep uvicorn
ps aux | grep node

# Убить процессы по портам
lsof -ti:8000 | xargs kill -9  # Backend
lsof -ti:8080 | xargs kill -9  # Frontend
```

## 🔄 Git workflow

### Ежедневная работа:
```bash
# Получить изменения
git pull origin main

# Создать ветку для новой фичи
git checkout -b feature/amazing-feature

# Зафиксировать изменения
git add .
git commit -m "✨ Add amazing feature"

# Отправить ветку
git push origin feature/amazing-feature
```

### Перед коммитом:
```bash
# Проверить качество кода
black app/ && flake8 app/ && pytest

# Или кратко
make check  # если есть Makefile
```

## 🗄️ База данных

### Supabase:
```bash
# Проверить подключение (в Python)
python -c "from app.services.supabase_client import get_supabase_client; print(get_supabase_client())"
```

### Локальные данные:
```bash
# Использовать mock данные
ls mok-data/
# sales_data_minimal.csv
# sales_data_mock.csv
# sales_data_proper.csv
```

## 🤖 GigaChat

### Проверка API:
```bash
# Проверить credentials в .env
cat .env | grep GIGACHAT

# Тест подключения (в Python)
python -c "from app.services.gigachat_service import GigaChatService; print(GigaChatService().test_connection())"
```

### Режимы работы:
- **Реальный GigaChat**: Заполнить GIGACHAT_* в .env
- **Mock режим**: Оставить GIGACHAT_* пустыми

## 📱 Frontend интеграция

### Проверка соединения:
```bash
# Из frontend директории
curl http://localhost:8000/api/v1/health

# CORS headers
curl -H "Origin: http://localhost:8080" \
     -H "Access-Control-Request-Method: POST" \
     -H "Access-Control-Request-Headers: Content-Type" \
     -X OPTIONS \
     http://localhost:8000/api/v1/forecast
```

## 📁 Структура файлов

### Основные директории:
```
app/
├── api/endpoints.py      # REST API endpoints
├── models/schemas.py     # Pydantic models
├── services/            # Business logic
│   ├── csv_service.py   # CSV processing
│   ├── forecast_service.py  # Forecasting logic
│   ├── gigachat_service.py  # AI integration
│   └── supabase_client.py   # Database client
└── utils/logger.py      # Logging configuration
```

### Конфигурация:
```
.env                 # Секретные настройки (НЕ коммитить!)
.env.example         # Шаблон настроек
requirements.txt     # Python зависимости
```

### Скрипты:
```
start-dev.sh         # Linux/Mac запуск
start-dev.bat        # Windows запуск
```

## 🔍 Troubleshooting

### Частые проблемы:

**"Port already in use"**:
```bash
# Найти и убить процесс
lsof -i :8000
kill -9 <PID>
```

**"Module not found"**:
```bash
# Переустановить зависимости
pip install -r requirements.txt
```

**"GigaChat connection failed"**:
```bash
# Проверить .env файл
cat .env | grep GIGACHAT
# Использовать mock режим (очистить credentials)
```

**"Frontend can't connect"**:
```bash
# Проверить backend
curl http://localhost:8000/api/v1/health
# Проверить CORS настройки
```

## 📚 Документация

- **Подробная настройка**: [DEV_SETUP.md](DEV_SETUP.md)
- **API документация**: http://localhost:8000/docs
- **Frontend repo**: [habarovsk-forecast-buddy](https://github.com/AbayReushenov/habarovsk-forecast-buddy)
- **GigaChat API**: [developers.sber.ru](https://developers.sber.ru/portal/products/gigachat-api)

---

**🎯 TL;DR**: `./start-dev.sh` → http://localhost:8080
