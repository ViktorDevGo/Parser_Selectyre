-- Создание таблицы Selectyre_tyer
DROP TABLE IF EXISTS Selectyre_tyer;

CREATE TABLE Selectyre_tyer (
    id TEXT PRIMARY KEY,
    article TEXT,
    name TEXT,
    brand TEXT,
    model TEXT,
    quantity INTEGER,
    price NUMERIC(10, 2),
    season TEXT,
    vehicle_type TEXT,
    width TEXT,
    profile TEXT,
    diameter TEXT,
    load_index TEXT,
    speed_index TEXT,
    reinforcement_type TEXT,
    studded TEXT,
    run_on_flat TEXT,
    homologation TEXT,
    rim_protection TEXT,
    sidewall_text TEXT,
    shop_length TEXT,
    shop_width TEXT,
    shop_height TEXT,
    shop_weight TEXT,
    supplier_code TEXT,
    production_year TEXT,
    sale_item TEXT,
    delivery_time TEXT,
    applying TEXT,
    axle TEXT,
    layering TEXT,
    studdable TEXT,
    supplier_article TEXT,
    image_url TEXT,
    image_sha1 TEXT,
    warehouse_id TEXT,
    warehouse_name TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Создание индексов для ускорения поиска
CREATE INDEX idx_brand ON Selectyre_tyer(brand);
CREATE INDEX idx_model ON Selectyre_tyer(model);
CREATE INDEX idx_warehouse_id ON Selectyre_tyer(warehouse_id);
CREATE INDEX idx_article ON Selectyre_tyer(article);
