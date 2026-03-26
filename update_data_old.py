#!/usr/bin/env python3
"""
Скрипт для автоматического обновления данных Selectyre
Скачивает новый CSV и обновляет таблицу в БД
"""

import csv
import psycopg2
from psycopg2.extras import execute_batch
import os
import subprocess
from datetime import datetime
import logging

# Настройка логирования
LOG_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logs')
os.makedirs(LOG_DIR, exist_ok=True)
LOG_FILE = os.path.join(LOG_DIR, f'update_{datetime.now().strftime("%Y%m%d")}.log')

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE, encoding='utf-8'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# Параметры
CSV_URL = 'https://files.selectyre.ru/a42eab22-713d-4cf4-b618-b9b4d4a8d09c.csv'
CSV_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'selectyre_data.csv')
CSV_FILE_NEW = CSV_FILE + '.new'
ENCODING = 'windows-1251'
DELIMITER = ';'

DB_CONNECTION = {
    'host': 'c37e696087932476c61fd621.twc1.net',
    'port': 5432,
    'database': 'default_db',
    'user': 'gen_user',
    'password': 'Poison-79',
    'sslmode': 'require'
}

def download_csv():
    """Скачивание нового CSV файла"""
    try:
        logger.info(f"Скачивание CSV из {CSV_URL}...")
        result = subprocess.run(
            ['curl', '-o', CSV_FILE_NEW, CSV_URL],
            capture_output=True,
            text=True,
            timeout=300
        )

        if result.returncode != 0:
            raise Exception(f"Ошибка скачивания: {result.stderr}")

        # Проверка размера файла
        file_size = os.path.getsize(CSV_FILE_NEW)
        if file_size < 1000:
            raise Exception(f"Файл слишком маленький ({file_size} байт), возможно ошибка скачивания")

        logger.info(f"✓ CSV скачан успешно ({file_size / 1024 / 1024:.2f} MB)")
        return True
    except Exception as e:
        logger.error(f"✗ Ошибка скачивания CSV: {e}")
        if os.path.exists(CSV_FILE_NEW):
            os.remove(CSV_FILE_NEW)
        return False

def create_connection():
    """Создание подключения к БД"""
    try:
        conn = psycopg2.connect(**DB_CONNECTION)
        logger.info("✓ Подключение к БД установлено")
        return conn
    except Exception as e:
        logger.error(f"✗ Ошибка подключения к БД: {e}")
        raise

def get_current_stats(conn):
    """Получение текущей статистики"""
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) FROM Selectyre_tyer")
            count = cur.fetchone()[0]

            cur.execute("SELECT MAX(created_at) FROM Selectyre_tyer")
            last_update = cur.fetchone()[0]

        return {'count': count, 'last_update': last_update}
    except:
        return {'count': 0, 'last_update': None}

