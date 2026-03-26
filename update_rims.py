#!/usr/bin/env python3
"""
Скрипт для автоматического обновления данных о дисках Selectyre
Логика UPSERT:
- Полные дубли по ID - обновляем только updated_at
- Изменившиеся записи - обновляем все поля + updated_at
- Новые записи - добавляем в таблицу
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
LOG_FILE = os.path.join(LOG_DIR, f'update_rims_{datetime.now().strftime("%Y%m%d")}.log')

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
CSV_URL = 'https://files.selectyre.ru/6aaad4d8-68b1-43cc-a238-90432d7ffa94.csv'
CSV_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'selectyre_rims.csv')
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

        file_size = os.path.getsize(CSV_FILE_NEW)
        if file_size < 1000:
            raise Exception(f"Файл слишком маленький ({file_size} байт)")

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
            cur.execute("SELECT COUNT(*) FROM selectyre_rims")
            count = cur.fetchone()[0]

            cur.execute("""
                SELECT
                    MAX(created_at) as last_created,
                    MAX(updated_at) as last_updated
                FROM selectyre_rims
            """)
            row = cur.fetchone()

        return {
            'count': count,
            'last_created': row[0] if row else None,
            'last_updated': row[1] if row else None
        }
    except:
        return {'count': 0, 'last_created': None, 'last_updated': None}

def update_table(conn):
    """Обновление данных в таблице (UPSERT логика)"""
    try:
        logger.info("Начало обновления таблицы...")

        with open(CSV_FILE_NEW, 'r', encoding=ENCODING) as f:
            new_rows_count = sum(1 for _ in f) - 1

        logger.info(f"В новом файле {new_rows_count} записей")

        with open(CSV_FILE_NEW, 'r', encoding=ENCODING) as csvfile:
            reader = csv.DictReader(csvfile, delimiter=DELIMITER)

            upsert_query = """
                INSERT INTO selectyre_rims (
                    id, article, name, brand, model, quantity, price,
                    width, diameter, bolt_count, pcd, pcd2, et, dia, lz2,
                    wheel_type, color, shop_length, shop_width, shop_height, shop_weight,
                    category, supplier_code, production_year, sale_item, delivery_time,
                    color_description, supplier_article, image_url, image_sha1,
                    product_image, product_image_sha1, warehouse_id, warehouse_name,
                    created_at, updated_at
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP
                )
                ON CONFLICT (id) DO UPDATE SET
                    article = EXCLUDED.article,
                    name = EXCLUDED.name,
                    brand = EXCLUDED.brand,
                    model = EXCLUDED.model,
                    quantity = EXCLUDED.quantity,
                    price = EXCLUDED.price,
                    width = EXCLUDED.width,
                    diameter = EXCLUDED.diameter,
                    bolt_count = EXCLUDED.bolt_count,
                    pcd = EXCLUDED.pcd,
                    pcd2 = EXCLUDED.pcd2,
                    et = EXCLUDED.et,
                    dia = EXCLUDED.dia,
                    lz2 = EXCLUDED.lz2,
                    wheel_type = EXCLUDED.wheel_type,
                    color = EXCLUDED.color,
                    shop_length = EXCLUDED.shop_length,
                    shop_width = EXCLUDED.shop_width,
                    shop_height = EXCLUDED.shop_height,
                    shop_weight = EXCLUDED.shop_weight,
                    category = EXCLUDED.category,
                    supplier_code = EXCLUDED.supplier_code,
                    production_year = EXCLUDED.production_year,
                    sale_item = EXCLUDED.sale_item,
                    delivery_time = EXCLUDED.delivery_time,
                    color_description = EXCLUDED.color_description,
                    supplier_article = EXCLUDED.supplier_article,
                    image_url = EXCLUDED.image_url,
                    image_sha1 = EXCLUDED.image_sha1,
                    product_image = EXCLUDED.product_image,
                    product_image_sha1 = EXCLUDED.product_image_sha1,
                    warehouse_id = EXCLUDED.warehouse_id,
                    warehouse_name = EXCLUDED.warehouse_name,
                    updated_at = CURRENT_TIMESTAMP
            """

            batch_data = []
            total_rows = 0

            for row in reader:
                try:
                    quantity = int(row['QUANTITY']) if row['QUANTITY'] else None
                    price = float(row['PRICE'].replace(',', '.')) if row['PRICE'] else None

                    data = (
                        row['ID'], row['ARTICLE'], row['NAME'], row['BRAND'], row['MODEL'],
                        quantity, price, row['Ширина'], row['Диаметр'],
                        row['KOL_VO_KREPEZHNYKH_OTVERSTIY'], row['PCD'], row['PCD2'],
                        row['ET'], row['DIA'], row['LZ2'], row['WHEEL_TYPE'], row['COLOR'],
                        row['SHOP_LENGTH'], row['SHOP_WIDTH'], row['SHOP_HEIGHT'], row['SHOP_WEIGHT'],
                        row['CATEGORY'], row['Код поставщика'], row['Год производства'],
                        row['Товар SALE'], row['Срок доставки'], row['Расшифровка цвета'],
                        row['Артикул поставщика'], row['Изображение ММ 1'], row['Изображение ММ 1_SHA1'],
                        row['PRODUCT_IMAGE'], row['PRODUCT_IMAGE_SHA1'],
                        row['WAREHOUSE_ID'], row['WAREHOUSE_NAME']
                    )

                    batch_data.append(data)
                    total_rows += 1

                    if len(batch_data) >= 500:
                        with conn.cursor() as cur:
                            execute_batch(cur, upsert_query, batch_data)
                            conn.commit()
                        logger.info(f"  Обработано {total_rows} строк...")
                        batch_data = []

                except Exception as e:
                    logger.warning(f"Ошибка обработки строки {total_rows + 1}: {e}")
                    continue

            if batch_data:
                with conn.cursor() as cur:
                    execute_batch(cur, upsert_query, batch_data)
                    conn.commit()

            logger.info(f"✓ Всего обработано: {total_rows} строк")

        if os.path.exists(CSV_FILE):
            os.remove(CSV_FILE)
        os.rename(CSV_FILE_NEW, CSV_FILE)

        return total_rows

    except Exception as e:
        logger.error(f"✗ Ошибка обновления таблицы: {e}")
        conn.rollback()
        raise

def get_update_statistics(conn, before_count):
    """Получение статистики обновления"""
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) FROM selectyre_rims")
            after_count = cur.fetchone()[0]

            cur.execute("""
                SELECT COUNT(*)
                FROM selectyre_rims
                WHERE DATE(updated_at) = CURRENT_DATE
            """)
            updated_today = cur.fetchone()[0]

            cur.execute("""
                SELECT COUNT(*)
                FROM selectyre_rims
                WHERE DATE(created_at) = CURRENT_DATE
            """)
            created_today = cur.fetchone()[0]

        return {
            'total_before': before_count,
            'total_after': after_count,
            'new_records': created_today,
            'updated_records': updated_today - created_today,
            'unchanged_records': after_count - updated_today
        }
    except Exception as e:
        logger.error(f"Ошибка получения статистики: {e}")
        return None

def send_notification(status, message):
    """Отправка уведомления"""
    logger.info(f"[{status}] {message}")

def main():
    """Основная функция"""
    start_time = datetime.now()
    logger.info("=" * 80)
    logger.info(f"НАЧАЛО ОБНОВЛЕНИЯ ДАННЫХ SELECTYRE RIMS (v2 - UPSERT)")
    logger.info(f"Время запуска: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("=" * 80)

    conn = None
    try:
        conn = create_connection()

        old_stats = get_current_stats(conn)
        logger.info(f"\nТекущее состояние БД:")
        logger.info(f"  Записей: {old_stats['count']}")
        logger.info(f"  Последнее создание: {old_stats['last_created']}")
        logger.info(f"  Последнее обновление: {old_stats['last_updated']}")

        if not download_csv():
            send_notification("ERROR", "Не удалось скачать новый CSV файл")
            return 1

        processed_count = update_table(conn)
        stats = get_update_statistics(conn, old_stats['count'])

        duration = (datetime.now() - start_time).total_seconds()
        logger.info("\n" + "=" * 80)
        logger.info("ОБНОВЛЕНИЕ ЗАВЕРШЕНО УСПЕШНО")
        logger.info("=" * 80)
        logger.info(f"Обработано записей из CSV: {processed_count}")

        if stats:
            logger.info(f"\nСтатистика изменений:")
            logger.info(f"  Было записей в БД: {stats['total_before']}")
            logger.info(f"  Стало записей в БД: {stats['total_after']}")
            logger.info(f"  Новых записей: {stats['new_records']}")
            logger.info(f"  Обновленных записей: {stats['updated_records']}")
            logger.info(f"  Без изменений: {stats['unchanged_records']}")

        logger.info(f"\nВремя выполнения: {duration:.2f} сек")
        logger.info("=" * 80)

        send_notification("SUCCESS", f"Обработано {processed_count} записей за {duration:.2f} сек")

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
