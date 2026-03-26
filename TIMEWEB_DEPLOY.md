# Деплой на Timeweb Cloud

## 🚀 Быстрый деплой

### 1. Подготовка проекта

```bash
# Создать production образ локально
docker build -f Dockerfile.production -t selectyre-parser:production .

# Или загрузить через Git
git init
git add .
git commit -m "Initial commit"
git remote add origin YOUR_REPO_URL
git push -u origin main
```

### 2. Создание контейнера на Timeweb Cloud

#### Через веб-интерфейс:

1. Войти в панель Timeweb Cloud
2. Перейти в **"Облачные вычисления"** → **"Контейнеры"**
3. Нажать **"Создать контейнер"**
4. Выбрать способ развертывания:
   - **Из Docker Hub** (если загрузили образ)
   - **Из Git репозитория** (рекомендуется)

#### Настройки контейнера:

- **Имя**: `selectyre-parser`
- **Образ**: `selectyre-parser:production`
- **Dockerfile**: `Dockerfile.production`
- **Порт**: не требуется (фоновая задача)
- **Ресурсы**:
  - CPU: 0.5-1 vCPU
  - RAM: 512 MB - 1 GB
  - Диск: 5 GB

### 3. Настройка переменных окружения

В разделе **"Переменные окружения"** добавить:

```bash
# База данных PostgreSQL
DB_HOST=c37e696087932476c61fd621.twc1.net
DB_PORT=5432
DB_NAME=default_db
DB_USER=gen_user
DB_PASSWORD=Poison-79
DB_SSL_MODE=verify-full

# Интервал обновления (секунды)
UPDATE_INTERVAL=14400

# Опционально: уведомления
TELEGRAM_BOT_TOKEN=your_bot_token
TELEGRAM_CHAT_ID=your_chat_id
```

### 4. Настройка томов (Volumes)

Создать постоянные тома для:

```
/app/logs  → Логи обновлений
/app/data  → Кэш CSV файлов
```

### 5. Запуск

Нажать **"Создать"** → контейнер автоматически запустится

---

## 📋 Переменные окружения

### Обязательные:

| Переменная | Значение | Описание |
|------------|----------|----------|
| `DB_HOST` | `c37e696087932476c61fd621.twc1.net` | Адрес PostgreSQL сервера |
| `DB_PORT` | `5432` | Порт PostgreSQL |
| `DB_NAME` | `default_db` | Имя базы данных |
| `DB_USER` | `gen_user` | Пользователь БД |
| `DB_PASSWORD` | `Poison-79` | Пароль БД |
| `DB_SSL_MODE` | `verify-full` | Режим SSL |

### Опциональные:

| Переменная | Значение по умолчанию | Описание |
|------------|----------------------|----------|
| `UPDATE_INTERVAL` | `14400` | Интервал обновления (сек) |
| `BATCH_SIZE` | `500` | Размер пакета при импорте |
| `CSV_TIRES_URL` | `https://files.selectyre.ru/...` | URL файла с шинами |
| `CSV_RIMS_URL` | `https://files.selectyre.ru/...` | URL файла с дисками |
| `TELEGRAM_BOT_TOKEN` | - | Токен Telegram бота |
| `TELEGRAM_CHAT_ID` | - | ID чата для уведомлений |
| `TZ` | `Asia/Novosibirsk` | Часовой пояс |

---

## 🔧 Настройка через API Timeweb

### Создание контейнера через API:

```bash
curl -X POST https://api.timeweb.cloud/api/v1/containers \
  -H "Authorization: Bearer YOUR_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "selectyre-parser",
    "image": "selectyre-parser:production",
    "env": [
      {"name": "DB_HOST", "value": "c37e696087932476c61fd621.twc1.net"},
      {"name": "DB_PORT", "value": "5432"},
      {"name": "DB_NAME", "value": "default_db"},
      {"name": "DB_USER", "value": "gen_user"},
      {"name": "DB_PASSWORD", "value": "Poison-79"},
      {"name": "DB_SSL_MODE", "value": "verify-full"},
      {"name": "UPDATE_INTERVAL", "value": "14400"}
    ],
    "resources": {
      "cpu": 0.5,
      "ram": 512,
      "disk": 5
    },
    "volumes": [
      {"name": "logs", "path": "/app/logs"},
      {"name": "data", "path": "/app/data"}
    ]
  }'
```

---

## 📊 Мониторинг

### Просмотр логов:

**Через веб-интерфейс:**
1. Перейти в контейнер
2. Вкладка **"Логи"**
3. Выбрать период

**Через API:**
```bash
curl https://api.timeweb.cloud/api/v1/containers/CONTAINER_ID/logs \
  -H "Authorization: Bearer YOUR_API_TOKEN"
```

### Метрики:

Доступны в разделе **"Мониторинг"**:
- CPU использование
- RAM использование
- Сетевой трафик
- Дисковые операции

---

## 🔄 Обновление контейнера

### Способ 1: Пересборка образа

```bash
# Локально
docker build -f Dockerfile.production -t selectyre-parser:production .
docker push YOUR_REGISTRY/selectyre-parser:production

# На Timeweb Cloud
# Перейти в контейнер → "Пересоздать"
```

### Способ 2: Через Git

```bash
# Обновить код
git add .
git commit -m "Update"
git push

# На Timeweb Cloud
# Контейнер автоматически обновится (если настроен webhook)
```

---

## 🛡️ Безопасность

### SSL сертификаты:

Сертификат будет автоматически извлечен из PostgreSQL сервера при первом подключении.

### Secrets:

Для хранения паролей рекомендуется использовать:
1. Timeweb Cloud Secrets
2. Переменные окружения с флагом "Secret"

### Сетевая изоляция:

Контейнер работает в приватной сети Timeweb Cloud и имеет доступ только к:
- PostgreSQL серверу
- Интернету (для скачивания CSV)

---

## 📝 Troubleshooting

### Контейнер не запускается:

```bash
# Проверить логи
docker logs CONTAINER_ID

# Проверить переменные окружения
docker inspect CONTAINER_ID | grep -A 20 "Env"
```

### Ошибка подключения к БД:

1. Проверить правильность `DB_HOST`, `DB_PORT`, `DB_USER`, `DB_PASSWORD`
2. Проверить что PostgreSQL разрешает подключения из Timeweb Cloud
3. Проверить SSL сертификат

### Высокое использование ресурсов:

1. Увеличить `UPDATE_INTERVAL` (например, до 21600 = 6 часов)
2. Увеличить ресурсы контейнера (CPU/RAM)

---

## 💰 Стоимость

Примерная стоимость на Timeweb Cloud:

- **CPU**: 0.5 vCPU × ~300 руб/месяц = 150 руб
- **RAM**: 512 MB × ~200 руб/GB/месяц = 100 руб
- **Диск**: 5 GB × ~3 руб/GB/месяц = 15 руб

**ИТОГО**: ~265 руб/месяц

---

## 📞 Поддержка

- Документация Timeweb Cloud: https://timeweb.cloud/help
- API документация: https://timeweb.cloud/api-docs
- Техподдержка: support@timeweb.ru

---

**Версия**: 1.0
**Дата**: 2026-03-26
**Автор**: Viktor
