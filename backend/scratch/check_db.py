import psycopg2
from decouple import config

user = config('DB_USER')
password = config('DB_PASSWORD')
host = config('DB_HOST')
port = config('DB_PORT')
dbname = config('DB_NAME')

conn = psycopg2.connect(
    dbname=dbname, user=user, password=password, host=host, port=port
)
cur = conn.cursor()
cur.execute("SELECT table_name FROM information_schema.tables WHERE table_schema='public';")
tables = cur.fetchall()
print("Tables in public schema:")
for t in tables:
    print(" -", t[0])
conn.close()
