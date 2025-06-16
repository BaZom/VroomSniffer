# CLI Tool
# --------
# Run this file with commands to interact with the scraper's JSON storage and notifications.
#
# USAGE EXAMPLES:
# ===============
#
# 1. Run the scraper with a marketplace URL:
#    python cli/main.py run "https://marketplace-url.com/search-cars"
#
# 2. List the latest scraped listings:
#    python cli/main.py list
#
# 3. Search for specific cars in the listings:
#    python cli/main.py search "bmw"
#    python cli/main.py search "giulietta"
#    python cli/main.py search "automatic"
#
# 4. Send a listing via Telegram (use index from 'list' command):
#    python cli/main.py send 3
#
# WORKFLOW:
# =========
# 1. First, run the scraper to get fresh data:
#    python cli/main.py run "<your-marketplace-search-url>"
#
# 2. Browse the results:
#    python cli/main.py list
#
# 3. Search for specific terms:
#    python cli/main.py search "your-keyword"
#
# 4. Share interesting listings:
#    python cli/main.py send <listing-index>
#
# DATA STORAGE:
# =============
# - Latest scraping results: storage/latest_results.json
# - Historical data: storage/all_old_results.json
# - New listings only: storage/latest_new_results.json
#
# NOTES:
# ======
# - The 'run' command will overwrite previous results in latest_results.json
# - Use the Streamlit UI for more advanced filtering and monitoring
# - Telegram functionality requires proper configuration in notifier/

import argparse
import sys
import time
from pathlib import Path

# Add the parent directory to the path so we can import from project modules
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

# Import services via the provider pattern
from providers.services_provider import (
    get_storage_service,
    get_notification_service,
    get_scraper_service,
    get_scheduler_service,
    get_url_pool_service,
    get_statistics_service
)

# Initialize services via the provider
storage_service = get_storage_service()
notification_service = get_notification_service()
scraper_service = get_scraper_service()
scheduler_service = get_scheduler_service()
url_pool_service = get_url_pool_service()
statistics_service = get_statistics_service()

def _check_listings_exist():
    """Helper function to check if listings exist and print error if not"""
    listings = storage_service.get_all_cached_listings(storage_service.latest_results_path)
    if not listings:
        print("[!] No listings found. Run 'python cli/main.py run <url>' first.")
        return False
    return True

def list_listings():
    """List the latest scraped listings from JSON file"""
    if not _check_listings_exist():
        return
    
    listings = storage_service.get_all_cached_listings(storage_service.latest_results_path)
    print(f"[*] Found {len(listings)} listings:")
    for i, listing in enumerate(listings[:10], 1):  # Show only first 10
        title = listing.get("Title", "Unknown")[:50]
        price = listing.get("Price", "Unknown")
        location = listing.get("Location", "Unknown")
        print(f"[{i}] {title} | {price} | {location}")

def search_listings(keyword):
    """Search listings by keyword in title"""
    if not _check_listings_exist():
        return
    
    listings = storage_service.get_listings_by_search_criteria(
        storage_service.latest_results_path,
        search_term=keyword
    )
    
    if listings:
        print(f"[*] Found {len(listings)} matches for '{keyword}':")
        for i, listing in enumerate(listings[:10], 1):  # Show only first 10 matches
            title = listing.get("Title", "Unknown")[:50]
            price = listing.get("Price", "Unknown")
            print(f"[{i}] {title} | {price}")
    else:
        print(f"[!] No listings found matching '{keyword}'")

def send_listing(listing_index):
    """Send a listing via Telegram by index"""
    if not _check_listings_exist():
        return
    
    listings = storage_service.get_all_cached_listings(storage_service.latest_results_path)
    if 1 <= listing_index <= len(listings):
        listing = listings[listing_index - 1]
        success = notification_service.send_listing(listing)
        
        if success:
            print(f"[+] Listing {listing_index} sent via Telegram")
        else:
            print(f"[!] Failed to send listing {listing_index} via Telegram")
    else:
        print(f"[!] Listing index {listing_index} not found. Use 'list' command to see available listings.")

