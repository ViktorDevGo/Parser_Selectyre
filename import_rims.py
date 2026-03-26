#!/usr/bin/env python3
"""
Скрипт для первичного импорта данных о дисках из CSV в PostgreSQL
"""

import csv
import psycopg2
from psycopg2.extras import execute_batch
import os

DB_CONNECTION = {
    'host': 'c37e696087932476c61fd621.twc1.net',
    'port': 5432,
    'database': 'default_db',
    'user': 'gen_user',
    'password': 'Poison-79',
    'sslmode': 'verify-full',
    'sslrootcert': os.path.expanduser('~/.cloud-certs/root.crt')
}

CSV_FILE = 'selectyre_rims.csv'
ENCODING = 'windows-1251'
DELIMITER = ';'

def create_connection():
    try:
        conn = psycopg2.connect(**DB_CONNECTION)
        print("✓ Подключение к БД успешно установлено")
        return conn
    except Exception as e:
        print(f"✗ Ошибка подключения к БД: {e}")
        raise

def create_table(conn):
    try:
        with open('create_table_rims.sql', 'r', encoding='utf-8') as f:
            sql = f.read()

        with conn.cursor() as cur:
            cur.execute(sql)
            conn.commit()
        print("✓ Таблица selectyre_rims успешно создана")
    except Exception as e:
        print(f"✗ Ошибка создания таблицы: {e}")
        conn.rollback()
        raise

def import_csv(conn):
    try:
        with open(CSV_FILE, 'r', encoding=ENCODING) as csvfile:
            reader = csv.DictReader(csvfile, delimiter=DELIMITER)

            insert_query = """
                INSERT INTO selectyre_rims (
                    id, article, name, brand, model, quantity, price,
                    width, diameter, bolt_count, pcd, pcd2, et, dia, lz2,
                    wheel_type, color, shop_length, shop_width, shop_height, shop_weight,
                    category, supplier_code, production_year, sale_item, delivery_time,
                    color_description, supplier_article, image_url, image_sha1,
                    product_image, product_image_sha1, warehouse_id, warehouse_name
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                    %s, %s, %s, %s
                )
            """

            batch_data = []
            total_rows = 0

            for row in reader:
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

                if len(batch_data) >= 1000:
                    with conn.cursor() as cur:
                        execute_batch(cur, insert_query, batch_data)
                        conn.commit()
                    print(f"✓ Импортировано {total_rows} строк...")
                    batch_data = []

            if batch_data:
                with conn.cursor() as cur:
                    execute_batch(cur, insert_query, batch_data)
                    conn.commit()

            print(f"✓ Всего импортировано: {total_rows} строк")

    except Exception as e:
        print(f"✗ Ошибка импорта данных: {e}")
        conn.rollback()
        raise

def main():
    print("Начало импорта данных о дисках (Selectyre Rims) в PostgreSQL\n")

    conn = None
    try:
        conn = create_connection()

        print("\nСоздание таблицы...")
        create_table(conn)

        print("\nИмпорт данных из CSV...")
        import_csv(conn)

        with conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) FROM selectyre_rims")
            count = cur.fetchone()[0]
            print(f"\n✓ Импорт завершен успешно!")
            print(f"  Количество записей в таблице: {count}")

    except Exception as e:
        print(f"\n✗ Ошибка: {e}")
        return 1
    finally:
        if conn:
            conn.close()
            print("\n✓ Подключение к БД закрыто")

    return 0

if __name__ == '__main__':
    exit(main())
