# 🗄️ Supabase Database Setup Guide

**Пошаговая настройка базы данных для Khabarovsk Forecast Buddy**

## 📋 Шаг 1: Создание проекта Supabase

### 1.1 Регистрация и создание проекта

1. **Перейдите на** [supabase.com](https://supabase.com)
2. **Нажмите "Start your project"** или войдите если уже есть аккаунт
3. **Создайте новый проект**:
   - **Organization**: выберите существующую или создайте новую
   - **Name**: `khabarovsk-forecast-buddy`
   - **Database Password**: создайте надежный пароль (СОХРАНИТЕ ЕГО!)
   - **Region**: `Europe West (Ireland)` или ближайший к вам
   - **Pricing Plan**: `Free tier` (достаточно для разработки)

4. **Ждите создания** (2-3 минуты)

### 1.2 Получение конфигурации

После создания проекта:

1. Перейдите в **Settings → API** (левое меню)
2. **Скопируйте следующие данные**:

```bash
# Project URL (например: https://abcdefgh.supabase.co)
Project URL: ___________________________

# anon public key (длинный JWT token)
anon public: ___________________________

# service_role key (СЕКРЕТНЫЙ ключ!)
service_role: __________________________
```

**⚠️ ВАЖНО**: `service_role` ключ - секретный! Не публикуйте его.

## 📋 Шаг 2: Создание таблиц

### 2.1 Открытие SQL Editor

1. В Supabase Dashboard перейдите в **SQL Editor** (левое меню)
2. Нажмите **"New query"**

### 2.2 Выполнение SQL скрипта

1. **Скопируйте содержимое** файла `supabase_schema.sql`
2. **Вставьте в SQL Editor**
3. **Нажмите "Run"** (или Ctrl+Enter)

### 2.3 Проверка результата

Вы должны увидеть:
```
✅ Tables created: sales_data, forecasts, csv_upload_logs, api_usage_stats
✅ Indexes created
✅ RLS policies enabled
✅ Sample data inserted
✅ Views created
```

## 📋 Шаг 3: Обновление конфигурации

### 3.1 Обновление .env файла

Замените в файле `.env` значения на ваши новые:

```bash
# Supabase Database Configuration
SUPABASE_URL=https://ВАШ_PROJECT_ID.supabase.co
SUPABASE_ANON_KEY=ВАШ_ANON_KEY
SUPABASE_SERVICE_KEY=ВАШ_SERVICE_KEY
```

### 3.2 Перезапуск сервера

```bash
# Остановите current dev script (Ctrl+C)
# Затем запустите заново
./start-dev.sh
```

## 📋 Шаг 4: Тестирование подключения

### 4.1 Проверка API

```bash
# Health check должен теперь работать
curl http://localhost:8000/api/v1/health

# Ожидаемый результат:
{
  "status": "healthy",
  "timestamp": "2024-07-10T15:30:00Z",
  "version": "1.0.0"
}
```

### 4.2 Проверка данных

```bash
# Получение данных о продажах
curl http://localhost:8000/api/v1/data/DOWN_JACKET_001

# Должен вернуть sample данные
```

### 4.3 Проверка в Supabase Dashboard

1. Перейдите в **Table Editor** → **sales_data**
2. Вы должны увидеть sample записи:

| sku_id | date | units_sold | revenue | price |
|--------|------|------------|---------|-------|
| DOWN_JACKET_001 | 2024-01-01 | 5 | 35000 | 7000 |
| DOWN_JACKET_001 | 2024-01-02 | 3 | 21000 | 7000 |
| ... | ... | ... | ... | ... |

## 🔧 Troubleshooting

### ❌ "connection refused"

**Причина**: Неправильные credentials или проект недоступен

**Решение**:
1. Проверьте URL проекта в Supabase Dashboard
2. Убедитесь что скопировали правильные ключи
3. Проверьте что проект не приостановлен

### ❌ "permission denied"

**Причина**: RLS policies блокируют доступ

**Решение**:
1. Убедитесь что используете `SUPABASE_SERVICE_KEY` в бэкенде
2. Проверьте что policies созданы правильно:

```sql
-- В SQL Editor выполните:
SELECT * FROM pg_policies WHERE tablename = 'sales_data';
```

### ❌ "table does not exist"

**Причина**: SQL скрипт не выполнился полностью

**Решение**:
1. Откройте SQL Editor
2. Выполните команду:

```sql
-- Проверить какие таблицы созданы
SELECT tablename FROM pg_tables WHERE schemaname = 'public';
```

3. Если таблиц нет, повторно выполните `supabase_schema.sql`

### ❌ Frontend не может загрузить данные

**Причина**: CORS или RLS настройки

**Решение**:
1. Убедитесь что anon policies созданы:

```sql
-- Проверить anon policies
SELECT * FROM pg_policies WHERE roles @> '{anon}';
```

2. В крайнем случае временно отключите RLS:

```sql
-- ТОЛЬКО ДЛЯ ОТЛАДКИ!
ALTER TABLE sales_data DISABLE ROW LEVEL SECURITY;
```

## 📊 Структура базы данных

### Основные таблицы:

1. **`sales_data`** - исторические данные продаж
   - `sku_id` - ID товара
   - `date` - дата продажи
   - `units_sold` - количество проданных единиц
   - `revenue` - выручка
   - `price` - цена за единицу

2. **`forecasts`** - сгенерированные прогнозы
   - `sku_id` - ID товара
   - `forecast_type` - тип прогноза (7/14/30 дней)
   - `predicted_units` - прогноз продаж
   - `predicted_revenue` - прогноз выручки
   - `ai_explanation` - объяснение от GigaChat

3. **`csv_upload_logs`** - логи загрузки файлов
4. **`api_usage_stats`** - статистика использования API

### Полезные views:

- **`sales_analytics`** - аналитика по товарам
- **`recent_forecasts`** - последние прогнозы

## 🎯 Следующие шаги

После успешной настройки:

1. ✅ **Health check** работает (статус 200)
2. ✅ **Upload CSV** работает
3. ✅ **Generate forecast** работает
4. ✅ **Frontend** подключается к API

**Теперь ваша система полностью функциональна!**

## 🔗 Полезные ссылки

- [Supabase Documentation](https://supabase.com/docs)
- [Supabase Dashboard](https://supabase.com/dashboard)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)

---

**🎉 Happy coding with Supabase!**

*Khabarovsk Forecast Buddy Team*
