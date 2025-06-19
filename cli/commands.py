"""
CLI Commands Module
------------------
Implementation of all command functions for the VroomSniffer CLI.
"""
from typing import Dict, List, Optional, Any, Union, Tuple
import json
import sys
import time
import random
from pathlib import Path
from colorama import Fore, Style, Back

from cli.utils import Services, check_listings_exist, progress_decorator, project_root


def list_listings(
    services: Services, 
    list_type: str = "all", 
    count: int = 10
) -> None:
    """
    List car listings based on the specified type
    
    Args:
        services: Services instance
        list_type: Type of listings to display ('latest', 'all', or 'new'), defaults to 'all'
        count: Maximum number of listings to display (0 = all)
    """
    # Import colored output functions
    from cli.utils import print_info, print_warning, print_error, print_success
    from colorama import Fore, Style, Back
    
    # Choose the appropriate file based on the list_type
    if list_type == "latest":
        file_path = services.get_path("latest_results")
        file_description = f"{Fore.CYAN}latest run{Style.RESET_ALL}"
    elif list_type == "all":
        file_path = services.get_path("all_old")
        file_description = f"{Fore.CYAN}all stored{Style.RESET_ALL}"
    elif list_type == "new":
        file_path = services.get_path("latest_new")
        file_description = f"{Fore.GREEN}new findings{Style.RESET_ALL}"
    else:
        print_warning(f"Invalid listing type: {list_type}")
        return
    
    try:
        listings = services.storage_service.get_all_cached_listings(file_path)
        
        if not listings:
            print_warning(f"No listings found in {file_description}")
            return
            
        print_info(f"Found {len(listings)} {file_description} listings:")
        print(f"{Back.BLUE}{Fore.WHITE} {'ID':<4} {'TITLE':<48} {'PRICE'} {'LOCATION'} {'POSTED'} {Style.RESET_ALL}")
        
        # Determine how many listings to display
        display_count = len(listings) if count == 0 else min(count, len(listings))
        
        # Display listings
        for i, listing in enumerate(listings[:display_count], 1):
            # Clean up the listing data
            title = listing.get("Title", "Unknown").strip()
            # Remove any line breaks from the title
            title = title.replace("\n", " ").replace("\r", "")
            # Truncate title if too long
            if len(title) > 40:
                title = title[:37] + "..."
                
            # Clean up price - remove any line breaks and take only first line if multiline
            price_raw = listing.get("Price", "Unknown")
            if isinstance(price_raw, str):
                # Take only the first line if there are multiple lines
                price = price_raw.split("\n")[0].strip()
            else:
                price = str(price_raw)
            
            # Clean up location data
            location = listing.get("Location", "").strip() if "Location" in listing else ""
            location = location.replace("\n", " ").replace("\r", "")
            if len(location) > 20:
                location = location[:17] + "..."
                
            posted = listing.get("Posted", "").strip() if listing.get("Posted") else ""
            posted = posted.replace("\n", " ").replace("\r", "")
            
            # Add alternating row colors for better readability
            bg_color = Back.BLACK if i % 2 == 0 else ""
            print(f"{bg_color}{Fore.CYAN}[{i:<2}]{Style.RESET_ALL} {title:<48} {Fore.GREEN}{price}{Style.RESET_ALL} {Fore.YELLOW}{location}{Style.RESET_ALL} {posted}")
            
        if len(listings) > display_count:
            print_info(f"Showing {display_count} of {len(listings)} listings. Use --count option to show more.")
            
    except Exception as e:
        print_error(f"Error reading {file_description} listings: {e}")


