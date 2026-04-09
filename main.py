from fastapi import FastAPI
import psycopg2
import random
import string
from fastapi.responses import RedirectResponse
import redis

r = redis.Redis(host='localhost', port=6379, db=0)
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
cursor.execute("""
    CREATE INDEX IF NOT EXISTS idx_short_code ON urls (short_code)
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

@app.get("/stats")
def get_stats():
    conn.rollback()
    cursor.execute(
        "SELECT COUNT(*), SUM(click_count), MAX(created_at) FROM urls"
    )
    result = cursor.fetchone()
    cursor.execute("SELECT short_code, long_url, click_count FROM urls "
                   "ORDER BY click_count DESC "
                   "LIMIT 1")
    output = cursor.fetchone()
    if output is None:
        return {"error" : "URL output is None"}

    return {"total_count": result[0] , "total_clicks": result[1], "latest_created_time":result[2], 
            "Most_accessed_short_url":output[0], "Most_accessed_long_url":output[1], "total_url_clicks":output[2]}

@app.get("/{code}")
def redirect(code: str):
    @app.get("/{code}")
    def redirect(code: str):
        cached = r.get(code)
        if cached:
            return RedirectResponse(url=cached.decode('utf-8'))

    cursor.execute(
        "SELECT long_url FROM urls WHERE short_code = %s",
        (code,)
    )

    result = cursor.fetchone()

    cursor.execute(
	"UPDATE urls SET click_count = click_count + 1 WHERE short_code = %s",
	(code,)
    )

    conn.commit()

    if result is None:
        return {"error": "URL not found"}
    r.set(code, result[0])
    return RedirectResponse(url=result[0])


