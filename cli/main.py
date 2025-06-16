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
import json
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
    # Use storage/all_old_results.json file
    all_old_path = storage_service.all_old_path
    listings = storage_service.get_all_cached_listings(all_old_path)
    if not listings:
        print("[!] No listings found. Run 'python cli/main.py run <url>' first.")
        return False
    return True

def list_listings(list_type="all", count=10):
    """
    List car listings based on the specified type
    
    Args:
        list_type: Type of listings to display ('latest', 'all', or 'new'), defaults to 'all'
        count: Maximum number of listings to display (0 = all)
    """# Define paths for different listing files
    # latest_results.json is not a direct attribute, so construct its path
    storage_dir = Path(storage_service.all_old_path).parent
    latest_results_path = str(storage_dir / "latest_results.json")
    all_old_path = storage_service.all_old_path
    new_results_path = storage_service.latest_new_path
    
    # Choose the appropriate file based on the list_type
    if list_type == "latest":
        file_path = latest_results_path
        file_description = "latest run"
    elif list_type == "all":
        file_path = all_old_path
        file_description = "all stored"
    elif list_type == "new":
        file_path = new_results_path
        file_description = "new findings"
    else:
        print(f"[!] Invalid listing type: {list_type}")
        return
    
    try:
        listings = storage_service.get_all_cached_listings(file_path)
        
        if not listings:
            print(f"[!] No listings found in {file_description}")
            return
            
        print(f"[*] Found {len(listings)} {file_description} listings:")
        
        # Determine how many listings to display
        display_count = len(listings) if count == 0 else count
        
        # Display listings
        for i, listing in enumerate(listings[:display_count], 1):
            title = listing.get("Title", "Unknown")[:50]
            price = listing.get("Price", "Unknown")
            location = listing.get("Location", "Unknown")
            posted = listing.get("Posted", "Unknown")
            print(f"[{i}] {title} | {price} | {location} | {posted}")
            
        if len(listings) > display_count:
            print(f"[*] Showing {display_count} of {len(listings)} listings. Use --count option to show more.")
            
    except Exception as e:
        print(f"[!] Error reading {file_description} listings: {e}")

