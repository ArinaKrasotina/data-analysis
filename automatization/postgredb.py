import psycopg2

class PGDatabase:
    def __init__(self, host, database, user, password, port=5432):
        # Приводим всё к строке и чистим
        params = {
            'host': str(host).strip(),
            'database': str(database).strip(),
            'user': str(user).strip(),
            'password': str(password).strip(),
            'port': int(str(port).strip()) if str(port).strip() else 5432
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