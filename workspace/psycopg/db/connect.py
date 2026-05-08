import psycopg
from db import p1Settings

def connect():
    conn = psycopg.connect(
        dbname=p1Settings.POSTGRES_DB,
        user=p1Settings.POSTGRES_USER,
        password=p1Settings.POSTGRES_PASSWORD,
        host=p1Settings.POSTGRES_HOST,
        port=p1Settings.POSTGRES_PORT,
        options=p1Settings.POSTGRES_SCHEMA
    )
    print("Connected")
    return conn