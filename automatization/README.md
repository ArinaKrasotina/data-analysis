# Retail Sales Automation (Python)

Учебный проект по автоматизации обработки кассовых CSV-выгрузок и загрузки данных в PostgreSQL.

## Описание

Проект эмулирует работу кассового ПО в торговой сети:
- ежедневно (кроме воскресенья) генерируются CSV-файлы с продажами;
- данные автоматически загружаются в базу данных PostgreSQL;
- лишние файлы в папке игнорируются;
- после загрузки файлы удаляются.

## Структура проекта

```
automatization/
├── generate-data.py
├── load-to-db.py
├── postgredb.py
├── config.ini
├── requirements.txt
├── start.bat
├── data/
├── sql/
│   └── create-tables.sql
├── img/
└── README.md
```

## Формат данных (CSV)

Имя файла:
```
{shop_num}_{cash_num}.csv
```

Поля:
- doc_id
- item
- category
- amount
- price
- discount
- sale_date

## Требования

- Python 3.10+
- PostgreSQL

## Установка и запуск

```bash
git clone <repo_url>
cd automatization
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

Создать таблицы:
```sql
sql/create-tables.sql
```

Запуск:
```bash
python generate-data.py
python load-to-db.py
```

или:
```bat
start.bat
```

## Автоматизация

Скрипты запускаются ежедневно (кроме воскресенья) через Windows Task Scheduler.

## База данных

Используется PostgreSQL, таблица `sales` создаётся через DDL-скрипт.

## Назначение проекта

Итоговый учебный проект по автоматизации обработки данных на Python.
