# Selectyre Parser - Парсер данных о шинах

Проект для загрузки и парсинга данных о шинах из CSV файла Selectyre в базу данных PostgreSQL.

## 📊 Результаты импорта

✅ **Успешно импортировано: 6829 записей**

### Статистика по брендам (топ-10):
- Ikon Tyres: 837 шт.
- Maxxis: 636 шт.
- Yokohama: 446 шт.
- Hankook: 391 шт.
- Nexen: 390 шт.
- Sonix: 373 шт.
- Mazzini: 315 шт.
- Cordiant: 282 шт.
- Pirelli: 270 шт.
- Prinx: 236 шт.

### Статистика по складам:
- Запаска Новосибирск: 4046 шт.
- Форточки Новосибирск: 1547 шт.
- Бринекс Новосибирск 2: 674 шт.
- Север Авто ЦС Новосибирск: 315 шт.
- Бринекс Новосибирск: 150 шт.
- Big Machine Новосибирск: 97 шт.

**Средняя цена: 10,962.23 руб.**

## 🗂 Структура проекта

```
Parser_Selectyre/
├── selectyre_data.csv      # Скачанный CSV файл (кодировка windows-1251)
├── create_table.sql        # SQL скрипт для создания таблицы
├── import_data.py          # Python скрипт для первичного импорта данных
├── update_data.py          # Python скрипт для автоматического обновления
├── check_data.py           # Python скрипт для проверки данных
├── setup_cron.sh           # Скрипт установки cron (Linux/macOS)
├── setup_launchd.sh        # Скрипт установки launchd (macOS)
├── logs/                   # Директория с логами обновлений
└── README.md               # Этот файл
```

## 🗄 Структура таблицы `Selectyre_tyer`

Таблица содержит следующие поля:

| Поле | Тип | Описание |
|------|-----|----------|
| id | TEXT | Уникальный идентификатор (PRIMARY KEY) |
| article | TEXT | Артикул |
| name | TEXT | Полное название |
| brand | TEXT | Бренд |
| model | TEXT | Модель |
| quantity | INTEGER | Количество в наличии |
| price | NUMERIC(10,2) | Цена |
| season | TEXT | Сезон (зимняя/летняя) |
| vehicle_type | TEXT | Тип ТС |
| width | TEXT | Ширина |
| profile | TEXT | Профиль |
| diameter | TEXT | Диаметр |
| load_index | TEXT | Индекс нагрузки |
| speed_index | TEXT | Индекс скорости |
| reinforcement_type | TEXT | Тип усиленности |
| studded | TEXT | Шипованность |
| run_on_flat | TEXT | Run Flat |
| homologation | TEXT | Омологация |
| rim_protection | TEXT | Защита диска |
| sidewall_text | TEXT | Надпись на боковине |
| shop_length | TEXT | Длина (склад) |
| shop_width | TEXT | Ширина (склад) |
| shop_height | TEXT | Высота (склад) |
| shop_weight | TEXT | Вес (склад) |
| supplier_code | TEXT | Код поставщика |
| production_year | TEXT | Год производства |
| sale_item | TEXT | Товар SALE |
| delivery_time | TEXT | Срок доставки |
| applying | TEXT | Applying |
| axle | TEXT | Axle |
| layering | TEXT | Layering |
| studdable | TEXT | Studdable |
| supplier_article | TEXT | Артикул поставщика |
| image_url | TEXT | URL изображения |
| image_sha1 | TEXT | SHA1 изображения |
| warehouse_id | TEXT | ID склада |
| warehouse_name | TEXT | Название склада |
| created_at | TIMESTAMP | Дата создания записи |

### Индексы:
- `idx_brand` - по бренду
- `idx_model` - по модели
- `idx_warehouse_id` - по ID склада
- `idx_article` - по артикулу

## 🔧 Требования

- Python 3.x
- psycopg2-binary
- PostgreSQL с SSL

## 📥 Установка зависимостей

```bash
pip3 install psycopg2-binary
```

## 🚀 Использование

### 1. Скачивание и импорт данных

```bash
# Скачать CSV файл
curl -o selectyre_data.csv "https://files.selectyre.ru/a42eab22-713d-4cf4-b618-b9b4d4a8d09c.csv"

# Запустить импорт
python3 import_data.py
```

### 2. Проверка данных

```bash
python3 check_data.py
```

### 3. Настройка автоматического обновления (каждые 4 часа)

**Вариант 1: Использование launchd (рекомендуется для macOS)**

```bash
# Автоматическая установка
./setup_launchd.sh

# Ручное управление
launchctl list | grep selectyre              # Проверить статус
launchctl start com.selectyre.parser.update  # Запустить вручную
launchctl stop com.selectyre.parser.update   # Остановить
```

**Вариант 2: Использование cron (Linux/macOS)**

```bash
# Автоматическая установка
./setup_cron.sh

# Проверка задач
crontab -l

# Ручное редактирование
crontab -e
```

**Вариант 3: Ручное обновление**

```bash
python3 update_data.py
```

### 4. Просмотр логов обновлений

```bash
# Логи текущего дня
tail -f logs/update_$(date +%Y%m%d).log

# Логи cron
tail -f logs/cron.log

# Логи launchd
tail -f logs/launchd.out.log
tail -f logs/launchd.err.log
```

### 5. Прямое подключение к БД (если установлен psql)

```bash
export PGSSLROOTCERT=$HOME/.cloud-certs/root.crt
psql 'postgresql://gen_user:Poison-79@c37e696087932476c61fd621.twc1.net:5432/default_db?sslmode=verify-full'
```

## 📝 Примеры SQL запросов

