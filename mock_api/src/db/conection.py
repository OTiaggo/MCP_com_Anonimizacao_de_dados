import psycopg2
from psycopg2.extras import RealDictCursor
import os


DB_HOST = "postgres"
DB_NAME = "database"
DB_USER = "user"
DB_PASS = "userpassword"
DB_PORT = "5432"

def get_db_connection():
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASS,
            port=DB_PORT
        )
        return conn
    except Exception as e:
        print(f"Erro ao conectar ao banco: {e}")
        raise HTTPException(status_code=500, detail="Erro de conexão com o banco de dados")