def send_top_listings(count=5):
    """Send top N listings via Telegram"""
    if not _check_listings_exist():
        return
    
    listings = storage_service.get_all_cached_listings(storage_service.latest_results_path)
    
    actual_count = min(count, len(listings))
    print(f"[*] Sending top {actual_count} listings via Telegram...")
    
    success_count = notification_service.send_multiple_listings(
        listings[:actual_count],
        delay_seconds=2
    )
    
    print(f"[+] Bulk notification complete! {success_count}/{actual_count} messages sent successfully.")

def notify_new_findings(search_keyword=""):
    """Send notification about new findings with optional search filter"""
    if not _check_listings_exist():
        return
    
    listings = storage_service.get_all_cached_listings(storage_service.latest_results_path)
    
    # Filter by keyword if provided
    if search_keyword:
        filtered_listings = storage_service.get_listings_by_search_criteria(
            storage_service.latest_results_path, 
            search_term=search_keyword
        )
        if not filtered_listings:
            print(f"[!] No listings found matching '{search_keyword}'")
            return
    else:
        filtered_listings = listings
    
    # Send summary notification
    success = notification_service.send_summary_notification(
        filtered_listings,
        search_keyword=search_keyword,
        max_preview=3
    )
    
    if success:
        print(f"[+] Summary notification sent for {len(filtered_listings)} listings")
    else:
        print(f"[!] Failed to send summary notification")

