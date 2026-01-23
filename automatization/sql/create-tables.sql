-- sql/create-table.sql
DROP TABLE IF EXISTS sales;

CREATE TABLE sales (
    id SERIAL PRIMARY KEY,
    doc_id VARCHAR(32) NOT NULL,
    item VARCHAR(255) NOT NULL,
    category VARCHAR(255) NOT NULL,
    amount INTEGER NOT NULL CHECK (amount > 0),
    price NUMERIC(10, 2) NOT NULL CHECK (price >= 0),
    discount NUMERIC(10, 2) NOT NULL CHECK (discount >= 0),
    sale_date DATE NOT NULL,
    -- скидка не может превышать стоимость товара
    CONSTRAINT valid_discount CHECK (discount <= price * amount)
);

-- индексы для ускорения запросов
CREATE INDEX idx_sales_doc_id ON sales(doc_id);
CREATE INDEX idx_sales_category ON sales(category);
CREATE INDEX idx_sales_sale_date ON sales(sale_date);