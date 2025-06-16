"""
VroomSniffer Service - Main interface for the VroomSniffer application.
A facade that coordinates all specialized services.
"""
import sys
import json
import time
import re
from pathlib import Path

# Import the new service classes
from services.storage_service import StorageService
from services.url_pool_service import UrlPoolService
from services.statistics_service import StatisticsService
from services.notification_service import NotificationService
from services.scraper_service import ScraperService
from services.scheduler_service import SchedulerService

# Initialize service instances (lazy loading)
_storage_service = None
_url_pool_service = None
_statistics_service = None
_notification_service = None
_scraper_service = None
_scheduler_service = None

def _get_storage_service():
    """Get or create the storage service instance"""
    global _storage_service
    if _storage_service is None:
        _storage_service = StorageService()
    return _storage_service

def _get_url_pool_service():
    """Get or create the URL pool service instance"""
    global _url_pool_service
    if _url_pool_service is None:
        _url_pool_service = UrlPoolService()
    return _url_pool_service

def _get_statistics_service():
    """Get or create the statistics service instance"""
    global _statistics_service
    if _statistics_service is None:
        _statistics_service = StatisticsService(_get_storage_service())
    return _statistics_service

def _get_notification_service():
    """Get or create the notification service instance"""
    global _notification_service
    if _notification_service is None:
        _notification_service = NotificationService()
    return _notification_service

def _get_scraper_service():
    """Get or create the scraper service instance"""
    global _scraper_service
    if _scraper_service is None:
        _scraper_service = ScraperService(_get_storage_service())
    return _scraper_service

def _get_scheduler_service():
    """Get or create the scheduler service instance"""
    global _scheduler_service
    if _scheduler_service is None:
        _scheduler_service = SchedulerService()
    return _scheduler_service

# === STORAGE FUNCTIONS ===

def load_cache(cache_path):
    """Load cached data from the specified path"""
    return _get_storage_service().load_cache(cache_path)

def save_cache(cache_dict, cache_path):
    """Save cache dictionary to the specified path"""
    return _get_storage_service().save_cache(cache_dict, cache_path)

def is_listing_cached(url, cache_path):
    """Check if a listing URL exists in the cache"""
    return _get_storage_service().is_listing_cached(url, cache_path)

def add_listing_to_cache(listing, cache_path):
    """Add a new listing to the cache"""
    return _get_storage_service().add_listing_to_cache(listing, cache_path)

def remove_listing_from_cache(url, cache_path):
    """Remove a listing from the cache by URL"""
    return _get_storage_service().remove_listing_from_cache(url, cache_path)

def get_cached_listing(url, cache_path):
    """Get a specific listing by URL from the cache"""
    return _get_storage_service().get_cached_listing(url, cache_path)

def get_all_cached_listings(cache_path):
    """Get all listings from the cache"""
    return _get_storage_service().get_all_cached_listings(cache_path)

def clear_cache(cache_path):
    """Clear all listings from the specified cache"""
    return _get_storage_service().clear_cache(cache_path)

def get_cache_stats(cache_path):
    """Get statistics about the cache (size, count, etc.)"""
    return _get_storage_service().get_cache_stats(cache_path)

def remove_listings_by_ids(listing_urls, cache_path):
    """Remove multiple listings by their URLs"""
    return _get_storage_service().remove_listings_by_ids(listing_urls, cache_path)

def clear_all_caches(root_dir=None):
    """Clear all caches in the system"""
    return _get_storage_service().clear_all_caches(root_dir)

def get_listings_by_search_criteria(cache_path, search_term=None, min_price=None, max_price=None):
    """Search listings that match specified criteria"""
    return _get_storage_service().get_listings_by_search_criteria(search_term, min_price, max_price, cache_path)

# === SCRAPER FUNCTIONS ===

