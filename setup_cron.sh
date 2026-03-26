#!/bin/bash
#
# Скрипт для настройки автоматического обновления данных каждые 4 часа
#

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
UPDATE_SCRIPT="$SCRIPT_DIR/update_data.py"
PYTHON_PATH=$(which python3)

echo "======================================"
echo "Настройка автоматического обновления"
echo "======================================"
echo ""
echo "Директория проекта: $SCRIPT_DIR"
echo "Скрипт обновления: $UPDATE_SCRIPT"
echo "Python: $PYTHON_PATH"
echo ""

# Проверка Python
if [ ! -f "$PYTHON_PATH" ]; then
    echo "✗ Python3 не найден!"
    exit 1
fi

# Проверка скрипта обновления
if [ ! -f "$UPDATE_SCRIPT" ]; then
    echo "✗ Скрипт update_data.py не найден!"
    exit 1
fi

# Делаем скрипт исполняемым
chmod +x "$UPDATE_SCRIPT"
echo "✓ Права на выполнение установлены"

# Создание директории для логов
mkdir -p "$SCRIPT_DIR/logs"
echo "✓ Директория для логов создана"

# Настройка cron
CRON_COMMAND="0 */4 * * * $PYTHON_PATH $UPDATE_SCRIPT >> $SCRIPT_DIR/logs/cron.log 2>&1"

echo ""
echo "======================================"
echo "Настройка cron"
echo "======================================"
echo ""
echo "Будет добавлена следующая задача:"
echo "$CRON_COMMAND"
echo ""
echo "Это означает: обновление каждые 4 часа (в 00:00, 04:00, 08:00, 12:00, 16:00, 20:00)"
echo ""

# Проверка существующих задач cron
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

    # Удаление старой задачи
    crontab -l 2>/dev/null | grep -v -F "$UPDATE_SCRIPT" | crontab -
    echo "✓ Старая задача удалена"
fi

# Добавление новой задачи
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

# Тестовый запуск
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
echo "Автоматическое обновление настроено."
echo ""
echo "Полезные команды:"
echo "  - Просмотр задач cron:      crontab -l"
echo "  - Редактирование cron:      crontab -e"
echo "  - Удаление всех задач:      crontab -r"
echo "  - Просмотр логов:           tail -f $SCRIPT_DIR/logs/cron.log"
echo "  - Ручной запуск обновления: python3 $UPDATE_SCRIPT"
echo ""
echo "Расписание обновлений:"
echo "  00:00, 04:00, 08:00, 12:00, 16:00, 20:00 (каждый день)"
echo ""
