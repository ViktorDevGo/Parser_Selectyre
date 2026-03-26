#!/usr/bin/env python3
"""
Скрипт для проверки импортированных данных
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
    'sslrootcert': os.path.expanduser('~/.cloud-certs/root.crt')
}

def main():
    conn = psycopg2.connect(**DB_CONNECTION)
    cur = conn.cursor()

    # Общая статистика
    print("=" * 80)
    print("СТАТИСТИКА ТАБЛИЦЫ Selectyre_tyer")
    print("=" * 80)

    cur.execute("SELECT COUNT(*) FROM Selectyre_tyer")
    total = cur.fetchone()[0]
    print(f"\nВсего записей: {total}")

    # Статистика по брендам
    cur.execute("""
        SELECT brand, COUNT(*) as count
        FROM Selectyre_tyer
        GROUP BY brand
        ORDER BY count DESC
        LIMIT 10
    """)
    print("\nТоп-10 брендов:")
    for row in cur.fetchall():
        print(f"  {row[0]}: {row[1]} шт.")

    # Статистика по складам
    cur.execute("""
        SELECT warehouse_name, COUNT(*) as count
        FROM Selectyre_tyer
        GROUP BY warehouse_name
        ORDER BY count DESC
    """)
    print("\nСтатистика по складам:")
    for row in cur.fetchall():
        print(f"  {row[0]}: {row[1]} шт.")

    # Средняя цена
    cur.execute("SELECT AVG(price)::numeric(10,2) FROM Selectyre_tyer WHERE price > 0")
    avg_price = cur.fetchone()[0]
    print(f"\nСредняя цена: {avg_price} руб.")

    # Пример данных
    print("\n" + "=" * 80)
    print("ПРИМЕРЫ ДАННЫХ (первые 5 записей)")
    print("=" * 80)
    cur.execute("""
        SELECT id, brand, model, name, quantity, price, warehouse_name
        FROM Selectyre_tyer
        LIMIT 5
    """)

    for row in cur.fetchall():
        print(f"\nID: {row[0]}")
        print(f"Бренд: {row[1]}")
        print(f"Модель: {row[2]}")
        print(f"Название: {row[3]}")
        print(f"Количество: {row[4]} шт.")
        print(f"Цена: {row[5]} руб.")
        print(f"Склад: {row[6]}")
        print("-" * 80)

    cur.close()
    conn.close()

if __name__ == '__main__':
    main()
