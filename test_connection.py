import os
from dotenv import load_dotenv
import mysql.connector

# Load environment variables
load_dotenv()

def get_db():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME"),
        port=int(os.getenv("DB_PORT")),
        ssl_disabled=True
    )

# Test the connection
try:
    conn = get_db()
    print("Connected successfully using .env!")
    conn.close()
except Exception as e:
    print("Connection failed:", e)