-- Добавление поля updated_at для отслеживания последнего обновления
ALTER TABLE Selectyre_tyer
ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP;

-- Обновление существующих записей
UPDATE Selectyre_tyer
SET updated_at = created_at
WHERE updated_at IS NULL;

-- Создание индекса для updated_at
CREATE INDEX IF NOT EXISTS idx_updated_at ON Selectyre_tyer(updated_at);