def update_table(conn):
    """Обновление данных в таблице"""
    try:
        logger.info("Начало обновления таблицы...")

        # Подсчет строк в новом файле
        with open(CSV_FILE_NEW, 'r', encoding=ENCODING) as f:
            new_rows_count = sum(1 for _ in f) - 1  # минус заголовок

        logger.info(f"В новом файле {new_rows_count} записей")

        # Очистка старых данных
        with conn.cursor() as cur:
            cur.execute("TRUNCATE TABLE Selectyre_tyer")
            conn.commit()
        logger.info("✓ Старые данные удалены")

        # Загрузка новых данных
        with open(CSV_FILE_NEW, 'r', encoding=ENCODING) as csvfile:
            reader = csv.DictReader(csvfile, delimiter=DELIMITER)

            insert_query = """
                INSERT INTO Selectyre_tyer (
                    id, article, name, brand, model, quantity, price,
                    season, vehicle_type, width, profile, diameter,
                    load_index, speed_index, reinforcement_type, studded,
                    run_on_flat, homologation, rim_protection, sidewall_text,
                    shop_length, shop_width, shop_height, shop_weight,
                    supplier_code, production_year, sale_item, delivery_time,
                    applying, axle, layering, studdable, supplier_article,
                    image_url, image_sha1, warehouse_id, warehouse_name
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s
                )
            """

            batch_data = []
            total_rows = 0

            for row in reader:
                try:
                    quantity = int(row['QUANTITY']) if row['QUANTITY'] else None
                    price = float(row['PRICE'].replace(',', '.')) if row['PRICE'] else None

                    data = (
                        row['ID'], row['ARTICLE'], row['NAME'], row['BRAND'], row['MODEL'],
                        quantity, price, row['Сезон'], row['Тип ТС'], row['Ширина'],
                        row['Профиль'], row['Диаметр'], row['Индекс нагрузки'],
                        row['Индекс скорости'], row['Тип усиленности'], row['Шипованность'],
                        row['Run on Flat'], row['Омологация'], row['Защита диска'],
                        row['Надпись на боковине'], row['SHOP_LENGTH'], row['SHOP_WIDTH'],
                        row['SHOP_HEIGHT'], row['SHOP_WEIGHT'], row['Код поставщика'],
                        row['Год производства'], row['Товар SALE'], row['Cрок доставки'],
                        row['APPLYING'], row['AXLE'], row['LAYERING'], row['STUDDABLE'],
                        row['Артикул поставщика'], row['Изображение ММ 1'],
                        row['Изображение ММ 1_SHA1'], row['WAREHOUSE_ID'], row['WAREHOUSE_NAME']
                    )

                    batch_data.append(data)
                    total_rows += 1

                    if len(batch_data) >= 1000:
                        with conn.cursor() as cur:
                            execute_batch(cur, insert_query, batch_data)
                            conn.commit()
                        logger.info(f"  Импортировано {total_rows} строк...")
                        batch_data = []

                except Exception as e:
                    logger.warning(f"Ошибка обработки строки {total_rows + 1}: {e}")
                    continue

            # Вставка оставшихся записей
            if batch_data:
                with conn.cursor() as cur:
                    execute_batch(cur, insert_query, batch_data)
                    conn.commit()

            logger.info(f"✓ Всего импортировано: {total_rows} строк")

        # Замена старого файла новым
        if os.path.exists(CSV_FILE):
            os.remove(CSV_FILE)
        os.rename(CSV_FILE_NEW, CSV_FILE)

        return total_rows

    except Exception as e:
        logger.error(f"✗ Ошибка обновления таблицы: {e}")
        conn.rollback()
        raise

def send_notification(status, message):
    """Отправка уведомления (можно расширить для email/telegram)"""
    logger.info(f"[{status}] {message}")

def main():
    """Основная функция"""
    start_time = datetime.now()
    logger.info("=" * 80)
    logger.info(f"НАЧАЛО ОБНОВЛЕНИЯ ДАННЫХ SELECTYRE")
    logger.info(f"Время запуска: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("=" * 80)

    conn = None
    try:
        # Подключение к БД
        conn = create_connection()

        # Текущая статистика
        old_stats = get_current_stats(conn)
        logger.info(f"\nТекущее состояние БД:")
        logger.info(f"  Записей: {old_stats['count']}")
        logger.info(f"  Последнее обновление: {old_stats['last_update']}")

        # Скачивание нового CSV
        if not download_csv():
            send_notification("ERROR", "Не удалось скачать новый CSV файл")
            return 1

        # Обновление таблицы
        new_count = update_table(conn)

        # Новая статистика
        new_stats = get_current_stats(conn)

        # Итоги
        duration = (datetime.now() - start_time).total_seconds()
        logger.info("\n" + "=" * 80)
        logger.info("ОБНОВЛЕНИЕ ЗАВЕРШЕНО УСПЕШНО")
        logger.info("=" * 80)
        logger.info(f"Было записей: {old_stats['count']}")
        logger.info(f"Стало записей: {new_stats['count']}")
        logger.info(f"Изменение: {new_stats['count'] - old_stats['count']:+d}")
        logger.info(f"Время выполнения: {duration:.2f} сек")
        logger.info("=" * 80)

        send_notification("SUCCESS", f"Обновлено {new_count} записей за {duration:.2f} сек")

        return 0

    except Exception as e:
        logger.error(f"\n✗ КРИТИЧЕСКАЯ ОШИБКА: {e}")
        send_notification("ERROR", f"Ошибка обновления: {e}")
        return 1

    finally:
        if conn:
            conn.close()
            logger.info("\n✓ Подключение к БД закрыто")

if __name__ == '__main__':
    exit(main())
