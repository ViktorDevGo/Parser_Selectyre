-- Создание таблицы selectyre_rims для дисков
DROP TABLE IF EXISTS selectyre_rims;

CREATE TABLE selectyre_rims (
    id TEXT PRIMARY KEY,
    article TEXT,
    name TEXT,
    brand TEXT,
    model TEXT,
    quantity INTEGER,
    price NUMERIC(10, 2),
    width TEXT,
    diameter TEXT,
    bolt_count TEXT,
    pcd TEXT,
    pcd2 TEXT,
    et TEXT,
    dia TEXT,
    lz2 TEXT,
    wheel_type TEXT,
    color TEXT,
    shop_length TEXT,
    shop_width TEXT,
    shop_height TEXT,
    shop_weight TEXT,
    category TEXT,
    supplier_code TEXT,
    production_year TEXT,
    sale_item TEXT,
    delivery_time TEXT,
    color_description TEXT,
    supplier_article TEXT,
    image_url TEXT,
    image_sha1 TEXT,
    product_image TEXT,
    product_image_sha1 TEXT,
    warehouse_id TEXT,
    warehouse_name TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Создание индексов для ускорения поиска
CREATE INDEX idx_rims_brand ON selectyre_rims(brand);
CREATE INDEX idx_rims_model ON selectyre_rims(model);
CREATE INDEX idx_rims_warehouse_id ON selectyre_rims(warehouse_id);
CREATE INDEX idx_rims_article ON selectyre_rims(article);
CREATE INDEX idx_rims_diameter ON selectyre_rims(diameter);
CREATE INDEX idx_rims_width ON selectyre_rims(width);
CREATE INDEX idx_rims_pcd ON selectyre_rims(pcd);
CREATE INDEX idx_rims_updated_at ON selectyre_rims(updated_at);
