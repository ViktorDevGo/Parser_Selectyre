# Docker deployment для Selectyre Parser

## 🐳 Быстрый старт

### 1. Подготовка

```bash
# Создать .env файл (скопировать из примера)
cp .env.example .env

# Отредактировать .env при необходимости
nano .env
```

### 2. Запуск

```bash
# Собрать образ и запустить
docker-compose up -d

# Или используя Makefile
make build
make up
```

### 3. Проверка

```bash
# Логи
docker-compose logs -f selectyre-parser

# Или через Makefile
make logs
```

---

## 📋 Доступные команды (Makefile)

```bash
make help          # Показать все команды
make build         # Собрать Docker образ
make up            # Запустить контейнер
make down          # Остановить контейнер
make logs          # Показать логи
make restart       # Перезапустить
make clean         # Удалить контейнер и образ
make check         # Проверить статус
make shell         # Войти в контейнер
make test          # Запустить тестовое обновление
make check-db      # Проверить подключение к БД
make stats-tires   # Статистика по шинам
make stats-rims    # Статистика по дискам
```

---

## 🔧 Ручное управление (docker-compose)

### Запуск и остановка

```bash
# Запустить в фоне
docker-compose up -d

# Остановить
docker-compose down

# Перезапустить
docker-compose restart

# Пересобрать и запустить
docker-compose up -d --build
```

### Мониторинг

```bash
# Логи (следить в реальном времени)
docker-compose logs -f selectyre-parser

# Логи за последние 100 строк
docker-compose logs --tail=100 selectyre-parser

# Статус контейнеров
docker-compose ps
```

### Выполнение команд

```bash
# Запустить обновление вручную
docker-compose exec selectyre-parser python3 update_all.py

# Проверить данные
docker-compose exec selectyre-parser python3 check_data.py
docker-compose exec selectyre-parser python3 check_rims.py

# Войти в контейнер
docker-compose exec selectyre-parser bash
```

---

## 📁 Структура проекта

```
Parser_Selectyre/
├── Dockerfile              # Описание образа
├── docker-compose.yml      # Оркестрация контейнеров
├── .env.example            # Пример переменных окружения
├── .env                    # Ваши переменные окружения (создать!)
├── .dockerignore           # Игнорируемые файлы при сборке
├── requirements.txt        # Python зависимости
├── Makefile                # Команды для управления
│
├── logs/                   # Логи (монтируется как volume)
├── data/                   # CSV файлы (монтируется как volume)
└── ~/.cloud-certs/         # SSL сертификаты (монтируется read-only)
```

---

## 🔐 Переменные окружения (.env)

```bash
# Обязательные
DB_HOST=c37e696087932476c61fd621.twc1.net
DB_PORT=5432
DB_NAME=default_db
DB_USER=gen_user
DB_PASSWORD=Poison-79
DB_SSL_MODE=verify-full

# Опциональные
CSV_TIRES_URL=https://files.selectyre.ru/a42eab22-...csv
CSV_RIMS_URL=https://files.selectyre.ru/6aaad4d8-...csv
BATCH_SIZE=500
UPDATE_INTERVAL=14400
```

---

## 📊 Volumes (постоянные данные)

### Монтируемые директории:

1. **./logs** → Логи обновлений
   - Сохраняются между перезапусками
   - Доступны на хосте

2. **./data** → CSV файлы
   - Кэш скачанных файлов
   - Экономия трафика

3. **~/.cloud-certs** → SSL сертификаты
   - Read-only
   - Используются для подключения к БД

---

## 🔄 Автоматическое обновление

Контейнер автоматически:
1. Запускает первое обновление при старте
2. Ждет 4 часа (14400 секунд)
3. Запускает следующее обновление
4. Повторяет бесконечно

### Изменить интервал обновления:

В `docker-compose.yml` измените `sleep 14400` на нужное значение:
- 1 час: `sleep 3600`
- 2 часа: `sleep 7200`
- 6 часов: `sleep 21600`

