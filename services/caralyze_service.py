"""
Service layer for caralyze: handles scraping, caching, price extraction, filter key logic, and notifications.
This is the main interface between UI and backend logic (scraper, notifications, proxy, etc).
"""
import sys
import json
import time
import re
import subprocess
from pathlib import Path

# Add parent directory for imports
sys.path.append(str(Path(__file__).parent.parent))

def get_filter_key(filters):
    def safe(val):
        if isinstance(val, (tuple, list)):
            return '-'.join(str(x) for x in val)
        return str(val).lower().replace(' ', '_') if val else 'any'
    return '_'.join([
        safe(filters.get('car_make')),
        safe(filters.get('car_model')),
        safe(filters.get('price_range')),
        safe(filters.get('year_range')),
        safe(filters.get('transmission')),
        safe(filters.get('max_mileage'))
    ])

def load_json_dict(path):
    if Path(path).exists():
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_json_dict(data, path):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def run_scraper_and_load_results(filters, build_search_url_ui, root_dir):
    """
    Run the ebay_kleinanzeigen_engine.py scraper as a subprocess with the given filters and load results from the output JSON file.
    Returns a list of listings.
    """
    import subprocess
    listings_data = []
    try:
        if filters and filters.get("custom_url"):
            url = filters["custom_url"]
        else:
            url = build_search_url_ui(filters)
        args = [sys.executable, str(Path(root_dir) / "scraper" / "ebay_kleinanzeigen_engine.py"), "--url", url]
        result = subprocess.run(
            args,
            cwd=root_dir, capture_output=True, text=True
        )
        if result.returncode == 0:
            json_path = Path(root_dir) / "scraper" / "latest_results.json"
            if json_path.exists():
                with open(json_path, "r", encoding="utf-8") as f:
                    listings_data = json.load(f)
        else:
            raise RuntimeError(f"Scraper error: {result.stderr}")
    except Exception as e:
        raise RuntimeError(f"Error during scraping: {str(e)}")
    return listings_data

def get_listings_for_filter(filters, all_old_path, latest_new_path, build_search_url_ui, root_dir):
    """
    Get all listings and new listings for the given filters by running the scraper
    and comparing with previously stored listings.
    
    Args:
        filters: Dictionary containing search filters
        all_old_path: Path to the JSON file storing all previously seen listings
        latest_new_path: Path to the JSON file storing latest new listings
        build_search_url_ui: Function to build search URL from filters
        root_dir: Root directory of the project
        
    Returns:
        Tuple of (all_listings, new_listings)
    """
    filter_key = get_filter_key(filters)
    listings_data = run_scraper_and_load_results(filters, build_search_url_ui, root_dir)
    old_dict = load_json_dict(all_old_path)
    old_listings = old_dict.get(filter_key, [])
    old_urls = set(l["URL"] for l in old_listings)
    new_listings = [l for l in listings_data if l["URL"] not in old_urls]
    merged_listings = old_listings + [l for l in listings_data if l["URL"] not in old_urls]
    old_dict[filter_key] = merged_listings
    save_json_dict(old_dict, all_old_path)
    new_dict = load_json_dict(latest_new_path)
    new_dict[filter_key] = new_listings
    save_json_dict(new_dict, latest_new_path)
    return merged_listings, new_listings

def extract_prices(listings):
    prices = []
    for item in listings:
        price_str = item.get("Price", "").replace(".", "").replace(",", "").replace("€", "").strip()
        match = re.search(r"\d+", price_str)
        if match:
            prices.append(int(match.group()))
    return prices

