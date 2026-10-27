import os
from pathlib import Path
import psycopg
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent.parent / '.env')

def get_connection():
    return psycopg.connect(
        host="127.0.0.1",
        port=5432,
        dbname=os.environ["POSTGRES_DB"],
        user=os.environ["POSTGRES_USER"],
        password=os.environ["POSTGRES_PASSWORD"],
        connect_timeout=5,
    )