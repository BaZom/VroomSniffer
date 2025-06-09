# Scraper Engine for eBay Kleinanzeigen
# --------------
# Uses Playwright to fetch dynamic web content from eBay Kleinanzeigen.

from playwright.sync_api import sync_playwright
import json
import argparse
import sys
import time
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from notifier.telegram import send_telegram_message, format_car_listing_message

def parse_listing(item):
    try:
        title = item.query_selector(".text-module-begin").inner_text().strip()
        price = item.query_selector(".aditem-main--middle--price-shipping").inner_text().strip()
        location = item.query_selector(".aditem-main--top--left").inner_text().strip()
        link_suffix = item.query_selector("a").get_attribute("href")
        image_url = item.query_selector("img").get_attribute("src")
        posted = item.query_selector(".aditem-main--top--right").inner_text().strip() if item.query_selector(".aditem-main--top--right") else ""
        url_full = f"https://www.ebay-kleinanzeigen.de{link_suffix}"
        return {
            "Title": title,
            "Price": price,
            "Location": location,
            "Posted": posted,
            "URL": url_full,
            "Image": image_url
        }
    except Exception as e:
        print(f"[!] Error parsing listing: {e}")
        return None

def fetch_listings_from_url(url):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()
        print(f"[*] Navigating to eBay Kleinanzeigen search page: {url}")
        page.goto(url, wait_until="networkidle")
        page.wait_for_selector(".aditem")
        listings = page.query_selector_all(".aditem")
        print(f"[*] Found {len(listings)} listings")
        parsed = [parse_listing(item) for item in listings]
        context.close()
        browser.close()
    return [l for l in parsed if l]

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", type=str, required=True)
    parser.add_argument("--notify", action="store_true", help="Send Telegram notifications for new listings")
    parser.add_argument("--notify-count", type=int, default=5, help="Number of top listings to notify (default: 5)")
    args = parser.parse_args()
    
    listings = fetch_listings_from_url(args.url)
    
    # Save results
    with open("scraper/latest_results.json", "w", encoding="utf-8") as f:
        json.dump(listings, f, ensure_ascii=False, indent=2)
    print(f"[+] Wrote {len(listings)} listings to scraper/latest_results.json")
    
    # Send notifications if requested
    if args.notify and listings:
        print(f"[*] Sending Telegram notifications for top {min(args.notify_count, len(listings))} listings...")
        
        for i, listing in enumerate(listings[:args.notify_count]):
            if listing:  # Ensure listing is not None
                formatted_msg = format_car_listing_message(listing)
                success = send_telegram_message(formatted_msg)
                if success:
                    print(f"[+] Notification {i+1}/{min(args.notify_count, len(listings))} sent successfully")
                else:
                    print(f"[!] Failed to send notification {i+1}")
                
                # Rate limiting - wait between messages
                if i < min(args.notify_count, len(listings)) - 1:
                    time.sleep(2)  # 2 second delay between messages
        
        print(f"[+] Notification batch complete!")
