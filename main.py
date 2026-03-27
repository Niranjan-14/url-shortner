from fastapi import FastAPI
import psycopg2
import random
import string

app = FastAPI()

# Database connection
conn = psycopg2.connect(
    host="localhost",
    database="urlshortener",
    user="postgres",
    password="shivu"
)
cursor = conn.cursor()

# Create table if not exists
cursor.execute("""
    CREATE TABLE IF NOT EXISTS urls (
        id         SERIAL PRIMARY KEY,
        short_code TEXT NOT NULL,
        long_url   TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT NOW(),
        click_count INTEGER DEFAULT 0
    )
""")
conn.commit()

def generate_code():
    return ''.join(random.choices(string.ascii_lowercase, k=6))

@app.post("/shorten")
def shorten(long_url: str):
    code = generate_code()
    cursor.execute(
        "INSERT INTO urls (short_code, long_url) VALUES (%s, %s)",
        (code, long_url)
    )
    conn.commit()
    return {"short_url": code}

@app.get("/{code}")
def redirect(code: str):
    cursor.execute(
        "SELECT long_url FROM urls WHERE short_code = %s",
        (code,)
    )
    result = cursor.fetchone()
    if result is None:
        return {"error": "URL not found"}
    return {"url": result[0]}