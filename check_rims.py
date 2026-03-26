#!/usr/bin/env python3
"""
Скрипт для проверки импортированных данных о дисках
"""

import psycopg2
import os

DB_CONNECTION = {
    'host': 'c37e696087932476c61fd621.twc1.net',
    'port': 5432,
    'database': 'default_db',
    'user': 'gen_user',
    'password': 'Poison-79',
    'sslmode': 'verify-full',
    'sslrootcert': 'system'
}

def main():
    conn = psycopg2.connect(**DB_CONNECTION)
    cur = conn.cursor()

    print("=" * 80)
    print("СТАТИСТИКА ТАБЛИЦЫ selectyre_rims")
    print("=" * 80)

    cur.execute("SELECT COUNT(*) FROM selectyre_rims")
    total = cur.fetchone()[0]
    print(f"\nВсего записей: {total}")

    # Статистика по брендам
    cur.execute("""
        SELECT brand, COUNT(*) as count
        FROM selectyre_rims
        GROUP BY brand
        ORDER BY count DESC
        LIMIT 10
    """)
    print("\nТоп-10 брендов дисков:")
    for row in cur.fetchall():
        print(f"  {row[0]}: {row[1]} шт.")

    # Статистика по складам
    cur.execute("""
        SELECT warehouse_name, COUNT(*) as count
        FROM selectyre_rims
        GROUP BY warehouse_name
        ORDER BY count DESC
    """)
    print("\nСтатистика по складам:")
    for row in cur.fetchall():
        print(f"  {row[0]}: {row[1]} шт.")

    # Средняя цена
    cur.execute("SELECT AVG(price)::numeric(10,2) FROM selectyre_rims WHERE price > 0")
    avg_price = cur.fetchone()[0]
    print(f"\nСредняя цена: {avg_price} руб.")

    # Статистика по диаметрам
    cur.execute("""
        SELECT diameter, COUNT(*) as count
        FROM selectyre_rims
        GROUP BY diameter
        ORDER BY diameter::int
    """)
    print("\nСтатистика по диаметрам:")
    for row in cur.fetchall():
        print(f"  R{row[0]}: {row[1]} шт.")

    # Статистика по типу дисков
    cur.execute("""
        SELECT wheel_type, COUNT(*) as count
        FROM selectyre_rims
        GROUP BY wheel_type
        ORDER BY count DESC
    """)
    print("\nСтатистика по типу дисков:")
    for row in cur.fetchall():
        print(f"  {row[0]}: {row[1]} шт.")

    # Пример данных
    print("\n" + "=" * 80)
    print("ПРИМЕРЫ ДАННЫХ (первые 5 записей)")
    print("=" * 80)
    cur.execute("""
        SELECT id, brand, model, name, width, diameter, pcd, et, dia,
               quantity, price, warehouse_name
        FROM selectyre_rims
        LIMIT 5
    """)

    for row in cur.fetchall():
        print(f"\nID: {row[0]}")
        print(f"Бренд: {row[1]}")
        print(f"Модель: {row[2]}")
        print(f"Название: {row[3]}")
        print(f"Размер: {row[4]}x{row[5]}, PCD: {row[6]}, ET: {row[7]}, DIA: {row[8]}")
        print(f"Количество: {row[9]} шт.")
        print(f"Цена: {row[10]} руб.")
        print(f"Склад: {row[11]}")
        print("-" * 80)

    cur.close()
    conn.close()

if __name__ == '__main__':
    main()
