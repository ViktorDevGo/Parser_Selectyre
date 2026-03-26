# 🚀 Быстрый старт - Selectyre Parser

## 📋 Что делает система

1. **Скачивает** CSV файл с данными о шинах каждые 4 часа
2. **Обновляет** базу данных PostgreSQL по UPSERT логике:
   - Существующие записи (по ID) → обновляет данные + `updated_at`
   - Новые записи → добавляет с `created_at` и `updated_at`
3. **Логирует** все операции с подробной статистикой

## ⚡ Быстрая установка

### 1. Установка зависимостей
```bash
pip3 install psycopg2-binary
```

### 2. Настройка автообновления (выберите один способ)

**macOS (рекомендуется - launchd):**
```bash
./setup_launchd.sh
```

**Linux/macOS (альтернатива - cron):**
```bash
./setup_cron.sh
```

### 3. Проверка
```bash
# Просмотр логов
tail -f logs/update_$(date +%Y%m%d).log

# Ручной запуск обновления
python3 update_data.py

# Проверка данных
python3 check_data.py
```

## 📊 Логика обновления UPSERT

```
┌─────────────────────────────────────────────────┐
│  Скачан новый CSV файл                          │
└─────────────────┬───────────────────────────────┘
                  │
                  ▼
      ┌───────────────────────────┐
      │  Для каждой записи в CSV  │
      └───────────┬───────────────┘
                  │
                  ▼
          ┌───────────────┐
          │ ID существует?│
          └───┬───────┬───┘
              │       │
          ДА  │       │  НЕТ
              │       │
              ▼       ▼
    ┌─────────────┐ ┌─────────────┐
    │ ОБНОВЛЕНИЕ  │ │  СОЗДАНИЕ   │
    │ всех полей  │ │ новой записи│
    │ + updated_at│ │ + created_at│
    │             │ │ + updated_at│
    └─────────────┘ └─────────────┘
```

## 🕐 Расписание обновлений

Автоматическое обновление **каждые 4 часа**:
- 00:00 | 04:00 | 08:00 | 12:00 | 16:00 | 20:00

## 📁 Ключевые файлы

| Файл | Описание |
|------|----------|
| `update_data.py` | Основной скрипт обновления (UPSERT) |
| `check_data.py` | Проверка данных и статистика |
| `test_upsert.py` | Тестирование UPSERT логики |
| `logs/update_YYYYMMDD.log` | Логи обновлений по дням |

## 🔍 Полезные команды

### Мониторинг

```bash
# Следить за обновлением в реальном времени
tail -f logs/update_$(date +%Y%m%d).log

# Последние 5 обновлений
ls -lt logs/update_*.log | head -5

# Проверить статус последнего обновления
grep "ОБНОВЛЕНИЕ ЗАВЕРШЕНО" logs/update_$(date +%Y%m%d).log | tail -1
```

### Управление автообновлением

**launchd (macOS):**
```bash
# Статус
launchctl list | grep selectyre

# Запустить вручную
launchctl start com.selectyre.parser.update

# Остановить
launchctl stop com.selectyre.parser.update

# Удалить из автозапуска
launchctl unload ~/Library/LaunchAgents/com.selectyre.parser.update.plist
```

**cron:**
```bash
# Просмотр задач
crontab -l

# Редактирование
crontab -e

# Удаление всех задач
crontab -r
```

### База данных

```bash
# Ручной запуск обновления
python3 update_data.py

# Статистика и проверка
python3 check_data.py

# Тест UPSERT логики
python3 test_upsert.py
```

## 📈 Статистика обновления

После каждого обновления в логах будет:

```
================================================================================
ОБНОВЛЕНИЕ ЗАВЕРШЕНО УСПЕШНО
================================================================================
Обработано записей из CSV: 6829

Статистика изменений:
  Было записей в БД: 6820
  Стало записей в БД: 6829
  Новых записей: 9           ← Добавлено новых позиций
  Обновленных записей: 6500  ← Обновлены цены/остатки
  Без изменений: 320         ← Не изменились

Время выполнения: 31.46 сек
================================================================================
```

## 🔧 Настройка уведомлений

Отредактируйте функцию `send_notification()` в `update_data.py`:

### Telegram
```python
import requests

def send_notification(status, message):
    logger.info(f"[{status}] {message}")

    # Отправка в Telegram
    TELEGRAM_BOT_TOKEN = "ваш_токен"
    TELEGRAM_CHAT_ID = "ваш_chat_id"

    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    data = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": f"🔄 Selectyre Update\n\n{status}: {message}"
    }
    requests.post(url, data=data)
```

## ❓ FAQ

**Q: Как часто обновляются данные?**
A: Каждые 4 часа автоматически.

**Q: Удаляются ли старые записи?**
A: Нет! Старые записи остаются, обновляются только измененные поля.

**Q: Как увидеть что изменилось?**
A: Сравните `created_at` и `updated_at`. Если `updated_at` > `created_at` - запись обновлялась.

**Q: Можно ли изменить частоту обновления?**
A: Да:
- **launchd**: измените `<integer>14400</integer>` (секунды)
- **cron**: измените `0 */4 * * *` (cron формат)

**Q: Что делать если обновление не работает?**
A: Проверьте логи в `logs/` и статус задачи (`launchctl list` или `crontab -l`)

## 🐛 Решение проблем

### Ошибка подключения к БД
```bash
# Проверьте SSL сертификат
ls -lh ~/.cloud-certs/root.crt

# Перезагрузите сертификат
openssl s_client -showcerts -connect c37e696087932476c61fd621.twc1.net:5432 \
  -starttls postgres < /dev/null 2>/dev/null | \
  sed -ne '/-BEGIN CERTIFICATE-/,/-END CERTIFICATE-/p' > ~/.cloud-certs/root.crt
```

### Автообновление не запускается
```bash
# launchd
launchctl list | grep selectyre
tail -f ~/Library/Logs/selectyre_parser.log

# cron
tail -f /var/log/system.log | grep cron  # macOS
```

## 📞 Поддержка

Для детальной документации см. [README.md](README.md)

---
**Версия**: 2.0 (UPSERT)
**Последнее обновление**: 2026-03-26
