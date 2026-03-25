from fastapi import FastAPI
import string
import random

app = FastAPI()
db = {}

def generate_code():
    return "".join(random.choices(string.ascii_lowercase, k=6))

@app.post("/shorten")
def shorten(long_url: str):
    code = generate_code()
    db[code] = long_url
    return {"short_url": code}

@app.get("/{code}")
def redirect(code):
    long_url = db[code]
    return {"url" : long_url}