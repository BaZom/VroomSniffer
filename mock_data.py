# Mock Data Inserter
# ------------------
# Run this file to insert sample car listings into the database for testing.

from car_scraper.storage.db import save_listing

MOCK_LISTINGS = [
    ("VW Golf 7", "10.999 €", "Berlin", "https://example.com/golf7", "https://example.com/img1.jpg"),
    ("BMW 3er", "12.500 €", "Hamburg", "https://example.com/bmw3", "https://example.com/img2.jpg"),
    ("Audi A4", "13.750 €", "München", "https://example.com/audi", "https://example.com/img3.jpg")
]

for title, price, location, url, img in MOCK_LISTINGS:
    save_listing(title, price, location, url, img)
    print(f"[+] Inserted mock listing: {title}")
