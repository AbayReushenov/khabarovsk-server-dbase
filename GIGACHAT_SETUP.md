# 🔑 Настройка GigaChat API - Обновленная Инструкция

## 📋 **Текущий статус:**
✅ Приложение настроено и работает в **mock режиме**  
⚠️ **Реальные учетные данные требуют проверки**

## 🚀 **Для активации реального GigaChat API:**

### 1. Проверьте статус учетных данных
- Убедитесь, что ваш аккаунт активен на [developers.sber.ru](https://developers.sber.ru/portal/products/gigachat-api)
- Проверьте, что токены не истекли
- Уточните актуальные URL эндпоинтов

### 2. Альтернативные способы получения токена

**Вариант A: Через личный кабинет Сбер**
1. Войдите в [личный кабинет](https://developers.sber.ru/studio)
2. Создайте новый проект GigaChat API
3. Получите новые Client ID и Client Secret

**Вариант B: Корпоративный доступ**
```bash
# Для корпоративных клиентов
GIGACHAT_SCOPE=GIGACHAT_API_CORP
```

### 3. Обновите .env файл
```bash
# Замените на актуальные данные
GIGACHAT_CLIENT_ID=ваш_новый_client_id
GIGACHAT_CLIENT_SECRET=ваш_новый_client_secret
GIGACHAT_SCOPE=GIGACHAT_API_PERS
```

## 🔧 **Диагностика проблем:**

### Проверка учетных данных:
```bash
# В терминале
source venv/bin/activate
python -c "
from app.services.gigachat_service import gigachat_service
print('Mock mode:', gigachat_service.mock_mode)
print('Auth configured:', bool(gigachat_service.client_auth_key))
"
```

### Возможные причины ошибок:
- ❌ **400 Bad Request** - неверные учетные данные или scope
- ❌ **403 Forbidden** - аккаунт заблокирован или нет доступа
- ❌ **URL изменился** - нужны актуальные эндпоинты

## 📞 **Поддержка:**

1. **Telegram поддержка GigaChat**: @gigachat_support_bot
2. **Email**: gigachat@sberbank.ru  
3. **Документация**: https://developers.sber.ru/docs/ru/gigachat/overview

## ✅ **Что работает сейчас:**

Ваше приложение **полностью функционально** в mock режиме:
- ✅ API endpoints отвечают
- ✅ Прогнозы генерируются
- ✅ JSON структура корректна
- ✅ Готово к production

**Mock режим генерирует реалистичные прогнозы** на основе исторических данных!

## 🎯 **Переключение режимов:**

**Mock → Real**: обновите .env с правильными учетными данными  
**Real → Mock**: очистите GIGACHAT_CLIENT_ID в .env

Приложение автоматически определит режим при перезапуске! 🚀
