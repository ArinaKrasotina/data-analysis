import pandas as pd
from pathlib import Path
from datetime import datetime

# предподготовка

SBIS_DIR = Path("Входящие")
PHARM_DIR = Path("Аптеки/csv/correct")
RESULT_DIR = Path("Результат") / datetime.today().strftime("%Y-%m-%d")

DOC_TYPES = ["СчФктр", "УпдДоп", "УпдСчфДоп", "ЭДОНакл"]

# загрузка данных сбис

sbis_frames = []

for file in SBIS_DIR.iterdir():
    if file.suffix.lower() != ".csv":
        continue

    try:
        df = pd.read_csv(file, sep=";", encoding="cp1251")
    except UnicodeDecodeError:
        df = pd.read_csv(file, sep=";", encoding="utf-8")

    sbis_frames.append(df)

sbis_df = pd.concat(sbis_frames, ignore_index=True)

sbis_df.columns = [
    "Дата", "Номер", "Сумма", "Статус", "Примечание", "Комментарий",
    "Контрагент", "ИНН_КПП", "Организация", "ИНН_КПП_1",
    "Тип_документа", "Имя_файла", "Дата_1", "Номер_1", "Сумма_1",
    "Сумма_НДС", "Ответственный", "Подразделение", "Код",
    "Дата_2", "Время", "Тип_пакета", "Идентификатор_пакета",
    "Запущено_в_обработку", "Получено_контрагентом", "Завершено",
    "Увеличение_суммы", "НДС", "Уменьшение_суммы", "НДС_1"
]

sbis_df["Дата"] = pd.to_datetime(
    sbis_df["Дата"],
    format="%d.%m.%Y",
    errors="coerce"
)

# выбираем только нужные типы документов
sbis_df = sbis_df[sbis_df["Тип_документа"].isin(DOC_TYPES)]

# Если по номеру несколько документов — берём первый
sbis_df = sbis_df.drop_duplicates(subset="Номер", keep="first")

# работа с аптеками

RESULT_DIR.mkdir(parents=True, exist_ok=True)

for file in PHARM_DIR.iterdir():
    if file.suffix.lower() != ".csv":
        continue

    pharm_df = pd.read_csv(file, sep=";", encoding="cp1251")

    # Корректируем номер накладной для ЕАПТЕКИ
    pharm_df["Номер_для_поиска"] = pharm_df["Номер накладной"].astype(str)

    mask = pharm_df["Поставщик"] == "ЕАПТЕКА"
    pharm_df.loc[mask, "Номер_для_поиска"] += "/15"

    # берем дату накладной
    pharm_df["Дата накладной_dt"] = pd.to_datetime(
        pharm_df["Дата накладной"],
        format="%d.%m.%Y",
        errors="coerce"
    )

    # MERGE

    merged = pharm_df.merge(
        sbis_df[["Номер", "Сумма", "Дата"]],
        how="left",
        left_on="Номер_для_поиска",
        right_on="Номер"
    )

    # заполняем итоговые столбцы
    merged["Номер_счет_фактуры"] = merged["Номер"]
    merged["Сумма_счет_фактуры"] = merged["Сумма"]

    merged["Дата_счет_фактуры"] = merged["Дата"].dt.strftime("%d.%m.%Y")

    merged["Сравнение_дат"] = ""
    merged.loc[
        (merged["Дата"].notna()) &
        (merged["Дата накладной_dt"] != merged["Дата"]),
        "Сравнение_дат"
    ] = "Не совпадает!"

    # настройка итогового вида таблицы

    final_columns = [
        '№ п/п', 'Штрих-код партии', 'Наименование товара', 'Поставщик',
        'Дата приходного документа', 'Номер приходного документа',
        'Дата накладной', 'Номер накладной', 'Номер_счет_фактуры',
        'Сумма_счет_фактуры', 'Кол-во',
        'Сумма в закупочных ценах без НДС', 'Ставка НДС поставщика',
        'Сумма НДС', 'Сумма в закупочных ценах с НДС',
        'Дата_счет_фактуры', 'Сравнение_дат'
    ]

    result_df = merged[final_columns]

    output_path = RESULT_DIR / f"{file.stem}_результат.xlsx"
    result_df.to_excel(output_path, index=False)

print("Обработка завершена успешно.")
