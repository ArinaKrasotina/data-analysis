import configparser
import os
import random
import string
from datetime import datetime, timedelta
import pandas as pd

# чтение файла конфигураций
dirname = os.path.dirname(__file__)

config = configparser.ConfigParser()
config.read(os.path.join(dirname, "config.ini"), encoding="utf-8")

NUM_SHOPS = int(config["Shops"]["NUM_SHOPS"])
MAX_CASHES_PER_SHOP = int(config["Shops"]["MAX_CASHES_PER_SHOP"])
DATA_DIR = os.path.join(dirname, config["Files"]["DATA_DIR"])

# создаем папку если нет
os.makedirs(DATA_DIR, exist_ok=True)

# статические данные
CATEGORIES = {
    "Бытовая химия": ["Порошок", "Средство для мытья посуды", "Отбеливатель"],
    "Текстиль": ["Полотенце", "Простыня", "Наволочка"],
    "Посуда": ["Тарелка", "Кружка", "Сковорода"],
    "Кухня": ["Нож", "Разделочная доска", "Контейнер"]
}

# сегодня и вчера 
today = datetime.today()
yesterday = today - timedelta(days=1)
sale_date = yesterday.strftime("%Y-%m-%d")  

# пн-сб: 0-5
if 0 <= today.weekday() <= 5:  
    
    print(f"Генерация данных за {yesterday.strftime('%d-%m-%Y')} (sale_date: {sale_date})")
    
    # для каждого магазина
    for shop_num in range(1, NUM_SHOPS + 1):
        # случайное количество касс в магазине (1-4)
        cashes = random.randint(1, MAX_CASHES_PER_SHOP)
        
        # для каждой кассы
        for cash_num in range(1, cashes + 1):
            filename = f"{shop_num}_{cash_num}.csv"
            filepath = os.path.join(DATA_DIR, filename)
            
            # готовим данные для этой кассы 
            data = {
                "doc_id": [],
                "item": [],
                "category": [],
                "amount": [],
                "price": [],
                "discount": [],
                "sale_date": []  
            }
            
            # генерируем чеки для этой кассы
            num_docs = random.randint(5, 15)  # 5-15 чеков на кассу
            
            for _ in range(num_docs):
                # уникальный ID чека: 3 буквы + 4 цифры
                doc_id = f"{''.join(random.choices(string.ascii_uppercase, k=3))}{random.randint(1000, 9999)}"
                
                # сколько товаров в чеке 
                num_items = random.randint(1, 5)
                
                for _ in range(num_items):
                    category = random.choice(list(CATEGORIES.keys()))
                    item = random.choice(CATEGORIES[category])
                    amount = random.randint(1, 5)
                    price = round(random.uniform(50, 1500), 2)
                    
                    # скидка: 30% вероятность, размер 0-30% от стоимости
                    if random.random() < 0.3:
                        discount_percent = random.uniform(0, 0.3)
                        discount = round(price * amount * discount_percent, 2)
                        # гарантируем что скидка не превышает стоимость
                        discount = min(discount, price * amount)
                    else:
                        discount = 0
                    
                    # добавляем в данные 
                    data["doc_id"].append(doc_id)
                    data["item"].append(item)
                    data["category"].append(category)
                    data["amount"].append(amount)
                    data["price"].append(price)
                    data["discount"].append(discount)
                    data["sale_date"].append(sale_date)  
            
            # создаем DataFrame и сохраняем в CSV
            df = pd.DataFrame(data)
            df.to_csv(filepath, index=False, encoding="utf-8")
            print(f"  Создан файл: {filename} ({len(df)} записей)")
    
    
else:
    print(f"Сегодня воскресенье ({today.strftime('%d-%m-%Y')})")
    print("Магазины не работают, данные не генерируются.")