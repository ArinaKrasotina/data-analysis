# Auto-n-deploy: Retail Data Pipeline

Проект для автоматизации обработки данных продаж торговой сети.

## Структура проекта

```
auto-n-deploy/
├── generate-data.py          # Генератор CSV файлов (Пн–Сб)
├── load-to-db.py             # Загрузчик в PostgreSQL
├── postgredb.py              # Класс для работы с БД
├── config.ini                # Конфигурация подключения
├── requirements.txt          # Зависимости Python
├── README.md                 # Документация проекта
├── data/                     # CSV файлы
│   └── {shop}_{cash}.csv     # Пример: 1_1.csv, 2_3.csv
├── sql/
│   └── create-table.sql      # DDL таблицы sales
└── img/                      # Скриншоты отчётов
```

## Быстрая установка

### 1. Установка PostgreSQL и создание БД

```bash
psql -U postgres -c "CREATE DATABASE retail;"
```

### 2. Настройка проекта

```bash
git clone <репозиторий>
cd auto-n-deploy
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Настройка `config.ini`

```ini
[Database]
HOST = localhost
DATABASE = retail
USER = postgres
PASSWORD = ваш_пароль
```

### 4. Создание таблицы

```bash
psql -U postgres -d retail -f sql\create-table.sql
```

## Использование

### Ручной запуск

```bash
# Генерация данных (только Пн–Сб)
python generate-data.py

# Загрузка данных в БД
python load-to-db.py
```

### Автоматизация (Планировщик заданий Windows)

1. **Retail Data Generator** — ежедневно в 00:01 (Пн–Сб)
2. **Retail Data Loader** — ежедневно в 00:06 (Пн–Сб)

## Формат данных

### CSV файлы

- Имя файла: `{номер_магазина}_{номер_кассы}.csv`
- Пример: `1_1.csv`, `2_3.csv`
- Колонки:
  - `doc_id`
  - `item`
  - `category`
  - `amount`
  - `price`
  - `discount`
  - `sale_date`

### Таблица `sales`

```sql
CREATE TABLE sales (
    id SERIAL PRIMARY KEY,
    doc_id VARCHAR(32) NOT NULL,
    item VARCHAR(255) NOT NULL,
    category VARCHAR(255) NOT NULL,
    amount INTEGER CHECK (amount > 0),
    price NUMERIC(10,2) CHECK (price >= 0),
    discount NUMERIC(10,2) CHECK (discount >= 0),
    sale_date DATE NOT NULL,
    CHECK (discount <= price * amount)
);
```

## Проверка работы

```sql
SELECT COUNT(*) FROM sales;

SELECT sale_date, COUNT(*)
FROM sales
GROUP BY sale_date;

SELECT COUNT(*)
FROM sales
WHERE discount > price * amount;
```

## Примечания

- Данные генерируются за предыдущий день
- Воскресенье — выходной день, данные не создаются
- CSV файлы удаляются после успешной загрузки в БД
- Обрабатываются только файлы, соответствующие шаблону `\d+_\d+\.csv`

---

Проект готов к использованию. Для автоматизации используйте Планировщик заданий Windows.