def search_listings(keyword):
    """Search listings by keyword in title"""
    if not _check_listings_exist():
        return
    
    # Use storage/all_old_results.json file by default
    all_old_path = storage_service.all_old_path
    
    listings = storage_service.get_listings_by_search_criteria(
        search_term=keyword,
        cache_path=all_old_path
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
    
    # Use storage/latest_results.json file
    storage_dir = Path(storage_service.all_old_path).parent
    latest_results_path = str(storage_dir / "latest_results.json")
    listings = storage_service.get_all_cached_listings(latest_results_path)
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
    
    # Use storage/latest_results.json file
    storage_dir = Path(storage_service.all_old_path).parent
    latest_results_path = str(storage_dir / "latest_results.json")
    listings = storage_service.get_all_cached_listings(latest_results_path)
    
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
    
    # Use storage/latest_new_results.json file which only contains new unique listings
    new_results_path = storage_service.latest_new_path
    listings = storage_service.get_all_cached_listings(new_results_path)    # Filter by keyword if provided
    if search_keyword:
        filtered_listings = storage_service.get_listings_by_search_criteria(
            new_results_path, 
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

def run_scraper_with_url_improved(urls, notify_new=False, notify_count=5):
    """
    Improved function to run the scraper with one or more direct URLs
    
    Args:
        urls: Single URL string or list of URLs to scrape
        notify_new: Whether to send notifications for new listings
        notify_count: Number of new listings to send detailed notifications for
    """
    if isinstance(urls, str):
        urls = [urls]  # Convert single URL to list
        
    all_listings = []
    new_listings = []
    success = False
    
    # Try to use tqdm for progress bar
    try:
        from tqdm import tqdm
        has_tqdm = True
    except ImportError:
        has_tqdm = False
        print("[!] tqdm package not found. Install it for progress bars: pip install tqdm")
    
    # Process URLs with progress bar if multiple URLs
    if has_tqdm and len(urls) > 1:
        url_iter = tqdm(enumerate(urls, 1), total=len(urls), desc="Processing URLs", unit="url")
    else:
        url_iter = enumerate(urls, 1)
    
    for i, url in url_iter:
        if has_tqdm and len(urls) > 1:
            tqdm.write(f"[*] Running scraper with URL {i}/{len(urls)}: {url}")
        else:
            print(f"[*] Running scraper with URL {i}/{len(urls)}: {url}")
        
        # Create filters dictionary with custom_url
        filters = {"custom_url": url}
        
        # Use the scraper service's get_listings_for_filter method to properly handle storage
        url_all_listings, url_new_listings = scraper_service.get_listings_for_filter(
            filters,
            build_search_url_ui=lambda x: x.get("custom_url", ""),  # Simple lambda to return the URL
            root_dir=project_root
        )
        
        if url_all_listings:
            msg = f"[+] URL {i}/{len(urls)} complete! Found {len(url_all_listings)} listings ({len(url_new_listings)} new)."
            if has_tqdm and len(urls) > 1:
                tqdm.write(msg)
            else:
                print(msg)
            all_listings.extend(url_all_listings)
            new_listings.extend(url_new_listings)
            success = True
        else:
            msg = f"[!] URL {i}/{len(urls)} completed but no listings found."
            if has_tqdm and len(urls) > 1:
                tqdm.write(msg)
            else:
                print(msg)
              # Save combined listings to latest_results.json
    if all_listings:        # Save to the latest_results.json file
        storage_dir = Path(storage_service.all_old_path).parent
        latest_results_path = str(storage_dir / "latest_results.json")
        # Use direct json dump as StorageService doesn't have save_to_json method
        Path(latest_results_path).parent.mkdir(parents=True, exist_ok=True)
        with open(latest_results_path, "w", encoding="utf-8") as f:
            json.dump(all_listings, f, ensure_ascii=False, indent=2)
        print(f"[+] All URLs processed. Total listings found: {len(all_listings)} ({len(new_listings)} new).")
        
        # Send notifications about new listings if requested
        if notify_new and new_listings:
            notify_new_listings(new_listings, notify_count)
        
        return True
    else:
        print("[!] All URLs processed but no listings found.")
        return False

def send_listings_by_indexes(indexes):
    """
    Send multiple specific listings via Telegram by their indexes
    
    Args:
        indexes: List of integer indexes to send
    """
    if not _check_listings_exist():
        return
    
    # Use "storage/all_old_results.json" file by default
    all_old_path = storage_service.all_old_path
    listings = storage_service.get_all_cached_listings(all_old_path)
    
    # Get total count of listings
    total_listings = len(listings)
    valid_indexes = []
    
    # Validate indexes
    for idx in indexes:
        if 1 <= idx <= total_listings:
            valid_indexes.append(idx)
        else:
            print(f"[!] Invalid index: {idx}. Must be between 1 and {total_listings}")
            
    if not valid_indexes:
        print("[!] No valid indexes provided. Use 'list' command to see available listings.")
        return
        
    print(f"[*] Sending {len(valid_indexes)} listings via Telegram...")
    
    # Use tqdm to create a progress bar
    try:
        from tqdm import tqdm
        has_tqdm = True
    except ImportError:
        has_tqdm = False
        
    # Send each listing
    success_count = 0
    
    if has_tqdm:
        indexes_iter = tqdm(valid_indexes, desc="Sending to Telegram", unit="listing")
    else:
        indexes_iter = valid_indexes
    
    for idx in indexes_iter:
        listing = listings[idx-1]  # -1 because indexes are 1-based
        success = notification_service.send_listing(listing)
        
        if success:
            success_count += 1
            if not has_tqdm:
                print(f"[+] Listing {idx} sent successfully")
        else:
            if has_tqdm:
                tqdm.write(f"[!] Failed to send listing {idx}")
            else:
                print(f"[!] Failed to send listing {idx}")
                
        # Add delay between messages
        if idx != valid_indexes[-1]:  # If not the last message
            import time
            time.sleep(2)
    
    print(f"[+] Sent {success_count}/{len(valid_indexes)} listings successfully.")

def notify_new_listings(new_listings, count=5):
    """
    Send notification about new listings after scraping
    
    Args:
        new_listings: List of newly found listings
        count: Maximum number of listings to send individual notifications for
    """
    if not new_listings:
        print("[*] No new listings to notify about.")
        return
    
    print(f"[*] Sending summary notification for {len(new_listings)} new listings...")
    
    # Create summary message
    summary_msg = f"🔥 <b>New Car Listings Found</b>\n\n"
    summary_msg += f"📊 Found {len(new_listings)} new listings\n"
    
    if new_listings:
        # Add preview of top new listings
        max_preview = min(3, len(new_listings))
        summary_msg += "\n<b>New Listings:</b>\n"
        for i, listing in enumerate(new_listings[:max_preview]):
            title = listing.get("Title", "Unknown")
            if len(title) > 50:
                title = title[:50] + "..."
            price = listing.get("Price", "Unknown")
            summary_msg += f"{i+1}. {title} - {price}\n"
    
    summary_msg += f"\n💡 Use CLI to explore: 'python cli/main.py list --type new'"
      # Send the summary message
    success, _ = notification_service.send_telegram_message(summary_msg)
    
    if success:
        print(f"[+] Summary notification sent for {len(new_listings)} new listings")
    else:
        print(f"[!] Failed to send summary notification")
        return
        
    # If requested, also send individual notifications for top X new listings
    if count > 0 and count <= len(new_listings):
        print(f"[*] Sending individual notifications for top {count} new listings...")
        
        # Use tqdm to create a progress bar
        try:
            from tqdm import tqdm
            has_tqdm = True
        except ImportError:
            has_tqdm = False
            
        # Send each listing
        if has_tqdm:
            listings_iter = tqdm(new_listings[:count], desc="Sending detailed notifications", unit="listing")
        else:
            listings_iter = new_listings[:count]
        
        success_count = 0
        for i, listing in enumerate(listings_iter):
            success = notification_service.send_listing(listing)
            
            if success:
                success_count += 1
            else:
                if has_tqdm:
                    tqdm.write(f"[!] Failed to send detailed notification {i+1}")
                else:
                    print(f"[!] Failed to send detailed notification {i+1}")
                    
            # Add delay between messages
            if i < count - 1:  # If not the last message
                import time
                time.sleep(2)
        
        print(f"[+] Sent {success_count}/{count} detailed notifications successfully.")

def load_saved_urls():
    """
    Load saved URLs from saved_urls.json
    
    Returns:
        list: List of saved URLs, or empty list if none found
    """
    saved_urls_path = project_root / "storage" / "saved_urls.json"
    
    if not saved_urls_path.exists():
        print(f"[!] No saved URLs found at {saved_urls_path}")
        return []
    
    try:
        with open(saved_urls_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            urls = data.get("urls", [])
            
            if not urls:
                print("[!] No URLs found in saved_urls.json")
                return []
                
            print(f"[*] Loaded {len(urls)} URLs from saved_urls.json")
            return urls
    except (json.JSONDecodeError, Exception) as e:
        print(f"[!] Error loading saved URLs: {str(e)}")
        return []

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
    list_parser.add_argument(
        "--type",
        choices=["latest", "all", "new"],
        default="all",
        help="Type of listings to display: 'all' (default) for all stored listings, 'latest' for most recent run, 'new' for new findings only"
    )
    list_parser.add_argument(
        "--count",
        type=int,
        default=10,
        help="Number of listings to display (default: 10, use 0 for all)"
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
        help="Send one or more listings via Telegram",
        description="Send specific car listings via Telegram by their indexes. Use 'list' command first to see available indices."
    )
    send_parser.add_argument(
        "indexes", 
        type=int, 
        nargs='+',
        help="One or more indexes of listings to send (use 'list' command to see indices, starting from 1)"
    )    # Note: send-top command removed (functionality merged into enhanced send command)

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
        help="Run the scraper engine with one or more marketplace URLs",
        description="Execute the car scraper with one or more marketplace search URLs. Results will be saved to storage/latest_results.json"
    )
    run_parser.add_argument(
        "urls", 
        type=str, 
        nargs='+',
        help="One or more marketplace search URLs (e.g., 'https://www.example-marketplace.com/s-autos/bmw/k0c216')"
    )
    run_parser.add_argument(
        "--notify-new", 
        action="store_true", 
        help="Send Telegram notifications for new listings found after scraping"
    )
    run_parser.add_argument(
        "--notify-count", 
        type=int, 
        default=5,
        help="Number of new listings to send detailed notifications for (default: 5)"
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
        "urls",
        type=str,
        nargs="*",
        help="One or more marketplace search URLs to scrape periodically (omit to use saved URLs)"
    )
    schedule_parser.add_argument(
        "--use-saved",
        action="store_true",
        help="Use URLs from saved_urls.json instead of providing URLs directly"
    )
    schedule_parser.add_argument(
        "--random",
        action="store_true",
        help="Select URLs randomly instead of sequentially (only applies with multiple URLs)"
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
        help="Maximum number of scraping runs to perform (default: 5, use 0 for unlimited runs until stopped)"
    )
    schedule_parser.add_argument(
        "--notify-new",
        action="store_true",
        help="Send notifications for new listings found in each run"
    )
    schedule_parser.add_argument(
        "--notify-count", 
        type=int, 
        default=5,
        help="Number of new listings to send detailed notifications for (default: 5)"
    )

    args = parser.parse_args()
    if args.command == "list":
        list_listings(args.type, args.count)
    elif args.command == "search":
        search_listings(args.keyword)
    elif args.command == "send":
        send_listings_by_indexes(args.indexes)
    elif args.command == "notify":
        notify_new_findings(args.keyword)
    elif args.command == "version":
        print("🚗 VroomSniffer Car Scraper v2.1.0 (Service Layer Refactored)")
    elif args.command == "run":
        run_scraper_with_url_improved(args.urls, args.notify_new, args.notify_count)
    elif args.command == "schedule":
        try:
            # Load URLs - either from command line or saved_urls.json
            urls = []
            
            # If --use-saved flag is set or no URLs provided, load from saved_urls.json
            if args.use_saved or not args.urls:
                urls = load_saved_urls()
                if not urls:
                    print("[!] No URLs available. Either provide URLs directly or ensure saved_urls.json is populated.")
            else:
                urls = args.urls
                  # Set up scheduler
            scheduler_service.set_interval(args.interval)
            scheduler_service.start_scraping()
            
            print(f"[*] Starting scheduled scraping with {len(urls)} URLs")
            print(f"[*] Interval: {args.interval} seconds")
            print(f"[*] Mode: {'Random' if args.random else 'Sequential'} URL selection")
            if args.runs > 0:
                print(f"[*] Will perform up to {args.runs} runs")
            else:
                print(f"[*] Will run indefinitely until stopped")
            print(f"[*] Press Ctrl+C to stop early")
            
            runs_completed = 0
            import random
            # Initialize the random seed with current time for better randomness
            random.seed()
            
            # Loop until we hit max runs (if specified) or until manually stopped
            while (args.runs == 0 or runs_completed < args.runs) and scheduler_service.is_scraping_active():
                if scheduler_service.is_time_to_scrape():
                    print(f"\n[*] Run {runs_completed + 1}/{args.runs}")
                      # Select URL(s) - either randomly or sequentially
                    run_urls = []
                    if args.random:
                        # Force re-seeding of random for true randomness on each selection
                        random.seed()
                        # Pick a random URL
                        selected_url = random.choice(urls)
                        run_urls = [selected_url]
                        print(f"[*] Randomly selected URL: {selected_url}")
                    else:
                        # Use the next URL in sequence
                        url_index = runs_completed % len(urls)
                        selected_url = urls[url_index]
                        run_urls = [selected_url]
                        print(f"[*] Using URL {url_index + 1}/{len(urls)}: {selected_url}")
                    
                    # Use a default of 3 for notify_count if not explicitly specified
                    notify_count = getattr(args, 'notify_count', 3)
                    success = run_scraper_with_url_improved(run_urls, args.notify_new, notify_count)
                    
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
