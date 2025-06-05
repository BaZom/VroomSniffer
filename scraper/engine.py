# Scraper Engine
# --------------
# Uses Playwright to fetch dynamic web content from eBay Kleinanzeigen.

from playwright.sync_api import sync_playwright
from utils.deduplication import is_duplicate
from notifier.whatsapp_pywhatkit import send_whatsapp_message
#from storage.db import save_listing
import time
import json

def run_scraper():
    urls = [
        "https://www.kleinanzeigen.de/s-autos/anbieter:privat/preis:1:10000/golf/k0c216+autos.ez_i:2014%2C+autos.km_i:%2C150000+autos.shift_s:automatik", 
        "https://www.kleinanzeigen.de/s-autos/bmw/anbieter:privat/preis:1:16000/x1/k0c216+autos.ez_i:2015%2C+autos.km_i:%2C130000+autos.marke_s:bmw+autos.shift_s:automatik"
    ]
    listing_urls = []
    for url in urls:
        print(f"[*] Scraping URL: {url}")
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context()
            page = context.new_page()

            print("[*] Navigating to eBay Kleinanzeigen search page...")
            page.goto(url, wait_until="networkidle")

            page.wait_for_selector(".aditem")
            
            listings = page.query_selector_all(".aditem")
            print(f"[*] Found {len(listings)} listings")

            for item in listings:
                try:
                    title = item.query_selector(".text-module-begin").inner_text().strip()
                    price = item.query_selector(".aditem-main--middle--price-shipping").inner_text().strip()
                    location = item.query_selector(".aditem-main--top--left").inner_text().strip()
                    link_suffix = item.query_selector("a").get_attribute("href")
                    image_url = item.query_selector("img").get_attribute("src")
                    url = f"https://www.ebay-kleinanzeigen.de{link_suffix}"

                    #if not is_duplicate(title, price, url):
                    print(f"[+] New listing: {url}")
                    listing_urls.append(url)
                        #save_listing(title, price, location, url, image_url)
                    #else:
                        #print(f"[-] Duplicate: {title}")

                except Exception as e:
                    print(f"[!] Error parsing listing: {e}")
            if listing_urls:
                message = "\n".join(listing_urls)
                send_whatsapp_message(message)
                print("[+] Sent WhatsApp message with new listings")
                listing_urls = []
            else:
                print("[-] No new listings found")
            context.close()
            browser.close()

def collect_listings():
    from playwright.sync_api import sync_playwright
    urls = [
        "https://www.kleinanzeigen.de/s-autos/anbieter:privat/preis:1:10000/golf/k0c216+autos.ez_i:2014%2C+autos.km_i:%2C150000+autos.shift_s:automatik", 
        "https://www.kleinanzeigen.de/s-autos/bmw/anbieter:privat/preis:1:16000/x1/k0c216+autos.ez_i:2015%2C+autos.km_i:%2C130000+autos.marke_s:bmw+autos.shift_s:automatik"
    ]
    listings_data = []
    for url in urls:
        print(f"[*] Scraping URL: {url}")
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context()
            page = context.new_page()
            print("[*] Navigating to eBay Kleinanzeigen search page...")
            page.goto(url, wait_until="networkidle")
            page.wait_for_selector(".aditem")
            listings = page.query_selector_all(".aditem")
            print(f"[*] Found {len(listings)} listings")
            for item in listings:
                try:
                    title = item.query_selector(".text-module-begin").inner_text().strip()
                    price = item.query_selector(".aditem-main--middle--price-shipping").inner_text().strip()
                    location = item.query_selector(".aditem-main--top--left").inner_text().strip()
                    link_suffix = item.query_selector("a").get_attribute("href")
                    image_url = item.query_selector("img").get_attribute("src")
                    url_full = f"https://www.ebay-kleinanzeigen.de{link_suffix}"
                    listings_data.append({
                        "Title": title,
                        "Price": price,
                        "Location": location,
                        "URL": url_full,
                        "Image": image_url
                    })
                except Exception as e:
                    print(f"[!] Error parsing listing: {e}")
            context.close()
            browser.close()
    return listings_data

if __name__ == "__main__":
    #while True:
    #    run_scraper()
    #    time.sleep(300)  # wait 5 mins before next scrape

    # CLI mode: write results to JSON for Streamlit
    listings = collect_listings()
    with open("scraper/latest_results.json", "w", encoding="utf-8") as f:
        json.dump(listings, f, ensure_ascii=False, indent=2)
    print(f"[+] Wrote {len(listings)} listings to scraper/latest_results.json")
