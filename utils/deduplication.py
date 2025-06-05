# Deduplication Logic
# -------------------
# Generates a hash from listing fields and checks if it exists in the database.

import hashlib
import sqlite3

def generate_hash(title, price, url):
    raw = f"{title}{price}{url}"
    return hashlib.sha256(raw.encode()).hexdigest()

def is_duplicate(title, price, url):
    listing_hash = generate_hash(title, price, url)
    conn = sqlite3.connect("scraper.db")
    cur = conn.cursor()
    cur.execute("SELECT 1 FROM car_listings WHERE hash = ?", (listing_hash,))
    exists = cur.fetchone() is not None
    conn.close()
    return exists
