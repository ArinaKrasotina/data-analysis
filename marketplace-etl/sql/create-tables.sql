DROP TABLE IF EXISTS sales;

CREATE TABLE sales (
    id SERIAL PRIMARY KEY,
    client_id BIGINT,
    gender CHAR(1),
    product_id BIGINT,
    quantity INTEGER,
    price_per_item NUMERIC,
    discount_per_item NUMERIC,
    total_price NUMERIC,
    purchase_datetime DATE,
    purchase_time_seconds INTEGER
);

CREATE INDEX idx_sales_date ON sales(purchase_datetime);
CREATE INDEX idx_sales_client ON sales(client_id);
CREATE INDEX idx_sales_product ON sales(product_id);