### Поиск шин по бренду:
```sql
SELECT * FROM Selectyre_tyer WHERE brand = 'Pirelli';
```

### Поиск по размерам:
```sql
SELECT * FROM Selectyre_tyer
WHERE width = '205' AND profile = '55' AND diameter = '16';
```

### Товары на складе с количеством > 50:
```sql
SELECT brand, model, quantity, price, warehouse_name
FROM Selectyre_tyer
WHERE quantity > 50
ORDER BY price ASC;
```

### Зимние шипованные шины:
```sql
SELECT * FROM Selectyre_tyer
WHERE season = 'зимняя' AND studded = 'шип'
ORDER BY price ASC;
```

## 🔐 Настройка SSL сертификата

Сертификат извлекается автоматически из сервера при первом запуске. Если нужно обновить:

```bash
openssl s_client -showcerts -connect c37e696087932476c61fd621.twc1.net:5432 \
  -starttls postgres < /dev/null 2>/dev/null | \
  sed -ne '/-BEGIN CERTIFICATE-/,/-END CERTIFICATE-/p' > ~/.cloud-certs/root.crt
```

## 📄 Формат CSV

- **Кодировка**: windows-1251
- **Разделитель**: `;`
- **Заголовок**: первая строка
- **Формат данных**: текстовые поля и числовые значения

## ⚙️ Параметры подключения к БД

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

## 📊 Особенности импорта

- Данные импортируются пакетами по 1000 записей для оптимальной производительности
- Автоматическое преобразование типов данных (числа, текст)
- Создание индексов для ускорения поиска
- Обработка русских символов (windows-1251 → UTF-8)

## ⏰ Автоматическое обновление

Система поддерживает автоматическое обновление данных каждые 4 часа:

### Расписание обновлений:
- **00:00** - полночь
- **04:00** - раннее утро
- **08:00** - утро
- **12:00** - полдень
- **16:00** - день
- **20:00** - вечер

### Процесс обновления:
1. Скачивание нового CSV файла с Selectyre
2. Проверка целостности файла
3. Очистка старых данных в таблице
4. Загрузка новых данных
5. Сохранение логов и статистики

### Логирование:
- Все обновления записываются в `logs/update_YYYYMMDD.log`
- При использовании cron: `logs/cron.log`
- При использовании launchd: `logs/launchd.out.log` и `logs/launchd.err.log`
- Логи содержат информацию о времени выполнения, количестве записей, ошибках

### Мониторинг:

```bash
# Посмотреть последние обновления
ls -lht logs/update_*.log | head -5

# Следить за обновлением в реальном времени
tail -f logs/update_$(date +%Y%m%d).log

# Проверить статус последнего обновления
grep "ОБНОВЛЕНИЕ ЗАВЕРШЕНО" logs/update_$(date +%Y%m%d).log
```

## 🛠 Возможные улучшения

1. ✅ ~~Настроить автоматическое обновление данных по расписанию~~ (Готово!)
2. Добавить инкрементальное обновление данных (только изменения)
3. Реализовать историю изменений цен и остатков
4. Добавить уведомления при критических изменениях (например, Telegram/Email)
5. Добавить API для доступа к данным
6. Создать веб-интерфейс для поиска и мониторинга
7. Добавить метрики и дашборды (Grafana)

## 🔔 Уведомления

Вы можете расширить скрипт `update_data.py` для отправки уведомлений:

### Telegram уведомления:
```python
# Добавьте в функцию send_notification()
import requests

TELEGRAM_BOT_TOKEN = "ваш_токен"
TELEGRAM_CHAT_ID = "ваш_chat_id"

def send_telegram(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    data = {"chat_id": TELEGRAM_CHAT_ID, "text": message}
    requests.post(url, data=data)
```

### Email уведомления:
```python
import smtplib
from email.mime.text import MIMEText

def send_email(subject, message):
    msg = MIMEText(message)
    msg['Subject'] = subject
    msg['From'] = 'your@email.com'
    msg['To'] = 'recipient@email.com'

    with smtplib.SMTP('smtp.gmail.com', 587) as server:
        server.starttls()
        server.login('your@email.com', 'password')
        server.send_message(msg)
```

## 🐛 Устранение неполадок

### Проблема: обновление не запускается автоматически

**Решение для cron:**
```bash
# Проверьте задачи cron
crontab -l

# Проверьте логи cron системы
tail -f /var/log/system.log | grep cron  # macOS
tail -f /var/log/syslog | grep CRON     # Linux
```

**Решение для launchd:**
```bash
# Проверьте статус
launchctl list | grep selectyre

# Перезагрузите задание
launchctl unload ~/Library/LaunchAgents/com.selectyre.parser.update.plist
launchctl load ~/Library/LaunchAgents/com.selectyre.parser.update.plist
```

### Проблема: ошибки подключения к БД

**Решение:**
```bash
# Проверьте SSL сертификат
ls -lh ~/.cloud-certs/root.crt

# Перезагрузите сертификат
openssl s_client -showcerts -connect c37e696087932476c61fd621.twc1.net:5432 \
  -starttls postgres < /dev/null 2>/dev/null | \
  sed -ne '/-BEGIN CERTIFICATE-/,/-END CERTIFICATE-/p' > ~/.cloud-certs/root.crt
```

### Проблема: CSV файл не скачивается

**Решение:**
```bash
# Проверьте доступность файла
curl -I "https://files.selectyre.ru/a42eab22-713d-4cf4-b618-b9b4d4a8d09c.csv"

# Проверьте логи
tail -50 logs/update_$(date +%Y%m%d).log
```

---

**Дата создания**: 2026-03-26
**Последнее обновление**: 2026-03-26
**Версия**: 2.0
**Автор**: Viktor
