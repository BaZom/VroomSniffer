# Generic Car Marketplace Scraper Engine
# --------------------------------------
# Uses Playwright to fetch dynamic web content from various car marketplace websites.
# Adaptable to different platforms through dynamic URL construction.

from playwright.sync_api import sync_playwright
import json
import argparse
import sys
import time
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from notifier.telegram import send_telegram_message, format_car_listing_message
from proxy.manager import ProxyManager, ProxyType

def parse_listing(item, base_url=""):
    try:
        title = item.query_selector(".text-module-begin").inner_text().strip()
        price = item.query_selector(".aditem-main--middle--price-shipping").inner_text().strip()
        location = item.query_selector(".aditem-main--top--left").inner_text().strip()
        link_suffix = item.query_selector("a").get_attribute("href")
        image_url = item.query_selector("img").get_attribute("src")
        posted = item.query_selector(".aditem-main--top--right").inner_text().strip() if item.query_selector(".aditem-main--top--right") else ""
        
        # Dynamic URL construction based on provided base_url
        if link_suffix and base_url:
            if link_suffix.startswith('http'):
                url_full = link_suffix
            else:
                url_full = f"{base_url}{link_suffix}"
        else:
            url_full = link_suffix or ""
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

def fetch_listings_from_url(url, use_proxy=False, proxy_manager=None):
    from urllib.parse import urlparse
    from proxy.manager import ProxyManager, ProxyType
    
    # Extract base URL for dynamic URL construction
    parsed_url = urlparse(url)
    base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
    
    # Get proxy manager if needed
    if use_proxy and proxy_manager is None:
        proxy_manager = ProxyManager.create_from_environment()
    
    # Initialize the IP address variable - we don't check it here anymore
    # since it was already checked in the main function to avoid duplication
    current_ip = "Unknown" if proxy_manager is None else proxy_manager.get_current_ip()
    
    with sync_playwright() as p:
        browser_options = {}
        
        # Configure proxy if WebShare residential proxy is enabled
        if use_proxy and proxy_manager and proxy_manager.proxy_type == ProxyType.WEBSHARE_RESIDENTIAL:
            proxy_config = proxy_manager.get_playwright_proxy()
            if proxy_config:
                browser_options["proxy"] = proxy_config
                print(f"[*] Using WebShare residential proxy")
        
        browser = p.chromium.launch(headless=True, **browser_options)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        )
        page = context.new_page()
        
        # Skip duplicate IP check as we already did this in the main script
        # This avoids redundant output and speeds up the scraping process
            
        print(f"[*] Navigating to marketplace search page: {url}")
        try:
            # Use 'domcontentloaded' first for faster initial load
            page.goto(url, wait_until="domcontentloaded", timeout=40000)
            print("[*] Page initial DOM loaded, waiting for content...")
            # Then wait for network to quiet down
            try:
                page.wait_for_load_state("networkidle", timeout=30000)
            except Exception as wait_error:
                print(f"[!] Network idle wait timed out: {str(wait_error)}")
                print("[*] Continuing anyway as the page content may be usable...")
        except Exception as e:
            print(f"[!] Navigation error: {str(e)}")
            print("[*] Trying again with a longer timeout and relaxed conditions...")
            # Try again with a longer timeout and relaxed wait_until condition
            page.goto(url, wait_until="load", timeout=60000)
        
        # Try different selectors and handle no results gracefully
        listings = []
        try:
            # First check if there's a "no results" message or if page loaded properly
            # We already waited for page to load above, so no need for another long wait here
            
            # Check for no results message first
            no_results_selectors = [
                "text=Keine Anzeigen gefunden",
                "text=Es wurden keine Anzeigen gefunden", 
                ".messagebox--alert",
                ".search-results-error",
                "[data-testid='no-results']"
            ]
            
            has_no_results = False
            for selector in no_results_selectors:
                try:
                    if page.locator(selector).is_visible(timeout=2000):
                        print(f"[!] No results found for this search")
                        has_no_results = True
                        break
                except:
                    continue
            
            # Try to get the page content to see if there are any errors
            try:
                if has_no_results:
                    # Get page title to help with debugging
                    title = page.title()
                    print(f"[DEBUG] Page title: {title}")
                    
                    # Check if we've been blocked or got a CAPTCHA
                    if "captcha" in title.lower() or "blocked" in title.lower():
                        print("[WARNING] Possible CAPTCHA or blocking detected")
            except Exception as e:
                print(f"[DEBUG] Could not get page title: {str(e)}")
            
            if has_no_results:
                context.close()
                browser.close()
                return [], current_ip, (use_proxy and proxy_manager and proxy_manager.proxy_type == ProxyType.WEBSHARE_RESIDENTIAL)
            
            # Wait for listings to load but with shorter timeout
            try:
                page.wait_for_selector(".aditem", timeout=15000)
                listings = page.query_selector_all(".aditem")
            except:
                # If .aditem not found, try alternative selectors
                alternative_selectors = [".ad-listitem", ".aditem-main", ".adlist .aditem"]
                for selector in alternative_selectors:
                    try:
                        page.wait_for_selector(selector, timeout=5000)
                        listings = page.query_selector_all(selector)
                        if listings:
                            break
                    except:
                        continue
            
            print(f"[*] Found {len(listings)} listings")
        
        except Exception as e:
            print(f"[!] No listings found with .aditem selector, trying alternatives...")
            # Try alternative selectors
            alternative_selectors = [
                "[data-testid='result-item']",
                ".ad-listitem",
                ".aditem-main",
                ".result-item"
            ]
            
            for selector in alternative_selectors:
                try:
                    page.wait_for_selector(selector, timeout=10000)
                    listings = page.query_selector_all(selector)
                    if listings:
                        print(f"[*] Found {len(listings)} listings with selector: {selector}")
                        break
                except:
                    continue
            
            if not listings:
                print("[!] No listings found with any selector - possibly no results for this search")
        
        parsed = [parse_listing(item, base_url) for item in listings] if listings else []
        context.close()
        browser.close()
    
    return [l for l in parsed if l], current_ip, (use_proxy and proxy_manager and proxy_manager.proxy_type == ProxyType.WEBSHARE_RESIDENTIAL)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", type=str, required=True)
    parser.add_argument("--notify", action="store_true", help="Send Telegram notifications for new listings")
    parser.add_argument("--notify-count", type=int, default=5, help="Number of top listings to notify (default: 5)")
    parser.add_argument("--use-proxy", action="store_true", help="Use proxy configuration from environment")
    parser.add_argument("--proxy-type", type=str, choices=[pt.name for pt in ProxyType], 
                        default="NONE", help="Type of proxy to use")
    args = parser.parse_args()
    
    # Set up proxy manager without redundant IP checks
    proxy_manager = None
    try:
        # Set up proxy if requested - silently without logging
        if args.use_proxy or args.proxy_type != "NONE":
            proxy_type = ProxyType[args.proxy_type]
            proxy_manager = ProxyManager(proxy_type)
            # Don't print proxy type here - it's logged in CLI main
        else:
            print("[*] Not using proxy - requests will use your direct IP address.")
    except Exception as e:
        print(f"[!] Error setting up proxy: {str(e)}")
        print("[!] Will continue with scraping, but proxy may not be available.")
    
    listings, used_ip, is_proxy_used = fetch_listings_from_url(args.url, args.use_proxy, proxy_manager)
    # Save results
    with open("storage/latest_results.json", "w", encoding="utf-8") as f:
        json.dump(listings, f, ensure_ascii=False, indent=2)
    print(f"[+] Wrote {len(listings)} listings to storage/latest_results.json")
    
    # Make the IP information very clear and easy to parse
    print(f"[*] Scraping completed using IP: {used_ip}")
    print(f"[*] Used proxy: {'Yes' if is_proxy_used else 'No'}")
    print(f"[*] ACTUAL_IP_USED: {used_ip} via {'proxy' if is_proxy_used else 'direct connection'}")
    
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
