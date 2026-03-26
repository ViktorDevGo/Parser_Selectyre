# Selectyre Parser - Полная система импорта данных

Проект для автоматической загрузки и обновления данных о **шинах** и **дисках** из CSV файлов Selectyre в базу данных PostgreSQL.

## 📊 Статус проекта

✅ **Успешно импортировано:**
- **Шины** (Tires): 6,829 записей → таблица `Selectyre_tyer`
- **Диски** (Rims): 3,005 записей → таблица `selectyre_rims`
- **Всего**: 9,834 товарных позиций

## 🔄 Логика обновления (UPSERT)

Система использует умную логику обновления без удаления данных:

```
┌─────────────────────────┐
│ Скачивание нового CSV   │
└───────────┬─────────────┘
            │
            ▼
┌─────────────────────────┐
│ Для каждой записи       │
└───────────┬─────────────┘
            │
      ┌─────┴─────┐
      │ ID есть?  │
      └─┬───────┬─┘
   ДА   │       │   НЕТ
        │       │
        ▼       ▼
   ┌────────┐ ┌────────┐
   │UPDATE  │ │INSERT  │
   │+ time  │ │+ time  │
   └────────┘ └────────┘
```

- **Существующие записи** → обновление всех полей + `updated_at`
- **Новые записи** → добавление с `created_at` + `updated_at`
- **Удаления НЕТ** → данные накапливаются и обновляются

## 📁 Структура проекта

```
Parser_Selectyre/
│
├── 📖 Документация
│   ├── README_FULL.md           ← Полная документация (этот файл)
│   ├── README.md                ← Документация по шинам
│   └── QUICKSTART.md            ← Быстрый старт
│
├── 🗄️ SQL скрипты
│   ├── create_table.sql         ← Создание таблицы шин
│   ├── create_table_rims.sql    ← Создание таблицы дисков
│   └── alter_table.sql          ← Добавление updated_at
│
├── 🔄 Скрипты обновления
│   ├── update_all.py            ← Обновление ВСЕХ данных (рекомендуется!)
│   ├── update_data.py           ← Обновление только шин
│   └── update_rims.py           ← Обновление только дисков
│
├── 📥 Скрипты первичного импорта
│   ├── import_data.py           ← Импорт шин
│   └── import_rims.py           ← Импорт дисков
│
├── 📊 Скрипты проверки
│   ├── check_data.py            ← Статистика по шинам
│   ├── check_rims.py            ← Статистика по дискам
│   └── test_upsert.py           ← Тестирование UPSERT
│
├── ⚙️ Настройка автообновления
│   ├── setup_all_launchd.sh     ← Установка для ВСЕХ (macOS)
│   ├── setup_all_cron.sh        ← Установка для ВСЕХ (Linux/macOS)
│   ├── setup_launchd.sh         ← Установка только шин (macOS)
│   └── setup_cron.sh            ← Установка только шин (Linux/macOS)
│
├── 📂 Данные
│   ├── selectyre_data.csv       ← CSV файл с шинами
│   └── selectyre_rims.csv       ← CSV файл с дисками
│
└── 📂 logs/                     ← Логи обновлений
    ├── update_all_YYYYMMDD.log  ← Объединенные обновления
    ├── update_YYYYMMDD.log      ← Обновления шин
    └── update_rims_YYYYMMDD.log ← Обновления дисков
```

## 🗄️ Структура таблиц

### Таблица `Selectyre_tyer` (Шины)

38 полей + индексы:
- Основные: id, article, name, brand, model, quantity, price
- Характеристики: season, width, profile, diameter, load_index, speed_index
- Особенности: studded, run_on_flat, reinforcement_type
- Логистика: warehouse_id, warehouse_name, supplier_code
- Изображения: image_url, image_sha1
- Время: created_at, updated_at

**Индексы**: brand, model, warehouse_id, article, updated_at

### Таблица `selectyre_rims` (Диски)

35 полей + индексы:
- Основные: id, article, name, brand, model, quantity, price
- Характеристики: width, diameter, bolt_count, pcd, et, dia
- Тип: wheel_type (литой/штампованный), color
- Логистика: warehouse_id, warehouse_name, category
- Изображения: image_url, product_image (2 изображения)
- Время: created_at, updated_at

**Индексы**: brand, model, warehouse_id, article, diameter, width, pcd, updated_at

## 🚀 Быстрый старт