Или через `.env`:
```bash
UPDATE_INTERVAL=3600  # 1 час
```

---

## 🐛 Отладка

### Проверка подключения к БД

```bash
make check-db
```

Или вручную:
```bash
docker-compose exec selectyre-parser python3 -c "
import psycopg2
import os
conn = psycopg2.connect(
    host=os.getenv('DB_HOST'),
    port=os.getenv('DB_PORT'),
    database=os.getenv('DB_NAME'),
    user=os.getenv('DB_USER'),
    password=os.getenv('DB_PASSWORD'),
    sslmode=os.getenv('DB_SSL_MODE'),
    sslrootcert='/root/.cloud-certs/root.crt'
)
print('✓ Подключение успешно')
conn.close()
"
```

### Просмотр логов приложения

```bash
# Внутри контейнера
docker-compose exec selectyre-parser tail -f logs/update_all_$(date +%Y%m%d).log

# На хосте
tail -f logs/update_all_$(date +%Y%m%d).log
```

### Проверка SSL сертификата

```bash
docker-compose exec selectyre-parser cat /root/.cloud-certs/root.crt
```

---

## 🚀 Production deployment

### Рекомендации:

1. **Использовать docker-compose.override.yml** для локальных настроек
2. **Добавить health check**:
   ```yaml
   healthcheck:
     test: ["CMD", "python3", "-c", "import psycopg2; import os; psycopg2.connect(...)"]
     interval: 1m
     timeout: 10s
     retries: 3
   ```

3. **Добавить ротацию логов**:
   ```yaml
   logging:
     driver: "json-file"
     options:
       max-size: "10m"
       max-file: "3"
   ```

4. **Использовать secrets для паролей**:
   ```yaml
   secrets:
     db_password:
       file: ./secrets/db_password.txt
   ```

---

## 🔧 Расширенная конфигурация

### Добавление уведомлений

В `.env`:
```bash
TELEGRAM_BOT_TOKEN=your_token
TELEGRAM_CHAT_ID=your_chat_id
```

### Запуск с локальным PostgreSQL

Раскомментировать в `docker-compose.yml`:
```yaml
postgres:
  image: postgres:14-alpine
  ...
```

---

## 📝 Примеры использования

### Сценарий 1: Первый запуск

```bash
# 1. Подготовка
cp .env.example .env
nano .env  # настроить параметры

# 2. Запуск
make build
make up

# 3. Проверка
make logs
make check
```

### Сценарий 2: Обновление кода

```bash
# 1. Остановка
make down

# 2. Обновление кода (git pull или изменения)
git pull

# 3. Пересборка и запуск
make build
make up
```

### Сценарий 3: Проверка данных

```bash
# Статистика по шинам
make stats-tires

# Статистика по дискам
make stats-rims

# Или вручную
docker-compose exec selectyre-parser python3 check_data.py
```

---

## 🛑 Полная очистка

```bash
# Остановить и удалить контейнеры
docker-compose down

# Удалить образ
docker rmi parser_selectyre-selectyre-parser

# Или через Makefile
make clean

# Удалить volumes (ОСТОРОЖНО! Удалит логи и данные)
docker-compose down -v
```

---

## 📞 Troubleshooting

### Контейнер не запускается

```bash
# Проверить логи
docker-compose logs selectyre-parser

# Проверить переменные окружения
docker-compose config
```

### Ошибка SSL сертификата

```bash
# Удалить старый сертификат
rm ~/.cloud-certs/root.crt

# Перезапустить контейнер (сертификат загрузится заново)
docker-compose restart
```

### Ошибка подключения к БД

```bash
# Проверить переменные окружения
cat .env

# Проверить сеть
docker-compose exec selectyre-parser ping -c 3 c37e696087932476c61fd621.twc1.net
```

---

**Версия**: 1.0
**Дата**: 2026-03-26
**Автор**: Viktor
