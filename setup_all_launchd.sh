#!/bin/bash
#
# Скрипт для настройки автоматического обновления ВСЕХ данных (шины + диски)
# через launchd (для macOS) каждые 4 часа
#

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
UPDATE_SCRIPT="$SCRIPT_DIR/update_all.py"
PYTHON_PATH=$(which python3)
PLIST_FILENAME="com.selectyre.parser.updateall.plist"
PLIST_PATH="$HOME/Library/LaunchAgents/$PLIST_FILENAME"

echo "======================================"
echo "Настройка автоматического обновления ВСЕХ данных (macOS launchd)"
echo "======================================"
echo ""

mkdir -p "$HOME/Library/LaunchAgents"
mkdir -p "$SCRIPT_DIR/logs"

# Создание plist файла
cat > "$PLIST_PATH" <<EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.selectyre.parser.updateall</string>

    <key>ProgramArguments</key>
    <array>
        <string>$PYTHON_PATH</string>
        <string>$UPDATE_SCRIPT</string>
    </array>

    <key>StartInterval</key>
    <integer>14400</integer>

    <key>RunAtLoad</key>
    <false/>

    <key>StandardOutPath</key>
    <string>$SCRIPT_DIR/logs/launchd_all.out.log</string>

    <key>StandardErrorPath</key>
    <string>$SCRIPT_DIR/logs/launchd_all.err.log</string>

    <key>WorkingDirectory</key>
    <string>$SCRIPT_DIR</string>

    <key>EnvironmentVariables</key>
    <dict>
        <key>PATH</key>
        <string>/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin</string>
    </dict>
</dict>
</plist>
EOF

echo "✓ Файл конфигурации создан: $PLIST_PATH"
echo ""

chmod 644 "$PLIST_PATH"
chmod +x "$UPDATE_SCRIPT"

echo "✓ Права установлены"
echo ""

# Выгрузка старого задания если существует
launchctl unload "$PLIST_PATH" 2>/dev/null

# Загрузка нового задания
launchctl load "$PLIST_PATH"

if [ $? -eq 0 ]; then
    echo "✓ Задание успешно загружено в launchd"
else
    echo "✗ Ошибка загрузки задания"
    exit 1
fi

echo ""
echo "======================================"
echo "Информация о задании"
echo "======================================"
echo ""
echo "Label: com.selectyre.parser.updateall"
echo "Интервал: каждые 14400 секунд (4 часа)"
echo "Обновляет: Шины (tires) + Диски (rims)"
echo "Скрипт: $UPDATE_SCRIPT"
echo "Логи: $SCRIPT_DIR/logs/"
echo ""

echo "Проверка статуса задания:"
launchctl list | grep com.selectyre.parser.updateall

echo ""
echo "======================================"
echo "Полезные команды"
echo "======================================"
echo ""
echo "Управление заданием:"
echo "  launchctl list | grep selectyre"
echo "  launchctl start com.selectyre.parser.updateall"
echo "  launchctl stop com.selectyre.parser.updateall"
echo "  launchctl unload $PLIST_PATH"
echo ""
echo "Просмотр логов:"
echo "  tail -f $SCRIPT_DIR/logs/update_all_\$(date +%Y%m%d).log"
echo "  tail -f $SCRIPT_DIR/logs/launchd_all.out.log"
echo ""

read -p "Выполнить тестовый запуск сейчас? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo ""
    echo "Запуск обновления через launchd..."
    launchctl start com.selectyre.parser.updateall
    sleep 2
    echo ""
    echo "Проверьте логи:"
    echo "  tail -f $SCRIPT_DIR/logs/launchd_all.out.log"
fi

echo ""
echo "✓ Готово! Автоматическое обновление ВСЕХ данных настроено."
echo ""
