#!/usr/bin/env python3
"""
Объединенный скрипт для обновления данных о шинах и дисках Selectyre
Запускает оба обновления последовательно
"""

import subprocess
import sys
from datetime import datetime
import logging
import os

# Настройка логирования
LOG_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logs')
os.makedirs(LOG_DIR, exist_ok=True)
LOG_FILE = os.path.join(LOG_DIR, f'update_all_{datetime.now().strftime("%Y%m%d")}.log')

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE, encoding='utf-8'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def run_script(script_name, description):
    """Запуск скрипта обновления"""
    logger.info(f"\n{'=' * 80}")
    logger.info(f"Запуск: {description}")
    logger.info(f"{'=' * 80}\n")

    try:
        result = subprocess.run(
            ['python3', script_name],
            capture_output=True,
            text=True,
            timeout=600
        )

        # Вывод результата
        if result.stdout:
            for line in result.stdout.split('\n'):
                if line.strip():
                    logger.info(line)

        if result.stderr:
            for line in result.stderr.split('\n'):
                if line.strip():
                    logger.error(line)

        if result.returncode == 0:
            logger.info(f"✓ {description} завершено успешно")
            return True
        else:
            logger.error(f"✗ {description} завершилось с ошибкой (код: {result.returncode})")
            return False

    except subprocess.TimeoutExpired:
        logger.error(f"✗ {description} превысило лимит времени")
        return False
    except Exception as e:
        logger.error(f"✗ Ошибка при запуске {description}: {e}")
        return False

def main():
    """Основная функция"""
    start_time = datetime.now()

    logger.info("\n" + "=" * 80)
    logger.info("НАЧАЛО ОБНОВЛЕНИЯ ВСЕХ ДАННЫХ SELECTYRE")
    logger.info(f"Время запуска: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("=" * 80)

    results = {}

    # Обновление шин
    results['tires'] = run_script('update_data.py', 'Обновление данных о шинах')

    # Обновление дисков
    results['rims'] = run_script('update_rims.py', 'Обновление данных о дисках')

    # Итоги
    duration = (datetime.now() - start_time).total_seconds()

    logger.info("\n" + "=" * 80)
    logger.info("ИТОГОВАЯ СТАТИСТИКА")
    logger.info("=" * 80)
    logger.info(f"Шины (Tires):  {'✓ Успешно' if results['tires'] else '✗ Ошибка'}")
    logger.info(f"Диски (Rims):  {'✓ Успешно' if results['rims'] else '✗ Ошибка'}")
    logger.info(f"Общее время:   {duration:.2f} сек")
    logger.info("=" * 80)

    # Возврат кода ошибки если хотя бы одно обновление не удалось
    if not all(results.values()):
        logger.error("\n⚠ Некоторые обновления завершились с ошибками!")
        return 1

    logger.info("\n✓ Все обновления завершены успешно!")
    return 0

if __name__ == '__main__':
    exit(main())
