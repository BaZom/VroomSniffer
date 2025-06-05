# CLI Tool
# --------
# Run this file with commands to interact with the scraper's database and Twilio.

import sqlite3
import argparse
from car_scraper.notifier.whatsapp import send_whatsapp_message

DB_PATH = "scraper.db"

def list_listings():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT id, title, price, location FROM car_listings ORDER BY id DESC LIMIT 10")
    for row in cur.fetchall():
        print(f"[{row[0]}] {row[1]} | {row[2]} | {row[3]}")
    conn.close()

def search_listings(keyword):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT id, title, price FROM car_listings WHERE title LIKE ?", (f"%{keyword}%",))
    for row in cur.fetchall():
        print(f"[{row[0]}] {row[1]} | {row[2]}")
    conn.close()

def send_listing(listing_id):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT title, price, location, listing_url FROM car_listings WHERE id = ?", (listing_id,))
    row = cur.fetchone()
    conn.close()

    if row:
        message = f"{row[0]} | {row[1]} | {row[2]}\n{row[3]}"
        send_whatsapp_message(message)
    else:
        print("[!] Listing not found.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Car Listings CLI")
    subparsers = parser.add_subparsers(dest="command")

    subparsers.add_parser("list", help="List latest listings")
    search_parser = subparsers.add_parser("search", help="Search listings by keyword")
    search_parser.add_argument("keyword", type=str)

    send_parser = subparsers.add_parser("send", help="Send a listing via WhatsApp")
    send_parser.add_argument("id", type=int)

    args = parser.parse_args()

    if args.command == "list":
        list_listings()
    elif args.command == "search":
        search_listings(args.keyword)
    elif args.command == "send":
        send_listing(args.id)
    else:
        parser.print_help()
