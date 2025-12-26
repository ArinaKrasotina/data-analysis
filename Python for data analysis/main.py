from pandas import read_excel, to_datetime
from numpy import cumsum, select
import matplotlib.pyplot as plt
import seaborn as sns

# базовые настройки графиков
sns.set_style("whitegrid")

# 1. загрузка и подготовка данных
orders = read_excel("orders.xlsx")
products = read_excel("products.xlsx")

df = orders.merge(products, on="product_id", how="left")
df = df.dropna(subset=["level1", "level2"])
df["accepted_at"] = to_datetime(df["accepted_at"])
df["revenue"] = df["price"] * df["quantity"]
df["margin_rub"] = (df["price"] - df["cost_price"]) * df["quantity"]

# 2. самая ходовая товарная категория
sales_by_category = (
    df.groupby("level1", as_index=False)
      .agg(total_quantity=("quantity", "sum"))
      .sort_values("total_quantity", ascending=False)
)

print("Продажи по категориям:")
print(sales_by_category)

# график
plt.figure(figsize=(10, 6))
sns.barplot(
    data=sales_by_category,
    y="level1",
    x="total_quantity"
)
plt.title("Количество проданных штук товара в каждой товарной категории")
plt.xlabel("Количество проданных штук")
plt.ylabel("Категория")
plt.tight_layout()
plt.show()

# 3. распределение продаж по подкатегориям
subcategory_distribution = (
    df.groupby(["level1", "level2"], as_index=False)
      .agg(total_quantity=("quantity", "sum"))
      .sort_values(["level1", "total_quantity"], ascending=[True, False])
)

print("Распределение по подкатегориям:")
print(subcategory_distribution)

# 4. средний чек за 13.01.2022
df_day = df[df["accepted_at"].dt.date == to_datetime("2022-01-13").date()]
checks = df_day.groupby("order_id", as_index=False).agg(order_sum=("revenue", "sum"))
average_check = checks["order_sum"].mean()
print(f"Средний чек 13.01.2022: {average_check:.2f} руб.")

# 5. доля промо в категории 'сыры'
cheese = df[df["level1"] == "Сыры"].copy()
cheese["is_promo"] = cheese["price"] != cheese["regular_price"]

promo_share = (
    cheese.groupby("is_promo", as_index=False)
          .agg(quantity=("quantity", "sum"))
)
promo_share["share"] = promo_share["quantity"] / promo_share["quantity"].sum()
print("Доля промо в категории сыры:")
print(promo_share)

# pie chart
plt.figure(figsize=(8, 8))
plt.pie(
    promo_share.sort_values("is_promo")["quantity"],
    labels=["не промо", "промо"],
    autopct="%.1f%%",
    startangle=90
)
plt.title("Доля промо-продаж в категории «сыры»")
plt.tight_layout()
plt.show()

# 6. маржа по категориям
margin_by_category = (
    df.groupby("level1", as_index=False)
      .agg(revenue=("revenue", "sum"),
           margin_rub=("margin_rub", "sum"))
)
margin_by_category["margin_pct"] = margin_by_category["margin_rub"] / margin_by_category["revenue"] * 100
print("Маржа по категориям:")
print(margin_by_category)

# маржа в рублях
plt.figure(figsize=(10, 6))
sns.barplot(
    data=margin_by_category.sort_values("margin_rub"),
    y="level1",
    x="margin_rub"
)
plt.title("Маржа по категориям (рубли)")
plt.xlabel("Маржа, руб.")
plt.ylabel("Категория")
plt.tight_layout()
plt.show()

# маржа в процентах
plt.figure(figsize=(10, 6))
sns.barplot(
    data=margin_by_category.sort_values("margin_pct"),
    y="level1",
    x="margin_pct"
)
plt.title("Маржа по категориям (%)")
plt.xlabel("Маржа, %")
plt.ylabel("Категория")
plt.tight_layout()
plt.show()

# 7. abc-анализ по подкатегориям
abc_base = (
    df.groupby(["level1", "level2"], as_index=False)
      .agg(quantity=("quantity", "sum"),
           revenue=("revenue", "sum"))
)

def abc_analysis(data, value_col):
    data = data.sort_values(value_col, ascending=False).copy()
    data["cum_share"] = cumsum(data[value_col]) / data[value_col].sum()
    data["abc"] = select(
        [data["cum_share"] <= 0.8, data["cum_share"] <= 0.95],
        ["A", "B"],
        default="C"
    )
    return data

abc_qty = abc_analysis(abc_base, "quantity")[["level1", "level2", "abc"]].rename(columns={"abc": "abc_quantity"})
abc_rev = abc_analysis(abc_base, "revenue")[["level1", "level2", "abc"]].rename(columns={"abc": "abc_revenue"})

abc_final = abc_base.merge(abc_qty, on=["level1", "level2"]).merge(abc_rev, on=["level1", "level2"])
abc_final["abc_total"] = abc_final["abc_quantity"] + " " + abc_final["abc_revenue"]

print("Итог abc-анализа:")
print(abc_final.sort_values("revenue", ascending=False))