def search_listings(
    services: Services, 
    keyword: str
) -> None:
    """
    Search listings by keyword in title
    
    Args:
        services: Services instance
        keyword: Search term to look for in listings
    """
    # Import colored output functions
    from cli.utils import print_info, print_warning, print_error, print_success
    from colorama import Fore, Style
    
    if not check_listings_exist(services):
        return
    
    # Use storage/all_old_results.json file by default
    all_old_path = services.get_path("all_old")
    
    print_info(f"Searching for '{keyword}' in listings...")
    
    listings = services.storage_service.get_listings_by_search_criteria(
        search_term=keyword,
        cache_path=all_old_path
    )
    
    if listings:
        print_success(f"Found {len(listings)} matches for '{keyword}':")
        for i, listing in enumerate(listings[:10], 1):  # Show only first 10 matches
            title = listing.get("Title", "Unknown")[:50]
            price = listing.get("Price", "Unknown")
            location = listing.get("Location", "Unknown") if "Location" in listing else ""
            
            print(f"{Fore.CYAN}[{i}]{Style.RESET_ALL} {title} | {Fore.GREEN}{price}{Style.RESET_ALL} {Fore.YELLOW}{location}{Style.RESET_ALL}")
        
        if len(listings) > 10:
            print_info(f"Showing 10 of {len(listings)} results. Use list command to see more.")
    else:
        print_warning(f"No listings found matching '{keyword}'")


def send_listing(
    services: Services, 
    listing_index: int
) -> bool:
    """
    Send a single listing via Telegram by index
    
    Args:
        services: Services instance
        listing_index: Index of the listing to send
        
    Returns:
        bool: True if successful, False otherwise
    """
    # Import colored output functions
    from cli.utils import print_info, print_warning, print_error, print_success
    from colorama import Fore, Style
    
    if not check_listings_exist(services):
        return False
    
    # Use storage/latest_results.json file
    latest_results_path = services.get_path("latest_results")
    listings = services.storage_service.get_all_cached_listings(latest_results_path)
    
    if 1 <= listing_index <= len(listings):
        listing = listings[listing_index - 1]
        title = listing.get("Title", "Unknown")[:30]
        
        print_info(f"Sending listing #{listing_index} to Telegram: '{title}...'")
        
        success = services.notification_service.send_listing(listing)
        
        if success:
            print_success(f"Listing {listing_index} sent via Telegram")
            return True
        else:
            print_error(f"Failed to send listing {listing_index} via Telegram")
            return False
    else:
        print_warning(f"Listing index {listing_index} not found. Use 'list' command to see available listings.")
        return False


def send_listings_by_indexes(
    services: Services, 
    indexes: List[int]
) -> None:
    """
    Send multiple specific listings via Telegram by their indexes
    
    Args:
        services: Services instance
        indexes: List of integer indexes to send
    """
    if not check_listings_exist(services):
        return
    
    # Use "storage/all_old_results.json" file by default
    all_old_path = services.get_path("all_old")
    listings = services.storage_service.get_all_cached_listings(all_old_path)
    
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
    
    # Use decorated function to handle tqdm progress bar
    _send_listings_with_progress(services, valid_indexes, listings)


@progress_decorator
def _send_listings_with_progress(
    services: Services, 
    indexes: List[int], 
    listings: List[Dict], 
    progress_bar=None
) -> None:
    """
    Internal function to send multiple listings with progress bar
    
    Args:
        services: Services instance
        indexes: List of integer indexes to send
        listings: List of all available listings
        progress_bar: Progress bar function
    """
    # Import colored output functions
    from cli.utils import print_info, print_warning, print_error, print_success, print_progress_bar
    from colorama import Fore, Style
    
    print_info(f"Sending {len(indexes)} listings via Telegram...")
    
    # Send each listing
    success_count = 0
    failed_listings = []
    total = len(indexes)
    
    # Use simpler iterator
    for i, idx in enumerate(indexes, 1):
        listing = listings[idx-1]  # -1 because indexes are 1-based
        title = listing.get("Title", "Unknown")[:30]
        
        # Show progress
        print_progress_bar(
            iteration=i-1, 
            total=total,
            prefix='', 
            suffix=f'{i-1}/{total} {title}...',
            length=30
        )
        # Add a newline to prevent output overlap
        print()
        
        success = services.notification_service.send_listing(listing)
        
        if success:
            success_count += 1
            print_success(f"Listing {idx} sent successfully")
        else:
            failed_listings.append(idx)
            print_error(f"Failed to send listing {idx}")
                
        # Add delay between messages
        if idx != indexes[-1]:  # If not the last message
            time.sleep(2)
    
    # Complete the progress bar
    print_progress_bar(total, total, prefix='Sending: ', suffix=f'({total}/{total}) Complete', length=30)
    
    if success_count == total:
        print_success(f"All {success_count} listings sent successfully!")
    else:
        print_success(f"Sent {success_count}/{total} listings successfully.")
        if failed_listings:
            print_warning(f"Failed to send listings: {', '.join(map(str, failed_listings))}")


