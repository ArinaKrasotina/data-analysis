import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

class PGDatabase:
    def __init__(self, host=None, database=None, user=None, password=None, port=5432):
        params = {
            'host': host or os.getenv("DB_HOST"),
            'database': database or os.getenv("DB_NAME"),
            'user': user or os.getenv("DB_USER"),
            'password': password or os.getenv("DB_PASSWORD"),
            'port': port or os.getenv("DB_PORT", 5432)
        }
        
        try:
            self.connection = psycopg2.connect(**params)
        except Exception as e:
            print(f"Ошибка подключения к БД: {e}")
            raise
        
        self.cursor = self.connection.cursor()
        self.connection.autocommit = True
    
    def post(self, query, args=()):
        try:
            self.cursor.execute(query, args)
            return True
        except Exception:
            return False