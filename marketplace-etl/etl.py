from datetime import datetime, timedelta
from api_client import get_data_for_date
import psycopg2
from psycopg2.extras import RealDictCursor

# Подключение к БД
conn = psycopg2.connect(
    host="localhost",
    database="marketplace",
    user="analyst",
    password="password"
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

    # используем курсор
    with conn.cursor() as cur:
        for row in data:
            cleaned = clean_row(row)

            if not cleaned:
                skipped += 1
                continue

            query = """
                INSERT INTO sales (
                    client_id,
                    gender,
                    product_id,
                    quantity,
                    price_per_item,
                    discount_per_item,
                    total_price,
                    purchase_datetime,
                    purchase_time_seconds
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """

            cur.execute(query, cleaned)
            inserted += 1

    conn.commit()
    print(f"Загружено: {inserted}, пропущено: {skipped}")


# Загрузка за вчера
yesterday = (datetime.today()).date()
load_day(yesterday.strftime("%Y-%m-%d"))


def load_history(start_date, end_date):
    current = start_date

    while current <= end_date:
        load_day(current.strftime("%Y-%m-%d"))
        current += timedelta(days=1)


if __name__ == "__main__":
    import sys

    if sys.argv[1] == "daily":
        load_day(yesterday.strftime("%Y-%m-%d"))

    elif sys.argv[1] == "history":
        load_history(
            datetime(2023, 1, 1),
            datetime(2023, 12, 31)
        )