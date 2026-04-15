from datetime import datetime, timedelta
from api_client import get_data_for_date
from postgredb import PGDatabase

# подключение к БД
db = PGDatabase(
    host="localhost",
    database="retail",
    user="postgres",
    password="1234"
)

def clean_row(row):
    # фильтрация
    if row["quantity"] <= 0:
        return None

    if row["price_per_item"] < 0:
        return None

    # пересчет total_price
    total_price = row["quantity"] * (
        row["price_per_item"] - row["discount_per_item"]
    )

    return (
        row["client_id"],
        row["gender"],
        row["product_id"],
        row["quantity"],
        row["price_per_item"],
        row["discount_per_item"],
        total_price,
        row["purchase_datetime"],
        row["purchase_time_as_seconds_from_midnight"]
    )


def load_day(date):
    print(f"Загрузка за {date}")

    data = get_data_for_date(date)

    inserted = 0
    skipped = 0

    for row in data:
        cleaned = clean_row(row)

        if not cleaned:
            skipped += 1
            continue

        query = """
            INSERT INTO sales (
                client_id, gender, product_id,
                quantity, price_per_item,
                discount_per_item, total_price,
                purchase_datetime, purchase_time_seconds
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """

        db.post(query, cleaned)
        inserted += 1

    print(f"Загружено: {inserted}, пропущено: {skipped}")


# загрузка за вчера
yesterday = (datetime.today() - timedelta(days=1)).strftime("%Y-%m-%d")
load_day(yesterday)

def load_history(start_date, end_date):
    current = start_date

    while current <= end_date:
        load_day(current.strftime("%Y-%m-%d"))
        current += timedelta(days=1)



if __name__ == "__main__":
    import sys

    if sys.argv[1] == "daily":
        load_day(yesterday)

    elif sys.argv[1] == "history":
        load_history(
            datetime(2023, 1, 1),
            datetime(2023, 12, 31)
        )