def send_top_listings(
    services: Services, 
    count: int = 5
) -> None:
    """
    Send top N listings via Telegram
    
    Args:
        services: Services instance
        count: Number of listings to send
    """
    if not check_listings_exist(services):
        return
    
    # Use storage/latest_results.json file
    latest_results_path = services.get_path("latest_results")
    listings = services.storage_service.get_all_cached_listings(latest_results_path)
    
    actual_count = min(count, len(listings))
    print(f"[*] Sending top {actual_count} listings via Telegram...")
    
    success_count = services.notification_service.send_multiple_listings(
        listings[:actual_count],
        delay_seconds=2
    )
    
    print(f"[+] Bulk notification complete! {success_count}/{actual_count} messages sent successfully.")


def notify_new_findings(
    services: Services, 
    search_keyword: str = ""
) -> None:
    """
    Send notification about new findings with optional search filter
    
    Args:
        services: Services instance
        search_keyword: Optional keyword to filter listings by
    """
    if not check_listings_exist(services):
        return
    
    # Use storage/latest_new_results.json file which only contains new unique listings
    new_results_path = services.get_path("latest_new")
    listings = services.storage_service.get_all_cached_listings(new_results_path)
    
    # Filter by keyword if provided
    if search_keyword:
        filtered_listings = services.storage_service.get_listings_by_search_criteria(
            new_results_path, 
            search_term=search_keyword
        )
        if not filtered_listings:
            print(f"[!] No listings found matching '{search_keyword}'")
            return
    else:
        filtered_listings = listings
    
    # Send summary notification
    success = services.notification_service.send_summary_notification(
        filtered_listings,
        search_keyword=search_keyword,
        max_preview=3
    )
    
    if success:
        print(f"[+] Summary notification sent for {len(filtered_listings)} listings")
    else:
        print(f"[!] Failed to send summary notification")


def run_scraper_with_url(
    services: Services, 
    url: str, 
    notify: bool = False, 
    notify_count: int = 5
) -> bool:
    """
    Run the scraper with a direct URL
    
    Args:
        services: Services instance
        url: URL to scrape
        notify: Whether to send notifications for new listings
        notify_count: Number of listings to notify about
        
    Returns:
        bool: True if successful, False otherwise
    """
    print(f"[*] Running scraper with URL: {url}")
    
    # Create filters dictionary with custom_url
    filters = {"custom_url": url}
    
    # Use the scraper service to run the scraper
    listings = services.scraper_service.run_scraper_and_load_results(
        filters,
        build_search_url_ui=lambda x: x.get("custom_url", ""),  # Simple lambda to return the URL
        root_dir=project_root
    )
    
    if listings:
        print(f"[+] Scraping complete! Found {len(listings)} listings.")
        
        # Send notifications if requested
        if notify and listings:
            print(f"[*] Sending notifications for top {min(notify_count, len(listings))} listings...")
            send_top_listings(services, notify_count)
        
        return True
    else:
        print("[!] Scraping completed but no listings found.")
        return False


def run_scraper_with_url_improved(
    services: Services,
    urls: Union[str, List[str]], 
    notify_new: bool = False, 
    notify_count: int = 5
) -> bool:
    """
    Improved function to run the scraper with one or more direct URLs
    
    Args:
        services: Services instance
        urls: Single URL string or list of URLs to scrape
        notify_new: Whether to send notifications for new listings
        notify_count: Number of new listings to send detailed notifications for
        
    Returns:
        bool: True if successful, False otherwise
    """
    if isinstance(urls, str):
        urls = [urls]  # Convert single URL to list
        
    # Use our progress bar function
    return _run_scraper_with_urls_with_progress(
        services, urls, notify_new, notify_count
    )


