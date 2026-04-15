import requests

BASE_URL = "http://final-project.simulative.ru/data"

def get_data_for_date(date: str):
    params = {"date": date}

    response = requests.get(BASE_URL, params=params)

    if response.status_code != 200:
        raise Exception(f"API error: {response.status_code}")

    data = response.json()

    if not data:
        print(f"Нет данных за {date}")

    return data

data = get_data_for_date("2023-01-01")
print(data[:3])