### 1. Установка зависимостей
```bash
pip3 install psycopg2-binary
```

### 2. Настройка автообновления ВСЕХ данных (рекомендуется)

**macOS (launchd):**
```bash
./setup_all_launchd.sh
```

**Linux/macOS (cron):**
```bash
./setup_all_cron.sh
```

### 3. Проверка работы

```bash
# Просмотр логов
tail -f logs/update_all_$(date +%Y%m%d).log

# Ручной запуск
python3 update_all.py

# Статистика
python3 check_data.py    # Шины
python3 check_rims.py    # Диски
```

## ⏰ Расписание обновлений

**Автоматическое обновление каждые 4 часа:**
- 00:00 | 04:00 | 08:00 | 12:00 | 16:00 | 20:00

**Процесс обновления (~40 секунд):**
1. Обновление шин (6,829 записей) ~ 26 сек
2. Обновление дисков (3,005 записей) ~ 14 сек

## 📝 Примеры SQL запросов

### Поиск шин

```sql
-- По бренду и модели
SELECT * FROM Selectyre_tyer
WHERE brand = 'Pirelli' AND model LIKE 'P Zero%';

-- По размеру
SELECT brand, model, price, quantity
FROM Selectyre_tyer
WHERE width = '205' AND profile = '55' AND diameter = '16'
  AND quantity > 0
ORDER BY price ASC;

-- Зимние шипованные шины
SELECT brand, model, name, price, quantity, warehouse_name
FROM Selectyre_tyer
WHERE season = 'зимняя'
  AND studded = 'шип'
  AND quantity > 0
ORDER BY price ASC
LIMIT 20;

-- Обновленные сегодня
SELECT COUNT(*) as updated_today
FROM Selectyre_tyer
WHERE DATE(updated_at) = CURRENT_DATE;
```

### Поиск дисков

```sql
-- По размеру и разболтовке
SELECT brand, model, name, price, quantity
FROM selectyre_rims
WHERE diameter = '16'
  AND width = '6.5'
  AND pcd = '114.3'
  AND bolt_count = '5'
  AND quantity > 0
ORDER BY price ASC;

-- Литые диски определенного диаметра
SELECT brand, model, color, price, quantity, warehouse_name
FROM selectyre_rims
WHERE wheel_type = 'Литой'
  AND diameter = '17'
  AND quantity > 4
ORDER BY price ASC;

-- Топ брендов по наличию
SELECT brand, SUM(quantity) as total_qty, COUNT(*) as models
FROM selectyre_rims
GROUP BY brand
ORDER BY total_qty DESC
LIMIT 10;
```

### Комбинированные запросы

```sql
-- Общая статистика по обеим таблицам
SELECT
    'Шины' as type,
    COUNT(*) as total,
    SUM(quantity) as total_qty,
    AVG(price)::numeric(10,2) as avg_price
FROM Selectyre_tyer
UNION ALL
SELECT
    'Диски' as type,
    COUNT(*) as total,
    SUM(quantity) as total_qty,
    AVG(price)::numeric(10,2) as avg_price
FROM selectyre_rims;

-- Товары обновленные за последние 24 часа
SELECT 'Шины' as type, COUNT(*) as count
FROM Selectyre_tyer
WHERE updated_at >= NOW() - INTERVAL '24 hours'
UNION ALL
SELECT 'Диски' as type, COUNT(*) as count
FROM selectyre_rims
WHERE updated_at >= NOW() - INTERVAL '24 hours';
```

## 📊 Мониторинг и логирование

### Просмотр логов

```bash
# Все обновления
tail -f logs/update_all_$(date +%Y%m%d).log

# Только шины
tail -f logs/update_$(date +%Y%m%d).log

# Только диски
tail -f logs/update_rims_$(date +%Y%m%d).log

# Последние 50 строк всех логов
tail -50 logs/update_all_*.log
```

### Проверка статуса

```bash
# launchd (macOS)
launchctl list | grep selectyre

# cron
crontab -l | grep update

# Последнее обновление
grep "ОБНОВЛЕНИЕ ЗАВЕРШЕНО" logs/update_all_$(date +%Y%m%d).log | tail -1
```

## 🔧 Управление автообновлением

### launchd (macOS)

