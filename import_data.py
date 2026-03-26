#!/usr/bin/env python3
"""
Скрипт для импорта данных из CSV в PostgreSQL
"""

import csv
import psycopg2
from psycopg2.extras import execute_batch
import os

# Параметры подключения к БД
DB_CONNECTION = {
    'host': 'c37e696087932476c61fd621.twc1.net',
    'port': 5432,
    'database': 'default_db',
    'user': 'gen_user',
    'password': 'Poison-79',
    'sslmode': 'verify-full',
    'sslrootcert': os.path.expanduser('~/.cloud-certs/root.crt')
}

CSV_FILE = 'selectyre_data.csv'
ENCODING = 'windows-1251'
DELIMITER = ';'

def create_connection():
    """Создание подключения к БД"""
    try:
        conn = psycopg2.connect(**DB_CONNECTION)
        print("✓ Подключение к БД успешно установлено")
        return conn
    except Exception as e:
        print(f"✗ Ошибка подключения к БД: {e}")
        raise

def create_table(conn):
    """Создание таблицы"""
    try:
        with open('create_table.sql', 'r', encoding='utf-8') as f:
            sql = f.read()

        with conn.cursor() as cur:
            cur.execute(sql)
            conn.commit()
        print("✓ Таблица успешно создана")
    except Exception as e:
        print(f"✗ Ошибка создания таблицы: {e}")
        conn.rollback()
        raise

def import_csv(conn):
    """Импорт данных из CSV"""
    try:
        with open(CSV_FILE, 'r', encoding=ENCODING) as csvfile:
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
                # Преобразование данных
                quantity = int(row['QUANTITY']) if row['QUANTITY'] else None
                price = float(row['PRICE'].replace(',', '.')) if row['PRICE'] else None

                data = (
                    row['ID'],
                    row['ARTICLE'],
                    row['NAME'],
                    row['BRAND'],
                    row['MODEL'],
                    quantity,
                    price,
                    row['Сезон'],
                    row['Тип ТС'],
                    row['Ширина'],
                    row['Профиль'],
                    row['Диаметр'],
                    row['Индекс нагрузки'],
                    row['Индекс скорости'],
                    row['Тип усиленности'],
                    row['Шипованность'],
                    row['Run on Flat'],
                    row['Омологация'],
                    row['Защита диска'],
                    row['Надпись на боковине'],
                    row['SHOP_LENGTH'],
                    row['SHOP_WIDTH'],
                    row['SHOP_HEIGHT'],
                    row['SHOP_WEIGHT'],
                    row['Код поставщика'],
                    row['Год производства'],
                    row['Товар SALE'],
                    row['Cрок доставки'],
                    row['APPLYING'],
                    row['AXLE'],
                    row['LAYERING'],
                    row['STUDDABLE'],
                    row['Артикул поставщика'],
                    row['Изображение ММ 1'],
                    row['Изображение ММ 1_SHA1'],
                    row['WAREHOUSE_ID'],
                    row['WAREHOUSE_NAME']
                )

                batch_data.append(data)
                total_rows += 1

                # Вставка пачками по 1000 записей
                if len(batch_data) >= 1000:
                    with conn.cursor() as cur:
                        execute_batch(cur, insert_query, batch_data)
                        conn.commit()
                    print(f"✓ Импортировано {total_rows} строк...")
                    batch_data = []

            # Вставка оставшихся записей
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
    """Основная функция"""
    print("Начало импорта данных Selectyre в PostgreSQL\n")

    conn = None
    try:
        # Подключение к БД
        conn = create_connection()

        # Создание таблицы
        print("\nСоздание таблицы...")
        create_table(conn)

        # Импорт данных
        print("\nИмпорт данных из CSV...")
        import_csv(conn)

        # Проверка результата
        with conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) FROM Selectyre_tyer")
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
