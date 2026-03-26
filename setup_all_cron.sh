#!/bin/bash
#
# Скрипт для настройки автоматического обновления ВСЕХ данных (шины + диски)
# через cron каждые 4 часа
#

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
UPDATE_SCRIPT="$SCRIPT_DIR/update_all.py"
PYTHON_PATH=$(which python3)

echo "======================================"
echo "Настройка автоматического обновления ВСЕХ данных"
echo "======================================"
echo ""
echo "Директория проекта: $SCRIPT_DIR"
echo "Скрипт обновления: $UPDATE_SCRIPT"
echo "Python: $PYTHON_PATH"
echo ""

if [ ! -f "$PYTHON_PATH" ]; then
    echo "✗ Python3 не найден!"
    exit 1
fi

if [ ! -f "$UPDATE_SCRIPT" ]; then
    echo "✗ Скрипт update_all.py не найден!"
    exit 1
fi

chmod +x "$UPDATE_SCRIPT"
echo "✓ Права на выполнение установлены"

mkdir -p "$SCRIPT_DIR/logs"
echo "✓ Директория для логов создана"

CRON_COMMAND="0 */4 * * * $PYTHON_PATH $UPDATE_SCRIPT >> $SCRIPT_DIR/logs/cron_all.log 2>&1"

echo ""
echo "======================================"
echo "Настройка cron"
echo "======================================"
echo ""
echo "Будет добавлена следующая задача:"
echo "$CRON_COMMAND"
echo ""
echo "Обновление каждые 4 часа (00:00, 04:00, 08:00, 12:00, 16:00, 20:00)"
echo "Обновляет: Шины (tires) + Диски (rims)"
echo ""

EXISTING_CRON=$(crontab -l 2>/dev/null | grep -F "$UPDATE_SCRIPT" || true)

if [ -n "$EXISTING_CRON" ]; then
    echo "⚠ Найдена существующая задача cron:"
    echo "$EXISTING_CRON"
    echo ""
    read -p "Удалить старую и создать новую? (y/n): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Отменено пользователем"
        exit 0
    fi

    crontab -l 2>/dev/null | grep -v -F "$UPDATE_SCRIPT" | crontab -
    echo "✓ Старая задача удалена"
fi

(crontab -l 2>/dev/null; echo "$CRON_COMMAND") | crontab -

if [ $? -eq 0 ]; then
    echo "✓ Задача cron успешно добавлена"
else
    echo "✗ Ошибка добавления задачи cron"
    exit 1
fi

echo ""
echo "======================================"
echo "Проверка установки"
echo "======================================"
echo ""
crontab -l | grep -F "$UPDATE_SCRIPT"
echo ""

echo "======================================"
echo "Тестовый запуск"
echo "======================================"
echo ""
read -p "Выполнить тестовый запуск сейчас? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo ""
    echo "Запуск обновления..."
    echo ""
    $PYTHON_PATH "$UPDATE_SCRIPT"
    echo ""
    echo "✓ Тестовый запуск завершен"
    echo ""
    echo "Проверьте логи в: $SCRIPT_DIR/logs/"
fi

echo ""
echo "======================================"
echo "Готово!"
echo "======================================"
echo ""
echo "Автоматическое обновление ВСЕХ данных настроено."
echo ""
echo "Полезные команды:"
echo "  - Просмотр задач cron:      crontab -l"
echo "  - Просмотр логов:           tail -f $SCRIPT_DIR/logs/update_all_\$(date +%Y%m%d).log"
echo "  - Ручной запуск обновления: python3 $UPDATE_SCRIPT"
echo ""