@progress_decorator
def _run_scraper_with_urls_with_progress(
    services: Services,
    urls: List[str],
    notify_new: bool = False,
    notify_count: int = 5,
    progress_bar=None
) -> bool:
    """
    Internal function to run scraper with progress bar support
    
    Args:
        services: Services instance
        urls: List of URLs to scrape
        notify_new: Whether to notify about new listings
        notify_count: Maximum number of listings to send notifications for
        progress_bar: Function to display progress
        
    Returns:
        bool: True if successful, False otherwise
    """
    # Import colored output functions and progress bar
    from cli.utils import print_info, print_warning, print_error, print_success, print_progress_bar
    from colorama import Fore, Style
    
    all_listings = []
    new_listings = []
    success = False
    
    # Process URLs
    url_iter = enumerate(urls, 1)
    if len(urls) > 1:
        print(f"{Fore.CYAN}Processing {len(urls)} URLs:{Style.RESET_ALL}")
    
    for i, url in url_iter:
        print_info(f"Running scraper with URL {i}/{len(urls)}: {url}")
        
        # Show progress with our custom progress bar
        if len(urls) > 1:
            print_progress_bar(i-1, len(urls), prefix='', suffix=f'URL {i}/{len(urls)}', length=30)
            # Add a newline to prevent overlap with debug output
            print()
        
        # Create filters dictionary with custom_url
        filters = {"custom_url": url}
        
        # Use the scraper service's get_listings_for_filter method to properly handle storage
        url_all_listings, url_new_listings = services.scraper_service.get_listings_for_filter(
            filters,
            build_search_url_ui=lambda x: x.get("custom_url", ""),  # Simple lambda to return the URL
            root_dir=project_root
        )
        
        if url_all_listings:
            print_success(f"URL {i}/{len(urls)} complete! Found {len(url_all_listings)} listings ({len(url_new_listings)} new).")
            all_listings.extend(url_all_listings)
            new_listings.extend(url_new_listings)
            success = True
        else:
            print_warning(f"URL {i}/{len(urls)} completed but no listings found.")
    
    # Save combined listings to latest_results.json
    if all_listings:
        # Save to the latest_results.json file
        latest_results_path = services.get_path("latest_results")
        # Use direct json dump as StorageService doesn't have save_to_json method
        Path(latest_results_path).parent.mkdir(parents=True, exist_ok=True)
        with open(latest_results_path, "w", encoding="utf-8") as f:
            json.dump(all_listings, f, ensure_ascii=False, indent=2)
        print(f"[+] All URLs processed. Total listings found: {len(all_listings)} ({len(new_listings)} new).")
        
        # Send notifications about new listings if requested
        if notify_new and new_listings:
            notify_new_listings_after_scrape(services, new_listings, notify_count)
        
        return True
    else:
        print("[!] All URLs processed but no listings found.")
        return False


def notify_new_listings_after_scrape(
    services: Services,
    new_listings: List[Dict],
    count: int = -1
) -> None:
    """
    Send notification about new listings after scraping
    
    Args:
        services: Services instance
        new_listings: List of newly found listings
        count: Controls notification behavior:
            If count = -1: Send all new listings individually (default)
            If count > 0: Send individual notifications for the first N listings
    """
    if not new_listings:
        print("[*] No new listings to notify about.")
        return
    
    # Default behavior: send all new listings individually
    # If count is -1 (default), use all new listings
    # If count is positive, limit to that many listings
    listings_to_send = new_listings
    if count > 0:
        listings_to_send = new_listings[:count]
        print(f"[*] Sending individual notifications for {len(listings_to_send)} out of {len(new_listings)} new listings...")
    else:
        print(f"[*] Sending individual notifications for all {len(listings_to_send)} new listings...")
    
    if len(listings_to_send) > 15:
        print("[*] Large number of notifications - using batch processing to avoid Telegram rate limits")
    
    # Use the notification service to send individual listings
    # Get the URL description if available
    source_url = None
    if len(new_listings) > 0 and "source_url" in new_listings[0]:
        source_url = new_listings[0].get("source_url")
        
    success_count, failed = services.notification_service.manual_send_listings(
        listings_to_send,
        parse_mode="HTML",
        retry_on_network_error=True,
        source_url=source_url
    )
    
    print(f"[+] Sent {success_count}/{len(listings_to_send)} detailed notifications successfully.")
    if failed:
        print(f"[!] Failed to send {len(failed)} listings")
        # Log detailed error information for debugging
        for fail in failed[:3]:  # Show details for first 3 failures
            print(f"    - Failed to send '{fail['title']}': {fail['error']}")