def run_scraper_and_load_results(filters, build_search_url_ui, root_dir):
    """Run the scraper with filters and return results"""
    return _get_scraper_service().run_scraper_and_load_results(filters, build_search_url_ui, root_dir)

def get_listings_for_filter(filters, all_old_path, latest_new_path, build_search_url_ui, root_dir):
    """Get all listings and new listings for a specific filter"""
    return _get_scraper_service().get_listings_for_filter(filters, build_search_url_ui, all_old_path, latest_new_path, root_dir)

# === STATISTICS FUNCTIONS ===

def extract_prices(listings):
    """Extract price information from listings"""
    return _get_statistics_service().extract_prices(listings)

def show_statistics(listings_data):
    """Generate and display statistics for listings data"""
    return _get_statistics_service().show_statistics(listings_data)

# === NOTIFICATION FUNCTIONS ===

def manual_send_listings(listings, send_telegram_message, format_car_listing_message, parse_mode="HTML", retry_on_network_error=True):
    """
    Send listings to Telegram with custom messaging functions
    
    Args:
        listings: List of listings to send
        send_telegram_message: Function to send Telegram messages
        format_car_listing_message: Function to format car listing messages
        parse_mode: Telegram parse mode (default "HTML")
        retry_on_network_error: Whether to retry on network errors
        
    Returns:
        tuple: (success_count, failed_list)
    """
    # Create a notification service with the provided functions
    temp_notification_service = NotificationService(
        telegram_send=send_telegram_message,
        telegram_format=format_car_listing_message
    )
    return temp_notification_service.manual_send_listings(listings, parse_mode, retry_on_network_error)

def send_listing(listing):
    """Send a single listing via Telegram"""
    return _get_notification_service().send_listing(listing)

def send_multiple_listings(listings, delay_seconds=1.5):
    """Send multiple listings via Telegram with delay between messages"""
    return _get_notification_service().send_multiple_listings(listings, delay_seconds)

def send_summary_notification(listings, search_keyword="", max_preview=3):
    """Send a summary notification with listing preview"""
    return _get_notification_service().send_summary_notification(listings, search_keyword, max_preview)

# === SCHEDULER FUNCTIONS ===

def set_scraping_interval(seconds):
    """Set the time interval between scraping runs"""
    return _get_scheduler_service().set_interval(seconds)

def get_scraping_interval():
    """Get the current time interval between scraping runs"""
    return _get_scheduler_service().get_interval()

def is_time_to_scrape():
    """Check if enough time has passed for the next scrape"""
    return _get_scheduler_service().is_time_to_scrape()

def start_scraping():
    """Start the automated scraping process"""
    return _get_scheduler_service().start_scraping()

def stop_scraping():
    """Stop the automated scraping process"""
    return _get_scheduler_service().stop_scraping()

def is_scraping_active():
    """Check if automated scraping is currently active"""
    return _get_scheduler_service().is_scraping_active()

def record_scrape():
    """Record that a scrape has occurred and increment run count"""
    return _get_scheduler_service().record_scrape()

def get_total_runs():
    """Get the total number of scraper runs performed"""
    return _get_scheduler_service().get_total_runs()

def set_total_runs(count):
    """Set the total number of scraper runs (for state loading)"""
    return _get_scheduler_service().set_total_runs(count)

def get_time_until_next_scrape():
    """Calculate time remaining until the next scrape"""
    return _get_scheduler_service().get_time_until_next_scrape()

def get_progress_percentage():
    """Calculate progress percentage toward next scrape"""
    return _get_scheduler_service().get_progress_percentage()

def select_next_url_index(url_count):
    """Select which URL to scrape next from the pool"""
    return _get_scheduler_service().select_next_url_index(url_count)

def get_next_url_index():
    """Get the index of the URL selected for next scrape"""
    return _get_scheduler_service().get_next_url_index()

def is_next_url_selected():
    """Check if a URL has been selected for the next scrape"""
    return _get_scheduler_service().is_next_url_selected()
