# Selectyre Parser - Makefile для управления Docker

.PHONY: help build up down logs restart clean check shell test

help: ## Показать справку
	@echo "Доступные команды:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

build: ## Собрать Docker образ
	docker-compose build

up: ## Запустить контейнер
	docker-compose up -d

down: ## Остановить контейнер
	docker-compose down

logs: ## Показать логи контейнера
	docker-compose logs -f selectyre-parser

restart: ## Перезапустить контейнер
	docker-compose restart

clean: ## Удалить контейнер и образ
	docker-compose down -v
	docker rmi parser_selectyre-selectyre-parser 2>/dev/null || true

check: ## Проверить статус контейнера
	@docker-compose ps
	@echo ""
	@echo "Последние обновления:"
	@docker-compose exec selectyre-parser ls -lt logs/ 2>/dev/null || echo "Контейнер не запущен"

shell: ## Войти в контейнер (bash)
	docker-compose exec selectyre-parser bash

test: ## Запустить тестовое обновление
	docker-compose exec selectyre-parser python3 update_all.py

check-db: ## Проверить подключение к БД
	docker-compose exec selectyre-parser python3 -c "import psycopg2; import os; conn = psycopg2.connect(host=os.getenv('DB_HOST'), port=os.getenv('DB_PORT'), database=os.getenv('DB_NAME'), user=os.getenv('DB_USER'), password=os.getenv('DB_PASSWORD'), sslmode=os.getenv('DB_SSL_MODE'), sslrootcert='/root/.cloud-certs/root.crt'); print('✓ Подключение к БД успешно'); conn.close()"

stats-tires: ## Статистика по шинам
	docker-compose exec selectyre-parser python3 check_data.py

stats-rims: ## Статистика по дискам
	docker-compose exec selectyre-parser python3 check_rims.py

# Быстрые команды
start: up ## Alias для up
stop: down ## Alias для down