def run_scheduler(
    services: Services,
    urls: List[str],
    interval: int = 60,
    runs: int = 5,
    random_selection: bool = False,
    notify_new: bool = False,
    notify_count: int = 5,
    check_ip_rotation: bool = True
) -> None:
    """
    Run the scheduler for periodic scraping
    
    Args:
        services: Services instance
        urls: List of URLs to scrape
        interval: Time between scraping runs in seconds
        runs: Maximum number of runs (0 for unlimited)
        random_selection: Whether to select URLs randomly
        notify_new: Whether to notify about new listings
        notify_count: Number of listings to send notifications for
    """
    try:
        # Set up scheduler
        services.scheduler_service.set_interval(interval)
        services.scheduler_service.start_scraping()
        
        # Import color utilities
        from cli.utils import print_info
        
        print(f"\n{Back.BLUE}{Fore.WHITE} SCHEDULER STARTED {Style.RESET_ALL}")
        print_info(f"Starting scheduled scraping with {len(urls)} URLs")
        
        minutes, seconds = divmod(interval, 60)
        if minutes > 0:
            interval_str = f"{minutes}m {seconds}s"
        else:
            interval_str = f"{seconds}s"
        
        print_info(f"Interval: {interval_str}")
        print_info(f"Mode: {'Random' if random_selection else 'Sequential'} URL selection")
        
        if runs > 0:
            print_info(f"Will perform up to {runs} runs")
        else:
            print_info(f"Will run indefinitely until stopped")
            
        print(f"{Fore.YELLOW}[!] Press Ctrl+C to stop early{Style.RESET_ALL}")
        
        runs_completed = 0
        # Initialize the random seed with current time for better randomness
        random.seed()
        
        # Loop until we hit max runs (if specified) or until manually stopped
        while (runs == 0 or runs_completed < runs) and services.scheduler_service.is_scraping_active():
            if services.scheduler_service.is_time_to_scrape():
                runs_remaining = "unlimited" if runs == 0 else str(runs)
                print(f"\n{Fore.CYAN}[*] Run {runs_completed + 1}/{runs_remaining}{Style.RESET_ALL}")
                
                # Use scheduler service for URL selection
                url_index = services.scheduler_service.select_next_url_index(
                    url_count=len(urls),
                    random_selection=random_selection,
                    current_run=runs_completed
                )
                selected_url = urls[url_index]
                run_urls = [selected_url]
                
                selection_mode = "Random" if random_selection else "Sequential"
                print(f"{Fore.BLUE}[*] {selection_mode} URL selection:{Style.RESET_ALL} {selected_url} {Fore.YELLOW}(index {url_index+1}/{len(urls)}){Style.RESET_ALL}")
                
                success = run_scraper_with_url_improved(
                    services, 
                    run_urls, 
                    notify_new, 
                    notify_count
                )
                
                runs_completed = services.scheduler_service.record_scrape()
                
                if runs > 0 and runs_completed >= runs:
                    services.scheduler_service.stop_scraping()
                    break
                    
                next_run_in = services.scheduler_service.get_time_until_next_scrape()
                minutes, seconds = divmod(int(next_run_in), 60)
                time_str = f"{minutes}m {seconds}s" if minutes > 0 else f"{seconds}s"
                print(f"{Fore.CYAN}[*] Next run in {time_str}{Style.RESET_ALL}")
            
            # Sleep for a short time to avoid CPU spinning
            time.sleep(1)
            
        print(f"[+] Scheduled scraping complete. Performed {runs_completed} runs.")
        
    except KeyboardInterrupt:
        print("\n[*] Scheduled scraping stopped by user")
        services.scheduler_service.stop_scraping()
