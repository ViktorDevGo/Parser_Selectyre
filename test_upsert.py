#!/usr/bin/env python3
"""
Скрипт для тестирования UPSERT логики
"""

import psycopg2
import os
from datetime import datetime

DB_CONNECTION = {
    'host': 'c37e696087932476c61fd621.twc1.net',
    'port': 5432,
    'database': 'default_db',
    'user': 'gen_user',
    'password': 'Poison-79',
    'sslmode': 'require'
}

def main():
    conn = psycopg2.connect(**DB_CONNECTION)
    cur = conn.cursor()

    print("=" * 80)
    print("ПРОВЕРКА UPSERT ЛОГИКИ")
    print("=" * 80)

    # Проверка структуры таблицы
    cur.execute("""
        SELECT column_name, data_type
        FROM information_schema.columns
        WHERE table_name = 'selectyre_tyer'
        AND column_name IN ('id', 'created_at', 'updated_at')
        ORDER BY ordinal_position
    """)
    print("\nПоля для отслеживания:")
    for row in cur.fetchall():
        print(f"  {row[0]}: {row[1]}")

    # Общая статистика
    cur.execute("SELECT COUNT(*) FROM Selectyre_tyer")
    total = cur.fetchone()[0]
    print(f"\nВсего записей в БД: {total}")

    # Записи созданные сегодня
    cur.execute("""
        SELECT COUNT(*)
        FROM Selectyre_tyer
        WHERE DATE(created_at) = CURRENT_DATE
    """)
    created_today = cur.fetchone()[0]
    print(f"Созданных сегодня: {created_today}")

    # Записи обновленные сегодня
    cur.execute("""
        SELECT COUNT(*)
        FROM Selectyre_tyer
        WHERE DATE(updated_at) = CURRENT_DATE
    """)
    updated_today = cur.fetchone()[0]
    print(f"Обновленных сегодня: {updated_today}")

    # Записи где created_at != updated_at (были обновлены после создания)
    cur.execute("""
        SELECT COUNT(*)
        FROM Selectyre_tyer
        WHERE created_at != updated_at
    """)
    modified = cur.fetchone()[0]
    print(f"Изменявшихся после создания: {modified}")

    # Примеры записей
    print("\n" + "=" * 80)
    print("ПРИМЕРЫ ЗАПИСЕЙ (5 последних обновленных)")
    print("=" * 80)

    cur.execute("""
        SELECT id, brand, model, price, quantity,
               created_at, updated_at,
               (updated_at - created_at) as time_diff
        FROM Selectyre_tyer
        ORDER BY updated_at DESC
        LIMIT 5
    """)

    for row in cur.fetchall():
        print(f"\nID: {row[0]}")
        print(f"Бренд: {row[1]}, Модель: {row[2]}")
        print(f"Цена: {row[3]}, Количество: {row[4]}")
        print(f"Создан: {row[5]}")
        print(f"Обновлен: {row[6]}")
        print(f"Разница: {row[7]}")
        print("-" * 80)

    # Статистика по датам
    print("\n" + "=" * 80)
    print("РАСПРЕДЕЛЕНИЕ ПО ДАТАМ СОЗДАНИЯ")
    print("=" * 80)

    cur.execute("""
        SELECT DATE(created_at) as date, COUNT(*) as count
        FROM Selectyre_tyer
        GROUP BY DATE(created_at)
        ORDER BY date DESC
        LIMIT 10
    """)

    for row in cur.fetchall():
        print(f"{row[0]}: {row[1]} записей")

    cur.close()
    conn.close()

if __name__ == '__main__':
    main()
