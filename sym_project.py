import logging
from datetime import datetime, timedelta
from pathlib import Path
import requests
import psycopg2
import ast
import pandas as pd
import smtplib
import ssl
from email.message import EmailMessage

# ==================== ЛОГИРОВАНИЕ ====================
# Настройка логирования
log_dir = Path("logs")
log_dir.mkdir(exist_ok=True)

log_file = log_dir / f"{datetime.now().date()}.log"

logging.basicConfig(
    filename=log_file,
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s"
)

logging.info("Скрипт запущен")

# Очистка старых логов
for file in log_dir.iterdir():
    if file.is_file():
        mtime = datetime.fromtimestamp(file.stat().st_mtime)
        if datetime.now() - mtime > timedelta(days=3):
            file.unlink()
            logging.info(f"Удалён старый лог: {file.name}")


# ==================== ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ====================
# Разбор passback_params в словарь
# (оставляем ваш комментарий)
def parse_passback(value):
    if not value:
        return {}
    try:
        return ast.literal_eval(value)
    except Exception:
        return {}


# Валидация данных
# (оставляем ваш комментарий)
def validate(record):
    required = ["lti_user_id", "attempt_type", "created_at"]
    return all(record.get(k) is not None for k in required)


# ==================== ЗАГРУЗКА ДАННЫХ ИЗ API ====================
API_URL = "https://b2b.itresume.ru/api/statistics"

params = {
    "client": "Skillfactory",
    "client_key": "M2MGWS",
    "start": "2023-05-31 00:00:00",
    "end": "2023-05-31 23:59:59"
}

try:
    logging.info("Начало загрузки данных из API")
    response = requests.get(API_URL, params=params)
    response.raise_for_status()
    data = response.json()
    logging.info(f"Данные загружены, записей: {len(data)}")
except Exception as e:
    logging.error(f"Ошибка при обращении к API: {e}")
    raise


# ==================== ПОДКЛЮЧЕНИЕ К БД ====================
try:
    logging.info("Подключение к базе данных")
    conn = psycopg2.connect(
        host="localhost",
        port=5432,
        dbname="postgres",
        user="postgres",
        password="password"
    )
    cursor = conn.cursor()
except Exception as e:
    logging.error(f"Ошибка подключения к БД: {e}")
    raise


# ==================== ЗАПИСЬ В БД ====================
inserted = 0  # Счётчик успешных записей
skipped = 0   # Счётчик пропущенных записей

# SQL-запрос для вставки данных (оставляем ваш комментарий)
insert_sql = """
INSERT INTO public.grader_attempts (
    user_id,
    oauth_consumer_key,
    lis_result_sourcedid,
    lis_outcome_service_url,
    is_correct,
    attempt_type,
    created_at
)
VALUES (%s, %s, %s, %s, %s, %s, %s)
"""

rows_for_df = []  # будем собирать данные и для pandas

for row in data:
    if not validate(row):
        skipped += 1
        logging.warning("Запись пропущена: не прошла валидацию")
        continue

    # Парсим дополнительные параметры
    pb = parse_passback(row.get("passback_params"))

    raw_is_correct = row.get("is_correct")
    if raw_is_correct == 1:
        is_correct = True
    elif raw_is_correct == 0:
        is_correct = False
    else:
        is_correct = None

    try:
        cursor.execute(
            insert_sql,
            (
                row["lti_user_id"],
                pb.get("oauth_consumer_key"),
                pb.get("lis_result_sourcedid"),
                pb.get("lis_outcome_service_url"),
                is_correct,
                row["attempt_type"],
                row["created_at"]
            )
        )
        inserted += 1

        # сохраняем строку для последующей агрегации
        rows_for_df.append({
            "user_id": row["lti_user_id"],
            "is_correct": is_correct,
            "attempt_type": row["attempt_type"],
            "created_at": row["created_at"]
        })

    except Exception as e:
        conn.rollback()
        skipped += 1
        logging.error(f"Ошибка вставки записи: {e}")

conn.commit()

logging.info(f"Запись в БД завершена. Успешно: {inserted}, пропущено: {skipped}")


# ==================== АГРЕГАЦИЯ ДАННЫХ ЗА ДЕНЬ ====================
df = pd.DataFrame(rows_for_df)
df['created_at'] = pd.to_datetime(df['created_at'])
df['date'] = df['created_at'].dt.date

report = (
    df.groupby('date')
    .agg(
        total_attempts=('user_id', 'count'),
        successful_attempts=('is_correct', lambda x: x.eq(True).sum()),
        unique_users=('user_id', 'nunique')
    )
    .reset_index()
)

logging.info(f"Агрегация выполнена: {report.to_dict(orient='records')}")


# ==================== GOOGLE SHEETS (Apps Script WebApp) ====================
import requests

WEBAPP_URL = "https://script.google.com/macros/s/AKfycbxoxYLxFxPCWNOSvFnCnbzlDlC1i6n42q_CpR7ymIft9ybqcT99twWtXkaMyZ1_4Q_jwQ/exec"

try:
    for _, r in report.iterrows():
        payload = {
            "date": str(r["date"]),
            "total_attempts": int(r["total_attempts"]),
            "successful_attempts": int(r["successful_attempts"]),
            "unique_users": int(r["unique_users"])
        }

        response = requests.post(WEBAPP_URL, json=payload)
        response.raise_for_status()

    logging.info("Данные успешно отправлены в Google Sheets через Apps Script")

except Exception as e:
    logging.error(f"Ошибка отправки данных в Google Sheets: {e}")

# ==================== EMAIL-ОПОВЕЩЕНИЕ ====================
smtp_server = "smtp.mail.ru"
smtp_port = 465

sender_email = "sender@mail.ru"
sender_password = "KDup3XMGdct8mcDvrf4n"
receiver_email = "receiver@mail.ru"

try:
    msg = EmailMessage()
    msg["Subject"] = "Грейдер: ежедневный отчет готов"
    msg["From"] = sender_email
    msg["To"] = receiver_email

    msg.set_content(
        f"""
Скрипт успешно завершил работу.

Дата отчета: {report.iloc[0]['date']}

Агрегация:
{report.to_string(index=False)}

Записей добавлено в БД: {inserted}
Записей пропущено: {skipped}

Данные также отправлены в Google Sheets.
"""
    )

    context = ssl.create_default_context()

    with smtplib.SMTP_SSL(smtp_server, smtp_port, context=context) as server:
        server.login(sender_email, sender_password)
        server.send_message(msg)

    logging.info("Email-уведомление успешно отправлено")

except Exception as e:
    logging.error(f"Ошибка при отправке email: {e}")



# ==================== ЗАВЕРШЕНИЕ ====================
cursor.close()
conn.close()

logging.info("Скрипт полностью завершён")
