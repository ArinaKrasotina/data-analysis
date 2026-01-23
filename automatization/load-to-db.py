import configparser
import os
import re
import pandas as pd
from postgredb import PGDatabase

# чтение файла конфигураций
dirname = os.path.dirname(__file__)

config = configparser.ConfigParser()
config.read(os.path.join(dirname, "config.ini"), encoding="utf-8")

DATA_DIR = os.path.join(dirname, config["Files"]["DATA_DIR"])

# Преобразуем SectionProxy в обычный словарь
DB_CREDS = {
    "HOST": str(config["Database"]["HOST"]).strip(),
    "DATABASE": str(config["Database"]["DATABASE"]).strip(),
    "USER": str(config["Database"]["USER"]).strip(),
    "PASSWORD": str(config["Database"]["PASSWORD"]).strip(),
    "PORT": 5432
}

# подключение к бд
database = PGDatabase(
    host=DB_CREDS["HOST"],
    database=DB_CREDS["DATABASE"],
    user=DB_CREDS["USER"],
    password=DB_CREDS["PASSWORD"],
    port=DB_CREDS["PORT"]
)

# проверка имени файла
filename_pattern = re.compile(r"^\d+_\d+\.csv$")

# обработка файлов
processed_files = 0
total_rows = 0
csv_files = []

# собираем все CSV файлы
for filename in os.listdir(DATA_DIR):
    if filename_pattern.match(filename):
        csv_files.append(filename)

if not csv_files:
    print("Нет CSV файлов для обработки.")
    exit(0)

# обрабатываем каждый файл
for filename in csv_files:
    file_path = os.path.join(DATA_DIR, filename)
    
    try:
        df = pd.read_csv(file_path, encoding='utf-8')
    except Exception as err:
        print(f"Ошибка чтения {filename}: {err}")
        continue

    # проверяем наличие нужных колонок
    expected_columns = {
        "doc_id", "item", "category", "amount", "price", "discount", "sale_date"
    }

    if not expected_columns.issubset(df.columns):
        print(f"Неверный формат файла {filename}")
        continue

    # вставка данных
    inserted = 0
    errors = 0
    
    for _, row in df.iterrows():
        query = """
            INSERT INTO sales (doc_id, item, category, amount, price, discount, sale_date)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        
        try:
            database.post(
                query,
                (
                    str(row["doc_id"]),
                    str(row["item"]),
                    str(row["category"]),
                    int(row["amount"]),
                    float(row["price"]),
                    float(row["discount"]),
                    str(row["sale_date"])
                )
            )
            inserted += 1
        except Exception:
            errors += 1
    
    # удаляем файл после загрузки
    try:
        os.remove(file_path)
        processed_files += 1
        total_rows += inserted
    except Exception:
        pass  # игнорируем ошибку удаления

# финальный вывод
print(f"ОБРАБОТКА ЗАВЕРШЕНА")
print(f"Файлов обработано: {processed_files}")
print(f"Записей загружено: {total_rows}")