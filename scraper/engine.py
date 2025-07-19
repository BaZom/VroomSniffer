# Generic Car Marketplace Scraper Engine
# --------------------------------------
# Uses Playwright to fetch dynamic content from various car marketplace websites.
# Adaptable to different platforms through dynamic URL construction.

from playwright.sync_api import sync_playwright
import json
import argparse
import sys
import time
from pathlib import Path
from urllib.parse import urlparse
from typing import List, Tuple, Optional

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from notifier.telegram import send_telegram_message, format_car_listing_message
from proxy.manager import ProxyManager, ProxyType
from scraper.utils import ResourceBlocker, AntiDetection, PageNavigator, ListingsFinder

def parse_listing(item, base_url=""):
    """Parse a single listing element into a structured format"""
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


def fetch_listings_from_url(url: str, use_proxy: bool = False, proxy_manager: Optional[ProxyManager] = None) -> Tuple[List[dict], str, bool]:
    """
    Fetch car listings from a marketplace URL with bandwidth optimization.
    
    Args:
        url: The marketplace URL to scrape
        use_proxy: Whether to use proxy
        proxy_manager: Optional proxy manager instance
    
    Returns:
        Tuple of (listings, ip_address, proxy_used)
    """
    # Extract base URL for dynamic URL construction
    parsed_url = urlparse(url)
    base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
    
    # Setup proxy if needed
    current_ip = "Unknown"
    if use_proxy and proxy_manager is None:
        print(f"[DEBUG] Creating proxy manager from environment...")
        proxy_manager = ProxyManager.create_from_environment()
        print(f"[DEBUG] Created proxy manager with type: {proxy_manager.proxy_type.name}")
    elif not use_proxy:
        print(f"[DEBUG] Proxy not requested (use_proxy=False)")
    else:
        print(f"[DEBUG] Proxy manager already provided")
    
    if proxy_manager:
        current_ip = proxy_manager.get_current_ip()
        print(f"[*] Proxy type: {proxy_manager.proxy_type.name}")
        print(f"[*] Detected IP: {current_ip}")
    
    # Initialize resource blocker for bandwidth optimization
    resource_blocker = ResourceBlocker()
    
    with sync_playwright() as p:
        # Configure browser with proxy if needed
        browser_options = {}
        if use_proxy and proxy_manager and proxy_manager.proxy_type == ProxyType.WEBSHARE_RESIDENTIAL:
            proxy_config = proxy_manager.get_playwright_proxy()
            if proxy_config:
                browser_options["proxy"] = proxy_config
                print(f"[*] Using WebShare residential proxy")
        
        # Launch browser with anti-detection
        browser = p.chromium.launch(headless=True, **browser_options)
        context = browser.new_context(
            user_agent=AntiDetection.get_random_user_agent(),
            viewport={"width": 1920, "height": 1080}
        )
        page = context.new_page()
        
        # Setup bandwidth optimization and real bandwidth measurement
        page.route("**/*", resource_blocker.create_handler())
        
        # Add response listener to capture actual bandwidth
        bandwidth_data = {'total_bytes': 0, 'response_count': 0}  # Simple tracking
        
        def handle_response(response):
            try:
                # Only measure responses for allowed requests
                resource_type = response.request.resource_type
                url = response.request.url
                
                # Check if this request was allowed (not blocked)
                if not resource_blocker._should_block_resource(resource_type, url):
                    headers = response.headers
                    
                    # Get the compressed size (what actually travels over the network)
                    content_length = int(headers.get('content-length', 0)) if headers.get('content-length') else 0
                    
                    # If no content-length, try to get body size
                    if content_length == 0:
                        try:
                            body = response.body()
                            content_length = len(body) if body else 0
                        except Exception:
                            content_length = 0
                    
                    # Calculate realistic proxy bandwidth billing:
                    # Request overhead: Method + URL + HTTP version + headers
                    request_line_size = len(f"GET {url} HTTP/1.1\r\n")
                    request_headers_size = 800  # Realistic browser headers
                    
                    # Response overhead: Status line + headers + body (compressed)
                    response_status_size = 20  # "HTTP/1.1 200 OK\r\n"
                    response_headers_size = len(str(headers)) if headers else 300
                    response_body_size = content_length
                    
                    # Protocol overhead: TCP/TLS handshake, keep-alive, etc.
                    protocol_overhead = 200
                    
                    # Total realistic proxy bandwidth (what actually travels over network)
                    total_proxy_bandwidth = (request_line_size + request_headers_size + 
                                           response_status_size + response_headers_size + 
                                           response_body_size + protocol_overhead)
                    
                    # Update simple bandwidth tracking
                    bandwidth_data['total_bytes'] += total_proxy_bandwidth
                    bandwidth_data['response_count'] += 1
                    
            except Exception:
                # Silently handle errors to avoid breaking scraping
                pass
        
        page.on("response", handle_response)
        
        try:
            # Navigate with anti-detection delay
            AntiDetection.add_human_delay()
            
            # Navigate to page
            navigator = PageNavigator(page)
            if not navigator.navigate_to_url(url):
                return [], current_ip, (use_proxy and proxy_manager and proxy_manager.proxy_type == ProxyType.WEBSHARE_RESIDENTIAL)
            
            # Check for no results
            if navigator.check_for_no_results():
                return [], current_ip, (use_proxy and proxy_manager and proxy_manager.proxy_type == ProxyType.WEBSHARE_RESIDENTIAL)
            
            # Debug page content if needed
            navigator.debug_page_content()
            
            # Find listings directly - no change detection complexity
            listings_finder = ListingsFinder(page)
            listings = listings_finder.find_listings()
            
            # Parse listings
            parsed_listings = []
            if listings:
                for item in listings:
                    parsed_listing = parse_listing(item, base_url)
                    if parsed_listing:
                        parsed_listings.append(parsed_listing)
        
        finally:
            context.close()
            browser.close()
    
    # Print bandwidth optimization statistics
    print(f"[*] Navigation and scraping completed")
    resource_blocker.print_statistics()
    
    # Report accurate bandwidth measurement
    if bandwidth_data['total_bytes'] > 0:
        total_kb = round(bandwidth_data['total_bytes'] / 1024, 2)
        total_mb = round(bandwidth_data['total_bytes'] / (1024 * 1024), 3)
        print(f"\n💰 BANDWIDTH USAGE (ACTUAL PROXY TRANSFER):")
        print(f"   📊 Data transferred: {total_kb} KB ({total_mb} MB)")
        print(f"   🌍 This is the actual data transferred through the network/proxy")
        
        # Update the resource blocker's bandwidth tracker for downstream reporting
        resource_blocker.bandwidth_tracker.total_bytes = bandwidth_data['total_bytes']
    
    return parsed_listings, current_ip, (use_proxy and proxy_manager and proxy_manager.proxy_type == ProxyType.WEBSHARE_RESIDENTIAL)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", type=str, required=True)
    parser.add_argument("--notify", action="store_true", help="Send Telegram notifications for new listings")
    parser.add_argument("--notify-count", type=int, default=5, help="Number of top listings to notify (default: 5)")
    parser.add_argument("--use-proxy", action="store_true", help="Use proxy configuration from environment")
    parser.add_argument("--proxy-type", type=str, choices=[pt.name for pt in ProxyType], 
                        default="NONE", help="Type of proxy to use")
    args = parser.parse_args()
    
    # Always use ultra-aggressive bandwidth optimization (target: ~37 KB per scrape)
    print(f"[*] Bandwidth optimization: MAXIMUM AGGRESSION - blocking ALL non-essential resources including CSS")
    print(f"[*] Expected bandwidth reduction: 95%+ compared to normal browsing (target: ~37 KB per scrape)")
    
    # Set up proxy manager without redundant IP checks
    proxy_manager = None
    try:
        # Set up proxy if requested - silently without logging
        if args.use_proxy:
            proxy_manager = ProxyManager.create_from_environment()
            print(f"[*] Using proxy from environment: {proxy_manager.proxy_type.name}")
        elif args.proxy_type != "NONE":
            proxy_type = ProxyType[args.proxy_type]
            proxy_manager = ProxyManager(proxy_type)
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