```bash
# Статус
launchctl list | grep com.selectyre.parser.updateall

# Запустить вручную
launchctl start com.selectyre.parser.updateall

# Остановить автообновление
launchctl stop com.selectyre.parser.updateall

# Удалить из автозапуска
launchctl unload ~/Library/LaunchAgents/com.selectyre.parser.updateall.plist

# Добавить обратно
launchctl load ~/Library/LaunchAgents/com.selectyre.parser.updateall.plist
```

### cron

```bash
# Просмотр задач
crontab -l

# Редактирование
crontab -e

# Удаление конкретной задачи
crontab -l | grep -v update_all.py | crontab -

# Удаление всех задач
crontab -r
```

## 📈 Статистика по данным

### Шины (Selectyre_tyer)
- **Всего записей**: 6,829
- **Брендов**: 50+
- **Складов**: 6
- **Средняя цена**: 10,962 руб.
- **Топ бренды**: Ikon Tyres, Maxxis, Yokohama

### Диски (selectyre_rims)
- **Всего записей**: 3,005
- **Брендов**: 30+
- **Складов**: 3
- **Средняя цена**: 10,288 руб.
- **Типы**: Литые (2,732), Штампованные (273)
- **Диаметры**: R13-R22

## 🔔 Настройка уведомлений

Для получения уведомлений при обновлениях, отредактируйте функцию `send_notification()` в скриптах:

### Telegram

```python
import requests

def send_notification(status, message):
    logger.info(f"[{status}] {message}")

    TELEGRAM_BOT_TOKEN = "ваш_токен"
    TELEGRAM_CHAT_ID = "ваш_chat_id"

    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    emoji = "✅" if status == "SUCCESS" else "❌"
    data = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": f"{emoji} Selectyre Update\n\n{status}: {message}"
    }
    requests.post(url, data=data)
```

## 🐛 Устранение неполадок

### Ошибка подключения к БД

```bash
# Проверка SSL сертификата
ls -lh ~/.cloud-certs/root.crt

# Перезагрузка сертификата
openssl s_client -showcerts -connect c37e696087932476c61fd621.twc1.net:5432 \
  -starttls postgres < /dev/null 2>/dev/null | \
  sed -ne '/-BEGIN CERTIFICATE-/,/-END CERTIFICATE-/p' > ~/.cloud-certs/root.crt
```

### Автообновление не запускается

```bash
# Проверка задачи (macOS)
launchctl list | grep selectyre
tail -f logs/launchd_all.out.log

# Проверка задачи (cron)
tail -f /var/log/system.log | grep cron  # macOS
tail -f /var/log/syslog | grep CRON     # Linux
```

### CSV файл не скачивается

```bash
# Проверка доступности
curl -I "https://files.selectyre.ru/a42eab22-713d-4cf4-b618-b9b4d4a8d09c.csv"
curl -I "https://files.selectyre.ru/6aaad4d8-68b1-43cc-a238-90432d7ffa94.csv"

# Проверка логов
tail -50 logs/update_all_$(date +%Y%m%d).log
```

## 🛠 Возможные улучшения

1. ✅ Автоматическое обновление каждые 4 часа
2. ✅ UPSERT логика без удаления данных
3. ✅ Подробное логирование
4. 🔄 История изменений цен
5. 🔄 Веб-интерфейс для поиска
6. 🔄 REST API
7. 🔄 Интеграция с 1C
8. 🔄 Dashboard с метриками (Grafana)
9. 🔄 Уведомления в Telegram/Email
10. 🔄 Отчеты по изменениям остатков

## 📞 Параметры подключения

```python
DB_CONNECTION = {
    'host': 'c37e696087932476c61fd621.twc1.net',
    'port': 5432,
    'database': 'default_db',
    'user': 'gen_user',
    'password': 'Poison-79',
    'sslmode': 'verify-full',
    'sslrootcert': '~/.cloud-certs/root.crt'
}
```

## 📌 Источники данных

- **Шины**: https://files.selectyre.ru/a42eab22-713d-4cf4-b618-b9b4d4a8d09c.csv
- **Диски**: https://files.selectyre.ru/6aaad4d8-68b1-43cc-a238-90432d7ffa94.csv
- **Кодировка**: windows-1251
- **Разделитель**: `;`
- **Формат**: CSV с заголовком

---

**Дата создания**: 2026-03-26
**Последнее обновление**: 2026-03-26
**Версия**: 2.0 (UPSERT для обеих таблиц)
**Автор**: Viktor
**Лицензия**: Private