def send_new_listing_notifications(new_listings, filters=None, max_count=5):
    """
    Send Telegram notifications for new listings
    
    Args:
        new_listings (list): List of new car listings
        filters (dict): Optional filter information for context
        max_count (int): Maximum number of notifications to send
        
    Returns:
        dict: Summary of notification results
    """
    try:
        from notifier.telegram import send_telegram_message, format_car_listing_message
        
        if not new_listings:
            return {"success": False, "message": "No new listings to notify", "sent": 0}
        
        # Send summary first
        summary_msg = f"🚗 <b>New Car Findings!</b>\n\n"
        summary_msg += f"🆕 Found {len(new_listings)} new listings\n"
        
        if filters:
            summary_msg += f"🔍 Search: {filters.get('car_make', 'Any')} {filters.get('car_model', '')}\n"
            if filters.get('price_range'):
                min_price, max_price = filters['price_range']
                summary_msg += f"💰 Budget: €{min_price:,} - €{max_price:,}\n"
        
        # Calculate average price
        prices = extract_prices(new_listings)
        if prices:
            avg_price = int(sum(prices) / len(prices))
            summary_msg += f"📊 Average price: €{avg_price:,}\n"
        
        summary_msg += f"\n🔔 Sending top {min(max_count, len(new_listings))} listings..."
        
        success = send_telegram_message(summary_msg)
        if not success:
            return {"success": False, "message": "Failed to send summary", "sent": 0}
        
        # Send individual listings
        sent_count = 0
        for i, listing in enumerate(new_listings[:max_count]):
            formatted_msg = format_car_listing_message(listing)
            success = send_telegram_message(formatted_msg)
            if success:
                sent_count += 1
              # Rate limiting
            if i < min(max_count, len(new_listings)) - 1:
                time.sleep(1.5)  # 1.5 second delay between messages
        
        return {
            "success": True, 
            "message": f"Successfully sent {sent_count}/{min(max_count, len(new_listings))} notifications",
            "sent": sent_count,
            "total_new": len(new_listings)
        }
        
    except ImportError:
        return {"success": False, "message": "Telegram notifier not available", "sent": 0}
    except Exception as e:
        return {"success": False, "message": f"Notification error: {str(e)}", "sent": 0}

def send_monitoring_summary(all_listings, new_listings, filters=None):
    """
    Send a monitoring summary via Telegram
    
    Args:
        all_listings (list): All listings found
        new_listings (list): New listings only
        filters (dict): Optional filter information
        
    Returns:
        bool: Success status
    """
    try:
        from notifier.telegram import send_telegram_message
        
        summary_msg = f"📊 <b>Caralyze Monitoring Report</b>\n\n"
        summary_msg += f"📈 Total listings: {len(all_listings)}\n"
        summary_msg += f"🆕 New findings: {len(new_listings)}\n"
        
        # Price analysis
        if all_listings:
            all_prices = extract_prices(all_listings)
            if all_prices:
                avg_all = int(sum(all_prices) / len(all_prices))
                summary_msg += f"💰 Average price: €{avg_all:,}\n"
                summary_msg += f"📉 Lowest: €{min(all_prices):,}\n"
                summary_msg += f"📈 Highest: €{max(all_prices):,}\n"
        
        if new_listings:
            new_prices = extract_prices(new_listings)
            if new_prices:
                avg_new = int(sum(new_prices) / len(new_prices))
                summary_msg += f"🆕 New avg: €{avg_new:,}\n"
        
        # Search context
        if filters:
            summary_msg += f"\n🔍 <b>Search Details:</b>\n"
            summary_msg += f"Car: {filters.get('car_make', 'Any')} {filters.get('car_model', '')}\n"
            if filters.get('price_range'):
                min_price, max_price = filters['price_range']
                summary_msg += f"Budget: €{min_price:,} - €{max_price:,}\n"
            if filters.get('year_range'):
                min_year, max_year = filters['year_range']
                summary_msg += f"Year: {min_year} - {max_year}\n"
        
        summary_msg += f"\n⏰ Report generated at {datetime.now().strftime('%H:%M:%S')}"
        
        return send_telegram_message(summary_msg)
        
    except ImportError:
        print("[!] Telegram notifier not available")
        return False
    except Exception as e:
        print(f"[!] Error sending monitoring summary: {e}")
        return False
