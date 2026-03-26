# Selectyre Parser Docker Image
FROM python:3.9-slim

# Установка системных зависимостей
RUN apt-get update && apt-get install -y \
    curl \
    openssl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Создание рабочей директории
WORKDIR /app

# Копирование requirements и установка зависимостей
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копирование всех файлов проекта
COPY . .

# Создание директории для логов
RUN mkdir -p logs

# Создание директории для SSL сертификатов
RUN mkdir -p /root/.cloud-certs

# Права на выполнение для скриптов
RUN chmod +x *.py *.sh 2>/dev/null || true

# По умолчанию запускаем обновление всех данных
CMD ["python3", "update_all.py"]