def run_scraper_with_url(url, notify=False, notify_count=5):
    """Run the scraper with a direct URL"""
    print(f"[*] Running scraper with URL: {url}")
    
    # Create filters dictionary with custom_url
    filters = {"custom_url": url}
    
    # Use the scraper service to run the scraper
    listings = scraper_service.run_scraper_and_load_results(
        filters,
        build_search_url_ui=lambda x: x.get("custom_url", ""),  # Simple lambda to return the URL
        root_dir=project_root
    )
    
    if listings:
        print(f"[+] Scraping complete! Found {len(listings)} listings.")
        
        # Send notifications if requested
        if notify and listings:
            print(f"[*] Sending notifications for top {min(notify_count, len(listings))} listings...")
            send_top_listings(notify_count)
        
        return True
    else:
        print("[!] Scraping completed but no listings found.")
        return False

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="VroomSniffer Car Scraper CLI - Interact with JSON-based listing data",        epilog="""
EXAMPLES:
  %(prog)s run "https://www.example-marketplace.com/s-autos/bmw/k0c216"
  %(prog)s list
  %(prog)s search "bmw x5"  
  %(prog)s send 3

For more advanced features, use the Streamlit UI:
  streamlit run ui/streamlit_app.py
        """,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # List command
    list_parser = subparsers.add_parser(
        "list", 
        help="List latest scraped listings from JSON",
        description="Display the most recent car listings from the last scraping run. Shows first 10 listings with title, price, and location."
    )

    # Search command  
    search_parser = subparsers.add_parser(
        "search", 
        help="Search listings by keyword",
        description="Search through the latest listings for cars matching a keyword in the title."
    )
    search_parser.add_argument(
        "keyword", 
        type=str, 
        help="Keyword to search for in listing titles (e.g., 'bmw', 'automatic', 'diesel')"
    )
    
    # Send command
    send_parser = subparsers.add_parser(
        "send", 
        help="Send a listing via Telegram",
        description="Send a specific car listing via Telegram. Use 'list' command first to see available indices."
    )
    send_parser.add_argument(
        "index", 
        type=int, 
        help="Index of the listing to send (use 'list' command to see indices, starting from 1)"
    )

    # Send-top command
    send_top_parser = subparsers.add_parser(
        "send-top", 
        help="Send top N listings via Telegram",
        description="Send multiple top listings via Telegram with formatting. Includes rate limiting between messages."
    )
    send_top_parser.add_argument(
        "count", 
        type=int, 
        nargs='?', 
        default=5,
        help="Number of top listings to send (default: 5)"
    )

    # Notify command
    notify_parser = subparsers.add_parser(
        "notify", 
        help="Send summary notification about findings",
        description="Send a summary notification about all findings or filtered by keyword."
    )
    notify_parser.add_argument(
        "keyword", 
        type=str, 
        nargs='?', 
        default="",
        help="Optional keyword to filter listings before notification"
    )
    
    # Run command
    run_parser = subparsers.add_parser(
        "run", 
        help="Run the scraper engine with a direct marketplace URL",
        description="Execute the car scraper with a specific marketplace search URL. Results will be saved to storage/latest_results.json"
    )
    run_parser.add_argument(
        "url", 
        type=str, 
        help="Direct marketplace search URL (e.g., 'https://www.example-marketplace.com/s-autos/bmw/k0c216')"
    )
    run_parser.add_argument(
        "--notify", 
        action="store_true", 
        help="Send Telegram notifications for top listings after scraping"
    )
    run_parser.add_argument(
        "--notify-count", 
        type=int, 
        default=5,
        help="Number of top listings to notify via Telegram (default: 5)"
    )
    
    # Version command
    version_parser = subparsers.add_parser(
        "version", 
        help="Show version information",
        description="Display version and system information for the VroomSniffer car scraper."
    )

    # Scheduler commands
    schedule_parser = subparsers.add_parser(
        "schedule",
        help="Schedule periodic scraping runs",
        description="Set up automatic scraping at fixed intervals"
    )
    schedule_parser.add_argument(
        "url",
        type=str,
        help="Direct marketplace search URL to scrape periodically"
    )
    schedule_parser.add_argument(
        "--interval",
        type=int,
        default=60,
        help="Interval between scraping runs in seconds (default: 60)"
    )
    schedule_parser.add_argument(
        "--runs",
        type=int,
        default=5,
        help="Maximum number of scraping runs to perform (default: 5)"
    )
    schedule_parser.add_argument(
        "--notify",
        action="store_true",
        help="Send notifications for new listings found in each run"
    )

    args = parser.parse_args()

    if args.command == "list":
        list_listings()
    elif args.command == "search":
        search_listings(args.keyword)
    elif args.command == "send":
        send_listing(args.index)
    elif args.command == "send-top":
        send_top_listings(args.count)
    elif args.command == "notify":
        notify_new_findings(args.keyword)
    elif args.command == "version":
        print("🚗 VroomSniffer Car Scraper v2.1.0 (Service Layer Refactored)")
    elif args.command == "run":
        run_scraper_with_url(args.url, args.notify, args.notify_count)
    elif args.command == "schedule":
        try:
            # Set up scheduler
            scheduler_service.set_interval(args.interval)
            scheduler_service.start_scraping()
            
            print(f"[*] Starting scheduled scraping with interval: {args.interval} seconds")
            print(f"[*] Will perform up to {args.runs} runs")
            print(f"[*] Press Ctrl+C to stop early")
            
            runs_completed = 0
            while runs_completed < args.runs and scheduler_service.is_scraping_active():
                if scheduler_service.is_time_to_scrape():
                    print(f"\n[*] Run {runs_completed + 1}/{args.runs}")
                    success = run_scraper_with_url(args.url, args.notify, 3)
                    
                    runs_completed = scheduler_service.record_scrape()
                    
                    if runs_completed >= args.runs:
                        scheduler_service.stop_scraping()
                        break
                        
                    next_run_in = scheduler_service.get_time_until_next_scrape()
                    print(f"[*] Next run in {int(next_run_in)} seconds")
                
                # Sleep for a short time to avoid CPU spinning
                time.sleep(1)
                
            print(f"[+] Scheduled scraping complete. Performed {runs_completed} runs.")
            
        except KeyboardInterrupt:
            print("\n[*] Scheduled scraping stopped by user")
            scheduler_service.stop_scraping()
    else:
        parser.print_help()
